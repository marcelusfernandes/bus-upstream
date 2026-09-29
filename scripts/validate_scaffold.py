#!/usr/bin/env python3
from pathlib import Path
import tomllib, re, sys
ROOT=Path(__file__).resolve().parents[1]

def fail(msg): raise AssertionError(msg)

# agents TOML
agents=list((ROOT/'.codex/agents').glob('*.toml'))
if len(agents) < 5: fail('expected at least 5 custom agents')
for p in agents:
    with p.open('rb') as f: d=tomllib.load(f)
    for k in ('name','description','model','model_reasoning_effort','developer_instructions'):
        if not d.get(k): fail(f'{p}: missing {k}')

# skills
skills=list((ROOT/'.agents/skills').glob('*/SKILL.md'))
if len(skills) < 7: fail('expected at least 7 skills')
for p in skills:
    t=p.read_text(encoding='utf-8')
    if not t.startswith('---\n'): fail(f'{p}: missing frontmatter')
    if not re.search(r'^name:\s*\S+',t,re.M): fail(f'{p}: missing name')
    if not re.search(r'^description:\s*.+',t,re.M): fail(f'{p}: missing description')

# assert this is Codex-native, not Lohra runtime scaffold
banned=['run_workflow','workflow_status','workflow_preview','loop_until_dry','judge_panel']
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.md','.toml','.yml','.yaml','.json'}:
        t=p.read_text(encoding='utf-8',errors='ignore')
        for term in banned:
            if term in t: fail(f'{p}: contains runtime primitive {term}')

if (ROOT/'workflows').exists(): fail('workflows/ directory must not exist')

print(f'OK: {len(agents)} Codex agents, {len(skills)} skills, no Lohra runtime workflow layer')
