from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
from .compressors import OpenAICompressor, RecordedCompressor
from .core import Fact, run_turbine

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure required-fact survival across repeated context compression.")
    parser.add_argument("spec")
    parser.add_argument("--responses", help="JSON array of recorded compression responses")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080")
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--fail-on-loss", action="store_true")
    args = parser.parse_args(argv)
    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        facts = [Fact(**item) for item in spec["facts"]]
        if args.responses:
            responses = json.loads(Path(args.responses).read_text(encoding="utf-8"))
            compressor = RecordedCompressor(responses)
        else:
            compressor = OpenAICompressor(args.endpoint, args.model)
        report = run_turbine(spec["source"], facts, spec.get("rounds", 3), compressor, target_characters=spec.get("target_characters", 4000))
    except Exception as exc:
        print(f"contextturbine: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 1 if args.fail_on_loss and report.first_required_loss_round is not None else 0
