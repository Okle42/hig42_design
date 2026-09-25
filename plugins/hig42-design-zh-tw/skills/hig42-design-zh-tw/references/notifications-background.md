# 通知、權限請求、背景常駐、選單列與 App 圖示

> 證據來源：HIG（Notifications、Managing notifications、Privacy、Onboarding、Launching、App icons、Icons、Images、SF Symbols、The menu bar，2026-09 抓的 DocC JSON）、Apple 開發者文件（UserNotifications、ServiceManagement、AppKit、Icon Composer 文章）、App Review Guidelines 2.4.5／4.5.4、WWDC21-10091、WWDC25-220／361；作者環境 MacOSX27.sdk 標頭核對；作者環境 macOS 27 系統 `.loctable` 繁中字串；範例用 `swiftc -parse-as-library -swift-version 6 -typecheck -target arm64-apple-macos26.0` 編譯過，0 錯誤。來源清單見 repo 的 `SOURCES.md`
> 選單列 extra 的基本 HIG 規則、`MenuBarExtra`／`expandedInterfaceSession`、Settings 視窗寫法在 `macos-components.md` §3、§5、§12，這裡不重複。

標記：**【官方】** HIG／Apple 文件／WWDC／審查指南；**【SDK】** 作者環境 SDK 標頭或編譯過；**【實測】** 作者環境量到；**【系統字串】** macOS 27 繁中介面實際用字；**【第三方】**；**【推論】**。

## 目錄
1. 通知：什麼時候發、怎麼寫
2. 中斷等級（interruption level）
3. 通知 API 與程式碼
4. 權限請求（通知以外）
5. 登入時打開與背景常駐（SMAppService）
6. Dock 圖示有無：LSUIElement／activation policy
7. 選單列圖示（template image）規格
8. App 圖示（Icon Composer、`.icon`）
9. 關於、結束、首次啟動
10. 繁中用語（系統字串）
11. 坑

---

## 1. 通知：什麼時候發、怎麼寫【官方 HIG Notifications】

**該發**：及時、高價值、瞄一眼就懂的資訊。
**不該發**：
- 同一件事發好幾次，即使使用者沒回應也一樣（塞滿通知中心，人會把整個 app 的通知關掉）。
- 叫人「進 app 做某件事」的通知（關掉就忘了）。簡單的事改成通知動作按鈕。
- **錯誤訊息**：用 alert，不用通知。
- 行銷／促銷：**除非使用者明確同意**，而且 app 內要有設定可以改回來。行銷通知**絕不可用 Time Sensitive**。【官方 HIG Managing notifications＋審查指南 4.5.4】
- 敏感、個人、機密資訊（別人可能看到螢幕）。

**App 在前景時**：系統不顯示你的通知，要用不打擾的方式呈現（更新 badge、把新資料插進目前畫面）。

### 內容寫法
| 欄位 | 規則 |
|---|---|
| 標題 | 短、瞄一眼能讀；**放有用的資訊**（事件名、主旨），不要放 app 名稱。只能給空泛標題（像「新文件」）時，乾脆不給，系統會顯示 app 名稱。英文用 title case、不加句尾標點 |
| 內文 | 完整句、正確標點；**不要自己截斷**，系統會截 |
| 預覽隱藏時的替代文字 | 使用者可以關掉所有預覽，這時系統只顯示 app 圖示和預設標題「通知」。用 `hiddenPreviewsBodyPlaceholder` 給概括描述（「溫度警示」「新留言」），不透露細節 |
| App 名稱／圖示 | **不要放**：系統已在通知左側顯示大的 app 圖示 |
| 聲音 | 可自訂但要短、有辨識度、專業製作；**不能靠聲音傳達重要資訊** |

- HIG **沒有給字數上限**。標題能一行讀完，內文一兩句是【推論】。
- 中文沒有 title case／sentence case，照 `zh-tw-writing.md`：完整句用「。」，標題不加句號。

### 動作按鈕
- **最多 4 顆**。放能省時、不必打開 app 的常用動作（例：「延後」）。
- 按鈕文字短、描述結果、**不放 app 名稱**；要考慮翻譯後長度。
- **不要放「打開 app」的動作**：點通知本身就會打開。
- 優先非破壞性；破壞性要標 `.destructive`，系統會用不同外觀。
- 每顆配一個簡單的圖示（SF Symbol），系統放在標題尾端。

### Badge
- **只用來表示未讀通知數**，不要拿來顯示溫度、日期、股價這類數字。
- 不能只靠 badge 傳達重要資訊（使用者可以關掉）；已讀就立刻更新；不要自己畫假 badge。
- 選單列 app 通常沒 Dock 圖示，badge 沒地方顯示【推論】。

### macOS 差異
- HIG 對 macOS **沒有額外規定**。
- 授權請求在 macOS 上是一則通知橫幅：標題「「%@」通知」、內文「通知可能包含提示、聲音和圖像標記。」，按鈕有「選項」→「允許」。【系統字串】
- Time Sensitive 在 Mac 第一次出現時，系統會問「要保留「具時效性」的%@通知嗎？」【系統字串】

## 2. 中斷等級【官方 HIG Managing notifications＋SDK】

| 等級 | 意思 | 蓋過排程摘要 | 穿透專注模式 | 需要權限 | 例子 |
|---|---|---|---|---|---|
| `.passive` | 有空再看，**不亮螢幕、不出聲** | 否 | 否 | — | 每日溫度摘要、背景工作完成 |
| `.active`（預設） | 到的時候知道就好，可能出聲 | 否 | 否 | — | 一般警示 |
| `.timeSensitive` | **直接影響本人、需要立即注意** | 是 | 是 | Xcode 開 **Time Sensitive Notifications** capability | 帳號安全、快遞到了；溫度到臨界、風扇故障 |
| `.critical` | 健康與人身安全，**極少見**，通常來自政府／醫療／居家 | 是 | 是（也蓋過靜音） | entitlement `com.apple.developer.usernotifications.critical-alerts`，要向 Apple 申請 | 天災、居家安全警報 |

- **Time Sensitive 只給「正在發生或一小時內會發生」的事**。系統第一次會問使用者要不要保留，之後也會定期再問，濫用就會被關掉。
- **Mac 溫度警示不是 Critical**，最多用 Time Sensitive，而且只用在「現在就要處理」的那一則；恢復正常、每日統計用 `.passive`。【推論】
- 摘要排序：`relevanceScore` 0–1，分數最高的會成為摘要的主打（macOS 12+）。【官方】
- 分組：`threadIdentifier` 決定同一串（macOS 10.14+）。`summaryArgument` 在 iOS 15 起被忽略；macOS 的 DocC 沒標棄用。【官方】
- 舊的 `UNAuthorizationOptions.timeSensitive` 已棄用，要改用 capability／entitlement。【SDK】
- 沒開 capability 卻設 `.timeSensitive` 會怎樣：Apple 沒寫；社群說法是被當成 `.active`。【第三方】

## 3. 通知 API 與程式碼

### 3.1 流程【官方 Asking permission to use notifications】
1. **在情境中請求**：例如使用者打開「溫度過高時通知」開關時才呼叫 `requestAuthorization`，**不要在第一次啟動時就要**。
2. 系統**只會問一次**，之後再呼叫也不會跳出來。
3. **每次排通知前都先查** `notificationSettings()`，因為使用者隨時可以改。
4. **provisional（試用授權）**：`[.provisional]` 不跳對話框，直接靜默送到通知中心，旁邊有「保留⋯」／「關閉」讓使用者評估。用這個就可以在啟動時請求。【官方】
5. category／action 在**啟動時**註冊（`setNotificationCategories` 不會跳授權框）。
6. 相同 `identifier` 的新請求會**取代**舊的通知並放到最上面，**但會再提醒一次**。適合「同一件事的最新狀態」，不能拿來靜音。【官方】
7. `UNNotificationActionIcon`、`interruptionLevel`、`relevanceScore` 都是 macOS 12+；`setBadgeCount` 是 macOS 13+。【SDK】

### 3.2 程式碼（macOS 26，Swift 6 編譯過）【SDK】
```swift
import UserNotifications

enum HeatNotifier {
    static let categoryID = "HEAT_ALERT"
    static let snoozeID = "HEAT_SNOOZE_30M"
    static let showTopID = "HEAT_SHOW_TOP"

    /// applicationDidFinishLaunching 呼叫；不會跳授權框
    static func registerCategories() {
        let showTop = UNNotificationAction(
            identifier: showTopID, title: "顯示耗用程序", options: [.foreground],
            icon: UNNotificationActionIcon(systemImageName: "list.bullet"))
        let snooze = UNNotificationAction(
            identifier: snoozeID, title: "30分鐘內不再提醒", options: [],
            icon: UNNotificationActionIcon(systemImageName: "bell.slash"))
        let cat = UNNotificationCategory(
            identifier: categoryID, actions: [showTop, snooze], intentIdentifiers: [],
            hiddenPreviewsBodyPlaceholder: "溫度警示", options: [])
        UNUserNotificationCenter.current().setNotificationCategories([cat])
    }

    /// 使用者打開「溫度過高時通知」時才呼叫
    static func requestIfNeeded() async -> Bool {
        let center = UNUserNotificationCenter.current()
        switch await center.notificationSettings().authorizationStatus {
        case .authorized, .provisional: return true
        case .denied: return false
        case .notDetermined:
            return (try? await center.requestAuthorization(options: [.alert, .sound])) ?? false
        @unknown default: return false
        }
    }

    static func postHeat(celsius: Int, topProcess: String) async {
        let center = UNUserNotificationCenter.current()
        let s = await center.notificationSettings()
        guard s.authorizationStatus == .authorized || s.authorizationStatus == .provisional else { return }
        let c = UNMutableNotificationContent()
        c.title = "CPU溫度\(celsius)°C"                          // 有用的資訊當標題，不放 app 名稱
        c.body = "\(topProcess)占用最多CPU。風扇已切到全速。"      // 完整句、全形句號
        c.sound = .default
        c.categoryIdentifier = categoryID
        c.threadIdentifier = "thermal"
        c.interruptionLevel = .timeSensitive                      // 要開 capability；只給「現在」的事
        c.relevanceScore = 0.9
        try? await center.add(UNNotificationRequest(identifier: "heat-current", content: c, trigger: nil))
    }
}

final class NotifDelegate: NSObject, UNUserNotificationCenterDelegate {
    // 有實作這個 delegate 卻沒實作 willPresent 時，前景通知不會顯示（等同 .none）
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
        [.banner, .list, .sound]   // 選單列 app 沒有「在前景看畫面」的情境，照常顯示
    }
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse) async {
        switch response.actionIdentifier {
        case HeatNotifier.snoozeID: break                              // 記錄 30 分鐘靜音
        case HeatNotifier.showTopID, UNNotificationDefaultActionIdentifier: break  // 打開面板
        default: break
        }
    }
}
// AppDelegate.applicationDidFinishLaunching：
//   UNUserNotificationCenter.current().delegate = notif（要強引用）
//   HeatNotifier.registerCategories()
```
- 有設 delegate 但**沒實作 `willPresent`**，app 在前景時系統等同回傳 `.none`，通知不顯示；**完全沒設 delegate** 則照原設定顯示。【官方】
- 使用者拒絕後：開關切回關閉，旁邊用次要文字說明「通知已在系統設定中關閉。」，並給按鈕帶去系統設定。不要一直重問（也問不了）。【推論＋HIG Settings「給直接按鈕，不要描述路徑」】

## 4. 權限請求（通知以外）【官方 HIG Privacy】

### 4.1 時機
- **只在真的需要時要**；最好等使用者**實際用到那個功能**才要。
- **不要在啟動時要**，除非沒有它 app 就不能動（例如導航 app 要位置）；**不要一次要好幾個**。【官方＋推論】
- 真的需要先 onboarding 的 app，可以把請求放進 onboarding 流程，順便說明好處；否則在第一次用到功能時才要。【官方 HIG Onboarding】
- 請求要盡量具體（只要需要的那一種）。

### 4.2 用途字串（`NS…UsageDescription`）
HIG 規則：**簡短的完整句、主動語態、具體說明怎麼用、句尾加句號**。系統把它顯示在 app 名稱之後、按鈕之前。

| | 例子 | 問題 |
|---|---|---|
| ✅ | The app records during the night to detect snoring sounds. | 主動、說清楚怎麼用、為什麼用 |
| ❌ | Microphone access is needed for a better experience. | 被動、理由空泛 |
| ❌ | Turn on microphone access. | 命令句、沒有理由 |

**Apple 自己的繁中寫法**（作者環境系統 app `InfoPlist.loctable`）【系統字串】：
- 語音備忘錄 `NSLocationUsageDescription`：「語音備忘錄會依照錄音的位置來命名。」
- 提醒事項 `NSUserNotificationsUsageDescription`：「「通知」可在提醒事項到期時讓你知道。」
- 日誌 `NSCameraUsageDescription`：「取用相機可讓你拍攝照片和影片。」
- 備忘錄 `NSMicrophoneUsageDescription`：「這可讓你將錄製的音訊加入備忘錄。」
- 句型：「取用X可讓你⋯」「「App名」會使用X來⋯」「你的X會用來⋯」；用「取用」不用「存取」；稱「你」；句尾「。」；中英之間不空格。

**背景工具常用的 key 與繁中範例**（範例是【推論】，key 已查過官方文件）：
| Key | 何時需要 | 範例 |
|---|---|---|
| `NSAppleEventsUsageDescription` | 用 Apple events 控制別的 app（必填） | 「「溫度監控」會傳送指令給「音樂」，在溫度過高時暫停播放。」 |
| `NSLocalNetworkUsageDescription` | 直接或間接用區域網路（含 Bonjour） | 「「溫度監控」會在區域網路上尋找你的其他Mac，以顯示它們的溫度。」 |
| `NSBluetoothAlwaysUsageDescription` | 用藍牙 | 「「溫度監控」會連接藍牙溫度感測器來讀取機箱溫度。」 |
| `NSCameraUsageDescription`／`NSMicrophoneUsageDescription` | 相機／麥克風（macOS 10.14+） | — |

- **輔助使用、完整磁碟取用、螢幕錄製**沒有用途字串可以填：前兩者只能引導使用者去系統設定手動加入；輔助使用可呼叫 `AXIsProcessTrustedWithOptions`（帶 prompt 選項）讓系統跳出引導；螢幕錄製用 `CGPreflightScreenCaptureAccess()`／`CGRequestScreenCaptureAccess()`（macOS 10.15+）。【SDK＋第三方】
- 系統對話框的繁中：「要允許「%@」取用你的相機嗎？」／「允許」／「不允許」。【系統字串】

### 4.3 請求前的自訂說明畫面（pre-alert）【官方】
- **只放一顆按鈕，而且要看得出來它會打開系統對話框**。用「繼續」「下一步」，**不要用「允許」**（會跟系統的允許鈕混淆，等於誘導）。
- **不放其他動作**：沒有「關閉」「取消」「以後再說」（除非法律同意需要）。
- 不要用獎勵誘導、不要模仿系統對話框、不要放對話框截圖、不要在背景標註箭頭（會被審查退件）。

### 4.4 macOS 其他【官方】
- 用 Developer ID 簽名（App Store 外發佈）；Mac App Store 必須 sandbox。
- 不要假設登入的是誰（快速使用者切換）。

## 5. 登入時打開與背景常駐（SMAppService）

### 5.1 規則
- **Mac App Store 審查 2.4.5(iii)**：未經同意不可在開機／登入時自動啟動或執行程式碼；使用者結束 app 後不可留下仍在執行的程序；不可自動把圖示加進 Dock 或在桌面留捷徑。【官方】
- 現行 HIG **沒有**「Open at login」專頁。「預設關閉、由使用者在設定裡打開」是從審查指南和 HIG「讓使用者決定要不要放 menu bar extra」推出來的。【推論】
- 做法：設定視窗「一般」分頁放 **「在登入時打開」** checkbox（或 mini switch），**預設關**；也可以在首次啟動的歡迎視窗提供同一個選項（使用者主動勾）。【推論】
- **每次都讀 `status`，不要只信自己存的 bool**：使用者可以在系統設定裡關掉。【官方】

### 5.2 API【SDK：MacOSX27.sdk `SMAppService.h`，全部 macOS 13+】
| 用法 | 用途 | 位置 | `register()` 之後 |
|---|---|---|---|
| `SMAppService.mainApp` | **主 app 本身登入時打開**（選單列 app 最常用） | — | 下次登入起才啟動 |
| `.loginItem(identifier:)` | 內嵌 helper app | `Contents/Library/LoginItems/` | **立刻啟動**，之後每次登入；crash 或非 0 結束會被重啟 |
| `.agent(plistName:)` | 使用者層 LaunchAgent | `Contents/Library/LaunchAgents/` | 立刻 bootstrap，之後每次登入；要多個使用者就在每個使用者的 session 各呼叫一次 |
| `.daemon(plistName:)` | 系統層 LaunchDaemon | `Contents/Library/LaunchDaemons/` | **管理者在系統設定核准後**才 bootstrap，之後每次開機 |

- `status`：`.notRegistered`／`.enabled`／`.requiresApproval`（已註冊，但要使用者去系統設定允許；使用者撤銷同意時也會回這個）／`.notFound`。
- `SMAppService.openSystemSettingsLoginItems()`：直接打開「登入項目與延伸功能」。
- 錯誤：`kSMErrorAlreadyRegistered`、`kSMErrorLaunchDeniedByUser`、`kSMErrorInvalidSignature`。**App 必須有 code signing；含 LaunchDaemon 的 app 必須公證。**
- plist 用 **`BundleProgram`**（相對於 bundle 的路徑）取代 `Program`，這樣 app 被搬走也能跑。
- **更新了 agent／daemon 的 plist 或執行檔，要重新 register**（換了執行檔建議先 unregister）。
- Daemon 要在登入前能被讀到，建議 app 放 `/Applications`。
- 取代：`SMLoginItemSetEnabled`、自己寫檔到 `~/Library/LaunchAgents`、`/Library/LaunchDaemons`。

### 5.3 系統設定裡怎麼顯示【官方＋系統字串】
- 位置：**系統設定 → 一般 → 登入項目與延伸功能**。
- 兩區：「在登入時打開」（`mainApp`，「這些項目在你登入時會自動打開。」）；「背景App活動」（agent／daemon／loginItem，「這些App可在背景中自動執行，以進行同步資料和檢查更新項目等操作。」），每個 app 一個開關。
- bundle 內的 agent／daemon **自動歸在你的 app 名下**；舊式裝在 `/Library` 的 plist 要加 `AssociatedBundleIdentifiers`，否則顯示憑證的組織名稱，未簽名就顯示執行檔名。
- 註冊時系統會發通知（英文標題「Login Item Added」，附「You can manage this in Login Items & Extensions.」）。【實測：BackgroundTaskManagementAgent 字串】
- 開發時殘留項目：`sudo sfltool resetbtm` 會重設**所有**第三方登入項目，別在使用者的機器上亂跑。【官方】

### 5.4 程式碼【SDK，編譯過】
```swift
import ServiceManagement

@MainActor
final class LoginItemModel: ObservableObject {
    @Published private(set) var status = SMAppService.mainApp.status
    @Published var lastError: String?
    var isOn: Bool { status == .enabled }

    func refresh() { status = SMAppService.mainApp.status }
    func set(_ on: Bool) {
        do {
            if on { try SMAppService.mainApp.register() }
            else  { try SMAppService.mainApp.unregister() }
        } catch { lastError = error.localizedDescription }
        refresh()
    }
}

// 設定視窗「一般」分頁
Section {
    Toggle("在登入時打開", isOn: Binding(get: { login.isOn }, set: { login.set($0) }))
    if login.status == .requiresApproval {
        LabeledContent("需要在系統設定中允許") {
            Button("打開登入項目設定⋯") { SMAppService.openSystemSettingsLoginItems() }
        }
    }
}
// 從系統設定切回來時要重讀：
.onReceive(NotificationCenter.default.publisher(for: NSApplication.didBecomeActiveNotification)) { _ in login.refresh() }
```

## 6. Dock 圖示有無：LSUIElement／activation policy

| 做法 | 效果 | 什麼時候用 |
|---|---|---|
| Info.plist `LSUIElement = YES` | agent app：**不在 Dock、沒有選單列（App 選單）**，一啟動就是 `.accessory` | 純選單列工具 |
| `NSApp.setActivationPolicy(.accessory)` | 同上，執行中切換 | 讓使用者選「顯示Dock圖示」 |
| `.regular` | 一般 app：有 Dock 圖示、有選單列 | 有主視窗的 app |
| `.prohibited` | 不能被啟動、沒有介面 | 純背景 helper |
【官方 AppKit 文件；`.accessory` 等同 `LSUIElement = 1`】

- **accessory app 沒有 App 選單**，所以沒有系統自動提供的「關於」「設定⋯（⌘,）」「結束（⌘Q）」，**這些入口都要自己放進 menu bar extra 的選單**（見 §9）。【官方＋推論】
- `setActivationPolicy` 在 10.9 起可以切換任何值，回傳 Bool。從 `.accessory` 切成 `.regular` 後要 `NSApp.activate()`（macOS 14+）才會到前面；`activate()` **不保證成功**（協作式啟用）。【SDK＋官方】
- 取捨【推論】：
  - 純監控工具 → `LSUIElement`，不佔 Dock。
  - 有常開主視窗 → `.regular`；可提供「顯示Dock圖示」選項。
  - 常見折衷：開設定或主視窗時切 `.regular`（有 Dock 圖示和 ⌘Q 可用），全部關掉後切回 `.accessory`。切換時 Dock 圖示會閃一下，要不要這樣做看產品。【第三方】
- HIG 建議主要功能也要能從 menu bar extra 以外的地方用到（Dock 選單、主視窗）；純選單列 app 做不到時，至少讓「從 Finder 再打開 app」會跳出設定或歡迎視窗（見 §9.3）。

## 7. 選單列圖示（template image）規格

### 7.1 Apple 給的
- **優先用 SF Symbol**，可以原樣用或自訂。自訂圖示只能用**黑＋透明**，系統依選單列深淺與選取狀態上色。【官方 HIG The menu bar／Icons】
- HIG 說選單列高 **24pt**；但 `NSStatusBar.system.thickness` 在作者環境回傳 **22**（API 值與外觀高度不一致，版面不要寫死）。【官方＋實測】
- 自訂介面圖示用**向量（PDF／SVG）**，系統自動處理高解析度；PNG 要自己給 @1x＋@2x（macOS 只需 @1x、@2x）。【官方 HIG Icons／Images】
- 大小、細節程度、**線寬**、透視要跟其他圖示一致；圖示字重跟相鄰文字一致；不對稱的圖示用留白做**光學置中**。【官方 HIG Icons】
- 要提供 accessibility 描述。

### 7.2 Apple 沒給、要自己抓的（附作者環境量測）
| 項目 | 建議值 | 依據 |
|---|---|---|
| 畫布 | **18×18pt**（@1x 18px、@2x 36px）；寬可放到 22pt | 系統 menu extra 的 PDF：PPP 18×18、VPN 與 ExpressCard 18×14、PPPoE 22×14【實測】 |
| 圖形高度 | 14–18pt | 同上【實測】；舊經驗值 16–18pt【第三方】 |
| SF Symbol 預設大小 | 交給系統：`fan` 18×16、`thermometer.medium` 11×17、`gauge…` 15×15pt | `NSImage(systemSymbolName:)` 預設尺寸【實測】 |
| 線寬 | 對齊 SF Symbols Regular 字重的筆畫（約 1.5pt 以上，@2x 不低於 2px）| 【推論】；HIG 只要求「避免過細線條」 |
| 顏色 | 只用黑＋alpha | `isTemplate` 文件【官方】 |

- 系統的 Time Machine extra 用的是**向量 glyph（自訂符號）**＋三組點陣後備。自訂符號是最接近 Apple 做法的路線。【實測：assetutil】

### 7.3 自訂 SF Symbol 流程【官方 Creating custom symbol images】
1. SF Symbols app 選最像的符號 → **File › Duplicate as Custom Symbol** → **File › Export Template**（選 **variable**：只要畫 `Ultralight-S`、`Regular-S`、`Black-S` 三組，系統內插出其餘 24 組；只需一種字重就選 static）。
2. 在向量軟體改圖：**只用填色路徑、不要用描邊**（有描邊就不能內插）；保留所有 id（`Regular-M`、`left-margin-Regular-M`⋯）；S／M／L 比例 0.783／1.0／1.29。
3. 匯出 SVG，**小數精度 7 位以上**（Illustrator 預設精度太低）。
4. **File › Validate Templates** 或拖進 Asset Catalog 驗證。
5. 可以標註 hierarchical／multicolor 圖層、variable color 門檻（表達溫度等級）。
6. **不能修改 Apple 產品／功能的符號**（SF Symbols app 會標 Info 圖示）。
```swift
// AppKit（macOS 13+）【SDK】
let img = NSImage(symbolName: "custom.fan.gauge", bundle: .main, variableValue: level)  // level 0...1
img?.isTemplate = true
statusItem.button?.image = img
// SwiftUI
Image("custom.fan.gauge", variableValue: level).accessibilityLabel("風扇轉速")
```

### 7.4 動態狀態圖示【SDK＋推論】
```swift
@MainActor
final class StatusController {
    let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
    init() {
        item.autosaveName = "com.example.monitor.status"                   // 記住使用者 ⌘拖曳後的位置
        item.behavior = [.removalAllowed, .terminationOnRemoval]
        setState(hot: false)
    }
    func setState(hot: Bool) {
        let img = NSImage(systemSymbolName: hot ? "thermometer.high" : "fan",
                          accessibilityDescription: hot ? "溫度過高" : "溫度監控")
        img?.isTemplate = true                                // 狀態用「換形狀」表達，不要改成紅色
        item.button?.image = img
        item.button?.toolTip = hot ? "CPU溫度過高" : "溫度監控"
    }
}
```
- template 圖示**不能靠顏色表達狀態**（系統會重新上色）；用換符號、variable value、加 badge 形狀（`thermometer.high`、`exclamationmark`）表達。真的要彩色警示時，把 `isTemplate` 關掉，但要自己處理深淺選單列和選取狀態，屬於刻意偏離。【推論】
- 動畫用 symbol effect，狀態結束就停、尊重 Reduce Motion（`macos-components.md` §10、§12.8）。
- 用 `NSImage(named:)` 載入點陣素材：Asset Catalog 設 **Render As = Template Image**，或程式裡設 `isTemplate = true`；檔名以 `Template` 結尾的圖也會被當成 template【第三方】。

## 8. App 圖示（Icon Composer、`.icon`）【官方 HIG App icons＋Icon Composer 文章＋WWDC25】

### 8.1 規格
| 項目 | iOS／iPadOS／macOS | watchOS |
|---|---|---|
| 畫布 | **1024×1024 px**，正方形 | 1088×1088 px |
| 遮罩後 | 圓角矩形（系統加圓角） | 圓形 |
| 外觀 | Default、Dark、Clear light、Clear dark、Tinted light、Tinted dark | — |
| 色彩空間 | sRGB、Gray Gamma 2.2、Display P3 | 同左 |

- 檔案：**`.icon`**（UTI `com.apple.iconcomposer.icon`，是 package）。Icon Composer 在 **Xcode › Open Developer Tool › Icon Composer**（Xcode 27 內附 27.0 版），也可以單獨下載。【官方＋實測 Info.plist】
- 在 target **General › App Icons** 填 `.icon` 的檔名（不含副檔名）。**加了 `.icon` 就會取代舊的 AppIcon asset catalog**；deployment target 較舊時，Xcode 會在建置時自動產生舊系統用的圖。想讓舊系統顯示原本的舊圖示，就繼續用 asset catalog。【官方】

### 8.2 流程
1. 從 Apple Design Resources 下載 app icon 範本（Figma／Sketch／Photoshop／Illustrator，有新格線）。
2. **分層設計**，由後往前排，圖層名稱加編號；文字轉外框；**優先 SVG**，網格漸層或點陣圖用 PNG。
3. **不要在圖層裡做**：模糊、陰影、高光、透明度、背景色／漸層、**遮罩圓角**。這些都在 Icon Composer 裡做，系統會動態產生。
4. 拖進 Icon Composer，最多整理成 **4 個 group**（group 就是最終的深度層）。
5. 背景用純色或漸層（Icon Composer 內建），不需要匯入背景圖；真要匯入就要滿版、不透明。
6. 對每個 group 調 Liquid Glass：Specular（Automatic／Inside／Outside／Off）、Blur、Refraction、Translucency、Shadow；Mode 選 Individual 或 Combined。
7. 預覽 Default／Dark／Mono（Mono 再切 Clear／Tinted、Light／Dark），用自己的桌布截圖當背景測透明度；可以對照 26 與 27 的渲染（27 以前 Refraction 沒效果、Inside／Outside 都只是打開高光）。
8. 各外觀**保持同樣的核心造型**，不要每種外觀換元素；Dark 以 Default 為基礎、避免過亮，有色背景在深色模式對比最好。

### 8.3 不規則外形與 macOS 灰框【官方 WWDC25-220】
- macOS 26 起**畫布形狀就是遮罩**：以前可以凸出圓角矩形的部分（例如舊「聯絡人」的分頁標籤）不再允許。
- 已經接近圓角矩形的舊圖示，系統自動遮罩或延伸填滿。
- **外形很特別的舊圖示：系統拿掉陰影、自動縮小放進圓角矩形畫布**（也就是一般說的「灰框」）。Apple 明說**最好重畫**，讓圖形用滿畫布。
- 所以：**不要交透明背景、不規則外形的 1024 PNG 當 macOS 圖示**；一定要有滿版背景層。

### 8.4 設計規則
- 簡單、一個核心概念、形狀越少越好；背景簡單（純色／漸層），不必填滿整個畫布。
- 主要內容置中（遮罩和圓角可能會切到）；前景邊緣要清楚（不要羽化）。
- **文字只在必要時放**（不支援無障礙與在地化）；不要放「Play」「New」之類的字。
- 偏好插畫，不要照片；不要複製 UI 元件或截圖；避免極細線條與尖角；**不要畫 Apple 硬體**。
- **不可用 SF Symbols 做 app icon**（授權，見 `macos-components.md` §10）。

## 9. 關於、結束、首次啟動

### 9.1 「關於」【官方 HIG The menu bar＋AppKit】
- 一般 app：App 選單第一項「關於%@」，自己一組（後面加分隔線）；**選單項目名稱不含版本號**，16 字元以內。
- 關於視窗顯示**版權與版本**。用系統的 `NSApp.orderFrontStandardAboutPanel(options:)`：`.applicationName`、`.applicationVersion`（顯示用版本）、`.version`（build）、`.credits`（`NSAttributedString`）、`.applicationIcon`；版權沒給就讀 `NSHumanReadableCopyright`。系統格式是「版本%1$@（%2$@）」。【官方＋系統字串】
- accessory app 要先 `NSApp.activate()` 再開關於視窗，否則視窗可能出現在其他 app 後面。【推論】

### 9.2 結束的入口【官方＋推論】
- 一般 app：「結束%@」＋ ⌘Q，名稱跟「關於」用同一個短名。
- **純選單列 app 沒有 App 選單和 Dock 圖示，結束只能從 extra 的選單進入**：放在**選單最底部**，前面加分隔線，文字「結束溫度監控」，加 `.keyboardShortcut("q")`（選單打開時 ⌘Q 有效）。【推論：系統選單列 app 的慣例】
- 選單建議順序：狀態資訊 → 主要動作 → 分隔線 → 關於%@、設定⋯（⌘,）→ 分隔線 → 結束%@。【推論】
- `.window` 樣式的 extra：在面板底部或齒輪選單放「設定⋯」「結束」。
- 結束時要一併停掉你啟動的子程序（審查指南 2.4.5(iii)）。登入項目／agent 的「關閉」是在設定裡取消註冊，不是結束 app。

```swift
struct MenuContent: View {
    @Environment(\.openSettings) private var openSettings
    var body: some View {
        Text("CPU 72°C")
        Divider()
        Button("關於溫度監控") {
            NSApp.activate()
            NSApp.orderFrontStandardAboutPanel(options: [
                .credits: NSAttributedString(string: "Apple Silicon風扇守門員")])
        }
        Button("設定⋯") { NSApp.activate(); openSettings() }
            .keyboardShortcut(",")
        Divider()
        Button("結束溫度監控") { NSApp.terminate(nil) }
            .keyboardShortcut("q")
    }
}
```

### 9.3 首次啟動：使用者找不到選單列圖示
問題：純選單列 app 打開後**沒有視窗、沒有 Dock 圖示**；選單列太擠時 extra 會被**系統藏起來**（瀏海機型更常見），使用者也可以在「系統設定 › 選單列 › 在選單列中允許」把它關掉（作者環境 macOS 27 有這個選項【系統字串】；從 macOS 26 開始有是【第三方】）。系統會隱藏 extra 這件事是【官方】。

解法：
1. **第一次啟動開一個小歡迎視窗**：一句話說圖示在哪（附圖示本身），給「在登入時打開」選項（預設不勾）和「完成」。HIG：讓人在設定流程中選擇要不要放 extra。【官方＋推論】
2. **從 Finder／Spotlight 再打開 app 時**（`applicationShouldHandleReopen`，或偵測到 extra 被移除），打開設定視窗，讓人找得到「在選單列中顯示」和「結束」。【推論；呼應 `macos-components.md` §3.2】
3. Onboarding 保持短、可略過、不要每次都顯示；權限請求放到第一次用到時。【官方 HIG Onboarding】
4. 不要用通知來說「我在選單列」（HIG：不要用通知叫人做事）。【官方】

```swift
@main
struct ThermalMonitorApp: App {
    @AppStorage("showMenuBarExtra") private var showMenuBarExtra = true
    @AppStorage("didShowWelcome") private var didShowWelcome = false
    var body: some Scene {
        MenuBarExtra("溫度監控", systemImage: "fan", isInserted: $showMenuBarExtra) { MenuContent() }
        Settings { GeneralSettings() }
        Window("歡迎使用溫度監控", id: "welcome") {
            WelcomeView().onAppear { didShowWelcome = true }
        }
        .windowResizability(.contentSize)
        .restorationBehavior(.disabled)
        .defaultLaunchBehavior(didShowWelcome ? .suppressed : .presented)   // macOS 15+
    }
}
```
【SDK：`defaultLaunchBehavior(_:)`／`SceneLaunchBehavior.automatic/.presented/.suppressed` 是 macOS 15+】

## 10. 繁中用語（系統字串）【系統字串】

| English | 繁中 | 出處 |
|---|---|---|
| Login Items & Extensions | 登入項目與延伸功能 | LoginItems.appex |
| Open at Login | 在登入時打開 | LoginItems.appex |
| Background App Activity | 背景App活動 | LoginItems.appex |
| Running in background／Not running in background | 正在背景中執行／未在背景中執行 | LoginItems.appex |
| Allow in the Menu Bar | 在選單列中允許 | ControlCenterSettings.appex |
| Show in Menu Bar／Don’t Show in Menu Bar | 在選單列中顯示／不要在選單列中顯示 | ControlCenterSettings.appex |
| “%@” Notifications | 「%@」通知 | askpermissions.bundle |
| Notifications may include alerts, sounds, and icon badges. | 通知可能包含提示、聲音和圖像標記。 | askpermissions.bundle |
| Time Sensitive | 具時效性 | NotificationCenter.app |
| Deliver Quietly／Deliver Prominently | 傳送靜音通知／傳送重要通知 | NotificationCenter.app |
| Keep…／Turn Off／Options | 保留⋯／關閉／選項 | NotificationCenter.app |
| Summary | 摘要 | NotificationCenter.app |
| Critical Alerts | 重要提示 | askpermissions.bundle |
| Allow／Don’t Allow | 允許／不允許 | TCC |
| Allow “%@” to access your camera? | 要允許「%@」取用你的相機嗎？ | TCC |
| You can change this in Privacy settings. | 你可以在「隱私權」設定中更改。 | TCC |
| About %@／Quit %@／Hide %@ | 關於%@／結束%@／隱藏%@ | SwiftUI MainMenu |
| Version %@ (%@) | 版本%1$@（%2$@） | AppKit |

- 「access」一律譯「取用」（不是「存取」）；通知「alert」譯「提示」，Critical Alert 譯「重要提示」。

## 11. 坑
1. **第一次啟動就 `requestAuthorization`**，或一次要通知＋輔助使用＋位置。改成在使用者打開對應功能時才要。
2. 通知標題寫 app 名稱、內文自己加「⋯」截斷、把錯誤訊息當通知發、同一件事每分鐘發一次。
3. **Time Sensitive 當預設**、行銷通知用 Time Sensitive、溫度警示用 Critical（要特殊 entitlement，而且不符合用途）。
4. 設了 `UNUserNotificationCenter.delegate` 卻沒實作 `willPresent`，前景通知全部消失；delegate 沒強引用被釋放。
5. 以為相同 identifier 就不會再響：取代已送達的通知時**會再提醒一次**。
6. 用 badge 顯示溫度數字；自己畫假 badge。
7. pre-alert 畫面的按鈕寫「允許」、附「以後再說」、放系統對話框截圖。
8. 用途字串寫「需要取用麥克風以提供更好的體驗」（被動、空泛）或只寫「請開啟麥克風權限」。
9. **登入時打開預設為開**、自己寫 plist 到 `~/Library/LaunchAgents`、只存自己的 bool 不讀 `SMAppService.status`、沒處理 `.requiresApproval`。
10. 改了 agent 執行檔沒重新 register（舊版繼續跑或起不來）；ad-hoc／未簽名去 register（`kSMErrorInvalidSignature`）；含 daemon 沒公證。
11. `LSUIElement` app 沒在 extra 選單放「結束」「設定⋯」「關於」，使用者只能開活動監視器強制結束。
12. 首次啟動什麼都不顯示，使用者以為沒打開；extra 被系統藏起來後就再也找不到 app。
13. 選單列圖示用彩色 PNG、只給 @1x、點陣圖沒設 `isTemplate`；用顏色表達警示狀態（template 會被重新上色）。
14. 自訂符號用描邊路徑（不能內插）、SVG 精度太低、改了 Apple 產品符號。
15. App icon 交透明背景的不規則 PNG，在 macOS 26+ 被縮進灰色圓角框；在圖層裡自己畫陰影高光、預先切好圓角。
16. 加了 `.icon` 以為舊的 AppIcon asset catalog 還會用在舊系統：`.icon` 會取代它，舊系統的圖由 Xcode 自動產生。
17. `NSStatusBar.system.thickness`（22）和 HIG 的 24pt 不一致，不要用它算死版面。
