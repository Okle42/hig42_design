# Components and Interaction Patterns (macOS first, plus iOS, animation, SF Symbols)

> Checked against the Xcode 27 SDK and 51 HIG pages. Sources: see `SOURCES.md` in the repo.
> For Traditional Chinese UI terminology, see `zh-tw-writing.md`.

## Contents
1. Windows, split views, toolbars
2. The menu bar
3. Menu bar extras ★
4. Panels, popovers, sheets, alerts
5. The Settings window ★
6. Controls
7. Keyboard, drag and drop, undo
8. Empty states, loading, errors, launch
9. Animation
10. SF Symbols
11. iOS components
12. Code templates
13. Pitfalls

---

## 1. Windows, split views, toolbars **[Official]**

- Don't build your own window frame or red/yellow/green buttons. Always refer to them as "windows" to users.
- Windows have three states — main, key, and inactive — and custom windows must switch appearance accordingly.
- Don't put critical information or actions in a bottom bar or at the bottom of a sidebar (windows often get dragged toward the bottom edge of the screen).
- Don't open new windows by default; you can offer "Open in New Window."
- **Split views**: every pane that leads to a detail view should keep its current selection highlighted; set sensible minimum/maximum widths; let people hide panes and provide multiple ways to bring them back (toolbar button + menu command + keyboard shortcut); use only one title above the whole split view; prefer an inspector over a new window for supplementary information.
- **Sidebars**: at most two levels; beyond that, switch to three columns; icons follow the accent color by default. Starting in macOS 27, sidebars extend to the window edge, selection uses semibold, and icons regain color.
- **Toolbars**:
  - **Every toolbar item needs a corresponding menu bar command** (toolbars can be hidden or customized).
  - Use unbordered SF Symbols; at most about 3 groups; the primary action uses `.prominent`, only one, at the trailing end.
  - Make the window title useful, **don't use the app name**, and keep it within 15 characters.
  - Apps people use for long stretches can let them customize the toolbar.
- Full screen: use the system's, and let people decide when to enter and exit (green button, View menu, ⌃⌘F).
- Restore the previous state at launch (scroll position, windows, tabs).
- SwiftUI: `.windowToolbarStyle(.unified)`, `.navigationSubtitle(_:)`, `.windowResizability(.contentMinSize)`, `.restorationBehavior(.disabled)` (for diagnostic windows).
- For sheets/modals that don't need to block app termination, set `NSWindow.preventsApplicationTerminationWhenModal = false`. **[Official WWDC26]**

## 2. The menu bar **[Official]**

Order: Apple → **App → File → Edit → Format → View → custom menus → Window → Help** → menu bar extras.

- When an item is unavailable, **dim it, don't hide it** (the opposite of context menus).
- Custom commands must always go in the menu bar (so they're discoverable, can have keyboard shortcuts, and work with Full Keyboard Access). Custom menus go between View and Window.
- App menu: About → Settings… (⌘,) → custom app settings → Services → Hide (⌘H) / Hide Others (⌥⌘H) / Show All → Quit (⌘Q). "About" doesn't include the version number.
- Edit menu: Undo/Redo should name what they act on ("Undo Typing"); don't call Delete "Clear" or "Erase."
- View menu: include it even if you have only one window; items like "Show/Hide Toolbar" should reflect the current state.
- Window menu: include it even if you have only one window (Minimize ⌘M and Zoom exist for Full Keyboard Access); the list of open windows **doesn't include panels**.
- **Menu item icons (2026-06 HIG update)**: use them sparingly — only for frequent actions, key features, file locations, connected devices, and user content; **within a group, either all items have icons or none do**; if there's no clear icon, leave it out. macOS 27 hides menu icons by default; to show them, use `.labelStyle(.titleAndIcon)`.
- SwiftUI: `CommandGroup(replacing:/before:/after:)`, `CommandMenu("Name")` (automatically inserted between View and Window); with a `Settings` scene you automatically get "Settings…" + ⌘,.

## 3. Menu bar extras ★

### 3.1 HIG rules **[Official]**
1. Use an **SF Symbol or a template image** (black + transparency defines the shape) for the icon; the system colors it according to the menu bar's appearance and selection state. **Don't use color PNGs.**
2. The menu bar is 24pt tall (taller on notched MacBooks — don't hard-code it); the HIG gives no icon size, but the industry convention is 16–18pt tall. With an SF Symbol, let the system handle it.
3. **Clicking shows a menu by default**; use the window style only when the functionality is too complex for a menu.
4. **Let people decide whether it appears in the menu bar**: put a "Show in Menu Bar" toggle in Settings.
5. **Don't rely on it always being there** (the system hides extras when space runs out).
6. **Make the main functionality reachable elsewhere too** (main window, Settings, Dock menu).

### 3.2 API
- SwiftUI `MenuBarExtra(isInserted:)` (macOS 13+); `.menuBarExtraStyle(.menu)` (default) or `.window` (only for information-dense monitoring panels).
- Menu-bar-only apps: Info.plist `LSUIElement = YES`. **When the user removes the extra from the menu bar, the system automatically terminates a menu-bar-only app**; the next time it's opened from the Finder, open the Settings window so people can add it back.
- **VoiceOver name**: there's a contradiction over whether a `MenuBarExtra`'s title becomes the accessibility name of the menu bar button (the official docs say it does; reading the AX tree in the author's setup showed it doesn't; not yet verified with VoiceOver on). Safe approach: use the `label:` closure and add `.accessibilityLabel` to the Image. See `accessibility.md`.
- AppKit `NSStatusItem`: set `isTemplate = true` on `button.image`, and set `button.setAccessibilityLabel(...)`.
- **New in macOS 27** `expandedInterfaceDelegate` / `expandedInterfaceSession`: for a status item that shows its own window (not an NSMenu), show the window in `statusItem(_:didBeginExpandedInterfaceSession:)` and dismiss it in `statusItemDidEndExpandedInterfaceSession(_:animated:)`. **Don't toggle it yourself in the button action** — this is what makes keyboard navigation and menu tracking work correctly; when the user closes it some other way, call `expandedInterfaceSession?.cancel()`. SwiftUI MenuBarExtra already handles this. **[SDK]**
- The icon can express state with a variable value (`thermometer.variable`) or a symbol effect, but respect Reduce Motion and avoid distracting continuous animation.

## 4. Panels, popovers, sheets, alerts

### 4.1 Panels **[Official]**
- Purpose: quick controls related to the current content/selection (use a panel for an inspector; use a regular window for an Info window with fixed content).
- Prefer simple adjustment controls (sliders, steppers); avoid ones that require typing.
- **Give it a title bar**, with a noun as the title ("Fonts," "Inspector").
- **Bring panels to the front when the app becomes active, and hide all panels when the app is inactive**; don't list them in the Window menu; generally no minimize button.
- Use the HUD style only in media apps, or when a standard panel would obscure critical content; keep it small and use little color.
- SwiftUI `UtilityWindow` (macOS 15+): `.floating` by default, hidden when the app is inactive, closes on Esc, can't be minimized, automatically added to the View menu.
- AppKit: `NSPanel` style masks `.nonactivatingPanel` (clicking doesn't activate the app), `.utilityWindow`, `.hudWindow`; `isFloatingPanel`, `becomesKeyOnlyIfNeeded`, `hidesOnDeactivate`.
- **HUD-style panels that are entirely glass** (macOS 26+): use borderless + `.clear` glass + tint, not `.titled` (which adds an extra layer of system frame); for the approach and measured values, see `liquid-glass.md` §3.1a. Standard utility panels still keep a title bar per the HIG.
- **An always-on-top monitoring panel is a deliberate deviation from the HIG** (the HIG requires hiding panels when the app is inactive). If you do it, compensate: make it closable, make staying on top optional, use nonactivating so it doesn't steal focus, keep it small with little color, and state this explicitly in the delivery notes.

### 4.2 Popovers **[Official]**
Small amounts of content; clicking outside dismisses it automatically; **keep the user's changes when it auto-dismisses** (discard them only on Cancel); only one at a time, never stacked; **don't use a popover for warnings**; on macOS people can drag it out into a standalone panel.

### 4.3 Sheets **[Official]**
Only one at a time; if there's a "Done," pair it with "Cancel"; while a macOS sheet is open, people should be able to use other windows; **for repeated input where people need to see results (Find and Replace), use a panel, not a sheet**.

### 4.4 Alerts **[Official]**
- **Use sparingly**: show purely informational messages in context instead; common, undoable destructive actions (deleting an email, trashing a file) don't need an alert; **don't show an alert at launch**.
- The title should state specifically what happened — not "Error" or "Error 329347"; two lines max. Use a period for complete sentences; no punctuation for fragments.
- Keep the informative text short, in complete sentences, and don't explain the buttons.
- Buttons: one- or two-word verbs that echo the title; **use "OK" only for purely informational alerts**; avoid "Yes/No"; **always call Cancel "Cancel"**; three buttons max.
- Placement (macOS): the default button on the **right (trailing)**, Cancel to its left.
- **Reserve the destructive style for destructive outcomes the user didn't deliberately choose**; if the user deliberately chose "Empty Trash," don't make the confirm button red (confirming with Return matters more).
- Any destructive action must have a Cancel; **Cancel must never be the default**; if you want to force people to read the content, set no default at all.
- Esc or ⌘. cancels. Use the caution triangle icon only when data could be lost unexpectedly.
- SwiftUI: alerts have no Cancel by default, so add `role: .cancel` yourself; for the default, use `.keyboardShortcut(.defaultAction)`; `.dialogSeverity(.critical)`; for "Don't ask again," use `.dialogSuppressionToggle(_:isSuppressed:)`. `ButtonRole.confirm` / `.close` are new in macOS 26.

## 5. The Settings window ★ **[Official HIG Settings]**

- Choose defaults so most people never need to change them; the fewer settings the better; **don't duplicate system settings** (Dark Mode, accessibility); don't ask about anything you can detect yourself.
- Options tied to a task (sorting, filtering, show/hide) belong in the task's view, not in Settings.
- **The app menu should have "Settings…" + ⌘,; don't put a gear settings button in a window's toolbar.**
- **Dim the Settings window's minimize and zoom buttons**; size the window to fit the current tab's content.
- Tab toolbar: not customizable, always visible, indicates the current tab.
- **The window title changes to match the current tab**; with only one pane, the title is "App Name Settings."
- **When reopened, return to the last-viewed tab.**
- Labels should clearly say "what happens when this is on"; when directing people to a particular setting, give them a button that goes there directly rather than describing the path.
- **Changes take effect immediately — no "OK / Apply / Cancel"**: the current HIG doesn't state this explicitly, but Apple's samples bind directly with `@AppStorage`, System Settings applies changes immediately, and older HIG versions said so explicitly. **[Inferred + older Official]**
- Use `.formStyle(.grouped)` to match the look of System Settings; **use mini switches for toggles inside grouped forms** (`.toggleStyle(.switch).controlSize(.mini)`). **[Official HIG Toggles]**
- Opening Settings from within the app: `SettingsLink`, `@Environment(\.openSettings)` (macOS 14+).

## 6. Controls **[Official]**

### 6.1 Buttons
- Custom buttons need a pressed state.
- **At most 1–2 prominent buttons per screen**; convey importance with style, not size.
- **A destructive action is never the primary action**, even if it's the most likely choice.
- macOS: **buttons that open another window/view get a trailing "…" in the title**; square (+/−) buttons contain only icons and go inside a view; at most one Help button per window, placed at the bottom left or bottom right; button order puts confirm on the right with Cancel to its left.
- Icon buttons need a tooltip (`.help("...")`) and an accessibility label; buttons with text usually don't need a tooltip.

### 6.2 Toggle-style controls (macOS)
| Control | When to use |
|---|---|
| Checkbox | **The default choice**; use when there's hierarchy (indented child settings); can have a mixed state |
| Switch | Settings you want to **emphasize**, or that control a whole group; mini inside grouped forms; **don't replace existing checkboxes with switches** |
| Radio | 2–5 mutually exclusive options; beyond about 5, use a pop-up |
- All three belong only in the content area, not in the toolbar.
- iOS: switches only in list rows.

### 6.3 Others
- **Segmented control**: don't mix selection and action segments; text or icons, not both; about 5–7 segments in wide interfaces; **in a macOS main window, switch views with a tab view, not a segmented control**.
- **Pop-up vs. pull-down**: a pop-up holds **mutually exclusive options** and shows the current value; a pull-down holds **actions** and shows a fixed title. The common mistake is exactly the reverse.
- **Slider**: minimum value on the left; live feedback on macOS; labels in sentence case + colon. **Stepper**: Shift-click changes the value by 10× at once. **Disclosure**: at most one disclosure button per view.
- **Table / outline**: column headers are nouns, no colon; click a column header to sort; columns are resizable; remember expansion state; truncate in the middle to keep the beginning and end.
- **Context menus**: only the most relevant items; **every item must also be findable in the menu bar**; **hide unavailable items rather than dimming them** (except Cut/Copy/Paste on macOS); **don't show keyboard shortcuts in context menus**.

## 7. Keyboard, drag and drop, undo **[Official]**

- Focus: text fields use a focus ring; lists highlight the whole row; **don't move focus without user interaction**.
- AppKit: turn on `NSWindow.autorecalculatesKeyViewLoop`; **don't override `mouseDown`** for selection/right-click/dragging — use gesture recognizers or macOS 27 control events; overlapping sibling views silently swallow clicks. **[Official WWDC26]**
- **Keyboard shortcuts**: don't repurpose standard shortcuts; ⌘ primary, ⇧ secondary, ⌥ sparingly, **avoid ⌃**; list modifiers in the order **⌃⌥⇧⌘**; ⇧⌘Z may only relate to undo/redo.
- Common standards: ⌘, Settings, ⌘Q Quit, ⌘W Close, ⌘M Minimize, ⌘N New, ⌘O Open, ⌘S Save, ⌘Z / ⇧⌘Z, ⌘F Find, ⌘G Find Next, ⌃⌘F Full Screen, ⌥⌘T Show/Hide Toolbar, ⌥⌘I Inspector, Esc Cancel, ⌘. cancel operation.
- **Drag and drop**: always provide an alternative menu command; move within the same container, copy across containers, Option forces a copy; drag and drop must be undoable.
- **Undo**: at the top of the Edit menu; name what will be undone; **don't limit the number of undos**; don't add an undo button when it isn't needed.

## 8. Empty states, loading, errors, launch **[Official]**

- **Empty states**: give a clear next step, ideally with a button; use `ContentUnavailableView`; for no search results, use `ContentUnavailableView.search(text:)`.
- **Loading**: show something as soon as possible (placeholders); beyond a second or two, use a progress indicator; **use determinate progress whenever you can**; keep progress accurate; **avoid vague descriptions like "Loading…"** — say specifically what's happening; if it can be interrupted, offer Cancel; **don't switch from a spinner to a progress bar**; on macOS, use a spinner for background work or tight spaces, usually unlabeled.
- **Errors**: show them next to the problem; don't blame; explain how to fix it; **no "oops" or "whoops"**; **don't use "we"**; no machine-speak like "Invalid name."
- **Launch**: launch instantly; on iOS the launch screen should be nearly identical to the first screen, with no text or logo.
- **Onboarding**: prefer contextual tips over a one-time long flow; make it skippable; defer nonessential setup; explain why when you need a permission.

## 9. Animation

### 9.1 Principles **[Official HIG Motion]**
Add animation only with purpose; **don't animate frequent interactions** (system components already have subtle animation); let people interrupt it; it can't be the only way to convey important information; direction should match the gesture; on trackpads, system effects are more restrained than on touch.

### 9.2 Reduce Motion **[Official]**
When `@Environment(\.accessibilityReduceMotion)` is true: tighten springs to reduce bounce, replace positional transitions with cross-fades, and avoid z-axis depth animation and blur-in/blur-out.

### 9.3 SwiftUI defaults **[SDK: read from the inlined implementation in SwiftUICore.swiftinterface]**
| API | duration | bounce |
|---|---|---|
| `.smooth` | 0.5 | 0 |
| `.snappy` | 0.5 | 0.15 |
| `.bouncy` | 0.5 | 0.3 |
| `.spring` | 0.5 | 0 |
| `.interactiveSpring` | 0.15 | 0.15 |
| `.default` | Since iOS 17 / macOS 14: spring(response 0.55, damping 1.0) | — |

**Choosing**: use `.smooth` for general state changes and layout changes (closest to the system); `.snappy` for crisp small components; `.bouncy` only for occasional playful feedback; **utility apps shouldn't use `.bouncy` as a global default**; when a monitoring number updates every second, don't bounce on every update.

## 10. SF Symbols

- Versions: SF Symbols 7 (2025, iOS/macOS 26) added Draw On/Off, Variable Draw, and gradients; the current download on the website is `SF-Symbols-27.dmg`, and new symbols are available only on 27 systems; macOS 27 **added no new symbol effects**. **[Official + SDK]**
- **Rendering modes**: monochrome, hierarchical (layered opacity), palette (one color per layer), multicolor (built-in semantic colors); 26+ has `.symbolColorRenderingMode(.gradient)`.
- **Variable value**: expresses a changing quantity (capacity, intensity, progress) — don't use it to express depth. `Image(systemName: "speaker.wave.3", variableValue: 0.6)`; 26+ `.symbolVariableValueMode(.draw)`.
- **Effects**: Bounce (an event happened, one-shot), Pulse / Breathe (in progress), Rotate (spinning, e.g., a fan), Variable Color (progress or activity), Replace (swap symbols), Wiggle (draw attention), Scale (selection), Appear / Disappear, Draw On/Off (26+).
  - **Use one-shot effects (bounce, replace) for state changes; use looping effects only while something is ongoing, and stop when the state ends**; under Reduce Motion, go static or use replace.
- Weight should **match adjacent text**; adjust emphasis with `.imageScale(.small/.medium/.large)` without breaking weight alignment.
- Variants: outline suits toolbars, lists, and inline with text; fill suits iOS tab bars, swipe actions, and indicating selection. In most cases the container decides automatically.
- **License**: only for apps running on Apple platforms. **Not for web pages, HTML artifacts, presentations, app icons, or logos.**

## 11. iOS components **[Official]**

- Navigation: large titles help orientation and transition to a standard title on scroll.
- Toolbars: only the most important items; use system symbols for back/close — **don't write "Back" or "Close" as text**; primary action `.prominent` at the trailing end.
- **Tab bars**: for navigation, not actions; keep visible between sections; **the current HIG has dropped the count limit** (formerly 3–5), saying only the fewer the better and to avoid More; **don't disable or hide tabs** — if there's no content, explain why; you can put a search tab at the trailing end and add a bottom accessory.
- **Sheets**: `.presentationDetents([.medium, .large])`; show a grabber on resizable sheets; support swipe-down to dismiss, confirming when there are unsaved changes; in a single-page sheet, "Cancel" goes top left and "Done" top right.
- Lists: use inset grouped for settings-style screens (the default for SwiftUI `Form` on iOS); use a disclosure indicator for drill-down.
- Swipe actions use fill symbols.
- For choices related to a deliberate action, use an action sheet (confirmationDialog), at most 4 buttons (including Cancel), destructive at the top.
- Pull to refresh: also refresh automatically on a schedule; `.refreshable`.
- Search: search as people type; the placeholder says what can be searched; on iPhone, put it at the bottom when there's room.
- Haptics: use the system-defined meanings; don't overuse them; make them possible to turn off; `.sensoryFeedback(_:trigger:)`.

## 12. Code templates (SwiftUI, macOS)

### 12.1 Menu bar extra + user-removable
```swift
@main
struct MonitorApp: App {
    @AppStorage("showMenuBarExtra") private var showMenuBarExtra = true

    var body: some Scene {
        MenuBarExtra(isInserted: $showMenuBarExtra) {
            MonitorPanelView().frame(width: 320)
        } label: {
            Image(systemName: "thermometer.variable", variableValue: 0.6)
                .accessibilityLabel("CPU Temperature")   // recommended: the official docs say the title becomes the name, but the AX tree in the author's setup didn't show it (not verified with VoiceOver)
        }
        .menuBarExtraStyle(.window)   // use .window only for dense info; otherwise omit it (default menu)

        Settings {
            SettingsView(showMenuBarExtra: $showMenuBarExtra)
        }
    }
}
```

### 12.2 Settings (tabs, grouped form, immediate effect, remembered tab)
```swift
struct SettingsView: View {
    @Binding var showMenuBarExtra: Bool
    @AppStorage("settingsTab") private var tab = "general"
    @AppStorage("notifyOnHeat") private var notifyOnHeat = true

    var body: some View {
        TabView(selection: $tab) {
            Tab("General", systemImage: "gearshape", value: "general") {
                Form {
                    Section {
                        Toggle("Show in Menu Bar", isOn: $showMenuBarExtra)
                    }
                    Section("Alerts") {
                        Toggle("Notify When Temperature Is High", isOn: $notifyOnHeat)
                            .toggleStyle(.switch)
                            .controlSize(.mini)
                    }
                }
                .formStyle(.grouped)
            }
            Tab("Advanced", systemImage: "slider.horizontal.3", value: "advanced") {
                AdvancedSettingsView()
            }
        }
        .frame(width: 460)
    }
}
```

### 12.3 NavigationSplitView + inspector
```swift
NavigationSplitView {
    List(items, selection: $selection) { Label($0.name, systemImage: $0.symbol) }
        .navigationSplitViewColumnWidth(min: 180, ideal: 220, max: 300)
} detail: {
    DetailView(id: selection)
        .navigationTitle("Devices")
        .navigationSubtitle("3 Online")
        .inspector(isPresented: $showInspector) {
            InspectorView(id: selection)
                .inspectorColumnWidth(min: 220, ideal: 260, max: 360)
        }
        .toolbar {
            ToolbarItem {
                Button("Show Inspector", systemImage: "sidebar.trailing") { showInspector.toggle() }
            }
        }
}
// Scene: .commands { SidebarCommands(); InspectorCommands() }
```

### 12.4 Menu commands
```swift
.commands {
    CommandGroup(after: .appSettings) {
        Button("Check for Updates…") { checkForUpdates() }
    }
    CommandGroup(replacing: .newItem) { }      // remove "New" if you don't handle documents
    CommandMenu("Monitor") {
        Button("Refresh Now") { refresh() }
            .keyboardShortcut("r")
        Divider()
        Toggle("Pause Sampling", isOn: $paused)
            .keyboardShortcut("p", modifiers: [.command, .shift])
    }
}
```

### 12.5 Alert / confirmation dialog
```swift
.confirmationDialog("Delete all logs for “\(name)”?", isPresented: $confirm) {
    Button("Delete Logs", role: .destructive) { deleteLogs() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("You can’t undo this action.")
}
.dialogSuppressionToggle("Don’t Ask Again", isSuppressed: $suppress)

.alert("Can’t Connect to Sensor", isPresented: $failed) {
    Button("Try Again") { retry() }
        .keyboardShortcut(.defaultAction)
    Button("Cancel", role: .cancel) { }
} message: {
    Text("Make sure the USB cable is connected, then try again.")
}
```

### 12.6 Empty state
```swift
ContentUnavailableView {
    Label("No Devices", systemImage: "sensor")
} description: {
    Text("Readings will appear here after you connect a sensor.")
} actions: {
    Button("Add Device…") { addDevice() }
}
```

### 12.7 Floating panels
```swift
// Standard utility panel (macOS 15+)
UtilityWindow("Inspector", id: "inspector") { InspectorView() }

// Always-on-top monitoring mini window (deliberate deviation from the HIG; see §4.1)
Window("Temperature", id: "hud") { HUDView() }
    .windowLevel(.floating)
    .windowResizability(.contentSize)
    .restorationBehavior(.disabled)
```
```swift
// AppKit: a floating panel that doesn't steal focus
let panel = NSPanel(contentRect: rect,
                    styleMask: [.titled, .closable, .utilityWindow, .nonactivatingPanel],
                    backing: .buffered, defer: false)
panel.isFloatingPanel = true
panel.becomesKeyOnlyIfNeeded = true
panel.hidesOnDeactivate = false   // the default (and the HIG requirement) is to hide when the app is inactive; have a reason to change it
panel.title = "Temperature"
// For a full-window glass HUD (macOS 26+), use styleMask [.borderless, .nonactivatingPanel] and backgroundColor = .clear instead; see liquid-glass.md §3.1a
```

### 12.8 Status icon + Reduce Motion
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

## 13. Pitfalls
1. Main functionality only in the menu bar extra; color PNG icon; `.window` by default; no toggle to remove it.
2. Settings window with "OK / Apply / Cancel," resizable/minimizable, title not following the tab, not remembering the last tab; gear button in the main window toolbar.
3. Toolbar items without menu bar commands.
4. An icon stuffed into every menu item.
5. Context menu items dimmed instead of hidden, showing keyboard shortcuts, missing from the menu bar.
6. Alert overuse: at launch, purely informational, confirming every delete, "Yes/No," Cancel as default, destructive as default, deliberate actions marked red.
7. Popovers as warnings; popovers stacked on popovers; auto-dismiss discarding input.
8. Sheets stacked on sheets; a sheet where repeated interaction is needed.
9. Panels listed in the Window menu, with a minimize button, without a title bar; HUD as the default style.
10. Switches in the toolbar; switches for hierarchical settings; existing checkboxes replaced with switches.
11. Segmented control for main-window view switching; actions in a pop-up, options in a pull-down.
12. Just writing "Loading…"; switching from a spinner to a progress bar.
13. `.bouncy` as a global default; animating frequent interactions; ignoring Reduce Motion.
14. SF Symbols on web pages, app icons, or logos.
15. Overriding `mouseDown`; toggling the window yourself in the status item button action (on macOS 27, use expandedInterfaceSession).
16. ⌃ as the primary modifier; repurposing ⌘H / ⌘M / ⌘,.
