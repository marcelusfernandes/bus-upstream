#!/usr/bin/env python3
"""Create or update the BUS upstream labels on the current GitHub repository.

Dry-run by default; pass --apply to run `gh label create --force` (idempotent).
Label families come from upstream_contract.LABEL_FAMILIES.
"""
import argparse
import subprocess
import sys

import upstream_contract as c


def label_specs():
    """[(name, color, description)] for every label in the contract."""
    return [(f"{family.prefix}{value}", family.color, description)
            for family in c.LABEL_FAMILIES for value, description in family.values]


def gh_command(name, color, description, repo=None):
    cmd = ["gh", "label", "create", name, "--color", color, "--description", description, "--force"]
    return cmd + (["--repo", repo] if repo else [])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="create/update labels on GitHub")
    parser.add_argument("--repo", help="owner/name (default: current repository)")
    args = parser.parse_args(argv)

    failures = 0
    for name, color, description in label_specs():
        cmd = gh_command(name, color, description, args.repo)
        if not args.apply:
            print("DRY-RUN", " ".join(cmd[:4]), f"({description})")
            continue
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            failures += 1
            print(f"FAILED {name}: {result.stderr.strip()}", file=sys.stderr)
        else:
            print(f"OK {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
