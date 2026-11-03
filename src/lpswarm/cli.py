"""Command line: `lpswarm <command>` or `python -m lpswarm <command>`.

Commands:
  validate    run the validation harness, write reports/validation.{csv,md,json}
  null-check  measure the oracle's false-positive rate on fresh nulls
  baseline    brute-force a ciphertext (file or synthetic demo) into the ledger
  ruled-out   list hypotheses tried and failed, from a ledger
  leads       list passing (and optionally near-miss) attempts, from a ledger
  encode      show how a text file is read under an alphabet (sanity check)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import tomllib
from pathlib import Path
from typing import Any, Sequence

from lpswarm.alphabet import get_alphabet
from lpswarm.oracle import FullOracle, OracleConfig


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    return tomllib.loads(Path(path).read_text(encoding="utf-8"))


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
                  "difficulty": args.difficulty}
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


def cmd_baseline(args) -> int:
    from lpswarm.baseline import BaselineConfig, load_key_texts, run_baseline
    from lpswarm.executor import Target
    from lpswarm.ledger import Ledger
    from lpswarm.textgen import corpus
    conf = _load_config(args.config)
    alphabet = get_alphabet(args.alphabet or "latin26")
    if args.ciphertext:
        text = Path(args.ciphertext).read_text(encoding="utf-8")
        ct = alphabet.encode(text)
        label = args.label or Path(args.ciphertext).name
        synthetic = False
    elif args.demo:
        from lpswarm.textgen.synth import generate_case
        fam, _, length = args.demo.partition(":")
        case = generate_case(fam, int(length or 80), args.difficulty or "medium",
                             alphabet=alphabet, seed=args.seed or 0)
        ct = case.ciphertext
        label = f"demo:{fam}:{len(ct)}:{case.case_id}"
        synthetic = True
        print(f"demo target: {fam} length {len(ct)}; true params {case.params}")
    else:
        raise SystemExit("give --ciphertext FILE or --demo FAMILY:LENGTH")
    if len(ct) < 8:
        raise SystemExit(f"ciphertext has only {len(ct)} symbols under alphabet {alphabet.name}; "
                         "check --alphabet")
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
    key_texts = load_key_texts(args.running_key_texts or [], alphabet)
    oracle = FullOracle(alphabet, _oracle_cfg(args, conf))
    with Ledger(args.ledger) as led:
        tgt = Target(alphabet, ct, label, page_range=args.page_range, is_synthetic=synthetic)
        res = run_baseline(tgt, led, oracle, words, bc, key_texts, progress=not args.quiet)
        leads = led.leads(res.target_id, include_near_miss=True, limit=args.top)
        print(f"\nledger: {args.ledger}  " + ", ".join(f"{k}={v}" for k, v in led.counts().items()))
        if leads:
            print(f"\ntop {len(leads)} leads (pass / near_miss):")
            for r in leads:
                print(f"  {r['verdict']:<9} {r['cipher_family']:<12} key={r['key_preview']!s:<20} "
                      f"params={r['params_json']:<30} margin={r['combined'] - r['threshold']:+.3f}  "
                      f"{r['plaintext_preview']}")
        else:
            print("\nno passes or near misses: everything tried is recorded as ruled out")
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
        rows = led.leads(include_near_miss=args.near_miss, limit=args.top)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        print(f"{r['verdict']:<9} {r['cipher_family']:<12} key={r['key_preview']!s:<20} "
              f"margin={r['combined'] - r['threshold']:+.3f} n={r['attempt_count_at_scoring']:<7} "
              f"{r['plaintext_preview']}")
    if not rows:
        print("no leads")
    return 0


def cmd_encode(args) -> int:
    alphabet = get_alphabet(args.alphabet or "latin26")
    arr = alphabet.encode(Path(args.file).read_text(encoding="utf-8"))
    print(f"alphabet {alphabet.name} (size {alphabet.size}); {len(arr)} symbols")
    print("tokens:", alphabet.decode(arr[:200]))
    print("ints:  ", " ".join(str(int(x)) for x in arr[:60]))
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
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("null-check", help="oracle FPR on fresh nulls")
    _add_oracle_args(p)
    p.add_argument("--lengths")
    p.add_argument("--samples", type=int, default=2000)
    p.set_defaults(func=cmd_null_check)

    p = sub.add_parser("baseline", help="brute-force baseline into the ledger")
    _add_oracle_args(p)
    p.add_argument("--ciphertext", help="text file holding the ciphertext")
    p.add_argument("--demo", help="synthetic target FAMILY:LENGTH, e.g. vigenere:120")
    p.add_argument("--difficulty", choices=("easy", "medium", "hard"))
    p.add_argument("--seed", type=int)
    p.add_argument("--label")
    p.add_argument("--page-range")
    p.add_argument("--ledger", default="ledger.sqlite")
    p.add_argument("--wordlist", help="word list file (one word per line); default corpus words")
    p.add_argument("--words", type=int, default=5000, help="corpus words to use if no --wordlist")
    p.add_argument("--families")
    p.add_argument("--running-key-texts", nargs="*", help="files or folders of .txt key texts")
    p.add_argument("--columnar-max-width", type=int)
    p.add_argument("--max-attempts", type=int, help="new attempts per family")
    p.add_argument("--timeout", type=float, help="seconds per family")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_baseline)

    for name, fn in (("ruled-out", cmd_ruled_out), ("leads", cmd_leads)):
        p = sub.add_parser(name)
        p.add_argument("--ledger", default="ledger.sqlite")
        p.add_argument("--json", action="store_true")
        if name == "leads":
            p.add_argument("--near-miss", action="store_true")
            p.add_argument("--top", type=int, default=50)
        p.set_defaults(func=fn)

    p = sub.add_parser("encode", help="show how a file is read under an alphabet")
    p.add_argument("file")
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
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
