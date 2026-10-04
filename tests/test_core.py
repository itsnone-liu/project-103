import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from p103.core import create_run, load_run, record_repair, validate_project


class CoreRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.source = self.root / "lesson source.md"
        self.source.write_text("Two-source interference", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_copies_source_and_scaffolds_run(self):
        run = create_run(self.workspace, "video", self.source, run_id="wave-test")
        self.assertEqual(run.state()["state"], "CREATED")
        self.assertEqual(run.project()["source"], "input/lesson source.md")
        self.assertEqual((run.root / "input" / "lesson source.md").read_text(encoding="utf-8"), "Two-source interference")
        for folder in ("plan", "audio", "scenes", "attempt-1", "verification", "final"):
            self.assertTrue((run.root / folder).is_dir())
        self.assertTrue((run.root / "run.log").is_file())

    def test_state_machine_rejects_skips(self):
        run = create_run(self.workspace, "interactive", self.source, run_id="state-test")
        with self.assertRaisesRegex(ValueError, "Illegal state transition"):
            run.transition("FINAL")
        run.transition("PLANNING")
        run.transition("BUILDING")
        self.assertEqual(load_run(self.workspace, "state-test").state()["state"], "BUILDING")

    def test_repair_limit_is_one(self):
        run = create_run(self.workspace, "video", self.source, run_id="repair-test")
        for state in ("PLANNING", "BUILDING", "RENDERING", "VERIFYING"):
            run.transition(state)
        record_repair(run, "first repair")
        self.assertEqual(run.state()["repair_count"], 1)
        run.transition("RENDERING")
        run.transition("VERIFYING")
        with self.assertRaisesRegex(ValueError, "Repair limit reached"):
            record_repair(run, "must fail")

    def test_artifact_path_blocks_traversal(self):
        run = create_run(self.workspace, "video", self.source, run_id="path-test")
        out = run.artifact("scenes/scene-01/main.tsx")
        self.assertTrue(str(out).endswith("scenes\\scene-01\\main.tsx"))
        with self.assertRaises(ValueError):
            run.artifact("../../escape.txt")

    def test_project_contract_caps_repairs_and_checks_duration(self):
        self.assertEqual(validate_project({"mode": "video", "max_repairs": 1, "target_duration": [45, 60]})["mode"], "video")
        with self.assertRaises(ValueError):
            validate_project({"mode": "video", "max_repairs": 2})
        with self.assertRaises(ValueError):
            validate_project({"mode": "video", "target_duration": [60, 45]})

    def test_duplicate_run_id_is_rejected(self):
        create_run(self.workspace, "video", self.source, run_id="duplicate")
        with self.assertRaises(FileExistsError):
            create_run(self.workspace, "video", self.source, run_id="duplicate")


if __name__ == "__main__":
    unittest.main()
