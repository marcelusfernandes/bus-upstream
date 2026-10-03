"""Pure plans for every contract write an agent makes after intake.

Each plan_* function takes a snapshot ({"issues", "files"}) and returns an ordered list
of actions for scripts/upstream_ops.py to execute. Paired writes (header + comment,
comment + file, label + register) always come out of the same plan, so the validator's
drift checks hold by construction. Plans raise OpsError instead of producing a write
that breaks a rule.
"""
import re
import statistics

import upstream_contract as c
import upstream_validate as v

LAYER = {"B": ("layer:business", "business"), "U": ("layer:user", "user"),
         "S": ("layer:solution", "solution"), "PRD": ("layer:prd", "prd")}
STATES = tuple(value for f in c.LABEL_FAMILIES if f.prefix == "state:" for value, _ in f.values)
HYP_STATUSES = ("validated", "invalidated", "parked", "reframed", "merged")


class OpsError(ValueError):
    pass


# ---------- lookups ----------

def _base(slug):
    return f"initiatives/{slug}"


def _epic(snap, layer):
    label = LAYER[layer][0]
    for i in snap["issues"]:
        if "epic" in i["labels"] and label in i["labels"]:
            return i
    raise OpsError(f"no epic for layer {layer}")


def _children(snap, number):
    return [i for i in snap["issues"] if i.get("parent") == number]


def _by_id(snap, prefix_id, type_label):
    for i in snap["issues"]:
        if type_label in i["labels"] and re.match(rf"^{re.escape(prefix_id)}\b", i["title"]):
            return i
    return None


def _readme_value(snap, slug, key):
    text = snap["files"].get(f"{_base(slug)}/README.md", "")
    m = re.search(rf"^{key}: (\S+)\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def _layer_of(target):
    if target == "PRD":
        return "PRD"
    if target == "BU-fit":
        return "U"
    if target == "US-fit":
        return "S"
    return target[0]


def _one_line(text, name):
    if not text or "\n" in text:
        raise OpsError(f"{name} must be one non-empty line")
    return text


def _cell(text):
    return str(text).replace("|", "/").replace("\n", " ")


def _evidence_files(snap, slug):
    """E-id -> path of its evidence file."""
    pattern = re.compile(rf"^{re.escape(_base(slug))}/[a-z]+/evidence/({c.EVIDENCE_ID})\.md$")
    return {m.group(1): path for path in snap["files"] if (m := pattern.match(path))}


def _evidence_paths(snap, slug):
    return set(_evidence_files(snap, slug))


def _answer_path(slug, answer_id):
    return f"{_base(slug)}/{LAYER[answer_id[0]][1]}/answers/{answer_id}.md"


def _require_answer_file(snap, slug, answer_id):
    if re.fullmatch(c.ANSWER_ID, answer_id) and _answer_path(slug, answer_id) not in snap["files"]:
        raise OpsError(f"draft {_answer_path(slug, answer_id)} first (state 'open' is fine)")


def _require_evidence(snap, slug, evidence):
    for eid in evidence:
        if not re.fullmatch(c.EVIDENCE_ID, eid):
            raise OpsError(f"{eid} is not an evidence ID")
    missing = sorted(set(evidence) - _evidence_paths(snap, slug))
    if missing:
        raise OpsError(f"evidence not recorded as files: {', '.join(missing)}")


def _commit(message, paths, allow_empty=False):
    """Each operation commits only its own files, so a later answer commit is never swallowed."""
    errors = v.check_commit_message(message)
    if errors:
        raise OpsError("; ".join(str(e) for e in errors))
    return {"kind": "commit", "paths": sorted(set(paths)), "message": message, "allow_empty": allow_empty}


# ---------- route ----------

def plan_route(snap, layer, state):
    if state not in STATES:
        raise OpsError(f"state must be one of {STATES}")
    epic = _epic(snap, layer)
    children = _children(snap, epic["number"])
    if state in ("in-review", "done") and any("human:pending" in ch["labels"] for ch in children):
        raise OpsError(f"{layer} has a pending human decision; it cannot move to {state}")
    if state == "done":
        open_h = [ch["title"] for ch in children if "type:hypothesis" in ch["labels"] and "hyp:open" in ch["labels"]]
        if open_h:
            raise OpsError(f"{layer} has open hypotheses: {open_h}")
    target = f"state:{state}"
    remove = [l for l in epic["labels"] if l.startswith("state:") and l != target]
    add = [target]
    if state == "blocked":  # anti-loop: a blocked layer always waits for a human (check 4)
        add.append("human:pending")
    elif "human:pending" in epic["labels"]:
        remove.append("human:pending")
    return [{"kind": "labels", "issue": epic["number"], "add": add, "remove": remove}]


# ---------- score ----------

def plan_score(snap, layer, panel, why, mostly_bets=False):
    if not 2 <= len(panel) <= 3:
        raise OpsError("a re-score needs a panel of 2 or 3 scorers")
    for d, g in panel:
        if not (c.SCORE_MIN <= d <= c.SCORE_MAX and c.SCORE_MIN <= g <= c.SCORE_MAX):
            raise OpsError("scores must be 0-10")
    ds, gs = [d for d, _ in panel], [g for _, g in panel]
    d, g = round(statistics.median(ds)), round(statistics.median(gs))
    if mostly_bets:
        g = min(g, 5)
    spread = max(max(ds) - min(ds), max(gs) - min(gs))
    epic = _epic(snap, layer)
    old = re.search(c.SCORE_HEADER, epic["body"].replace("\r\n", "\n"), re.MULTILINE)
    if not old:
        raise OpsError(f"{layer} epic has no score header")
    header = f"> **Definition:** {d} · **Grounding:** {g} · **Spread:** {spread}"
    body = epic["body"].replace(old.group(0), header, 1)
    title = f"## Score · {layer} · Definition {old['d']} → {d} · Grounding {old['g']} → {g}"
    return [{"kind": "edit_body", "issue": epic["number"], "body": body},
            {"kind": "comment", "issue": epic["number"],
             "body": f"{title}\nWhy: {_one_line(why, 'why')} · Spread: {spread}"}]


# ---------- review ----------

def plan_review(snap, slug, target, verdict, blocking="none", return_to="none"):
    if not re.fullmatch(rf"{c.ANSWER_ID}|{c.FIT_ID}|PRD", target):
        raise OpsError(f"{target} is not a reviewable ID")
    if verdict not in ("approved", "rejected"):
        raise OpsError("verdict must be approved or rejected")
    _require_answer_file(snap, slug, target)
    layer = _layer_of(target)
    path = f"{_base(slug)}/{LAYER[layer][1]}/review.md"
    line = f"Blocking: {_one_line(blocking or 'none', 'blocking')} · Return to: {return_to or 'none'}"
    entry = f"## Review · {target} · {verdict}\n\n{line}\n"
    existing = snap["files"].get(path, "")
    text = entry + ("\n" + existing if existing else "")
    return [{"kind": "write_file", "path": path, "text": text},
            {"kind": "comment", "issue": _epic(snap, layer)["number"],
             "body": f"## Review · {target} · {verdict}\n{line} · Detail: {path}"},
            _commit(f"chore({slug}): review {target} {verdict}",
                    [path] + ([_answer_path(slug, target)] if re.fullmatch(c.ANSWER_ID, target) else []))]


# ---------- answer ----------

def _latest_review(snap, slug, answer_id):
    text = snap["files"].get(f"{_base(slug)}/{LAYER[answer_id[0]][1]}/review.md", "")
    for m in re.finditer(c.REVIEW_TITLE, text, re.MULTILINE):
        if m["id"] == answer_id:
            return m["verdict"]
    return None


def _require_decided(snap, decision_id):
    d = _by_id(snap, decision_id, "type:decision")
    if not d or not ({"human:decided", "agent:decided"} & set(d["labels"])):
        raise OpsError(f"{decision_id} is not decided yet")


def plan_answer(snap, slug, answer_id, text, why, evidence, reasoning, learning, decision=None):
    if not re.fullmatch(c.ANSWER_ID, answer_id):
        raise OpsError(f"{answer_id} is not an answer ID")
    _one_line(text, "answer")  # one sentence for B1/U1/S2 is judged by the reviewer, not here
    layer, folder = answer_id[0], LAYER[answer_id[0]][1]
    path = f"{_base(slug)}/{folder}/answers/{answer_id}.md"
    if path not in snap["files"]:
        raise OpsError(f"write {path} before committing the answer")
    _require_evidence(snap, slug, evidence)
    if _latest_review(snap, slug, answer_id) != "approved":
        raise OpsError(f"{answer_id} needs an approved review before it is committed")
    if decision:
        _require_decided(snap, decision)
    trailers = [f"Layer: {folder}"] + ([f"Evidence: {', '.join(evidence)}"] if evidence else []) + (
        [f"Decision: {decision}"] if decision else [])
    message = (f"{answer_id}: {text}\n\nReasoning: {_one_line(reasoning, 'reasoning')}\n"
               f"Learning: {_one_line(learning, 'learning')}\n\n" + "\n".join(trailers) + "\n")
    refs = " · ".join(x for x in (f"Evidence: {', '.join(evidence)}" if evidence else "",
                                  f"Decision: {decision}" if decision else "") if x)
    body = f"## Answer {answer_id} · {text}\nWhy: {_one_line(why, 'why')}" + (f" · {refs}" if refs else "") + \
        f" · Detail: {path}"
    readme = f"{_base(slug)}/{folder}/README.md"
    files = _evidence_files(snap, slug)
    paths = [path] + [files[e] for e in evidence] + ([readme] if readme in snap["files"] else [])
    return [_commit(message, paths, allow_empty=True),
            {"kind": "comment", "issue": _epic(snap, layer)["number"], "body": body}]


# ---------- decisions ----------

def _decision_body(decision_id, ref, question, options, recommendation, why, would_change, evidence, blocks, piloted):
    lines = [f"## {decision_id} · {question}", "", f"**Ref:** {ref}", "", f"**Question:** {question}", "",
             "**Options**"]
    lines += [f"- **{o['key']}** — {_one_line(o['text'], 'option')} · trade-offs: {o.get('tradeoffs', '—')}"
              f" · reversibility: {o.get('reversibility', '—')}" for o in options]
    lines += ["", f"**Recommendation:** {recommendation} — {why}", "",
              f"**What would change the recommendation:** {would_change}", "",
              f"**Evidence:** {', '.join(evidence) or '—'} · **Blocks:** {blocks}"]
    if piloted:
        lines += ["", "---", "", "### How to decide", "", "Reply with your own comment:", "",
                  f"/decide {recommendation}", "/decide other: <your own option>", "",
                  "From another issue, name the decision:", "", f"/decide {decision_id} {recommendation}", "",
                  "Add `Why: <your reasoning>` on the next line. Other comments keep the decision pending."]
    return "\n".join(lines) + "\n"


def plan_decision_open(snap, slug, decision_id, ref, question, options, recommendation, why, would_change,
                       evidence, blocks):
    if not re.fullmatch(c.DECISION_ID, decision_id):
        raise OpsError(f"{decision_id} is not a decision ID")
    if _by_id(snap, decision_id, "type:decision"):
        raise OpsError(f"{decision_id} already exists")
    if not re.fullmatch(rf"{c.ANSWER_ID}|{c.FIT_ID}", ref):
        raise OpsError(f"{ref} is not an answer or fit ID")
    keys = [o.get("key") for o in options]
    if len(options) < 2 or len(set(keys)) != len(keys) or not all(re.fullmatch(r"[A-Z]", k or "") for k in keys):
        raise OpsError("a decision needs at least two options with unique keys A, B, C…")
    if recommendation not in keys:
        raise OpsError("the recommendation must be one of the option keys")
    _one_line(question, "question")
    _require_evidence(snap, slug, evidence)
    _require_answer_file(snap, slug, ref)
    pm, mode = _readme_value(snap, slug, "PM"), _readme_value(snap, slug, "Mode") or "piloted"
    if not pm:
        raise OpsError("initiative README has no 'PM: @login' line")
    layer = _layer_of(ref)
    labels = ["type:decision", LAYER[layer][0]] + (["human:pending"] if mode == "piloted" else [])
    body = _decision_body(decision_id, ref, question, options, recommendation, why, would_change, evidence, blocks,
                          mode == "piloted")
    return [{"kind": "create_issue", "title": f"{decision_id} · {question}", "body": body, "labels": labels,
             "assignees": [pm.lstrip("@")], "parent": _epic(snap, layer)["number"]}]


def _options(body):
    return {m.group(1): m.group(2) for m in re.finditer(r"^- \*\*([A-Z])\*\* — (.+?) · trade-offs:", body, re.M)}


def _pm_decide(snap, decision):
    """(author, choice, why) of the latest valid /decide by an assignee, or None."""
    did = re.match(c.DECISION_ID, decision["title"]).group(0)
    found = []
    for i in snap["issues"]:
        for cm in i.get("comments", []):
            if cm["author"] not in decision["assignees"]:
                continue
            text = cm["body"].replace("\r\n", "\n")
            m = re.search(c.DECIDE_COMMAND, text, re.MULTILINE)
            if m and ((m["target"] is None and i is decision) or m["target"] == did):
                why = re.search(r"^Why: (.+)$", text, re.MULTILINE)
                found.append((cm["created_at"], cm["author"], m["choice"], why.group(1) if why else None))
    return max(found)[1:] if found else None


def _parent_mode(snap, decision):
    parent = next((i for i in snap["issues"] if i["number"] == decision.get("parent")), None)
    return "autonomous" if parent and "mode:autonomous" in parent["labels"] else "piloted"


def plan_decision_record(snap, slug, decision_id, agent_choice=None, agent_why=None):
    d = _by_id(snap, decision_id, "type:decision")
    if not d or d["state"] != "open":
        raise OpsError(f"{decision_id} is not an open decision")
    options = _options(d["body"])
    ref = re.search(r"^\*\*Ref:\*\* (\S+)$", d["body"], re.MULTILINE)
    if not ref:
        raise OpsError(f"{decision_id} body has no **Ref:** line")
    actions = []
    if "human:decided" in d["labels"]:
        decided = _pm_decide(snap, d)
        if not decided:
            raise OpsError(f"{decision_id} is labeled decided but has no /decide from the assigned PM")
        author, choice, why = decided
        by = f"@{author} (/decide {choice})"
    elif agent_choice:
        if _parent_mode(snap, d) != "autonomous":
            raise OpsError("only autonomous mode lets the agent decide")
        choice, why, by = agent_choice, agent_why, "agent (autonomous mode)"
        actions.append({"kind": "labels", "issue": d["number"], "add": ["agent:decided"], "remove": []})
    else:
        raise OpsError(f"{decision_id} is not decided yet")
    answer = choice[len("other: "):] if choice.startswith("other: ") else options.get(choice)
    if not answer:
        raise OpsError(f"choice {choice} is not one of the options {sorted(options)}")
    title = f"## Decision {decision_id} · {ref.group(1)} · {_one_line(answer, 'answer')}"
    record = f"{title}\n\nDecided by: {by}\nWhy: {why or '—'}\nIssue: #{d['number']}\n"
    return actions + [
        {"kind": "write_file", "path": f"{_base(slug)}/decisions/{decision_id}.md", "text": record},
        {"kind": "comment", "issue": d["number"], "body": f"{title}\nDecided by: {by} · Why: {why or '—'}"},
        {"kind": "close", "issue": d["number"]},
        _commit(f"chore({slug}): record decision {decision_id}", [f"{_base(slug)}/decisions/{decision_id}.md"])]


# ---------- hypotheses ----------

def _update_register(text, hid, status, resolution):
    lines, column = text.splitlines(), None
    for n, line in enumerate(lines):
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if "Status" in cells:
            column = (cells.index("Status"), cells.index("Resolution") if "Resolution" in cells else None)
        elif column and cells and cells[0] == hid:
            cells[column[0]] = status
            if column[1] is not None:
                cells[column[1]] = resolution
            lines[n] = "| " + " | ".join(cells) + " |"
            return "\n".join(lines) + "\n"
    raise OpsError(f"{hid} is not in hypotheses.md")


def plan_hypothesis_close(snap, slug, hid, status, why, evidence, into=None):
    if status not in HYP_STATUSES:
        raise OpsError(f"status must be one of {HYP_STATUSES}")
    h = _by_id(snap, hid, "type:hypothesis")
    if not h or "hyp:open" not in h["labels"]:
        raise OpsError(f"{hid} is not an open hypothesis")
    if status in ("reframed", "merged") and not (into and re.fullmatch(c.HYPOTHESIS_ID, into)):
        raise OpsError(f"{status} needs the hypothesis it became (--into H-nn)")
    if status in ("validated", "invalidated") and not evidence:
        raise OpsError(f"{status} needs evidence")
    _require_evidence(snap, slug, evidence)
    full = f"{status} → {into}" if status in ("reframed", "merged") else status
    path = f"{_base(slug)}/hypotheses.md"
    resolution = _cell(f"{', '.join(evidence) or '—'} · {_one_line(why, 'why')}")
    refs = f" · Evidence: {', '.join(evidence)}" if evidence else ""
    return [{"kind": "write_file", "path": path,
             "text": _update_register(snap["files"].get(path, ""), hid, full, resolution)},
            {"kind": "comment", "issue": h["number"], "body": f"## Hypothesis {hid} · {full}\nWhy: {why}{refs}"},
            {"kind": "labels", "issue": h["number"], "add": [f"hyp:{status}"], "remove": ["hyp:open"]},
            {"kind": "close", "issue": h["number"]},
            _commit(f"chore({slug}): close {hid} as {status}", [path])]
