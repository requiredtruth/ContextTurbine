from __future__ import annotations

import shlex


def demo_arguments(value: str) -> tuple[str, ...]:
    """Return user arguments or the deterministic bundled-demo arguments."""
    if value.strip():
        return tuple(shlex.split(value))
    return (
        "examples/spec.json",
        "--responses",
        "examples/responses.json",
        "--fail-on-loss",
    )
