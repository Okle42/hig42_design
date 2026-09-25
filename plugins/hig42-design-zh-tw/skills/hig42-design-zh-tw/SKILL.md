---
name: hig42-design-zh-tw
description: Apple Human Interface Guidelines（HIG）實作規範，涵蓋 iOS/iPadOS 26–27、macOS Tahoe 26／macOS 27 的 Liquid Glass 新設計。凡是做或改 SwiftUI／AppKit／UIKit 介面（menu bar app、MenuBarExtra、NSPanel 浮動面板、Settings 設定視窗、NavigationSplitView、toolbar、alert、iOS 畫面），或要做「像 Apple」「macOS 風」「iOS 風」「Apple 官網風」的網頁／HTML／儀表板，都要先用這個 skill。也用於：審查介面是否符合 HIG、挑系統色／字級／間距／圓角／控制項尺寸、Liquid Glass API（glassEffect、GlassEffectContainer、NSGlassEffectView）用法與坑、深色模式與對比、繁體中文介面用語（好／取消／拷貝／還原／⋯）。使用者沒提到 HIG 也一樣，只要是 Apple 平台 UI 或 Apple 風視覺就用。
---

# hig42-design（繁體中文版）

讓 Claude 做出「Apple 工程師看了不會皺眉」的介面。內容來自 2026-09 的官方 HIG、macOS 27／Xcode 27 SDK 實證、iOS 26.5 模擬器實測，另經獨立交叉核對（68 條抽查、錯誤已修正），每個數字都有證據等級（見文末）。

## 第一步：判斷情境，只讀需要的參考檔

| 情境 | 例子 | 必讀 |
|---|---|---|
| **A. 原生 macOS** | menu bar 工具、浮動監控面板、設定視窗、主視窗 | `references/macos-components.md`、`references/liquid-glass.md`、`references/typography-layout.md` |
| **B. 原生 iOS／iPadOS** | iPhone app 畫面、tab bar、sheet | `references/liquid-glass.md`、`references/typography-layout.md`、`references/macos-components.md` 的 iOS 段 |
| **C. App 風網頁** | 本地 HTML 工具頁、儀表板、設定頁、表單 | `references/web.md`、`assets/apple-web-base.css` |
| **D. 行銷風網頁** | 產品介紹頁、landing page | `references/web.md` 的 apple.com 段、`assets/apple-web-base.css` |
| 任何情境要挑顏色 | 色碼、深色模式、對比、材質 | `references/color-materials.md` |
| 任何情境有中文介面字 | 按鈕、選單、alert、空狀態 | `references/zh-tw-writing.md` |
| 顯示即時數據／圖表 | 溫度走勢、sparkline、Gauge、狀態徽章、widget | `references/charts-live-data.md` |
| 背景常駐工具 | 通知、權限請求、登入時打開、LSUIElement、選單列圖示與 app icon 製作 | `references/notifications-background.md` |
| 無障礙實作 | VoiceOver label、鍵盤操作、macOS 文字大小、稽核 | `references/accessibility.md` |

**C 和 D 不要混**：apple.com 是大字、大留白、全出血色塊；工具頁要照 HIG 的 grouped list、小字級（macOS 13、iOS 17）。

開工前先確認 **deployment target**。Liquid Glass API 全部是 iOS 26／macOS 26 起；要支援舊系統就用 `#available` 分支（fallback 寫法在 `references/liquid-glass.md`）。用 Xcode 27 建置時，`UIDesignRequiresCompatibility` 會被系統忽略，**沒有退回舊外觀的選項**。

## 十條核心原則（附原因）

1. **標準元件優先，自訂最後。** 標準元件自動拿到 Liquid Glass、深色模式、無障礙退化、鍵盤導覽、在地化。自己畫的每一樣都要自己處理這些，而且系統明年一改你就落後。
2. **不寫死色碼，用語意色／系統色 API。** iOS 26 把幾乎所有系統色都換了（藍 `#007AFF`→`#0088FF`），寫死的 app 一夜變舊。網頁沒有 API 才用 token，並註明是哪一版的值。
3. **不寫死字級與控制項高度。** 用 text style（`.body`、`.headline`）讓 Dynamic Type 生效；macOS 26 起控制項變高（regular 按鈕 24pt、large 以上變膠囊），寫死高度會被裁切。
4. **Liquid Glass 只用在功能層**（toolbar、tab bar、sidebar、浮動控制項），不用在內容層（卡片、列表 cell）。內容層要分層用標準 material 或實色。不要玻璃疊玻璃。
5. **先刪再加。** 採用新設計時，最常見的錯是留著舊的自訂 bar 背景、sidebar 的 `NSVisualEffectView`、`toolbarBackground`，這些會蓋掉玻璃和 scroll edge effect。
6. **顏色克制。** 強調色只給主要動作（每畫面 1–2 個 prominent 按鈕）；在玻璃上上色要上在背景、不上在文字；不要一排按鈕都上色。
7. **對比要過 4.5:1。** iOS 26 的預設系統彩色在淺色模式大多不夠當小字（藍 3.52:1、綠 2.22:1）。小字用 label 色或較深的色；自訂色要給 Light／Dark／高對比共四個變體。
8. **macOS 不是大一號的 iOS。** macOS 內文 13pt（iOS 17pt）、Headline 是 Bold 13；每個 toolbar 按鈕都要有選單列對應指令；設定在 App 選單「設定⋯」＋ ⌘,，不放 toolbar 齒輪。
9. **動畫要有目的、可中斷、尊重 Reduce Motion。** 工具型 app 預設用 `.smooth`（無彈跳）或 `.snappy`，不要用 `.bouncy` 當全域預設；頻繁互動不加動畫。
10. **繁中照 Apple 自己的譯法。** OK＝好、Copy＝拷貝、Undo＝還原、Quit＝結束、省略號用「⋯」(U+22EF)、中英之間不加空格、引號用「」。這些是統計 macOS 27 繁中介面實際用字得來的，不是個人偏好。

## 工作流程

1. **判斷情境**（上表）並讀對應參考檔。
2. **確認版本**：deployment target、要不要支援 macOS 15／iOS 18 以前。
3. **列出畫面上每個元素對應的標準元件**，找不到標準元件的才自訂，自訂的要明確寫出如何處理深色、高對比、Reduce Motion、鍵盤。
4. **套 token**：字級、間距、圓角、色彩都從參考檔拿，不要憑印象。
5. **實作後截圖自檢**：至少淺色＋深色各一張；有自訂玻璃或材質時，再加「增加對比」「減少透明度」。macOS 用 `screencapture -x`；網頁用 puppeteer。截不到就明說沒看到畫面。
6. **跑下方審查清單**，逐條回報。

## 最常用數值（詳表在參考檔）

| 項目 | macOS | iOS | 證據 |
|---|---|---|---|
| 內文字級 | 13pt（Headline 13 Bold） | 17pt（Headline 17 Semibold） | 官方＋實測 |
| 最小字級 | 10pt | 11pt | 官方 |
| 可點範圍 預設／最小 | 28／20pt | 44／28pt | 官方 |
| 控制項高 regular／large／extraLarge | 24／28／36pt（實測，Apple 未公布） | 系統元件自動補到 44 | 實測 |
| 版面邊距 | 視窗內容自訂 | 小 iPhone 16pt、大 iPhone 與 iPad 20pt | 實測 |
| 巢狀圓角 | 內圓角 ＝ 外圓角 − 內距 | 同左 | 官方 |
| 系統藍 | `#0088FF`／深 `#0091FF`（26 起兩平台統一） | 同左 | 官方＋實測 |

- **8pt 網格不是 Apple 規定**，是業界慣例，可以用但不要說成官方。
- `RoundedRectangle` 一律明寫 `style: .continuous`。
- 新的同心圓角 API 是 `.rect(corners: .concentric)`／`ConcentricRectangle`；WWDC25 範例裡的 `.rect(corner: .containerConcentric)` 在正式 SDK 不存在，編不過。

## 最常見的錯（先檢查這些）

1. 寫死 `#007AFF`、`.font(.system(size: 17))`、控制項高度 22pt。
2. 在列表 cell、卡片上用 `.glassEffect()`；在 glass toolbar 裡的按鈕再套玻璃。
3. `.glassEffect()` 寫在 `.padding()` 前面（玻璃只包到文字）。
4. 多塊自訂玻璃沒包 `GlassEffectContainer`（外觀不一致、morph 失效）。
5. Menu bar extra 用彩色 PNG（要用 SF Symbol 或 template image）、主要功能只放在 menu bar extra、沒提供「在選單列中顯示」開關。
6. 設定視窗放「套用／好／取消」按鈕、可放大縮小、標題不跟分頁變。
7. Alert 按鈕用「是／否」、Cancel 設成 default、刻意的刪除動作也標紅。
8. 選單每一項都塞 SF Symbol（macOS 27 起預設隱藏選單圖示，HIG 要求節制、同組全有或全無）。
9. 中文手動指定 `PingFangTC-Regular`（行高變 23.8、中英基線錯位）；用系統字讓它自動 fallback。
10. 網頁內嵌 SF 字型或 SF Symbols（授權禁止）、中文套英文負字距、玻璃擬態卡片漂在紫色漸層上。

## 審查清單（交付前逐條回報 ✅／❌）

- [ ] 所有顏色來自語意色 API 或註明版本的 token；深色模式正確；高對比有變體
- [ ] 所有文字用 text style；Dynamic Type（iOS）放大到 AX 級不截斷關鍵內容
- [ ] 可點範圍達標（iOS 44、macOS 28、visionOS 60）
- [ ] 玻璃只在功能層；沒有玻璃疊玻璃；自訂玻璃在 container 裡
- [ ] 沒有殘留的自訂 bar／sidebar 背景
- [ ] 每畫面 prominent 按鈕 ≤2；破壞性動作不是 default
- [ ] macOS：toolbar 項目都有選單列指令；設定在 ⌘,；鍵盤可完整操作
- [ ] 動畫尊重 Reduce Motion；沒有 `.bouncy` 全域預設
- [ ] 圖示按鈕與選單列圖示都有 accessibility label（`.help()` 不會變成 label；MenuBarExtra 圖示也建議明確加 label）
- [ ] 繁中用語、省略號、標點照 `references/zh-tw-writing.md`
- [ ] 狀態不只靠顏色（顏色＋SF Symbol 形狀＋文字）；即時數字用 `monospacedDigit()`
- [ ] 通知與權限在第一次需要時才請求；「在登入時打開」預設關
- [ ] 網頁：系統字堆疊、`lang="zh-Hant-TW"`、`color-scheme`、`prefers-reduced-motion`、無 SF 字型／Symbols 內嵌

## 與其他指引衝突時

- **frontend-design skill 說「避開系統預設字」**：Apple 風格的本質就是系統字，這是刻意的品牌選擇。做 Apple 風時以本 skill 為準；品質差別在光學尺寸、字距、600/400 層級、灰階次要文字有沒有做對。
- **使用者的產品刻意偏離 HIG**（例如永遠置頂的監控面板，HIG 要求 app 不在前景時隱藏 panel）：可以做，但要補上可關閉、可選要不要置頂、不搶焦點、盡量小，並在交付說明裡寫明是刻意偏離。
- **整窗玻璃的浮動面板**（選單列 app 面板、HUD）：官方的 regular 會跟著背景變灰，實測改 `.clear`＋tint 才可讀，屬刻意偏離，見 `references/liquid-glass.md` §3.1a。
- **HIG 自己矛盾**（例如 buttons 頁說按鈕 title case、alerts 頁說 sentence case）：參考檔已標出，採用系統實際行為。

## 證據等級與原始資料

參考檔裡的標記：**【官方】** HIG／Apple 文件／WWDC 逐字稿；**【SDK】** Xcode 27 SDK 查到或編譯過；**【實測】** 作者在 macOS 27／iOS 26.5 模擬器量到；**【第三方】** 社群來源；**【推論】** 由上述推得。標【第三方】【推論】的數字，用在關鍵地方前要再查。

每個主題的來源 URL 與查證方法在 repo 的 `SOURCES.md`。本 skill 沒寫到的細節，或懷疑某個 API 已經改名，直接 grep 你本機的 SDK：

```bash
SDK=$(xcrun --sdk macosx --show-sdk-path)
F=$SDK/System/Library/Frameworks
# 很多外觀 API（glassEffect、Glass、動畫）在 SwiftUICore，不在 SwiftUI；兩個都要搜
grep -n "func glassEffect" $F/SwiftUI.framework/Versions/A/Modules/SwiftUI.swiftmodule/arm64e-apple-macos.swiftinterface \
  $F/SwiftUICore.framework/Versions/A/Modules/SwiftUICore.swiftmodule/arm64e-apple-macos.swiftinterface
# AppKit 看標頭：$F/AppKit.framework/Headers/NSGlassEffectView.h
# 27 的新 API 用 @available(anyAppleOS 27.0, *) 標示，只搜 "macOS 27" 會漏
```

Apple 文件網站是 JS 渲染，WebFetch 抓不到內容時改抓 DocC JSON：`https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<頁名>.json`、`https://developer.apple.com/tutorials/data/documentation/<framework>/<symbol>.json`。HIG 總更新紀錄在 `https://developer.apple.com/design/whats-new/`。

---

資料截至 2026-09（iOS／iPadOS 27、macOS 27、Xcode 27）。本專案與 Apple Inc. 無關，未經 Apple 授權或背書。Apple、macOS、iOS、SF Symbols、Liquid Glass 等為 Apple Inc. 的商標。內容是作者依公開文件與實測整理的實作指引，不是 Apple 官方文件。

由 [Okle42](https://github.com/Okle42) 維護 · https://github.com/Okle42/hig42_design
