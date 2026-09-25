# Accessibility: VoiceOver, Keyboard, Text Size, Voice Control, Auditing

> Research machine: macOS 27.0 (Darwin 27), Xcode 27 (MacOSX27.0.sdk / iPhoneOS27.0.sdk), 2026-09-25. Sources: HIG Accessibility (2025-06-09 revision) and VoiceOver (new page, 2025-03-07), Focus and selection, Keyboards, Charts, Typography; Apple developer documentation (DocC JSON); the evaluation criteria for each App Store Connect "Accessibility Nutrition Labels" item; WWDC23-10035, WWDC26-220; SDK grep in the author's setup. **Measurements in the author's setup were taken by reading the SwiftUI-generated accessibility tree with NSAccessibility from within the same process** (VoiceOver was not turned on). Sources: see `SOURCES.md` in the repo.
>
> **Not repeated here**: contrast values and system color contrast are in `color-materials.md` §7; Reduce Motion animation code is in `macos-components.md` §9.2; how Liquid Glass degrades under Reduce transparency, Increase contrast, and Show borders is in `liquid-glass.md` §5; hit targets are in `typography-layout.md` §5.1.

## Contents
1. Principles
2. VoiceOver: label / value / hint / traits
3. Grouping, order, custom actions, rotors
4. Custom controls (SwiftUI / AppKit NSView)
5. Dynamic content notifications
6. Images and charts
7. macOS keyboard and focus
8. Menu bar apps and floating panels
9. Text size (macOS and iOS differ)
10. Voice Control
11. Other system settings at a glance
12. Automated auditing and Accessibility Nutrition Labels
13. Pitfalls

---

## 1. Principles [Official]
- The HIG's three requirements for accessible interfaces: **Intuitive** (familiar, consistent interactions), **Perceivable** (never convey information in only one way), **Adaptable** (respond to system settings).
- Standard components provide their own label, traits, keyboard operation, and Voice Control names. **Custom components must supply all of this themselves, to the same level as native components.** The App Store VoiceOver criteria require custom components to offer accessibility support equivalent to native ones.
- Passing every audit doesn't mean the app is accessible. Apple's words: "eliminating all audit issues … doesn't guarantee a fully accessible app". You still need to walk through common tasks with VoiceOver.
- **VoiceOver, Voice Control, and Switch Control don't work in Simulator** — test on a real device (per Apple's docs). On macOS, ⌘F5 toggles VoiceOver.

## 2. VoiceOver: label / value / hint / traits

| Attribute | Rule | Good | Bad | Evidence |
|---|---|---|---|---|
| **label** | Very short, identifies what the element is; **no control type** (traits carry the type) and **no state** | "Save" | "Save button", "Checked checkbox" | [Official] UIKit `accessibilityLabel`, SwiftUI `accessibilityLabel(_:)`, App Store VoiceOver criteria |
| Labels must make sense out of context | With multiple "Delete" controls on screen, say what gets deleted | "Delete CPU Sensor" | "Click here", "Learn more" | [Official] App Store criteria |
| **value** | Only when the element has a **current value** beyond its label (slider, progress, temperature) | label "Volume" + value "35%" | Giving a "Save" button the value "Save" | [Official] UIKit `accessibilityValue` |
| Text fields | Keep label and value separate: label "Phone Number", value is what the person typed | — | Using the placeholder as the label | [Official] App Store criteria |
| **hint** | Describes **what happens when you act on it**; a brief verb phrase; **doesn't repeat the element's name or describe the gesture** | "Opens Settings", "Downloads the attachment" | "Double-tap this row to select the message" | [Official] UIKit `accessibilityHint`, SwiftUI `accessibilityHint(_:)` |
| **traits** | Use traits for type and state (`.isButton`, `.isHeader`, `.isSelected`, `.isToggle`, `.updatesFrequently`) | — | Writing "button" into the label | [Official] |

**Writing style** [Inferred, applying the rules above]: labels are nouns or bare verbs ("Share", "Refresh", "CPU Temperature"), without "button" or "icon"; hints are verb + object ("Opens notification settings"), not "Double-tap to…" (VoiceOver announces how to operate the element on its own); include units in numbers ("72 degrees", "3,200 RPM") rather than symbolic forms like "72°C", which some voices mispronounce. For zh-TW: labels like「分享」「重新整理」「CPU 溫度」, hints like「開啟通知設定」(not「點兩下以⋯」), numbers like「72 度」.

**Measured (macOS 27, SwiftUI-generated AX tree; the author's system language is zh-TW, so auto-generated descriptions below are the zh-TW strings, with English glosses)**:
- `Button { Image(systemName: "gearshape") }` with no label gives VoiceOver **the SF Symbol's automatic description**「齒輪形狀」("gear shape"), not "Settings". **`.help("Settings")` only becomes AXHelp, not the label** — write both.
- `Label("Filter", systemImage:)` with `.labelStyle(.iconOnly)` still has the label "Filter" — **the easiest way to build an icon button**.
- `.accessibilityHint(...)` maps to **AXHelp** on macOS (VoiceOver reads it after a delay, or on VO‑⇧‑H).
- `.accessibilityAddTraits(.isHeader)` has the role **AXHeading** on macOS 26 and later (`NSAccessibilityHeadingRole` is new in macOS 26).
- `Toggle` defaults to AXCheckBox; `.toggleStyle(.switch)` is AXCheckBox / subrole AXSwitch, and **the label is a separate text element next to it, not on the switch itself**.
- A shape-only view (`Circle()`) made into `.accessibilityElement()` has the role **AXUnknown, and its value isn't exposed**. Attach status dots to a Text / Label, or merge the whole row into one element with `children: .ignore` (see §3).

```swift
// Icon buttons: an iconOnly Label is easiest; for custom icons, set the label explicitly and add help separately (tooltip ≠ label)
Button("Refresh", systemImage: "arrow.clockwise") { reload() }
    .labelStyle(.iconOnly)
    .help("Refresh")
Button { openSettings() } label: { Image(systemName: "gearshape") }
    .accessibilityLabel("Settings")
    .help("Settings")
```

## 3. Grouping, order, custom actions, rotors

### 3.1 `accessibilityElement(children:)` [Official + Measured]
| Value | Behavior | Use for |
|---|---|---|
| `.ignore` (default) | Creates a new element and **ignores all children**; you supply label / value yourself | Rows where you want to control exactly what's spoken (recommended) |
| `.combine` | **Merges** the properties of non-hidden children into one; some traits aren't merged; child buttons' default actions become named actions | Icon + name + value rows |
| `.contain` | Becomes a **container** and keeps its children; VoiceOver finishes this container before moving to the next | Sidebar sections, card groups, message lists |

Measured: `HStack { Image("cpu"); Text("CPU"); Text("72°C") }.accessibilityElement(children: .combine)` yields a single AXStaticText with the value "CPU, 72°C" — **the image is dropped**. If state is conveyed only by an icon (e.g., a flame meaning overheating), `.combine` loses that information; use `.ignore` and write the value yourself:

```swift
HStack {
    Image(systemName: hot ? "flame.fill" : "thermometer.medium")
    Text(name); Spacer(); Text("\(temp)°C").monospacedDigit()
}
.accessibilityElement(children: .ignore)
.accessibilityLabel(name)
.accessibilityValue(hot ? "\(temp) degrees, overheating" : "\(temp) degrees")
```

### 3.2 Order
- VoiceOver reads in the language's reading direction (top to bottom, left to right for both English and Chinese). **Tell VoiceOver about visual relationships (like an image and its caption) through grouping**, or it reads all the images before any captions. [Official HIG VoiceOver]
- Adjust order with `accessibilitySortPriority(_:)`: higher numbers are read first, the default is 0, and it only compares elements at the same level. [Official]
- Each screen should have a unique title; mark section titles with `.isHeader` so VoiceOver users can jump between headings with the rotor. [Official]

### 3.3 Custom actions [Official + Measured]
- Buttons that appear only via context menu, long press, swipe, or hover **must also be provided as custom actions** (App Store VoiceOver criteria; Voice Control relies on them too — saying "Show actions for 3" brings them up).
- The `Text` variant of `accessibilityAction(named:)` is iOS 13 / macOS 10.15+; the `LocalizedStringKey` variant used by string literals is iOS 14 / macOS 11+ (the `StringProtocol` variable variant arrived in iOS 16 / macOS 13). Measured: on macOS these become `NSAccessibilityCustomAction`s, **presented in reverse declaration order** (the last declared comes first), so declare the most common action last.

```swift
Text(subject)
    .contextMenu { Button("Archive", action: archive); Button("Mark as Read", action: markRead) }
    .accessibilityAction(named: "Archive", archive)
    .accessibilityAction(named: "Mark as Read", markRead)
```

### 3.4 Rotor [Official + SDK]
```swift
ScrollView { LazyVStack { ForEach(messages) { MessageRow($0) } } }
    .accessibilityElement(children: .contain)
    .accessibilityRotor("Flagged") {
        ForEach(messages.filter(\.isFlagged)) { m in AccessibilityRotorEntry(m.subject, id: m.id) }
    }
```
- **Pitfall [SDK-verified]**: Apple's documentation sample writes `if m.isFlagged { … }` inside the rotor's `ForEach`. That requires `Optional: AccessibilityRotorContent`, a conformance that **only exists in macOS 27 / iOS 27**. Targeting 26, Swift 6 fails to compile outright and Swift 5 warns. Filter first, then pass to `ForEach`.
- System rotors for text navigation: `.accessibilityRotor(.headings)` and so on.

## 4. Custom controls

### 4.1 SwiftUI: use a style if you can, a representation if you can't [Official]
The order of preference: **a custom `ButtonStyle` / `ToggleStyle`** (accessibility behavior is inherited automatically) → `accessibilityRepresentation` (an invisible standard control stands in for it) → manually supply label, value, traits, and actions.

```swift
// A custom-drawn tachometer → a Slider to assistive technologies (measured: AXSlider, label "Fan Speed", min/max correct)
FanDial(rpm: $rpm)
    .accessibilityRepresentation {
        Slider(value: $rpm, in: 0...6000, step: 100) { Text("Fan Speed") }
    }

// Manual version: an adjustable element
Text("Level \(level)")
    .accessibilityElement()
    .accessibilityLabel("Level").accessibilityValue("\(level)")
    .accessibilityAdjustableAction { dir in
        switch dir {
        case .increment: level = min(level + 1, 5)
        case .decrement: level = max(level - 1, 1)
        @unknown default: break
        }
    }
```
- A custom control needs at least: **label**, **value** (if it has one), **trait or role**, **primary action** (`accessibilityAction { }`), **adjustable action** (if the value can be adjusted), **keyboard operation** (§7), and **a notification when the value changes**. [Official: the four aspects in WWDC26-220 — purpose, value, action, feedback]
- Other APIs from WWDC26-220: `accessibilityActivationPoint`, `accessibilityDirectTouch(_:)` (iOS 17 / macOS 14; `.requiresActivation`, `.silentOnTouch`). If you use direct touch, **also provide custom actions** for Switch Control and Voice Control. [Official]

### 4.2 AppKit: minimal implementation for a custom NSView [SDK]
- Use the **role-based protocols** (`NSAccessibilityButton`, `NSAccessibilitySwitch`, `NSAccessibilityCheckBox`, `NSAccessibilitySlider`, `NSAccessibilityStaticText`, …), and the compiler requires you to implement the necessary methods. For example, Button needs `accessibilityLabel()` + `accessibilityPerformPress()`; Slider needs label, value, increment, decrement.
- Otherwise, override `isAccessibilityElement()`, `accessibilityRole()`, `accessibilityLabel()`, `accessibilityValue()`. **Post `.valueChanged` when the value changes** (the protocol header comments explicitly require it).
- For virtual elements outside the view hierarchy (e.g., points in a canvas), use `NSAccessibilityElement` and convert frames with `NSAccessibilityFrameInView`.

```swift
final class LevelMeterView: NSView {
    var level: Double = 0 { didSet { needsDisplay = true
        NSAccessibility.post(element: self, notification: .valueChanged) } }
    override func isAccessibilityElement() -> Bool { true }
    override func accessibilityRole() -> NSAccessibility.Role? { .levelIndicator }
    override func accessibilityLabel() -> String? { "CPU Usage" }
    override func accessibilityValue() -> Any? { NSNumber(value: level) }
    override func accessibilityMinValue() -> Any? { NSNumber(value: 0) }
    override func accessibilityMaxValue() -> Any? { NSNumber(value: 1) }
}
final class PillButton: NSView, NSAccessibilityButton {   // In Swift 6 mode, write @preconcurrency NSAccessibilityButton
    var title = "Start"; var action: () -> Void = {}
    override var acceptsFirstResponder: Bool { true }
    override var canBecomeKeyView: Bool { true }             // Makes it reachable with Tab
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
- AX constants new in macOS 26 [SDK]: `NSAccessibilityHeadingRole`, `HeadingLevelAttribute`, `LanguageAttribute`, `VisitedAttribute`, `ScrollToVisibleAction`, `BlockQuoteLevelAttribute`, `FontBold/ItalicAttribute`.

## 5. Dynamic content notifications [Official]
When content or layout changes, **notify for anything visible**; otherwise the VoiceOver user's mental picture of the screen drifts from reality.

| Situation | SwiftUI (iOS 17 / macOS 14+, Accessibility framework, re-exported by SwiftUI) | AppKit |
|---|---|---|
| Speak a message (sync finished, error) | `AccessibilityNotification.Announcement(msg).post()` | `NSAccessibility.post(element:notification: .announcementRequested, userInfo: [.announcement:…, .priority:…])` |
| Part of the layout changed | `AccessibilityNotification.LayoutChanged(element?).post()` | `.layoutChanged` |
| New screen, large content replacement | `AccessibilityNotification.ScreenChanged(element?).post()` | Move focus to the new window |
| Scrolling finished | `.PageScrolled` | — |

```swift
var msg = AttributedString("Sync complete, 12 items updated")
msg.accessibilitySpeechAnnouncementPriority = .high   // .high interrupts current speech and can't itself be interrupted mid-announcement
AccessibilityNotification.Announcement(msg).post()
```
- **Don't announce every change of a continuously changing value.** WWDC26-220's approach: announce only when enough time has passed since the last announcement **and** the value has actually changed. Add the `.updatesFrequently` trait to elements that change constantly. [Official]
- Background refreshes must not send the VoiceOver reading position back to the top; when a modal appears, the VoiceOver cursor must move into it and **background content must become unreachable**; `Esc` / `accessibilityPerformEscape` must dismiss the modal. [Official App Store criteria]
- Use auto-dismissing toasts or banners sparingly; if you must, announce them and keep them up long enough, or make them manually dismissible. [Official HIG Cognitive]

## 6. Images and charts [Official]
- Describe meaningful images; **describe only the information the image itself conveys** — VoiceOver reads the adjacent caption on its own.
- Purely decorative images: `Image(decorative:)` or `.accessibilityHidden(true)` (measured: both remove the image from the tree).
- Charts:
  - Make titles and subtitles state the takeaway directly.
  - Swift Charts includes Audio Graphs, and each mark has a default element.
  - For custom-drawn charts, use `accessibilityChartDescriptor(_:)`, or at least provide a complete text alternative.
  - Labels give **actual values and context** (dates, places), not subjective words ("sharply", "almost"), and **don't describe colors** (not "the red line" — say what the line represents).
  - Hide the visible axis and tick text from VoiceOver.
  - Interactive charts must also be operable with the keyboard and Switch Control (`accessibilityRespondsToUserInteraction`).
  - Important information must not be visible only after interaction.

## 7. macOS keyboard and focus

### 7.1 Two different system settings [Official SDK headers + HIG]
| Setting | Location | Effect | How to read it |
|---|---|---|---|
| **Keyboard navigation** | System Settings › Keyboard | When on, Tab moves to **all** controls (buttons, checkboxes); when off, Tab moves only between text fields and lists | `NSApp.isFullKeyboardAccessEnabled` (badly named — it's actually this setting; not KVO-compliant, read it directly each time) |
| **Full Keyboard Access** | System Settings › Accessibility › Keyboard | Accessibility feature: focus gets a highlighted outline, and all UI can be operated, including gestures | No public API |

- HIG: iPadOS / macOS have Full Keyboard Access, so **an app only needs to make "content elements" (list items, text fields, search fields) focusable; leave controls like buttons, sliders, and switches to the system** — don't build your own keyboard navigation for controls.
- **Tab moves between focus groups; arrow keys move within a group**; order is front to back, top to bottom.
- Focus appearance: text fields and search fields use a focus ring; lists and collections use full-row highlighting (accent-color background + white text).
- Don't override system shortcuts (Control‑F1 through F3, ⌘F5, and others used by accessibility). [Official HIG Keyboards]

### 7.2 SwiftUI focus APIs [SDK]
| API | Availability | Purpose |
|---|---|---|
| `@FocusState` + `.focused(_:equals:)` | macOS 12 / iOS 15 | Control focus programmatically; move to the next field on submit |
| `.defaultFocus(_:_:priority:)` | macOS 13 / iOS 17 | Default focus when a window first appears; `.userInitiated` also applies during user navigation |
| `.focusable(_:)` | macOS 12 / iOS 17 | Make a custom view focusable |
| `.focusable(interactions: .activate / .edit)` | macOS 14 / iOS 17 | Participate only in "activate" focus (button-like) or "edit" focus (text-like) |
| `.focusSection()` | **macOS 13+ / tvOS only** | Tab visits this section's children before moving to the next section; arrow keys can also direct focus into the section |
| `.onKeyPress` | macOS 14 / iOS 17 | Custom key handling (Space to activate, etc.) |
| `.focusEffectDisabled()` | macOS 14 | Turn off the system focus effect when you draw your own |
| `.accessibilityDefaultFocus(_:_:)` | **26** | Default position of the VoiceOver cursor (a separate `AccessibilityFocusState`, distinct from keyboard focus) |

```swift
// Form: default focus + Return moves to next field + default button
Form {
    TextField("Account", text: $account).focused($focus, equals: .account)
    SecureField("Password", text: $password).focused($focus, equals: .password).onSubmit(signIn)
    Button("Sign In", action: signIn).keyboardShortcut(.defaultAction)
}
.defaultFocus($focus, .account)

// A custom clickable card: keyboard, mouse, and VoiceOver all need to work
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
- AppKit Tab order: chain `nextKeyView` into a loop, or set `window.autorecalculatesKeyViewLoop = true`. Custom views need `acceptsFirstResponder` + `canBecomeKeyView` and must draw a focus ring (`focusRingMaskBounds`, `drawFocusRingMask`). [SDK]

## 8. Menu bar apps and floating panels
- **⚠ Contradicts the official docs (which say the title becomes the name; not verified with VoiceOver on). Measured (macOS 27, reading the AX tree): the first argument of `MenuBarExtra("CPU Temperature", systemImage: "thermometer.medium")` does not become the accessibility title of the status bar button.** VoiceOver gets the SF Symbol's automatic description (「指示中等溫度的溫度計」, "thermometer indicating medium temperature", in the author's zh-TW locale). `Label("Temperature Monitor", systemImage:)` behaves the same way, yielding「指向中刻度的儀表」("gauge pointing to the middle mark"). **Only a `label:` closure with `.accessibilityLabel("Fan Guard")` on the Image works**:
  ```swift
  MenuBarExtra { MenuContent() } label: {
      Image(systemName: "fanblades").accessibilityLabel("Fan Guard")
  }
  ```
  In AppKit, set `statusItem.button?.image?.accessibilityDescription` or call `button.setAccessibilityLabel(_:)`. [Measured + SDK]
- If the status bar icon conveys state (temperature high/low), **put the state in the label or value too**, e.g., "CPU temperature, 88 degrees, overheating", and update it when the state changes. [Inferred, per §2]
- Floating `NSPanel` (`.nonactivatingPanel`) [Inferred, not tested with VoiceOver]:
  - A panel that never becomes the key window is hard to reach with the keyboard and VoiceOver.
  - Provide a menu bar command or shortcut that brings the panel forward and makes it key (override `canBecomeKey` to return true, or use `becomesKeyOnlyIfNeeded`).
  - Set the panel's `title` so it has a name in VoiceOver's window list.
  - Support `Esc` to close (`cancelOperation(_:)`).
- **Every primary feature of a menu bar app must be operable from menu items.** Menus are system components and get VoiceOver and keyboard support for free; custom SwiftUI window content you must check yourself.

## 9. Text size (macOS and iOS differ)

### 9.1 macOS: third-party SwiftUI apps don't follow the system Text size [Official + Measured]
- Since macOS 14, System Settings › Accessibility › Display has **Text size**, **but it applies only to the listed Apple apps and system components**: Finder, Mail, Messages, Notes, Reminders, Calendar, Books, Stocks, Weather, Journal, Magnifier, Accessibility Reader (the `FontSizeCategory` list in `com.apple.universalaccess` in the author's setup is exactly these).
- **Measured**: with the global setting at XXL in the author's setup, a third-party SwiftUI app still reads `dynamicTypeSize` as `.large` and `.body` is still 13pt; **forcing `.dynamicTypeSize(.accessibility5)` doesn't enlarge text either, and `@ScaledMetric` doesn't scale**. Apple's docs: "On macOS, this value cannot be changed by users and does not affect the text size."
- The macOS 26 / 27 SDKs have **no** new text-size API (AppKit has no content size category), and nothing was announced at WWDC25 / 26. The App Store Larger Text label explicitly says "**All except Mac**" — Mac apps can't claim it.
- The HIG still asks that people "ideally be able to enlarge text to at least 200%", which can be achieved with "custom UI". **On the Mac you have to build text enlargement yourself**: offer an in-app text size setting (store a multiplier in `@AppStorage`, then `.font(.system(size: 13 * scale))`, or `⌘+` / `⌘-`), especially for reading-oriented content. The system's Zoom and Hover Text don't count as app support (App Store criteria, verbatim).

### 9.2 iOS: adapting layout for Dynamic Type [Official]
- The goal is no overlap and no severe truncation at AX5, with the information hierarchy intact; **AX3 is roughly 200%**, and AX5 is over 300% (App Store criteria).
- Switching horizontal to vertical:
  - Use `dynamicTypeSize.isAccessibilitySize` to switch between `AnyLayout(HStackLayout…)` / `AnyLayout(VStackLayout…)` (view identity is preserved across the switch, so animation is smoother).
  - Or use `ViewThatFits(in: .horizontal)`: list versions from "ideal" to "fallback", and the first that fits is chosen.
- Scale non-text dimensions with `@ScaledMetric(relativeTo:)`; SF Symbols scale with Dynamic Type on their own.
- **Range limits like `.dynamicTypeSize(...DynamicTypeSize.xxxLarge)`**: use them only on small components that truly have no room (badges, tab bar, toolbar icons), **and pair them with the Large Content Viewer**. **Never apply them to a whole screen or the root view** — that effectively turns off accessibility text sizes. The range clamps values set *outside* it, so write the range modifier first (innermost) in the chain (documentation example: range first, then `.xLarge`, results in `.large`).
- Large Content Viewer: `.accessibilityShowsLargeContentViewer()` or the variant that takes content, for components that **must stay small**. **It can't substitute for Dynamic Type** (per the docs).

```swift
Text("\(count)").font(.caption2.bold()).padding(4).background(.red, in: Capsule())
    .dynamicTypeSize(...DynamicTypeSize.xxxLarge)                 // Badge doesn't grow into AX sizes
    .accessibilityShowsLargeContentViewer { Label("\(count) unread", systemImage: "envelope.badge") }
```

## 10. Voice Control [Official]
- Saying "Show names" displays each element's name, and people say "Click <name>" (iOS: "Tap <name>") to operate it. **The label must match the visible text.** If a button reads "End Call" but its label is "Leave Call", people can't invoke it (the example given verbatim in the App Store criteria).
- For icon buttons, use the word people would naturally say as the label; put synonyms in `accessibilityInputLabels`, **ordered by importance, with the first matching the visible text or label**. **Full Keyboard Access also uses input labels** (per the docs).
  ```swift
  Button { share() } label: { Image(systemName: "square.and.arrow.up") }
      .accessibilityLabel("Share")
      .accessibilityInputLabels(["Share", "Send", "Export"])   // Measured: exposed as AXUserInputLabels on macOS
  ```
  The AppKit counterpart is `accessibilityUserInputLabels()` (macOS 14); in UIKit it's `accessibilityUserInputLabels`.
- When a label is long (e.g., "Delete CPU Sensor"), add a short input label ("Delete").
- Hover-only UI, swipe-only actions, and drag and drop all need a voice-accessible alternative (context menu, custom actions). Test dictation editing commands like "Select …" and "Delete that" in custom text fields.

## 11. Other system settings at a glance

| Setting | SwiftUI environment value | Availability / platform | How to respond | Evidence |
|---|---|---|---|---|
| Differentiate without color | `accessibilityDifferentiateWithoutColor` | All platforms | Add icons (✓ / ✕) or text to status dots; add shapes or patterns to charts. **Don't rely on color alone by default** — this setting is an extra reinforcement | [Official] |
| Bold Text | `legibilityWeight == .bold` | iOS / tvOS / watchOS; **macOS has no such setting** (measured: reads `nil`) | System fonts get bolder automatically; custom font weights and hand-drawn strokes should follow | [Official + Measured] |
| Button Shapes / Show borders | `accessibilityShowBorders` (the old `accessibilityShowButtonShapes` is deprecated, renamed; the new name back-deploys to iOS 14 / macOS 11) | iOS "Button Shapes"; macOS 27 "Show borders" | Add an underline or outline to borderless text or icon buttons | [SDK] |
| On/Off Labels | **No SwiftUI environment value**; UIKit `UIAccessibility.isOnOffSwitchLabelsEnabled` + `onOffSwitchLabelsDidChangeNotification` | iOS | Standard `Toggle` handles it; custom-drawn switches need I / O marks | [SDK] |
| Invert Colors / Smart Invert | `accessibilityInvertColors`; use `.accessibilityIgnoresInvertColors()` on photos, video, avatars | iOS 14 / macOS 11 | Don't let photos, maps, or video get inverted | [SDK] |
| Prefer cross-fade transitions | `accessibilityPrefersCrossFadeTransitions` | **26.4** | Replace slide / scale transitions with `.opacity` | [SDK] |
| Reduce highlighting effects | `accessibilityReduceHighlightingEffects` | **26.4** | Minimize button highlights, flashes, and glow effects | [Official] |
| Dim flashing lights | `accessibilityDimFlashingLights` | iOS 17 / macOS 14 | Dim flashes in video or animation | [SDK] |
| Auto-play animated images | `accessibilityPlayAnimatedImages` | iOS 17 / macOS 14 | When false, GIFs / APNGs stay on the first frame | [SDK] |
| VoiceOver / Switch Control running | `accessibilityVoiceOverEnabled`, `accessibilitySwitchControlEnabled` | macOS 12 / iOS 15 | **Use only to adjust behavior** (e.g., don't auto-hide controls), **not to swap in a different UI** | [SDK] |
| AppKit counterparts | `NSWorkspace.shared.accessibilityDisplayShould{IncreaseContrast, DifferentiateWithoutColor, ReduceTransparency, ReduceMotion, InvertColors}`, `isVoiceOverEnabled`; changes arrive via `NSWorkspace.accessibilityDisplayOptionsDidChangeNotification` | macOS | — | [SDK] |

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
            Text(ok ? "Normal" : "Error")          // The text itself keeps state from relying on color alone
        }
        .padding(.horizontal, 6)
        .overlay { if showBorders || contrast == .increased { Capsule().strokeBorder(.secondary) } }
    }
}
```

## 12. Automated auditing and Accessibility Nutrition Labels

### 12.1 `performAccessibilityAudit` (XCUITest) [Official + SDK]
- `XCUIApplication.performAccessibilityAudit(for:_:)`: iOS 17 / macOS 14+, Xcode 15+ (current docs and headers place it in the **XCUIAutomation** framework, with docs marked Xcode 16.3). Issues **fail the test automatically** — no asserts needed. **It only checks elements currently on screen**, so run it once per screen.
- Audit types (**they differ by platform; using another platform's type won't compile** — measured: `.dynamicType` errors on macOS):

| Type | Platform | What it checks |
|---|---|---|
| `.sufficientElementDescription` | All | Whether elements have specific, descriptive labels |
| `.contrast` | All | Color contrast between overlapping elements |
| `.hitRegion` | All | Whether hit targets are too small |
| `.elementDetection` | All | Content that isn't exposed as an element |
| `.dynamicType`, `.textClipped`, `.trait` | iOS / tvOS / watchOS | Dynamic Type support, text clipped when enlarged, attributes required by traits |
| `.action`, `.parentChild` | **macOS** | Whether actions are valid for the element type; whether parent/child relationships point both ways (parent lists child, and child's parent is that parent) |

```swift
@MainActor func testMainWindowAudit() throws {
    let app = XCUIApplication(); app.launch()
    try app.performAccessibilityAudit(for: [.sufficientElementDescription, .contrast, .hitRegion,
                                            .elementDetection, .action, .parentChild]) { issue in
        // Return true = ignore this issue. Ignore only confirmed false positives, with a comment explaining why
        issue.auditType == .contrast && issue.element?.identifier == "decorativeWatermark"
    }
}
```

### 12.2 Accessibility Inspector [Official]
- Open it via Xcode › Open Developer Tool › Accessibility Inspector, and pick your app as the target in the top-left.
- **Inspection**: point at an element to see its label, value, traits, and actions. Useful for confirming the measured behavior in §2, such as SF Symbol automatic descriptions and the difference between help and label.
- **Audits**:
  - All platforms: Element description, Hit region, Contrast, Element detection.
  - macOS only: Parent/child, Action.
  - Results include a Fix suggestion; you can capture a screenshot of the offending element, and export an HTML report with File › Save Audit Report As….
- **Settings**: toggle Invert colors, Increase contrast, Reduce transparency, Reduce motion, Full Keyboard Access, Differentiate without color, and more directly (this changes the target device's system settings — **remember to switch them back after testing**). There's also a color contrast calculator (⌥⌘C).

### 12.3 App Store "Accessibility Nutrition Labels" (since 2025) [Official]
- Currently **voluntary, and will become required for submission** (no timeline announced yet). Shown on App Store product pages on iOS / macOS 26 and later; people can search with terms like "VoiceOver notes app".
- **There's only one criterion: you may claim a feature only if all "common tasks" can be completed using that feature alone.** Common tasks include:
  1. Primary functionality (what the product page and screenshots promote)
  2. First-launch flow
  3. Sign-in (including sign-up and forgot password)
  4. Purchasing
  5. Settings
  6. Also counted: widgets, notifications, the default launch screen
- Criteria summary:

| Label | Mac eligible? | Key criteria |
|---|---|---|
| VoiceOver | ✓ | Labels concise, no type or state; all visible text is spoken; logical order with no skipping or looping; modal background unreachable and `Esc` dismisses; context menus and long presses have custom actions; charts have text alternatives |
| Voice Control | ✓ (not applicable to Apple TV, Watch) | Label = visible text; every interaction achievable by voice; custom text fields support dictation editing |
| Larger Text | **✗ (All except Mac)** | Enlarges to ≥200%; custom in-app text sizing counts; system zoom **doesn't** |
| Dark Interface | ✓ | Every screen in common tasks has a dark mode (a custom dark color scheme counts) |
| Differentiate Without Color Alone | ✓ | Important information isn't distinguished by color alone |
| Sufficient Contrast | ✓ | Text ≥4.5:1, **non-text controls and states ≥3:1**; may be met via the Increase contrast setting; test both light and dark; recommended to test with Bold Text, Increase contrast, and Reduce transparency on together |
| Reduced Motion | ✓ | With the setting on, animations are reduced or changed |
| Captions / Audio Descriptions | ✓ | Media in common tasks has synchronized captions and audio descriptions |

- VoiceOver and Voice Control **can't be replaced with custom implementations** — use the native APIs; other labels can be implemented yourself (e.g., a custom dark color scheme). [Official]
- Inaccurate labels can prompt App Review to require changes (Guideline 2.3).

## 13. Pitfalls
1. Icon buttons with only `.help()` and no label: VoiceOver reads the SF Symbol's automatic description ("gear shape"), not the function name.
2. The title in `MenuBarExtra("Title", systemImage:)` didn't become the status bar button's label in AX tree measurements (the official docs say it does; not verified with VoiceOver on — add it anyway to be safe). Use a `label:` closure and put `.accessibilityLabel` on the Image.
3. Writing "button", "icon", or "checked" in labels, or "Double-tap to…" in hints.
4. In rows merged with `.combine`, state conveyed only by an icon is dropped. Use `.ignore` and write the value yourself.
5. Shape views as standalone elements: role AXUnknown, value not exposed (measured).
6. An `if` inside a rotor's `ForEach`: compile failure or warning when targeting 26 (the Optional conformance requires 27).
7. Declaring custom actions without thinking about order: macOS presents them in reverse declaration order.
8. Context menus, hover buttons, and swipe actions not also provided as custom actions — VoiceOver and Voice Control users can't reach them.
9. Visible text doesn't match the label (Voice Control can't invoke it); the first input label isn't the visible text.
10. Assuming SwiftUI on macOS follows the system Text size or `dynamicTypeSize`. It doesn't — build in-app text sizing. Mac apps can't claim the Larger Text label.
11. Locking text size with `.dynamicTypeSize(...(.large))` on the root view; or using the Large Content Viewer instead of Dynamic Type.
12. Assuming `NSApp.isFullKeyboardAccessEnabled` is the Full Keyboard Access accessibility feature. It's actually the Keyboard navigation setting.
13. A custom NSView that's clickable but lacks `canBecomeKeyView` / focus ring / Space to activate (unreachable with Tab); not posting `.valueChanged` when the value changes.
14. Swapping in a whole different UI based on `accessibilityVoiceOverEnabled`; or announcing value changes too frequently.
15. Writing `performAccessibilityAudit(for: .dynamicType)` on macOS (won't compile); using the closure to ignore an entire category of issues; assuming passing all audits means the app is accessible.
16. `accessibilityShowButtonShapes` is deprecated; use `accessibilityShowBorders`.
17. Testing VoiceOver or Voice Control in Simulator (unsupported); forgetting to switch settings back after toggling them in Accessibility Inspector.
