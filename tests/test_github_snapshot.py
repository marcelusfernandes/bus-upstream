"""The loader transform is tested on a synthetic payload shaped like the GitHub GraphQL
response in github_snapshot.QUERY. It is not a recording of real data."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import github_snapshot as g  # noqa: E402


def payload():
    return {"data": {"repository": {"milestone": {"number": 3, "issues": {"nodes": [
        {"number": 1, "title": "B · Business problem", "body": "> **Definition:** 5 · **Grounding:** 3 · **Spread:** 0",
         "state": "OPEN", "parent": None,
         "labels": {"nodes": [{"name": "epic"}, {"name": "layer:business"}]},
         "assignees": {"nodes": []},
         "comments": {"nodes": [{"author": {"login": "agent-bot"}, "body": "## Score · B · Definition – → 5 · Grounding – → 3",
                                 "createdAt": "2026-10-02T10:00:00Z"}]},
         "timelineItems": {"nodes": [
             {"__typename": "LabeledEvent", "createdAt": "2026-10-02T10:00:01Z",
              "label": {"name": "epic"}, "actor": {"login": "agent-bot"}},
             {"__typename": "UnlabeledEvent", "createdAt": "2026-10-02T11:00:00Z",
              "label": {"name": "state:ready"}, "actor": None}]}},
        {"number": 5, "title": "H-01 · a faster flow", "body": None, "state": "CLOSED", "parent": {"number": 3},
         "labels": {"nodes": [{"name": "type:hypothesis"}]}, "assignees": {"nodes": [{"login": "junior-pm"}]},
         "comments": {"nodes": []}, "timelineItems": {"nodes": []}},
    ]}}}}}


class Transform(unittest.TestCase):
    def test_issue_shape(self):
        snap = g.transform(payload(), files={"initiatives/x/hypotheses.md": "t"})
        first = snap["issues"][0]
        self.assertEqual(first["state"], "open")
        self.assertEqual(first["labels"], ["epic", "layer:business"])
        self.assertEqual(first["comments"][0]["author"], "agent-bot")
        self.assertEqual(first["comments"][0]["created_at"], "2026-10-02T10:00:00Z")
        self.assertEqual(first["label_events"][1], {"label": "state:ready", "action": "removed",
                                                    "created_at": "2026-10-02T11:00:00Z", "actor": None})
        self.assertEqual(snap["files"], {"initiatives/x/hypotheses.md": "t"})

    def test_parent_assignees_and_null_body(self):
        h = g.transform(payload(), files={})["issues"][1]
        self.assertEqual(h["parent"], 3)
        self.assertEqual(h["assignees"], ["junior-pm"])
        self.assertEqual(h["body"], "")
        self.assertEqual(h["state"], "closed")

    def test_truncated_pages_raise_instead_of_partial_snapshot(self):
        data = payload()
        data["data"]["repository"]["milestone"]["issues"]["pageInfo"] = {"hasNextPage": True}
        with self.assertRaises(ValueError):
            g.transform(data, files={})
        data = payload()
        data["data"]["repository"]["milestone"]["issues"]["nodes"][0]["comments"]["pageInfo"] = {"hasNextPage": True}
        with self.assertRaises(ValueError):
            g.transform(data, files={})

    def test_missing_milestone_raises(self):
        with self.assertRaises(ValueError):
            g.transform({"data": {"repository": {"milestone": None}}}, files={})

    def test_milestone_number_from_readme(self):
        self.assertEqual(g.milestone_from_readme("# X\n\nMilestone: #12\n"), 12)
        self.assertIsNone(g.milestone_from_readme("# X\n"))


if __name__ == "__main__":
    unittest.main()
