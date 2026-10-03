"""Git steps every initiative needs: its own branch from an updated main, and a commit
and push of what was produced. PMs never do this by hand. The runner is injectable so
tests can assert the exact command sequence."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = ("main",)


class GitError(RuntimeError):
    pass


def run_git(args):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args[:2])}: {result.stderr.strip()}")
    return result.stdout


def branch_name(slug):
    return f"upstream/{slug}"


def ensure_branch(slug, git=run_git):
    """Switch to upstream/<slug>, creating it from an updated origin/main if needed."""
    branch = branch_name(slug)
    if git(["status", "--porcelain"]).strip():
        raise GitError("uncommitted changes; commit or stash them before starting an initiative")
    if git(["branch", "--show-current"]).strip() == branch:
        return branch
    git(["fetch", "origin", "main"])
    if git(["branch", "--list", branch]).strip():
        git(["switch", branch])
    elif git(["ls-remote", "--heads", "origin", branch]).strip():
        git(["fetch", "origin", branch])
        git(["switch", "-c", branch, "--track", f"origin/{branch}"])
    else:
        git(["switch", "-c", branch, "origin/main"])
    return branch


def commit_and_push(paths, message, branch, git=run_git, allow_empty=False):
    """allow_empty: an answer commit is a checkpoint even when its files were already committed."""
    if branch in PROTECTED:
        raise GitError(f"refusing to commit initiative work on {branch}")
    git(["add", "--", *paths])
    git(["commit", "-m", message] + (["--allow-empty"] if allow_empty else []))
    git(["push", "-u", "origin", branch])
