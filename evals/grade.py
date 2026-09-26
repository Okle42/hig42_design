#!/usr/bin/env python3
"""Grading script for the hig42-design A/B test.

Put each run's output in evals/<iteration>/<eval-name>/<with_skill|without_skill>/outputs/, then:
  python3 evals/grade.py iteration-1
It runs the objective checks for each eval (some type-check Swift with xcrun, so run it on a Mac with Xcode)
and writes grading.json next to each outputs/ folder. Check descriptions are in Traditional Chinese.
"""
import json, re, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
it = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "iteration-1")

def read_all(d, pattern):
    txt = "\n".join(p.read_text(errors="ignore") for p in sorted(d.glob(pattern)))
    if pattern.endswith(".swift"):   # 去掉 // 註解，避免「不加 .bouncy」這種註解被誤判
        txt = re.sub(r"(?m)//.*$", "", txt)
    return txt

def typecheck(files):
    if not files:
        return False, "沒有 .swift 檔"
    r = subprocess.run(["xcrun", "--sdk", "macosx", "swiftc", "-typecheck", "-target", "arm64-apple-macos26.0", *map(str, files)],
                       capture_output=True, text=True)
    errs = [l for l in r.stderr.splitlines() if ": error:" in l]
    return r.returncode == 0, ("0 錯誤" if r.returncode == 0 else f"{len(errs)} 錯誤：" + " | ".join(errs[:3]))

def strings_in_swift(src):
    return re.findall(r'"((?:[^"\\]|\\.)*)"', src)

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")

def menubar(out):
    src = read_all(out, "*.swift")
    ui = " ".join(strings_in_swift(src))
    ok, msg = typecheck(sorted(out.glob("*.swift")))
    return [
        ("可以編譯（macOS 26 typecheck）", ok, msg),
        ("使用 MenuBarExtra", "MenuBarExtra" in src, ""),
        ("選單列圖示用 SF Symbol（systemName / systemImage）", "MenuBarExtra" in src and bool(re.search(r"(systemImage|systemName)\s*:", src)) and not re.search(r"NSImage\(named|Image\(\"[^\"]+\"\)", src), ""),
        ("提供可移除選單列圖示的開關（isInserted）", "isInserted" in src, ""),
        ("有 Settings scene", bool(re.search(r"\bSettings\s*\{", src)), ""),
        ("設定用 .formStyle(.grouped)", ".formStyle(.grouped)" in src, ""),
        ("設定視窗沒有「確定／套用／好」按鈕（即時生效）", not re.search(r'Button\("(確定|套用|好|OK|Apply)"', src), ""),
        ("沒有寫死 RGB／hex 色碼", not re.search(r"Color\(red:|Color\(#|0x[0-9A-Fa-f]{6}|NSColor\(red:", src), ""),
        ("沒有寫死字級 .font(.system(size:", ".system(size:" not in src, f"出現 {src.count('.system(size:')} 次"),
        ("沒有用「偏好設定」（macOS 13 起叫設定）", "偏好設定" not in ui, ""),
        ("UI 字串沒有「...」或「…」（Apple 繁中用 ⋯）", not re.search(r"\.\.\.|…", ui), ""),
        ("沒有用 .bouncy", ".bouncy" not in src, ""),
    ]

def dashboard(out):
    html = read_all(out, "*.html")
    low = html.lower()
    neg_ls = re.findall(r"letter-spacing\s*:\s*-", low)
    return [
        ("html lang 為 zh-Hant-TW 或 zh-TW", bool(re.search(r'<html[^>]*lang="zh-(hant-tw|hant|tw)"', low)), ""),
        ("宣告 color-scheme（meta 或 CSS）", "color-scheme" in low, ""),
        ("字型堆疊同時有 -apple-system 與 BlinkMacSystemFont", "-apple-system" in low and "blinkmacsystemfont" in low, ""),
        ("沒有 @font-face 內嵌字型", "@font-face" not in low, ""),
        ("有 prefers-color-scheme: dark", "prefers-color-scheme" in low, ""),
        ("有 prefers-reduced-motion", "prefers-reduced-motion" in low, ""),
        ("有 prefers-contrast（高對比）", "prefers-contrast" in low, ""),
        ("沒有 emoji 當圖示", not EMOJI.search(html), "".join(sorted(set(EMOJI.findall(html))))[:20]),
        ("沒有漸層背景（linear/radial-gradient）", not re.search(r"(linear|radial|conic)-gradient", low), ""),
        ("數字用 tabular-nums", "tabular-nums" in low, ""),
        ("沒有未限定語言的負字距", len(neg_ls) == 0 or ":lang(zh)" in low, f"負字距 {len(neg_ls)} 處"),
        ("沒寫死舊藍 #007AFF 當強調色", "#007aff" not in low, ""),
    ]

def review(out):
    rv = read_all(out, "review.md")
    src = read_all(out, "*.swift")
    ui = " ".join(strings_in_swift(src))
    ok, msg = typecheck(sorted(out.glob("*.swift")))
    return [
        ("修正版可以編譯", ok, msg),
        ("修正版列表不再用 glassEffect", ".glassEffect(" not in src, ""),
        ("修正版 toolbar 不再放齒輪設定鈕", not re.search(r"ToolbarItem[\s\S]{0,200}gearshape", src), ""),
        ("修正版 prominent 按鈕 ≤1", src.count("glassProminent") + src.count("borderedProminent") <= 1, ""),
        ("修正版 alert 不用「是／否」", not re.search(r'Button\("(是|否)"', src), ""),
        ("修正版沒有 .bouncy", ".bouncy" not in src, ""),
        ("修正版沒有「確定」「偏好設定」", "確定" not in ui and "偏好設定" not in ui, ""),
        ("修正版沒有寫死 RGB 色碼、字級", "Color(red:" not in src and ".system(size:" not in src, ""),
        ("修正版省略號用「⋯」", "⋯" in ui and not re.search(r"\.\.\.|…", ui), ""),
        ("報告指出綠色／藍色小字對比不足", bool(re.search(r"對比", rv)), ""),
        ("報告指出設定應即時生效、不要確定／取消", bool(re.search(r"即時|立即生效|不需要?.{0,6}(確定|套用)", rv)), ""),
        ("報告指出設定入口應在 App 選單 ⌘,", "⌘," in rv or "Command-," in rv or "⌘ ," in rv, ""),
        ("報告指出刻意的刪除動作不該標 destructive 或 alert 用詞問題", bool(re.search(r"destructive|破壞性", rv)), ""),
    ]

CHECKS = {"menubar-monitor": menubar, "web-dashboard": dashboard, "review-bad-code": review}

summary = {}
for ev, fn in CHECKS.items():
    for cfg in ("with_skill", "without_skill"):
        out = it / ev / cfg / "outputs"
        if not out.exists() or not any(out.iterdir()):
            continue
        res = fn(out)
        exp = [{"text": t, "passed": bool(p), "evidence": e} for t, p, e in res]
        passed = sum(x["passed"] for x in exp)
        (it / ev / cfg / "grading.json").write_text(json.dumps({
            "expectations": exp,
            "summary": {"passed": passed, "failed": len(exp) - passed, "total": len(exp), "pass_rate": round(passed / len(exp), 3)}
        }, ensure_ascii=False, indent=2))
        summary[f"{ev}/{cfg}"] = f"{passed}/{len(exp)}"
        print(f"\n== {ev} / {cfg}: {passed}/{len(exp)}")
        for x in exp:
            print(("  ✅ " if x["passed"] else "  ❌ ") + x["text"] + (f"（{x['evidence']}）" if x["evidence"] else ""))
print("\n", json.dumps(summary, ensure_ascii=False))
