#!/usr/bin/env python3
"""
check_drift.py — fail when the shared parts of the Cairn plugin repos drift apart.

The plugins must each be self-contained, so the shared parts are copied into every repo
(decision D6). Copies drift. This compares each plugin repo against the reference in this
repo and fails on any difference in:

  palette      the colour and font tokens in assets/make_assets.py (INK … REDUCED)
  stones       the PEBBLES paths the logo mark and banners are drawn from
  icon         .claude-plugin/icon.svg against assets/icon.svg here
  logo         assets/cairn-logo.png against assets/cairn-logo.png here
  sections     the README's `## ` headings, in order
  badges       the four README badges (plugin, self-test, licence, privacy)
  family       the Cairn family table: the same three plugins and questions

Usage:
  python scripts/check_drift.py PLUGIN_REPO_DIR [PLUGIN_REPO_DIR ...]
  python scripts/check_drift.py --self-test

Read-only. Line endings are normalised, so a Windows checkout compares equal to Linux.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

SECTIONS = ["Who it's for", "What you get", "How it compares", "Install", "The script",
            "What it runs, and what it doesn't", "Evidence", "Privacy", "The Cairn family",
            "Who made this", "License"]
BADGES = [r"badge/Claude_Code-plugin-0A6CFF\?style=flat-square",
          r"workflow/status/nicuk/[\w.-]+/self-test\.yml\?branch=main&label=self-test&style=flat-square",
          r"badge/license-MIT-16A34A\?style=flat-square",
          r"badge/privacy-nothing_collected-6CCBFF\?style=flat-square"]
FAMILY = {
    "Cairn Memory": "Is what your agents remember cheap to load, and still true?",
    "Cairn Signals": "Are the numbers your AI product shows real?",
    "Cairn Verify": "Did the AI really fix it?",
}


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def block(src: str, start: str, end: str) -> str:
    i = src.find(start)
    if i < 0:
        return ""
    j = src.find(end, i)
    return src[i:j + len(end)] if j >= 0 else ""


def check(repo: Path, ref: Path) -> list[str]:
    name = repo.name
    problems: list[str] = []
    gen, ref_gen = repo / "assets/make_assets.py", ref / "assets/make_assets.py"
    if not gen.exists():
        return [f"{name}: assets/make_assets.py is missing"]
    g, rg = text(gen), text(ref_gen)
    if block(g, "INK = ", "REDUCED = ") != block(rg, "INK = ", "REDUCED = "):
        problems.append(f"{name}: palette tokens (INK … REDUCED) differ from the reference")
    if block(g, "PEBBLES = [", "\n]") != block(rg, "PEBBLES = [", "\n]"):
        problems.append(f"{name}: PEBBLES (the stone paths) differ from the reference")

    icon = repo / ".claude-plugin/icon.svg"
    if not icon.exists() or text(icon) != text(ref / "assets/icon.svg"):
        problems.append(f"{name}: .claude-plugin/icon.svg is missing or differs from assets/icon.svg")
    logo = repo / "assets/cairn-logo.png"
    if not logo.exists() or logo.read_bytes() != (ref / "assets/cairn-logo.png").read_bytes():
        problems.append(f"{name}: assets/cairn-logo.png is missing or differs")

    readme = text(repo / "README.md") if (repo / "README.md").exists() else ""
    heads = re.findall(r"^## (.+?)\s*$", readme, re.M)
    if heads != SECTIONS:
        problems.append(f"{name}: README sections are {heads}, expected {SECTIONS}")
    for b in BADGES:
        if not re.search(b, readme):
            problems.append(f"{name}: README badge missing or changed: {b}")
    fam = readme.split("## The Cairn family", 1)[-1].split("\n## ", 1)[0] if "## The Cairn family" in readme else ""
    for plugin, question in FAMILY.items():
        if not re.search(rf"\|[^|\n]*{re.escape(plugin)}[^|\n]*\|\s*{re.escape(question)}\s*\|", fam):
            problems.append(f"{name}: family table row for {plugin} is missing or its question changed")
    if "github.com/nicuk/cairn-principles" not in fam:
        problems.append(f"{name}: family section doesn't link nicuk/cairn-principles")
    if re.search(r"github\.com/nicuk/cairn(?![-\w])", readme):
        problems.append(f"{name}: README links the private repo nicuk/cairn")
    return problems


def self_test() -> int:
    """Copy this reference as a fake plugin repo, confirm it passes, then plant one defect
    per check and confirm each one is caught."""
    good_readme = "\n".join(
        ["[![a](https://img.shields.io/badge/Claude_Code-plugin-0A6CFF?style=flat-square)](#install)",
         "[![b](https://img.shields.io/github/actions/workflow/status/nicuk/x/self-test.yml?branch=main&label=self-test&style=flat-square)](y)",
         "[![c](https://img.shields.io/badge/license-MIT-16A34A?style=flat-square)](LICENSE)",
         "[![d](https://img.shields.io/badge/privacy-nothing_collected-6CCBFF?style=flat-square)](PRIVACY.md)", ""]
        + [f"## {s}\n\ntext\n" if s != "The Cairn family" else
           "## The Cairn family\n\n[principles](https://github.com/nicuk/cairn-principles)\n\n| Plugin | Q |\n|---|---|\n"
           + "".join(f"| **{p}** | {q} |\n" for p, q in FAMILY.items())
           for s in SECTIONS])
    defects = {
        "palette": lambda r: _sub(r / "assets/make_assets.py", '"#0A6CFF"', '"#0A6CFE"'),
        "stones": lambda r: _sub(r / "assets/make_assets.py", "M252,915", "M253,915"),
        "icon": lambda r: _sub(r / ".claude-plugin/icon.svg", "#1E4FB8", "#1E4FB9"),
        "logo": lambda r: (r / "assets/cairn-logo.png").write_bytes(b"not the logo"),
        "sections": lambda r: _sub(r / "README.md", "## Evidence", "## Results"),
        "badges": lambda r: _sub(r / "README.md", "license-MIT-16A34A", "license-MIT-green"),
        "family": lambda r: _sub(r / "README.md", "Did the AI really fix it?", "Did it fix it?"),
        "private-link": lambda r: _sub(r / "README.md", "\n## Who made this", "\n[plan](https://github.com/nicuk/cairn)\n\n## Who made this"),
    }
    ok = True
    with tempfile.TemporaryDirectory() as t:
        def fresh() -> Path:
            r = Path(t) / "plugin"
            if r.exists():
                shutil.rmtree(r)
            (r / "assets").mkdir(parents=True)
            (r / ".claude-plugin").mkdir()
            shutil.copy(HERE / "assets/make_assets.py", r / "assets/make_assets.py")
            shutil.copy(HERE / "assets/cairn-logo.png", r / "assets/cairn-logo.png")
            shutil.copy(HERE / "assets/icon.svg", r / ".claude-plugin/icon.svg")
            (r / "README.md").write_text(good_readme, encoding="utf-8")
            return r
        clean = check(fresh(), HERE)
        print(f"{'ok  ' if not clean else 'FAIL'} a faithful copy passes" + (f": {clean}" if clean else ""))
        ok &= not clean
        for label, plant in defects.items():
            r = fresh()
            plant(r)
            caught = check(r, HERE)
            print(f"{'ok  ' if caught else 'MISS'} {label}")
            ok &= bool(caught)
    print(f"\nself-test {'passed' if ok else 'FAILED'}: {len(defects)} planted defects")
    return 0 if ok else 1


def _sub(p: Path, a: str, b: str) -> None:
    s = p.read_text(encoding="utf-8")
    assert a in s, f"self-test fixture lost its anchor {a!r} in {p.name}"
    p.write_text(s.replace(a, b, 1), encoding="utf-8")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return self_test()
    if not args:
        print(__doc__)
        return 2
    problems = [p for a in args for p in check(Path(a).resolve(), HERE)]
    for p in problems:
        print("DRIFT", p)
    print(f"\n{len(args)} repo(s) checked, {len(problems)} drift finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
