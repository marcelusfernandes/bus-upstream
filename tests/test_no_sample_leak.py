"""Guard: the golden case is a test sample. Its domain must not leak into the process
(skills, agent definitions, templates, spec rules, AGENTS.md), because agents copy examples.
Fix process problems, not the sample (see memory: fix-process-not-sample)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_TERMS = r"basket|cesta|sacola|repurchase|recompra|recurrence|recorr[eê]ncia|\bAOV\b|faster flow|fluxo mais r|than the App|converts? more|usual-basket"
PROCESS_FILES = (list((ROOT / ".agents" / "skills").rglob("*.md")) + list((ROOT / ".codex" / "agents").glob("*.toml"))
                 + list((ROOT / "templates").glob("*")) + [ROOT / "AGENTS.md"]
                 + [p for p in (ROOT / "spec" / "v1").glob("*.md")
                    if p.name not in ("09-worked-example.md", "11-legacy-mapping.md")])


class NoSampleLeak(unittest.TestCase):
    def test_process_files_do_not_carry_the_golden_case_domain(self):
        leaks = []
        for path in PROCESS_FILES:
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if re.search(SAMPLE_TERMS, line, re.IGNORECASE):
                    leaks.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()[:80]}")
        self.assertEqual(leaks, [], "golden-case terms in process files:\n" + "\n".join(leaks))


if __name__ == "__main__":
    unittest.main()
