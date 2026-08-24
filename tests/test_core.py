import unittest
from contextturbine.compressors import RecordedCompressor
from contextturbine.core import Fact, run_turbine

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

if __name__ == "__main__":
    unittest.main()
