"""Subscription CLIs as models: Claude Code (`claude -p`) and Codex (`codex exec`).

Design rules, so plan usage stays within what the providers document:
  - Only the official, unmodified CLI is run, signed in with *your* account. The
    harness never reads, copies or stores the CLI's login or tokens.
  - Each call runs in a fresh empty temporary folder with tools off (Claude Code)
    or a read-only sandbox (Codex), so the CLI answers as a chat model and cannot
    touch the repo, the ledger or the oracle.
  - API-key and backend variables (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL,
    CLAUDE_CODE_USE_BEDROCK/VERTEX, OPENAI_API_KEY, ...) are removed from the CLI's
    environment. This covers the common ways a call gets billed to an API instead of
    the plan, but not settings inside the CLIs' own config files (for example an
    apiKeyHelper or env block in ~/.claude/settings.json): keep those plan-based.
  - Codex's read-only sandbox stops writes, not reads; on Windows its sandbox is
    weaker than on macOS/Linux. Treat it as a chat model you trust not to go looking.
  - Prompts go over stdin; the system prompt goes in a file (no command-line
    quoting problems with Windows .cmd launchers).
Usage limits are detected from the CLI's reply and raised as AdapterError with
`rate_limited=True`; the router turns that into a recorded pause.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Sequence

from lpswarm.router.adapters import AdapterError, Completion
from lpswarm.router.limits import looks_like_limit, parse_resume_at


class CLILimitError(AdapterError):
    def __init__(self, msg: str, resume_at: float, parsed: bool):
        super().__init__(msg, transient=False)
        self.rate_limited = True
        self.resume_at = resume_at
        self.parsed = parsed


def _split(messages: Sequence[dict]) -> tuple[str, str]:
    system = "\n\n".join(m["content"] for m in messages if m.get("role") == "system")
    rest = "\n\n".join(m["content"] for m in messages if m.get("role") != "system")
    return system, rest


def _clean_env(drop: Sequence[str]) -> dict:
    env = dict(os.environ)
    for k in drop:
        env.pop(k, None)
    return env


def _resolve(exe: str) -> str:
    found = shutil.which(exe)
    if not found:
        raise AdapterError(f"'{exe}' not found on PATH; install it and sign in first")
    return found


def _kill_tree(proc: subprocess.Popen) -> None:
    """Kill the CLI and everything it started. npm launchers (.cmd -> node -> CLI) would
    otherwise leave the real CLI running and holding our pipes after a timeout."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True, timeout=30)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc.kill()
    except OSError:
        pass


def _run(cmd: list[str], stdin: str, cwd: str, env: dict, timeout: float) -> subprocess.CompletedProcess:
    kw: dict = {}
    if os.name == "nt":
        kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd, env=env, **kw)
    except FileNotFoundError:
        raise AdapterError(f"command not found: {cmd[0]}") from None
    try:
        out, err = proc.communicate(stdin.encode("utf-8"), timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        try:
            proc.communicate(timeout=10)
        except (subprocess.TimeoutExpired, OSError, ValueError):
            pass
        raise AdapterError(f"{Path(cmd[0]).name} timed out after {timeout:.0f}s", transient=True) from None
    return subprocess.CompletedProcess(cmd, proc.returncode, out.decode("utf-8", "replace"),
                                       err.decode("utf-8", "replace"))


# Short, anchored forms of the CLIs' usage-limit replies; used to catch a limit message
# returned as a normal (non-error) result. Long replies are never treated as limits.
_LIMIT_REPLY = re.compile(r"^\s*(claude ai usage limit reached|you'?ve (hit|reached) your "
                          r"(usage )?limit|usage limit reached|.{0,40}limit reached\b)", re.I)


def _is_limit_reply(text: str) -> bool:
    return bool(text) and len(text) < 300 and bool(_LIMIT_REPLY.search(text))


def _last_result_json(out: str):
    """The CLI's final result object. Scans from the end, so update notices or other
    lines printed around the JSON don't break parsing; accepts the --verbose array form."""
    for line in reversed([x for x in out.splitlines() if x.strip()]):
        try:
            val = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(val, list):
            for item in reversed(val):
                if isinstance(item, dict) and item.get("type") == "result":
                    return item
            continue
        if isinstance(val, dict) and ("result" in val or val.get("type") == "result"):
            return val
    try:
        val = json.loads(out)
        if isinstance(val, list):
            val = next((i for i in reversed(val) if isinstance(i, dict) and i.get("type") == "result"), None)
        return val if isinstance(val, dict) else None
    except json.JSONDecodeError:
        return None


class ClaudeCodeAdapter:
    """`claude -p` with tools off, JSON output, no session saved."""

    # Variables that would send calls to API billing or another backend instead of the plan.
    DROP_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY")

    def __init__(self, model: str = "", exe: str = "claude", timeout: float = 600,
                 extra_args: Sequence[str] = ()):
        self.model, self.exe, self.timeout = model, exe, timeout
        self.extra_args = list(extra_args)

    def command(self, system_file: str | None) -> list[str]:
        cmd = [_resolve(self.exe), "-p", "--output-format", "json", "--tools", "",
               "--max-turns", "1", "--no-session-persistence", "--strict-mcp-config",
               "--disable-slash-commands", "--permission-mode", "dontAsk"]
        if system_file:
            cmd += ["--system-prompt-file", system_file]
        if self.model and self.model not in ("default", "claude"):
            cmd += ["--model", self.model]
        return cmd + self.extra_args

    def complete(self, messages: Sequence[dict], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        system, user = _split(messages)
        t0 = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="lpswarm-claude-", ignore_cleanup_errors=True) as tmp:
            sys_file = None
            if system:
                sys_file = str(Path(tmp) / "system.txt")
                Path(sys_file).write_text(system, encoding="utf-8")
            r = _run(self.command(sys_file), user, tmp, _clean_env(self.DROP_ENV), self.timeout)
        out = (r.stdout or "").strip()
        data = _last_result_json(out) if out else None
        text = data.get("result") if data else None
        is_error = bool(data.get("is_error")) if data else r.returncode != 0
        # With a parsed result, judge limits on its text only (a stderr warning that
        # mentions 429 must not pause the model); without one, use whatever was printed.
        blob = (text or "") if data else " ".join(filter(None, [out, r.stderr]))
        if ((is_error or r.returncode != 0) and looks_like_limit(blob)) or \
                (isinstance(text, str) and _is_limit_reply(text)):
            at, parsed = parse_resume_at(blob)
            raise CLILimitError(f"Claude Code usage limit: {blob[:200]}", at, parsed)
        if r.returncode != 0 or is_error or not isinstance(text, str):
            detail = blob or (r.stderr or "")
            raise AdapterError(f"claude exited {r.returncode}: {detail[:300]}")
        u = (data or {}).get("usage") or {}
        tin = int(u.get("input_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0) \
            + int(u.get("cache_creation_input_tokens") or 0)
        tout = int(u.get("output_tokens") or 0)
        # Plan usage costs nothing per call; the CLI's API-equivalent estimate is kept in raw.
        return Completion(text, self.model or "claude", tin, tout, 0.0, time.monotonic() - t0,
                          {"api_equivalent_usd": data.get("total_cost_usd")})


class CodexAdapter:
    """`codex exec -` in a read-only sandbox, ephemeral, last message written to a file."""

    DROP_ENV = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")

    def __init__(self, model: str = "", exe: str = "codex", timeout: float = 600,
                 extra_args: Sequence[str] = ()):
        self.model, self.exe, self.timeout = model, exe, timeout
        self.extra_args = list(extra_args)

    def command(self, out_file: str) -> list[str]:
        cmd = [_resolve(self.exe), "exec", "--sandbox", "read-only", "--ephemeral",
               "--skip-git-repo-check", "--color", "never", "--json", "-o", out_file]
        if self.model and self.model not in ("default", "codex"):
            cmd += ["-m", self.model]
        return cmd + self.extra_args + ["-"]

    def complete(self, messages: Sequence[dict], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        system, user = _split(messages)
        prompt = (system + "\n\n" + user) if system else user
        t0 = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="lpswarm-codex-", ignore_cleanup_errors=True) as tmp:
            out_file = str(Path(tmp) / "last_message.txt")
            r = _run(self.command(out_file), prompt, tmp, _clean_env(self.DROP_ENV), self.timeout)
            text = Path(out_file).read_text(encoding="utf-8", errors="replace") \
                if Path(out_file).is_file() else ""
        tin = tout = 0
        errors = []
        for line in (r.stdout or "").splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(ev, dict):
                continue
            u = ev.get("usage") if isinstance(ev.get("usage"), dict) else None
            if u:
                tin += int(u.get("input_tokens") or 0)
                tout += int(u.get("output_tokens") or 0)
            if "error" in str(ev.get("type", "")) or "failed" in str(ev.get("type", "")):
                errors.append(json.dumps(ev)[:300])
        blob = " ".join(errors + [r.stderr or ""])
        if ((r.returncode != 0 or not text.strip()) and looks_like_limit(blob)) or \
                _is_limit_reply(text.strip()):
            blob = blob if blob.strip() else text
            at, parsed = parse_resume_at(blob)
            raise CLILimitError(f"Codex usage limit: {blob[:200]}", at, parsed)
        if r.returncode != 0 or not text.strip():
            raise AdapterError(f"codex exited {r.returncode}: {blob[:300]}")
        return Completion(text, self.model or "codex", tin, tout, 0.0, time.monotonic() - t0)


def cli_version(exe: str, timeout: float = 30) -> str | None:
    """`<exe> --version` (no model call, no usage). None if not installed."""
    path = shutil.which(exe)
    if not path:
        return None
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr).strip() else "?"
