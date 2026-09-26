#!/usr/bin/env python3
"""Build the Claude.ai upload files: dist/hig42-design.skill and dist/hig42-design-zh-tw.skill.

  python3 tools/package.py

A .skill file is a zip of the skill folder (folder name at the root of the archive).
Run tools/check.py first; this script refuses to package if the checks fail.
"""
import subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = [
    ROOT / "plugins/hig42-design/skills/hig42-design",
    ROOT / "plugins/hig42-design-zh-tw/skills/hig42-design-zh-tw",
]

if subprocess.run([sys.executable, str(ROOT / "tools/check.py")]).returncode != 0:
    sys.exit("checks failed — fix them before packaging")

dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
for skill in SKILLS:
    out = dist / f"{skill.name}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(skill.rglob("*")):
            if f.is_file() and f.name != ".DS_Store":
                z.write(f, f.relative_to(skill.parent))
    print(f"built {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")
