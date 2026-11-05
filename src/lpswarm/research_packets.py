"""Fixed review packets for small, bounded experiments.

A packet is a literal list of cipher-program proposals plus the exact command, counts, caps and
stop rule for running them through the *existing* swarm (a `scripted` proposer replays the list,
one reply per round), so the real oracle, ledger and comparison accounting apply unchanged.
Nothing here runs the oracle or calls a model: it only writes files and checks the proposals.

    python -m lpswarm.research_packets --out packets

Packets (from the Astra research note, development SHA f822be5):
  exp1_feedback     invertible neighbour/chain feedback, with and without word reset
  exp2_two_shear    determinant-one 2x2 Hill blocks (two shears), offset 0
  exp2b_all_shifts  the same with all 29 constant offsets (needs its own approval)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from lpswarm.alphabet import get_alphabet
from lpswarm.programs import compile_spec, decrypt, spec_hash
from lpswarm.textio import read_text

N = 29
MANIFEST = "data/lp/manifest.json"
ALPHABET = "data/alphabet/gematria_primus.json"
GENERATED_FROM = "development SHA f822be51e2e64c4979562e3cce497626c613f6e9 (Astra research note, 2026-11-05)"


# ----------------------------------------------------------------- proposals
def _spec(b: int, mix: dict | None = None) -> dict:
    s: dict = {"stream": {"kind": "constant", "value": b}, "combine": "sub"}
    if mix:
        s["mix"] = mix
    return s


def _reply(specs: list[dict], why: str) -> str:
    return json.dumps({"proposals": [{"spec": s, "why": why} for s in specs]}, sort_keys=True,
                      separators=(",", ":"))


def feedback_forms() -> list[tuple[str, dict]]:
    """Eight operator forms: kind x sign x reset, lag 1, previous direction."""
    out = []
    for kind in ("neighbor", "chain"):
        for sign, op in (("+", "add"), ("-", "sub")):
            for reset in ("none", "word"):
                out.append((f"{kind} {sign} reset={reset}",
                            {"kind": kind, "op": op, "lag": 1, "dir": "prev", "reset": reset,
                             "at": "before"}))
    return out


def exp1_replies() -> tuple[list[str], list[dict]]:
    replies, table = [], []
    for name, mix in feedback_forms():
        replies.append(_reply([_spec(b, mix) for b in range(N)], f"feedback form {name}, offset b"))
        table.append({"form": name, "proposals": N})
    replies.append(_reply([_spec(b) for b in range(N)], "control: constant shift only, no mixing"))
    table.append({"form": "control: constant shifts only", "proposals": N})
    return replies, table


def shear_matrices() -> list[tuple[str, list[int]]]:
    out = []
    for order in ("UL", "LU"):
        for a in (1, 2, 27, 28):
            for t in (1, 2, 27, 28):
                if order == "UL":          # U(a) L(t) = [[1+a*t, a], [t, 1]]
                    m = [(1 + a * t) % N, a % N, t % N, 1]
                else:                      # L(t) U(a) = [[1, a], [t, 1+a*t]]
                    m = [1, a % N, t % N, (1 + a * t) % N]
                out.append((f"{order} a={a} t={t}", m))
    return out


def _hill(m: list[int]) -> dict:
    return {"kind": "hill", "size": 2, "matrix": m, "at": "before"}


def exp2_replies(all_shifts: bool) -> tuple[list[str], list[dict]]:
    mats = shear_matrices()
    replies, table = [], []
    if not all_shifts:
        replies.append(_reply([_spec(0, _hill(m)) for _n, m in mats], "two-shear Hill block, b=0"))
        table.append({"form": "32 matrices, b=0", "proposals": len(mats)})
        replies.append(_reply([_spec(0)], "control: identity (no mixing, no shift)"))
        table.append({"form": "identity control", "proposals": 1})
    else:
        for b in range(N):
            replies.append(_reply([_spec(b, _hill(m)) for _n, m in mats],
                                  f"two-shear Hill block, b={b}"))
            table.append({"form": f"32 matrices, b={b}", "proposals": len(mats)})
        replies.append(_reply([_spec(b) for b in range(N)], "control: constant shifts only"))
        table.append({"form": "control: constant shifts only", "proposals": N})
    return replies, table


# -------------------------------------------------------------------- packets
PACKETS = {
    "exp1_feedback": {
        "title": "Invertible feedback: reset state at word boundaries, or continue it?",
        "sections": [13, 24, 25], "rounds": 9, "per_round": 29, "max_attempts": 300,
        "timeout": 900, "replies": lambda: exp1_replies(),
        "approved": "yes (initial envelope)",
        "mechanism": (
            "Decryption `p_i = z_i - b` where `z` is a single additive feedback stage over either the "
            "whole section or each parser word: `neighbor` (`z_i = c_i +/- c_(i-1)`) or `chain` "
            "(`z_i = c_i +/- z_(i-1)`), lag 1, direction `prev`, the first element of each span "
            "unchanged, then a constant offset b = 0..28 subtracted afterwards."),
        "overlap": [
            "`neighbor` with sub and no reset is exactly a ciphertext autokey with primer 0; `chain` "
            "with sub and no reset is exactly a plaintext autokey with primer 0 (tested). Earlier "
            "runs may have covered those with a constant shift; coverage is unknown until the "
            "local ledgers are compared. The new information is the reset comparison and the "
            "add forms.",
            "`at: after` is deliberately excluded: with a constant stream it would mostly repeat "
            "translated versions of these forms."],
        "not_implemented": [
            "The false-boundary control (rotating the list of word lengths by one word, 8 forms at "
            "b=0, 24 diagnostic transforms) needs custom word breaks, which the swarm cannot take. "
            "It is not part of this packet.",
            "Lag 2 and the `next` direction (a second envelope of 2,784 candidates in Astra's note) "
            "are not generated."],
    },
    "exp2_two_shear": {
        "title": "Two-shear Hill blocks without a full matrix enumeration (b = 0)",
        "sections": [24, 25, 16], "rounds": 2, "per_round": 32, "max_attempts": 40,
        "timeout": 600, "replies": lambda: exp2_replies(False),
        "approved": "yes (initial envelope, b=0 only)",
        "mechanism": (
            "Blocks of two runes `(c_2j, c_2j+1)` starting at rune 0, across words, multiplied by "
            "`M = U(a) L(t)` or `L(t) U(a)` with a, t in {1, 2, 27, 28} (determinant 1, both "
            "coordinates mix), then `b` subtracted. The matrix is the DECRYPTION matrix. The "
            "selected sections have even length, so there is no partial trailing block."),
        "overlap": [
            "Any completed full 2x2 Hill sweep contains this family (the transmute lane's "
            "exhaustive Hill job did that on every unsolved section if it finished). Whether it "
            "ran, and on which targets, is unknown until the local ledgers are compared."],
        "not_implemented": [
            "The even/odd histogram and 29x29 pair diagnostic and the false-alignment control are "
            "separate diagnostics (see `research_diagnostics`), not part of this packet."],
    },
    "exp2b_all_shifts": {
        "title": "Two-shear Hill blocks with all 29 constant offsets",
        "sections": [24, 25, 16], "rounds": 30, "per_round": 32, "max_attempts": 1000,
        "timeout": 1200, "replies": lambda: exp2_replies(True),
        "approved": "NO: needs separate approval after exp2_two_shear is reviewed",
        "mechanism": "As exp2_two_shear, for every b = 0..28.",
        "overlap": ["As exp2_two_shear."],
        "not_implemented": ["Do not expand to all a, t in 1..28 (136,416 candidates across these "
                            "targets with all shifts); that is a different envelope."],
    },
}


def load_sections(manifest: str = MANIFEST, alphabet_path: str = ALPHABET,
                  indexes: list[int] | None = None) -> dict[int, dict]:
    """Encoded sections (ints), word breaks, label and recorded file hash, by manifest index."""
    alpha = get_alphabet(alphabet_path)
    mpath = Path(manifest)
    man = json.loads(read_text(mpath))
    out = {}
    for sec in man["sections"]:
        if indexes is not None and sec["index"] not in indexes:
            continue
        raw = read_text(mpath.parent / sec["file"])
        breaks: list[int] = []
        ct = alpha.encode(raw, glyphs_only=True, boundaries=breaks)
        out[sec["index"]] = {"ct": np.asarray(ct, dtype=np.int64), "breaks": breaks,
                             "label": f"{sec.get('part', '')}:{sec['label']}",
                             "runes": int(len(ct)), "sha256": sec.get("sha256"),
                             "clean": not (sec.get("replacement_chars") or sec.get("unknown_runes"))}
    return out


def distinct_decryptions(replies: list[str], sections: dict[int, dict]) -> dict[int, dict]:
    """Per target: how many of the packet's candidate decryptions are identical (read-only)."""
    alpha = get_alphabet(ALPHABET)
    specs = [compile_spec(p["spec"], alpha) for r in replies for p in json.loads(r)["proposals"]]
    out = {}
    for idx, sec in sections.items():
        seen: dict[str, int] = {}
        for s in specs:
            pt = decrypt(sec["ct"], s, alpha.size, breaks=sec["breaks"])
            seen[hashlib.sha256(pt.astype(np.int16).tobytes()).hexdigest()] = 1
        out[idx] = {"candidates": len(specs), "distinct_decryptions": len(seen)}
    return out


def validate(replies: list[str], per_round: int) -> list[dict]:
    """Compile every proposal with the current compiler; raise on anything invalid."""
    alpha = get_alphabet(ALPHABET)
    specs = []
    for r in replies:
        props = json.loads(r)["proposals"]
        if len(props) > per_round:
            raise ValueError(f"a reply has {len(props)} proposals; per_round is {per_round}")
        for p in props:
            specs.append(compile_spec(p["spec"], alpha))
    return specs


def render_packet(name: str, out_dir: Path, sections: dict[int, dict]) -> dict:
    cfg = PACKETS[name]
    replies, table = cfg["replies"]()
    specs = validate(replies, cfg["per_round"])
    if name.startswith("exp2"):
        odd = [i for i in cfg["sections"] if sections[i]["runes"] % 2]
        if odd:
            raise ValueError(f"sections {odd} have an odd length: not valid for the 2x2 Hill packet")
    per_target = len(specs)
    unique = len({spec_hash(s) for s in specs})
    pdir = out_dir / name
    pdir.mkdir(parents=True, exist_ok=True)
    body = json.dumps(replies, indent=1) + "\n"
    (pdir / "proposals.json").write_text(body, encoding="utf-8")
    digest = hashlib.sha256(body.encode()).hexdigest()
    rel = f"{out_dir.as_posix()}/{name}"
    (pdir / "models.toml").write_text(
        "# Scripted proposer: replays proposals.json, one reply per round. No keys, no model calls.\n"
        f'[models.packet-{name}]\nprovider = "scripted"\nmodel = "{name}"\nroles = ["proposer"]\n'
        f'replies_file = "{rel}/proposals.json"\n', encoding="utf-8")
    ids = ",".join(str(i) for i in cfg["sections"])
    cmd = (f"lpswarm swarm --manifest {MANIFEST} --alphabet {ALPHABET} --sections {ids} "
           f"--generators packet-{name} --models {rel}/models.toml "
           f"--spend-ledger {rel}/run/spend.sqlite --rounds {cfg['rounds']} "
           f"--per-round {cfg['per_round']} --max-attempts {cfg['max_attempts']} "
           f"--timeout {cfg['timeout']} --ledger {rel}/run/ledger.sqlite --report-dir {rel}/run")
    dup = distinct_decryptions(replies, {i: sections[i] for i in cfg["sections"]})
    L = [f"# Packet {name}: {cfg['title']}", "",
         f"Generated by `python -m lpswarm.research_packets` from {GENERATED_FROM}. "
         f"Approval: **{cfg['approved']}**. Nothing has been run.", "",
         "## What it tests", "", cfg["mechanism"], "",
         "## Targets", "", "| manifest id | source label | runes | recorded sha256 (section file) | clean |",
         "| ---: | --- | ---: | --- | --- |"]
    for i in cfg["sections"]:
        s = sections[i]
        L.append(f"| {i} | `{s['label']}` | {s['runes']} | `{(s['sha256'] or 'unknown')[:16]}` | "
                 f"{'yes' if s['clean'] else 'NO'} |")
    L += ["", "## Counts", "",
          f"Per target: **{per_target}** proposals in {len(replies)} rounds "
          f"(of which controls: {sum(t['proposals'] for t in table if t['form'].startswith(('control', 'identity')))}); "
          f"**{per_target * len(cfg['sections'])}** over {len(cfg['sections'])} targets. "
          f"Distinct specs in the packet: {unique} of {per_target}.", "",
          "| round | content | proposals |", "| ---: | --- | ---: |"]
    L += [f"| {k + 1} | {t['form']} | {t['proposals']} |" for k, t in enumerate(table)]
    L += ["", "Duplicate check (apply every candidate to each target, count distinct decryptions):", ""]
    L += [f"- section {i}: {d['distinct_decryptions']} distinct decryptions from {d['candidates']} "
          f"candidates" for i, d in dup.items()]
    L += ["", "## Run (only after review)", "",
          "First compare against recorded history (novelty is unknown until this is done):", "",
          "```powershell", "lpswarm coverage --latest 3 --out reports\\coverage", "```", "",
          "Then, from the repository folder:", "", "```powershell", cmd, "```", "",
          f"Caps: at most {cfg['max_attempts']} attempts and {cfg['timeout']} s per target. "
          "**Stop rule (literal):** stop at the first cap reached, on any invalid proposal, "
          "or on a section/transcription mismatch; report partial work as partial and do not raise "
          "a cap to finish. The swarm also stops a target after the round in which an in-run "
          "pass appears (`stop_on_pass`); that pass is a lead to inspect, not a result.", "",
          "## Accounting", "",
          "Every proposal is an ordinary attempt on its target and counts toward that target's "
          "end-of-search comparison total, controls included. Nothing in the oracle, null "
          "calibration, thresholds or budgets changes. Controls are labelled above so they can be "
          "reported separately.", "",
          "## Overlap with earlier work", ""]
    L += [f"- {x}" for x in cfg["overlap"]]
    L += ["", "## Not in this packet", ""] + [f"- {x}" for x in cfg["not_implemented"]]
    L += ["", "## Interpreting results", "",
          "A final-check survivor is a lead for independent inspection (full output, prefix and "
          "suffix, sustained structure), not a solution. If nothing passes and the controls "
          "behave, only this exact, single-stage, fixed envelope is weakened. After the run: "
          f"`lpswarm coverage --ledger {rel}/run/ledger.sqlite`.", "",
          f"`proposals.json` sha256: `{digest}`", ""]
    (pdir / "packet.md").write_text("\n".join(L), encoding="utf-8")
    return {"name": name, "per_target": per_target, "targets": cfg["sections"],
            "total": per_target * len(cfg["sections"]), "sha256": digest, "command": cmd,
            "distinct": dup}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_packets", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="packets")
    ap.add_argument("--only", action="append", choices=sorted(PACKETS))
    args = ap.parse_args(argv)
    names = args.only or list(PACKETS)
    need = sorted({i for n in names for i in PACKETS[n]["sections"]})
    sections = load_sections(indexes=need)
    out = Path(args.out)
    for n in names:
        r = render_packet(n, out, sections)
        print(f"{n}: {r['per_target']} per target x {len(r['targets'])} = {r['total']}; "
              f"sha256 {r['sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
