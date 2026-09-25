---
name: hig42-design
description: Practical Human Interface Guidelines (HIG) implementation rules for Apple platforms, covering the Liquid Glass redesign in iOS/iPadOS 26–27 and macOS Tahoe 26 / macOS 27. Use this skill before building or changing any SwiftUI / AppKit / UIKit interface (menu bar apps, MenuBarExtra, NSPanel floating panels, Settings windows, NavigationSplitView, toolbars, alerts, iOS screens), and before building any web page, HTML tool, or dashboard meant to look "Apple-like", "macOS-style", "iOS-style", or "like apple.com". Also use it to review a UI against the HIG; to pick system colors, type sizes, spacing, corner radii, and control sizes; for Liquid Glass APIs (glassEffect, GlassEffectContainer, NSGlassEffectView) and their pitfalls; for dark mode and contrast; and for Traditional Chinese (zh-TW) UI terminology (好／取消／拷貝／還原／⋯). Use it even when the user never mentions the HIG — any Apple-platform UI or Apple-style visual work qualifies.
---

# hig42-design

Helps Claude build interfaces an Apple engineer wouldn't wince at. The content is based on the official HIG as of 2026-09, evidence from the macOS 27 / Xcode 27 SDKs, and measurements in the iOS 26.5 Simulator, and it has been independently cross-checked (68 spot checks, errors corrected). Every number carries an evidence level (see the end of this file).

## Step 1: Identify the context and read only the references you need

| Context | Examples | Required reading |
|---|---|---|
| **A. Native macOS** | Menu bar utility, floating monitor panel, Settings window, main window | `references/macos-components.md`, `references/liquid-glass.md`, `references/typography-layout.md` |
| **B. Native iOS & iPadOS** | iPhone app screens, tab bar, sheets | `references/liquid-glass.md`, `references/typography-layout.md`, the iOS section of `references/macos-components.md` |
| **C. App-style web** | Local HTML tool page, dashboard, settings page, form | `references/web.md`, `assets/apple-web-base.css` |
| **D. Marketing-style web** | Product page, landing page | The apple.com section of `references/web.md`, `assets/apple-web-base.css` |
| Picking colors (any context) | Color values, dark mode, contrast, materials | `references/color-materials.md` |
| Chinese UI text (any context) | Buttons, menus, alerts, empty states | `references/zh-tw-writing.md` |
| Live data / charts | Temperature trends, sparklines, Gauge, status badges, widgets | `references/charts-live-data.md` |
| Background utilities | Notifications, permission requests, Open at Login, LSUIElement, menu bar icon and app icon production | `references/notifications-background.md` |
| Accessibility implementation | VoiceOver labels, keyboard navigation, macOS text size, auditing | `references/accessibility.md` |

**Don't mix C and D**: apple.com uses huge type, generous whitespace, and full-bleed color blocks; tool pages should follow the HIG's grouped lists and small type sizes (13 on macOS, 17 on iOS).

Confirm the **deployment target** before you start. Every Liquid Glass API requires iOS 26 / macOS 26 or later; to support older systems, branch with `#available` (fallback patterns are in `references/liquid-glass.md`). When building with Xcode 27, the system ignores `UIDesignRequiresCompatibility` — **there is no opt-out back to the old appearance**.

## Ten core principles (with reasons)

1. **Standard components first, custom last.** Standard components get Liquid Glass, dark mode, accessibility fallbacks, keyboard navigation, and localization for free. Everything you draw yourself has to handle all of that on its own — and the next time the system changes, you fall behind.
2. **Don't hard-code color values; use semantic / system color APIs.** iOS 26 changed almost every system color (blue `#007AFF` → `#0088FF`), so apps with hard-coded values looked dated overnight. On the web, where there's no API, use tokens and note which OS version the values come from.
3. **Don't hard-code type sizes or control heights.** Use text styles (`.body`, `.headline`) so Dynamic Type works. Controls got taller in macOS 26 (regular buttons are 24pt; large and up become capsules), so hard-coded heights get clipped.
4. **Use Liquid Glass only on the functional layer** (toolbars, tab bars, sidebars, floating controls), never on the content layer (cards, list cells). Separate content-layer regions with standard materials or solid colors. Don't stack glass on glass.
5. **Remove before you add.** When adopting the new design, the most common mistake is leaving behind old custom bar backgrounds, a sidebar `NSVisualEffectView`, or `toolbarBackground` — these cover up the glass and the scroll edge effect.
6. **Be restrained with color.** Reserve the accent color for primary actions (1–2 prominent buttons per screen). On glass, tint the background, not the text. Don't tint a whole row of buttons.
7. **Contrast must meet 4.5:1.** Most of iOS 26's default system colors aren't dark enough for small text in light mode (blue 3.52:1, green 2.22:1). Use label colors or darker colors for small text; custom colors need four variants: Light / Dark and a high-contrast version of each.
8. **macOS is not a bigger iOS.** macOS body text is 13pt (17pt on iOS), and Headline is Bold 13. Every toolbar button needs a corresponding menu bar command. Settings live under the app menu's "Settings…" item with ⌘, — not behind a gear button in the toolbar.
9. **Animation must be purposeful, interruptible, and respect Reduce Motion.** Utility apps should default to `.smooth` (no bounce) or `.snappy`; don't use `.bouncy` as a global default, and don't animate high-frequency interactions.
10. **For Traditional Chinese, use Apple's own translations.** OK = 好, Copy = 拷貝, Undo = 還原, Quit = 結束; the ellipsis is 「⋯」 (U+22EF); no space between Chinese and Latin characters; quotation marks are 「」. These come from tallying the actual strings in the macOS 27 Traditional Chinese UI, not personal preference.

## Workflow

1. **Identify the context** (table above) and read the matching references.
2. **Confirm versions**: the deployment target, and whether you need to support anything earlier than macOS 15 / iOS 18.
3. **Map every element on screen to a standard component.** Only build custom UI where no standard component fits, and for each custom piece spell out how it handles dark mode, high contrast, Reduce Motion, and the keyboard.
4. **Apply tokens**: take type sizes, spacing, corner radii, and colors from the references — not from memory.
5. **Screenshot and self-check after implementing**: at least one light and one dark screenshot; if there's custom glass or materials, also capture Increase Contrast and Reduce Transparency. Use `screencapture -x` on macOS and puppeteer for the web. If you can't capture the screen, say plainly that you haven't seen it.
6. **Run the review checklist below** and report on each item.

## Most-used values (full tables in the references)

| Item | macOS | iOS | Evidence |
|---|---|---|---|
| Body text size | 13pt (Headline 13 Bold) | 17pt (Headline 17 Semibold) | Official + Measured |
| Minimum text size | 10pt | 11pt | Official |
| Hit target default / minimum | 28 / 20pt | 44 / 28pt | Official |
| Control height regular / large / extraLarge | 24 / 28 / 36pt (measured; not published by Apple) | System components pad to 44 automatically | Measured |
| Layout margins | Window content is up to you | 16pt on smaller iPhones, 20pt on larger iPhones and iPad | Measured |
| Nested corner radius | Inner radius = outer radius − padding | Same | Official |
| System blue | `#0088FF` / dark `#0091FF` (unified across both platforms since 26) | Same | Official + Measured |

- **The 8pt grid is not an Apple rule** — it's an industry convention. Fine to use, but don't present it as official.
- Always write `style: .continuous` explicitly on `RoundedRectangle`.
- The new concentric-corner APIs are `.rect(corners: .concentric)` / `ConcentricRectangle`. The `.rect(corner: .containerConcentric)` shown in WWDC25 sample code doesn't exist in the shipping SDK and won't compile.

## Most common mistakes (check these first)

1. Hard-coding `#007AFF`, `.font(.system(size: 17))`, or a 22pt control height.
2. Using `.glassEffect()` on list cells or cards; adding glass to buttons that already sit in a glass toolbar.
3. Putting `.glassEffect()` before `.padding()` (the glass only wraps the text).
4. Multiple custom glass shapes not wrapped in a `GlassEffectContainer` (inconsistent appearance, broken morphing).
5. Menu bar extra using a color PNG (use an SF Symbol or a template image); putting core functionality only in the menu bar extra; no "Show in Menu Bar" toggle.
6. Settings window with Apply / OK / Cancel buttons, that's resizable, or whose title doesn't follow the selected tab.
7. Alert buttons labeled Yes / No; Cancel set as the default; a deliberate delete action also styled red.
8. Putting an SF Symbol on every menu item (macOS 27 hides menu icons by default; the HIG asks for restraint — within a group, all or nothing).
9. Manually specifying `PingFangTC-Regular` for Chinese (line height becomes 23.8, and Chinese and Latin baselines misalign); use the system font and let it fall back automatically.
10. Embedding SF fonts or SF Symbols in a web page (the license forbids it); applying English negative tracking to Chinese; glassmorphism cards floating on a purple gradient.

## Review checklist (report ✅ / ❌ for each before delivery)

- [ ] Every color comes from a semantic color API or a version-labeled token; dark mode is correct; high contrast has variants
- [ ] All text uses text styles; with Dynamic Type (iOS) at AX sizes, key content isn't truncated
- [ ] Hit targets meet the minimum (iOS 44, macOS 28, visionOS 60)
- [ ] Glass only on the functional layer; no glass on glass; custom glass inside a container
- [ ] No leftover custom bar / sidebar backgrounds
- [ ] ≤2 prominent buttons per screen; destructive actions are never the default
- [ ] macOS: every toolbar item has a menu bar command; Settings is on ⌘,; fully operable by keyboard
- [ ] Animation respects Reduce Motion; no global `.bouncy` default
- [ ] Icon buttons and menu bar icons all have accessibility labels (`.help()` does not become a label; give MenuBarExtra icons an explicit label too)
- [ ] (zh-TW UI) Traditional Chinese terminology, ellipses, and punctuation follow `references/zh-tw-writing.md`
- [ ] State isn't conveyed by color alone (color + SF Symbol shape + text); live numbers use `monospacedDigit()`
- [ ] Notification and other permissions are requested only when first needed; "Open at Login" is off by default
- [ ] Web: system font stack, correct `lang` (`zh-Hant-TW` for Traditional Chinese), `color-scheme`, `prefers-reduced-motion`, no embedded SF fonts / Symbols

## When this conflicts with other guidance

- **The frontend-design skill says "avoid default system fonts"**: the system font *is* the essence of the Apple look — a deliberate brand choice. For Apple-style work, this skill wins; the quality difference lies in getting optical sizes, tracking, the 600/400 weight hierarchy, and gray secondary text right.
- **The user's product is a deliberate deviation from the HIG** (e.g., an always-on-top monitor panel, whereas the HIG says panels should hide when the app isn't frontmost): you can build it, but add a way to close it, make always-on-top optional, don't steal focus, keep it as small as possible, and state in the delivery notes that it's a deliberate deviation.
- **Floating panels that are glass across the whole window** (menu bar app panels, HUDs): the official `.regular` variant turns gray along with the background; in testing, only `.clear` + tint stays readable. This is a deliberate deviation — see `references/liquid-glass.md` §3.1a.
- **The HIG contradicts itself** (e.g., the Buttons page says title case for buttons while the Alerts page says sentence case): the references flag these; follow the system's actual behavior.

## Evidence levels and primary sources

Markers used in the references: **[Official]** HIG / Apple documentation / WWDC transcripts; **[SDK]** found in or compiled against the Xcode 27 SDK; **[Measured]** measured by the author on macOS 27 / the iOS 26.5 Simulator; **[Third-party]** community sources; **[Inferred]** derived from the above. Re-check any number marked [Third-party] or [Inferred] before relying on it somewhere critical.

Source URLs and verification methods for each topic are in `SOURCES.md` in the repo. For details this skill doesn't cover, or if you suspect an API has been renamed, grep the SDK on your machine directly:

```bash
SDK=$(xcrun --sdk macosx --show-sdk-path)
F=$SDK/System/Library/Frameworks
# Many appearance APIs (glassEffect, Glass, animation) live in SwiftUICore, not SwiftUI; search both
grep -n "func glassEffect" $F/SwiftUI.framework/Versions/A/Modules/SwiftUI.swiftmodule/arm64e-apple-macos.swiftinterface \
  $F/SwiftUICore.framework/Versions/A/Modules/SwiftUICore.swiftmodule/arm64e-apple-macos.swiftinterface
# For AppKit, read the headers: $F/AppKit.framework/Headers/NSGlassEffectView.h
# APIs new in 27 are marked @available(anyAppleOS 27.0, *); searching only for "macOS 27" will miss them
```

Apple's documentation site is rendered with JavaScript. If WebFetch can't get the content, fetch the DocC JSON instead: `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page-name>.json`, `https://developer.apple.com/tutorials/data/documentation/<framework>/<symbol>.json`. The overall HIG change log is at `https://developer.apple.com/design/whats-new/`.

---

Information current as of 2026-09 (iOS / iPadOS 27, macOS 27, Xcode 27). This project is not affiliated with Apple Inc. and is not authorized or endorsed by Apple. Apple, macOS, iOS, SF Symbols, Liquid Glass, and related marks are trademarks of Apple Inc. The content is implementation guidance compiled by the author from public documentation and hands-on measurement; it is not official Apple documentation.

Maintained by [Okle42](https://github.com/Okle42) · https://github.com/Okle42/hig42_design
