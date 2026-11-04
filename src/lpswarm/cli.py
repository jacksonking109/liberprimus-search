"""Command line: `lpswarm <command>` or `python -m lpswarm <command>`.

Commands:
  validate    run the validation harness, write reports/validation.{csv,md,json}
  null-check  measure the oracle's false-positive rate on fresh nulls
  baseline    brute-force a ciphertext (file or synthetic demo) into the ledger
  ruled-out   list hypotheses tried and failed, from a ledger
  leads       list passing (and optionally near-miss) attempts, from a ledger
  encode      show how a text file is read under an alphabet (sanity check)
  swarm       Phase 3: generators propose cipher programs for targets
  tiertest    Phase 3: compare generators against the baselines
  doctor      check that everything needed for a run is in place
  overnight   run a queue of jobs unattended (resumable; SUMMARY.md; optional supervisor)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
import tomllib
from pathlib import Path
from typing import Any, Sequence

from lpswarm.alphabet import get_alphabet
from lpswarm.oracle import FullOracle, OracleConfig


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    from lpswarm.textio import read_text
    return tomllib.loads(read_text(path))


def _apply(dc_cls, base: dict, overrides: dict) -> Any:
    fields = {f.name: f for f in dataclasses.fields(dc_cls)}
    kw = {}
    for src in (base, overrides):
        for k, v in src.items():
            if v is None:
                continue
            if k not in fields:
                raise SystemExit(f"unknown {dc_cls.__name__} option: {k}")
            if isinstance(v, list):
                v = tuple(v)
            kw[k] = v
    return dc_cls(**kw)


def _oracle_cfg(args, conf: dict) -> OracleConfig:
    return _apply(OracleConfig, conf.get("oracle", {}),
                  {"alpha": args.alpha, "null_samples": args.null_samples, "seed": args.oracle_seed})


def _csv_ints(s: str | None) -> tuple[int, ...] | None:
    return tuple(int(x) for x in s.split(",") if x.strip()) if s else None


def _csv_strs(s: str | None) -> tuple[str, ...] | None:
    return tuple(x.strip() for x in s.split(",") if x.strip()) if s else None


def _add_oracle_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--config", help="TOML file with [oracle] / [validation] / [baseline] tables")
    p.add_argument("--alphabet", default=None,
                   help="latin26 (default), rune_likeNN, or path to alphabet JSON")
    p.add_argument("--alpha", type=float, help="per-attempt false-positive rate (default 0.01)")
    p.add_argument("--null-samples", type=int, help="null samples per type per length")
    p.add_argument("--oracle-seed", type=int)


def cmd_validate(args) -> int:
    from lpswarm.validation.harness import ValidationConfig, run_validation
    conf = _load_config(args.config)
    over: dict = {"families": _csv_strs(args.families), "lengths": _csv_ints(args.lengths),
                  "cases_per_cell": args.cases, "seed": args.seed, "out_dir": args.out,
                  "alphabet": args.alphabet, "decoys": args.decoys,
                  "difficulty": args.difficulty, "word_breaks": args.word_breaks or None}
    if args.quick:
        over.update(cases_per_cell=args.cases or 2, decoys=args.decoys or 100,
                    null_check_samples=500, lengths=over["lengths"] or (30, 80))
    vc = _apply(ValidationConfig, conf.get("validation", {}), over)
    oc = _oracle_cfg(args, conf)
    if args.quick and args.null_samples is None and "null_samples" not in conf.get("oracle", {}):
        oc = dataclasses.replace(oc, null_samples=500)
    res = run_validation(vc, oc, progress=not args.quiet)
    out = Path(vc.out_dir)
    print(f"\nwrote {out / 'validation.md'}, {out / 'validation.csv'}, {out / 'null_fpr.csv'}")
    ok = all(s["within_tolerance"] for s in res["null_check"]["summary"])
    print(f"null calibration within tolerance: {'yes' if ok else 'NO'}")
    return 0 if ok else 2


def cmd_null_check(args) -> int:
    from lpswarm.oracle import null_fpr_check
    conf = _load_config(args.config)
    alphabet = get_alphabet(args.alphabet or "latin26")
    oracle = FullOracle(alphabet, _oracle_cfg(args, conf))
    res = null_fpr_check(oracle, _csv_ints(args.lengths) or (20, 40, 60, 100, 200),
                         samples=args.samples)
    for r in res["rows"]:
        print(f"L={r['length']:<5} {r['null_type']:<10} fpr={r['fpr']:.4f} "
              f"[{r['ci_lo']:.4f}, {r['ci_hi']:.4f}] alpha={r['alpha']}")
    ok = True
    for s in res["summary"]:
        ok &= s["within_tolerance"]
        print(f"L={s['length']:<5} worst={s['worst_type_fpr']:.4f} tol={s['tolerance']:.4f} "
              f"{'ok' if s['within_tolerance'] else 'OUT OF TOLERANCE'}")
    return 0 if ok else 2


def _targets_from_args(args, alphabet) -> list[tuple]:
    """(ciphertext ints, label, page_range, is_synthetic, demo key texts) per target."""
    from lpswarm.textio import read_text
    given = [bool(args.ciphertext), bool(args.demo), bool(args.manifest)]
    if sum(given) != 1:
        raise SystemExit("give exactly one of --ciphertext, --demo, --manifest")
    out = []
    use_breaks = not getattr(args, "no_word_breaks", False)
    if args.ciphertext:
        for f in args.ciphertext:
            b: list[int] = []
            ct = alphabet.encode(read_text(f), glyphs_only=args.glyphs_only, boundaries=b)
            label = args.label or Path(f).name
            out.append((ct, label, args.page_range, False, [], tuple(b) if use_breaks else None))
    elif args.demo:
        from lpswarm.ciphers import get_family
        from lpswarm.textgen.synth import generate_case
        fam, _, length = args.demo.partition(":")
        get_family(fam)
        try:
            n_sym = int(length) if length else 80
        except ValueError:
            raise SystemExit(f"--demo expects FAMILY:LENGTH, e.g. vigenere:120 (got {args.demo!r})")
        case = generate_case(fam, n_sym, args.difficulty or "medium",
                             alphabet=alphabet, seed=args.seed or 0)
        keys = [("demo-key-text", case.key)] if fam == "running_key" else []
        print(f"demo target: {fam} length {len(case.ciphertext)}; true params {case.params}")
        from lpswarm.textgen.synth import case_breaks
        out.append((case.ciphertext, f"demo:{fam}:{len(case.ciphertext)}:{case.case_id}", None,
                    True, keys, case_breaks(case, alphabet) if use_breaks else None))
    else:
        mpath = Path(args.manifest)
        man = json.loads(read_text(mpath))
        if args.sections in ("unsolved", "solved", "all"):
            from lpswarm.overnight import manifest_sections
            wanted = set(manifest_sections(mpath, args.sections))
        else:
            wanted = set(_csv_ints(args.sections) or ())
        for sec in man["sections"]:
            if wanted and sec["index"] not in wanted:
                continue
            raw = read_text(mpath.parent / sec["file"])
            b = []
            ct = alphabet.encode(raw, glyphs_only=True, boundaries=b)
            label = f"{sec.get('part', '')}:{sec['label']}"
            if sec.get("replacement_chars") or sec.get("unknown_runes"):
                print(f"warning: section {sec['index']} ({sec['label']}) has corrupted or unknown "
                      "characters; they are dropped, so positions after them may be shifted")
            out.append((ct, label, sec["label"], False, [], tuple(b) if use_breaks else None))
    return out


def cmd_baseline(args) -> int:
    from lpswarm.baseline import BaselineConfig, load_key_texts, run_baseline
    from lpswarm.executor import Target
    from lpswarm.ledger import Ledger
    from lpswarm.textgen import corpus
    conf = _load_config(args.config)
    alphabet = get_alphabet(args.alphabet or "latin26")
    targets = _targets_from_args(args, alphabet)
    if args.wordlist:
        words = corpus.load_wordlist_file(args.wordlist)
        wl_name = Path(args.wordlist).name
    else:
        words = corpus.wordlist(min_len=1, limit=args.words)
        wl_name = f"corpus-top{args.words}"
    bc = _apply(BaselineConfig, conf.get("baseline", {}), {
        "families": _csv_strs(args.families), "wordlist_name": wl_name,
        "max_attempts_per_family": args.max_attempts, "timeout_s": args.timeout,
        "columnar_max_width": args.columnar_max_width})
    user_key_texts = load_key_texts(args.running_key_texts or [], alphabet)
    oracle = FullOracle(alphabet, _oracle_cfg(args, conf))
    summary_rows = []
    from lpswarm.reports import default_report_dir, target_entry, write_run_report
    report_dir = Path(args.report_dir) if args.report_dir else default_report_dir("baseline")
    entries: list[dict] = []
    cmdline = "lpswarm " + " ".join(sys.argv[1:])
    with Ledger(args.ledger) as led:
        for ct, label, page_range, synthetic, demo_keys, breaks in targets:
            if len(ct) < max(args.min_length, oracle.min_length):
                print(f"skip {label}: only {len(ct)} symbols under alphabet {alphabet.name} "
                      f"(minimum {max(args.min_length, oracle.min_length)}, --min-length)")
                continue
            print(f"\n== {label}  ({len(ct)} symbols)")
            tgt = Target(alphabet, ct, label, page_range=page_range, is_synthetic=synthetic,
                         breaks=breaks)
            t_start = time.monotonic()
            res = run_baseline(tgt, led, oracle, words, bc, user_key_texts + demo_keys,
                               progress=not args.quiet)
            entries.append(target_entry(led, res.target_id, label, len(ct), oracle=oracle,
                                        elapsed_s=time.monotonic() - t_start))
            write_run_report(report_dir, "Brute-force baseline", cmdline, entries)
            n_final = sum(1 for r in res.final if r["passed_final"])
            total = led.attempt_count(res.target_id)
            summary_rows.append((label, len(ct), total, n_final))
            print(f"final check: {n_final} attempt(s) pass at alpha/{total} over all attempts on "
                  "this target")
            leads = led.leads(res.target_id, include_near_miss=True, limit=args.top)
            for r in leads:
                tag = "FINAL" if r["passed_final"] else "     "
                print(f"  {tag} {r['verdict']:<9} {r['cipher_family']:<12} "
                      f"key={r['key_preview']!s:<20} params={r['params_json']:<30} "
                      f"margin={r['combined'] - r['threshold']:+.3f}  {r['plaintext_preview']}")
            if not leads:
                print("  no passes or near misses: everything tried is recorded as ruled out")
        print(f"\nledger: {args.ledger}  " + ", ".join(f"{k}={v}" for k, v in led.counts().items()))
        print(f"report: {report_dir / 'report.md'}")
    if len(summary_rows) > 1:
        print("\ntarget summary (symbols, attempts on target, final passes):")
        for label, n, total, nf in summary_rows:
            print(f"  {label[:50]:<50} {n:>6} {total:>9} {nf:>4}")
    return 0


def _auto_brief(args, router, alphabet, ct, label, values) -> str:
    """Ask the --auto-brief model for a brief on this target; '' if it is unavailable."""
    import numpy as np
    from lpswarm.router.adapters import AdapterError
    from lpswarm.router.limits import RateLimited
    from lpswarm.router.router import BudgetExceeded
    from lpswarm.swarm.generators import MAX_BRIEF_CHARS, GenContext, build_brief_prompt
    context = ""
    if args.brief_context and Path(args.brief_context).is_file():
        from lpswarm.textio import read_text
        context = read_text(args.brief_context).strip()
    ctx = GenContext(label, alphabet, np.asarray(ct), 0, 8, alphabet_values=values, task_id=label)
    from lpswarm.router.base import Role
    try:
        # A supervisor-role model (Opus) or any proposer (e.g. Codex briefing itself).
        roles = router.spec(args.auto_brief).roles
        role = "supervisor" if Role.SUPERVISOR in roles else "proposer"
        c = router.complete(args.auto_brief, build_brief_prompt(ctx, context), role=role,
                            task_id=f"{label}#brief", temperature=0.4, max_tokens=1500)
    except (RateLimited, BudgetExceeded, AdapterError, ValueError) as exc:
        print(f"auto-brief skipped ({args.auto_brief}): {str(exc)[:200]}", flush=True)
        return ""
    text = c.text.strip()[:MAX_BRIEF_CHARS]
    print(f"brief from {args.auto_brief} ({len(text)} chars):", flush=True)
    for line in text.splitlines():
        if line.strip():
            print(f"  | {line[:200]}", flush=True)
    return text


def cmd_swarm(args) -> int:
    from lpswarm.executor import Target
    from lpswarm.ledger import Ledger
    from lpswarm.router import Router
    from lpswarm.swarm import LLMGenerator, ModelRanker, RandomProgramGenerator, SwarmConfig, run_swarm
    conf = _load_config(args.config)
    alphabet = get_alphabet(args.alphabet or "latin26")
    targets = _targets_from_args(args, alphabet)
    names = _csv_strs(args.generators) or ("random_program",)
    model_names = [g for g in names if g != "random_program"]
    if (model_names or args.ranker) and not args.models:
        raise SystemExit("model generators/ranker need --models config/models.toml")
    values = None
    if args.alphabet and Path(args.alphabet).is_file():
        from lpswarm.textio import read_text
        values = json.loads(read_text(args.alphabet)).get("values")
    oracle = FullOracle(alphabet, _oracle_cfg(args, conf))
    sc = _apply(SwarmConfig, conf.get("swarm", {}), {
        "rounds": args.rounds, "per_round": args.per_round, "max_attempts": args.max_attempts,
        "timeout_s": args.timeout, "parallel": False if args.serial else None})
    with Ledger(args.ledger) as led:
        # Model calls are counted in one shared spend ledger (also used by tiertest and
        # doctor), so per-model USD caps and call-per-window caps hold across all runs.
        spend = Ledger(args.spend_ledger) if args.models else None
        router = Router.from_toml(args.models, ledger=spend, global_max_usd=args.max_usd) \
            if args.models else None
        gens = []
        for g in names:
            if g == "random_program":
                gens.append(RandomProgramGenerator(seed=args.seed or 0))
            else:
                router.spec(g)
                gens.append(LLMGenerator(router, g))
        ranker = ModelRanker(router, args.ranker) if args.ranker else None
        brief = ""
        if args.brief_file:
            from lpswarm.textio import read_text
            brief = read_text(args.brief_file).strip()
            print(f"brief for the generators ({len(brief)} chars): {brief[:200]}"
                  + ("..." if len(brief) > 200 else ""))
        from dataclasses import asdict as _asdict
        from lpswarm.reports import default_report_dir, target_entry, write_run_report
        report_dir = Path(args.report_dir) if args.report_dir else default_report_dir("swarm")
        entries: list[dict] = []
        cmdline = "lpswarm " + " ".join(sys.argv[1:])

        from lpswarm.router.limits import pause_text

        def usage_lines() -> list[str]:
            if not router:
                return []
            out = ["Model usage (spend ledger): " + ", ".join(
                f"{n} ${router.spent(n):.4f}" for n in router.names()), ""]
            for n in router.names():
                st = router.window_status(n)
                if st["cap"] or st["paused_until"]:
                    out.append(f"- {n}: {st['calls']} call(s) in the last {st['window_hours']:g}h "
                               f"(cap {st['cap'] or 'none'})"
                               + pause_text(st))
            return out + [""]
        for ct, label, page_range, synthetic, _, breaks in targets:
            if len(ct) < max(args.min_length, oracle.min_length):
                print(f"skip {label}: only {len(ct)} symbols (minimum "
                      f"{max(args.min_length, oracle.min_length)}, --min-length); too short to judge")
                continue
            from lpswarm.reports import short_note
            if short_note(len(ct)):
                print(f"note: {short_note(len(ct))}")
            print(f"\n== {label}  ({len(ct)} symbols)")
            tgt_brief = brief
            if args.auto_brief and router is not None:
                tgt_brief = "\n\n".join(x for x in (_auto_brief(args, router, alphabet, ct, label,
                                                                  values), brief) if x)
            res = run_swarm(Target(alphabet, ct, label, page_range=page_range, is_synthetic=synthetic,
                                   breaks=breaks),
                            led, oracle, gens, sc, ranker=ranker, alphabet_values=values,
                            progress=not args.quiet, brief=tgt_brief)
            n_final = sum(1 for r in res.final if r["passed_final"])
            print(f"stopped: {res.stopped or 'rounds done'}; final passes: {n_final}")
            entries.append(target_entry(led, res.target_id, label, len(ct), oracle=oracle, stopped=res.stopped,
                                        stats={k: _asdict(v) for k, v in res.stats.items()},
                                        elapsed_s=res.elapsed_s))
            write_run_report(report_dir, "Swarm run", cmdline, entries, usage_lines())
            from lpswarm.reports import chance_text
            for ld in entries[-1]["leads"][: args.top]:
                tag = "FINAL" if ld["final"] else "     "
                ch = chance_text(ld.get("chance"))
                print(f"  {tag} {ld['verdict']:<9} by {ld['by']:<16} {ld['key']}"
                      + (f"  [{ch}]" if ch else "") + f"\n        {ld['plaintext']}")
        if entries:
            print(f"\nreport: {report_dir / 'report.md'}")
        if router:
            print(f"model spend ({args.spend_ledger}): " + ", ".join(
                f"{n}=${router.spent(n):.4f}" for n in router.names()))
            spend.close()
    return 0


def cmd_tiertest(args) -> int:
    from lpswarm.validation.tiertest import TierConfig, run_tiertest
    conf = _load_config(args.config)
    over = {"arms": _csv_strs(args.arms), "lengths": _csv_ints(args.lengths),
            "cases_per_length": args.cases, "rounds": args.rounds, "per_round": args.per_round,
            "max_attempts": args.max_attempts, "ranker": args.ranker, "models_config": args.models,
            "max_usd": args.max_usd, "seed": args.seed, "out_dir": args.out,
            "difficulty": args.difficulty, "alphabet": args.alphabet,
            "spend_ledger": args.spend_ledger, "word_breaks": args.word_breaks or None,
            "resume": args.resume or None,
            "case_families": _csv_strs(args.case_families)}
    if args.quick:
        over.update(lengths=over["lengths"] or (100,), cases_per_length=args.cases or 2,
                    rounds=args.rounds or 2, per_round=args.per_round or 4)
    tc = _apply(TierConfig, conf.get("tiertest", {}), over)
    oc = _oracle_cfg(args, conf)
    if args.quick and args.null_samples is None:
        oc = dataclasses.replace(oc, null_samples=500)
    res = run_tiertest(tc, oc, progress=not args.quiet)
    print(f"\nwrote {Path(tc.out_dir) / 'tiertest.md'}")
    for s in res["summary"]:
        if s["length"] == "all":
            print(f"  {s['arm']:<20} recall {s['recall']:.2f} ({s['recovered']}/{s['cases']})  "
                  f"attempts {s['attempts']:<8} calls {s['model_calls']:<5} ${s['usd']:.4f}")
    return 0


def cmd_doctor(args) -> int:
    from lpswarm.doctor import print_report, run_checks
    models = args.models
    if models is None and Path("config/models.toml").is_file():
        models = "config/models.toml"
    ledgers = list(args.ledger or [])
    if not ledgers:
        ledgers = [p for p in ("reports/model_spend.sqlite",) if Path(p).is_file()]
    return print_report(run_checks(models, ping=args.ping, ledgers=ledgers))


def cmd_overnight(args) -> int:
    from lpswarm.ledger import Ledger
    from lpswarm.overnight import Overnight, latest_unfinished, load_config
    from lpswarm.router import Role, Router
    cfg = load_config(args.config)
    if args.until:
        cfg.until = args.until
    if args.serial:
        cfg.max_parallel = 1
    base = Path("reports") / "overnight"
    run_dir = Path(args.run_dir) if args.run_dir else None
    if run_dir is None and not args.new:
        run_dir = latest_unfinished(base)
        if run_dir is not None:
            print(f"resuming {run_dir} (use --new to start a fresh run)")
    if run_dir is None:
        run_dir = base / time.strftime("%Y%m%d-%H%M")
    router = None
    spend = None
    if Path(cfg.models).is_file():
        spend = Ledger(cfg.spend_ledger)
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            router = Router.from_toml(cfg.models, ledger=spend)
        for w in caught:   # e.g. "prices are 0": one readable line instead of a traceback-ish warning
            print(f"[overnight] note: {w.message}", flush=True)
        if cfg.supervisor:
            if Role.SUPERVISOR not in router.spec(cfg.supervisor).roles:
                raise SystemExit(f"model {cfg.supervisor} needs roles = [\"supervisor\"] in {cfg.models}")
    elif cfg.supervisor:
        raise SystemExit(f"supervisor {cfg.supervisor} configured but {cfg.models} not found")
    run = Overnight(cfg, run_dir, publish=False if args.no_publish else None, router=router,
                    retry_failed=args.retry_failed, echo_jobs=not args.quiet_jobs)
    try:
        st = run.run()
    finally:
        if spend is not None:
            spend.close()
    print(f"\nsummary: {run_dir / 'SUMMARY.md'}  (status: {st['status']})")
    return 0


def cmd_ruled_out(args) -> int:
    from lpswarm.ledger import Ledger
    _require_ledger(args.ledger)
    with Ledger(args.ledger) as led:
        rows = led.ruled_out()
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        print(f"{r['label']:<40} {r['cipher_family']:<12} attempts={r['attempts']:<8} "
              f"near={r['near_misses']:<4} by={r['proposer_model']}/{r['proposer_role']}  "
              f"{r['description']}")
    if not rows:
        print("nothing ruled out yet")
    return 0


def cmd_leads(args) -> int:
    from lpswarm.ledger import Ledger
    _require_ledger(args.ledger)
    with Ledger(args.ledger) as led:
        rows = led.leads(include_near_miss=args.near_miss, limit=args.top,
                         final_only=args.final_only)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        tag = {1: "FINAL", 0: "     ", None: "  ?  "}[r["passed_final"]]
        print(f"{tag} {r['verdict']:<9} {r['cipher_family']:<12} key={r['key_preview']!s:<20} "
              f"margin={r['combined'] - r['threshold']:+.3f} n={r['attempt_count_at_scoring']:<7} "
              f"{r['plaintext_preview']}")
    if not rows:
        print("no leads")
    return 0


def cmd_encode(args) -> int:
    alphabet = get_alphabet(args.alphabet or "latin26")
    from lpswarm.textio import read_text
    text = read_text(args.file)
    skipped: list[str] = []
    arr = alphabet.encode(text, skipped=skipped, glyphs_only=args.glyphs_only)
    dropped = sorted({ch for ch in skipped if not ch.isspace()})
    print(f"alphabet {alphabet.name} (size {alphabet.size}); {len(arr)} symbols")
    print("tokens:", alphabet.decode(arr[:200]))
    print("ints:  ", " ".join(str(int(x)) for x in arr[:60]))
    if dropped:
        print("characters not in the alphabet (dropped):", " ".join(dropped[:80]))
    return 0


def _require_ledger(path: str) -> None:
    if not Path(path).exists():
        raise SystemExit(f"ledger not found: {path}")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="lpswarm", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="run the validation harness")
    _add_oracle_args(p)
    p.add_argument("--families", help="comma list (default: all)")
    p.add_argument("--lengths", help="comma list, e.g. 20,40,60,100,200")
    p.add_argument("--cases", type=int, help="cases per family x length (default 5)")
    p.add_argument("--decoys", type=int, help="decoy keys per word-keyed case (default 500)")
    p.add_argument("--difficulty", choices=("easy", "medium", "hard"))
    p.add_argument("--seed", type=int)
    p.add_argument("--out", help="report directory (default reports)")
    p.add_argument("--quick", action="store_true", help="small fast run")
    p.add_argument("--word-breaks", action="store_true",
                   help="give the oracle the plaintext's word breaks (as Liber Primus pages show)")
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("null-check", help="oracle FPR on fresh nulls")
    _add_oracle_args(p)
    p.add_argument("--lengths")
    p.add_argument("--samples", type=int, default=2000)
    p.set_defaults(func=cmd_null_check)

    p = sub.add_parser("baseline", help="brute-force baseline into the ledger")
    _add_oracle_args(p)
    p.add_argument("--ciphertext", nargs="+", help="text file(s); one target per file")
    p.add_argument("--manifest", help="section manifest JSON (e.g. data/lp/manifest.json); "
                   "one target per section")
    p.add_argument("--sections", help="comma list of manifest indexes, or unsolved / solved / all "
                   "(default all)")
    p.add_argument("--glyphs-only", action="store_true",
                   help="read --ciphertext files by exact glyphs only (manifest always does)")
    p.add_argument("--no-word-breaks", action="store_true",
                   help="ignore word separators in the ciphertext")
    p.add_argument("--demo", help="synthetic target FAMILY:LENGTH, e.g. vigenere:120")
    p.add_argument("--difficulty", choices=("easy", "medium", "hard"))
    p.add_argument("--seed", type=int)
    p.add_argument("--label")
    p.add_argument("--page-range")
    p.add_argument("--ledger", default="ledger.sqlite")
    p.add_argument("--report-dir", help="where report.md/report.json go (default "
                   "reports/baseline-<timestamp>)")
    p.add_argument("--wordlist", help="word list file (one word per line); default corpus words")
    p.add_argument("--words", type=int, default=5000, help="corpus words to use if no --wordlist")
    p.add_argument("--families")
    p.add_argument("--running-key-texts", nargs="*", help="files or folders of .txt key texts")
    p.add_argument("--columnar-max-width", type=int)
    p.add_argument("--max-attempts", type=int, help="new attempts per family")
    p.add_argument("--timeout", type=float, help="seconds per family")
    p.add_argument("--min-length", type=int, default=20,
                   help="skip targets shorter than this many symbols (default 20: shorter text "
                        "cannot be judged)")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_baseline)

    def add_targets(p):
        p.add_argument("--ciphertext", nargs="+", help="text file(s); one target per file")
        p.add_argument("--manifest", help="section manifest JSON; one target per section")
        p.add_argument("--sections", help="comma list of manifest indexes, or unsolved / solved / all")
        p.add_argument("--demo", help="synthetic target FAMILY:LENGTH (e.g. program:120)")
        p.add_argument("--glyphs-only", action="store_true")
        p.add_argument("--difficulty", choices=("easy", "medium", "hard"))
        p.add_argument("--seed", type=int)
        p.add_argument("--label")
        p.add_argument("--page-range")
        p.add_argument("--no-word-breaks", action="store_true",
                       help="ignore word separators in the ciphertext")

    p = sub.add_parser("swarm", help="Phase 3: model/random generators propose cipher programs")
    _add_oracle_args(p)
    add_targets(p)
    p.add_argument("--ledger", default="ledger.sqlite")
    p.add_argument("--report-dir", help="where report.md/report.json go (default "
                   "reports/swarm-<timestamp>)")
    p.add_argument("--models", help="models TOML (see config/models.example.toml)")
    p.add_argument("--generators", help="comma list: random_program and/or model names")
    p.add_argument("--ranker", help="model name with the weighting role")
    p.add_argument("--rounds", type=int)
    p.add_argument("--per-round", type=int)
    p.add_argument("--max-attempts", type=int, help="new attempts per target")
    p.add_argument("--max-usd", type=float, help="global model spend cap (spend ledger)")
    p.add_argument("--spend-ledger", default="reports/model_spend.sqlite",
                   help="where model calls, spend and usage-limit pauses are logged (shared by "
                        "swarm, tiertest and doctor)")
    p.add_argument("--timeout", type=float, help="seconds per target")
    p.add_argument("--min-length", type=int, default=20,
                   help="skip targets shorter than this many symbols (default 20: shorter text "
                        "cannot be judged)")
    p.add_argument("--brief-file", help="text file with direction for the model generators "
                   "(written by the overnight supervisor when it delegates a job)")
    p.add_argument("--auto-brief", metavar="MODEL",
                   help="before each target, ask this supervisor-role model (e.g. "
                        "claude-supervisor) to write a brief for the generators")
    p.add_argument("--brief-context", help="text file with results so far on this target, shown "
                   "to the --auto-brief model (written by the overnight runner)")
    p.add_argument("--serial", action="store_true",
                   help="call generators one at a time (default: generators on different "
                        "backends, e.g. Codex and a local GPU, are called at the same time)")
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_swarm)

    p = sub.add_parser("tiertest", help="Phase 3: compare generators against the baselines")
    _add_oracle_args(p)
    p.add_argument("--arms", help="comma list: baseline, random_program[:N], model names")
    p.add_argument("--models")
    p.add_argument("--ranker")
    p.add_argument("--case-families", help="cipher families of the test cases (default program)")
    p.add_argument("--lengths")
    p.add_argument("--cases", type=int, help="cases per length")
    p.add_argument("--difficulty", choices=("easy", "medium", "hard"))
    p.add_argument("--rounds", type=int)
    p.add_argument("--per-round", type=int)
    p.add_argument("--max-attempts", type=int)
    p.add_argument("--max-usd", type=float)
    p.add_argument("--word-breaks", action="store_true",
                   help="give the oracle the plaintext's word breaks")
    p.add_argument("--resume", action="store_true",
                   help="continue an interrupted run in the same --out folder (keeps finished cases)")
    p.add_argument("--spend-ledger", help="where model calls are logged (default "
                   "reports/model_spend.sqlite; never deleted, so caps are cumulative)")
    p.add_argument("--seed", type=int)
    p.add_argument("--out")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_tiertest)

    p = sub.add_parser("doctor", help="check Python, data, models config, Ollama and API keys")
    p.add_argument("--models", help="models TOML (default config/models.toml if present)")
    p.add_argument("--ping", action="store_true",
                   help="send one tiny prompt to each healthy model (costs a little on paid APIs)")
    p.add_argument("--ledger", nargs="*", help="spend ledger(s) to read call counts and pauses "
                   "from (default: reports/model_spend.sqlite)")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("overnight", help="run a queue of jobs unattended, with SUMMARY.md, "
                       "resume, optional supervisor and publishing")
    p.add_argument("--config", default="config/overnight.toml")
    p.add_argument("--run-dir", help="run folder (default: resume the latest unfinished run in "
                   "reports/overnight, else start a new one)")
    p.add_argument("--new", action="store_true", help="start a new run even if one is unfinished")
    p.add_argument("--until", help="stop at this local time, HH:MM (resumable later)")
    p.add_argument("--no-publish", action="store_true", help="do not push results to GitHub")
    p.add_argument("--retry-failed", action="store_true",
                   help="when resuming, run failed and blocked jobs again")
    p.add_argument("--serial", action="store_true",
                   help="one job at a time (default: up to max_parallel jobs on different backends)")
    p.add_argument("--quiet-jobs", action="store_true",
                   help="do not echo running jobs' log lines; only start/finish and heartbeats")
    p.set_defaults(func=cmd_overnight)

    for name, fn in (("ruled-out", cmd_ruled_out), ("leads", cmd_leads)):
        p = sub.add_parser(name)
        p.add_argument("--ledger", default="ledger.sqlite")
        p.add_argument("--json", action="store_true")
        if name == "leads":
            p.add_argument("--near-miss", action="store_true")
            p.add_argument("--final-only", action="store_true",
                           help="only attempts that survived the final check")
            p.add_argument("--top", type=int, default=50)
        p.set_defaults(func=fn)

    p = sub.add_parser("encode", help="show how a file is read under an alphabet")
    p.add_argument("file")
    p.add_argument("--glyphs-only", action="store_true")
    p.add_argument("--alphabet")
    p.set_defaults(func=cmd_encode)
    return ap


def _safe_console() -> None:
    """Windows consoles often use cp1252; replace unencodable glyphs instead of crashing."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    _safe_console()
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except (ValueError, FileNotFoundError, PermissionError, tomllib.TOMLDecodeError) as exc:
        # Expected user errors: show the message, not a traceback.
        print(f"lpswarm: error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("lpswarm: interrupted (completed attempts are saved in the ledger)", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
