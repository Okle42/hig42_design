# Liquid Glass (iOS 26 / macOS Tahoe 26 → iOS 27 / macOS 27)

> SwiftUI / AppKit examples have been verified against the macOS 27 SDK with `swiftc -typecheck`. Sources: see `SOURCES.md` in the repo.

## Contents
1. When to use it, and when not to
2. SwiftUI API
3. AppKit API
4. UIKit API (summary)
5. Accessibility and user settings
6. Adoption / migration checklist
7. What changed in 27
8. Fallback for older systems
9. Pitfalls

---

## 1. Which layer it belongs to **[Official]**

- Liquid Glass is a **functional-layer** material: toolbars, tab bars, sidebars, and floating controls that sit above content.
- **Don't use it in the content layer** (list cells, card backgrounds). Layer content with standard materials (`.regularMaterial`) or solid colors. Exception: Slider and Toggle temporarily turn into glass while being manipulated.
- **No glass on glass**: buttons inside a glass toolbar shouldn't get another `.glassEffect()`; a sheet is already glass, so don't put glass cards inside it.
- There are two variants — **don't mix them**:
  - `regular` (default): blurs and adjusts luminosity, and adapts to what's behind it. Text-heavy components (alerts, sidebars, popovers) must use it. **Exception (deliberate deviation from the HIG, measured in a single case): for a floating panel whose entire window is glass over an uncontrollable background, regular turns gray along with the background — use clear + tint instead; see §3.1a.**
  - `clear`: highly transparent, non-adaptive. Use it only when all three conditions hold: the content underneath is rich media such as photos or video, you can add a dimming layer, and the text/symbols on top are bold and bright. When the content underneath skews bright, add a dark layer at roughly 35% opacity.
- Use glass on custom components "sparingly" — reserve it for the most important functional elements.
- Color: to give your app color, **put the color in the content layer** and let the glass pick it up; tint only 1–2 primary actions; don't tint everything (if everything is colored, nothing stands out).
- In the resting state (e.g., just opened, scrolled to the top), avoid content overlapping glass controls.
- Toolbars: group by function into at most about 3 groups; keep text buttons and icon buttons separate; one `.prominent` primary action per toolbar, placed at the trailing end; don't apply glass to non-interactive elements (titles, status text).

## 2. SwiftUI API (iOS 26.0 / macOS 26.0+ unless marked 27; unavailable on visionOS) **[SDK]**

### 2.1 glassEffect
```swift
func glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape()) -> some View
// Default shape is Capsule
```
**Apply it after appearance modifiers such as `.padding()` and `.frame()`**, otherwise the glass only wraps the text.
```swift
Label("62°C", systemImage: "thermometer.medium")
    .padding()
    .glassEffect()                                      // capsule, regular

StatusSummary()
    .padding(12)
    .glassEffect(in: .rect(cornerRadius: 16))           // rounded rect for larger components

Label("Pause", systemImage: "pause.fill")
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())  // tint + interactive feedback

Label("Full Screen", systemImage: "arrow.up.left.and.arrow.down.right")
    .padding()
    .glassEffect(.clear)
    .background(.black.opacity(0.3), in: Capsule())     // clear always needs a dimming layer

chip.glassEffect(isOn ? .regular : .identity)           // turn it off conditionally without restructuring the view
```
- `Glass`: `.regular`, `.clear`, `.identity`; `.tint(_ color: Color?)`, `.interactive(_ isEnabled: Bool = true)`.
- Starting in macOS 27, `.interactive()` gives a slight bounce on click — use it only on buttons or containers that hold buttons.

### 2.2 GlassEffectContainer and morphing
Multiple pieces of custom glass **must be wrapped in a container**: glass can't sample other glass, so only pieces in the same container look consistent, morph correctly, and perform better.
```swift
struct FanControls: View {
    @State private var showsModes = false
    @Namespace private var glassSpace

    var body: some View {
        GlassEffectContainer(spacing: 16) {          // no larger than the HStack spacing, so pieces don't merge at rest
            HStack(spacing: 16) {
                Button("Fan", systemImage: "fan") { withAnimation(.smooth) { showsModes.toggle() } }
                    .padding(10)
                    .glassEffect(.regular.interactive())
                    .glassEffectID("fan", in: glassSpace)
                if showsModes {
                    Button("Quiet", systemImage: "speaker.slash") { }
                        .padding(10)
                        .glassEffect(.regular.interactive())
                        .glassEffectID("quiet", in: glassSpace)   // grows out of the "Fan" glass when expanding
                }
            }
        }
    }
}
```
- If the container `spacing` is larger than the inner stack spacing, the pieces merge into one blob even at rest.
- `glassEffectID` / `glassEffectTransition(.matchedGeometry / .materialize / .identity)` only take effect during transition animations.
- `glassEffectUnion(id:namespace:)`: merges non-adjacent views into a single piece of glass, even at rest.

### 2.3 Buttons
```swift
Button("Start Monitoring") { }.buttonStyle(.glassProminent)     // primary action (accent-colored background), 1–2 per screen
Button("View History") { }.buttonStyle(.glass)                  // secondary
Button("Screenshot") { }.buttonStyle(.glass(.clear))            // floats over imagery (typechecks with an iOS / macOS 26.0 target)
```
Related: `.buttonBorderShape(.capsule)`, `.controlSize(.extraLarge)`, `.buttonSizing(.flexible)`.

### 2.4 Toolbar
```swift
.toolbar {
    ToolbarItemGroup {
        Button("Previous", systemImage: "chevron.left") { }
        Button("Next", systemImage: "chevron.right") { }
    }
    ToolbarSpacer(.fixed)                    // splits the shared glass background
    ToolbarItem { ShareLink(item: reportURL) }
    ToolbarItem { AccountBadge() }
        .sharedBackgroundVisibility(.hidden) // opt out of the shared glass (e.g., an avatar)
}
```
- **To hide a toolbar item, hide the whole item, not the view inside it** — otherwise you're left with an empty piece of glass.
- New in 27: `visibilityPriority(_:)` (iOS 27 / macOS 26.1), `ToolbarOverflowMenu` (iOS 27, unavailable on macOS), `.topBarPinnedTrailing` (iOS 27), `contentMarginsRemoved()`, `toolbarMinimizationBehavior(_:for:)` (note: `toolbarMinimizeBehavior`, as spoken by the WWDC26 presenter, is not the correct name; values such as `.onScrollDown` are unavailable on macOS).

### 2.5 Scroll edge effect and background extension
```swift
ScrollView { ... }
    .scrollEdgeEffectStyle(.hard, for: .top)  // .automatic / .soft / .hard
    .safeAreaBar(edge: .bottom) { StatusBar() }   // custom bars get the edge effect too

NavigationSplitView { DeviceList() } detail: {
    ScrollView {
        Image("cover").resizable().aspectRatio(contentMode: .fill)
            .backgroundExtensionEffect()      // mirrored blur extends under the sidebar; clips the view, so use only on background imagery
    }
}
```
- Use only one scroll edge effect per view, and don't use it where there's no floating UI (it isn't decoration).
- **Starting in 27, prefer `.automatic`**: it has its own new look (a unified toolbar band at the top while scrolling). Re-evaluate anywhere you previously set `.soft` by hand. **[Official HIG Scroll views 2026-06]**

### 2.6 TabView (iOS)
```swift
TabView {
    Tab("Overview", systemImage: "gauge.with.dots.needle.33percent") { OverviewScreen() }
    Tab("History", systemImage: "list.bullet.rectangle") { HistoryScreen() }
    Tab("Add", systemImage: "plus", role: .prominent) { AddDeviceScreen() }  // iOS 27: separate trailing position, only one allowed
    Tab(role: .search) { SearchScreen() }
}
.tabBarMinimizeBehavior(.onScrollDown)        // values are iOS-only
.tabViewBottomAccessory { LiveReadingBar() }  // iOS 26; for persistent cross-tab info, not screen-specific actions
```
Can adapt into a sidebar: `.tabViewStyle(.sidebarAdaptable)`.

### 2.7 Sheets
- In iOS 26, partial-height sheets are inset with a glass background by default; **if you use `presentationBackground`, consider removing it**.
- Morph a sheet out of a button: `matchedTransitionSource(id:in:)` + `.navigationTransition(.zoom(sourceID:in:))`.
- confirmationDialog grows out of its source button, so attach it to the triggering button.

### 2.8 Concentric corners
See `typography-layout.md` §6. `.rect(corners: .concentric(minimum: 12))`, `ConcentricRectangle`. **`.rect(corner: .containerConcentric)` is a WWDC25 beta name and doesn't exist in the shipping SDK.**

### 2.9 Other new appearance APIs in 27 **[SDK]**
`textInputBorderShape(.capsule / .roundedRectangle)`, `.textFieldStyle(.bordered)`, `PickerStyle.tabs`, `@Environment(\.systemPrefersReducedResourceUsage)` (scale back heavy effects when the system wants to conserve resources); to show icons on menu items, use `.labelStyle(.titleAndIcon)`.

## 3. AppKit API **[SDK]**

### 3.1 NSGlassEffectView (macOS 26)
```swift
let glass = NSGlassEffectView()
glass.contentView = readingView      // content always goes in contentView; don't place the glass behind it as a sibling view
glass.cornerRadius = 999             // more than half the height = capsule
glass.style = .regular               // or .clear
glass.tintColor = nil
if #available(macOS 27, *) { glass.effectIsInteractive = true }  // only for backgrounds of interactive controls
```

### 3.1a Floating panels that are entirely glass (menu bar app panels, HUDs)

> Scope of evidence: **measured in a single case** (the whole-window panel of the open-source menu bar monitor [cool42](https://github.com/Okle42/cool42), macOS 27, 1080p @1x external display, 2026-09-25, 8 rounds of same-screen screenshot comparison against the Dock / desktop widgets). The principles generalize; the numbers are **starting values** tuned for cool42 and must be re-measured for a different app or display. Reference implementation: `GlassStyle` / `TintedGlassView` in cool42's `Sources/cool42-panel/PanelApp.swift`.
> This is a **deliberate deviation from the HIG**: officially, clear is only for use over media such as images and video; a full-window panel sits over arbitrary desktops and windows, a scenario the official guidance doesn't cover.

**Principles [Measured, generalizable]**
- **When the entire window is glass, regular doesn't work**: it adapts its luminosity to what's underneath, so the whole panel goes gray along with the background (lifted to a foggy gray over a dark starfield, washed out to light gray over a white web page, mid-gray in Light appearance over a dark wallpaper), and contrast for colored numbers on top drops to 1.1–2:1. `NSGlassEffectView` also won't switch your content between light and dark for you.
- **A white `tintColor` over regular doesn't brighten it** (a heavier tint actually makes it darker), so you can't rely on it for Light appearance either.
- **Use `.clear` + `tintColor` as the dimming / brightening layer**: this is the same layer as §1's "clear always needs a dimming layer," just done with tint.
- **Let the user adjust transparency**, and state in the setting's description that "the more transparent, the harder to read over bright backgrounds"; fall back to a solid background when Reduce Transparency is on; strengthen the tint when Increase Contrast is on.
- **Don't lay near-solid cards on top of the glass** (it looks like plastic sheets stacked on glass). Separate sections with dividers or a very faint grouping background; use `labelColor` / `secondaryLabelColor` (vibrancy) for descriptive text, and reserve color for large numbers, chart lines, and status dots.
- **Directionality of the edge lighting**: the Dock and widgets are lit only along the top and bottom edges, with almost nothing on the left and right; an even white border around all four sides looks like a HUD frame. Draw a full border only in the Increase Contrast branch.
- **Make the window borderless**: an `NSPanel` with `.titled` + `.utilityWindow` gets an extra layer of system frame and background. Use `[.borderless, .nonactivatingPanel]`, `backgroundColor = .clear`, draw the rounded corners yourself, and call `invalidateShadow()` when the appearance changes. This conflicts with the HIG's "panels should have a title bar" and applies only to HUD-style panels (see `macos-components.md` §4.1).
- **Pitfall: when the glass is the `contentView` directly and holds an `NSHostingView`, the hosting view's intrinsic size stretches the content taller than the window** (cool42 measured 76pt extra, clipping the top edge). Give the hosting view `translatesAutoresizingMaskIntoConstraints = true` + autoresizing, and let the window measure the content height and set the frame itself.
- **Verify on real hardware**: offscreen rendering can't draw real glass. Place the panel side by side with the Dock / a widget in **the same full-screen screenshot** and compare base color, edge brightness, and corner radius; measure contrast over all three backgrounds: dark wallpaper, white web page, and Light appearance.
- **Screenshots capture personal data** (calendar events, working directories, contents of other windows); crop or blur before committing them to a repo or sharing externally, and run an OCR pass over them.

**cool42 starting values [Measured, single case]**
| Item | Value | Measured result (0–255 background luminance) |
|---|---|---|
| Dark tint | `NSColor(srgbRed: 0, green: 0, blue: 0.02, alpha: 0.70)` | ~10 over starfield, ~50 over white web page (Dock ~12) |
| Light tint | `NSColor(white: 1, alpha: 0.62)` | ~193 over starfield, ~250 over white web page; 0.80 turns pure white 255 over a white web page — too solid |
| User transparency t | tint = default × (1.2 − t), t defaults to 0.2 | — |
| Increase Contrast | tint at least 0.85 dark / 0.90 light | — |
| Corner radius | 26pt (measured from widget / Dock outlines; macOS 27 publishes no official value) | inner components adjusted concentrically |
| Top highlight edge | inward 83→28→21→18→16 (measured from the Dock) + 3–4pt inner soft glow, nothing added on left/right | — |

### 3.2 NSGlassEffectContainerView
```swift
let stack = NSStackView(views: [temperatureGlass, fanGlass])
stack.orientation = .horizontal
let container = NSGlassEffectContainerView()
container.contentView = stack
container.spacing = 12   // default 0: batches rendering only, no merging
```

### 3.3 Buttons and controls
```swift
let start = NSButton(title: "Start Monitoring", target: self, action: #selector(startMonitoring))
start.bezelStyle = .glass
start.controlSize = .extraLarge
start.keyEquivalent = "\r"           // the default button automatically gets primary prominence
clearButton.tintProminence = .secondary   // secondary / destructive actions
```
- `NSControl.BorderShape` (`.automatic/.capsule/.roundedRectangle/.circle`): NSButton, NSSegmentedControl, NSPopUpButton, NSTextField.
- `prefersCompactControlSizeMetrics`: returns dense inspectors to the old sizes; inherited by descendants.
- New in 27: `NSSegmentedControl.role` / `NSToolbarItemGroup.role` (`.tabs/.valueSelection`), `NSControl.Events`, `NSMenuItem.preferredImageVisibility`.

### 3.4 Toolbar, sidebar, split view
- The system automatically groups toolbar buttons into a single piece of glass; to separate them, use `NSToolbarItemGroup` or `.space`.
- Non-interactive items: `toolbarItem.isBordered = false`. Primary action: `toolbarItem.style = .prominent`, `backgroundTintColor`. Badges: `toolbarItem.badge = .count(4)`.
- **Use `NSSplitViewController` + `NSSplitViewItem(sidebarWithViewController:)` / `init(inspectorWithViewController:)` to get glass automatically**: the sidebar floats and the inspector goes edge to edge.
- **Delete the old sidebar `NSVisualEffectView`**, or it will block the glass (add it only in the `< macOS 26` branch).
- To extend content under the sidebar: set `splitViewItem.automaticallyAdjustsSafeAreaInsets = true` on the content column (not the sidebar).
- Background extension: `NSBackgroundExtensionView`; its `contentView` is automatically placed within the safe area, and the area outside is filled with a mirrored blur.
- Avoid the window's rounded corners: `layoutGuide(for: .safeArea(cornerAdaptation: .horizontal))`.

### 3.5 Concentric corners in macOS 27
```swift
@available(macOS 27, *)
final class CornerCard: NSView {
    override var cornerConfiguration: NSViewCornerConfiguration? {
        .uniformCorners(radius: .containerConcentric(8))   // concentric with the container, minimum 8pt
    }
    override func viewDidChangeEffectiveCornerRadii() {
        super.viewDidChangeEffectiveCornerRadii()
        layer?.cornerRadius = effectiveCornerRadii?.topLeft ?? 8
    }
}
```
- Touch APIs in macOS 27 such as `NSScreen.touchCapabilities` are for **Sidecar (iPad as a second display)**, not touchscreen Macs — don't enlarge Mac touch targets because of them.

## 4. UIKit (summary) **[SDK]**
| API | Version |
|---|---|
| `UIGlassEffect(style: .regular/.clear)`, `.isInteractive`, `.tintColor`; `UIGlassContainerEffect` | iOS 26 |
| `UIButton.Configuration.glass()` / `.prominentGlass()` / `.clearGlass()` / `.prominentClearGlass()` | iOS 26 |
| `UIBackgroundExtensionView`, `UIScrollEdgeEffect`, `UIBarButtonItem.hidesSharedBackground` | iOS 26 |
| `view.cornerConfiguration = .corners(radius: .containerConcentric(minimum: 12))` | iOS 26 (typechecked) |
| 27: `UIBarButtonItem.visibilityPriority`, `UINavigationItem.navigationBarMinimization`, `UITabBarController.prominentTabIdentifier`, `UIMenuElement.preferredImageVisibility` | iOS 27 |

- Remove `UIBarAppearance` / custom bar `backgroundColor`; they interfere with the glass.
- Apps built with the iOS 27 SDK **must use the scene-based life cycle** or they won't launch (not a design issue, but it blocks shipping).

## 5. Accessibility and user settings **[Official]**

| Setting | How glass changes |
|---|---|
| Reduce Transparency | Frostier; obscures more of the background |
| Increase Contrast | Mostly black and white, with a contrasting border |
| Reduce Motion | Toned-down effects; elastic behaviors disabled |
| Glass appearance preference (26.1: Clear / Tinted; 27: continuous slider) | User-adjustable; **no developer API to read it** |

- Standard components handle this automatically; **custom components must read the environment values and be tested**: `accessibilityReduceTransparency`, `accessibilityReduceMotion`, `colorSchemeContrast`, `accessibilityShowBorders` (macOS 27 has a separate Show Borders setting), `accessibilityReduceHighlightingEffects` (26.4), `accessibilityPrefersCrossFadeTransitions` (26.4).
- **Don't bet legibility on a particular transparency level**: use system monochrome or vibrant colors for text/symbols on glass; don't put your own translucent color block behind the glass (it looks muddy in the fully tinted mode and also covers up the scroll edge effect).
- Always give icon buttons an accessibility label.

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

Screenshot matrix for custom glass components: Light / Dark × both ends of the slider (clear / tinted) × Reduce Transparency × Increase Contrast × Show Borders.

## 6. Adoption / migration checklist
1. Rebuild with Xcode 26+; standard components pick up the new look automatically.
2. **Xcode 27 has no way back**: `UIDesignRequiresCompatibility` is ignored when building against 27. **[Official, verbatim from docs]**
3. **Delete custom backgrounds** (most important): SwiftUI `toolbarBackground`, `presentationBackground`; UIKit `UIBarAppearance`; AppKit sidebar `NSVisualEffectView` and custom `NSToolbar` appearance.
4. Don't hard-code control sizes.
5. List section headers are no longer forced to all caps; update the strings yourself.
6. Set a source for action sheets / confirmationDialog.
7. Menu icons: starting in 27, iPadOS / macOS menu bar menus hide them by default; give them only to key actions; all or none within a group.
8. Performance: merge custom glass into containers, limit how many appear at once, and measure with Instruments.

## 7. What changed in 27 (mostly applied without recompiling) **[Official WWDC26]**
- Glass diffuses the content behind it more, with darker edges + brighter highlights, improving legibility.
- The transparency setting became a continuous slider (clearest ↔ fully tinted).
- Sidebars on Mac and iPad extend to the window edge; **sidebar icons regain color** (the app's accent color by default); sidebar selection uses semibold.
- **All macOS windows use uniformly tighter corner radii** (values not published).
- Inactive windows on iPad dim (`@Environment(\.appearsActive)` lets custom components follow suit).
- iPhone apps can be freely resized on iOS 27.
- App icons render sharper, with optional refraction; Icon Composer 2.
- **The glass APIs themselves were not renamed or deprecated**; the 27 SDK uses the new `@available(anyAppleOS 27.0, *)` syntax, so search the SDK for that string.
- `PreviewProvider` is marked deprecated in 27; use `#Preview` instead.

## 8. Fallback for older systems (deployment target < 26)
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
        fx.material = .popover            // pick by semantics: .popover / .hudWindow / .menu
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
On older systems the goal is to **preserve hierarchy**, not to imitate refraction. `glassEffectID`, `backgroundExtensionEffect`, `scrollEdgeEffectStyle`, and `ToolbarSpacer` can simply be skipped on older systems.

## 9. Pitfalls
1. Custom bar backgrounds covering the glass.
2. Glass on glass; glass in the content layer.
3. `.glassEffect()` placed before `.padding()`.
4. Multiple pieces of glass not wrapped in a container; container spacing larger than stack spacing.
5. `NSGlassEffectView` placed behind content as a sibling view.
6. Clear without a dimming layer; tinting everything.
7. Hiding a toolbar item's content instead of the item → empty glass.
8. Text buttons and symbol buttons sharing the same piece of glass.
9. The two wrong names `.rect(corner: .containerConcentric)` and `toolbarMinimizeBehavior`.
10. Assuming `UIDesignRequiresCompatibility` still works.
11. Still forcing `.soft` scroll edges in 27; stuffing an icon into every menu item.
12. Keeping an irregular outline on a macOS app icon → it gets placed inside the system's gray backing shape.
