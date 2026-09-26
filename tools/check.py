#!/usr/bin/env python3
"""Repository checks for hig42-design. Standard library only, so it runs anywhere (including CI).

  python3 tools/check.py

Checks:
  1. marketplace.json and every plugin.json parse, and every marketplace source path exists
  2. SKILL.md frontmatter: kebab-case name ≤ 64 chars, description ≤ 1024 chars, no angle brackets
  3. The English and Traditional Chinese editions have the same files
  4. Each reference file has the same number of code blocks (per language) in both editions
  5. Every relative link in README / SKILL.md / references points to a file that exists
  6. No local machine paths leaked into published files
Exit code 0 = all good, 1 = something to fix.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "plugins/hig42-design/skills/hig42-design"
ZH = ROOT / "plugins/hig42-design-zh-tw/skills/hig42-design-zh-tw"
PUBLISHED = [ROOT / "README.md", ROOT / "README.zh-TW.md", ROOT / "SOURCES.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md"]
LEAK_PATTERNS = [r"/Users/[A-Za-z]", r"~/\.claude/skills/apple-design", r"scratchpad/"]

errors: list[str] = []
def fail(msg: str) -> None:
    errors.append(msg)

# 1. manifests
try:
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    for p in market.get("plugins", []):
        src = ROOT / p["source"]
        if not src.is_dir():
            fail(f"marketplace: source not found for {p['name']}: {p['source']}")
            continue
        manifest = json.loads((src / ".claude-plugin/plugin.json").read_text())
        if manifest.get("name") != p["name"]:
            fail(f"plugin.json name {manifest.get('name')!r} != marketplace name {p['name']!r}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
            fail(f"{p['name']}: plugin.json needs a semver version")
except (OSError, json.JSONDecodeError, KeyError) as e:
    fail(f"manifest error: {e}")

# 2. frontmatter
for edition in (EN, ZH):
    text = (edition / "SKILL.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{edition.name}: SKILL.md has no frontmatter")
        continue
    fm = dict(re.findall(r"^([a-z-]+):\s*(.*)$", m.group(1), re.M))
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != edition.name:
        fail(f"{edition.name}: frontmatter name {name!r} must match the folder name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        fail(f"{edition.name}: name must be kebab-case and ≤ 64 characters")
    if not desc or len(desc) > 1024 or "<" in desc or ">" in desc:
        fail(f"{edition.name}: description must be 1–1024 characters with no angle brackets (now {len(desc)})")
    extra = set(fm) - {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
    if extra:
        fail(f"{edition.name}: unsupported frontmatter keys {sorted(extra)}")

# 3. same files
def files(base: Path) -> set[str]:
    return {str(p.relative_to(base)) for p in base.rglob("*") if p.is_file() and p.name != ".DS_Store"}
en_files, zh_files = files(EN), files(ZH)
for f in sorted(en_files - zh_files):
    fail(f"only in English edition: {f}")
for f in sorted(zh_files - en_files):
    fail(f"only in Traditional Chinese edition: {f}")

# 4. same code blocks
def blocks(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for lang in re.findall(r"^```(\w+)", path.read_text(), re.M):
        counts[lang] = counts.get(lang, 0) + 1
    return counts
for f in sorted(en_files & zh_files):
    if f.endswith(".md"):
        a, b = blocks(EN / f), blocks(ZH / f)
        if a != b:
            fail(f"code blocks differ in {f}: en {a} vs zh-TW {b}")

# 5. relative links
link_re = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
docs = PUBLISHED + [EN / "SKILL.md", ZH / "SKILL.md"] + sorted(EN.rglob("*.md")) + sorted(ZH.rglob("*.md"))
for doc in dict.fromkeys(docs):
    if not doc.exists():
        continue
    for target in link_re.findall(doc.read_text()):
        if re.match(r"[a-z]+:", target):
            continue
        if not (doc.parent / target).exists():
            fail(f"broken link in {doc.relative_to(ROOT)}: {target}")

# 6. leaks
scan = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "dist" not in p.parts
        and p.suffix in {".md", ".json", ".css", ".py", ".yml", ".swift"} and p.name != "check.py"]
for p in scan:
    text = p.read_text(errors="ignore")
    for pat in LEAK_PATTERNS:
        if re.search(pat, text):
            fail(f"local path leaked in {p.relative_to(ROOT)} (pattern {pat})")

if errors:
    print(f"✗ {len(errors)} problem(s):")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"✓ all checks passed ({len(en_files)} files per edition)")
