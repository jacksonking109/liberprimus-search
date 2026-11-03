"""Swarm loop: generators propose cipher programs, code disposes.

Per round, each generator proposes k specs. Each spec is validated and
compiled (invalid ones are reported back as errors), optionally ordered by a
ranker, deduplicated by the ledger, run by the executor as its own hypothesis
(with the generator's model and role as provenance), and the coarse verdict is
fed back to that generator. A final Bonferroni check over every attempt on the
target closes the run.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from lpswarm.executor import Executor, ExplicitKeys, Target, final_check
from lpswarm.ledger import Ledger
from lpswarm.oracle import FullOracle
from lpswarm.programs import SpecError, compile_spec, describe, expand, spec_hash
from lpswarm.router.adapters import AdapterError
from lpswarm.router.limits import RateLimited
from lpswarm.router.router import BudgetExceeded
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

    def __post_init__(self) -> None:
        if self.rounds < 1 or self.per_round < 1:
            raise ValueError("SwarmConfig: rounds and per_round must be >= 1")


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
              progress: bool = True) -> SwarmResult:
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
        for gen in generators:
            if stop_path is not None and stop_path.exists():
                stopped = "stop_file"
                break
            if time_left() is not None and time_left() <= 0:
                stopped = "timeout"
                break
            if budget_left() is not None and budget_left() <= 0:
                stopped = "max_attempts"
                break
            gs = stats[gen.model]
            k = min(int(getattr(gen, "per_round", None) or cfg.per_round), 32)
            ctx = GenContext(shown_label, alpha, target.ciphertext, rnd, k,
                             history[gen.model], errors[gen.model],
                             summarise_tried(ledger.tried(tid)), alphabet_values,
                             task_id=target.label)
            try:
                raws = gen.propose(ctx)
                proposed_this_round += 1
            except RateLimited as exc:
                limited[gen.model] = exc.resume_at
                if progress:
                    print(f"  [{gen.model}] {exc}", flush=True)
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
            for e in getattr(gen, "last_errors", []) or []:
                errors[gen.model].append(e)
            compiled, seen = [], set()
            for rp in raws:
                gs.proposals += 1
                try:
                    spec = compile_spec(rp.spec, alpha)
                except SpecError as exc:
                    gs.invalid += 1
                    errors[gen.model].append(f"{str(rp.spec)[:100]} -> {str(exc)[:160]}")
                    continue
                except Exception as exc:  # noqa: BLE001 - malformed input must never crash a run
                    gs.invalid += 1
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
                    s = ex.run(target, hyp, "program",
                               ExplicitKeys(expand(spec), derivation=f"model:{gen.model}"))
                except (SpecError, ValueError) as exc:
                    gs.invalid += 1
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
                    verdict = f"duplicate (already tried): {verdict}"
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
            stopped = _wait_until(resume, stop_path, time_left, progress)
            if stopped:
                break
            rnd -= 1   # the round produced nothing; do not count it
        else:
            idle_rounds = 0
    final = final_check(ledger, oracle, tid)
    return SwarmResult(tid, rounds_run, stopped, stats, final, time.monotonic() - t0)


def _wait_until(resume_at: float, stop_path, time_left, progress: bool) -> str | None:
    """Sleep until resume_at, checking the STOP file and the run timeout every 30 s."""
    from datetime import datetime
    if progress:
        print(f"all generators are paused by usage limits; waiting until "
              f"{datetime.fromtimestamp(resume_at):%Y-%m-%d %H:%M} (create a STOP file to end)",
              flush=True)
    while True:
        now = time.time()
        if now >= resume_at:
            return None
        if stop_path is not None and stop_path.exists():
            return "stop_file"
        left = time_left()
        if left is not None and left <= 0:
            return "timeout"
        step = min(30.0, resume_at - now) if left is None else min(30.0, resume_at - now, left)
        time.sleep(max(0.5, step))
