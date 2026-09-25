# 無障礙實作：VoiceOver、鍵盤、文字大小、語音控制、稽核

> 研究機：macOS 27.0（Darwin 27）、Xcode 27（MacOSX27.0.sdk／iPhoneOS27.0.sdk），2026-09-25。來源：HIG Accessibility（2025-06-09 版）與 VoiceOver（2025-03-07 新頁）、Focus and selection、Keyboards、Charts、Typography；Apple 開發者文件（DocC JSON）；App Store Connect「Accessibility Nutrition Labels」各項評估判準；WWDC23-10035、WWDC26-220；作者環境 SDK grep；**作者環境實測是在同一個 process 裡用 NSAccessibility 讀 SwiftUI 產生的無障礙樹**（沒有開 VoiceOver）。來源清單見 repo 的 `SOURCES.md`
>
> **不重複的部分**：對比數值、系統色對比在 `color-materials.md` §7；Reduce Motion 動畫寫法在 `macos-components.md` §9.2；Liquid Glass 在減少透明度、增加對比、顯示邊線下怎麼退化，在 `liquid-glass.md` §5；可點範圍在 `typography-layout.md` §5.1。

## 目錄
1. 原則
2. VoiceOver：label／value／hint／traits
3. 分組、順序、自訂動作、rotor
4. 自訂控制項（SwiftUI／AppKit NSView）
5. 動態內容通知
6. 圖片與圖表
7. macOS 鍵盤與焦點
8. 選單列 app 與浮動面板
9. 文字大小（macOS 與 iOS 不一樣）
10. 語音控制
11. 其他系統設定對照表
12. 自動化稽核與 Accessibility Nutrition Labels
13. 坑

---

## 1. 原則【官方】
- HIG 對無障礙介面的三個要求：**Intuitive**（互動熟悉、一致）、**Perceivable**（不只用一種方式傳達資訊）、**Adaptable**（跟著系統設定調整）。
- 標準元件自己會提供 label、trait、鍵盤操作和語音控制名稱。**自訂元件要自己補齊，而且要做到跟原生元件一樣的程度**。App Store 的 VoiceOver 判準要求自訂元件提供跟原生元件同等的無障礙支援。
- 稽核工具全部通過，不代表 app 就是無障礙的。Apple 原文：「eliminating all audit issues … doesn't guarantee a fully accessible app」。還是要實際用 VoiceOver 走一遍常見任務。
- **VoiceOver、語音控制、切換控制在 Simulator 上都不能用**，一定要用實機測（Apple 文件原文）。macOS 按 ⌘F5 開關 VoiceOver。

## 2. VoiceOver：label／value／hint／traits

| 屬性 | 規則 | 好 | 壞 | 證據 |
|---|---|---|---|---|
| **label** | 很短、識別元素是什麼，**不含元件類型**（類型由 trait 負責），**也不含狀態** | 「儲存」 | 「儲存按鈕」「已勾選的核取方塊」 | 【官方】UIKit `accessibilityLabel`、SwiftUI `accessibilityLabel(_:)`、App Store VoiceOver 判準 |
| label 要能脫離上下文理解 | 同一畫面有多個「刪除」時，要說清楚刪的是什麼 | 「刪除 CPU 感測器」 | 「按這裡」「了解更多」 | 【官方】App Store 判準 |
| **value** | 只在元素有 label 以外的**目前值**時才給（滑桿、進度、溫度） | label「音量」＋value「35%」 | 在「儲存」按鈕上又給 value「儲存」 | 【官方】UIKit `accessibilityValue` |
| 文字欄位 | label 跟值分開：label「電話號碼」、value 是使用者輸入的內容 | — | 只用 placeholder 當 label | 【官方】App Store 判準 |
| **hint** | 描述**做了之後會發生什麼**；簡短的動詞片語；**不重複元素名稱、也不描述手勢** | 「開啟設定」「下載附件」 | 「點兩下這一列來選取訊息」 | 【官方】UIKit `accessibilityHint`、SwiftUI `accessibilityHint(_:)` |
| **traits** | 用 trait 說明類型和狀態（`.isButton`、`.isHeader`、`.isSelected`、`.isToggle`、`.updatesFrequently`） | — | 把「按鈕」寫進 label | 【官方】 |

**繁中寫法**【推論，套用上面規則】：label 用名詞或動詞原形（「分享」「重新整理」「CPU 溫度」），不加「按鈕」「圖示」；hint 用「動詞＋受詞」（「開啟通知設定」），不用「點兩下以⋯」（VoiceOver 會自己唸操作方式）；數值加單位（「72 度」「3,200 RPM」），不用「72°C」這種符號寫法，因為有些語音會唸錯。

**實測（macOS 27，SwiftUI 產生的 AX 樹）**：
- `Button { Image(systemName: "gearshape") }` 沒加 label 時，VoiceOver 拿到的是 **SF Symbol 的自動描述「齒輪形狀」**，不是「設定」。**`.help("設定")` 只會變成 AXHelp，不會變成 label**，兩個都要寫。
- `Label("篩選", systemImage:)` 加 `.labelStyle(.iconOnly)` 時，label 還是「篩選」，**這是圖示按鈕最省事的寫法**。
- `.accessibilityHint(...)` 在 macOS 上對應到 **AXHelp**（VoiceOver 要等一下才唸，或按 VO‑⇧‑H）。
- `.accessibilityAddTraits(.isHeader)` 在 macOS 26 以後的角色是 **AXHeading**（`NSAccessibilityHeadingRole` 是 macOS 26 新增的）。
- `Toggle` 預設是 AXCheckBox；`.toggleStyle(.switch)` 是 AXCheckBox／subrole AXSwitch，**label 放在旁邊獨立的文字元素，不在 switch 身上**。
- 只有形狀的 view（`Circle()`）做成 `.accessibilityElement()` 之後，角色是 **AXUnknown，而且 value 沒有輸出**。狀態點要掛在 Text／Label 上，或是用 `children: .ignore` 把整列合成一個元素（見 §3）。

```swift
// 圖示按鈕：iconOnly Label 最省事；自訂圖示就明寫 label，help 另外給（tooltip ≠ label）
Button("重新整理", systemImage: "arrow.clockwise") { reload() }
    .labelStyle(.iconOnly)
    .help("重新整理")
Button { openSettings() } label: { Image(systemName: "gearshape") }
    .accessibilityLabel("設定")
    .help("設定")
```

## 3. 分組、順序、自訂動作、rotor

### 3.1 `accessibilityElement(children:)`【官方＋實測】
| 值 | 行為 | 用在 |
|---|---|---|
| `.ignore`（預設值） | 產生一個新元素，**子元素全部忽略**，label／value 要自己給 | 一列資訊要自己控制唸法時（推薦） |
| `.combine` | 把非隱藏子元素的屬性**合併**成一個；部分 trait 不會合併；子按鈕的預設動作會變成具名動作 | 圖示＋名稱＋數值的列 |
| `.contain` | 變成**容器**，子元素保留；VoiceOver 會先走完這個容器，再往下一個 | 側邊欄區塊、卡片群、訊息列表 |

實測：`HStack { Image("cpu"); Text("CPU"); Text("72°C") }.accessibilityElement(children: .combine)` 的結果是一個 AXStaticText，value 是「CPU, 72°C」，**圖示被丟掉了**。狀態如果只靠圖示（例如火焰代表過熱），用 `.combine` 會把這個資訊弄丟，要改用 `.ignore` 自己寫 value：

```swift
HStack {
    Image(systemName: hot ? "flame.fill" : "thermometer.medium")
    Text(name); Spacer(); Text("\(temp)°C").monospacedDigit()
}
.accessibilityElement(children: .ignore)
.accessibilityLabel(name)
.accessibilityValue(hot ? "\(temp) 度，過熱" : "\(temp) 度")
```

### 3.2 順序
- VoiceOver 照語言的閱讀方向讀（中文、英文都是由上到下、由左到右）。**視覺上的關聯（例如圖片和圖說）要用分組告訴 VoiceOver**，不然會先唸完所有圖片才唸圖說。【官方 HIG VoiceOver】
- 要調整順序用 `accessibilitySortPriority(_:)`：數字大的先唸，預設值是 0，只會跟同一層的元素比較。【官方】
- 每個畫面要有獨一無二的標題；區段標題加 `.isHeader`，VoiceOver 使用者可以用 rotor 在標題之間跳。【官方】

### 3.3 自訂動作【官方＋實測】
- 右鍵選單、長按、滑動才出現的按鈕、hover 才出現的按鈕，**都要同時提供成自訂動作**（App Store VoiceOver 判準；語音控制也靠這個，說「Show actions for 3」就能叫出來）。
- `accessibilityAction(named:)` 的 `Text` 版是 iOS 13／macOS 10.15 起，字串常值走的 `LocalizedStringKey` 版是 iOS 14／macOS 11 起（iOS 16／macOS 13 才有的是 `StringProtocol` 變數版）。實測：macOS 上會變成 `NSAccessibilityCustomAction`，**呈現順序是宣告順序的反過來**（最後宣告的排第一），最常用的動作要寫在最後。

```swift
Text(subject)
    .contextMenu { Button("封存", action: archive); Button("標為已讀", action: markRead) }
    .accessibilityAction(named: "封存", archive)
    .accessibilityAction(named: "標為已讀", markRead)
```

### 3.4 Rotor【官方＋SDK】
```swift
ScrollView { LazyVStack { ForEach(messages) { MessageRow($0) } } }
    .accessibilityElement(children: .contain)
    .accessibilityRotor("已標幟") {
        ForEach(messages.filter(\.isFlagged)) { m in AccessibilityRotorEntry(m.subject, id: m.id) }
    }
```
- **坑【SDK 實證】**：Apple 文件範例是在 rotor 的 `ForEach` 裡面寫 `if m.isFlagged { … }`。這需要 `Optional: AccessibilityRotorContent`，而這個 conformance **要 macOS 27／iOS 27 才有**。target 26 的話，Swift 6 會直接編譯失敗，Swift 5 則是警告。要先 filter 再丟進 `ForEach`。
- 文字導覽用的系統 rotor：`.accessibilityRotor(.headings)` 等等。

## 4. 自訂控制項

### 4.1 SwiftUI：能用 style 就用 style，不行再用 representation【官方】
優先順序是：**自訂 `ButtonStyle`／`ToggleStyle`**（無障礙行為自動繼承）→ `accessibilityRepresentation`（用一個看不見的標準控制項代表它）→ 手動補 label、value、trait、動作。

```swift
// 自畫的轉速錶 → 對輔助技術而言是 Slider（實測：AXSlider、label「風扇轉速」、min/max 都正確）
FanDial(rpm: $rpm)
    .accessibilityRepresentation {
        Slider(value: $rpm, in: 0...6000, step: 100) { Text("風扇轉速") }
    }

// 手動版：可調整的元素
Text("等級 \(level)")
    .accessibilityElement()
    .accessibilityLabel("等級").accessibilityValue("\(level)")
    .accessibilityAdjustableAction { dir in
        switch dir {
        case .increment: level = min(level + 1, 5)
        case .decrement: level = max(level - 1, 1)
        @unknown default: break
        }
    }
```
- 自訂控制項至少要補齊：**label**、**value**（有值的話）、**trait 或 role**、**主要動作**（`accessibilityAction { }`）、**調整動作**（有值可以調的話）、**鍵盤操作**（§7）、**值改變時的通知**。【官方 WWDC26-220 的四個面向：用途、值、動作、回饋】
- WWDC26-220 的其他 API：`accessibilityActivationPoint`、`accessibilityDirectTouch(_:)`（iOS 17／macOS 14；`.requiresActivation`、`.silentOnTouch`）。用了直接觸控，還是要**另外提供自訂動作**，給切換控制和語音控制用。【官方】

### 4.2 AppKit：自訂 NSView 的最小實作【SDK】
- 用 **role-based 協定**（`NSAccessibilityButton`、`NSAccessibilitySwitch`、`NSAccessibilityCheckBox`、`NSAccessibilitySlider`、`NSAccessibilityStaticText`⋯），編譯器會要求你把必要方法實作出來。例如 Button 要 `accessibilityLabel()`＋`accessibilityPerformPress()`，Slider 要 label、value、increment、decrement。
- 其他狀況就 override `isAccessibilityElement()`、`accessibilityRole()`、`accessibilityLabel()`、`accessibilityValue()`。**值改變時要 post `.valueChanged`**（協定標頭的註解明確要求）。
- 不在 view 階層裡的虛擬元素（例如 canvas 裡的點）用 `NSAccessibilityElement`，frame 用 `NSAccessibilityFrameInView` 換算。

```swift
final class LevelMeterView: NSView {
    var level: Double = 0 { didSet { needsDisplay = true
        NSAccessibility.post(element: self, notification: .valueChanged) } }
    override func isAccessibilityElement() -> Bool { true }
    override func accessibilityRole() -> NSAccessibility.Role? { .levelIndicator }
    override func accessibilityLabel() -> String? { "CPU 使用率" }
    override func accessibilityValue() -> Any? { NSNumber(value: level) }
    override func accessibilityMinValue() -> Any? { NSNumber(value: 0) }
    override func accessibilityMaxValue() -> Any? { NSNumber(value: 1) }
}
final class PillButton: NSView, NSAccessibilityButton {   // Swift 6 模式要寫 @preconcurrency NSAccessibilityButton
    var title = "開始"; var action: () -> Void = {}
    override var acceptsFirstResponder: Bool { true }
    override var canBecomeKeyView: Bool { true }             // 讓 Tab 走得到
    override var focusRingMaskBounds: NSRect { bounds }
    override func drawFocusRingMask() {
        NSBezierPath(roundedRect: bounds, xRadius: bounds.height/2, yRadius: bounds.height/2).fill()
    }
    override func keyDown(with e: NSEvent) { e.charactersIgnoringModifiers == " " ? action() : super.keyDown(with: e) }
    override func mouseUp(with e: NSEvent) { action() }
    override func accessibilityLabel() -> String? { title }
    override func accessibilityPerformPress() -> Bool { action(); return true }
}
```
- macOS 26 新增的 AX 常數【SDK】：`NSAccessibilityHeadingRole`、`HeadingLevelAttribute`、`LanguageAttribute`、`VisitedAttribute`、`ScrollToVisibleAction`、`BlockQuoteLevelAttribute`、`FontBold/ItalicAttribute`。

## 5. 動態內容通知【官方】
內容或版面有變化，**只要是看得見的就要通知**，否則 VoiceOver 使用者腦中的畫面會跟實際對不上。

| 情況 | SwiftUI（iOS 17／macOS 14 起，Accessibility framework，SwiftUI 已經重新匯出） | AppKit |
|---|---|---|
| 要唸一段話（同步完成、錯誤） | `AccessibilityNotification.Announcement(msg).post()` | `NSAccessibility.post(element:notification: .announcementRequested, userInfo: [.announcement:…, .priority:…])` |
| 局部版面變了 | `AccessibilityNotification.LayoutChanged(element?).post()` | `.layoutChanged` |
| 換成新畫面、大面積內容換掉 | `AccessibilityNotification.ScreenChanged(element?).post()` | 焦點移到新視窗 |
| 捲動完成 | `.PageScrolled` | — |

```swift
var msg = AttributedString("同步完成，已更新 12 筆")
msg.accessibilitySpeechAnnouncementPriority = .high   // .high 會打斷正在唸的內容，而且唸到一半不能被打斷
AccessibilityNotification.Announcement(msg).post()
```
- **連續變化的值不要每一次都廣播**。WWDC26-220 的做法是：距離上次廣播要隔夠久，**而且**值真的有變才唸。會一直變的元素加 `.updatesFrequently` trait。【官方】
- 背景刷新不能讓 VoiceOver 的閱讀位置跳回開頭；彈出 modal 時，VoiceOver 游標要移進去，**背景內容要變成讀不到**；`Esc`／`accessibilityPerformEscape` 要能關閉 modal。【官方 App Store 判準】
- 會自動消失的 toast 或 banner 要少用；真的要用，就廣播，而且停留時間要夠長，或改成手動關閉。【官方 HIG Cognitive】

## 6. 圖片與圖表【官方】
- 有意義的圖片要描述；**只描述圖片本身傳達的資訊**，旁邊的圖說 VoiceOver 會自己唸。
- 純裝飾的圖用 `Image(decorative:)` 或 `.accessibilityHidden(true)`（實測：兩種都會從樹裡消失）。
- 圖表：
  - 標題和副標題直接講出重點。
  - Swift Charts 內建 Audio Graphs，每個 mark 也有預設元素。
  - 自己畫的圖表用 `accessibilityChartDescriptor(_:)`，或至少給一段完整的文字替代。
  - label 寫**實際數值和脈絡**（日期、地點），不寫主觀詞（「急遽」「幾乎」），**不描述顏色**（不要寫「紅線」，要寫這條線代表什麼）。
  - 軸和刻度的可見文字要對 VoiceOver 隱藏。
  - 可以互動的圖表，鍵盤和切換控制也要能操作（`accessibilityRespondsToUserInteraction`）。
  - 重要資訊不能只有互動之後才看得到。

## 7. macOS 鍵盤與焦點

### 7.1 兩個不同的系統設定【官方 SDK 標頭＋HIG】
| 設定 | 位置 | 效果 | 讀取 |
|---|---|---|---|
| **鍵盤導覽**（Keyboard navigation） | 系統設定 › 鍵盤 | 開啟時 Tab 會走到**所有**控制項（按鈕、核取方塊）；關閉時 Tab 只走文字欄位和列表 | `NSApp.isFullKeyboardAccessEnabled`（名字取得很糟，其實是這個設定；不支援 KVO，每次直接讀） |
| **全面鍵盤操控**（Full Keyboard Access） | 系統設定 › 輔助使用 › 鍵盤 | 無障礙功能：焦點有高亮外框，可以操作所有 UI、做手勢 | 沒有公開 API |

- HIG：iPadOS／macOS 有全面鍵盤操控，所以 **app 只需要讓「內容元素」（列表項目、文字欄位、搜尋欄）可以取得焦點，按鈕、滑桿、開關這類控制項交給系統處理**，不要自己做一套控制項的鍵盤導覽。
- **Tab 在焦點群組之間移動，方向鍵在群組內移動**；順序是從前到後、由上到下。
- 焦點外觀：文字欄位和搜尋欄用 focus ring，列表和集合用整列高亮（強調色背景＋白字）。
- 不要覆寫系統快捷鍵（Control‑F1～F3、⌘F5 這些是無障礙會用到的）。【官方 HIG Keyboards】

### 7.2 SwiftUI 焦點 API【SDK】
| API | 版本 | 用途 |
|---|---|---|
| `@FocusState`＋`.focused(_:equals:)` | macOS 12／iOS 15 | 用程式控制焦點；送出後跳到下一欄 |
| `.defaultFocus(_:_:priority:)` | macOS 13／iOS 17 | 視窗第一次出現時的預設焦點；`.userInitiated` 連使用者導覽時也套用 |
| `.focusable(_:)` | macOS 12／iOS 17 | 讓自訂 view 可以取得焦點 |
| `.focusable(interactions: .activate / .edit)` | macOS 14／iOS 17 | 只參與「啟動」類的焦點（按鈕型）或「編輯」類（文字型） |
| `.focusSection()` | **只有 macOS 13＋／tvOS** | 讓 Tab 先走完這一區的子元素，再往下一區；方向鍵也能把焦點導進這一區 |
| `.onKeyPress` | macOS 14／iOS 17 | 自訂按鍵處理（空白鍵啟動等） |
| `.focusEffectDisabled()` | macOS 14 | 自己畫焦點樣式時，把系統的關掉 |
| `.accessibilityDefaultFocus(_:_:)` | **26** | VoiceOver 游標的預設位置（這是另一套 `AccessibilityFocusState`，跟鍵盤焦點分開） |

```swift
// 表單：預設焦點＋Return 跳下一欄＋預設按鈕
Form {
    TextField("帳號", text: $account).focused($focus, equals: .account)
    SecureField("密碼", text: $password).focused($focus, equals: .password).onSubmit(signIn)
    Button("登入", action: signIn).keyboardShortcut(.defaultAction)
}
.defaultFocus($focus, .account)

// 自訂可點的卡片：鍵盤、滑鼠、VoiceOver 三條路都要通
Text(title).padding(8)
    .background(RoundedRectangle(cornerRadius: 8, style: .continuous)
        .strokeBorder(focused ? Color.accentColor : .clear, lineWidth: 2))
    .focusable(interactions: .activate).focused($focused)
    .onKeyPress(.space) { open(); return .handled }
    .onTapGesture(perform: open)
    .accessibilityElement().accessibilityLabel(title)
    .accessibilityAddTraits(.isButton)
    .accessibilityAction { open() }
```
- AppKit Tab 順序：`nextKeyView` 串成迴圈，或是 `window.autorecalculatesKeyViewLoop = true`。自訂 view 要 `acceptsFirstResponder`＋`canBecomeKeyView`，並畫出 focus ring（`focusRingMaskBounds`、`drawFocusRingMask`）。【SDK】

## 8. 選單列 app 與浮動面板
- **⚠ 與官方文件矛盾（官方說標題會成為名稱，未開 VoiceOver 驗證）。實測（macOS 27，讀 AX 樹）：`MenuBarExtra("CPU 溫度", systemImage: "thermometer.medium")` 的第一個參數「CPU 溫度」不會變成狀態列按鈕的無障礙標題**。VoiceOver 拿到的是 SF Symbol 的自動描述「指示中等溫度的溫度計」。`Label("溫度監控", systemImage:)` 也一樣，會變成「指向中刻度的儀表」。**要用 `label:` closure，在 Image 上加 `.accessibilityLabel("風扇守門員")`，才會生效**：
  ```swift
  MenuBarExtra { MenuContent() } label: {
      Image(systemName: "fanblades").accessibilityLabel("風扇守門員")
  }
  ```
  AppKit 的做法是設定 `statusItem.button?.image?.accessibilityDescription`，或 `button.setAccessibilityLabel(_:)`。【實測＋SDK】
- 狀態列圖示如果會表達狀態（溫度高低），**狀態也要放進 label 或 value**，例如「CPU 溫度，88 度，過熱」，並在狀態改變時更新。【推論，依 §2】
- 浮動 `NSPanel`（`.nonactivatingPanel`）【推論，未用 VoiceOver 實測】：
  - 不會變成 key window 的面板，鍵盤和 VoiceOver 都很難進去。
  - 要提供一個選單列指令或快捷鍵，把面板叫到前面並設成 key（override `canBecomeKey` 回傳 true，或用 `becomesKeyOnlyIfNeeded`）。
  - 面板要設 `title`，這樣 VoiceOver 的視窗清單裡才有名字。
  - 關閉鍵要支援 `Esc`（`cancelOperation(_:)`）。
- 選單列 app 的所有主要功能，**都要能從選單項目操作**。選單本身是系統元件，VoiceOver 和鍵盤免費支援；自訂的 SwiftUI 視窗內容就要自己檢查。

## 9. 文字大小（macOS 與 iOS 不一樣）

### 9.1 macOS：第三方 app 的 SwiftUI 不會跟著系統「文字大小」變【官方＋實測】
- macOS 14 起，系統設定 › 輔助使用 › 顯示器有「文字大小」，**但只作用在列出的 Apple app 和系統元件**：Finder、郵件、訊息、備忘錄、提醒事項、行事曆、書籍、股市、天氣、日記、放大鏡、輔助使用閱讀器（作者環境 `com.apple.universalaccess` 的 `FontSizeCategory` 清單就是這些）。
- **實測**：作者環境全域設成 XXL 時，第三方 SwiftUI app 讀到的 `dynamicTypeSize` 還是 `.large`，`.body` 還是 13pt；**強制寫 `.dynamicTypeSize(.accessibility5)` 字也不會變大，`@ScaledMetric` 也不會縮放**。Apple 文件原文：「On macOS, this value cannot be changed by users and does not affect the text size.」
- macOS 26／27 SDK **都沒有**新的文字大小 API（AppKit 沒有 content size category），WWDC25／26 也沒有宣布。App Store 的 Larger Text 標籤明確寫「**All except Mac**」，Mac app 不能勾這一項。
- HIG 還是要求「理想上讓人能把文字放大到至少 200%」，可以用「自訂 UI」達成。**Mac 上要做文字放大就要自己做**：在 app 內提供字級設定（`@AppStorage` 存倍率，然後 `.font(.system(size: 13 * scale))`，或 `⌘+`／`⌘-`），閱讀型內容特別需要。系統的「縮放」和「游標懸停文字」不算 app 有支援（App Store 判準原文）。

### 9.2 iOS：Dynamic Type 版面調適【官方】
- 目標是 AX5 下不重疊、不嚴重截斷，資訊層級不變；**AX3 大約是 200%**，AX5 超過 300%（App Store 判準）。
- 橫排改直排：
  - 用 `dynamicTypeSize.isAccessibilitySize` 切換 `AnyLayout(HStackLayout…)`／`AnyLayout(VStackLayout…)`（切換時保留 view 身分，動畫比較順）。
  - 或用 `ViewThatFits(in: .horizontal)`：依序放「理想版」到「退化版」，挑第一個放得下的。
- 能 scale 的非文字尺寸用 `@ScaledMetric(relativeTo:)`；SF Symbols 會自己跟著 Dynamic Type 縮放。
- **`.dynamicTypeSize(...DynamicTypeSize.xxxLarge)` 這類限制範圍**：只用在實在沒空間的小元件（徽章、tab bar、tool bar 圖示），**而且要搭配 Large Content Viewer**。**不要加在整個畫面或 root view**，那等於把無障礙字級整個關掉。範圍會夾住寫在它**外層**的設定值，所以 range modifier 要寫在 modifier 鏈的前面（最內層）（文件範例：先 range 再 `.xLarge`，結果是 `.large`）。
- Large Content Viewer：`.accessibilityShowsLargeContentViewer()` 或帶 content 的版本，給**必須維持小尺寸**的元件用。**不能拿它取代 Dynamic Type**（文件原文）。

```swift
Text("\(count)").font(.caption2.bold()).padding(4).background(.red, in: Capsule())
    .dynamicTypeSize(...DynamicTypeSize.xxxLarge)                 // 徽章不跟到 AX 級
    .accessibilityShowsLargeContentViewer { Label("\(count) 則未讀", systemImage: "envelope.badge") }
```

## 10. 語音控制（Voice Control）【官方】
- 使用者說「Show names」會看到每個元素的名稱，說「點一下 ＜名稱＞」來操作。**label 必須跟畫面上看得到的文字一致**。按鈕寫「結束通話」，label 卻是「離開通話」，使用者就叫不到它（App Store 判準原文舉的例子）。
- 圖示按鈕的 label 用使用者會直覺說出的詞；同義詞放進 `accessibilityInputLabels`，**依重要性排序，第一個跟可見文字或 label 一致**。**全面鍵盤操控也會用 input labels**（文件原文）。
  ```swift
  Button { share() } label: { Image(systemName: "square.and.arrow.up") }
      .accessibilityLabel("分享")
      .accessibilityInputLabels(["分享", "共享", "Share"])   // 實測：macOS 輸出為 AXUserInputLabels
  ```
  AppKit 對應 `accessibilityUserInputLabels()`（macOS 14）；UIKit 是 `accessibilityUserInputLabels`。
- label 很長時（例如「刪除 CPU 感測器」），input label 補一個短的（「刪除」）。
- hover 才出現的 UI、滑動才出現的動作、拖放，都要有語音可以達成的替代方式（右鍵選單、自訂動作）。自訂文字欄位要測「選取 ⋯」「刪除那個」這類聽寫編輯指令。

## 11. 其他系統設定對照表

| 設定 | SwiftUI 環境值 | 版本／平台 | 該怎麼回應 | 證據 |
|---|---|---|---|---|
| 不以顏色來區分（Differentiate Without Color） | `accessibilityDifferentiateWithoutColor` | 全平台 | 狀態點加圖示（✓／✕）或文字；圖表加形狀、圖樣。**預設就該不只靠顏色**，這個設定是再加強 | 【官方】 |
| 粗體文字（Bold Text） | `legibilityWeight == .bold` | iOS／tvOS／watchOS；**macOS 沒有這個設定**（實測讀到 `nil`） | 系統字自動變粗；自訂字重、手畫的線條要跟著加粗 | 【官方＋實測】 |
| 按鈕形狀／顯示邊線 | `accessibilityShowBorders`（舊名 `accessibilityShowButtonShapes` 已 deprecated，renamed；新名 back-deploy 到 iOS 14／macOS 11） | iOS 的「按鈕形狀」；macOS 27 的「顯示邊線」 | 無邊框的文字按鈕或圖示按鈕加底線或外框 | 【SDK】 |
| 開／關標籤（On/Off Labels） | **沒有 SwiftUI 環境值**；UIKit `UIAccessibility.isOnOffSwitchLabelsEnabled`＋`onOffSwitchLabelsDidChangeNotification` | iOS | 標準 `Toggle` 自動處理；自己畫的開關要加 I／O 標示 | 【SDK】 |
| 反相顏色（Invert Colors／Smart Invert） | `accessibilityInvertColors`；照片、影片、頭像用 `.accessibilityIgnoresInvertColors()` | iOS 14／macOS 11 | 照片、地圖、影片不要被反轉 | 【SDK】 |
| 偏好交叉淡入轉場 | `accessibilityPrefersCrossFadeTransitions` | **26.4** | 位移、縮放轉場改 `.opacity` | 【SDK】 |
| 降低亮部效果 | `accessibilityReduceHighlightingEffects` | **26.4** | 按鈕高亮、閃光、發光效果降到最低 | 【官方】 |
| 減弱閃爍 | `accessibilityDimFlashingLights` | iOS 17／macOS 14 | 影片或動畫中的閃光要減弱 | 【SDK】 |
| 自動播放動態圖片 | `accessibilityPlayAnimatedImages` | iOS 17／macOS 14 | false 時 GIF 或 APNG 停在第一格 | 【SDK】 |
| VoiceOver／切換控制開著 | `accessibilityVoiceOverEnabled`、`accessibilitySwitchControlEnabled` | macOS 12／iOS 15 | **只用來調整行為**（例如不要自動隱藏控制項），**不要拿來換一套 UI** | 【SDK】 |
| AppKit 對應 | `NSWorkspace.shared.accessibilityDisplayShould{IncreaseContrast, DifferentiateWithoutColor, ReduceTransparency, ReduceMotion, InvertColors}`、`isVoiceOverEnabled`；變動時收到 `NSWorkspace.accessibilityDisplayOptionsDidChangeNotification` | macOS | — | 【SDK】 |

```swift
struct StatusBadge: View {
    let ok: Bool
    @Environment(\.accessibilityDifferentiateWithoutColor) private var noColor
    @Environment(\.accessibilityShowBorders) private var showBorders
    @Environment(\.colorSchemeContrast) private var contrast
    var body: some View {
        HStack(spacing: 4) {
            Circle().fill(ok ? .green : .red).frame(width: 8, height: 8)
            if noColor { Image(systemName: ok ? "checkmark" : "xmark") }
            Text(ok ? "正常" : "異常")          // 文字本身就讓狀態不只靠顏色
        }
        .padding(.horizontal, 6)
        .overlay { if showBorders || contrast == .increased { Capsule().strokeBorder(.secondary) } }
    }
}
```

## 12. 自動化稽核與 Accessibility Nutrition Labels

### 12.1 `performAccessibilityAudit`（XCUITest）【官方＋SDK】
- `XCUIApplication.performAccessibilityAudit(for:_:)`：iOS 17／macOS 14 起，Xcode 15 起（目前文件與標頭歸在 **XCUIAutomation** framework，文件標 Xcode 16.3）。發現問題測試會**自動失敗**，不用寫 assert。**只檢查目前畫面上的元素**，每個畫面都要各跑一次。
- 稽核類型（**平台不同，類型不同；寫錯平台的類型會編譯不過**，實測 macOS 上用 `.dynamicType` 會報錯）：

| 類型 | 平台 | 檢查什麼 |
|---|---|---|
| `.sufficientElementDescription` | 全平台 | 元素有沒有具體描述的 label |
| `.contrast` | 全平台 | 重疊元素之間的色彩對比 |
| `.hitRegion` | 全平台 | 可點範圍是否太小 |
| `.elementDetection` | 全平台 | 有沒有內容沒被暴露成元素 |
| `.dynamicType`、`.textClipped`、`.trait` | iOS／tvOS／watchOS | 是否支援 Dynamic Type、放大後文字是否被截斷、trait 需要的屬性是否齊全 |
| `.action`、`.parentChild` | **macOS** | 動作對這種元素是否有效、父子關係是否互相指向（parent 列出 child，child 的 parent 也要是它） |

```swift
@MainActor func testMainWindowAudit() throws {
    let app = XCUIApplication(); app.launch()
    try app.performAccessibilityAudit(for: [.sufficientElementDescription, .contrast, .hitRegion,
                                            .elementDetection, .action, .parentChild]) { issue in
        // 回傳 true = 忽略這個問題。只忽略確認過的誤報，並寫註解說明原因
        issue.auditType == .contrast && issue.element?.identifier == "decorativeWatermark"
    }
}
```

### 12.2 Accessibility Inspector【官方】
- 開啟方式：Xcode › Open Developer Tool › Accessibility Inspector，左上角的 target 選你的 app。
- **Inspection**：指到元素看 label、value、trait、動作。可以用來確認 §2 的實測現象，例如 SF Symbol 的自動描述、help 跟 label 的差別。
- **Audits**：
  - 全平台項目：Element description、Hit region、Contrast、Element detection。
  - 只有 macOS 的項目：Parent/child、Action。
  - 結果會附 Fix suggestion，可以擷取問題元素的截圖，也可以 File › Save Audit Report As⋯ 匯出成 HTML。
- **Settings**：直接切換反相顏色、增加對比、減少透明度、減少動態效果、全面鍵盤操控、不以顏色來區分等設定（會改到目標裝置的系統設定，**測完要記得切回來**）。另有色彩對比計算器（⌥⌘C）。

### 12.3 App Store「Accessibility Nutrition Labels」（2025 起）【官方】
- 目前是**自願填寫，之後會改成送審必填**（還沒公布時程）。iOS／macOS 26 以後的 App Store 產品頁會顯示；使用者可以用「VoiceOver 筆記 app」這類詞搜尋。
- **判準只有一條：所有「常見任務」都能只靠這個功能完成**，才可以勾。常見任務包括：
  1. 主要功能（商店頁、截圖宣傳的那些功能）
  2. 首次啟動流程
  3. 登入（含註冊、忘記密碼）
  4. 購買
  5. 設定
  6. 另外也要算進去：widget、通知、預設載入畫面
- 各項判準摘要：

| 標籤 | Mac 可勾？ | 關鍵判準 |
|---|---|---|
| VoiceOver | ✓ | label 簡潔、不含類型或狀態；看得到的文字都唸得出來；順序合理、不跳過也不繞圈；modal 背景讀不到、`Esc` 可以關閉；右鍵選單和長按要有自訂動作；圖表有替代文字 |
| Voice Control | ✓（Apple TV、Watch 不適用） | label＝看得到的文字；所有互動用語音就能做到；自訂文字欄位支援聽寫編輯 |
| Larger Text | **✗（All except Mac）** | 放大到 ≥200%；自己做 app 內字級也算；系統縮放**不算** |
| Dark Interface | ✓ | 常見任務的所有畫面都有深色模式（自己做的深色配色也算） |
| Differentiate Without Color Alone | ✓ | 不只靠顏色區分重要資訊 |
| Sufficient Contrast | ✓ | 文字 ≥4.5:1、**非文字的控制項和狀態 ≥3:1**；可以靠「增加對比」設定達成；淺色和深色都要測；建議同時開粗體、增加對比、減少透明度一起測 |
| Reduced Motion | ✓ | 開啟設定後，動畫要減少或改變 |
| Captions／Audio Descriptions | ✓ | 常見任務裡的影音要有同步字幕、口述影像 |

- VoiceOver 和 Voice Control **不能用自訂實作取代**，要走原生 API；其他標籤可以自己實作（例如自訂的深色配色）。【官方】
- 標得不實，App Review 可以要求修改（Guideline 2.3）。

## 13. 坑
1. 圖示按鈕只加 `.help()` 沒加 label：VoiceOver 唸的是 SF Symbol 自動描述（「齒輪形狀」），不是功能名稱。
2. `MenuBarExtra("標題", systemImage:)` 的標題在 AX 樹實測中沒有變成狀態列按鈕的 label（官方文件說會，未開 VoiceOver 驗證；保險起見一律加）。要用 `label:` closure，在 Image 上加 `.accessibilityLabel`。
3. label 裡寫「按鈕」「圖示」「已勾選」，或 hint 寫「點兩下以⋯」。
4. 用 `.combine` 合併的列，狀態只靠圖示表達時，圖示資訊會被丟掉。要改用 `.ignore`，value 自己寫。
5. 形狀 view 單獨當元素：角色是 AXUnknown，value 沒有輸出（實測）。
6. rotor 的 `ForEach` 裡寫 `if`：target 26 會編譯失敗或出現警告（Optional conformance 要 27 才有）。
7. 自訂動作只宣告沒排序：macOS 呈現順序跟宣告順序相反。
8. 右鍵選單、hover 按鈕、滑動動作沒有同時提供成自訂動作，VoiceOver 和語音控制都做不到。
9. 可見文字跟 label 不一致（語音控制叫不到）；input labels 第一個沒放可見文字。
10. 以為 macOS 的 SwiftUI 會跟著系統「文字大小」或 `dynamicTypeSize` 放大。不會，要自己做 app 內字級。Mac app 不能勾 Larger Text 標籤。
11. 在 root view 加 `.dynamicTypeSize(...(.large))` 鎖字級；或用 Large Content Viewer 取代 Dynamic Type。
12. 以為 `NSApp.isFullKeyboardAccessEnabled` 就是輔助使用裡的「全面鍵盤操控」。它其實是「鍵盤導覽」設定。
13. 自訂 NSView 可以點，但沒有 `canBecomeKeyView`／focus ring／空白鍵啟動（Tab 走不到）；值改變沒 post `.valueChanged`。
14. 靠 `accessibilityVoiceOverEnabled` 換一整套 UI；或頻繁廣播數值變化。
15. 在 macOS 寫 `performAccessibilityAudit(for: .dynamicType)`（編不過）；用 closure 把整類問題忽略掉；以為稽核全部通過就是無障礙。
16. `accessibilityShowButtonShapes` 已 deprecated，改用 `accessibilityShowBorders`。
17. 在 Simulator 上測 VoiceOver 或語音控制（不支援）；用 Accessibility Inspector 切了設定之後沒切回來。
