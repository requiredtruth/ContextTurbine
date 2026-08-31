from __future__ import annotations
from dataclasses import asdict, dataclass
import re
from typing import Callable

_TOKEN = re.compile(r"[a-z0-9]+")

@dataclass(frozen=True, slots=True)
class Fact:
    id: str
    text: str
    required: bool = True

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.text.strip():
            raise ValueError("fact id and text cannot be empty")

@dataclass(frozen=True, slots=True)
class FactResult:
    id: str
    required: bool
    exact: bool
    token_recall: float

@dataclass(frozen=True, slots=True)
class RoundResult:
    round: int
    characters: int
    ratio_to_source: float
    required_survival: float
    facts: tuple[FactResult, ...]

@dataclass(frozen=True, slots=True)
class TurbineReport:
    source_characters: int
    rounds: tuple[RoundResult, ...]
    first_required_loss_round: int | None
    final_text: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["rounds"] = [asdict(item) for item in self.rounds]
        return payload

def _normalized(text: str) -> str:
    return " ".join(_TOKEN.findall(text.lower()))

def _contains_token_sequence(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    """Return whether ``needle`` occurs as complete consecutive tokens."""
    width = len(needle)
    return width > 0 and any(
        haystack[index:index + width] == needle
        for index in range(len(haystack) - width + 1)
    )

def _score(text: str, fact: Fact) -> FactResult:
    haystack = tuple(_normalized(text).split())
    needle = tuple(_normalized(fact.text).split())
    tokens = set(needle)
    present = set(haystack)
    recall = len(tokens & present) / len(tokens) if tokens else 0.0
    return FactResult(fact.id, fact.required, _contains_token_sequence(haystack, needle), recall)

def run_turbine(source: str, facts: list[Fact], rounds: int, compressor: Callable[[str, tuple[Fact, ...], int], str], *, target_characters: int = 4000) -> TurbineReport:
    if not source.strip() or not facts:
        raise ValueError("source and facts cannot be empty")
    if rounds < 1 or target_characters < 1:
        raise ValueError("rounds and target_characters must be positive")
    if len({fact.id for fact in facts}) != len(facts):
        raise ValueError("fact ids must be unique")
    current = source
    results: list[RoundResult] = []
    first_loss: int | None = None
    required_count = sum(fact.required for fact in facts)
    if required_count == 0:
        raise ValueError("at least one fact must be required")
    for index in range(1, rounds + 1):
        current = compressor(current, tuple(facts), target_characters)
        if not isinstance(current, str) or not current.strip():
            raise ValueError(f"compressor returned empty output at round {index}")
        scores = tuple(_score(current, fact) for fact in facts)
        survived = sum(score.exact for score in scores if score.required)
        survival = survived / required_count
        if survival < 1.0 and first_loss is None:
            first_loss = index
        results.append(RoundResult(index, len(current), len(current) / len(source), survival, scores))
    return TurbineReport(len(source), tuple(results), first_loss, current)
