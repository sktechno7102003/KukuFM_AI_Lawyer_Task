"""Model-agnostic LLM wrapper.

Every supported provider exposes an OpenAI-compatible endpoint, so swapping the model
is a config change (config.yaml or env vars), never a code change.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import BadRequestError, OpenAI, RateLimitError

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _expand(v: str | None) -> str | None:
    if not isinstance(v, str):
        return v
    return re.sub(r"\$\{(\w+)\}", lambda m: os.getenv(m.group(1), ""), v)


@dataclass
class CallLog:
    name: str
    model: str
    seconds: float
    prompt_tokens: int
    completion_tokens: int


@dataclass
class LLM:
    provider: str
    model: str
    base_url: str
    api_key: str
    json_mode: bool = True
    temperature: float = 0.2
    log: list[CallLog] = field(default_factory=list)

    @classmethod
    def from_config(cls, provider: str | None = None, model: str | None = None) -> "LLM":
        cfg = load_config()
        provider = provider or os.getenv("LLM_PROVIDER") or cfg["provider"]
        p = cfg["providers"][provider]
        key_env = p.get("api_key_env") or ""
        api_key = os.getenv("LLM_API_KEY") if provider == "custom" else (os.getenv(key_env) if key_env else "")
        return cls(
            provider=provider,
            model=model or os.getenv("LLM_MODEL") or _expand(p["model"]),
            base_url=os.getenv("LLM_BASE_URL") or _expand(p["base_url"]),
            api_key=api_key or "not-needed",
            json_mode=p.get("json_mode", False),
            temperature=cfg.get("temperature", 0.2),
        )

    @property
    def client(self) -> OpenAI:
        return OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=90, max_retries=2)

    # ------------------------------------------------------------------ chat
    def chat(self, system: str, messages: list[dict] | str, name: str = "chat",
             json_out: bool = False, temperature: float | None = None) -> str:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        kwargs = dict(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=self.temperature if temperature is None else temperature,
        )
        if json_out and self.json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        t0 = time.time()
        for attempt in range(6):  # free tiers have tight per-minute token limits: back off and retry
            try:
                resp = self.client.chat.completions.create(**kwargs)
                break
            except RateLimitError as e:
                if attempt == 5:
                    raise
                m = re.search(r"try again in ([\d.]+)(ms|s)", str(e))
                wait = (float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)) if m else 0
                time.sleep(max(wait, 2 ** attempt) + 1)
        u = getattr(resp, "usage", None)
        self.log.append(CallLog(name, self.model, round(time.time() - t0, 2),
                                getattr(u, "prompt_tokens", 0) or 0,
                                getattr(u, "completion_tokens", 0) or 0))
        return resp.choices[0].message.content or ""

    def chat_json(self, system: str, messages: list[dict] | str, name: str = "json") -> dict:
        """Chat and parse a JSON object; one repair retry if the model returns bad JSON."""
        try:
            raw = self.chat(system, messages, name=name, json_out=True)
        except BadRequestError as e:
            # Some providers (Groq + smaller models) reject output that fails their JSON check: retry in plain mode.
            if "json" not in str(e).lower():
                raise
            raw = self.chat(system, messages, name=name + "_nojsonmode", json_out=False)
        try:
            return parse_json(raw)
        except ValueError:
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            fix = [*messages, {"role": "assistant", "content": raw},
                   {"role": "user", "content": "That was not valid JSON. Reply with ONLY the JSON object."}]
            return parse_json(self.chat(system, fix, name=name + "_retry", json_out=True))

    # ------------------------------------------------------------------ voice
    def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        cfg = load_config()
        stt = cfg["providers"][cfg.get("stt_provider", "groq")]
        key = os.getenv(stt["api_key_env"]) if stt.get("api_key_env") else "not-needed"
        client = OpenAI(base_url=_expand(stt["base_url"]), api_key=key or "not-needed")
        r = client.audio.transcriptions.create(model=stt["stt_model"], file=(filename, audio_bytes))
        return r.text


def parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    raise ValueError(f"Model did not return JSON: {raw[:200]}")
