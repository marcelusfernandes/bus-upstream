"""Pure plans for every contract write an agent makes after intake.

Each plan_* function takes a snapshot ({"issues", "files"}) and returns an ordered list
of actions for scripts/upstream_ops.py to execute. Paired writes (header + comment,
comment + file, label + register) always come out of the same plan, so the validator's
drift checks hold by construction. Plans raise OpsError instead of producing a write
that breaks a rule.
"""
import re
import statistics

import decisions
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
    waiting = decisions.awaiting_pm(epic) or any("human:pending" in ch["labels"] for ch in children)
    if state in ("in-review", "done") and waiting:
        raise OpsError(f"{layer} has a decision waiting for the PM; it cannot move to {state}")
    if state == "done":
        open_h = [ch["title"] for ch in children if "type:hypothesis" in ch["labels"] and "hyp:open" in ch["labels"]]
        if open_h:
            raise OpsError(f"{layer} has open hypotheses: {open_h}")
    target = f"state:{state}"
    remove = [l for l in epic["labels"] if l.startswith("state:") and l != target]
    add = [target]
    if state == "blocked":  # anti-loop: a blocked layer always waits for a human (check 4)
        add.append("human:pending")
        remove += [l for l in ("human:decided",) if l in epic["labels"]]  # one human: label
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
    if not any(decision_id in decisions.records(i) for i in snap["issues"]):
        raise OpsError(f"{decision_id} is not recorded yet; record the decision before the answer")


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


# ---------- decisions (they live in the issue that requests them) ----------

def _request_comment(decision_id, ref, question, context, options, recommendation, why, would_change, evidence,
                     blocks, piloted):
    lines = [f"## Decision request {decision_id} · {ref} · {question}", "", f"**Context:** {context}", "",
             "**Options**"]
    lines += [f"- **{o['key']}** — {_one_line(o['text'], 'option')} · trade-offs: {o.get('tradeoffs', '—')}"
              f" · reversibility: {o.get('reversibility', '—')}" for o in options]
    lines += ["", f"**Recommendation:** {recommendation} — {why}",
              f"**What would change the recommendation:** {would_change}",
              f"**Evidence:** {', '.join(evidence) or '—'} · **Blocks:** {blocks}"]
    if piloted:  # instructions stay inline: a line starting with /decide must only ever come from the PM
        lines += ["", f"To decide, reply on this issue with `/decide {recommendation}` (add `Why: <your reasoning>` on "
                      f"the next line) or `/decide other: <your option>`. If several decisions are waiting here, "
                      f"name this one: `/decide {decision_id} {recommendation}`. Other comments keep it pending."]
    return "\n".join(lines) + "\n"


def _with_checklist_line(body, line, replace_prefix=None):
    """Add (or replace) a line in the issue body's `### Decisions` checklist."""
    lines = (body or "").rstrip("\n").split("\n")
    if replace_prefix:
        for n, existing in enumerate(lines):
            if existing.startswith(replace_prefix):
                lines[n] = line
                return "\n".join(lines) + "\n"
    if "### Decisions" not in lines:
        lines += ["", "### Decisions", ""]
    lines.append(line)
    return "\n".join(lines) + "\n"


def _all_decision_ids(snap):
    return {rid for i in snap["issues"] for rid in list(decisions.requests(i)) + list(decisions.records(i))}


def _check_request_lengths(question, context, options):
    """Format limits, so a PM can decide from the issue alone (detail lives in the answer draft)."""
    if len(question) > c.REQUEST_QUESTION_MAX:
        raise OpsError(f"question is longer than {c.REQUEST_QUESTION_MAX} characters; move detail to the context")
    if not context or len(context) > c.REQUEST_CONTEXT_MAX:
        raise OpsError(f"context is required and at most {c.REQUEST_CONTEXT_MAX} characters")
    for o in options:
        for field in ("text", "tradeoffs"):
            if len(o.get(field, "")) > c.REQUEST_OPTION_MAX:
                raise OpsError(f"option {o.get('key')} {field} is longer than {c.REQUEST_OPTION_MAX} characters")


def plan_decision_open(snap, slug, decision_id, ref, question, options, recommendation, why, would_change,
                       evidence, blocks, context):
    if not re.fullmatch(c.DECISION_ID, decision_id):
        raise OpsError(f"{decision_id} is not a decision ID")
    if decision_id in _all_decision_ids(snap):
        raise OpsError(f"{decision_id} already exists")
    if not re.fullmatch(rf"{c.ANSWER_ID}|{c.FIT_ID}", ref):
        raise OpsError(f"{ref} is not an answer or fit ID")
    keys = [o.get("key") for o in options]
    if len(options) < 2 or len(set(keys)) != len(keys) or not all(re.fullmatch(r"[A-Z]", k or "") for k in keys):
        raise OpsError("a decision needs at least two options with unique keys A, B, C…")
    if recommendation not in keys:
        raise OpsError("the recommendation must be one of the option keys")
    _one_line(question, "question")
    _check_request_lengths(question, context, options)
    _require_evidence(snap, slug, evidence)
    _require_answer_file(snap, slug, ref)
    pm, mode = _readme_value(snap, slug, "PM"), _readme_value(snap, slug, "Mode") or "piloted"
    if not pm:
        raise OpsError("initiative README has no 'PM: @login' line")
    pm, piloted = pm.lstrip("@"), mode == "piloted"
    epic = _epic(snap, _layer_of(ref))
    n = epic["number"]
    actions = [{"kind": "comment", "issue": n, "body": _request_comment(
        decision_id, ref, question, context, options, recommendation, why, would_change, evidence, blocks, piloted)},
        {"kind": "edit_body", "issue": n,
         "body": _with_checklist_line(epic["body"], f"- [ ] {decision_id} · {question}")}]
    if pm not in epic.get("assignees", []):
        actions.append({"kind": "assign", "issue": n, "assignees": [pm]})
    if piloted and ("human:pending" not in epic["labels"] or "human:decided" in epic["labels"]):
        # one human: label: a new request makes the issue pending again
        actions.append({"kind": "labels", "issue": n, "add": ["human:pending"],
                        "remove": [l for l in ("human:decided",) if l in epic["labels"]]})
    return actions


def _autonomous(snap, issue):
    parent = next((i for i in snap["issues"] if i["number"] == issue.get("parent")), None)
    return "mode:autonomous" in issue["labels"] or bool(parent and "mode:autonomous" in parent["labels"])


def plan_decision_record(snap, slug, decision_id, agent_choice=None, agent_why=None):
    issue, req = decisions.find_request(snap, decision_id)
    if not issue:
        raise OpsError(f"no request for {decision_id}")
    if decision_id in decisions.records(issue):
        raise OpsError(f"{decision_id} is already recorded")
    actions, add_labels = [], []
    decided = decisions.pm_decision(issue, decision_id)
    if decided:
        choice, why = decided["choice"], decided["why"]
        by = f"@{decided['author']} (/decide {choice}) on {decided['created_at'][:10]}"
    elif agent_choice:
        if not _autonomous(snap, issue):
            raise OpsError("only autonomous mode lets the agent decide")
        choice, why, by = agent_choice, agent_why, "agent (autonomous mode)"
        add_labels.append("agent:decided")
    else:
        raise OpsError(f"{decision_id} is not decided yet")
    answer = decisions.answer_text(issue, decision_id, choice)
    if not answer:
        raise OpsError(f"choice {choice} is not one of the options {sorted(req['options'])}")
    title = f"## Decision {decision_id} · {req['ref']} · {_one_line(answer, 'answer')}"
    still_waiting = [w for w in decisions.awaiting_pm(issue) if w != decision_id]
    remove = ["human:pending"] if "human:pending" in issue["labels"] and not still_waiting else []
    if decided and not still_waiting and "human:decided" not in issue["labels"]:
        add_labels.append("human:decided")  # the Action normally did this already
    if add_labels or remove:
        actions.append({"kind": "labels", "issue": issue["number"], "add": add_labels, "remove": remove})
    body = _with_checklist_line(issue.get("body"), f"- [x] {decision_id} · {req['question']} → {answer}",
                                replace_prefix=f"- [ ] {decision_id} ·")
    path = f"{_base(slug)}/decisions/{decision_id}.md"
    return actions + [
        {"kind": "write_file", "path": path,
         "text": f"{title}\n\nQuestion: {req['question']}\nDecided by: {by}\nWhy: {why or '—'}\n"
                 f"Issue: #{issue['number']}\n"},
        {"kind": "comment", "issue": issue["number"], "body": f"{title}\nDecided by: {by} · Why: {why or '—'}"},
        {"kind": "edit_body", "issue": issue["number"], "body": body},
        _commit(f"chore({slug}): record decision {decision_id}", [path])]


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


# ---------- label guard, replies, relayed decisions, checkpoints, summaries ----------

def plan_fix_labels(snap):
    """Make the decision labels match the comments (one human: label at most) and say so."""
    actions = []
    for issue, add, remove in v.label_fixes(snap):
        why = ("a decision is waiting for the PM" if "human:pending" in add
               else "nothing is waiting for the PM and the PM decided" if "human:decided" in add
               else "a decision is still waiting for the PM; `human:decided` returns once nothing waits"
               if "human:decided" in remove
               else "the comments show no decision waiting" if "human:pending" in remove
               else "the comments show the state")
        changes = ", ".join([f"added `{l}`" for l in add] + [f"removed `{l}`" for l in remove])
        actions += [{"kind": "labels", "issue": issue["number"], "add": add, "remove": remove},
                    {"kind": "comment", "issue": issue["number"], "body": f"## Labels fixed\n{changes}: {why}."}]
    return actions


def _open_request(snap, decision_id):
    issue, req = decisions.find_request(snap, decision_id)
    if not issue or decision_id not in decisions.open_requests(issue):
        raise OpsError(f"{decision_id} is not an open decision request")
    return issue, req


def plan_reply(snap, decision_id, text):
    """Answer a PM comment on a pending decision: options and a recommendation, never an open question."""
    issue, _ = _open_request(snap, decision_id)
    if not text.strip() or any(line.startswith("/decide") for line in text.splitlines()):
        raise OpsError("reply text is required and must never start a line with /decide")
    return [{"kind": "comment", "issue": issue["number"], "body": f"## Reply · {decision_id}\n\n{text.strip()}"}]


def plan_relay_decide(snap, slug, decision_id, choice, why):
    """Post the PM's own answer, typed in Codex, verbatim. It is the PM's decision: no agent marker."""
    import decide_action
    issue, _ = _open_request(snap, decision_id)
    pm = (_readme_value(snap, slug, "PM") or "").lstrip("@")
    refusal = decide_action._refusal(issue, decision_id, choice, pm)
    if refusal:
        raise OpsError(refusal)
    body = f"/decide {decision_id} {choice}" + (f"\nWhy: {_one_line(why, 'why')}" if why else "") + \
        f"\n{c.RELAY_MARKER}"
    return [{"kind": "comment", "issue": issue["number"], "body": body, "sign": False}]


def plan_checkpoint(slug, reason):
    """Save work in progress (drafts, evidence) on the branch before stopping, so GitHub shows it."""
    return [{"kind": "commit", "paths": [_base(slug)], "message": f"chore({slug}): checkpoint {_one_line(reason, 'reason')}",
             "allow_empty": False, "skip_if_clean": True}]


def _answer_rows(snap, slug, folder):
    pattern = re.compile(rf"^{re.escape(_base(slug))}/{folder}/answers/({c.ANSWER_ID})\.md$")
    rows = []
    for path in sorted(snap["files"]):
        m = pattern.match(path)
        if not m:
            continue
        text = snap["files"][path]
        title = re.search(r"^# \S+ · (.+)$", text, re.MULTILINE)
        answer = re.search(r"^\*\*Answer:\*\* (.+)$", text, re.MULTILINE)
        state = re.search(r"^\*\*State:\*\* (\w+)", text, re.MULTILINE)
        rows.append((m.group(1), title.group(1) if title else "—", state.group(1) if state else "—",
                     answer.group(1) if answer else "—"))
    return rows


def _replace_section(body, heading, section):
    """Replace (or insert before ### Decisions) a `### heading` section of the issue body."""
    lines, out, skipping = body.rstrip("\n").split("\n"), [], False
    for line in lines:
        if line.startswith("### "):
            skipping = line == heading
            if skipping:
                continue
        if not skipping:
            out.append(line)
    text = "\n".join(out)
    if "### Decisions" in out:
        return text.replace("### Decisions", section.rstrip("\n") + "\n\n### Decisions", 1) + "\n"
    return text.rstrip("\n") + "\n\n" + section


def plan_summary(snap, slug, layer, repo):
    """Make the layer epic self-contained: statement, key questions with answer and state, and a
    link to the files on the branch. A PM reading only GitHub can follow and decide."""
    epic = _epic(snap, layer)
    folder = LAYER[layer][1]
    rows = _answer_rows(snap, slug, folder)
    table = "### Key questions\n\n| ID | Question | State | Answer |\n|---|---|---|---|\n" + "".join(
        f"| {i} | {_cell(q)} | {s} | {_cell(a if len(a) <= 160 else a[:157] + '…')} |\n" for i, q, s, a in rows) \
        if rows else "### Key questions\n\nNo answer drafted yet.\n"
    statement_id = {"B": "B-01", "U": "U-01", "S": "S-02"}.get(layer)
    statement = next((a for i, _, s, a in rows if i == statement_id and s in ("evidenced", "bet")), "not yet writable")
    link = f"https://github.com/{repo}/tree/{('upstream/' + slug)}/{_base(slug)}/{folder}"
    statement_line, files_line = f"**Statement:** {_cell(statement)}", f"**Files:** [{_base(slug)}/{folder}]({link})"
    body = epic["body"]
    if not re.search(r"^\*\*Statement:\*\* ", body, re.M):  # older or minimal bodies: insert below the header
        first, _, rest = body.partition("\n")
        body = f"{first}\n\n{statement_line}\n\n{files_line}\n{rest}"
    body = re.sub(r"^\*\*Statement:\*\* .*$", statement_line, body, count=1, flags=re.M)
    if re.search(r"^\*\*(?:Reading order|Files):\*\* ", body, re.M):
        body = re.sub(r"^\*\*(?:Reading order|Files):\*\* .*$", files_line, body, count=1, flags=re.M)
    else:
        body = body.replace(statement_line, f"{statement_line}\n\n{files_line}", 1)
    body = _replace_section(body, "### Key questions", table)
    return [{"kind": "edit_body", "issue": epic["number"], "body": body}]


def sign(actions, role):
    """Every agent comment carries the invisible Enceladus marker, except a relayed PM decision."""
    return [dict(a, body=a["body"] + c.signature(role)) if a["kind"] == "comment" and a.get("sign", True) else a
            for a in actions]
