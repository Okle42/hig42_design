# Contributing / 貢獻指南

[English](#english) · [繁體中文](#繁體中文)

## English

### Ground rules
1. **Evidence first.** Every rule or number carries a tag: **[Official]** (Apple docs, HIG, WWDC), **[SDK]** (checked against or compiled with the Xcode SDK), **[Measured]** (you measured it — say on which OS), **[Third-party]**, **[Inferred]**. A correction without a source is a guess, not a fix.
2. **Both editions change together.** `plugins/hig42-design` (English) and `plugins/hig42-design-zh-tw` (Traditional Chinese) must have the same files, the same sections and the same code. If you can only write one language, open the PR anyway and say so — a maintainer will translate before merging.
3. **Code must compile.** Every Swift sample is type-checked:
   ```
   xcrun --sdk macosx swiftc -parse-as-library -typecheck -target arm64-apple-macos26.0 sample.swift
   ```
   Use `--sdk iphoneos -target arm64-apple-ios26.0` for iOS-only code. Add stubs in a scratch file, not in the docs.
4. **No Apple text copied.** Paraphrase and link. Short API names and UI strings are fine; paragraphs from the HIG or sample code from WWDC are not.
5. **Keep SKILL.md short.** Details belong in `references/`. SKILL.md routes the agent to the right file.

### Before you open a pull request
```
python3 tools/check.py      # manifests, frontmatter, edition parity, links, leaked local paths
python3 tools/package.py    # builds dist/*.skill (optional locally; CI does it too)
```
Add a line to `CHANGELOG.md`.

### Repository layout
```
.claude-plugin/marketplace.json     marketplace "okle42" listing both plugins
plugins/
  hig42-design/                     English edition
    .claude-plugin/plugin.json
    skills/hig42-design/
      SKILL.md                      entry point: routing, principles, checklist
      references/*.md               topic files the agent reads on demand
      assets/apple-web-base.css     drop-in CSS tokens
  hig42-design-zh-tw/               Traditional Chinese edition (same structure)
evals/                              A/B test prompts, input and grading script
tools/check.py · tools/package.py   repository checks and .skill packaging
SOURCES.md                          public sources behind the evidence tags
```

### After each WWDC
Check `https://developer.apple.com/design/whats-new/`, re-verify the system color table, control sizes and any renamed APIs against the new SDK, then bump the version in both `plugin.json` files.

---

## 繁體中文

### 基本規則
1. **先有證據。** 每條規則或數字都要標：**【官方】**（Apple 文件、HIG、WWDC）、**【SDK】**（對照或用 Xcode SDK 編譯過）、**【實測】**（你量的，註明系統版本）、**【第三方】**、**【推論】**。沒有來源的更正只是猜測。
2. **兩個版本一起改。** `plugins/hig42-design`（英文）和 `plugins/hig42-design-zh-tw`（繁中）的檔案、章節、程式碼必須一致。只會寫一種語言也可以發 PR，註明即可，合併前由維護者補翻譯。
3. **程式碼要能編譯。** 每段 Swift 範例都要 typecheck（指令見上方英文段）；需要的 stub 放在另外的測試檔，不要寫進文件。
4. **不抄 Apple 原文。** 用自己的話寫並附連結。API 名稱、介面字串可以；HIG 整段文字、WWDC 範例程式不行。
5. **SKILL.md 保持精簡。** 細節放 `references/`，SKILL.md 只負責把 agent 導到對的檔案。

### 發 PR 之前
```
python3 tools/check.py      # 檢查設定檔、frontmatter、中英版一致、連結、本機路徑外洩
python3 tools/package.py    # 打包 dist/*.skill（本機可略，CI 會做）
```
並在 `CHANGELOG.md` 加一行。

### 每年 WWDC 之後
查 `https://developer.apple.com/design/whats-new/`，用新 SDK 重新核對系統色表、控制項尺寸與改名的 API，然後把兩個 `plugin.json` 的版本號往上加。
