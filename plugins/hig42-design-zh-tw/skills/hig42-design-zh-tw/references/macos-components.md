# 元件與互動模式（macOS 為主，含 iOS、動畫、SF Symbols）

> Xcode 27 SDK 核對、HIG 51 頁。來源清單見 repo 的 `SOURCES.md`
> 中文用語另見 `zh-tw-writing.md`。

## 目錄
1. 視窗、split view、toolbar
2. 選單列
3. Menu bar extra ★
4. Panel、popover、sheet、alert
5. Settings 視窗 ★
6. 控制項
7. 鍵盤、拖放、undo
8. 空狀態、載入、錯誤、啟動
9. 動畫
10. SF Symbols
11. iOS 元件
12. 程式碼範本
13. 坑

---

## 1. 視窗、split view、toolbar【官方】

- 不要自製視窗外框與紅黃綠按鈕。對使用者一律稱「視窗」。
- 視窗有 main／key／inactive 三態，自訂視窗要跟著切外觀。
- 關鍵資訊與動作不要放 bottom bar 或 sidebar 底部（視窗常被拖到螢幕下緣）。
- 不要預設開新視窗；可提供「在新視窗打開」。
- **Split view**：每個通往 detail 的窗格要持續高亮目前選取；設合理最小／最大寬度；允許隱藏窗格並提供多種叫回方式（toolbar 按鈕＋選單指令＋快捷鍵）；整個 split view 上方只一個標題；補充資訊優先用 inspector 而不是開新視窗。
- **Sidebar**：最多兩層，超過改三欄；圖示預設跟隨 accent color。macOS 27 起 sidebar 延伸到視窗邊緣、選取用 semibold、圖示恢復顏色。
- **Toolbar**：
  - **每個 toolbar 項目都要有對應的選單列指令**（toolbar 可被隱藏或自訂）。
  - 用無外框 SF Symbol；最多約 3 組；主要動作用 `.prominent`，只一個，放尾端。
  - 視窗標題要有用、**不要用 app 名稱**、15 字元以內。
  - 長時間使用的 app 可讓使用者自訂 toolbar。
- 全螢幕：用系統的，讓使用者決定進出（綠色按鈕、顯示方式選單、⌃⌘F）。
- 啟動時還原上次狀態（捲動位置、視窗、分頁）。
- SwiftUI：`.windowToolbarStyle(.unified)`、`.navigationSubtitle(_:)`、`.windowResizability(.contentMinSize)`、`.restorationBehavior(.disabled)`（診斷類視窗）。
- 不必要阻擋 app 結束的 sheet／modal，設 `NSWindow.preventsApplicationTerminationWhenModal = false`。【官方 WWDC26】

## 2. 選單列【官方】

順序：Apple → **App → 檔案 → 編輯 → 格式 → 顯示方式 → 自訂選單 → 視窗 → 輔助說明** → menu bar extras。

- 項目不可用時**變暗，不要隱藏**（context menu 相反）。
- 自訂指令一定要進選單列（才找得到、能配快捷鍵、全面鍵盤操控可用）。自訂選單放在顯示方式與視窗之間。
- App 選單：關於 → 設定⋯（⌘,）→ 自訂 app 設定 → 服務 → 隱藏（⌘H）／隱藏其他（⌥⌘H）／顯示全部 → 結束（⌘Q）。「關於」不含版本號。
- 編輯選單：還原／重做要標明對象（「還原輸入」）；刪除不要叫「清除／抹除」。
- 顯示方式選單：即使只有一個視窗也要有；「顯示／隱藏工具列」這類項目要反映當下狀態。
- 視窗選單：即使只有一個視窗也要有（縮到最小 ⌘M、縮放是給全面鍵盤操控用的）；開啟中視窗清單**不列 panel**。
- **選單項目圖示（2026-06 HIG 更新）**：節制使用，只給常用動作、關鍵功能、檔案位置、連接裝置、使用者內容；**同一組要嘛全有要嘛全沒有**；找不到明確圖示就不放。macOS 27 預設隱藏選單圖示，要顯示用 `.labelStyle(.titleAndIcon)`。
- SwiftUI：`CommandGroup(replacing:/before:/after:)`、`CommandMenu("名稱")`（自動插在顯示方式與視窗之間）；有 `Settings` scene 時自動有「設定⋯」＋ ⌘,。

## 3. Menu bar extra ★

### 3.1 HIG 規則【官方】
1. 圖示用 **SF Symbol 或 template image**（黑＋透明定義形狀），系統依選單列深淺與選取狀態上色。**不要用彩色 PNG。**
2. 選單列高 24pt（有瀏海的 MacBook 選單列會跟著瀏海變高，版面不要寫死）；圖示尺寸 HIG 沒給，業界慣例 16–18pt 高。用 SF Symbol 就交給系統。
3. **點擊預設出選單**；功能複雜到選單裝不下才用視窗樣式。
4. **讓使用者決定要不要放在選單列**：設定裡放「在選單列中顯示」開關。
5. **不要依賴它一定存在**（空間不夠時系統會隱藏）。
6. **主要功能也要能從別處用到**（主視窗、設定、Dock 選單）。

### 3.2 API
- SwiftUI `MenuBarExtra(isInserted:)`（macOS 13+）；`.menuBarExtraStyle(.menu)`（預設）或 `.window`（資訊密集的監控面板才用）。
- 純選單列 app：Info.plist `LSUIElement = YES`。**使用者把 extra 從選單列移除時，純選單列 app 會被系統自動終止**；下次從 Finder 打開時要開設定視窗讓人加回來。
- **VoiceOver 名稱**：`MenuBarExtra` 的標題是否會成為選單列按鈕的無障礙名稱有矛盾（官方文件說會，作者環境讀 AX 樹實測沒有，尚未開 VoiceOver 驗證）。保險做法：用 `label:` closure 並在 Image 上加 `.accessibilityLabel`。見 `accessibility.md`。
- AppKit `NSStatusItem`：`button.image` 設 `isTemplate = true`，並設 `button.setAccessibilityLabel(...)`。
- **macOS 27 新增** `expandedInterfaceDelegate`／`expandedInterfaceSession`：自己彈視窗（非 NSMenu）的 status item，要在 `statusItem(_:didBeginExpandedInterfaceSession:)` 顯示視窗、`statusItemDidEndExpandedInterfaceSession(_:animated:)` 收起，**不要在 button action 裡自己 toggle**，這樣鍵盤導覽和選單追蹤才正常；使用者用別的方式關掉時呼叫 `expandedInterfaceSession?.cancel()`。SwiftUI MenuBarExtra 已處理。【SDK】
- 圖示可用 variable value（`thermometer.variable`）或 symbol effect 表達狀態，但要尊重 Reduce Motion，不要持續動畫干擾。

## 4. Panel、popover、sheet、alert

### 4.1 Panel【官方】
- 用途：跟目前內容／選取相關的快速控制（inspector 用 panel；內容固定的 Info 視窗用一般視窗）。
- 優先放簡單調整控制（slider、stepper），避免要打字的。
- **要有標題列**，標題用名詞（「字體」「檢閱器」）。
- **app 變 active 時帶到前面，app inactive 時隱藏所有 panel**；不要列進視窗選單；一般不給最小化按鈕。
- HUD 風格只用在媒體類 app 或標準 panel 會擋住關鍵內容時；保持小、少用色。
- SwiftUI `UtilityWindow`（macOS 15+）：預設 `.floating`、app inactive 時隱藏、Esc 關閉、不可最小化、自動加進顯示方式選單。
- AppKit：`NSPanel` style mask `.nonactivatingPanel`（點了不啟動 app）、`.utilityWindow`、`.hudWindow`；`isFloatingPanel`、`becomesKeyOnlyIfNeeded`、`hidesOnDeactivate`。
- **整窗玻璃的 HUD 型面板**（macOS 26+）：用 borderless＋`.clear` 玻璃＋tint，不用 `.titled`（會多一層系統外框），做法與實測值見 `liquid-glass.md` §3.1a。標準工具 panel 仍照 HIG 保留標題列。
- **常駐置頂的監控面板屬刻意偏離 HIG**（HIG 要求 app inactive 時隱藏 panel）。要做就補：可關閉、可選要不要置頂、nonactivating 不搶焦點、保持小、少色，並在交付說明寫明。

### 4.2 Popover【官方】
少量內容；點外面自動關；**自動關閉時保留使用者的修改**（只有按取消才丟）；一次只一個、不要疊；**不要用 popover 發警告**；macOS 可讓它拖出成獨立 panel。

### 4.3 Sheet【官方】
一次只一個；有「完成」就配「取消」；macOS sheet 開著時使用者應能操作其他視窗；**需要反覆輸入並看結果（尋找與取代）用 panel 不用 sheet**。

### 4.4 Alert【官方】
- **少用**：純告知改在情境中顯示；常見、可還原的破壞性動作（刪信、丟檔）不需要 alert；**啟動時不要跳 alert**。
- 標題具體說明發生什麼，不要「錯誤」「Error 329347」；最多兩行。完整句用句號，片語不加標點。
- 說明文字短、完整句、不解釋按鈕。
- 按鈕：一兩個字的動詞，呼應標題；**只有純資訊 alert 才用「好」**；避免「是／否」；**取消一律叫「取消」**；最多三顆。
- 位置（macOS）：default 在**右（尾端）**，取消在左。
- **destructive 樣式只給使用者「沒有刻意選擇」的破壞性後果**；使用者刻意選「清空垃圾桶」，確認鈕不標紅（按 Return 直接確認比較重要）。
- 有破壞性動作就要有取消；**取消不可當 default**；要逼人讀內容就不設 default。
- Esc 或 ⌘. 取消。警告三角圖示只在可能意外丟資料時用。
- SwiftUI：alert 沒有預設取消，要自己放 `role: .cancel`；default 用 `.keyboardShortcut(.defaultAction)`；`.dialogSeverity(.critical)`；「不要再詢問」用 `.dialogSuppressionToggle(_:isSuppressed:)`。`ButtonRole.confirm`／`.close` 是 macOS 26 新增。

## 5. Settings 視窗 ★【官方 HIG Settings】

- 預設值要讓多數人不用改；設定越少越好；**不要重複系統設定**（深色模式、無障礙）；能自己偵測的不要問。
- 跟任務相關的選項（排序、篩選、顯示／隱藏）放在任務畫面，不放設定。
- **App 選單要有「設定⋯」＋ ⌘,；不要在視窗 toolbar 放齒輪設定鈕。**
- **設定視窗的最小化與放大按鈕要變暗**；視窗大小跟著目前分頁內容。
- 分頁 toolbar：不可自訂、永遠可見、標示目前分頁。
- **視窗標題跟著目前分頁變**；只有一頁時標題為「App名稱設定」。
- **重開時回到上次看的分頁**。
- 標籤寫清楚「開啟時會做什麼」；要引導人去某設定時給直接按鈕，不要描述路徑。
- **改了就生效，不放「好／套用／取消」**：現行 HIG 沒明文，但 Apple 範例用 `@AppStorage` 直接綁定、系統設定也即時生效、舊版 HIG 明寫。【推論＋舊版官方】
- `.formStyle(.grouped)` 做成系統設定的樣子；**grouped form 內的開關用 mini switch**（`.toggleStyle(.switch).controlSize(.mini)`）。【官方 HIG Toggles】
- 從 app 內開設定：`SettingsLink`、`@Environment(\.openSettings)`（macOS 14+）。

## 6. 控制項【官方】

### 6.1 按鈕
- 自訂按鈕要有按下狀態。
- **每畫面最多 1–2 個 prominent**；用樣式不用大小區分重要性。
- **破壞性動作永遠不當 primary**，即使最可能被選。
- macOS：**會開另一個視窗／view 的按鈕，標題加「⋯」**；square（+／−）按鈕只放圖示、放在 view 裡；Help 按鈕每視窗最多一個、放左下或右下；按鈕順序確認在右、取消在其左。
- 圖示按鈕要有 tooltip（`.help("...")`）和 accessibility label；有文字的按鈕通常不需要 tooltip。

### 6.2 開關類（macOS）
| 元件 | 何時用 |
|---|---|
| Checkbox | **預設選擇**；有階層（子設定縮排）時用；可有 mixed 狀態 |
| Switch | 想**強調**的設定、控制一整組；grouped form 內用 mini；**已經用 checkbox 的地方不要換成 switch** |
| Radio | 2–5 個互斥選項；超過約 5 個改 pop-up |
- 這三種都只放在內容區，不放 toolbar。
- iOS：switch 只用在 list row。

### 6.3 其他
- **Segmented control**：選取型與動作型不混；文字或圖示擇一；寬介面約 5–7 段；**macOS 主視窗切換 view 用 tab view，不用 segmented**。
- **Pop-up vs pull-down**：pop-up 放**互斥選項**、顯示目前值；pull-down 放**動作**、顯示固定標題。常見錯誤是剛好相反。
- **Slider**：最小值在左；macOS 即時回饋；標籤 sentence case＋冒號。**Stepper**：Shift-click 一次改 10 倍。**Disclosure**：一個 view 最多一個 disclosure button。
- **Table／outline**：欄標題名詞、不加冒號；點欄標題排序；可調欄寬；記住展開狀態；截斷用中間省略保留頭尾。
- **Context menu**：只放最相關的；**所有項目也要在選單列找得到**；**不可用的項目隱藏而不是變暗**（macOS 剪下／拷貝／貼上例外）；**不要在 context menu 顯示快捷鍵**。

## 7. 鍵盤、拖放、undo【官方】

- Focus：text field 用 focus ring；list 用整列高亮；**不要在使用者沒互動時移動焦點**。
- AppKit：開 `NSWindow.autorecalculatesKeyViewLoop`；**不要 override `mouseDown`** 做選取／右鍵／拖曳，用 gesture recognizer 或 macOS 27 的 control events；兄弟 view 重疊會默默吃掉點擊。【官方 WWDC26】
- **快捷鍵**：不要挪用標準快捷鍵；⌘ 為主、⇧ 為輔、⌥ 少用、**避免 ⌃**；列示順序 **⌃⌥⇧⌘**；⇧⌘Z 只能跟 undo／redo 有關。
- 常用標準：⌘, 設定、⌘Q 結束、⌘W 關閉、⌘M 縮到最小、⌘N 新增、⌘O 打開、⌘S 儲存、⌘Z／⇧⌘Z、⌘F 尋找、⌘G 找下一個、⌃⌘F 全螢幕、⌥⌘T 顯示／隱藏工具列、⌥⌘I 檢閱器、Esc 取消、⌘. 取消操作。
- **拖放**：一定要有替代的選單指令；同容器移動、跨容器拷貝、按 Option 強制拷貝；拖放要可 undo。
- **Undo**：放編輯選單最上方；標明要還原什麼；**不要限制次數**；不需要時別放 undo 按鈕。

## 8. 空狀態、載入、錯誤、啟動【官方】

- **空狀態**：給清楚的下一步，盡量附按鈕；用 `ContentUnavailableView`；搜尋無結果用 `ContentUnavailableView.search(text:)`。
- **載入**：盡快顯示東西（placeholder）；超過一兩秒用 progress indicator；**能用確定進度就用**；進度要準；**避免「載入中⋯」這種空泛描述**，寫具體在做什麼；可中斷就給取消；**不要從 spinner 切成進度條**；macOS 背景作業或空間小用 spinner，通常不加標籤。
- **錯誤**：顯示在問題旁；不責怪；說明怎麼修；**不要「oops」「哎呀」**；**不要用「我們」**；不要「名稱無效」這種機器話。
- **啟動**：立即啟動；iOS launch screen 幾乎等同第一個畫面、不放文字或 logo。
- **Onboarding**：優先情境式提示，不要一次性長流程；可跳過；延後非必要設定；需要權限時說明原因。

## 9. 動畫

### 9.1 原則【官方 HIG Motion】
有目的才加；**頻繁互動不加動畫**（系統元件已有細微動畫）；讓人能中斷；不能是傳達重要資訊的唯一方式；方向符合手勢；trackpad 上系統效果會比觸控收斂。

### 9.2 Reduce Motion【官方】
`@Environment(\.accessibilityReduceMotion)` 為 true 時：收緊 spring 減少彈跳、位移轉場改淡入淡出、避免 z 軸深度動畫和模糊進出。

### 9.3 SwiftUI 預設值【SDK：從 SwiftUICore.swiftinterface 內聯實作讀出】
| API | duration | bounce |
|---|---|---|
| `.smooth` | 0.5 | 0 |
| `.snappy` | 0.5 | 0.15 |
| `.bouncy` | 0.5 | 0.3 |
| `.spring` | 0.5 | 0 |
| `.interactiveSpring` | 0.15 | 0.15 |
| `.default` | iOS 17／macOS 14 起為 spring(response 0.55, damping 1.0) | — |

**選用**：一般狀態切換、版面變化用 `.smooth`（最像系統）；俐落的小元件用 `.snappy`；`.bouncy` 只給偶發的趣味回饋；**工具型 app 不要用 `.bouncy` 當全域預設**；監控數字每秒更新時不要每次都做彈跳。

## 10. SF Symbols

- 版本：SF Symbols 7（2025，iOS／macOS 26）加入 Draw On／Off、Variable Draw、gradient；官網現行下載檔 `SF-Symbols-27.dmg`，新符號只在 27 系統可用；macOS 27 **沒有新增 symbol effect**。【官方＋SDK】
- **Rendering mode**：monochrome、hierarchical（分層透明度）、palette（每層一色）、multicolor（內建語意色）；26+ 有 `.symbolColorRenderingMode(.gradient)`。
- **Variable value**：表達會變的量（容量、強度、進度），不要用來表達深度。`Image(systemName: "speaker.wave.3", variableValue: 0.6)`；26+ `.symbolVariableValueMode(.draw)`。
- **Effects**：Bounce（事件發生，一次性）、Pulse／Breathe（進行中）、Rotate（旋轉，例：風扇）、Variable Color（進度或活動）、Replace（換符號）、Wiggle（引起注意）、Scale（選取）、Appear／Disappear、Draw On／Off（26+）。
  - **狀態變化用一次性效果（bounce、replace）；持續中才用循環效果，狀態結束就停**；Reduce Motion 時改靜態或 replace。
- 字重要**跟相鄰文字一致**；用 `.imageScale(.small/.medium/.large)` 調強調，不破壞字重對齊。
- 變體：outline 適合 toolbar、list、與文字並排；fill 適合 iOS tab bar、swipe action、表示選取。多數情況由容器自動決定。
- **授權**：只能用在 Apple 平台上執行的 app。**不能用在網頁、HTML artifact、簡報、app icon、logo**。

## 11. iOS 元件【官方】

- Navigation：large title 幫助定位，捲動時轉標準標題。
- Toolbar：只放最重要項目；返回／關閉用系統符號，**不要寫「返回」「關閉」文字**；主要動作 `.prominent` 放尾端。
- **Tab bar**：用於導覽不是動作；各區之間保持可見；**現行 HIG 已拿掉數量上限**（舊版 3–5），只說越少越好、避免 More；**不要停用或隱藏 tab**，沒內容就說明原因；可在尾端放 search tab、可加 bottom accessory。
- **Sheet**：`.presentationDetents([.medium, .large])`；可縮放的顯示 grabber；支援下滑關閉，有未存修改時確認；單頁 sheet「取消」在左上、「完成」在右上。
- List：設定式畫面用 inset grouped（SwiftUI `Form` 在 iOS 預設即是）；鑽入用 disclosure indicator。
- Swipe actions 用 fill 符號。
- 跟刻意動作相關的選擇用 action sheet（confirmationDialog），最多 4 顆（含取消），破壞性放最上。
- Pull to refresh：也要自動定期更新；`.refreshable`。
- Search：打字即搜尋；placeholder 說明可搜什麼；iPhone 有空間就放底部。
- Haptics：用系統定義的意義；不要濫用；可關閉；`.sensoryFeedback(_:trigger:)`。

## 12. 程式碼範本（SwiftUI，macOS）

### 12.1 Menu bar extra＋使用者可移除
```swift
@main
struct MonitorApp: App {
    @AppStorage("showMenuBarExtra") private var showMenuBarExtra = true

    var body: some Scene {
        MenuBarExtra(isInserted: $showMenuBarExtra) {
            MonitorPanelView().frame(width: 320)
        } label: {
            Image(systemName: "thermometer.variable", variableValue: 0.6)
                .accessibilityLabel("CPU 溫度")   // 建議加：官方文件說標題會成為名稱，但作者環境 AX 樹實測沒有（未開 VoiceOver 驗證）
        }
        .menuBarExtraStyle(.window)   // 資訊密集才用 .window；否則省略（預設選單）

        Settings {
            SettingsView(showMenuBarExtra: $showMenuBarExtra)
        }
    }
}
```

### 12.2 Settings（分頁、grouped form、即時生效、記住分頁）
```swift
struct SettingsView: View {
    @Binding var showMenuBarExtra: Bool
    @AppStorage("settingsTab") private var tab = "general"
    @AppStorage("notifyOnHeat") private var notifyOnHeat = true

    var body: some View {
        TabView(selection: $tab) {
            Tab("一般", systemImage: "gearshape", value: "general") {
                Form {
                    Section {
                        Toggle("在選單列中顯示", isOn: $showMenuBarExtra)
                    }
                    Section("警示") {
                        Toggle("溫度過高時通知", isOn: $notifyOnHeat)
                            .toggleStyle(.switch)
                            .controlSize(.mini)
                    }
                }
                .formStyle(.grouped)
            }
            Tab("進階", systemImage: "slider.horizontal.3", value: "advanced") {
                AdvancedSettingsView()
            }
        }
        .frame(width: 460)
    }
}
```

### 12.3 NavigationSplitView＋inspector
```swift
NavigationSplitView {
    List(items, selection: $selection) { Label($0.name, systemImage: $0.symbol) }
        .navigationSplitViewColumnWidth(min: 180, ideal: 220, max: 300)
} detail: {
    DetailView(id: selection)
        .navigationTitle("裝置")
        .navigationSubtitle("3 個在線")
        .inspector(isPresented: $showInspector) {
            InspectorView(id: selection)
                .inspectorColumnWidth(min: 220, ideal: 260, max: 360)
        }
        .toolbar {
            ToolbarItem {
                Button("顯示檢閱器", systemImage: "sidebar.trailing") { showInspector.toggle() }
            }
        }
}
// Scene：.commands { SidebarCommands(); InspectorCommands() }
```

### 12.4 選單指令
```swift
.commands {
    CommandGroup(after: .appSettings) {
        Button("檢查更新⋯") { checkForUpdates() }
    }
    CommandGroup(replacing: .newItem) { }      // 不處理文件就拿掉「新增」
    CommandMenu("監控") {
        Button("立即重新整理") { refresh() }
            .keyboardShortcut("r")
        Divider()
        Toggle("暫停取樣", isOn: $paused)
            .keyboardShortcut("p", modifiers: [.command, .shift])
    }
}
```

### 12.5 Alert／confirmation dialog
```swift
.confirmationDialog("要刪除「\(name)」的所有紀錄嗎？", isPresented: $confirm) {
    Button("刪除紀錄", role: .destructive) { deleteLogs() }
    Button("取消", role: .cancel) { }
} message: {
    Text("此動作無法還原。")
}
.dialogSuppressionToggle("不要再詢問", isSuppressed: $suppress)

.alert("無法連接感測器", isPresented: $failed) {
    Button("再試一次") { retry() }
        .keyboardShortcut(.defaultAction)
    Button("取消", role: .cancel) { }
} message: {
    Text("請確認 USB 線已連接，然後再試一次。")
}
```

### 12.6 空狀態
```swift
ContentUnavailableView {
    Label("沒有裝置", systemImage: "sensor")
} description: {
    Text("連接感測器後，讀數會顯示在這裡。")
} actions: {
    Button("加入裝置⋯") { addDevice() }
}
```

### 12.7 浮動面板
```swift
// 標準工具 panel（macOS 15+）
UtilityWindow("檢閱器", id: "inspector") { InspectorView() }

// 常駐置頂監控小窗（刻意偏離 HIG，見 §4.1）
Window("溫度", id: "hud") { HUDView() }
    .windowLevel(.floating)
    .windowResizability(.contentSize)
    .restorationBehavior(.disabled)
```
```swift
// AppKit：不搶焦點的浮動 panel
let panel = NSPanel(contentRect: rect,
                    styleMask: [.titled, .closable, .utilityWindow, .nonactivatingPanel],
                    backing: .buffered, defer: false)
panel.isFloatingPanel = true
panel.becomesKeyOnlyIfNeeded = true
panel.hidesOnDeactivate = false   // 預設（也是 HIG 要求）是 app inactive 就隱藏；改掉要有理由
panel.title = "溫度"
// 整窗玻璃 HUD（macOS 26+）改用 styleMask [.borderless, .nonactivatingPanel]、backgroundColor = .clear，見 liquid-glass.md §3.1a
```

### 12.8 狀態圖示＋Reduce Motion
```swift
struct StatusIcon: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let isSyncing: Bool
    let alertCount: Int

    var body: some View {
        Image(systemName: isSyncing ? "arrow.triangle.2.circlepath" : "checkmark.circle")
            .contentTransition(.symbolEffect(.replace))
            .symbolEffect(.rotate, isActive: isSyncing && !reduceMotion)
            .symbolEffect(.bounce, value: alertCount)
            .animation(reduceMotion ? nil : .smooth, value: isSyncing)
    }
}
```

## 13. 坑
1. 主要功能只放 menu bar extra；彩色 PNG 圖示；預設就用 `.window`；沒有移除開關。
2. 設定視窗放「好／套用／取消」、可放大縮小、標題不跟分頁變、不記得上次分頁；主視窗 toolbar 放齒輪。
3. Toolbar 項目沒有選單列指令。
4. 每個選單項都塞圖示。
5. Context menu 項目變暗而不隱藏、顯示快捷鍵、沒進選單列。
6. Alert 濫用：啟動就跳、純資訊、每次刪除都確認、「是／否」、取消當 default、破壞性當 default、刻意動作標紅。
7. Popover 當警告；popover 疊 popover；自動關閉丟掉輸入。
8. Sheet 疊 sheet；需要反覆操作卻用 sheet。
9. Panel 列進視窗選單、有最小化按鈕、沒標題列；HUD 當預設風格。
10. Switch 放 toolbar；有階層設定卻用 switch；已用 checkbox 的換成 switch。
11. Segmented 做主視窗切換；pop-up 放動作、pull-down 放選項。
12. 只寫「載入中⋯」；spinner 切進度條。
13. `.bouncy` 全域預設；頻繁互動加動畫；不看 Reduce Motion。
14. SF Symbols 用在網頁、app icon、logo。
15. `mouseDown` override；status item button action 裡自己 toggle 視窗（macOS 27 應用 expandedInterfaceSession）。
16. 快捷鍵用 ⌃ 當主修飾鍵、挪用 ⌘H／⌘M／⌘,。
