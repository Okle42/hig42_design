# 顏色、材質、深色模式、對比

> 研究機：macOS 27.0、iOS 26.5 模擬器、Safari 27（2026-09）。來源清單見 repo 的 `SOURCES.md`

## 目錄
1. 原則
2. 系統色（iOS 26／macOS 26 起，統一表）
3. 語意色（iOS／macOS）
4. SwiftUI 寫法與 accent color
5. 材質
6. 深色模式
7. 對比
8. 坑

---

## 1. 原則【官方】
- **不要寫死系統色色碼**。HIG 明說系統色的實際數值會隨版本變動；iOS 26 就把幾乎全部系統色換了。
- 自訂色要給**四個變體**：Light、Dark、Light 高對比、Dark 高對比（Asset Catalog 勾 High Contrast）。就算 app 只有一種外觀也要給 light＋dark，因為 Liquid Glass 會依底下內容切明暗。
- 不要重新定義語意色的意義（不要把 `separator` 當文字色、`secondaryLabel` 當背景）。
- 不要只靠顏色傳達資訊（紅綠色盲）；加圖示、形狀或文字。顏色的文化意涵不同（台股紅漲綠跌跟美股相反）。
- 不要提供 app 內的深淺色切換（HIG 明言避免），跟系統走。網頁工具頁可允許 `data-theme` 手動覆寫。

## 2. 系統色（iOS 26／iPadOS 26／macOS 26 起兩平台統一；macOS 27 實測沒再改）【官方＋實測】

| 名稱 | Light | Dark | 高對比 Light | 高對比 Dark |
|---|---|---|---|---|
| Red | `#FF383C` | `#FF4245` | `#E9152D` | `#FF6165` |
| Orange | `#FF8D28` | `#FF9230` | `#C55300` | `#FFA056` |
| Yellow | `#FFCC00` | `#FFD600` | `#A16A00` | `#FEDF43` |
| Green | `#34C759` | `#30D158` | `#008932` | `#4AD968` |
| Mint | `#00C8B3` | `#00DAC3` | `#008575` | `#54DFCB` |
| Teal | `#00C3D0` | `#00D2E0` | `#008198` | `#3BDDEC` |
| Cyan | `#00C0E8` | `#3CD3FE` | `#007EAE` | `#6DD9FF` |
| Blue | `#0088FF` | `#0091FF` | `#1E6EF4` | `#5CB8FF` |
| Indigo | `#6155F5` | `#6D7CFF` | `#564ADE` | `#A7AAFF` |
| Purple | `#CB30E0` | `#DB34F2` | `#B02FC2` | `#EA8DFF` |
| Pink | `#FF2D55` | `#FF375F` | `#E7124D` | `#FF8AC4` |
| Brown | `#AC7F5E` | `#B78A66` | `#956D51` | `#DBA679` |
| Gray | `#8E8E93` | iOS `#8E8E93`／macOS `#98989D` | `#6C6C70` | `#AEAEB2` |

iOS gray 2–6（macOS 沒有）：
| | Light | Dark |
|---|---|---|
| systemGray2 | `#AEAEB2` | `#636366` |
| systemGray3 | `#C7C7CC` | `#48484A` |
| systemGray4 | `#D1D1D6` | `#3A3A3C` |
| systemGray5 | `#E5E5EA` | `#2C2C2E` |
| systemGray6 | `#F2F2F7` | `#1C1C1E` |

- 舊版（iOS 15–18／macOS 12–15）的經典值：藍 `#007AFF`／`#0A84FF`、紅 `#FF3B30`、綠 `#34C759`（macOS `#28CD41`）、橘 `#FF9500`。要做「支援 iOS 18 以前」或「經典 Apple 色」時才用，完整表在研究檔。
- **三種藍並存**（macOS 27 實測）：iOS `link` 仍是 `#007AFF`；macOS `controlAccentColor`（多色設定下）是 `#007AFF`；SwiftUI `Color.accentColor`／`Color.blue` 是 `#0088FF`。原因官方沒說明。**原生 app 一律用 API，網頁要選一套並寫明版本。**

## 3. 語意色

### 3.1 iOS（UIColor，iOS 26.5 模擬器實測）
| UIColor | Light | Dark（base） | Dark elevated |
|---|---|---|---|
| `label` | `#000000` | `#FFFFFF` | 同 |
| `secondaryLabel` | `#3C3C43` α0.60 | `#EBEBF5` α0.60 | 同 |
| `tertiaryLabel` | `#3C3C43` α0.30 | `#EBEBF5` α0.30 | 同 |
| `quaternaryLabel` | `#3C3C43` α0.18 | `#EBEBF5` α0.16 | 同 |
| `separator` | `#3C3C43` α0.12 | `#545458` α0.50 | 同 |
| `opaqueSeparator` | `#C6C6C8` | `#38383A` | 同 |
| `link` | `#007AFF` | `#0984FF` | 同 |
| `systemBackground` | `#FFFFFF` | **`#000000`** | `#1C1C1E` |
| `secondarySystemBackground` | `#F2F2F7` | `#1C1C1E` | `#2C2C2E` |
| `tertiarySystemBackground` | `#FFFFFF` | `#2C2C2E` | `#3A3A3C` |
| `systemGroupedBackground` | `#F2F2F7` | `#000000` | `#1C1C1E` |
| `secondarySystemGroupedBackground` | `#FFFFFF` | `#1C1C1E` | `#2C2C2E` |
| `tertiarySystemGroupedBackground` | `#F2F2F7` | `#2C2C2E` | `#3A3A3C` |
| `systemFill` | `#787880` α0.20 | α0.36 | 同 |
| `secondarySystemFill` | `#787880` α0.16 | α0.32 | 同 |
| `tertiarySystemFill` | `#767680` α0.12 | α0.24 | 同 |
| `quaternarySystemFill` | `#747480` α0.08 | `#767680` α0.18 | 同 |

- 高對比時 secondary／tertiary／quaternary label 的 alpha 提高（淺 0.80／0.70／0.55，深 0.70／0.55／0.40），背景層加深；separator、link 不變。
- elevated 背景用在 sheet、popover、多工視窗，系統自動切換；用自訂背景會破壞這個區分。
- 有 grouped table 用 `systemGroupedBackground` 三層，否則用 `systemBackground` 三層。

### 3.2 macOS（NSColor，macOS 27 實測）
| NSColor | Light | Dark |
|---|---|---|
| `labelColor` | `#000000` α0.847 | `#FFFFFF` α0.847 |
| `secondaryLabelColor` | `#000000` α0.498 | `#FFFFFF` α0.549 |
| `tertiaryLabelColor` | `#000000` α0.259 | `#FFFFFF` α0.247 |
| `quaternaryLabelColor` | `#000000` α0.098 | `#FFFFFF` α0.098 |
| `linkColor` | `#0068DA` | `#419CFF` |
| `windowBackgroundColor` | `#FFFFFF` | `#1E1E1E` |
| `controlBackgroundColor` | `#FFFFFF` | `#1E1E1E` |
| `underPageBackgroundColor` | `#F6F6F6` | `#282828` |
| `separatorColor` | `#000000` α0.098 | `#FFFFFF` α0.098 |
| `selectedContentBackgroundColor` | `#0064E1` | `#0059D1` |
| `unemphasizedSelectedContentBackgroundColor` | `#DCDCDC` | `#464646` |
| `selectedTextBackgroundColor` | `#B3D7FF` | `#3F638B` |
| `alternatingContentBackgroundColors` | `#FFFFFF`／`#F4F5F5` | `#1E1E1E`／`#FFFFFF` α0.047 |
| `systemFill`／secondary／tertiary | `#000000` α0.098／0.078／0.047 | `#FFFFFF` 同 alpha |

- **macOS label 是「黑／白＋alpha」，iOS 是「`#3C3C43`／`#EBEBF5`＋alpha」，兩平台不要混用。**
- **macOS 深色視窗背景是 `#1E1E1E`，不是純黑**；做 Mac 風網頁不要套 iOS 的純黑底。
- 選取色、focus ring、`controlAccentColor` 會隨使用者的系統強調色改變，上表是預設（多色）下的值。

## 4. SwiftUI 寫法與 accent color

| 需求 | 寫法 |
|---|---|
| 前景層級 | `.foregroundStyle(.primary / .secondary / .tertiary / .quaternary)`；**在 material 上會保留 vibrancy**，換成具體顏色（`.red`）就沒了 |
| 系統色 | `Color.red` … `Color.brown`、`Color.gray` |
| 平台語意色 | iOS `Color(.secondarySystemBackground)`；macOS `Color(nsColor: .windowBackgroundColor)` |
| App 強調色 | `Color.accentColor`；整棵子樹換色用 `.tint(_:)`（`.accentColor(_:)` modifier 已棄用） |
| 背景層級 | `.background(.background)`、`.background(.background.secondary)` |

Accent color【官方】：
- Asset Catalog 的 `AccentColor` color set；Build Setting「Global Accent Color Name」。記得勾 High Contrast。
- **macOS 只有在使用者的系統強調色設為「多色」時才套用 app 的 accent**，否則系統用使用者選的顏色蓋掉。這是設計，不是 bug。固定色只留給 logo 或有固定語意的 sidebar 圖示。
- `NSColor.controlAccentColor` 是使用者的系統強調色，不是 app 的。
- Liquid Glass 上，系統把 accent color 用在 prominent 按鈕的**背景**。

## 5. 材質

### 5.1 兩種材質【官方 HIG Materials】
- **Liquid Glass**：功能層專用，見 `liquid-glass.md`。
- **標準 material**：內容層內的結構區分。**依語意挑，不要依看起來的顏色挑**（系統設定會改變材質外觀）。材質上的文字一律用 vibrant 顏色（系統 label／fill／separator）。厚材質對比好，薄材質保留背景脈絡。

### 5.2 iOS
- SwiftUI：`.ultraThinMaterial`、`.thinMaterial`、`.regularMaterial`（預設）、`.thickMaterial`、`.ultraThickMaterial`、`.bar`（系統 toolbar 風格）。
- UIKit：`UIBlurEffect.Style.systemUltraThinMaterial … systemChromeMaterial`；舊的 `.light/.dark/.extraLight` 不要新用。
- Vibrancy：**`quaternaryLabel` 不要放在 thin／ultraThin 上**（對比太低）。

### 5.3 macOS `NSVisualEffectView`
| material | 用途 |
|---|---|
| `.sidebar` | 側欄（macOS 26+ 用 split view 的玻璃 sidebar，**不要自己加**） |
| `.titlebar` | 自訂標題列延伸 |
| `.menu`／`.popover` | 自訂選單式浮層／popover 樣式視窗 |
| `.hudWindow` | 深色 HUD 面板（影音、檢查器） |
| `.headerView` | 表格 sticky header |
| `.sheet`／`.windowBackground`／`.contentBackground` | 對應位置 |
| `.underWindowBackground` | 透出桌面的整窗背景 |
| `.selection` | 自訂選取高亮 |
| ~~`.light/.dark/.mediumLight/.ultraDark/.appearanceBased`~~ | **已棄用，不會適應深色模式** |

- `blendingMode`：`.behindWindow`（模糊桌面／其他視窗）vs `.withinWindow`（只模糊同視窗內容，toolbar 用這個）。
- `state`：預設跟隨視窗 active 狀態；**浮動面板設 `.active`** 才會一直是活躍外觀。
- Vibrancy：在**葉節點** view override `allowsVibrancy` 回 true；父層開了子層關不掉，彩色內容會被洗色。
- AppKit 會自動替 titlebar、popover、source list 建 visual effect view，不用自己加。

## 6. 深色模式【官方】
1. 不是反轉：深色值多半更亮更飽和。
2. iOS 有 base（`#000000`）與 elevated（`#1C1C1E` 起）兩套背景；macOS 視窗 `#1E1E1E`。
3. 純黑只放最底層全螢幕背景；浮層一律用 elevated 灰。
4. 白底插圖在深色會「發光」，要壓暗或另做深色版；用 Asset Catalog 把 light／dark 版合成一個具名圖。
5. 外觀相關的顏色設定放在會被重呼叫的地方（NSView `updateLayer()`／`draw(_:)`；UIView `traitCollectionDidChange` 或 iOS 17+ trait 註冊 API）。`CGColor` 不會自動更新，**不要在 init 設 `layer.backgroundColor = color.cgColor` 就不管**。
6. macOS 可對單一 view／window 指定 `NSAppearance`（例：列印預覽固定 `.aqua`）。
7. 測試：淺色／深色 × 增加對比 × 減少透明度，分開與組合都測；深色＋增加對比有時反而降低對比。`NSAppearance(named: .accessibilityHighContrastAqua)` 在程式裡強制**無效**（實測回傳 `.aqua`），要真的開系統設定或用 Xcode Environment Overrides。

## 7. 對比

### 7.1 要求【官方 HIG Accessibility】
| 文字 | 最低對比 |
|---|---|
| ≤17pt 一般字重 | **4.5:1** |
| ≥18pt，或任何粗體 | **3:1** |

預設配色達不到時，至少在「增加對比」開啟時提供更高對比版本。自訂前景／背景 HIG 建議力求 7:1，尤其小字。

### 7.2 系統色實際對比（WCAG 公式計算）
| 組合 | 對比 | 結論 |
|---|---|---|
| `#0088FF`（iOS 26 藍）字 on 白 | 3.52 | ✗ 小字不行 |
| `#007AFF`（舊藍／iOS link）on 白 | 4.02 | ✗ 小字不行 |
| `#1E6EF4`（高對比藍）on 白 | 4.57 | ✓ |
| macOS `linkColor` `#0068DA` on 白 | 5.26 | ✓ |
| apple.com 連結 `#0066CC` on 白 | 5.57 | ✓ |
| `#34C759` 綠 on 白 | 2.22 | ✗ 不能當文字色 |
| `#FF8D28` 橘 on 白 | 2.31 | ✗ |
| `#FF383C` 紅 on 白 | 3.57 | ✗ 小字不行 |
| 高對比版紅／綠／橘／黃 on 白 | 4.54–4.59 | ✓（Apple 刻意校準到剛好過） |
| iOS `secondaryLabel` 淺色（合成 `#8A8A8E`）on 白 | 3.44 | ✗ 小字不行 |
| macOS `secondaryLabelColor` 淺色 on 白 | 3.95 | ✗ 小字不行 |
| 白字 on `#0088FF` 填色按鈕 | 3.52 | 只有大字／粗體可（系統按鈕是 17pt semibold，所以過） |

**結論**：淺色模式下系統彩色只適合填色、圖示、大字、裝飾；**要閱讀的小字**用 `label`、macOS `linkColor`，或自訂較深的色（例 `#0066CC`）。secondary label 在淺色模式也不到 4.5，不要拿來放關鍵資訊。網頁要準備 `prefers-contrast: more` 版，直接套高對比欄的值。

## 8. 坑
1. 寫死 `#007AFF` 當「Apple 藍」。
2. 系統彩色當小字文字色。
3. 自訂色只給 light／dark，沒給高對比。
4. iOS 與 macOS 語意色混用；Mac 風網頁用純黑底。
5. 玻璃上一排按鈕都上色；把強調色上在符號而不是背景。
6. 內容層用 Liquid Glass。
7. 依看起來的顏色挑材質；用已棄用的 NSVisualEffectView material。
8. 父層開 `allowsVibrancy`；material 上用具體顏色導致 vibrancy 消失。
9. init 時設 `cgColor` 不隨外觀更新。
10. 提供 app 內深淺色切換（原生 app）。
11. 深色模式直接反轉、白底插圖原封不動。
12. 想用自訂 accent 蓋過使用者在 macOS 選的強調色。
