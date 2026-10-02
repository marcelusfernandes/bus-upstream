import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bootstrap_labels as b  # noqa: E402


class LabelSpecs(unittest.TestCase):
    def test_includes_every_family(self):
        names = {name for name, _, _ in b.label_specs()}
        for expected in ("layer:user", "state:blocked", "type:hypothesis", "hyp:reframed",
                         "human:pending", "human:decided", "agent:decided", "mode:autonomous", "epic"):
            self.assertIn(expected, names)

    def test_names_are_unique(self):
        names = [name for name, _, _ in b.label_specs()]
        self.assertEqual(len(names), len(set(names)))

    def test_gh_command_is_idempotent_and_repo_scoped(self):
        cmd = b.gh_command("state:done", "0E8A16", "Done", repo="owner/name")
        self.assertIn("--force", cmd)
        self.assertEqual(cmd[-2:], ["--repo", "owner/name"])

    def test_dry_run_is_default(self):
        self.assertEqual(b.main([]), 0)


if __name__ == "__main__":
    unittest.main()
