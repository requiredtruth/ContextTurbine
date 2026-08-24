from __future__ import annotations
import json
from typing import Iterable
from urllib import request
from .core import Fact

class RecordedCompressor:
    def __init__(self, responses: Iterable[str]) -> None:
        self._responses = iter(responses)

    def __call__(self, text: str, facts: tuple[Fact, ...], target: int) -> str:
        try:
            return next(self._responses)
        except StopIteration as exc:
            raise ValueError("recorded responses ended before all rounds") from exc

class OpenAICompressor:
    def __init__(self, endpoint: str, model: str, timeout: float = 60.0) -> None:
        self.endpoint = endpoint.rstrip("/")
        if not self.endpoint.endswith("/chat/completions"):
            self.endpoint += "/v1/chat/completions"
        self.model = model
        self.timeout = timeout

    def __call__(self, text: str, facts: tuple[Fact, ...], target: int) -> str:
        fact_lines = "\n".join(f"- {fact.id}: {fact.text}" for fact in facts if fact.required)
        prompt = f"Compress the state below to at most {target} characters. Preserve every required fact verbatim enough to remain identifiable. Return only compressed state.\nREQUIRED FACTS:\n{fact_lines}\nSTATE:\n{text}"
        body = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0}).encode()
        req = request.Request(self.endpoint, data=body, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=self.timeout) as response:
            payload = json.load(response)
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("endpoint returned no assistant content") from exc
