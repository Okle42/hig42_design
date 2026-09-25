# Apple 風格網頁（App 風與行銷風）

> apple.com 數值是 2026-09-24 用 puppeteer `getComputedStyle` 量測、下載 9 支 CSS 分析得來。來源清單見 repo 的 `SOURCES.md`
> 可直接用的 CSS：`assets/apple-web-base.css`

## 目錄
1. 先分清楚：App 風 vs 行銷風
2. 授權：可以／不可以
3. 字型
4. App 風元件
5. 行銷風（apple.com）數值
6. 毛玻璃
7. 深色模式與偏好查詢
8. 動畫
9. 中文排版
10. 「AI 感」反模式 → Apple 做法
11. 坑

---

## 1. App 風 vs 行銷風

| | App 風（工具頁、儀表板、設定頁） | 行銷風（產品頁、landing） |
|---|---|---|
| 依據 | HIG | apple.com |
| 字級 | macOS 13px 或 iOS 17px 內文，層級靠字重與灰階 | 17px 內文、48–80px 標題 |
| 版面 | grouped list、sidebar、細分隔線、靠左 | 大留白（區塊上下 160px）、全出血色塊、hero 可置中 |
| 藍色 | 系統藍 `#0088FF`／深 `#0091FF`（小字連結用 `#0066CC` 或 macOS `#0068DA`） | 按鈕 `#0071E3`、連結 `#0066CC`、深色區連結 `#2997FF` |
| 深色模式 | **跟系統**（`prefers-color-scheme`），可加 `data-theme` 覆寫 | apple.com 不跟系統，由設計決定哪些區塊是深色 |

兩套不要混。使用者說「做個 Apple 風的工具頁」就是 App 風。

## 2. 授權【官方】

| 項目 | ✅ 可以 | ❌ 不可以 |
|---|---|---|
| SF 字型 | CSS 用 `-apple-system`、`BlinkMacSystemFont`、`system-ui`、`ui-*` 或 `"SF Pro Text"` **叫用使用者電腦已有的系統字** | `@font-face` 把 SF 字型檔放上網頁或 Electron；盜連 `apple.com/wss/fonts`；用 SF 做非 Apple 平台設計 |
| SF Symbols | 只在原生 Apple 平台 app 裡用 | 匯出 SVG 放網頁、web app、簡報；用在 app icon、logo（相似到會混淆的也不行） |
| Apple Design Resources（Figma kit） | 做 Apple 平台 app 的 mockup | 抽圖形當網頁素材 |
| Apple 商標 |「適用於 iPhone」這類相容性描述 | 用  logo（包含 U+F8FF 字元）、Apple 產品照、做成讓人誤認為官方的頁面 |
| 設計語彙 | 膠囊按鈕、grouped list、毛玻璃導覽列、色值、間距（一般設計元素） | 逐字複製 apple.com 的 CSS 檔、HTML、圖片 |

依據：SF 字型授權「solely for creating mock-ups… may not embed」；Apple Design Resources License 2B 禁止用於「website content」；Xcode and Apple SDKs Agreement §2.10 限制 SF Symbols 只用於開發 Apple 平台 app。

**圖示替代**：自己畫 SVG，或開源圖示庫（Lucide ISC、Phosphor MIT、Heroicons MIT、Tabler MIT），以 inline SVG 使用並保留授權聲明。風格：單色線條 1.5–2px、圓端點、與文字同色。

## 3. 字型

### 3.1 瀏覽器行為【實測＋官方 BCD】
| 關鍵字 | Safari | Chrome | 說明 |
|---|---|---|---|
| `-apple-system` | ✅ | ❌ 不認得 | |
| `BlinkMacSystemFont` | — | ✅（Mac） | Chrome 靠它叫到 SF |
| `system-ui` | ✅ | ✅ | 通用；但 Windows CJK 環境拉丁字可能很醜，放後面 |
| `ui-rounded`／`ui-serif`／`ui-monospace` | ✅ | ❌ | 一定要配具名字型回退 |

### 3.2 建議堆疊（繁中）
```css
--font-text: -apple-system, BlinkMacSystemFont, "Segoe UI Variable Text", "Segoe UI",
             "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", system-ui,
             "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
--font-rounded: ui-rounded, "SF Pro Rounded", var(--font-text);
```
並設 `<html lang="zh-Hant-TW">`，系統才會回退到 PingFang **TC**（不寫或寫 `zh-CN` 可能拿到簡體字形）。

### 3.3 字距【實測 Chrome】
- 系統字在內文大小**已自帶字距，≤21px 不要加**。
- 英文標題 ≥28px 加 `-0.01em`，≥48px 加 `-0.012em`～`-0.016em`。
- **不要抄 apple.com 標題的正字距**（+0.011em 等），那是他們網頁字型的補償值。
- **中文一律 `letter-spacing: 0`**（apple.com 自己寫了 `body:lang(zh){letter-spacing:0em}`）。

## 4. App 風元件

### 4.1 色彩
用 `assets/apple-web-base.css` 的 token（系統色、語意色、深色、高對比都有）。重點：
- iOS 風背景：grouped `#F2F2F7`＋白色群組；深色 `#000`＋`#1C1C1E`。
- **macOS 風背景**：視窗 `#FFFFFF`／深色 `#1E1E1E`（不是純黑）；label 用黑／白＋alpha（0.847／0.498）。
- 淺色模式下系統彩色當小字對比不夠（藍 3.52:1），小字連結用 `#0066CC`。

### 4.2 Inset grouped list
| 項目 | iOS 13–18 經典 | iOS 26 風 |
|---|---|---|
| 群組圓角 | 10px | 約 24px【第三方 Framework7】 |
| 列最小高 | 44px | 約 52px【第三方】 |
| 左右外距／列內 padding | 16px | 16px |
| 分隔線 | 0.5px，**從文字起點開始**（左側內縮），最後一列不畫 | 同 |
| 區塊標題／註腳 | 13px 次要色；iOS 18 以前全大寫，iOS 26 起改一般大小寫 | 同 |

```css
.row + .row::before {            /* 分隔線只從內容起點開始 */
  content: ""; position: absolute; top: 0; right: 0; left: var(--row-inset, 16px);
  border-top: .5px solid var(--separator);
}
```

### 4.3 Switch
- **Safari 17.4+ 直接用原生 `<input type="checkbox" switch>`**，會畫成系統 switch（其他瀏覽器退回 checkbox）。
- 自畫尺寸：iOS 經典 51×31、旋鈕 27；iOS 26 是 61×28【實測】；macOS `NSSwitch` 54×24。開啟色預設綠色。
- HIG：switch 只用在 list row；macOS grouped form 內用 mini switch。

### 4.4 其他
- Segmented control：iOS 高 31；macOS regular 24。灰軌道（fill 色）、內距 2px、選中段白色膠囊＋極淡陰影。
- macOS 風 sidebar：寬約 220px、列高 28px、圓角 6px 選取底、13px 字、分組標題 11px 600 三級灰。
- 數字用 `font-variant-numeric: tabular-nums`。
- 儀表板不要每個數字一張卡：用一個 grouped 容器裡用分隔線分列。

## 5. 行銷風（apple.com）數值【實測】

### 5.1 字級（桌機 1069–1440px）
| 角色 | size / line-height | weight | 英文字距 |
|---|---|---|---|
| 區塊大標 | 80px / 1.05 | 600 | -0.015em |
| Hero 標題 | 64px / 1.0625 | 600 | -0.009em |
| 次級標題 | 48px / 1.0835 | 600 | -0.003em |
| Eyebrow（產品名） | 28px / 1.1429 | 600 | +0.007em |
| 引言 | 21px / 1.381 | 400（產品頁 600＋灰 `#86868B`） | +0.011em |
| 內文 | 17px / 1.4706 | 400 | -0.022em |
| 小內文 | 14px / 1.4286 | 400 | -0.016em |
| 註腳 | 12px / 1.3333 | 400 | -0.01em |

- 標題幾乎全用 600，不用 700／800；主要按鈕文字 400。
- 中文版 `:lang(zh)`：字距全部歸零、標題行高加大（80px 標題 1.0875、28px eyebrow 1.25）、`quotes: "「" "」"`、不用斜體。

### 5.2 版面
- 內容寬：≥1069px 980px；735–1068px 692px；≤734px 87.5%。
- 產品頁區塊上下留白 160px；首頁全出血產品磚之間 12px 白縫，背景 `#000` 與 `#F5F5F7` 交替。

### 5.3 按鈕
| 種類 | 樣式 |
|---|---|
| 主要 | 背景 `#0071E3`（hover `#0076DF`）、白字、圓角 980px（膠囊）、padding 11px 21px、17px／400 |
| 次要 | 透明、`#0066CC` 字與 1px 邊框 |
| 小型 | padding 8px 15px、14px |

連結 `#0066CC`，不加底線、不加「→」。

### 5.4 色票
| 用途 | 淺 | 深 |
|---|---|---|
| 背景 | `#FFFFFF` | `#000000` |
| 主文字 | `#1D1D1F` | `#F5F5F7` |
| 次要文字 | `#6E6E73` | `#86868B` |
| 三級文字 | `#86868B`（對白只有 3.62:1，只給大字） | `#6E6E73` |
| 灰區塊底 | `#F5F5F7` | `#1D1D1F` |
| 邊框 | `#D2D2D7` | `#424245` |
| 連結 | `#0066CC` | `#2997FF` |

## 6. 毛玻璃

- **只用在浮在內容上的導覽列／工具列**，不要拿來做卡片。
- apple.com 導覽列原值：`backdrop-filter: saturate(180%) blur(20px)`＋底色 `rgba(250,250,252,.8)`（深 `rgba(22,22,23,.8)`）；不支援時退回 `.92`／`.88` 不透明度。
- 前綴：Safari 18+ 無前綴即可；要支援 iOS 17 以下兩個都寫（`-webkit-backdrop-filter`）。用 `@supports` 包，失敗給高不透明底色。
- **不要追 Liquid Glass 折射**：社群的 SVG displacement filter（`backdrop-filter: url(#f)`）**只有 Chromium 會動，Safari 看不到**，而且很吃 GPU。網頁只做標準毛玻璃，最多加 1px 半透明白色內側邊。
- 減少透明度：用 `@media (prefers-contrast: more)` 與 `(prefers-reduced-transparency: reduce)` 兩個都寫，改成不透明底（**Safari 不支援 `prefers-reduced-transparency`**，實測反應跟亂寫的查詢一樣；前者一定要有，後者只對 Chrome 有效）。

## 7. 深色模式與偏好查詢
- `<meta name="color-scheme" content="light dark">`＋`:root { color-scheme: light dark; }`，捲軸和表單控制項一起切換、避免閃白。
- 工具頁跟系統：`@media (prefers-color-scheme: dark)`，並允許 `:root[data-theme="dark"|"light"]` 手動覆寫。
- 一定要寫 `prefers-reduced-motion`；有顏色時寫 `prefers-contrast: more`（直接套高對比色值）。
- `AccentColor` 系統色關鍵字拿不到使用者的 macOS 強調色（Safari、Chrome 都回固定值防指紋），自己定義藍色。
- `-apple-system-blue` 等 CSS 色名只在 Apple 平台 WebKit 有效且非標準，只能當漸進增強，前面一定先寫一般色值。

## 8. 動畫
- 行銷風：apple.com 最常用 `cubic-bezier(.4, 0, .6, 1)`，時長 240–320ms。
- App 風：spring。`linear()` 取樣版（Safari 17.2+）在 `assets/apple-web-base.css` 的 `--ease-spring`；不支援時回退 `cubic-bezier(.25, .1, .3, 1)`。
- 時長：微互動（switch、hover）150–250ms；面板／sheet 350–500ms。
- 不要每個區塊都 fade-and-slide-up 進場、每張卡都有 hover 動畫。
- 必寫 `@media (prefers-reduced-motion: reduce)`，位移改淡入或直接切換。

## 9. 中文排版
| 項目 | 建議 |
|---|---|
| `lang` | `zh-Hant-TW`（`:lang(zh)` 會命中） |
| 字距 | 0；英文負字距只套在 `:not(:lang(zh))` |
| 內文行高 | 行銷頁 1.47；工具頁長文 1.6–1.75 |
| 標題行高 | 比英文高 3–8% |
| 引號 | `quotes: "「" "」" "『" "』"` |
| 斜體 | 中文不用 |
| 中英間距 | `text-autospace: normal`（Safari 18.4+、Chrome 140+；初始值是不加，要自己寫）。註：Apple 原生 UI 字串是中英不加空格；網頁內文要不要自動間距看情境，UI 標籤建議不加 |
| 換行 | `line-break: strict` |
| 標題平衡 | `text-wrap: balance`；內文 `text-wrap: pretty` |
| 字重 | 中文 600 已經很重；標題 600、內文 400，避免 700+（Windows 會假粗體） |

## 10. 「AI 感」反模式 → Apple 做法

| AI 感 | Apple 做法 |
|---|---|
| 紫藍／indigo→violet 漸層背景、漸層文字 | 純色大面（白／`#F5F5F7`／黑），顏色來自內容本身；強調色只有一個藍 |
| 三欄等寬 feature 卡（icon＋標題＋兩行字） | 一個區塊講一件事：大標題＋一張大圖或一個數字；需要並列用不等寬格 |
| emoji 當圖示 | 不用圖示，或單色線條 SVG；**不能用 SF Symbols** |
| Inter＋所有東西同一個大圓角＋每張卡都有陰影 | 系統字；圓角依層級（按鈕膠囊、卡片 18–28px、群組 10–26px、小元件 6–8px）；**幾乎不用陰影**，靠背景色差分層（白卡在 `#F5F5F7` 上） |
| 全大寫、字距拉開的 eyebrow | eyebrow 用產品名本身、一般大小寫、Semibold |
| 每段都置中 | hero 可置中；內文、工具頁、設定頁一律靠左並限寬 |
| 玻璃擬態卡片漂在漸層上 | 毛玻璃只給浮動導覽列，內容區用實色 |
| 到處 700／800 粗體、標題只一個詞換色 | 標題 600、內文 400；次要資訊用灰色，不是更小更粗 |
| 「立即開始 →」按鈕加箭頭 | 膠囊藍按鈕、動詞明確；次要動作用文字連結 |
| `#111` 冒充黑、`#FAFAFA` 冒充白 | 文字黑 `#1D1D1F`、深色區背景 `#000`、白 `#FFF`、灰區 `#F5F5F7` |
| 空泛文案（「釋放你的潛能」） | 短、具體、有節奏，標題常以句號結尾 |
| 中文套英文負字距、行高 1.0 | 中文字距 0、標題行高 ≥1.09、內文 1.5–1.7 |
| 儀表板每個 KPI 一張漸層卡 | 一個 grouped 容器用分隔線分列；數字 tabular-nums |

**跟 frontend-design 指引的衝突**：Anthropic 的設計指引建議避開系統預設字，但 **Apple 風格的本質就是系統字**，這是刻意的品牌選擇。差別在於有沒有做對光學尺寸、字距曲線、600／400 層級、灰階次要文字。

## 11. 坑
1. `@font-face` 內嵌 SF、盜連 apple.com 字型；網頁用 SF Symbols。
2. 只寫 `-apple-system`，Chrome 使用者拿到 Times（要加 `BlinkMacSystemFont`）。
3. 沒設 `lang`，中文拿到簡體字形。
4. 中文套負字距；抄 apple.com 標題的正字距。
5. App 風和行銷風混用（設定頁用 80px 標題、產品頁用 13px grouped list）。
6. 小字用 `#0088FF` 或 `#86868B`（對比不夠）。
7. 毛玻璃做卡片；追 SVG 折射；沒有不透明回退。
8. 工具頁不跟系統深色模式；忘了 `color-scheme`。
9. 沒寫 `prefers-reduced-motion`。
10. Mac 風網頁用 iOS 純黑深色背景。
