import unittest
from contextturbine.compressors import RecordedCompressor
from contextturbine.core import Fact, run_turbine
from contextturbine.gui_support import demo_arguments

class TurbineTests(unittest.TestCase):
    def test_records_first_required_fact_loss(self) -> None:
        facts = [Fact("db", "database is SQLite"), Fact("port", "server port 8209")]
        compressor = RecordedCompressor(["Database is SQLite. Server port 8209.", "Database is SQLite."])
        report = run_turbine("Database is SQLite. Server port 8209. Extra words.", facts, 2, compressor)
        self.assertEqual(report.rounds[0].required_survival, 1.0)
        self.assertEqual(report.rounds[1].required_survival, 0.5)
        self.assertEqual(report.first_required_loss_round, 2)

    def test_normalization_tolerates_case_and_punctuation(self) -> None:
        report = run_turbine("RAM cap: 3 GiB", [Fact("ram", "RAM cap 3 GiB")], 1, RecordedCompressor(["ram CAP — 3 gib!"]))
        self.assertEqual(report.first_required_loss_round, None)

    def test_exact_survival_requires_complete_token_boundaries(self) -> None:
        report = run_turbine(
            "Server port 8209.",
            [Fact("port", "port 8209")],
            1,
            RecordedCompressor(["Airport 8209 remains available."]),
        )
        self.assertFalse(report.rounds[0].facts[0].exact)
        self.assertEqual(report.first_required_loss_round, 1)

    def test_gui_blank_arguments_use_bundled_recording(self) -> None:
        self.assertEqual(
            demo_arguments(""),
            (
                "examples/spec.json",
                "--responses",
                "examples/responses.json",
                "--fail-on-loss",
            ),
        )

    def test_gui_preserves_custom_arguments(self) -> None:
        self.assertEqual(demo_arguments('"my case.json" --model local'), ("my case.json", "--model", "local"))

if __name__ == "__main__":
    unittest.main()
