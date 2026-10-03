"""Issue bodies a PM reads on GitHub. They must be self-contained: no file paths as content,
evidence written out next to its ID. Shared by intake and `upstream_ops summary`."""
import re

import upstream_contract as c

LAYER_NAME = {"B": "Business", "U": "User", "S": "Solution"}


def _evidence_lines(text, claims):
    """Each E-id in `text` as '- E-nnn · <claim>' when the claim is known."""
    ids = list(dict.fromkeys(re.findall(c.EVIDENCE_ID, text or "")))
    return [f"- {eid} · {claims[eid]}" if eid in claims else f"- {eid}" for eid in ids]


def hypothesis_body(h, claims):
    """h: ID, Statement, Kind, Origin, Basis, Raised at, Routed to, Status, Resolution, Test (any may be missing)."""
    status = h.get("Status") or "open"
    lines = [f"## {h['ID']} · {h.get('Statement', '—')}", "",
             f"**As raised:** “{h.get('Statement', '—')}” — {h.get('Origin', '—')}", "",
             f"**Kind:** {h.get('Kind', '—')} · **Raised at:** {LAYER_NAME.get(h.get('Raised at'), h.get('Raised at', '—'))}"
             f" · **Tested in:** {LAYER_NAME.get(h.get('Routed to'), h.get('Routed to', '—'))}", "",
             f"**How it gets tested:** {h.get('Test') or 'not defined yet'}", "",
             f"**Status:** {status}"]
    if h.get("Resolution") and h["Resolution"] not in ("—", "-"):
        lines.append(f"**Resolution:** {h['Resolution']}")
    basis = h.get("Basis") or "—"
    lines += ["", f"**Basis:** {basis}"] + _evidence_lines(basis, claims)
    lines += ["", "Closed only with a `## Hypothesis <ID> · <status>` comment and the same status in the register."]
    return "\n".join(lines) + "\n"
