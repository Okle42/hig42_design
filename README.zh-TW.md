# hig42-design

**讓 AI 寫 Apple 平台介面時，照最新、查證過的設計規範來做。**
由 [Okle42](https://github.com/Okle42) 製作，追蹤我們可以拿到更多實際能用的 AI 工具。
這是一個 [Claude Code](https://claude.com/claude-code) skill，涵蓋 iOS/iPadOS 26–27、macOS 26–27（Liquid Glass）的 SwiftUI／AppKit／UIKit 介面，以及 Apple 風格網頁。每個數字都標明出處。

[English](README.md)

---

## 為什麼需要

iOS 26 和 macOS 26 把整套設計系統換掉了：系統色全換、加入 Liquid Glass、控制項變高、圓角改成同心。AI 模型大多是用舊資料訓練的，所以還在寫 `#007AFF`、把按鈕高度寫死成 22pt、在列表上套玻璃，甚至照抄已經編不過的 WWDC 範例。

這個 skill 讓 AI 改用現在正確、查證過的答案：

| AI 常犯的錯 | 這個 skill 的答案 |
|---|---|
| 系統藍是 `#007AFF` | iOS 26／macOS 26 起是 `#0088FF`（深色 `#0091FF`）；而且預設系統彩色大多不夠當白底小字（對比不到 4.5:1） |
| 照抄 WWDC25 範例 `.rect(corner: .containerConcentric)` | 正式 SDK 沒有這個名稱，要寫 `.rect(corners: .concentric)` |
| 用 `UIDesignRequiresCompatibility` 退回舊外觀 | 用 Xcode 27 建置時會被系統忽略 |
| 卡片、列表都套玻璃 | 玻璃只用在功能層（toolbar、sidebar），不要玻璃疊玻璃 |
| macOS 內文用 17pt | macOS 內文是 13pt，Headline 是 Bold 13 |
| 8pt 網格是 Apple 規定 | 不是，只是業界慣例 |
| 設定視窗放「好／套用」 | 改了就生效；設定入口在 App 選單的「設定⋯」＋ ⌘, |

**繁中使用者的額外賣點**：Apple 官方繁中介面用語，是統計 macOS 繁中介面實際用字整理出來的，例如 OK＝好、Copy＝拷貝、Undo＝還原、Quit＝結束、省略號用「⋯」、中英之間不加空格。

## 內容

| 檔案 | 內容 |
|---|---|
| `SKILL.md` | 依情境分流、十條核心原則、最常用數值、最常見的錯、交付前審查清單 |
| `references/typography-layout.md` | iOS／macOS 字級表、邊距、點擊範圍、macOS 控制項實測高度、同心圓角、中文字型 fallback |
| `references/color-materials.md` | 2025 起的系統色表（含高對比）、語意色、材質、深色模式、對比計算 |
| `references/liquid-glass.md` | SwiftUI／AppKit／UIKit 玻璃 API、27 的變化、遷移、舊系統 fallback、整窗玻璃面板 |
| `references/macos-components.md` | 視窗、選單列、選單列圖示 app、浮動面板、alert、設定視窗、控制項、動畫、SF Symbols |
| `references/charts-live-data.md` | Swift Charts、即時數字、Gauge、狀態色、widget |
| `references/notifications-background.md` | 通知、權限請求、登入時打開、`LSUIElement`、選單列圖示與 app icon 製作 |
| `references/accessibility.md` | VoiceOver label、鍵盤操作、macOS 文字大小、稽核、App Store 無障礙標籤 |
| `references/web.md` | App 風與行銷風網頁、授權可以與不可以、「AI 感」反模式 → Apple 做法 |
| `references/zh-tw-writing.md` | Apple 官方繁中用語對照、中文標點與排版、英文大小寫規則 |
| `assets/apple-web-base.css` | 可直接貼用的 CSS：系統色、淺色／深色／高對比、grouped list、switch、segmented control |

## 怎麼查證的

- **Apple 文件與 HIG**：抓 DocC JSON 原始資料，2026 年 9 月版本。
- **API 名稱與最低版本**：對照 Xcode 27.0 SDK；**所有 Swift 範例都實際編譯過**（macOS 26／iOS 26 target）。
- **實測**：在 macOS 27.0 與 iOS 26.5 模擬器上量控制項高度、語意色、字型 fallback、對比。
- **兩輪獨立交叉核對**：第一輪抽查 68 條（錯 10 條，已修），第二輪抽查 27 條（錯 8 條，已修）。
- 每條規則都標證據等級：【官方】【SDK】【實測】【第三方】【推論】。145 個來源連結在 [`SOURCES.md`](SOURCES.md)。

## 有沒有用？（小型 A/B 測試）

同樣三題，有 skill 和沒 skill 各做一次，每題用 12–13 項客觀檢查評分：

| 任務 | 有 skill | 沒 skill |
|---|---|---|
| macOS 選單列溫度監控（SwiftUI） | 12/12 | 10/12 |
| Apple 風服務儀表板（HTML） | 12/12 | 9/12 |
| 審查一段有問題的 SwiftUI 設定畫面 | 13/13 | 13/13 |

老實說：只有三題、每題只跑一次、評分項目是作者自己訂的（題目與評分腳本在 [`evals/`](evals/)）。差別主要在細節，例如高對比模式、選單列圖示可以移除、中文不套負字距、不寫死舊的 `#007AFF`。代價是 token 和時間大約多一倍。

| 有 skill | 沒 skill |
|---|---|
| ![有 skill](docs/img/dashboard-with-skill.png) | ![沒 skill](docs/img/dashboard-without-skill.png) |

## 安裝

**Claude Code（plugin）**

```
/plugin marketplace add Okle42/hig42_design
/plugin install hig42-design-zh-tw@okle42    # 繁體中文
/plugin install hig42-design@okle42          # English
```

**Claude Code（手動）**：把 `plugins/hig42-design-zh-tw/skills/hig42-design-zh-tw` 複製到 `~/.claude/skills/hig42-design-zh-tw`。

**Claude.ai**：到 [Releases](https://github.com/Okle42/hig42_design/releases) 下載 `.skill` 檔，在 Claude.ai 的 Skills 設定上傳。

中英版擇一安裝就好，兩版內容相同，同時裝會搶同一類請求。

裝好之後，只要請 Claude 做 Apple 平台介面、Apple 風網頁，或請它依 HIG 審查介面，它就會自動套用。

## 專案結構

```
.claude-plugin/marketplace.json   「okle42」plugin marketplace（中英兩版）
plugins/hig42-design/             英文版：skills/hig42-design/{SKILL.md, references/, assets/}
plugins/hig42-design-zh-tw/       繁中版（結構相同）
evals/                            A/B 測試題目、輸入檔與評分腳本
tools/                            check.py（專案檢查）· package.py（打包 .skill）
SOURCES.md · CHANGELOG.md · CONTRIBUTING.md
```

發現數值有錯或 API 過時？請開 [內容更正](https://github.com/Okle42/hig42_design/issues/new/choose) 並附來源，規則見 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 限制

- macOS 最完整，iOS 夠用，iPadOS／visionOS／watchOS／tvOS 內容較少。
- iOS 實測值來自 iOS 26.5 模擬器（當時沒有 iOS 27 模擬器）。
- 「整窗玻璃浮動面板」那一節只有單一案例實測（[cool42](https://github.com/Okle42/cool42)），而且是刻意偏離 HIG 的做法。
- 資料截至 2026 年 9 月，下一次 WWDC 之後需要更新。

## 關於 Okle42

[Okle42](https://github.com/Okle42) 專做能在真實工作裡站得住的 AI 流程：有研究、有驗證、有數據，不只是生成。
這個 skill 就是一個例子：多個研究 agent 平行讀了約 400 個來源，再由另一個 agent 獨立核對兩輪，每段程式碼都實際編譯過，整條流程的牆鐘時間大約一小時。

⭐ 幫這個 repo 按星、追蹤 [@Okle42](https://github.com/Okle42)，下一個工具出來時就會看到。問題或需求請開 [Issue](https://github.com/Okle42/hig42_design/issues)。

## 聲明

本專案與 Apple Inc. 無關，未經 Apple 授權、贊助或背書。Apple、macOS、iOS、iPadOS、SF Symbols、Liquid Glass 等為 Apple Inc. 的商標。內容是作者依公開文件與實測整理的實作指引，不是 Apple 官方文件，也沒有轉載官方文件。

## 授權

[MIT](LICENSE) © 2026 Okle42
