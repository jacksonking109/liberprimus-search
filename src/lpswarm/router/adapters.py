"""Model adapters. The ONLY module in lpswarm that opens network connections.

- OllamaAdapter:            local models (Qwen, Gemma, Granite) via Ollama's /api/chat.
- OpenAICompatibleAdapter:  hosted chat-completions APIs (DeepSeek). The API key is
                            read from the environment variable named in the config,
                            at call time, and is never stored, logged or echoed.
- CommandAdapter:           any CLI that reads a prompt on stdin and prints a reply.
- ScriptedAdapter:          canned replies, for tests and dry runs.

Errors never include request headers.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Sequence

Message = dict  # {"role": "system"|"user"|"assistant", "content": str}


class AdapterError(RuntimeError):
    pass


@dataclass
class Completion:
    text: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    usd: float = 0.0
    latency_s: float = 0.0
    raw: dict = field(default_factory=dict, repr=False)


def _post_json(url: str, body: dict, headers: dict[str, str], timeout: float) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    # Never send local model traffic (Ollama) through a system HTTP proxy.
    opener = (urllib.request.build_opener(urllib.request.ProxyHandler({}))
              if host in ("localhost", "127.0.0.1", "::1") else urllib.request.build_opener())
    try:
        with opener.open(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:  # noqa: BLE001
            pass
        raise AdapterError(f"HTTP {exc.code} from {url}: {detail}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AdapterError(f"cannot reach {url}: {getattr(exc, 'reason', exc)}") from None
    except json.JSONDecodeError:
        raise AdapterError(f"non-JSON reply from {url}") from None


class OllamaAdapter:
    def __init__(self, model: str, endpoint: str = "http://localhost:11434", timeout: float = 300,
                 json_mode: bool = False, options: dict | None = None):
        self.model, self.endpoint, self.timeout = model, endpoint.rstrip("/"), timeout
        self.json_mode, self.options = json_mode, options or {}

    def complete(self, messages: Sequence[Message], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        body = {"model": self.model, "messages": list(messages), "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens, **self.options}}
        if self.json_mode:
            body["format"] = "json"
        t0 = time.monotonic()
        r = _post_json(f"{self.endpoint}/api/chat", body, {}, self.timeout)
        text = (r.get("message") or {}).get("content", "")
        return Completion(text, self.model, int(r.get("prompt_eval_count") or 0),
                          int(r.get("eval_count") or 0), 0.0, time.monotonic() - t0, r)


class OpenAICompatibleAdapter:
    def __init__(self, model: str, endpoint: str, api_key_env: str | None, timeout: float = 120,
                 price_in_per_mtok: float = 0.0, price_out_per_mtok: float = 0.0,
                 json_mode: bool = False):
        self.model, self.endpoint, self.timeout = model, endpoint.rstrip("/"), timeout
        self.api_key_env = api_key_env
        self.price_in, self.price_out = price_in_per_mtok, price_out_per_mtok
        self.json_mode = json_mode

    def _key(self) -> str:
        if not self.api_key_env:
            raise AdapterError("no api_key_env configured for this model")
        key = os.environ.get(self.api_key_env)
        if not key:
            raise AdapterError(f"environment variable {self.api_key_env} is not set")
        return key

    def complete(self, messages: Sequence[Message], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        body = {"model": self.model, "messages": list(messages), "temperature": temperature,
                "max_tokens": max_tokens, "stream": False}
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}
        url = self.endpoint + ("/chat/completions" if not self.endpoint.endswith("/chat/completions")
                               else "")
        t0 = time.monotonic()
        r = _post_json(url, body, {"Authorization": f"Bearer {self._key()}"}, self.timeout)
        try:
            text = r["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            raise AdapterError("unexpected reply shape (no choices[0].message.content)") from None
        u = r.get("usage") or {}
        tin, tout = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
        usd = tin / 1e6 * self.price_in + tout / 1e6 * self.price_out
        return Completion(text, self.model, tin, tout, usd, time.monotonic() - t0, r)


class CommandAdapter:
    """Runs `command` (a list, no shell), writes the prompt to stdin, reads stdout."""

    def __init__(self, model: str, command: Sequence[str], timeout: float = 600):
        if not command:
            raise AdapterError("command adapter needs a non-empty command list")
        exe = shutil.which(command[0]) or command[0]  # resolves .cmd/.exe on Windows
        self.command = [exe, *command[1:]]
        self.model, self.timeout = model, timeout

    def complete(self, messages: Sequence[Message], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        prompt = "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)
        t0 = time.monotonic()
        try:
            r = subprocess.run(self.command, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=self.timeout)
        except FileNotFoundError:
            raise AdapterError(f"command not found: {self.command[0]}") from None
        except subprocess.TimeoutExpired:
            raise AdapterError(f"command timed out after {self.timeout}s") from None
        if r.returncode != 0:
            raise AdapterError(f"command exited {r.returncode}: {r.stderr[:300]}")
        return Completion(r.stdout, self.model, 0, 0, 0.0, time.monotonic() - t0)


class ScriptedAdapter:
    """Replies from a list (cycled) or a callable(messages) -> str. Optional fake usage."""

    def __init__(self, model: str, replies: Sequence[str] | Callable[[Sequence[Message]], str],
                 usd_per_call: float = 0.0, tokens: tuple[int, int] = (0, 0)):
        self.model, self.replies = model, replies
        self.usd_per_call, self.tokens = usd_per_call, tokens
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        self.calls.append(list(messages))
        if callable(self.replies):
            text = self.replies(messages)
        else:
            text = self.replies[(len(self.calls) - 1) % len(self.replies)]
        return Completion(text, self.model, self.tokens[0], self.tokens[1], self.usd_per_call)
