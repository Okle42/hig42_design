# 字型、版面、點擊範圍、圓角

> 查證環境：macOS 27.0、Xcode 27（iOS 27 SDK）、iOS 26.5 模擬器（2026-09；作者環境沒有 iOS 27 模擬器，文中「實測 iOS」皆為 26.5）。來源清單見 repo 的 `SOURCES.md`

## 目錄
1. 文字樣式（iOS／macOS 字級表）
2. 字族、optical size、tracking、字重
3. 繁體中文
4. 版面（邊距、safe area、size class）
5. 點擊範圍與控制項尺寸
6. 圓角（continuous、concentric）
7. 坑

---

## 1. 文字樣式

**原則**：一律用 text style，不寫死 pt。真的要自訂大小，用 `.font(.system(size: 15, relativeTo: .body))`、`@ScaledMetric` 或 `UIFontMetrics`，才會跟著 Dynamic Type 縮放。

### 1.1 預設與最小字級【官方】
| 平台 | 預設 | 最小 |
|---|---|---|
| iOS／iPadOS | 17 | 11 |
| macOS | 13 | 10 |
| visionOS | 17 | 12 |
| watchOS | 16 | 12 |
| tvOS | 29 | 23 |

文字要能放大到至少 200%（watchOS 140%）。

### 1.2 iOS（預設 Large）【官方＋實測一致】
| Style | 字重 | Size | Leading | 加粗後 | SwiftUI |
|---|---|---|---|---|---|
| Large Title | Regular | 34 | 41 | Bold | `.largeTitle` |
| Title 1 | Regular | 28 | 34 | Bold | `.title` |
| Title 2 | Regular | 22 | 28 | Bold | `.title2` |
| Title 3 | Regular | 20 | 25 | Semibold | `.title3` |
| Headline | **Semibold** | 17 | 22 | Semibold | `.headline` |
| Body | Regular | 17 | 22 | Semibold | `.body` |
| Callout | Regular | 16 | 21 | Semibold | `.callout` |
| Subheadline | Regular | 15 | 20 | Semibold | `.subheadline` |
| Footnote | Regular | 13 | 18 | Semibold | `.footnote` |
| Caption 1 | Regular | 12 | 16 | Semibold | `.caption` |
| Caption 2 | Regular | 11 | 13 | Semibold | `.caption2` |

- Body 各級：xSmall 14、Small 15、Medium 16、**Large 17**、xLarge 19、xxLarge 21、xxxLarge 23；無障礙 AX1–AX5：28／33／40／47／53。【官方＋實測】
- **坑**：UIKit 的 `UIFont.lineHeight` 比 HIG Leading 小（body 20.29，不是 22）。HIG Leading 是設計稿行距；要跟設計稿一致得自己設 paragraph style 或 `.lineSpacing()`。【實測】
- 大字級時改堆疊版面、減少欄數；最大無障礙字級下，顯示的有用內容要跟最大一般字級一樣多。【官方】

### 1.3 macOS（不支援 Dynamic Type，固定大小）【官方＋實測一致】
| Style | 字重 | Size | Line height | 加粗後 |
|---|---|---|---|---|
| Large Title | Regular | 26 | 32 | Bold |
| Title 1 | Regular | 22 | 26 | Bold |
| Title 2 | Regular | 17 | 22 | Bold |
| Title 3 | Regular | 15 | 20 | Semibold |
| Headline | **Bold** | 13 | 16 | Heavy |
| Body | Regular | 13 | 16 | Semibold |
| Callout | Regular | 12 | 15 | Semibold |
| Subheadline | Regular | 11 | 14 | Semibold |
| Footnote | Regular | 10 | 13 | Semibold |
| Caption 1 | Regular | 10 | 13 | Medium |
| Caption 2 | Medium | 10 | 13 | Semibold |

- `NSFont.systemFontSize` 13、`smallSystemFontSize` 11、`labelFontSize` 10。依控制項尺寸：mini 9、small 11、regular 13。【實測】
- 要跟系統控制項一致用 `NSFont.controlContentFont(ofSize:)`、`menuFont`、`labelFont` 等。【官方】
- **Mac 上用 17pt 內文會像放大版 iPad app**，這是最常見的錯。

### 1.4 其他平台
- visionOS：SF Pro 較粗版本，多 `.extraLargeTitle`／`.extraLargeTitle2`；無背景的文字加粗、不加陰影。【官方】
- tvOS 27 開始支援 Dynamic Type（WWDC26），HIG 表尚未更新。【官方】
- iOS 26 起字型「更粗、靠左對齊」，用在 alert、onboarding 等關鍵時刻。【官方】

## 2. 字族與細節

| 字族 | 用途 | SwiftUI |
|---|---|---|
| SF Pro | iOS／macOS／visionOS／tvOS 系統字；9 字重、含 Condensed／Expanded（`Font.Width`） | `.default` |
| SF Pro Rounded | 圓體 | `.rounded` |
| SF Mono | 等寬 | `.monospaced` |
| New York | 襯線 | `.serif` |
| SF Compact | watchOS | — |

- **不要把系統字型打包進 app**，用 `Font.Design` 取得。【官方】
- **Optical size**：現行系統字是可變字體，自動在 Text／Display 間內插，不用自己切。只有在不支援可變字體的設計工具做 mockup 時才照舊規則：19pt 以下 Text、20pt 以上 Display。【官方＋舊版 HIG】
- **Tracking**：系統自動依字級調整，**app 裡不要手動加**；`tracking` 不為 0 會關掉連字。只有做 mockup 才照表（17pt −0.43pt，網路流傳的 −0.41 是舊值）。【官方】
- **字重**：用 Regular／Medium／Semibold／Bold；避免 Ultralight／Thin／Light 做內文。【官方】
- **行距**：3 行以上的文字不要用 tight leading（`Font.leading(.tight)`）。【官方】
- 執行期字型名 `.SFUI-*`／`.SFNS-*` 是私有名稱，不要寫死。【實測】

## 3. 繁體中文

HIG 幾乎完全沒講 CJK 排版【官方：查無】，以下是實測與業界標準。

- **用系統字，讓它自動 fallback**：系統字遇到中文會改用 `.PingFang UI TC`（蘋方 UI 版），**行高不變**：17pt 時「Hello」「你好」「Hello 你好」行高都是 20.3。【實測 iOS 26.5／macOS 27】
- **不要手動指定 `PingFangTC-Regular`**：17pt 行高變 23.8（+17%），而且 ascender／descender 跟 SF 不同，中英混排會上下錯位。【實測】
- PingFang TC 有 Ultralight／Thin／Light／Regular／Medium／Semibold，**沒有 Bold**；對中文 `.bold()` 實際大約是 Semibold。【實測＋推論】
- 文字語言跟 UI 語言不同時，用 `.typesettingLanguage(.init(identifier: "zh-Hant"))`（iOS 17／macOS 14 起），行高、斷行、間距會照該語言處理。【官方】
- 標點：台灣標點置中（W3C clreq）；PingFang TC 本來就置中，不要在繁中介面用 SC 字形。【第三方標準】
- 長文行高：Apple 沒給數字，業界慣例 1.5–1.8 倍；UI 短標籤用系統自然行高即可。【第三方】
- 文案規則（不加空格、「⋯」、「」）見 `zh-tw-writing.md`。

## 4. 版面

### 4.1 邊距【實測 iOS 26.5】
| 裝置 | 系統最小左右邊距 | safe area 上／下 |
|---|---|---|
| iPhone 17 直向（402pt 寬） | **16** | 62／34 |
| iPhone 17 Pro Max 直向（440pt 寬） | **20** | 62／34 |
| iPad Pro 11" 直向 | **20** | 32／25 |

- 常見說法「compact 16、regular 20」不精確（Pro Max 直向是 compact 但邊距 20）。**不要寫死 16**，用 layout margins、`.padding()`、`.scenePadding()`、`safeAreaPadding`。
- 子 view 預設 layout margin 每邊 8pt。【官方＋實測】
- **readableContentGuide 在 iOS 26 起幾乎等於全寬**（iPad Pro 11" 直向 794pt）。長文要自己設最大寬度，約 600–700pt 或每行 60–75 字元。【實測】

### 4.2 Safe area 與背景【官方】
- 控制項和重要內容放在 safe area 內；**全螢幕背景要延伸到 sidebar／toolbar／tab bar 底下**，被 sidebar 蓋住時用 `backgroundExtensionEffect()`（SwiftUI）／`NSBackgroundExtensionView`／`UIBackgroundExtensionView`。
- **不要在控制項底下墊實色或半透明條**，用 scroll edge effect 分隔。
- macOS：**不要把控制項或關鍵資訊放在視窗底部**（視窗常被拖到螢幕下緣）。
- macOS 26+ 避開視窗大圓角：`layoutGuide(for: .safeArea(cornerAdaptation: .horizontal))`。

### 4.3 Size class【官方】
- 用 size class 決定版面，**不要用 `UIDevice.idiom` 或方向**（iPhone Mirroring、iPad 視窗化、iOS 27 iPhone app 可自由縮放、iPhone Duo 會出現任意組合）。
- 版面改變只改「露出多少功能」，不改功能本身（例：tab bar 變 sidebar）。
- iPhone Duo（2026-09 新頁）：外螢幕 compact、內螢幕 regular；toolbar／tab bar 可能移到側邊；grid 用偶數欄。相關 API（`ReservedRegion` 等）作者環境 Xcode 27.0 SDK 還沒有。

### 4.4 間距
- **8pt 網格不是 Apple 規定**，是業界慣例。官方出現過的數字：子 view 邊距 8、根 view 16／20、有外框元件周圍約 12、無外框元件周圍約 24、macOS image button 內距約 10。【官方】
- macOS 視窗最小尺寸 HIG 沒給數字；SwiftUI 用內容的 `.frame(minWidth:minHeight:)`。

## 5. 點擊範圍與控制項尺寸

### 5.1 最小控制項尺寸【官方 HIG Accessibility】
| 平台 | 預設 | 最小 |
|---|---|---|
| iOS／iPadOS | 44×44 | 28×28 |
| macOS | 28×28 | 20×20 |
| visionOS | 60×60 | 28×28 |
| watchOS | 44×44 | 28×28 |
| tvOS | 66×66 | 56×56 |

- 指的是可點範圍，視覺可以小，用 padding 或 `.contentShape()` 補足。
- 間距：有外框元件周圍約 12pt、無外框約 24pt；visionOS 按鈕中心距至少 60pt。【官方】

### 5.2 macOS 控制項高度【實測 macOS 27，Apple 文件沒寫數字】
| ControlSize | 字級 | Push button | Pop-up／Segmented | Text field | Checkbox |
|---|---|---|---|---|---|
| mini | 9 | 16 | 16 | 19 | 12 |
| small | 11 | 20 | 20 | 22 | 14 |
| **regular** | 13 | **24** | 24 | 24 | 16 |
| large | 13 | 28 | 28 | 24 | 18 |
| extraLarge | 13 | 36 | 36 | 24 | 18 |

- 版本注意：SwiftUI `ControlSize.extraLarge` 早在 iOS 17／macOS 14 就有；macOS 26 新增的是 AppKit 的 `NSControl.ControlSize.extraLarge`。
- macOS 26 起 mini～regular 比以前高、維持圓角矩形；**large 與 extraLarge 變膠囊**，extraLarge 用來強調最主要動作。【官方 WWDC25-310】
- 密集的 inspector 用 `prefersCompactControlSizeMetrics = true`，回到舊尺寸（regular 20）。【官方＋實測】
- **不要寫死高度**，用 Auto Layout／SwiftUI 自然尺寸。

### 5.3 iOS 控制項（視覺高度）【實測 iOS 26.5】
UIButton medium 34、large 50；`UISwitch` 61×28（舊版 51×31）；segmented 31；text field 34；navigation bar 54；tab bar iPhone 83（含 home indicator）。系統元件的可點範圍會自己補到 44。

## 6. 圓角

### 6.1 Continuous corner
- SwiftUI：`RoundedRectangle(cornerRadius: 12, style: .continuous)`、`.rect(cornerRadius: 12, style: .continuous)`。現行文件預設已是 continuous，但**一律明寫**確保跨版本一致。【官方】
- UIKit：`layer.cornerCurve = .continuous`；iOS 26 起可用 `cornerConfiguration`。

### 6.2 Concentric（同心）【官方】
- 公式：**內圓角 ＝ 外圓角 − 兩角之間距離**；算到 ≤0 就是直角，用 minimum 設下限。
- 三種形狀：fixed、capsule（半徑＝高度一半）、concentric。巢狀元件用 concentric＋fallback，單獨出現或放進容器都對。
- 內外用同一個半徑會「張開（flared）」，這是很常見的錯。
- Toolbar 裡的標準元件自動同心；自訂元件也要。

### 6.3 API
| API | 版本 |
|---|---|
| SwiftUI `ConcentricRectangle()`、`.rect(corners: .concentric)`、`.concentric(minimum: 12)`、`.fixed(24)` | iOS／macOS 26 |
| SwiftUI `.containerShape(RoundedRectangle(...))`：自訂容器要先宣告形狀，子元件才算得出同心半徑 | 既有 |
| UIKit `view.cornerConfiguration = .corners(radius: .containerConcentric(minimum: 12))` | iOS 26 |
| AppKit `NSView.cornerConfiguration`（唯讀，**要在子類別 override**）、`.uniformCorners(radius: .containerConcentric(8))` | **macOS 27** |

```swift
// SwiftUI：自訂控制項跟容器同心，最小 12
MyControl()
    .padding(8)
    .background(.tint, in: .rect(corners: .concentric(minimum: 12)))
```

- 舊系統 fallback：手算 `RoundedRectangle(cornerRadius: outer - padding, style: .continuous)`，或用 `ContainerRelativeShape`。
- 網頁：CSS `corner-shape: squircle` 目前只有 Chromium 支援，Safari 沒有，用一般 `border-radius` 即可。

## 7. 坑
1. 寫死字級 → Dynamic Type 失效。
2. iOS 字級搬到 macOS（Mac 內文 13 不是 17）。
3. 拿 HIG Leading 驗收 UIKit 行高。
4. 中文寫死 PingFang TC。
5. 手動替系統字加 tracking。
6. 寫死 16pt 邊距；依裝置／方向判斷版面。
7. 相信 readableContentGuide 會限寬。
8. 可點範圍 <44（visionOS <60）；圖示按鈕貼太近。
9. macOS 寫死控制項高度 21／22pt。
10. 巢狀圓角同一半徑；用 `.circular` 圓角。
11. 控制項底下墊色條；重要按鈕放 macOS 視窗最底。
12. 把 8pt 網格說成 Apple 官方規定。
