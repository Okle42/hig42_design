# Notifications, Permission Requests, Background Agents, Menu Bar, and App Icons

> Evidence: HIG (Notifications, Managing notifications, Privacy, Onboarding, Launching, App icons, Icons, Images, SF Symbols, The menu bar; DocC JSON fetched 2026-09), Apple developer documentation (UserNotifications, ServiceManagement, AppKit, the Icon Composer articles), App Review Guidelines 2.4.5 / 4.5.4, WWDC21-10091, WWDC25-220 / 361; headers checked against MacOSX27.sdk in the author's setup; zh-TW strings from the system `.loctable` files in the author's setup (macOS 27); samples compiled with `swiftc -parse-as-library -swift-version 6 -typecheck -target arm64-apple-macos26.0`, 0 errors. Sources: see `SOURCES.md` in the repo.
> Basic HIG rules for menu bar extras, `MenuBarExtra` / `expandedInterfaceSession`, and how to build the Settings window live in `macos-components.md` §3, §5, and §12 and are not repeated here.

Tags: **[Official]** HIG / Apple docs / WWDC / App Review Guidelines; **[SDK]** SDK headers in the author's setup, or compiled; **[Measured]** measured in the author's setup; **[System strings]** actual wording in the macOS 27 zh-TW UI; **[Third-party]**; **[Inferred]**.

## Contents
1. Notifications: when to send them and how to write them
2. Interruption levels
3. Notification API and code
4. Permission requests (other than notifications)
5. Open at login and background agents (SMAppService)
6. Dock icon or not: LSUIElement / activation policy
7. Menu bar icon (template image) specs
8. App icons (Icon Composer, `.icon`)
9. About, Quit, and first launch
10. zh-TW terminology (system strings)
11. Pitfalls

---

## 1. Notifications: when to send them and how to write them [Official HIG Notifications]

**Send**: timely, high-value information that people can understand at a glance.
**Don't send**:
- Multiple notifications about the same thing, even if the person hasn't responded (it clutters Notification Center, and people will turn off notifications for the whole app).
- Notifications that tell people to "go into the app and do something" (they dismiss it and forget). Turn simple tasks into notification action buttons instead.
- **Error messages**: use an alert, not a notification.
- Marketing / promotions: **only with explicit opt-in**, and the app must offer a setting to turn them back off. Marketing notifications must **never use Time Sensitive**. [Official HIG Managing notifications + App Review Guidelines 4.5.4]
- Sensitive, personal, or confidential information (someone else might see the screen).

**When the app is in the foreground**: the system doesn't display your notifications, so present the information unobtrusively (update the badge, insert new data into the current view).

### Writing the content
| Field | Rule |
|---|---|
| Title | Short and readable at a glance; **carry useful information** (event name, subject), not the app name. If all you could give is a generic title (like "New Document"), omit it and the system shows the app name. In English, use title case and no ending punctuation |
| Body | Complete sentences with correct punctuation; **don't truncate it yourself** — the system truncates |
| Placeholder when previews are hidden | People can turn off all previews; the system then shows only the app icon and the default title "Notification". Use `hiddenPreviewsBodyPlaceholder` to give a general description ("Temperature Alert", "New Comment") that reveals no details |
| App name / icon | **Don't include them**: the system already shows a large app icon on the leading side of the notification |
| Sound | Can be custom, but keep it short, distinctive, and professionally produced; **never rely on sound to convey important information** |

- The HIG **gives no character limits**. "Title fits on one line, body is one or two sentences" is **[Inferred]**.
- Chinese has no title case / sentence case; for zh-TW follow `zh-tw-writing.md`: complete sentences end with「。」, titles get no period.

### Action buttons
- **At most 4.** Include common actions that save time and don't require opening the app (e.g., "Snooze").
- Button titles are short, describe the result, and **don't include the app name**; account for length after localization.
- **Don't add an "Open app" action**: tapping/clicking the notification itself opens the app.
- Prefer nondestructive actions; mark destructive ones `.destructive` so the system gives them a distinct appearance.
- Give each one a simple icon (an SF Symbol); the system places it at the trailing end of the title.

### Badge
- **Use it only to indicate the number of unread notifications** — not for numbers like temperature, dates, or stock prices.
- Never rely solely on the badge for important information (people can turn it off); update it as soon as items are read; don't draw a fake badge.
- Menu bar apps usually have no Dock icon, so there's nowhere for a badge to appear. [Inferred]

### macOS differences
- The HIG has **no additional rules** for macOS.
- On macOS, the authorization request is a notification banner: title "“%@” Notifications", body "Notifications may include alerts, sounds, and icon badges.", with an "Options" button → "Allow". [System strings] (zh-TW:「「%@」通知」「通知可能包含提示、聲音和圖像標記。」「選項」→「允許」)
- The first time a Time Sensitive notification appears on a Mac, the system asks whether to keep Time Sensitive notifications from that app (zh-TW:「要保留「具時效性」的%@通知嗎？」). [System strings]

## 2. Interruption levels [Official HIG Managing notifications + SDK]

| Level | Meaning | Breaks through scheduled summary | Breaks through Focus | Requirement | Examples |
|---|---|---|---|---|---|
| `.passive` | Look when you have time; **doesn't light the screen or play a sound** | No | No | — | Daily temperature summary, background job finished |
| `.active` (default) | Good to know when it arrives; may play a sound | No | No | — | General alerts |
| `.timeSensitive` | **Directly affects the person and needs immediate attention** | Yes | Yes | Enable the **Time Sensitive Notifications** capability in Xcode | Account security, package delivered; temperature at a critical level, fan failure |
| `.critical` | Health and personal safety; **very rare**, usually from government / medical / home-security apps | Yes | Yes (also overrides the mute switch) | Entitlement `com.apple.developer.usernotifications.critical-alerts`, requires applying to Apple | Natural disasters, home security alarms |

- **Time Sensitive is only for things happening now or within the next hour.** The system asks the person the first time whether to keep them, and asks again periodically — abuse it and it gets turned off.
- **A Mac temperature warning is not Critical.** At most use Time Sensitive, and only for the one notification that needs handling right now; use `.passive` for "back to normal" and daily stats. [Inferred]
- Summary ranking: `relevanceScore` 0–1; the highest score becomes the featured notification in the summary (macOS 12+). [Official]
- Grouping: `threadIdentifier` determines the thread (macOS 10.14+). `summaryArgument` is ignored starting in iOS 15; the macOS DocC doesn't mark it deprecated. [Official]
- The old `UNAuthorizationOptions.timeSensitive` is deprecated; use the capability / entitlement instead. [SDK]
- What happens if you set `.timeSensitive` without the capability: Apple doesn't say; the community says it's treated as `.active`. [Third-party]

## 3. Notification API and code

### 3.1 Flow [Official Asking permission to use notifications]
1. **Ask in context**: e.g., call `requestAuthorization` only when the person turns on a "Notify when temperature is too high" switch — **not on first launch**.
2. The system **asks only once**; later calls don't show the prompt again.
3. **Check `notificationSettings()` every time before scheduling a notification**, because people can change it at any time.
4. **Provisional authorization**: `[.provisional]` shows no dialog; notifications are delivered quietly to Notification Center with "Keep…" / "Turn Off" so people can evaluate them. With this you *can* request at launch. [Official]
5. Register categories / actions **at launch** (`setNotificationCategories` doesn't trigger the authorization prompt).
6. A new request with the same `identifier` **replaces** the old notification and moves it to the top, **but alerts again**. Good for "latest status of the same thing"; it can't be used to silence. [Official]
7. `UNNotificationActionIcon`, `interruptionLevel`, and `relevanceScore` are all macOS 12+; `setBadgeCount` is macOS 13+. [SDK]

### 3.2 Code (macOS 26, compiled with Swift 6) [SDK]
```swift
import UserNotifications

enum HeatNotifier {
    static let categoryID = "HEAT_ALERT"
    static let snoozeID = "HEAT_SNOOZE_30M"
    static let showTopID = "HEAT_SHOW_TOP"

    /// Call from applicationDidFinishLaunching; doesn't show the authorization prompt
    static func registerCategories() {
        let showTop = UNNotificationAction(
            identifier: showTopID, title: "Show Top Processes", options: [.foreground],
            icon: UNNotificationActionIcon(systemImageName: "list.bullet"))
        let snooze = UNNotificationAction(
            identifier: snoozeID, title: "Mute for 30 Minutes", options: [],
            icon: UNNotificationActionIcon(systemImageName: "bell.slash"))
        let cat = UNNotificationCategory(
            identifier: categoryID, actions: [showTop, snooze], intentIdentifiers: [],
            hiddenPreviewsBodyPlaceholder: "Temperature Alert", options: [])
        UNUserNotificationCenter.current().setNotificationCategories([cat])
    }

    /// Call only when the person turns on "Notify when temperature is too high"
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
        c.title = "CPU at \(celsius)°C"                                   // Useful info as the title, no app name
        c.body = "\(topProcess) is using the most CPU. Fans are now at full speed."  // Complete sentences
        c.sound = .default
        c.categoryIdentifier = categoryID
        c.threadIdentifier = "thermal"
        c.interruptionLevel = .timeSensitive                      // Needs the capability; only for things happening "now"
        c.relevanceScore = 0.9
        try? await center.add(UNNotificationRequest(identifier: "heat-current", content: c, trigger: nil))
    }
}

final class NotifDelegate: NSObject, UNUserNotificationCenterDelegate {
    // If you implement this delegate but not willPresent, foreground notifications aren't shown (same as .none)
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification) async -> UNNotificationPresentationOptions {
        [.banner, .list, .sound]   // A menu bar app has no "looking at the screen in the foreground" case, so show as usual
    }
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse) async {
        switch response.actionIdentifier {
        case HeatNotifier.snoozeID: break                              // Record a 30-minute mute
        case HeatNotifier.showTopID, UNNotificationDefaultActionIdentifier: break  // Open the panel
        default: break
        }
    }
}
// AppDelegate.applicationDidFinishLaunching:
//   UNUserNotificationCenter.current().delegate = notif (keep a strong reference)
//   HeatNotifier.registerCategories()
```
- If you set a delegate but **don't implement `willPresent`**, the system behaves as if it returned `.none` while the app is in the foreground and the notification isn't shown; with **no delegate at all**, notifications display according to their normal settings. [Official]
- After the person denies: flip the switch back off, add secondary text next to it such as "Notifications are turned off in System Settings.", and provide a button that takes them to System Settings. Don't keep re-asking (you can't anyway). [Inferred + HIG Settings: "provide a direct button rather than describing the path"]

## 4. Permission requests (other than notifications) [Official HIG Privacy]

### 4.1 Timing
- **Ask only when you actually need it**; ideally wait until the person **actually uses the feature**.
- **Don't ask at launch** unless the app can't function without it (e.g., a navigation app needs location); **don't ask for several at once**. [Official + Inferred]
- Apps that genuinely need onboarding can put requests in the onboarding flow and explain the benefits there; otherwise ask the first time the feature is used. [Official HIG Onboarding]
- Make requests as specific as possible (ask only for the kind you need).

### 4.2 Purpose strings (`NS…UsageDescription`)
HIG rules: **a brief complete sentence, active voice, specific about how the data is used, ending with a period.** The system shows it after the app name and before the buttons.

| | Example | Issue |
|---|---|---|
| ✅ | The app records during the night to detect snoring sounds. | Active, says clearly how and why |
| ❌ | Microphone access is needed for a better experience. | Passive, vague reason |
| ❌ | Turn on microphone access. | Imperative, no reason |

**Common keys for background utilities, with English examples** (examples are **[Inferred]**; keys verified against official docs):
| Key | When required | Example |
|---|---|---|
| `NSAppleEventsUsageDescription` | Controlling other apps via Apple events (required) | "Thermal Monitor sends commands to Music to pause playback when your Mac gets too hot." |
| `NSLocalNetworkUsageDescription` | Using the local network directly or indirectly (including Bonjour) | "Thermal Monitor looks for your other Macs on the local network to show their temperatures." |
| `NSBluetoothAlwaysUsageDescription` | Using Bluetooth | "Thermal Monitor connects to Bluetooth temperature sensors to read your case temperature." |
| `NSCameraUsageDescription` / `NSMicrophoneUsageDescription` | Camera / microphone (macOS 10.14+) | — |

**zh-TW examples — how Apple writes them** (system apps' `InfoPlist.loctable` in the author's setup) [System strings]:
- Voice Memos `NSLocationUsageDescription`:「語音備忘錄會依照錄音的位置來命名。」
- Reminders `NSUserNotificationsUsageDescription`:「「通知」可在提醒事項到期時讓你知道。」
- Journal `NSCameraUsageDescription`:「取用相機可讓你拍攝照片和影片。」
- Notes `NSMicrophoneUsageDescription`:「這可讓你將錄製的音訊加入備忘錄。」
- Patterns:「取用X可讓你⋯」「「App名」會使用X來⋯」「你的X會用來⋯」. Apple always uses「取用」(not「存取」) for "access", addresses the user as「你」, ends with「。」, and puts no space between Chinese and Latin text. zh-TW versions of the keys above would read, e.g.,「「溫度監控」會傳送指令給「音樂」，在溫度過高時暫停播放。」「「溫度監控」會在區域網路上尋找你的其他Mac，以顯示它們的溫度。」「「溫度監控」會連接藍牙溫度感測器來讀取機箱溫度。」 [Inferred]

- **Accessibility, Full Disk Access, and Screen Recording** have no purpose string to fill in: for the first two you can only guide the person to add the app manually in System Settings; for Accessibility you can call `AXIsProcessTrustedWithOptions` (with the prompt option) so the system shows a guide; for Screen Recording use `CGPreflightScreenCaptureAccess()` / `CGRequestScreenCaptureAccess()` (macOS 10.15+). [SDK + Third-party]
- System dialog wording: "Allow “%@” to access your camera?" / "Allow" / "Don’t Allow" (zh-TW:「要允許「%@」取用你的相機嗎？」／「允許」／「不允許」). [System strings]

### 4.3 Custom explanation screen before the request (pre-alert) [Official]
- **Only one button, and it must be clear that it opens the system dialog.** Use "Continue" or "Next" — **not "Allow"** (it would be confused with the system's Allow button, which amounts to manipulation).
- **No other actions**: no "Close", "Cancel", or "Not Now" (unless legally required for consent).
- Don't offer rewards as incentives, don't imitate the system dialog, don't include screenshots of the dialog, and don't draw arrows pointing at it in the background (grounds for App Review rejection).

### 4.4 Other macOS notes [Official]
- Sign with Developer ID (distribution outside the App Store); the Mac App Store requires the sandbox.
- Don't assume who is logged in (Fast User Switching).

## 5. Open at login and background agents (SMAppService)

### 5.1 Rules
- **Mac App Store Review 2.4.5(iii)**: apps may not auto-launch or run code at startup / login without consent; may not leave processes running after the person quits the app; may not automatically add icons to the Dock or leave shortcuts on the desktop. [Official]
- The current HIG has **no** dedicated "Open at login" page. "Off by default, turned on by the person in Settings" is derived from the App Review Guidelines plus the HIG's "let people decide whether to put a menu bar extra in the menu bar". [Inferred]
- Approach: put an **"Open at Login"** checkbox (or mini switch) on the General tab of the Settings window, **off by default**; you can also offer the same option in a first-launch welcome window (the person checks it themselves). [Inferred]
- **Read `status` every time; don't trust only your own stored bool**: people can turn it off in System Settings. [Official]

### 5.2 API [SDK: MacOSX27.sdk `SMAppService.h`, all macOS 13+]
| Usage | Purpose | Location | After `register()` |
|---|---|---|---|
| `SMAppService.mainApp` | **The main app itself opens at login** (most common for menu bar apps) | — | Launches starting at the next login |
| `.loginItem(identifier:)` | Embedded helper app | `Contents/Library/LoginItems/` | **Launches immediately**, then at every login; relaunched if it crashes or exits non-zero |
| `.agent(plistName:)` | Per-user LaunchAgent | `Contents/Library/LaunchAgents/` | Bootstrapped immediately, then at every login; for multiple users, call it once in each user's session |
| `.daemon(plistName:)` | System-wide LaunchDaemon | `Contents/Library/LaunchDaemons/` | Bootstrapped only **after an administrator approves it in System Settings**, then at every boot |

- `status`: `.notRegistered` / `.enabled` / `.requiresApproval` (registered, but the person must allow it in System Settings; also returned when the person revokes consent) / `.notFound`.
- `SMAppService.openSystemSettingsLoginItems()`: opens Login Items & Extensions directly.
- Errors: `kSMErrorAlreadyRegistered`, `kSMErrorLaunchDeniedByUser`, `kSMErrorInvalidSignature`. **The app must be code signed; apps containing a LaunchDaemon must be notarized.**
- In the plist, use **`BundleProgram`** (a bundle-relative path) instead of `Program`, so it still works if the app is moved.
- **After updating an agent / daemon plist or executable, register again** (when the executable changes, unregister first).
- For a daemon to be readable before login, keep the app in `/Applications`.
- Replaces: `SMLoginItemSetEnabled`, and writing files yourself into `~/Library/LaunchAgents` or `/Library/LaunchDaemons`.

### 5.3 How it appears in System Settings [Official + System strings]
- Location: **System Settings › General › Login Items & Extensions**.
- Two sections: "Open at Login" (`mainApp`; zh-TW caption「這些項目在你登入時會自動打開。」— "These items will open automatically when you log in."); "Background App Activity" (agent / daemon / loginItem; zh-TW caption「這些App可在背景中自動執行，以進行同步資料和檢查更新項目等操作。」— roughly "These apps can run automatically in the background to do things like sync data and check for updates."), with one switch per app.
- Agents / daemons inside your bundle are **automatically listed under your app's name**; legacy plists installed in `/Library` need `AssociatedBundleIdentifiers`, otherwise the certificate's organization name is shown, or the executable name if unsigned.
- The system posts a notification on registration (English title "Login Item Added", with "You can manage this in Login Items & Extensions."). [Measured: BackgroundTaskManagementAgent strings]
- Leftover entries during development: `sudo sfltool resetbtm` resets **all** third-party login items — don't run it casually on someone else's machine. [Official]

### 5.4 Code [SDK, compiled]
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

// General tab of the Settings window
Section {
    Toggle("Open at Login", isOn: Binding(get: { login.isOn }, set: { login.set($0) }))
    if login.status == .requiresApproval {
        LabeledContent("Requires approval in System Settings") {
            Button("Open Login Items Settings…") { SMAppService.openSystemSettingsLoginItems() }
        }
    }
}
// Re-read when switching back from System Settings:
.onReceive(NotificationCenter.default.publisher(for: NSApplication.didBecomeActiveNotification)) { _ in login.refresh() }
```

## 6. Dock icon or not: LSUIElement / activation policy

| Approach | Effect | When to use |
|---|---|---|
| Info.plist `LSUIElement = YES` | Agent app: **no Dock icon, no menu bar (app menu)**; `.accessory` from launch | Pure menu bar utilities |
| `NSApp.setActivationPolicy(.accessory)` | Same as above, switched at runtime | Letting people choose "Show Dock Icon" |
| `.regular` | Ordinary app: Dock icon and menu bar | Apps with a main window |
| `.prohibited` | Can't be activated, no UI | Pure background helpers |
[Official AppKit docs; `.accessory` is equivalent to `LSUIElement = 1`]

- **An accessory app has no app menu**, so it doesn't get the system-provided About, Settings… (⌘,), and Quit (⌘Q) — **you must put all of these in the menu bar extra's menu yourself** (see §9). [Official + Inferred]
- Since 10.9, `setActivationPolicy` can switch to any value and returns a Bool. After switching from `.accessory` to `.regular`, call `NSApp.activate()` (macOS 14+) to come to the front; `activate()` is **not guaranteed to succeed** (cooperative activation). [SDK + Official]
- Trade-offs [Inferred]:
  - Pure monitoring utility → `LSUIElement`, no Dock space used.
  - Always-open main window → `.regular`; optionally offer a "Show Dock Icon" setting.
  - Common compromise: switch to `.regular` while Settings or the main window is open (Dock icon and ⌘Q work), and back to `.accessory` once they're all closed. The Dock icon flickers on each switch; whether that's acceptable is a product call. [Third-party]
- The HIG recommends that key features also be reachable outside the menu bar extra (Dock menu, main window); if a pure menu bar app can't do that, at least make "reopening the app from the Finder" bring up Settings or a welcome window (see §9.3).

## 7. Menu bar icon (template image) specs

### 7.1 What Apple specifies
- **Prefer SF Symbols**, as-is or customized. Custom icons may use only **black + transparency**; the system colors them based on the menu bar's appearance and selection state. [Official HIG The menu bar / Icons]
- The HIG says the menu bar is **24pt** tall, but `NSStatusBar.system.thickness` returns **22** in the author's setup (the API value and the visual height disagree — don't hard-code layout). [Official + Measured]
- Use **vector (PDF / SVG)** for custom interface icons and the system handles high resolution; for PNG, supply @1x + @2x yourself (macOS needs only @1x and @2x). [Official HIG Icons / Images]
- Keep size, level of detail, **stroke weight**, and perspective consistent with other icons; match icon weight to adjacent text; use padding to **optically center** asymmetric icons. [Official HIG Icons]
- Provide an accessibility description.

### 7.2 What Apple doesn't specify (with measurements from the author's setup)
| Item | Recommended value | Basis |
|---|---|---|
| Canvas | **18×18pt** (@1x 18px, @2x 36px); width can go up to 22pt | System menu extra PDFs: PPP 18×18, VPN and ExpressCard 18×14, PPPoE 22×14 [Measured] |
| Glyph height | 14–18pt | Same as above [Measured]; older rule of thumb 16–18pt [Third-party] |
| SF Symbol default size | Let the system decide: `fan` 18×16, `thermometer.medium` 11×17, `gauge…` 15×15pt | Default size from `NSImage(systemSymbolName:)` [Measured] |
| Stroke weight | Match SF Symbols Regular-weight strokes (about 1.5pt or more, no less than 2px @2x) | [Inferred]; the HIG only says "avoid overly thin lines" |
| Color | Black + alpha only | `isTemplate` docs [Official] |

- The system's Time Machine extra uses a **vector glyph (custom symbol)** plus three bitmap fallbacks. A custom symbol is the route closest to how Apple does it. [Measured: assetutil]

### 7.3 Custom SF Symbol workflow [Official Creating custom symbol images]
1. In the SF Symbols app, pick the closest symbol → **File › Duplicate as Custom Symbol** → **File › Export Template** (choose **variable**: draw only the three sets `Ultralight-S`, `Regular-S`, `Black-S` and the system interpolates the other 24; choose static if you need only one weight).
2. Edit in a vector app: **use filled paths only, no strokes** (strokes can't be interpolated); keep all ids (`Regular-M`, `left-margin-Regular-M`, …); the S / M / L scale ratio is 0.783 / 1.0 / 1.29.
3. Export SVG with **7 or more decimal places of precision** (Illustrator's default precision is too low).
4. Validate with **File › Validate Templates** or by dragging into an asset catalog.
5. You can annotate hierarchical / multicolor layers and variable color thresholds (to express temperature levels).
6. **You may not modify symbols of Apple products / features** (the SF Symbols app marks them with an Info icon).
```swift
// AppKit (macOS 13+) [SDK]
let img = NSImage(symbolName: "custom.fan.gauge", bundle: .main, variableValue: level)  // level 0...1
img?.isTemplate = true
statusItem.button?.image = img
// SwiftUI
Image("custom.fan.gauge", variableValue: level).accessibilityLabel("Fan Speed")
```

### 7.4 Dynamic status icon [SDK + Inferred]
```swift
@MainActor
final class StatusController {
    let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
    init() {
        item.autosaveName = "com.example.monitor.status"                   // Remembers the position after the person ⌘-drags it
        item.behavior = [.removalAllowed, .terminationOnRemoval]
        setState(hot: false)
    }
    func setState(hot: Bool) {
        let img = NSImage(systemSymbolName: hot ? "thermometer.high" : "fan",
                          accessibilityDescription: hot ? "Temperature Too High" : "Thermal Monitor")
        img?.isTemplate = true                                // Express state by changing the shape, not by turning it red
        item.button?.image = img
        item.button?.toolTip = hot ? "CPU temperature too high" : "Thermal Monitor"
    }
}
```
- A template icon **can't convey state through color** (the system recolors it); use a different symbol, a variable value, or a badge shape (`thermometer.high`, `exclamationmark`). If you truly need a colored warning, turn off `isTemplate`, but then you handle light/dark menu bars and selection state yourself — a deliberate deviation. [Inferred]
- Animate with symbol effects, stop when the state ends, and respect Reduce Motion (`macos-components.md` §10, §12.8).
- Loading bitmap assets with `NSImage(named:)`: set **Render As = Template Image** in the asset catalog, or set `isTemplate = true` in code; images whose file names end in `Template` are also treated as templates [Third-party].

## 8. App icons (Icon Composer, `.icon`) [Official HIG App icons + Icon Composer articles + WWDC25]

### 8.1 Specs
| Item | iOS / iPadOS / macOS | watchOS |
|---|---|---|
| Canvas | **1024×1024 px**, square | 1088×1088 px |
| After masking | Rounded rectangle (system applies the corners) | Circle |
| Appearances | Default, Dark, Clear light, Clear dark, Tinted light, Tinted dark | — |
| Color spaces | sRGB, Gray Gamma 2.2, Display P3 | Same |

- File: **`.icon`** (UTI `com.apple.iconcomposer.icon`, a package). Icon Composer is at **Xcode › Open Developer Tool › Icon Composer** (Xcode 27 bundles version 27.0) and is also available as a standalone download. [Official + Measured Info.plist]
- In the target's **General › App Icons**, enter the `.icon` file name (without extension). **Adding a `.icon` replaces the old AppIcon asset catalog**; with an older deployment target, Xcode generates images for older systems at build time. If you want older systems to keep showing your original icon, keep using the asset catalog. [Official]

### 8.2 Workflow
1. Download the app icon templates from Apple Design Resources (Figma / Sketch / Photoshop / Illustrator, with the new grid).
2. **Design in layers**, ordered back to front, with numbered layer names; convert text to outlines; **prefer SVG**, and use PNG for mesh gradients or raster art.
3. **Don't bake into layers**: blur, shadows, highlights, transparency, background color / gradient, or **the rounded-corner mask**. All of that is done in Icon Composer and generated dynamically by the system.
4. Drag into Icon Composer and organize into at most **4 groups** (groups are the final depth layers).
5. Use a solid color or gradient background (built into Icon Composer); there's no need to import a background image — if you do, it must be full-bleed and opaque.
6. Tune Liquid Glass per group: Specular (Automatic / Inside / Outside / Off), Blur, Refraction, Translucency, Shadow; set Mode to Individual or Combined.
7. Preview Default / Dark / Mono (Mono further switches Clear / Tinted, Light / Dark), using a screenshot of your own wallpaper as the background to test transparency; you can compare 26 vs. 27 rendering (before 27, Refraction has no effect and Inside / Outside both just turn on the highlight).
8. **Keep the same core shape** across appearances — don't swap elements per appearance; base Dark on Default and avoid making it too bright; colored backgrounds give the best contrast in Dark Mode.

### 8.3 Irregular shapes and the macOS gray frame [Official WWDC25-220]
- Starting in macOS 26, **the canvas shape is the mask**: parts that used to stick out of the rounded rectangle (like the tab on the old Contacts icon) are no longer allowed.
- Legacy icons that are already close to a rounded rectangle are automatically masked or extended to fill.
- **Legacy icons with unusual shapes: the system removes the shadow and shrinks them into a rounded-rectangle canvas** (what people call the "gray frame"). Apple explicitly says it's **best to redraw** so the artwork fills the canvas.
- So: **don't ship a 1024 PNG with a transparent background and an irregular shape as a macOS icon**; always include a full-bleed background layer.

### 8.4 Design rules
- Simple, one core idea, as few shapes as possible; a simple background (solid / gradient) that doesn't need to fill the whole canvas.
- Keep primary content centered (the mask and corners may clip it); keep foreground edges crisp (no feathering).
- **Include text only when essential** (it doesn't support accessibility or localization); don't add words like "Play" or "New".
- Prefer illustration over photos; don't replicate UI components or screenshots; avoid very thin lines and sharp corners; **don't depict Apple hardware**.
- **You may not use SF Symbols for an app icon** (licensing; see `macos-components.md` §10).

## 9. About, Quit, and first launch

### 9.1 About [Official HIG The menu bar + AppKit]
- Ordinary apps: the first item in the app menu is "About %@", in its own group (followed by a separator); **the menu item name doesn't include the version number** and is 16 characters or fewer.
- The About window shows **copyright and version**. Use the system's `NSApp.orderFrontStandardAboutPanel(options:)`: `.applicationName`, `.applicationVersion` (display version), `.version` (build), `.credits` (`NSAttributedString`), `.applicationIcon`; if no copyright is given, it reads `NSHumanReadableCopyright`. The system format is "Version %@ (%@)" (zh-TW「版本%1$@（%2$@）」). [Official + System strings]
- An accessory app should call `NSApp.activate()` before opening the About window, otherwise the window may appear behind other apps. [Inferred]

### 9.2 Where Quit lives [Official + Inferred]
- Ordinary apps: "Quit %@" + ⌘Q, using the same short name as About.
- **A pure menu bar app has no app menu and no Dock icon, so Quit can only be reached from the extra's menu**: put it at the **very bottom of the menu**, preceded by a separator, titled "Quit Thermal Monitor", with `.keyboardShortcut("q")` (⌘Q works while the menu is open). [Inferred: convention of the system's menu bar apps]
- Suggested menu order: status info → primary actions → separator → About %@, Settings… (⌘,) → separator → Quit %@. [Inferred]
- For a `.window`-style extra: put "Settings…" and "Quit" at the bottom of the panel or in a gear menu.
- On quit, also stop any child processes you started (App Review Guidelines 2.4.5(iii)). "Turning off" a login item / agent means unregistering it in Settings, not quitting the app.

```swift
struct MenuContent: View {
    @Environment(\.openSettings) private var openSettings
    var body: some View {
        Text("CPU 72°C")
        Divider()
        Button("About Thermal Monitor") {
            NSApp.activate()
            NSApp.orderFrontStandardAboutPanel(options: [
                .credits: NSAttributedString(string: "Fan guard for Apple silicon")])
        }
        Button("Settings…") { NSApp.activate(); openSettings() }
            .keyboardShortcut(",")
        Divider()
        Button("Quit Thermal Monitor") { NSApp.terminate(nil) }
            .keyboardShortcut("q")
    }
}
```

### 9.3 First launch: people can't find the menu bar icon
The problem: after opening, a pure menu bar app has **no window and no Dock icon**; when the menu bar is crowded, the **system hides** extras (more common on notched models), and people can also turn an extra off under System Settings › Menu Bar › Allow in the Menu Bar (present on macOS 27 in the author's setup [System strings]; that it exists since macOS 26 is [Third-party]). That the system hides extras is [Official].

Solutions:
1. **Open a small welcome window on first launch**: one sentence saying where the icon is (showing the icon itself), an "Open at Login" option (unchecked by default), and "Done". HIG: let people choose during setup whether to add the extra. [Official + Inferred]
2. **When the app is reopened from the Finder / Spotlight** (`applicationShouldHandleReopen`, or when you detect the extra was removed), open the Settings window so people can find "Show in Menu Bar" and "Quit". [Inferred; see also `macos-components.md` §3.2]
3. Keep onboarding short and skippable, and don't show it every time; defer permission requests until first use. [Official HIG Onboarding]
4. Don't use a notification to say "I'm in the menu bar" (HIG: don't use notifications to tell people to do something). [Official]

```swift
@main
struct ThermalMonitorApp: App {
    @AppStorage("showMenuBarExtra") private var showMenuBarExtra = true
    @AppStorage("didShowWelcome") private var didShowWelcome = false
    var body: some Scene {
        MenuBarExtra("Thermal Monitor", systemImage: "fan", isInserted: $showMenuBarExtra) { MenuContent() }
        Settings { GeneralSettings() }
        Window("Welcome to Thermal Monitor", id: "welcome") {
            WelcomeView().onAppear { didShowWelcome = true }
        }
        .windowResizability(.contentSize)
        .restorationBehavior(.disabled)
        .defaultLaunchBehavior(didShowWelcome ? .suppressed : .presented)   // macOS 15+
    }
}
```
[SDK: `defaultLaunchBehavior(_:)` / `SceneLaunchBehavior.automatic/.presented/.suppressed` are macOS 15+]

## 10. zh-TW terminology (system strings) [System strings]

When localizing into Traditional Chinese (Taiwan), match the system's own wording:

| English | zh-TW | Source |
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

- "access" is always「取用」(not「存取」); a notification "alert" is「提示」, and Critical Alert is「重要提示」.

## 11. Pitfalls
1. **Calling `requestAuthorization` on first launch**, or asking for notifications + Accessibility + location all at once. Ask only when the person turns on the corresponding feature.
2. Putting the app name in the notification title, truncating the body yourself with "…", sending error messages as notifications, sending the same thing every minute.
3. **Time Sensitive as the default**, Time Sensitive for marketing, Critical for temperature warnings (requires a special entitlement, and doesn't fit the purpose).
4. Setting `UNUserNotificationCenter.delegate` without implementing `willPresent`, so all foreground notifications vanish; the delegate being deallocated because nothing holds a strong reference.
5. Assuming the same identifier won't alert again: replacing a delivered notification **alerts again**.
6. Using the badge to show a temperature; drawing a fake badge.
7. Pre-alert button titled "Allow", with a "Not Now" option, or with a screenshot of the system dialog.
8. Purpose strings like "Microphone access is needed for a better experience" (passive, vague) or just "Please turn on microphone access".
9. **Open at login on by default**, writing your own plist into `~/Library/LaunchAgents`, storing only your own bool without reading `SMAppService.status`, not handling `.requiresApproval`.
10. Changing the agent executable without re-registering (old version keeps running or fails to start); registering ad-hoc / unsigned builds (`kSMErrorInvalidSignature`); shipping a daemon without notarization.
11. An `LSUIElement` app without Quit, Settings…, and About in the extra's menu, leaving Activity Monitor's Force Quit as the only way out.
12. Showing nothing on first launch so people think the app didn't open; once the system hides the extra, the app can never be found again.
13. Colored PNGs for the menu bar icon, only @1x, bitmaps without `isTemplate`; using color to convey a warning state (templates get recolored).
14. Custom symbols with stroked paths (can't interpolate), low SVG precision, modified Apple product symbols.
15. Shipping an irregular PNG with a transparent background as the app icon, which gets shrunk into a gray rounded frame on macOS 26+; painting shadows / highlights into layers or pre-cutting rounded corners.
16. Assuming the old AppIcon asset catalog is still used on older systems after adding a `.icon`: the `.icon` replaces it, and Xcode generates the older-system images automatically.
17. `NSStatusBar.system.thickness` (22) disagrees with the HIG's 24pt — don't compute fixed layouts from it.
