"""Swarm loop: generators propose cipher programs, code disposes.

Per round, each generator proposes k specs. Each spec is validated and
compiled (invalid ones are reported back as errors), optionally ordered by a
ranker, deduplicated by the ledger, run by the executor as its own hypothesis
(with the generator's model and role as provenance), and the coarse verdict is
fed back to that generator. A final Bonferroni check over every attempt on the
target closes the run.
"""
from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from lpswarm.executor import Executor, ExplicitKeys, Target, final_check
from lpswarm.ledger import Ledger
from lpswarm.oracle import FullOracle
from lpswarm.programs import (SpecError, compile_spec, describe, expand_iter, expansion_size,
                              spec_hash)
from lpswarm.router.adapters import AdapterError
from lpswarm.router.limits import RateLimited
from lpswarm.router.router import BudgetExceeded, backend_key
from lpswarm.swarm.generators import Feedback, GenContext, summarise_tried


@dataclass
class SwarmConfig:
    rounds: int = 5
    per_round: int = 8
    max_attempts: int | None = 50_000      # new attempts on this target in this run
    timeout_s: float | None = None
    stop_file: str | None = "STOP"
    stop_on_pass: bool = True
    wait_on_rate_limit: bool = True       # pause until a usage limit resets (else stop)
    # Call generators on different backends (GPU / plan / API, see backend_key) at the
    # same time; results are still processed one generator at a time, in order.
    parallel: bool = True
    # A proposal that expands to more ciphers than this runs as a lean sweep: failed attempts
    # are counted but not stored (see Executor.run). 0 disables, 1 forces lean for everything.
    lean_threshold: int = 50_000

    def __post_init__(self) -> None:
        if self.rounds < 1 or self.per_round < 1:
            raise ValueError("SwarmConfig: rounds and per_round must be >= 1")


MAX_REASON_KEYS = 40
REASON_CHARS = 100


def normalise_reason(text: str) -> str:
    """Group invalid-proposal messages: numbers, quoted fragments and bracketed lists collapsed."""
    t = re.sub(r"\[[^\]]*\]", "[...]", str(text))
    t = re.sub(r"'[^']*'|\"[^\"]*\"", "'...'", t)
    t = re.sub(r"-?\d+", "#", t)
    return t.strip()[:REASON_CHARS] or "(empty)"


@dataclass
class GeneratorStats:
    name: str
    proposals: int = 0
    invalid: int = 0
    duplicates: int = 0
    attempts: int = 0
    passes: int = 0
    near_misses: int = 0
    model_errors: int = 0
    first_pass_attempt: int | None = None   # attempts on target when this generator first passed
    # Why proposals were invalid: normalised reason -> [count, one short example]. Kept in
    # report.json (the errors fed back into prompts are not stored anywhere else).
    invalid_reasons: dict = field(default_factory=dict)

    def note_invalid(self, text: str) -> None:
        key = normalise_reason(text)
        if key not in self.invalid_reasons and len(self.invalid_reasons) >= MAX_REASON_KEYS:
            key = "(other reasons)"
        slot = self.invalid_reasons.setdefault(key, [0, str(text)[:REASON_CHARS]])
        slot[0] += 1


@dataclass
class SwarmResult:
    target_id: str
    rounds_run: int
    stopped: str | None
    stats: dict[str, GeneratorStats] = field(default_factory=dict)
    final: list[dict] = field(default_factory=list)
    elapsed_s: float = 0.0


def run_swarm(target: Target, ledger: Ledger, oracle: FullOracle, generators: Sequence,
              cfg: SwarmConfig | None = None, ranker=None, alphabet_values=None,
              progress: bool = True, brief: str = "", shared_fn=None,
              known_words=None) -> SwarmResult:
    cfg = cfg or SwarmConfig()
    alpha = target.alphabet
    tid = ledger.add_target(alpha, target.ciphertext, target.label, target.page_range,
                            target.is_synthetic, breaks=target.breaks)
    ledger.commit()
    names = [g.model for g in generators]
    if len(set(names)) != len(names):
        raise ValueError(f"generator names must be unique, got {names}")
    t0 = time.monotonic()
    stats = {g.model: GeneratorStats(g.model) for g in generators}
    history: dict[str, list[Feedback]] = {g.model: [] for g in generators}
    errors: dict[str, list[str]] = {g.model: [] for g in generators}
    used = 0
    stopped = None
    rounds_run = 0
    stop_path = Path(cfg.stop_file) if cfg.stop_file else None
    # Generators see a neutral name for synthetic targets (the label can reveal the
    # cipher family) and the page label for real ones.
    shown_label = "synthetic target" if target.is_synthetic else target.label

    def budget_left() -> int | None:
        return None if cfg.max_attempts is None else cfg.max_attempts - used

    def time_left() -> float | None:
        return None if cfg.timeout_s is None else max(0.0, cfg.timeout_s - (time.monotonic() - t0))

    rnd = 0
    idle_rounds = 0          # consecutive rounds where every generator was paused
    while rnd < cfg.rounds:
        rnd += 1
        rounds_run = rnd
        limited: dict[str, float] = {}
        proposed_this_round = 0
        stopped = _pre_check(stop_path, time_left, budget_left)
        if stopped:
            break
        # Every generator sees the ledger as it was at the start of the round.
        tried_now = summarise_tried(ledger.tried(tid))
        shared = ""
        if shared_fn is not None:   # re-read every round: the strategy note can change
            try:
                shared = shared_fn(tid) or ""
            except Exception:  # noqa: BLE001 - shared context is best-effort
                shared = ""
        ctxs = {}
        for gen in generators:
            k = min(int(getattr(gen, "per_round", None) or cfg.per_round), 32)
            ctxs[gen.model] = GenContext(shown_label, alpha, target.ciphertext, rnd, k,
                                         history[gen.model], errors[gen.model], tried_now,
                                         alphabet_values, task_id=target.label, brief=brief,
                                         shared=shared,
                                         known_words=[] if target.is_synthetic else list(known_words or []))
        fetched = _fetch_proposals(generators, ctxs, cfg.parallel, rnd, progress)
        for gen in generators:
            stopped = _pre_check(stop_path, time_left, budget_left)
            if stopped:
                break
            gs = stats[gen.model]
            ctx = ctxs[gen.model]
            k = ctx.k
            try:
                raws, gen_errors = fetched[gen.model]
                if isinstance(raws, BaseException):
                    raise raws
                proposed_this_round += 1
            except RateLimited as exc:
                limited[gen.model] = exc.resume_at
                if progress:
                    rest = "; the other generators carry on" if len(generators) > 1 else ""
                    print(f"  [{gen.model}] {exc}{rest}", flush=True)
                continue
            except BudgetExceeded as exc:
                stopped = f"budget: {exc}"
                break
            except AdapterError as exc:
                gs.model_errors += 1
                # The raw error (HTTP body etc.) is printed for the operator but never fed
                # back into a prompt.
                errors[gen.model].append("(your previous reply could not be obtained; try again)")
                if progress:
                    print(f"  [{gen.model}] model error: {exc}")
                continue
            except Exception as exc:  # noqa: BLE001 - one bad generator call must not end the run
                gs.model_errors += 1
                errors[gen.model].append("(your previous reply could not be processed)")
                if progress:
                    print(f"  [{gen.model}] generator error: {type(exc).__name__}: {exc}")
                continue
            for e in gen_errors:
                errors[gen.model].append(e)
            compiled, seen = [], set()
            for rp in raws:
                gs.proposals += 1
                try:
                    spec = compile_spec(rp.spec, alpha)
                except SpecError as exc:
                    gs.invalid += 1
                    gs.note_invalid(str(exc))
                    errors[gen.model].append(f"{str(rp.spec)[:100]} -> {str(exc)[:160]}")
                    continue
                except Exception as exc:  # noqa: BLE001 - malformed input must never crash a run
                    gs.invalid += 1
                    gs.note_invalid(f"invalid ({type(exc).__name__})")
                    errors[gen.model].append(f"{str(rp.spec)[:100]} -> invalid ({type(exc).__name__})")
                    continue
                h = spec_hash(spec)
                if h in seen:
                    continue
                seen.add(h)
                compiled.append((spec, rp.why))
            if len(compiled) > k:
                errors[gen.model].append(f"{len(compiled) - k} proposal(s) beyond the "
                                         f"limit of {k} per round were not run")
                compiled = compiled[:k]
            if ranker is not None and len(compiled) > 1:
                order = ranker.rank(ctx, [describe(sp, alpha) for sp, _ in compiled])
                compiled = [compiled[i] for i in order]
            ex = Executor(ledger, oracle, max_attempts=budget_left(), timeout_s=time_left(),
                          stop_file=cfg.stop_file)
            for spec, why in compiled:
                desc = describe(spec, alpha)
                hyp = ledger.add_hypothesis("program", desc + (f" | why: {why}" if why else ""),
                                            gen.model, gen.role)
                try:
                    lean_id = (spec_hash(spec) if cfg.lean_threshold and
                               expansion_size(spec) >= cfg.lean_threshold else None)
                    lean_spec = None
                    if lean_id is not None:
                        from lpswarm.programs.spec import EXPANSION_VERSION, canonical
                        lean_spec = {"spec_json": canonical(spec), "expansion_version": EXPANSION_VERSION,
                                     "text_length": int(len(target.ciphertext)),
                                     "requested": expansion_size(spec)}
                    s = ex.run(target, hyp, "program",
                               ExplicitKeys(expand_iter(spec, len(target.ciphertext)),
                                            derivation=f"model:{gen.model}"), lean_id=lean_id,
                               lean_spec=lean_spec)
                except (SpecError, ValueError) as exc:
                    gs.invalid += 1
                    gs.note_invalid(f"could not run: {exc}")
                    errors[gen.model].append(f"{desc} -> could not run: {str(exc)[:160]}")
                    continue
                used += s.new_attempts
                ex.max_attempts = budget_left()
                ex.timeout_s = time_left()
                gs.attempts += s.new_attempts
                if s.passes:
                    verdict = "pass"
                    gs.passes += 1
                    if gs.first_pass_attempt is None:
                        gs.first_pass_attempt = ledger.attempt_count(tid)
                elif s.prior_passes:
                    verdict = "pass"
                elif s.near_misses:
                    verdict = "near_miss"
                    gs.near_misses += 1
                else:
                    verdict = "fail"
                if s.new_attempts == 0 and s.skipped:
                    gs.duplicates += 1
                    why = ("same decryption as a different key already tried (an equivalent "
                           "program)" if s.equivalent == s.skipped else "already tried")
                    verdict = f"duplicate ({why}): {verdict}"
                history[gen.model].append(Feedback(desc, verdict))
                if s.stopped in ("max_attempts", "stop_file", "timeout"):
                    stopped = s.stopped
                    break
            if progress:
                print(f"round {rnd} [{gen.model}] proposals={len(raws)} valid={len(compiled)} "
                      f"attempts={gs.attempts} passes={gs.passes} near={gs.near_misses} "
                      f"invalid={gs.invalid}", flush=True)
            if stopped:
                break
        if stopped:
            break
        if cfg.stop_on_pass and any(st.passes for st in stats.values()):
            stopped = "pass_found"
            break
        if limited and proposed_this_round == 0:
            # Every generator is paused by a usage limit: wait (no deadline) or stop.
            # At least a minute per pause, and a cap on idle rounds, so a limit that keeps
            # reporting a past reset time can never turn into a tight call loop.
            resume = max(min(limited.values()), time.time() + 60)
            idle_rounds += 1
            if not cfg.wait_on_rate_limit:
                stopped = "rate_limited"
                break
            if idle_rounds > 500:
                stopped = "rate_limited: too many paused rounds in a row"
                break
            paused_gens = [g for g in generators if g.model in limited]
            stopped = _wait_until(resume, stop_path, time_left, progress,
                                  still_paused=lambda: _any_still_paused(paused_gens))
            if stopped:
                break
            rnd -= 1   # the round produced nothing; do not count it
        else:
            idle_rounds = 0
    final = final_check(ledger, oracle, tid)
    return SwarmResult(tid, rounds_run, stopped, stats, final, time.monotonic() - t0)


def _pre_check(stop_path, time_left, budget_left) -> str | None:
    if stop_path is not None and stop_path.exists():
        return "stop_file"
    if time_left() is not None and time_left() <= 0:
        return "timeout"
    if budget_left() is not None and budget_left() <= 0:
        return "max_attempts"
    return None


def generator_backend(gen) -> str:
    """The backend a generator's calls queue on (see router.backend_key); generators
    without a router (tests, scripted fakes) each get their own."""
    router, name = getattr(gen, "router", None), getattr(gen, "model", None)
    try:
        return backend_key(router.spec(name))
    except Exception:  # noqa: BLE001
        return f"generator:{name}"


def _fetch_proposals(generators, ctxs: dict, parallel: bool, rnd: int,
                     progress: bool) -> dict[str, tuple]:
    """Call every generator once; {model: (proposals or the exception, extra errors)}.

    Generators on different backends are called at the same time (one worker thread
    per backend); generators sharing a backend are called one after another. Nothing
    here touches the target ledger: processing happens afterwards, in order."""
    groups: dict[str, list] = {}
    for gen in generators:
        groups.setdefault(generator_backend(gen) if parallel else "serial", []).append(gen)
    out: dict[str, tuple] = {}

    def work(gens):
        for gen in gens:
            try:
                raws = gen.propose(ctxs[gen.model])
                out[gen.model] = (raws, list(getattr(gen, "last_errors", []) or []))
            except Exception as exc:  # noqa: BLE001 - re-raised per generator by the caller
                out[gen.model] = (exc, [])

    if len(groups) <= 1:
        for gens in groups.values():
            work(gens)
        return out
    if progress:
        print(f"round {rnd}: calling " + " | ".join(", ".join(g.model for g in gens)
                                                     for gens in groups.values())
              + " (in parallel)", flush=True)
    with ThreadPoolExecutor(max_workers=len(groups), thread_name_prefix="gen") as pool:
        for f in [pool.submit(work, gens) for gens in groups.values()]:
            f.result()
    return out


def _any_still_paused(gens) -> bool:
    """False once any paused generator's model is free again (e.g. its cap was raised
    in the models config). Generators without a router count as still paused."""
    for g in gens:
        router = getattr(g, "router", None)
        try:
            if router is not None and router.window_status(g.model)["paused_until"] is None:
                return False
        except Exception:  # noqa: BLE001
            continue
    return True


def _wait_until(resume_at: float, stop_path, time_left, progress: bool,
                still_paused=None, recheck_s: float = 60.0) -> str | None:
    """Sleep until resume_at, checking the STOP file and the run timeout every 30 s, and
    (still_paused) every recheck_s whether a pause has been lifted early."""
    from datetime import datetime
    if progress:
        print(f"all generators are paused by usage limits; waiting until "
              f"{datetime.fromtimestamp(resume_at):%Y-%m-%d %H:%M} (create a STOP file to end)",
              flush=True)
    last_check = time.monotonic()
    while True:
        now = time.time()
        if now >= resume_at:
            return None
        if still_paused is not None and time.monotonic() - last_check >= recheck_s:
            last_check = time.monotonic()
            if not still_paused():
                if progress:
                    print("a paused model is available again (cap raised?); carrying on", flush=True)
                return None
        if stop_path is not None and stop_path.exists():
            return "stop_file"
        left = time_left()
        if left is not None and left <= 0:
            return "timeout"
        step = min(30.0, resume_at - now) if left is None else min(30.0, resume_at - now, left)
        if still_paused is not None:
            step = min(step, recheck_s)
        time.sleep(max(0.1, step))
