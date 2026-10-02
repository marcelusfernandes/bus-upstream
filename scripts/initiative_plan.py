"""Pure plan for a new initiative (the deterministic part of intake).

The intake agent does the judgment and writes an intake JSON (see
templates/intake.example.json). This module validates it and turns it into what must
exist on GitHub and on disk. scripts/create_initiative.py executes the plan.
"""
import copy
import re

import upstream_contract as c

LAYERS = (("B", "layer:business", "Business problem", "business"),
          ("U", "layer:user", "User problem", "user"),
          ("S", "layer:solution", "Solution", "solution"))
LAYER_LABEL = {code: label for code, label, _, _ in LAYERS}
LAYER_FOLDER = {code: folder for code, _, _, folder in LAYERS}
SLUG = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
MODES = ("piloted", "autonomous")
KINDS = ("user-problem", "solution", "causal")
REGISTER_HEADER = ("| ID | Statement | Kind | Origin | Basis | Raised at | Routed to | Status | Resolution |\n"
                   "|---|---|---|---|---|---|---|---|---|\n")


# ---------- validation ----------

def _one_sentence(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]) <= 1


def _validate_layer(code, layer):
    errors = []
    if not isinstance(layer, dict):
        return [f"layers.{code} is missing"]
    for axis in ("definition", "grounding"):
        value = layer.get(axis)
        if not isinstance(value, int) or not c.SCORE_MIN <= value <= c.SCORE_MAX:
            errors.append(f"layers.{code}.{axis} must be an integer 0-10")
    if not layer.get("why"):
        errors.append(f"layers.{code}.why is required (why the scores, not closer to the other extreme)")
    statement = layer.get("statement")
    if statement is not None and not _one_sentence(statement):
        errors.append(f"layers.{code}.statement must be one sentence")
    return errors


def _validate_hypothesis(h):
    errors, hid = [], h.get("id", "?")
    if not re.fullmatch(c.HYPOTHESIS_ID, str(hid)):
        errors.append(f"hypothesis id {hid} must look like H-01")
    for field in ("statement", "origin"):
        if not h.get(field):
            errors.append(f"{hid}: {field} is required")
    if h.get("kind") not in KINDS:
        errors.append(f"{hid}: kind must be one of {KINDS}")
    for field in ("raised_at", "routed_to"):
        if h.get(field) not in LAYER_LABEL:
            errors.append(f"{hid}: {field} must be B, U or S")
    if h.get("origin") == "agent" and not h.get("basis"):
        errors.append(f"{hid}: basis is required when origin is agent (evidence IDs or 'guess')")
    return errors


EVIDENCE_KINDS = ("fact", "hypothesis", "assumption", "inference", "decision", "unknown")


def _cited_evidence(data):
    texts = [data.get("demand", ""), data.get("context") or ""]
    for layer in (data.get("layers") or {}).values():
        if isinstance(layer, dict):
            texts += [layer.get("why") or "", layer.get("statement") or ""]
    texts += [str(h.get("basis", "")) for h in data.get("hypotheses", [])]
    return set(re.findall(c.EVIDENCE_ID, " ".join(texts)))


def _validate_evidence(data):
    errors, recorded = [], set()
    for e in data.get("evidence", []):
        eid = e.get("id", "?")
        if not re.fullmatch(c.EVIDENCE_ID, str(eid)):
            errors.append(f"evidence id {eid} must look like E-001")
        if e.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{eid}: kind must be one of {EVIDENCE_KINDS}")
        if e.get("layer") not in LAYER_LABEL:
            errors.append(f"{eid}: layer must be B, U or S")
        for field in ("claim", "source"):
            if not e.get(field):
                errors.append(f"{eid}: {field} is required")
        recorded.add(eid)
    for missing in sorted(_cited_evidence(data) - recorded):
        errors.append(f"{missing} is cited but not recorded in evidence")
    for unused in sorted(recorded - _cited_evidence(data)):
        errors.append(f"{unused} is recorded but never cited (cite it in a layer 'why' or a hypothesis basis)")
    return errors


def validate_intake(data):
    errors = _validate_evidence(data)
    if not re.fullmatch(SLUG, str(data.get("slug", ""))):
        errors.append("slug must be lowercase words joined by hyphens")
    for field in ("title", "demand"):
        if not data.get(field):
            errors.append(f"{field} is required")
    if data.get("mode", "piloted") not in MODES:
        errors.append(f"mode must be one of {MODES}")
    layers = data.get("layers") or {}
    for code in LAYER_LABEL:
        errors += _validate_layer(code, layers.get(code))
    ids = [h.get("id") for h in data.get("hypotheses", [])]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"duplicate hypothesis id {dup}")
    for h in data.get("hypotheses", []):
        errors += _validate_hypothesis(h)
    return errors


# ---------- plan ----------

def _cell(text):
    return str(text).replace("|", "/").replace("\n", " ")


def _epic_body(code, name, layer):
    statement = layer.get("statement") or "not yet writable"
    return (f"> **Definition:** {layer['definition']} · **Grounding:** {layer['grounding']} · **Spread:** 0\n\n"
            f"## {name}\n\n**Statement:** {statement}\n\n"
            f"**Reading order:** `initiatives/<slug>/README.md` → `{LAYER_FOLDER[code]}/README.md`\n\n"
            "This layer cannot reach `state:done` while a hypothesis routed here is `hyp:open`.\n")


def _first_score(code, layer):
    return (f"## Score · {code} · Definition – → {layer['definition']} · Grounding – → {layer['grounding']}\n"
            f"Why: {layer['why']}")


def _epics(data):
    common = ["epic", "state:ready", f"mode:{data.get('mode', 'piloted')}"]
    epics = [{"layer": code, "title": f"{code} · {name}", "labels": common + [label],
              "body": _epic_body(code, name, data["layers"][code]).replace("<slug>", data["slug"]),
              "first_comment": _first_score(code, data["layers"][code])}
             for code, label, name, _ in LAYERS]
    epics.append({"layer": "PRD", "title": "PRD", "labels": common + ["layer:prd"],
                  "body": f"PRD for `{data['slug']}`. Written by the PRD writer from the committed layers.\n",
                  "first_comment": None})
    return epics


def _hypothesis_issue(h):
    body = (f"## {h['id']} · {h['statement']}\n\n| Field | Value |\n|---|---|\n"
            f"| Kind | {h['kind']} |\n| Origin | {_cell(h['origin'])} |\n| Basis | {_cell(h.get('basis', ''))} |\n"
            f"| Raised at | {h['raised_at']} |\n| Routed to | {h['routed_to']} |\n")
    return {"id": h["id"], "title": f"{h['id']} · {h['statement']}", "body": body,
            "labels": ["type:hypothesis", "hyp:open", LAYER_LABEL[h["routed_to"]]], "parent_layer": h["routed_to"]}


def _register(hypotheses):
    rows = "".join(f"| {h['id']} | {_cell(h['statement'])} | {h['kind']} | {_cell(h['origin'])} | "
                   f"{_cell(h.get('basis', ''))} | {h['raised_at']} | {h['routed_to']} | open | — |\n"
                   for h in hypotheses)
    return REGISTER_HEADER + rows


def _intake_md(data):
    fragments = "".join(f"| {f['layer']} | {_cell(f['text'])} | {_cell(f['kind'])} |\n"
                        for f in data.get("fragments", []))
    table = ("\n## Fragments per layer\n\n| Layer | Fragment | Kind |\n|---|---|---|\n" + fragments) if fragments else ""
    return (f"# Intake · {data['title']}\n\n## Literal demand\n\n> {data['demand']}\n\n"
            f"## Context\n\n{data.get('context') or 'App (default)'}\n" + table)


def _evidence_md(e):
    lines = [f"id: {e['id']}", f"claim: \"{e['claim']}\"", f"kind: {e['kind']}", f"source: {e['source']}"]
    for field in ("population", "time_window", "freshness", "limitations"):
        if e.get(field):
            lines.append(f"{field}: {e[field]}")
    return "\n".join(lines) + "\n"


def _files(data):
    root = f"initiatives/{data['slug']}"
    readme = (f"# {data['title']}\n\nMilestone: #{{milestone}}\n\n## Reading order\n\n"
              "1. `intake.md` — the literal demand and context\n2. `hypotheses.md` — every hypothesis and its status\n"
              "3. `business/README.md`, `user/README.md`, `solution/README.md` — current answer per layer\n"
              "4. `prd/README.md` — the PRD, once written\n")
    files = {f"{root}/README.md": readme, f"{root}/intake.md": _intake_md(data),
             f"{root}/hypotheses.md": _register(data.get("hypotheses", [])),
             f"{root}/learnings.md": "# Learnings\n\nAppend-only: date · ID · what we believed · what invalidated it · what to do differently.\n",
             f"{root}/prd/README.md": "# PRD\n\nNot written yet.\n"}
    for code, _, name, folder in LAYERS:
        statement = data["layers"][code].get("statement") or "not yet writable"
        files[f"{root}/{folder}/README.md"] = f"# {name}\n\n**Statement:** {statement}\n"
    for e in data.get("evidence", []):
        files[f"{root}/{LAYER_FOLDER[e['layer']]}/evidence/{e['id']}.md"] = _evidence_md(e)
    return files


def plan_initiative(data):
    """Validated intake JSON -> {"milestone", "epics", "hypotheses", "files"}. Does not mutate input."""
    data = copy.deepcopy(data)
    return {
        "milestone": {"title": data["title"],
                      "description": f"Intake snapshot (static).\n\nDemand: {data['demand']}\n\n"
                                     f"Context: {data.get('context') or 'App (default)'}\n\n"
                                     f"Reading order: initiatives/{data['slug']}/README.md"},
        "epics": _epics(data),
        "hypotheses": [_hypothesis_issue(h) for h in data.get("hypotheses", [])],
        "files": _files(data),
    }


def plan_to_snapshot(plan, t0="2026-01-01T00:00:00Z"):
    """The snapshot the validator would see right after the plan is executed."""
    issues, number_of = [], {}
    for n, epic in enumerate(plan["epics"], start=1):
        number_of[epic["layer"]] = n
        comments = [{"author": "agent", "body": epic["first_comment"], "created_at": t0}] if epic["first_comment"] else []
        issues.append({"number": n, "title": epic["title"], "labels": list(epic["labels"]), "body": epic["body"],
                       "parent": None, "state": "open", "assignees": [], "comments": comments, "label_events": []})
    for n, h in enumerate(plan["hypotheses"], start=len(issues) + 1):
        issues.append({"number": n, "title": h["title"], "labels": list(h["labels"]), "body": h["body"],
                       "parent": number_of[h["parent_layer"]], "state": "open", "assignees": [],
                       "comments": [], "label_events": []})
    return {"issues": issues, "files": dict(plan["files"])}
