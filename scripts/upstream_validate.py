#!/usr/bin/env python3
"""BUS upstream validator (spec/v1/08-validator-and-hooks.md).

Pure checks over a snapshot: {"issues": [...], "files": {path: text}}. The only I/O
is the CLI at the bottom (commit-msg mode, or a snapshot JSON file). Check numbers
follow the spec.

Snapshot loaders must emit every `created_at` as ISO-8601 UTC with a `Z` suffix:
checks 5, 6 and 9 compare timestamps as strings. Text may use CRLF line endings
(GitHub web edits); it is normalized before matching.
"""
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import upstream_contract as c

ADVANCED_STATES = ("state:in-review", "state:done")


@dataclass(frozen=True)
class Error:
    check: int
    where: str
    message: str

    def __str__(self):
        return f"[check {self.check}] {self.where}: {self.message}"


# ---------- helpers ----------

def _issues(snap):
    return snap.get("issues", [])


def _where(issue):
    return f"#{issue['number']} {issue['title']}"


def _children(snap, number):
    return [i for i in _issues(snap) if i.get("parent") == number]


def _has(issue, label):
    return label in issue.get("labels", [])


def _layer_epics(snap):
    return [i for i in _issues(snap)
            if _has(i, "epic") and any(_has(i, l) for l in c.LAYER_CODE)]


def _titles(text, pattern):
    normalized = (text or "").replace("\r\n", "\n")
    return [m for m in re.finditer(pattern, normalized, re.MULTILINE)]


def _all_comments(snap):
    return [(i, cm) for i in _issues(snap) for cm in i.get("comments", [])]


def _label_added_at(issue, label):
    times = [e["created_at"] for e in issue.get("label_events", [])
             if e["label"] == label and e["action"] == "added"]
    return max(times) if times else None


# ---------- check 3: exclusive label families ----------

def check_exclusive_families(snap):
    errors = []
    for issue in _issues(snap):
        for prefix in c.EXCLUSIVE_PREFIXES:
            found = [l for l in issue.get("labels", []) if l.startswith(prefix)]
            if len(found) > 1:
                errors.append(Error(3, _where(issue), f"more than one {prefix} label: {found}"))
    return errors


# ---------- check 4: blocked implies human:pending ----------

def check_blocked_needs_human(snap):
    return [Error(4, _where(i), "state:blocked without human:pending")
            for i in _issues(snap)
            if _has(i, "state:blocked") and not _has(i, "human:pending")]


# ---------- check 5: no state advance while human:pending ----------

def _pending_since(snap, issue):
    candidates = [issue] + [ch for ch in _children(snap, issue["number"]) if ch.get("state") == "open"]
    times = [_label_added_at(i, "human:pending") for i in candidates if _has(i, "human:pending")]
    times = [t for t in times if t]
    return min(times) if times else None


def check_no_advance_while_pending(snap):
    errors = []
    for issue in _issues(snap):
        since = _pending_since(snap, issue)
        if not since:
            continue
        for state in ADVANCED_STATES:
            added = _label_added_at(issue, state)
            if added and added > since:
                errors.append(Error(5, _where(issue), f"{state} added while a human:pending decision is open"))
    return errors


# ---------- check 7: score header ----------

def _in_range(*values):
    return all(c.SCORE_MIN <= int(v) <= c.SCORE_MAX for v in values)


def check_score_header(snap):
    errors = []
    for epic in _layer_epics(snap):
        headers = _titles(epic.get("body"), c.SCORE_HEADER)
        if len(headers) != 1:
            errors.append(Error(7, _where(epic), "layer epic needs exactly one score header"))
            continue
        h = headers[0]
        if not _in_range(h["d"], h["g"]):
            errors.append(Error(7, _where(epic), "score outside 0-10"))
            continue
        comments = sorted(epic.get("comments", []), key=lambda x: x["created_at"])
        scores = [m for cm in comments for m in _titles(cm["body"], c.SCORE_TITLE)]
        if not scores:
            errors.append(Error(7, _where(epic), "no score comment; intake posts the first one"))
        elif (scores[-1]["d1"], scores[-1]["g1"]) != (h["d"], h["g"]):
            errors.append(Error(7, _where(epic), "header does not match the latest score comment"))
    return errors


# ---------- check 9: decision authorship ----------

def _decision_id(issue):
    m = re.search(c.DECISION_ID, issue.get("title", ""))
    return m.group(0) if m else None


def _counts_as_decide(cm, decision, here):
    """A /decide counts on the decision issue itself, or anywhere when it names the D-id."""
    for m in _titles(cm["body"], c.DECIDE_COMMAND):
        if m["target"] is None and here:
            return True
        if m["target"] and m["target"] == _decision_id(decision):
            return True
    return False


def _has_pm_decide(snap, decision, before):
    assignees = set(decision.get("assignees", []))
    for issue in _issues(snap):
        here = issue is decision
        for cm in issue.get("comments", []):
            in_time = before is None or cm["created_at"] <= before
            if cm["author"] in assignees and in_time and _counts_as_decide(cm, decision, here):
                return True
    return False


def check_decision_authorship(snap):
    return [Error(9, _where(i), "human:decided without a /decide comment from the assigned PM")
            for i in _issues(snap)
            if _has(i, "human:decided") and not _has_pm_decide(snap, i, _label_added_at(i, "human:decided"))]


# ---------- check 10: no silent hypotheses ----------

def _hypotheses(snap):
    return [i for i in _issues(snap) if _has(i, "type:hypothesis")]


def _closing_status(issue):
    found = [m for cm in issue.get("comments", []) for m in _titles(cm["body"], c.HYPOTHESIS_TITLE)]
    return found[-1]["status"].split(" ")[0] if found else None


def check_no_silent_hypotheses(snap):
    errors = []
    for epic in _layer_epics(snap):
        if _has(epic, "state:done"):
            open_h = [h for h in _children(snap, epic["number"]) if _has(h, "type:hypothesis") and _has(h, "hyp:open")]
            for h in open_h:
                errors.append(Error(10, _where(epic), f"done with open hypothesis {_where(h)}"))
    for h in _hypotheses(snap):
        if h.get("state") != "closed":
            continue
        status = _closing_status(h)
        label = next((l.split(":", 1)[1] for l in h.get("labels", []) if l.startswith("hyp:")), None)
        if status is None:
            errors.append(Error(10, _where(h), "closed without a '## Hypothesis' status comment"))
        elif status != label:
            errors.append(Error(10, _where(h), f"comment says {status}, label says hyp:{label}"))
    return errors


# ---------- check 1: IDs resolve both ways ----------

_FILE_ID = re.compile(rf"/(?:answers|evidence|decisions)/(?P<id>{c.ANSWER_ID}|{c.EVIDENCE_ID}|{c.DECISION_ID})\.md$")
_REGISTER_ROW = re.compile(rf"^\| (?P<id>{c.HYPOTHESIS_ID}) \|", re.MULTILINE)


def _ids_in_files(snap):
    ids = set()
    for path, text in snap.get("files", {}).items():
        m = _FILE_ID.search(path)
        if m:
            ids.add(m["id"])
        if path.endswith("hypotheses.md"):
            ids.update(r["id"] for r in _REGISTER_ROW.finditer(text))
    return ids


def _ids_on_github(snap):
    ids = set()
    for issue in _issues(snap):
        texts = [issue.get("title", ""), issue.get("body") or ""] + [cm["body"] for cm in issue.get("comments", [])]
        for text in texts:
            ids.update(re.findall(c.CITABLE_ID, text))
    return ids


def check_ids_resolve(snap):
    on_github, in_files = _ids_on_github(snap), _ids_in_files(snap)
    errors = [Error(1, "github", f"{i} cited on GitHub but has no file") for i in sorted(on_github - in_files)]
    errors += [Error(1, "files", f"{i} defined in files but never cited on GitHub") for i in sorted(in_files - on_github)]
    return errors


# ---------- check 2: verdicts match ----------

def _cells(line):
    return [x.strip() for x in line.strip().strip("|").split("|")]


def _register_status(snap):
    """H-id -> status, located by the 'Status' column of templates/hypotheses-register.md."""
    status = {}
    for path, text in snap.get("files", {}).items():
        if not path.endswith("hypotheses.md"):
            continue
        column = None
        for line in text.replace("\r\n", "\n").splitlines():
            cells = _cells(line)
            if "Status" in cells:
                column = cells.index("Status")
            elif column is not None and cells and re.fullmatch(c.HYPOTHESIS_ID, cells[0]):
                status[cells[0]] = cells[column].split(" ")[0]
    return status


def _review_verdicts_in_files(snap):
    verdicts = {}
    for path, text in snap.get("files", {}).items():
        if path.endswith("review.md"):
            for m in _titles(text, c.REVIEW_TITLE):
                verdicts.setdefault(m["id"], m["verdict"])  # newest first
    return verdicts


def _latest_on_github(snap, pattern, key, value):
    """ID -> (issue, value) of the newest matching comment title."""
    latest = {}
    ordered = sorted(_all_comments(snap), key=lambda pair: pair[1]["created_at"])
    for issue, cm in ordered:
        for m in _titles(cm["body"], pattern):
            latest[m[key]] = (issue, value(m))
    return latest


def check_verdicts_match(snap):
    errors = []
    file_reviews, register = _review_verdicts_in_files(snap), _register_status(snap)
    reviews = _latest_on_github(snap, c.REVIEW_TITLE, "id", lambda m: m["verdict"])
    for rid, (issue, verdict) in sorted(reviews.items()):
        if file_reviews.get(rid) != verdict:
            errors.append(Error(2, _where(issue), f"review {rid} is {verdict} on GitHub, "
                                                  f"{file_reviews.get(rid)} in review.md"))
    hyps = _latest_on_github(snap, c.HYPOTHESIS_TITLE, "id", lambda m: m["status"].split(" ")[0])
    for hid, (issue, status) in sorted(hyps.items()):
        if register.get(hid) != status:
            errors.append(Error(2, _where(issue), f"{hid} is {status} on GitHub, "
                                                  f"{register.get(hid)} in hypotheses.md"))
    return errors


# ---------- check 6: anti-loop ----------

def _failed_without_new_evidence(comments, answer_id):
    seen, rejections = set(), 0
    for cm in sorted(comments, key=lambda x: x["created_at"]):
        body = cm["body"]
        is_review = bool(_titles(body, c.REVIEW_TITLE))
        new = set() if is_review else set(re.findall(c.EVIDENCE_ID, body)) - seen
        if new:  # new evidence starts a fresh attempt
            seen |= new
            rejections = 0
        for m in _titles(body, c.REVIEW_TITLE):
            if m["id"] == answer_id and m["verdict"] == "rejected":
                rejections += 1
                if rejections >= 2:
                    return True
            elif m["id"] == answer_id:
                rejections = 0
    return False


def check_anti_loop(snap):
    errors = []
    for issue in _issues(snap):
        comments = issue.get("comments", [])
        ids = {m["id"] for cm in comments for m in _titles(cm["body"], c.REVIEW_TITLE)}
        for answer_id in sorted(ids):
            if _failed_without_new_evidence(comments, answer_id) and not (
                    _has(issue, "state:blocked") and _has(issue, "human:pending")):
                errors.append(Error(6, _where(issue), f"{answer_id} failed twice without new evidence; "
                                                      "needs state:blocked + human:pending"))
    return errors


# ---------- check 8: commit message ----------

def _trailers(message):
    paragraphs = [p for p in message.strip().split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        return {}
    trailers = {}
    for line in paragraphs[-1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            trailers[key.strip()] = value.strip()
    return trailers


def check_commit_message(message):
    title = message.strip().splitlines()[0] if message.strip() else ""
    if re.match(c.PASSTHROUGH_TITLE, title) or re.match(c.CONVENTIONAL_TITLE, title):
        return []
    if not re.match(c.ANSWER_COMMIT_TITLE, title):
        return [Error(8, "commit", "title must be '<B|U|S>-nn: <answer>' or a conventional commit")]
    trailers, errors = _trailers(message), []
    for key in c.REQUIRED_TRAILERS:
        if key not in trailers:
            errors.append(Error(8, "commit", f"missing trailer {key}"))
    for key, value in trailers.items():
        pattern = c.TRAILER_FORMATS.get(key)
        if pattern and not re.match(pattern, value):
            errors.append(Error(8, "commit", f"trailer {key} has invalid value '{value}'"))
    return errors


# ---------- entry points ----------

SNAPSHOT_CHECKS = (check_exclusive_families, check_blocked_needs_human, check_no_advance_while_pending,
                   check_anti_loop, check_score_header, check_decision_authorship, check_no_silent_hypotheses)
FILE_CHECKS = (check_ids_resolve, check_verdicts_match)


def validate_snapshot(snap):
    """GitHub-only checks (3, 4, 5, 6, 7, 9, 10). Safe to run from a GitHub Action."""
    return [e for check in SNAPSHOT_CHECKS for e in check(snap)]


def validate_files_and_comments(snap):
    """Drift checks between files and GitHub (1, 2). Run at reconcile and on the handoff PR."""
    return [e for check in FILE_CHECKS for e in check(snap)]


def _report(errors):
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


def main(argv):
    if len(argv) == 3 and argv[1] == "commit-msg":
        return _report(check_commit_message(Path(argv[2]).read_text(encoding="utf-8")))
    if len(argv) == 3 and argv[1] == "snapshot":
        snap = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        return _report(validate_snapshot(snap) + validate_files_and_comments(snap))
    print("usage: upstream_validate.py commit-msg <file> | snapshot <snapshot.json>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
