#!/usr/bin/env python3
"""
run_ci_locally.py — run this repo's push-triggered CI steps on a commit before it is pushed,
so a failing check is caught on this machine instead of turning the public badge red.

Called by .githooks/pre-push (enable once per clone: git config core.hooksPath .githooks).
Also runnable by hand:  python .githooks/run_ci_locally.py [COMMIT]   (default HEAD)

It reads the workflow files themselves, so it can't drift from CI: every `run:` step of every
workflow triggered on `push` runs, in order, in a temporary worktree of the exact commit being
pushed (never the working folder, which may hold uncommitted changes).

What it can't do locally, it says so and skips:
  - `uses:` steps (actions); checkout and setup-python are what the local worktree replaces
  - steps with an `if:` or with ${{ … }} expressions, which need GitHub's context
  - `pip install` lines (install once on this machine; a missing module then fails loudly)
Paths under `plugins/<repo>` (checked out from sibling repos in CI) map to `../<repo>` here.
If `claude` is on PATH and the repo is a plugin, `claude plugin validate --strict` runs too.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("run_ci_locally: PyYAML is needed to read the workflows (pip install pyyaml); push blocked")


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def push_steps(workflow: Path) -> list[tuple[str, str]]:
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8")) or {}
    triggers = doc.get("on", doc.get(True, {}))            # PyYAML reads a bare `on:` key as True
    if isinstance(triggers, str):
        triggers = {triggers: None}
    elif isinstance(triggers, list):
        triggers = {t: None for t in triggers}
    if "push" not in (triggers or {}):
        return []
    steps = []
    for job in (doc.get("jobs") or {}).values():
        for i, step in enumerate(job.get("steps") or []):
            name = step.get("name") or f"step {i + 1}"
            if "run" not in step:
                continue
            if "if" in step or "${{" in step["run"]:
                print(f"  skip  {name}  (needs GitHub's context)")
                continue
            steps.append((name, step["run"]))
    return steps


def main() -> int:
    repo = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()))
    commit = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    sha = git("rev-parse", commit, cwd=repo)
    workflows = sorted((repo / ".github" / "workflows").glob("*.y*ml"))
    bash = shutil.which("bash") or "bash"
    tmp = Path(tempfile.mkdtemp(prefix="ci-local-"))
    wt = tmp / "wt"
    git("worktree", "add", "--detach", str(wt), sha, cwd=repo)
    failed: list[str] = []
    ran = 0
    try:
        for wf in workflows:
            steps = push_steps(wt / ".github" / "workflows" / wf.name) if (wt / ".github" / "workflows" / wf.name).exists() else []
            for name, script in steps:
                script = "\n".join(l for l in script.splitlines() if not l.strip().startswith("pip install"))
                script = re.sub(r"\bplugins/([A-Za-z0-9._-]+)", lambda m: str(repo.parent / m.group(1)).replace("\\", "/"), script)
                missing = [p for p in re.findall(r"(?:^|\s)(/[^\s]+|[A-Za-z]:/[^\s]+)", script) if not Path(p).exists()]
                if missing:
                    print(f"  skip  {name}  (not on this machine: {', '.join(missing)})")
                    continue
                r = subprocess.run([bash, "-e", "-c", script], cwd=wt, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=600)
                ran += 1
                if r.returncode == 0:
                    print(f"  ok    {name}")
                else:
                    failed.append(name)
                    print(f"  FAIL  {name}")
                    print("\n".join("        " + l for l in (r.stdout + r.stderr).strip().splitlines()[-15:]))
        if (wt / ".claude-plugin" / "plugin.json").exists() and shutil.which("claude"):
            r = subprocess.run(["claude", "plugin", "validate", "--strict", "."], cwd=wt, capture_output=True, text=True)
            ran += 1
            label = "claude plugin validate --strict (local extra)"
            if r.returncode == 0:
                print(f"  ok    {label}")
            else:
                failed.append(label)
                print(f"  FAIL  {label}\n        " + (r.stdout + r.stderr).strip()[-400:])
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=repo, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    if failed:
        print(f"\n{len(failed)} CI step(s) fail on {sha[:7]}; push blocked. Fix and commit, then push again.")
        return 1
    print(f"\nall {ran} local CI step(s) pass on {sha[:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
