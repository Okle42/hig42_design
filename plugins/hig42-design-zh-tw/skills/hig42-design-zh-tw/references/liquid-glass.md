# Liquid Glass（iOS 26／macOS Tahoe 26 → iOS 27／macOS 27）

> SwiftUI／AppKit 範例已對 macOS 27 SDK 用 `swiftc -typecheck` 驗過。來源清單見 repo 的 `SOURCES.md`

## 目錄
1. 什麼時候用、什麼時候不用
2. SwiftUI API
3. AppKit API
4. UIKit API（摘要）
5. 無障礙與使用者設定
6. 採用／遷移清單
7. 27 的變化
8. 舊系統 fallback
9. 坑

---

## 1. 用在哪一層【官方】

- Liquid Glass 是**功能層**材質：toolbar、tab bar、sidebar、浮動控制項，浮在內容上。
- **不要用在內容層**（列表 cell、卡片背景）。內容層分層用標準 material（`.regularMaterial`）或實色。例外：Slider、Toggle 被操作時會暫時變玻璃。
- **不要玻璃疊玻璃**：glass toolbar 裡的按鈕不要再 `.glassEffect()`；sheet 本身是玻璃，裡面不要再放玻璃卡片。
- 兩種變體，**不要混用**：
  - `regular`（預設）：模糊並調整亮度、會自適應。文字多的元件（alert、sidebar、popover）一定用它。**例外（刻意偏離 HIG，單一案例實測）：整片視窗都是玻璃、底下背景不可控的浮動面板，regular 會跟著背景變灰，改 clear＋tint，見 §3.1a。**
  - `clear`：高透明、不自適應。三個條件都成立才用：底下是照片／影片等豐富媒體、可以加暗化層、上面的文字符號粗而亮。底下偏亮時加約 35% 不透明度的深色層。
- 自訂元件用玻璃要「sparingly」，只給最重要的功能元素。
- 顏色：想讓 app 有顏色，**把顏色放在內容層**讓玻璃吸收；tint 只給 1–2 個主要動作；不要全部 tint（每個都上色，就沒有一個突出）。
- 靜止狀態（例如剛打開、在頂端）避免內容跟玻璃控制項重疊。
- Toolbar：依功能分組最多約 3 組；文字按鈕跟圖示按鈕分開；整個 toolbar 只有一個 `.prominent` 主要動作，放尾端；非互動元素（標題、狀態文字）不要套玻璃。

## 2. SwiftUI API（除另外標 27 的之外，都是 iOS 26.0／macOS 26.0 起；visionOS 不可用）【SDK】

### 2.1 glassEffect
```swift
func glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape()) -> some View
// 預設形狀是 Capsule
```
**要放在 `.padding()`、`.frame()` 等外觀 modifier 之後**，否則玻璃只包到文字。
```swift
Label("62°C", systemImage: "thermometer.medium")
    .padding()
    .glassEffect()                                      // 膠囊、regular

StatusSummary()
    .padding(12)
    .glassEffect(in: .rect(cornerRadius: 16))           // 大元件用圓角矩形

Label("暫停", systemImage: "pause.fill")
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())  // 上色＋互動回饋

Label("全螢幕", systemImage: "arrow.up.left.and.arrow.down.right")
    .padding()
    .glassEffect(.clear)
    .background(.black.opacity(0.3), in: Capsule())     // clear 一定配暗化層

chip.glassEffect(isOn ? .regular : .identity)           // 條件式關閉，不必拆 view 結構
```
- `Glass`：`.regular`、`.clear`、`.identity`；`.tint(_ color: Color?)`、`.interactive(_ isEnabled: Bool = true)`。
- `.interactive()` 在 macOS 27 起點擊時會輕微彈一下，只給按鈕或裝按鈕的容器。

### 2.2 GlassEffectContainer 與 morph
多塊自訂玻璃**一定要包進 container**：玻璃不能取樣另一塊玻璃，放同一容器才外觀一致、morph 才有效、效能也較好。
```swift
struct FanControls: View {
    @State private var showsModes = false
    @Namespace private var glassSpace

    var body: some View {
        GlassEffectContainer(spacing: 16) {          // 不大於 HStack spacing，靜止時不會黏在一起
            HStack(spacing: 16) {
                Button("風扇", systemImage: "fan") { withAnimation(.smooth) { showsModes.toggle() } }
                    .padding(10)
                    .glassEffect(.regular.interactive())
                    .glassEffectID("fan", in: glassSpace)
                if showsModes {
                    Button("靜音", systemImage: "speaker.slash") { }
                        .padding(10)
                        .glassEffect(.regular.interactive())
                        .glassEffectID("quiet", in: glassSpace)   // 展開時從「風扇」那塊玻璃長出來
                }
            }
        }
    }
}
```
- container `spacing` 大於內部 stack spacing 時，靜止狀態就會黏成一塊。
- `glassEffectID`／`glassEffectTransition(.matchedGeometry / .materialize / .identity)` 只在轉場動畫期間生效。
- `glassEffectUnion(id:namespace:)`：讓不相鄰的 view 靜止時也合成同一塊。

### 2.3 按鈕
```swift
Button("開始監控") { }.buttonStyle(.glassProminent)     // 主要動作（accent 色背景），每畫面 1–2 個
Button("查看紀錄") { }.buttonStyle(.glass)               // 次要
Button("截圖") { }.buttonStyle(.glass(.clear))          // 浮在影像上（iOS／macOS 26.0 target typecheck 通過）
```
相關：`.buttonBorderShape(.capsule)`、`.controlSize(.extraLarge)`、`.buttonSizing(.flexible)`。

### 2.4 Toolbar
```swift
.toolbar {
    ToolbarItemGroup {
        Button("上一段", systemImage: "chevron.left") { }
        Button("下一段", systemImage: "chevron.right") { }
    }
    ToolbarSpacer(.fixed)                    // 切開共用玻璃背景
    ToolbarItem { ShareLink(item: reportURL) }
    ToolbarItem { AccountBadge() }
        .sharedBackgroundVisibility(.hidden) // 脫離共用玻璃（例：頭像）
}
```
- **隱藏 toolbar 項目要隱藏整個 item，不是隱藏裡面的 view**，否則會留下一顆空玻璃。
- 27 新增：`visibilityPriority(_:)`（iOS 27／macOS 26.1）、`ToolbarOverflowMenu`（iOS 27，macOS 不可用）、`.topBarPinnedTrailing`（iOS 27）、`contentMarginsRemoved()`、`toolbarMinimizationBehavior(_:for:)`（注意：WWDC26 講者口述的 `toolbarMinimizeBehavior` 不是正確名稱；值 `.onScrollDown` 等 macOS 不可用）。

### 2.5 Scroll edge effect 與背景延伸
```swift
ScrollView { ... }
    .scrollEdgeEffectStyle(.hard, for: .top)  // .automatic / .soft / .hard
    .safeAreaBar(edge: .bottom) { StatusBar() }   // 自訂 bar 也吃得到 edge effect

NavigationSplitView { DeviceList() } detail: {
    ScrollView {
        Image("cover").resizable().aspectRatio(contentMode: .fill)
            .backgroundExtensionEffect()      // 鏡像模糊延伸到 sidebar 底下；會裁切 view，只用在背景圖
    }
}
```
- 每個 view 只用一個 scroll edge effect，沒有浮動 UI 的地方不要用（它不是裝飾）。
- **27 起偏好 `.automatic`**：它有自己的新外觀（捲動時頂部統一 toolbar 帶）。以前手動設 `.soft` 的要重新評估。【官方 HIG Scroll views 2026-06】

### 2.6 TabView（iOS）
```swift
TabView {
    Tab("總覽", systemImage: "gauge.with.dots.needle.33percent") { OverviewScreen() }
    Tab("紀錄", systemImage: "list.bullet.rectangle") { HistoryScreen() }
    Tab("新增", systemImage: "plus", role: .prominent) { AddDeviceScreen() }  // iOS 27：尾端獨立位置，只能一個
    Tab(role: .search) { SearchScreen() }
}
.tabBarMinimizeBehavior(.onScrollDown)        // 值只有 iOS
.tabViewBottomAccessory { LiveReadingBar() }  // iOS 26；放跨頁常駐資訊，不要放畫面專屬動作
```
可改成 sidebar：`.tabViewStyle(.sidebarAdaptable)`。

### 2.7 Sheet
- iOS 26 部分高度 sheet 預設內縮＋玻璃背景；**用了 `presentationBackground` 的考慮移除**。
- 從按鈕 morph 出 sheet：`matchedTransitionSource(id:in:)` ＋ `.navigationTransition(.zoom(sourceID:in:))`。
- confirmationDialog 會從來源按鈕長出來，要掛在觸發按鈕上。

### 2.8 同心圓角
見 `typography-layout.md` §6。`.rect(corners: .concentric(minimum: 12))`、`ConcentricRectangle`。**`.rect(corner: .containerConcentric)` 是 WWDC25 beta 名稱，正式 SDK 沒有。**

### 2.9 27 其他新外觀 API【SDK】
`textInputBorderShape(.capsule / .roundedRectangle)`、`.textFieldStyle(.bordered)`、`PickerStyle.tabs`、`@Environment(\.systemPrefersReducedResourceUsage)`（系統希望省資源時減少重效果）、選單項目要顯示圖示用 `.labelStyle(.titleAndIcon)`。

## 3. AppKit API【SDK】

### 3.1 NSGlassEffectView（macOS 26）
```swift
let glass = NSGlassEffectView()
glass.contentView = readingView      // 內容一定放 contentView，不要把 glass 當兄弟 view 墊在後面
glass.cornerRadius = 999             // 大於一半高度＝膠囊
glass.style = .regular               // 或 .clear
glass.tintColor = nil
if #available(macOS 27, *) { glass.effectIsInteractive = true }  // 只給互動控制項的背景
```

### 3.1a 整窗玻璃的浮動面板（選單列 app 面板、HUD）

> 證據範圍：**單一案例實測**（一個選單列監控 app 的整窗面板，macOS 27、1080p @1x 外接螢幕，2026-09-25，8 輪同螢幕截圖比對 Dock／桌面 widget）。原則部分可一般化；數字是該案例調出來的**起始值**，換 app 或螢幕要重量。
> 這是**刻意偏離 HIG**：官方說 clear 只用在影像／影片等媒體上方；整窗面板底下是任意桌面與視窗，官方沒涵蓋這個情境。

**原則【實測，可一般化】**
- **整片視窗都是玻璃時，regular 不合用**：它會依底下內容自適應亮度，面板整片跟著背景變灰（深色星空上被抬成霧灰、白網頁上洗成淺灰、淺色外觀壓在深色桌布上變中灰），上面的彩色數字對比掉到 1.1–2:1。`NSGlassEffectView` 也不會替你的內容換深淺色。
- **regular 疊白色 `tintColor` 提不亮**（tint 加重反而更暗），淺色外觀也不能靠它。
- **改用 `.clear`＋`tintColor` 當暗化／提亮層**：這就是 §1「clear 一定配暗化層」那一層，只是用 tint 做。
- **透明度給使用者調**，並在設定說明寫出「越透明，亮背景上越難讀」；「減少透明度」開著時退實色底；「增加對比」時 tint 加重。
- **玻璃上不要再鋪近實色卡片**（看起來像玻璃上疊塑膠板）。區段用分隔線或極淡分組底；說明文字用 `labelColor`／`secondaryLabelColor`（vibrancy），彩色只給大數字、圖表線、狀態點。
- **邊緣光學系統的方向性**：Dock／widget 只有上下緣亮、左右幾乎沒有；四邊一圈均勻白框會像 HUD 外框。「增加對比」分支才畫完整框。
- **視窗用 borderless**：`NSPanel` 帶 `.titled`＋`.utilityWindow` 會多一層系統外框與背景。改 `[.borderless, .nonactivatingPanel]`、`backgroundColor = .clear`，自己畫圓角，外觀變了呼叫 `invalidateShadow()`。這跟 HIG「panel 要有標題列」衝突，只適用 HUD 型面板（見 `macos-components.md` §4.1）。
- **坑：玻璃直接當 `contentView`、裡面放 `NSHostingView` 時，hosting view 的 intrinsic size 會把內容撐得比視窗高**（該案例實測多 76pt，上緣被裁）。hosting view 用 `translatesAutoresizingMaskIntoConstraints = true`＋autoresizing，由視窗自己量內容高度設 frame。
- **驗收要看實機**：離屏渲染畫不出真的玻璃。在**同一張整螢幕截圖**裡並排面板與 Dock／widget，比底色、邊緣亮度、圓角；對比要在「深色桌布、白網頁、淺色外觀」三種背景都量。
- **截圖會帶到個資**（行事曆事件、工作目錄、其他視窗內容），進 repo 或對外前要裁切或模糊，並用 OCR 掃一次。

**案例起始值【實測，單一案例】**
| 項目 | 值 | 量到的結果（0–255 底色亮度） |
|---|---|---|
| 深色 tint | `NSColor(srgbRed: 0, green: 0, blue: 0.02, alpha: 0.70)` | 星空底約 10、白網頁底約 50（Dock 約 12） |
| 淺色 tint | `NSColor(white: 1, alpha: 0.62)` | 星空底約 193、白網頁底約 250；0.80 在白網頁上變純白 255，太實 |
| 使用者透明度 t | tint ＝ 預設 × (1.2 − t)，t 預設 0.2 | — |
| 增加對比 | tint 至少深 0.85／淺 0.90 | — |
| 圓角 | 26pt（量 widget／Dock 輪廓；macOS 27 官方未公布數值） | 內部元件同心調整 |
| 上緣亮邊 | 往內 83→28→21→18→16（Dock 量測）＋內側 3–4pt 柔光，左右不補 | — |

### 3.2 NSGlassEffectContainerView
```swift
let stack = NSStackView(views: [temperatureGlass, fanGlass])
stack.orientation = .horizontal
let container = NSGlassEffectContainerView()
container.contentView = stack
container.spacing = 12   // 預設 0：只批次渲染不融合
```

### 3.3 按鈕與控制項
```swift
let start = NSButton(title: "開始監控", target: self, action: #selector(startMonitoring))
start.bezelStyle = .glass
start.controlSize = .extraLarge
start.keyEquivalent = "\r"           // default button 自動 primary prominence
clearButton.tintProminence = .secondary   // 次要／破壞性動作
```
- `NSControl.BorderShape`（`.automatic/.capsule/.roundedRectangle/.circle`）：NSButton、NSSegmentedControl、NSPopUpButton、NSTextField。
- `prefersCompactControlSizeMetrics`：密集 inspector 回到舊尺寸，會傳給子孫。
- 27 新增：`NSSegmentedControl.role`／`NSToolbarItemGroup.role`（`.tabs/.valueSelection`）、`NSControl.Events`、`NSMenuItem.preferredImageVisibility`。

### 3.4 Toolbar、Sidebar、Split view
- 系統自動把 toolbar 按鈕分組成同一塊玻璃；要分開用 `NSToolbarItemGroup` 或 `.space`。
- 非互動項目：`toolbarItem.isBordered = false`。主要動作：`toolbarItem.style = .prominent`、`backgroundTintColor`。徽章：`toolbarItem.badge = .count(4)`。
- **用 `NSSplitViewController` ＋ `NSSplitViewItem(sidebarWithViewController:)`／`init(inspectorWithViewController:)` 自動拿到玻璃**：sidebar 浮起、inspector 邊到邊。
- **舊的 sidebar `NSVisualEffectView` 要刪掉**，否則擋住玻璃（只在 `< macOS 26` 分支加）。
- 內容延伸到 sidebar 底下：在內容那一欄（不是 sidebar）設 `splitViewItem.automaticallyAdjustsSafeAreaInsets = true`。
- 背景延伸：`NSBackgroundExtensionView`，`contentView` 自動放在 safe area 內，外面用鏡像模糊補滿。
- 避開視窗圓角：`layoutGuide(for: .safeArea(cornerAdaptation: .horizontal))`。

### 3.5 macOS 27 同心圓角
```swift
@available(macOS 27, *)
final class CornerCard: NSView {
    override var cornerConfiguration: NSViewCornerConfiguration? {
        .uniformCorners(radius: .containerConcentric(8))   // 跟容器同心，最小 8pt
    }
    override func viewDidChangeEffectiveCornerRadii() {
        super.viewDidChangeEffectiveCornerRadii()
        layer?.cornerRadius = effectiveCornerRadii?.topLeft ?? 8
    }
}
```
- macOS 27 的 `NSScreen.touchCapabilities` 等觸控 API 是給 **Sidecar（iPad 當第二螢幕）** 用的，不是觸控螢幕 Mac，不要因此放大 Mac 的觸控目標。

## 4. UIKit（摘要）【SDK】
| API | 版本 |
|---|---|
| `UIGlassEffect(style: .regular/.clear)`、`.isInteractive`、`.tintColor`；`UIGlassContainerEffect` | iOS 26 |
| `UIButton.Configuration.glass()`／`.prominentGlass()`／`.clearGlass()`／`.prominentClearGlass()` | iOS 26 |
| `UIBackgroundExtensionView`、`UIScrollEdgeEffect`、`UIBarButtonItem.hidesSharedBackground` | iOS 26 |
| `view.cornerConfiguration = .corners(radius: .containerConcentric(minimum: 12))` | iOS 26（已 typecheck） |
| 27：`UIBarButtonItem.visibilityPriority`、`UINavigationItem.navigationBarMinimization`、`UITabBarController.prominentTabIdentifier`、`UIMenuElement.preferredImageVisibility` | iOS 27 |

- 移除 `UIBarAppearance`／bar `backgroundColor` 自訂，會干擾玻璃。
- iOS 27 SDK 編譯的 app **必須用 scene-based life cycle**，否則無法啟動（非設計但會擋上線）。

## 5. 無障礙與使用者設定【官方】

| 設定 | 玻璃的變化 |
|---|---|
| 減少透明度 | 更霧、遮住更多背景 |
| 增加對比 | 以黑白為主並加對比邊框 |
| 減少動態效果 | 降低效果、停用彈性行為 |
| 玻璃外觀偏好（26.1：清透／著色；27：連續滑桿） | 使用者可調，**沒有開發者 API 可讀** |

- 標準元件自動處理；**自訂元件要自己讀環境值並測**：`accessibilityReduceTransparency`、`accessibilityReduceMotion`、`colorSchemeContrast`、`accessibilityShowBorders`（macOS 27 有獨立「顯示邊線」設定）、`accessibilityReduceHighlightingEffects`（26.4）、`accessibilityPrefersCrossFadeTransitions`（26.4）。
- **不要把可讀性押在某種透明度上**：玻璃上的文字／符號用系統單色或 vibrant 色；不要在玻璃後面自己墊半透明色塊（在「完全著色」模式會變髒，也蓋掉 scroll edge effect）。
- 圖示按鈕一律給 accessibility label。

```swift
struct AdaptiveGlassChip: View {
    @Environment(\.accessibilityShowBorders) private var showBorders
    var body: some View {
        Label("Filter", systemImage: "line.3.horizontal.decrease")
            .padding(.horizontal, 12).padding(.vertical, 8)
            .glassEffect(.regular.interactive())
            .overlay { if showBorders { Capsule().strokeBorder(.primary.opacity(0.6)) } }
    }
}
```

自訂玻璃元件的截圖檢查組合：淺色／深色 × 滑桿兩端（清透／著色）× 減少透明度 × 增加對比 × 顯示邊線。

## 6. 採用／遷移清單
1. 用 Xcode 26+ 重新編譯，標準元件自動換新外觀。
2. **Xcode 27 沒有退路**：`UIDesignRequiresCompatibility` 在針對 27 建置時被忽略。【官方文件原文】
3. **刪掉自訂背景**（最重要）：SwiftUI `toolbarBackground`、`presentationBackground`；UIKit `UIBarAppearance`；AppKit sidebar 的 `NSVisualEffectView`、自訂 `NSToolbar` 外觀。
4. 不寫死控制項尺寸。
5. 清單 section header 不再強制全大寫，自己改字串。
6. Action sheet／confirmationDialog 要設來源。
7. 選單圖示：27 起 iPadOS／macOS 選單列預設隱藏，只給關鍵動作；同組全有或全無。
8. 效能：自訂玻璃合併進 container、限制同時出現的數量，用 Instruments 量。

## 7. 27 的變化（大多不用重編就會套用）【官方 WWDC26】
- 玻璃更能擴散背後內容、加深色邊緣＋更亮高光，可讀性提升。
- 設定裡的透明度改成連續滑桿（超清透 ↔ 完全著色）。
- Mac 與 iPad 的 sidebar 延伸到視窗邊緣；**sidebar 圖示恢復顏色**（預設 app accent color）；sidebar 選取改 semibold。
- **macOS 所有視窗統一較緊的圓角**（數值未公布）。
- iPad 非作用中視窗會變暗（`@Environment(\.appearsActive)` 可讓自訂元件跟著）。
- iPhone app 在 iOS 27 可自由縮放。
- App icon 渲染更銳利、新增可選折射；Icon Composer 2。
- **玻璃 API 本身沒有更名或棄用**；27 SDK 用 `@available(anyAppleOS 27.0, *)` 新語法，查 SDK 要搜這個字串。
- `PreviewProvider` 在 27 標 deprecated，改用 `#Preview`。

## 8. 舊系統 fallback（deployment target < 26）
```swift
extension View {
    @ViewBuilder
    func floatingControlBackground<S: Shape>(in shape: S = Capsule(),
                                             tint: Color? = nil,
                                             interactive: Bool = false) -> some View {
        if #available(iOS 26.0, macOS 26.0, *) {
            self.glassEffect(interactive ? .regular.tint(tint).interactive()
                                         : .regular.tint(tint), in: shape)
        } else {
            self.background(.regularMaterial, in: shape)
                .overlay(shape.stroke(.separator.opacity(0.5), lineWidth: 0.5))
                .shadow(color: .black.opacity(0.12), radius: 6, y: 2)
        }
    }

    @ViewBuilder
    func primaryActionStyle() -> some View {
        if #available(iOS 26.0, macOS 26.0, *) {
            self.buttonStyle(.glassProminent)
        } else {
            self.buttonStyle(.borderedProminent)
        }
    }
}
```
```swift
// AppKit
func makeFloatingPanel(content: NSView) -> NSView {
    if #available(macOS 26.0, *) {
        let glass = NSGlassEffectView()
        glass.contentView = content
        glass.cornerRadius = 12
        return glass
    } else {
        let fx = NSVisualEffectView()
        fx.material = .popover            // 依語意挑：.popover / .hudWindow / .menu
        fx.blendingMode = .withinWindow
        fx.state = .active
        fx.wantsLayer = true
        fx.layer?.cornerRadius = 12
        fx.layer?.cornerCurve = .continuous
        content.translatesAutoresizingMaskIntoConstraints = false
        fx.addSubview(content)
        NSLayoutConstraint.activate([
            content.leadingAnchor.constraint(equalTo: fx.leadingAnchor),
            content.trailingAnchor.constraint(equalTo: fx.trailingAnchor),
            content.topAnchor.constraint(equalTo: fx.topAnchor),
            content.bottomAnchor.constraint(equalTo: fx.bottomAnchor),
        ])
        return fx
    }
}
```
舊系統的目的是**維持層次**，不是模仿折射。`glassEffectID`、`backgroundExtensionEffect`、`scrollEdgeEffectStyle`、`ToolbarSpacer` 在舊系統直接不套用即可。

## 9. 坑
1. 自訂 bar 背景蓋掉玻璃。
2. 玻璃疊玻璃；內容層用玻璃。
3. `.glassEffect()` 放在 `.padding()` 前。
4. 多塊玻璃沒包 container；container spacing 比 stack spacing 大。
5. `NSGlassEffectView` 當兄弟 view 墊在後面。
6. Clear 沒加暗化層；全部 tint。
7. 隱藏 toolbar item 的內容而不是 item → 空玻璃。
8. 文字按鈕和符號按鈕同一塊玻璃。
9. `.rect(corner: .containerConcentric)`、`toolbarMinimizeBehavior` 這兩個錯誤名稱。
10. 以為 `UIDesignRequiresCompatibility` 還能用。
11. 27 還強制 `.soft` scroll edge；每個選單項都塞圖示。
12. macOS 圖示保留不規則外形 → 被放進系統灰底框。
