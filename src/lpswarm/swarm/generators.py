"""Hypothesis generators.

A generator sees a GenContext (ciphertext, alphabet, statistics, its own past
proposals with *coarse* verdicts, validation errors) and returns raw cipher
program specs. It never sees oracle scores, thresholds, or decrypted text.

- RandomProgramGenerator: non-LLM control, samples the program language.
- LLMGenerator:           asks a model (via the Router) for specs as JSON.
- ModelRanker:            optional cheap model that orders proposals (weighting role).
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.oracle.signals import index_of_coincidence
from lpswarm.programs import SEQUENCES
from lpswarm.programs.sampler import sample_spec
from lpswarm.programs.spec import GRID_READS


@dataclass
class Feedback:
    description: str
    verdict: str          # "fail" | "near_miss" | "pass" | "duplicate:<verdict>" | "invalid"


@dataclass
class GenContext:
    label: str
    alphabet: Alphabet
    ciphertext: np.ndarray
    round: int
    k: int
    history: list[Feedback] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    already_ruled_out: list[str] = field(default_factory=list)   # e.g. Phase 1 families tried
    alphabet_values: list[int] | None = None
    task_id: str = ""      # internal (cost attribution); never shown to the model
    style: str = ""        # per-model role hint: "exploratory" | "volume" | ""
    brief: str = ""        # direction written by the run supervisor for this job (optional)
    shared: str = ""       # cross-lane context: what other jobs tried here + the strategy note
    known_words: list = field(default_factory=list)   # verified keywords (solved-page notes + file)

    def stats(self) -> dict:
        c = self.ciphertext
        n = self.alphabet.size
        counts = np.bincount(c.astype(int), minlength=n)
        top = sorted(range(n), key=lambda i: -counts[i])[:8]
        doubles = int(np.sum(c[1:] == c[:-1])) if len(c) > 1 else 0
        return {"length": int(len(c)), "ic_normalised": round(index_of_coincidence(c, n), 3),
                "most_common": [(self.alphabet.tokens[i], int(counts[i])) for i in top],
                "adjacent_doubles": doubles,
                "expected_doubles_if_random": round((len(c) - 1) / n, 1)}


@dataclass
class RawProposal:
    spec: Any
    why: str = ""


class RandomProgramGenerator:
    """Control arm: random specs from the same language the models use."""
    role = "proposer"

    def __init__(self, seed: int = 0, difficulty: str = "hard", name: str = "random_program"):
        self.rng = np.random.default_rng(seed)
        self.difficulty = difficulty
        self.model = name

    def propose(self, ctx: GenContext) -> list[RawProposal]:
        n = ctx.alphabet.size
        return [RawProposal(sample_spec(self.rng, n, None, self.difficulty, len(ctx.ciphertext)))
                for _ in range(ctx.k)]


# ------------------------------------------------------------------ prompting
LANGUAGE_DOC = """You propose ciphers in a small JSON language. A deterministic program decrypts
the ciphertext with each proposal and an independent statistical test judges the result.
You only learn a coarse verdict per proposal: "fail", "near_miss" or "pass".

Decryption of ciphertext symbols c (integers 0..N-1), in this order:
  1. "transpose": undo a transposition of the text (optional), exactly one of
       {"columnar": [order]}                   a permutation of 0..w-1, w <= 12
       {"grid": {"width": W, "read": R}}       the plaintext was written row by row into a grid
                                               of W columns (2..500; the last row may be short)
                                               and read out by R, one of: rows_reversed, columns,
                                               columns_reversed, boustrophedon_rows,
                                               boustrophedon_columns, diagonal, spiral_in,
                                               spiral_out
       {"railfence": {"rails": r}}             rail-fence zigzag with r rails (2..64)
       {"decimate": {"step": k}}               every k-th position, wrapping (k must share no
                                               factor with the text length; others are skipped)
     "transpose_range": [lo, hi]             with grid/railfence/decimate: try every width, rail
                                               count or step in lo..hi in one proposal (lo >= 2;
                                               a bound outside the allowed range makes the whole
                                               proposal invalid)
  2. "reverse_text": true                 read the text backwards (optional)
  2b. "mix": a transformation that combines a rune with its neighbours or works on small groups
     (optional); {"kind": ..., "at": "before"|"after"} runs it before (default) or after the
     skip/map/combine/stream steps below. Kinds:
       {"kind": "neighbor", "op": OP, "lag": 1..16, "dir": "next"|"prev", "times": 1..3}
            out_i = x_i OP x_(i+lag) (or x_(i-lag)); OP: add sub rsub mul div rdiv
       {"kind": "chain", "op": OP, "lag": 1..16, "dir": "prev"|"next"}  OP: add sub rsub mul div
            out_i = x_i OP out_(i-lag): the recursive form (running sums and differences)
       {"kind": "window", "size": 2..16}       out_i = sum of the last `size` symbols
       {"kind": "hill", "size": 2..4, "matrix": [row-major entries]}
            blocks of `size` symbols are multiplied by an invertible matrix mod N;
            {"kind": "hill", "size": 2, "exhaustive": true} tries EVERY invertible 2x2 matrix
            (about 680,000, a few minutes); for size 3 or 4 add "family": "circulant" |
            "upper_triangular" | "diagonal" with "exhaustive": true
       {"kind": "block_perm", "size": 2..8, "perm": [..]}  reorders symbols inside each block;
            "exhaustive": true tries every order
     neighbor/chain/window accept "reset": "word" (do not cross word boundaries; not with a
     transposition) or {"every": k}. Edges, partial blocks and segment starts are unchanged.
     Zero (and any non-invertible symbol) is absorbing for mul; div leaves it unchanged.
     A mix does not combine with skip_mode "resolve". With "chain" op "sub", lag 1 equals a
     plaintext autokey; neighbor op "sub", lag 1, dir "prev" equals a ciphertext autokey.
  3. "skip": [symbols]                    ciphertext symbols left as plaintext; the key
                                          stream does NOT advance there (optional)
     "skip_mode": "all" | "resolve"       "all": every occurrence is a literal (default);
                                          "resolve": each occurrence may be a literal or an
                                          encrypted symbol; the program picks per occurrence
                                          (not with autokey streams)
  4. "map": "identity" | "reverse"        reverse maps symbol i to N-1-i before combining
  5. "combine": "sub" | "add" | "beaufort"  p = c - k | c + k | k - c   (mod N)
  6. "stream": the key stream k_0, k_1, ... over non-skipped positions, one of
       {"kind": "constant", "value": 3}
       {"kind": "repeat", "key": [1, 2, 3]}  or  {"kind": "repeat", "word": "SOMEWORD"}
       {"kind": "autokey", "primer": [..] or "word": "..", "source": "plaintext"|"ciphertext"}
       {"kind": "sequence", "name": NAME, "offset": 0, "scale": 1, "add": 0}
          k_t = (scale * NAME[offset + t] + add) mod N, NAME in: %(sequences)s
  Autokey: with "source": "ciphertext" the primer only changes the first len(primer) plaintext
  symbols (every later symbol is c_i - c_(i-m)), so ONE proposal covers all primers; do not
  enumerate them. With "source": "plaintext" the primer feeds the whole chain, so primers matter.
  Optional "offset_range": [lo, hi] (at most 2000 values) tries every start offset of a
  repeat/sequence stream in one proposal. A repeat stream may instead be
  {"kind": "repeat", "exhaustive": true, "key_length": m} (m = 1..4): EVERY key of that length
  (29^4 is about 700,000 ciphers; "sub" and "add" try the same set, so use one). One proposal may
  expand to at most 5000 ciphers (1,000,000 for an exhaustive key space); it cannot combine
  exhaustive with offset_range. Wide sweeps are preferred over single guesses.
Symbols may be given as integers or as alphabet tokens (strings); words are spelled with tokens.
"""

EXAMPLES = """Examples of valid proposals (generic illustrations, not hints about this target):
  {"spec": {"stream": {"kind": "repeat", "word": "KEY"}, "combine": "sub"}, "why": "periodic key"}
  {"spec": {"stream": {"kind": "constant", "value": 3}, "combine": "add", "map": "reverse"},
   "why": "shift on a reversed alphabet"}
  {"spec": {"stream": {"kind": "sequence", "name": "primes", "offset": 0, "scale": 1, "add": 0},
            "combine": "sub", "skip": [0]}, "why": "prime-number key, symbol 0 left in clear"}
  {"spec": {"stream": {"kind": "sequence", "name": "fibonacci"}, "combine": "beaufort",
            "offset_range": [0, 50]}, "why": "Fibonacci key, unknown start"}
  {"spec": {"stream": {"kind": "autokey", "word": "SEED", "source": "plaintext"}, "combine": "sub"},
   "why": "autokey with a short primer"}
  {"spec": {"stream": {"kind": "constant", "value": 3}, "combine": "sub",
            "transpose": {"grid": {"width": 9, "read": "columns"}}, "transpose_range": [2, 60]},
   "why": "Caesar after a column-read grid of unknown width"}
  {"spec": {"stream": {"kind": "sequence", "name": "primes"}, "offset_range": [0, 200],
            "combine": "sub", "transpose": {"railfence": {"rails": 3}}, "transpose_range": [2, 12]},
   "why": "rail fence of unknown depth, then a prime key at unknown offset"}
  {"spec": {"stream": {"kind": "repeat", "exhaustive": true, "key_length": 3}, "combine": "sub"},
   "why": "every 3-symbol periodic key"}
  {"spec": {"stream": {"kind": "constant", "value": 0}, "combine": "sub",
            "mix": {"kind": "hill", "size": 2, "exhaustive": true}},
   "why": "pairs of runes mixed by an unknown 2x2 matrix"}
  {"spec": {"stream": {"kind": "sequence", "name": "primes", "offset": 0}, "combine": "sub",
            "mix": {"kind": "neighbor", "op": "add", "lag": 1, "dir": "next", "reset": "word"},
            "offset_range": [0, 200]},
   "why": "each rune summed with the next one inside its word, then a prime key"}
"""


def _stream_schema() -> dict:
    ints = {"type": "array", "items": {"type": "integer"}, "minItems": 1, "maxItems": 64}
    return {"anyOf": [
        {"type": "object", "properties": {"kind": {"enum": ["constant"]}, "value": {"type": "integer"}},
         "required": ["kind", "value"], "additionalProperties": False},
        {"type": "object", "properties": {"kind": {"enum": ["repeat"]}, "key": ints,
                                          "word": {"type": "string"}, "offset": {"type": "integer"},
                                          "exhaustive": {"type": "boolean"},
                                          "key_length": {"type": "integer", "minimum": 1,
                                                         "maximum": 4}},
         "required": ["kind"], "additionalProperties": False},
        {"type": "object", "properties": {"kind": {"enum": ["autokey"]}, "primer": ints,
                                          "word": {"type": "string"},
                                          "source": {"enum": ["plaintext", "ciphertext"]}},
         "required": ["kind"], "additionalProperties": False},
        {"type": "object", "properties": {"kind": {"enum": ["sequence"]},
                                          "name": {"enum": sorted(SEQUENCES)},
                                          "offset": {"type": "integer"}, "scale": {"type": "integer"},
                                          "add": {"type": "integer"}},
         "required": ["kind", "name"], "additionalProperties": False},
    ]}


def proposal_schema(max_items: int = 16) -> dict:
    """JSON schema for a proposals reply; models with structured output are held to it."""
    spec = {"type": "object", "properties": {
        "stream": _stream_schema(),
        "combine": {"enum": ["sub", "add", "beaufort"]},
        "map": {"enum": ["identity", "reverse"]},
        "skip": {"type": "array", "items": {"anyOf": [{"type": "integer"}, {"type": "string"}]},
                 "maxItems": 8},
        "skip_mode": {"enum": ["all", "resolve"]},
        "reverse_text": {"type": "boolean"},
        "transpose": {"anyOf": [
            {"type": "object", "properties": {
                "columnar": {"type": "array", "items": {"type": "integer"}, "minItems": 2,
                             "maxItems": 12}},
             "required": ["columnar"], "additionalProperties": False},
            {"type": "object", "properties": {"grid": {"type": "object", "properties": {
                "width": {"type": "integer"}, "read": {"enum": list(GRID_READS)}},
                "required": ["width", "read"], "additionalProperties": False}},
             "required": ["grid"], "additionalProperties": False},
            {"type": "object", "properties": {"railfence": {"type": "object", "properties": {
                "rails": {"type": "integer"}}, "required": ["rails"], "additionalProperties": False}},
             "required": ["railfence"], "additionalProperties": False},
            {"type": "object", "properties": {"decimate": {"type": "object", "properties": {
                "step": {"type": "integer"}}, "required": ["step"], "additionalProperties": False}},
             "required": ["decimate"], "additionalProperties": False}]},
        "transpose_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
        "mix": {"type": "object", "properties": {
            "kind": {"enum": ["neighbor", "chain", "window", "hill", "block_perm"]},
            "at": {"enum": ["before", "after"]},
            "op": {"enum": ["add", "sub", "rsub", "mul", "div", "rdiv"]},
            "lag": {"type": "integer"}, "dir": {"enum": ["next", "prev"]},
            "times": {"type": "integer"}, "size": {"type": "integer"},
            "matrix": {"type": "array", "items": {"type": "integer"}, "maxItems": 16},
            "perm": {"type": "array", "items": {"type": "integer"}, "maxItems": 8},
            "exhaustive": {"type": "boolean"},
            "family": {"enum": ["full", "circulant", "upper_triangular", "diagonal"]},
            "reset": {"anyOf": [{"enum": ["none", "word"]}, {"type": "object", "properties": {
                "every": {"type": "integer"}}, "required": ["every"], "additionalProperties": False}]}},
            "required": ["kind"], "additionalProperties": False},
        "offset_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
    }, "required": ["stream"], "additionalProperties": False}
    return {"type": "object", "properties": {"proposals": {
        "type": "array", "maxItems": max_items, "items": {
            "type": "object", "properties": {"spec": spec, "why": {"type": "string"}},
            "required": ["spec", "why"], "additionalProperties": False}}},
        "required": ["proposals"], "additionalProperties": False}


STYLE_HINTS = {
    "exploratory": ("Your role: explorer. Favour structurally different ideas (different stream "
                    "kinds, maps, skip rules, transpositions) over small variations, and say in "
                    "'why' what each one tests."),
    "volume": ("Your role: brute force. Every proposal should sweep: give sequence and repeat "
               "streams an \"offset_range\": [lo, hi] of up to 2000 values (one proposal then "
               "tests every offset), rather than a single fixed offset. Vary the stream, combine "
               "mode and skip rule between proposals, and avoid families already tried."),
}


MAX_BRIEF_CHARS = 2000
MAX_REFINE_CHARS = 1200      # a refinement written by the proposer model under the supervisor's brief
MAX_BRIEF_TOTAL = 4500       # supervisor brief + refinement + any job brief, as shown to proposers


def known_keywords(manifest: str | None = None, extra_file: str | None = "data/lp/keywords.txt") -> list[str]:
    """Keywords with evidence: words named in the solved sections' notes in the manifest
    (e.g. '... (DIVINITY)'), plus any the owner verified in data/lp/keywords.txt (one per line)."""
    import json as _json
    from pathlib import Path as _P
    out: list[str] = []
    try:
        if manifest and _P(manifest).is_file():
            from lpswarm.textio import read_text
            for s in _json.loads(read_text(manifest)).get("sections", []):
                out += re.findall(r"\(([A-Z][A-Z]{3,})\)", str(s.get("source_note", "")))
        if extra_file and _P(extra_file).is_file():
            from lpswarm.textio import read_text
            out += [w.strip().upper() for w in read_text(extra_file).splitlines()
                    if w.strip() and not w.lstrip().startswith("#")]
    except Exception:  # noqa: BLE001 - best effort
        pass
    return list(dict.fromkeys(out))
MAX_SHARED_CHARS = 5000
MAX_STRATEGY_CHARS = 800


def summarise_peers(rows: Sequence[dict], limit: int = 30) -> list[str]:
    """Hypotheses other jobs tried on the same target, most-tested first. Only the
    deterministic description (the model's free-text 'why' is stripped), with who tried it."""
    c: Counter = Counter()
    who: dict = {}
    for r in rows:
        desc = str(r["description"]).split(" | why:", 1)[0][:140]
        c[desc] += int(r["attempts"])
        who.setdefault(desc, str(r.get("proposer_model") or "?"))
    return [f"{d} ({n} attempts, by {who[d]})" for d, n in c.most_common(limit)]


def build_shared_context(peer_rows: Sequence[dict], strategy: str = "") -> str:
    """Text for GenContext.shared from other lanes' work on this target and the
    supervisor's current strategy note (either may be empty)."""
    parts = []
    peers = summarise_peers(peer_rows)
    if peers:
        parts.append("Other models in this run have already tested these on this same target "
                     "(do not repeat them or trivial variations; look elsewhere):\n"
                     + "\n".join(f"  - {x}" for x in peers))
    if strategy.strip():
        parts.append("Current strategy note from the run supervisor (a suggestion for what to "
                     "favour next, based on every lane's results; your own style still applies):\n"
                     + strategy.strip()[:MAX_STRATEGY_CHARS])
    return "\n".join(parts)

SYSTEM_PROMPT = ("You are a cryptanalysis assistant proposing hypotheses for an unsolved "
                 "historical-style cipher. Be concrete and diverse; do not repeat proposals that "
                 "already failed. Reply with JSON only.")


def build_prompt(ctx: GenContext, max_symbols: int = 300) -> list[dict]:
    a = ctx.alphabet
    vals = ctx.alphabet_values
    table = ", ".join(f"{i}={t}" + (f"({vals[i]})" if vals else "") for i, t in enumerate(a.tokens))
    shown = ctx.ciphertext[:max_symbols]
    ct_tokens = " ".join(a.tokens[int(x)] for x in shown)
    ct_ints = " ".join(str(int(x)) for x in shown)
    st = ctx.stats()
    lines = [
        LANGUAGE_DOC % {"sequences": ", ".join(sorted(SEQUENCES))},
        EXAMPLES,
        f"Alphabet (N={a.size}, index=token" + ("(value)" if vals else "") + f"): {table}",
        f"Target: {ctx.label}. Length {st['length']} symbols"
        + (f" (first {len(shown)} shown)" if len(shown) < st["length"] else "") + ".",
        f"Ciphertext as tokens: {ct_tokens}",
        f"Ciphertext as integers: {ct_ints}",
        f"Statistics: {json.dumps(st)}",
    ]
    if ctx.already_ruled_out:
        lines.append("Already searched without success (do not repeat): "
                     + "; ".join(ctx.already_ruled_out[:30]))
    if ctx.history:
        lines.append("Your earlier proposals and verdicts (most recent last):")
        lines += [f"  - {f.description} -> {f.verdict}" for f in ctx.history[-40:]]
    if ctx.errors:
        lines.append("These earlier proposals were invalid and were not run:")
        lines += [f"  - {e}" for e in ctx.errors[-10:]]
    if ctx.style in STYLE_HINTS:
        lines.append(STYLE_HINTS[ctx.style])
    if ctx.known_words:
        lines.append("Keywords verified from solved pages of this puzzle: " + ", ".join(ctx.known_words)
                     + ". Try these first for word keys. Other words are welcome as guesses: say so in "
                     "'why' and where the idea came from (e.g. \"guess: a word from the puzzle text\"), "
                     "and do not call a word a known keyword unless it is in this list.")
    if ctx.shared:
        lines.append(ctx.shared[:MAX_SHARED_CHARS])
    if ctx.brief:
        lines.append("Direction from the run supervisor, who has read the results so far "
                     "(use it to choose what to try; the reply format and the rules above still "
                     "apply):\n" + ctx.brief[:MAX_BRIEF_TOTAL])
    lines.append(
        f'Round {ctx.round}. Propose {ctx.k} NEW, diverse hypotheses as JSON: '
        '{"proposals": [{"spec": {...}, "why": "one short sentence"}, ...]}')
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(lines)}]


BRIEF_SYSTEM = ("You are the lead cryptanalyst planning work on an unsolved cipher section. "
                "Another model will propose cipher programs from your brief; deterministic code "
                "tests every proposal against a null-calibrated English detector. Write a short, "
                "concrete brief in plain text (no JSON), at most 1800 characters.")


def build_brief_prompt(ctx: GenContext, results_so_far: str = "") -> list[dict]:
    """Prompt for the supervisor model to write a brief for one target (auto-brief)."""
    base = build_prompt(ctx)[1]["content"]
    # Reuse the proposer's view (language, examples, ciphertext, statistics), minus the
    # final instruction line, then ask for a plan instead of proposals.
    body = base.rsplit("\nRound ", 1)[0]
    ask = ("Word keys beyond the verified keyword list (if one is given above) are welcome as "
           "guesses, but mark each one \"(guess)\" with where the idea comes from, and do not "
           "present guesses or remembered puzzle history as established facts. "
           "Write the brief for the proposer: 4-8 numbered directions, each naming concrete "
           "program choices in the language above (stream kind and sequence, combine mode, "
           "offsets or ranges, skip rules, transpositions) and the reason (a statistic of this "
           "text, or a near miss below). Say what NOT to repeat. Prefer ideas that differ from "
           "what was already tried.")
    if results_so_far:
        body += "\n\nResults so far on this section across the run (best leads; margin < 0 means " \
                "below the pass threshold):\n" + results_so_far
    return [{"role": "system", "content": BRIEF_SYSTEM},
            {"role": "user", "content": body + "\n\n" + ask}]


REFINE_SYSTEM = ("You are a cryptanalyst tuning a plan written by the lead cryptanalyst (the "
                 "supervisor) for one unsolved cipher section. You work under the supervisor: every "
                 "direction in its brief stays in force and you may not contradict, drop or reorder "
                 "it. Deterministic code tests every proposal against a null-calibrated English "
                 "detector. Reply in plain text (no JSON), at most 1000 characters.")


def build_refine_prompt(ctx: GenContext, supervisor_brief: str, results_so_far: str = "") -> list[dict]:
    """Prompt for the proposer model that will act on the brief to tune it (refine-brief): it
    sharpens the supervisor's directions with concrete parameter choices in its own style and
    may add a few extra ideas, labelled, but cannot override the supervisor."""
    base = build_prompt(ctx)[1]["content"]
    body = base.rsplit("\nRound ", 1)[0]
    if results_so_far:
        body += "\n\nResults so far on this section across the run (best leads; margin < 0 means " \
                "below the pass threshold):\n" + results_so_far
    body += "\n\nBrief from the supervisor (it takes precedence over anything you add):\n" \
            + supervisor_brief[:MAX_BRIEF_CHARS]
    ask = ("Tune this brief for yourself as the proposer. For each numbered direction you can make "
           "sharper, give concrete program choices in the language above (exact offsets or ranges, "
           "stream kinds, combine modes, transpositions, sizes) that stay inside that direction, "
           "refer to it by its number. You may add at most 3 extra ideas, each starting with "
           "\"EXTRA:\", only where the supervisor's brief leaves a gap, and never repeating what "
           "was already tried. Do not restate the supervisor's brief and do not present guesses or "
           "remembered puzzle history as established facts.")
    return [{"role": "system", "content": REFINE_SYSTEM},
            {"role": "user", "content": body + "\n\n" + ask}]


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


MAX_REPLY_CHARS = 200_000


def _iter_json_values(text: str):
    dec = json.JSONDecoder()
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "{[":
            try:
                val, end = dec.raw_decode(text, i)
            except (json.JSONDecodeError, RecursionError, ValueError):
                i += 1
                continue
            yield val
            i = end
        else:
            i += 1


def _proposal_items(val: Any):
    if isinstance(val, dict) and isinstance(val.get("proposals"), list):
        return val["proposals"]
    if isinstance(val, dict) and ("stream" in val or isinstance(val.get("spec"), dict)):
        return [val]   # a single bare spec, or a single {"spec": ..., "why": ...}
    if isinstance(val, list) and val and all(isinstance(x, dict) and ("spec" in x or "stream" in x)
                                             for x in val):
        return val
    return None


def parse_proposals(text: str) -> tuple[list[RawProposal], list[str]]:
    """Extract proposals from a model reply. Tolerates code fences, chatter and
    stray JSON (e.g. a list of numbers in the prose): the first JSON value that
    looks like proposals wins."""
    errors: list[str] = []
    if len(text) > MAX_REPLY_CHARS:
        text = text[:MAX_REPLY_CHARS]
        errors.append("reply was truncated (too long)")
    chunks = [m.group(1) for m in _FENCE.finditer(text)] + [text]
    items = None
    for chunk in chunks:
        for val in _iter_json_values(chunk):
            items = _proposal_items(val)
            if items is not None:
                break
        if items is not None:
            break
    if items is None:
        return [], errors + ['no proposals found; reply with {"proposals": [{"spec": {...}}]}']
    out = []
    for it in items:
        if isinstance(it, dict) and "spec" in it:
            out.append(RawProposal(it["spec"], str(it.get("why", ""))[:200]))
        elif isinstance(it, dict) and "stream" in it:
            out.append(RawProposal(it, ""))
        else:
            errors.append(f"unrecognised proposal item: {str(it)[:80]}")
    return out, errors


class LLMGenerator:
    role = "proposer"

    def __init__(self, router, model: str, temperature: float = 0.8, max_tokens: int = 3000,
                 structured: bool = True, style: str | None = None):
        self.router, self.model = router, model
        self.structured = structured
        if style is None:
            try:
                style = str(router.spec(model).extra.get("style", ""))
            except Exception:  # noqa: BLE001
                style = ""
        self.style = style
        try:
            pr = router.spec(model).extra.get("per_round")
            self.per_round = int(pr) if pr else None   # per-model proposals per round
        except Exception:  # noqa: BLE001
            self.per_round = None
        self.temperature, self.max_tokens = temperature, max_tokens
        self.last_errors: list[str] = []

    def propose(self, ctx: GenContext) -> list[RawProposal]:
        if self.style and not ctx.style:
            ctx.style = self.style
        msgs = build_prompt(ctx)
        c = self.router.complete(self.model, msgs, role="proposer",
                                 schema=proposal_schema(2 * max(ctx.k, 1)) if self.structured else None,
                                 task_id=f"{ctx.task_id or ctx.label}#r{ctx.round}",
                                 temperature=self.temperature, max_tokens=self.max_tokens)
        props, errs = parse_proposals(c.text)
        self.last_errors = errs
        return props[: max(ctx.k, 1) * 2]


class ModelRanker:
    """Weighting role: a small model orders proposals by plausibility (0-10)."""

    def __init__(self, router, model: str):
        self.router, self.model = router, model

    def rank(self, ctx: GenContext, descriptions: Sequence[str]) -> list[int]:
        if len(descriptions) < 2:
            return list(range(len(descriptions)))
        st = ctx.stats()
        prompt = ("Score each cipher hypothesis 0-10 for how plausible it is for this ciphertext "
                  f"(length {st['length']}, normalised IC {st['ic_normalised']}, adjacent doubles "
                  f"{st['adjacent_doubles']} vs {st['expected_doubles_if_random']} expected if "
                  "random). Reply with JSON {\"scores\": [numbers in the same order]}.\n"
                  + "\n".join(f"{i}. {d}" for i, d in enumerate(descriptions)))
        try:
            c = self.router.complete(self.model, [{"role": "user", "content": prompt}],
                                     role="weighting",
                                     task_id=f"{ctx.task_id or ctx.label}#rank{ctx.round}",
                                     temperature=0.0, max_tokens=400)
            m = re.search(r"\{.*\}", c.text, re.S)
            scores = json.loads(m.group(0))["scores"] if m else None
            if not isinstance(scores, list) or len(scores) != len(descriptions):
                raise ValueError
            scores = [float(s) for s in scores]
        except Exception:  # noqa: BLE001 - ranking is best-effort; keep proposal order
            return list(range(len(descriptions)))
        return sorted(range(len(descriptions)), key=lambda i: -scores[i])


def summarise_tried(rows: Sequence[dict]) -> list[str]:
    """Compact 'already tried' lines for a target, from Ledger.tried rows.

    Lists every hypothesis tried on the target regardless of outcome (so the list
    reveals no verdicts), using only the deterministic description: the free-text
    `why` a model attached is stripped, so one model cannot inject text into
    another model's prompt.
    """
    c: Counter = Counter()
    for r in rows:
        desc = str(r["description"]).split(" | why:", 1)[0]
        c[(r["cipher_family"], desc)] += int(r["attempts"])
    return [f"{fam}: {desc} ({n} attempts)" for (fam, desc), n in c.most_common(30)]
