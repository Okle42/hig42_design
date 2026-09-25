# Typography, layout, hit targets, and corner radii

> Verification environment: macOS 27.0, Xcode 27 (iOS 27 SDK), iOS 26.5 Simulator (2026-09; the author's setup has no iOS 27 Simulator, so every "measured on iOS" figure here is from 26.5). Sources: see `SOURCES.md` in the repo.

## Contents
1. Text styles (iOS / macOS type size tables)
2. Font families, optical size, tracking, weight
3. Traditional Chinese
4. Layout (margins, safe area, size classes)
5. Hit targets and control sizes
6. Corner radii (continuous, concentric)
7. Pitfalls

---

## 1. Text styles

**Rule**: always use text styles, never hard-coded point sizes. If you truly need a custom size, use `.font(.system(size: 15, relativeTo: .body))`, `@ScaledMetric`, or `UIFontMetrics` so it still scales with Dynamic Type.

### 1.1 Default and minimum type sizes **[Official]**
| Platform | Default | Minimum |
|---|---|---|
| iOS / iPadOS | 17 | 11 |
| macOS | 13 | 10 |
| visionOS | 17 | 12 |
| watchOS | 16 | 12 |
| tvOS | 29 | 23 |

Text must be able to scale to at least 200% (140% on watchOS).

### 1.2 iOS (default size: Large) **[Official + Measured, consistent]**
| Style | Weight | Size | Leading | Emphasized | SwiftUI |
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

- Body at each size: xSmall 14, Small 15, Medium 16, **Large 17**, xLarge 19, xxLarge 21, xxxLarge 23; accessibility sizes AX1–AX5: 28 / 33 / 40 / 47 / 53. **[Official + Measured]**
- **Pitfall**: UIKit's `UIFont.lineHeight` is smaller than the HIG Leading (20.29 for body, not 22). HIG Leading is the design-spec line spacing; to match a design spec you have to set a paragraph style or `.lineSpacing()` yourself. **[Measured]**
- At large sizes, switch to stacked layouts and reduce the number of columns; at the largest accessibility size, show as much useful content as at the largest standard size. **[Official]**

### 1.3 macOS (no Dynamic Type; fixed sizes) **[Official + Measured, consistent]**
| Style | Weight | Size | Line height | Emphasized |
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

- `NSFont.systemFontSize` is 13, `smallSystemFontSize` 11, `labelFontSize` 10. By control size: mini 9, small 11, regular 13. **[Measured]**
- To match system controls, use `NSFont.controlContentFont(ofSize:)`, `menuFont`, `labelFont`, and so on. **[Official]**
- **17pt body text on a Mac looks like a blown-up iPad app** — this is the most common mistake.

### 1.4 Other platforms
- visionOS: a heavier cut of SF Pro, plus `.extraLargeTitle` / `.extraLargeTitle2`; text without a background should be bolder, with no shadow. **[Official]**
- tvOS 27 adds Dynamic Type support (WWDC26); the HIG tables haven't been updated yet. **[Official]**
- Starting in iOS 26, type is "bolder and left-aligned" at key moments such as alerts and onboarding. **[Official]**

## 2. Font families and details

| Family | Use | SwiftUI |
|---|---|---|
| SF Pro | System font on iOS / macOS / visionOS / tvOS; 9 weights, including Condensed / Expanded (`Font.Width`) | `.default` |
| SF Pro Rounded | Rounded | `.rounded` |
| SF Mono | Monospaced | `.monospaced` |
| New York | Serif | `.serif` |
| SF Compact | watchOS | — |

- **Don't bundle the system fonts in your app**; get them through `Font.Design`. **[Official]**
- **Optical size**: the current system font is a variable font that interpolates between Text and Display automatically — no manual switching needed. Only when mocking up in a design tool without variable-font support should you follow the old rule: Text at 19pt and below, Display at 20pt and above. **[Official + older HIG]**
- **Tracking**: the system adjusts it automatically by size, so **don't add it manually in an app**; any nonzero `tracking` disables ligatures. Only use the table for mockups (17pt is −0.43pt; the −0.41 circulating online is an old value). **[Official]**
- **Weight**: use Regular / Medium / Semibold / Bold; avoid Ultralight / Thin / Light for body text. **[Official]**
- **Line spacing**: don't use tight leading (`Font.leading(.tight)`) for text of three or more lines. **[Official]**
- Runtime font names like `.SFUI-*` / `.SFNS-*` are private names; don't hard-code them. **[Measured]**

## 3. Traditional Chinese

The HIG says almost nothing about CJK typography **[Official: nothing found]**; what follows is from measurement and industry standards.

- **Use the system font and let it fall back automatically**: when the system font hits Chinese, it switches to `.PingFang UI TC` (the UI variant of PingFang), and **the line height doesn't change** — at 17pt, "Hello", 「你好」, and "Hello 你好" all have a line height of 20.3. **[Measured on iOS 26.5 / macOS 27]**
- **Don't manually specify `PingFangTC-Regular`**: at 17pt the line height becomes 23.8 (+17%), and its ascender / descender differ from SF, so mixed Chinese and Latin text shifts up and down. **[Measured]**
- PingFang TC comes in Ultralight / Thin / Light / Regular / Medium / Semibold — **there's no Bold**; `.bold()` on Chinese text effectively renders around Semibold. **[Measured + Inferred]**
- When the text's language differs from the UI language, use `.typesettingLanguage(.init(identifier: "zh-Hant"))` (iOS 17 / macOS 14 and later) so line height, line breaking, and spacing follow that language's rules. **[Official]**
- Punctuation: Taiwan-style punctuation is centered in the character cell (W3C clreq). PingFang TC centers it already; don't use SC (Simplified Chinese) glyphs in a Traditional Chinese UI. **[Third-party standard]**
- Line height for long-form text: Apple gives no number; the industry convention is 1.5–1.8×. For short UI labels, the system's natural line height is fine. **[Third-party]**
- Copywriting rules (no space between Chinese and Latin text, 「⋯」, 「」) are in `zh-tw-writing.md`.

## 4. Layout

### 4.1 Margins **[Measured on iOS 26.5]**
| Device | System minimum side margin | Safe area top / bottom |
|---|---|---|
| iPhone 17 portrait (402pt wide) | **16** | 62 / 34 |
| iPhone 17 Pro Max portrait (440pt wide) | **20** | 62 / 34 |
| iPad Pro 11" portrait | **20** | 32 / 25 |

- The common claim "compact 16, regular 20" is imprecise (Pro Max in portrait is compact, yet its margin is 20). **Don't hard-code 16**; use layout margins, `.padding()`, `.scenePadding()`, or `safeAreaPadding`.
- A subview's default layout margin is 8pt per side. **[Official + Measured]**
- **Starting in iOS 26, readableContentGuide is nearly full width** (794pt on an iPad Pro 11" in portrait). Set your own max width for long-form text — about 600–700pt, or 60–75 characters per line. **[Measured]**

### 4.2 Safe area and backgrounds **[Official]**
- Keep controls and important content inside the safe area; **full-screen backgrounds should extend under the sidebar / toolbar / tab bar**. Where a sidebar covers it, use `backgroundExtensionEffect()` (SwiftUI) / `NSBackgroundExtensionView` / `UIBackgroundExtensionView`.
- **Don't put solid or translucent strips behind controls**; use the scroll edge effect for separation.
- macOS: **don't put controls or critical information at the bottom of a window** (people often drag windows partly below the bottom edge of the screen).
- macOS 26+: to avoid the window's large corner radius, use `layoutGuide(for: .safeArea(cornerAdaptation: .horizontal))`.

### 4.3 Size classes **[Official]**
- Use size classes to drive layout — **not `UIDevice.idiom` or orientation** (iPhone Mirroring, windowed iPad apps, freely resizable iPhone apps in iOS 27, and iPhone Duo produce arbitrary combinations).
- A layout change should only change how much functionality is exposed, not the functionality itself (e.g., a tab bar becoming a sidebar).
- iPhone Duo (new page, 2026-09): the outer display is compact, the inner display regular; toolbars / tab bars may move to the side; grids should use an even number of columns. The related APIs (`ReservedRegion`, etc.) aren't yet in the Xcode 27.0 SDK in the author's setup.

### 4.4 Spacing
- **The 8pt grid is not an Apple rule** — it's an industry convention. Numbers that do appear in official material: subview margins 8, root view 16 / 20, about 12 around bordered components, about 24 around borderless components, and about 10 of padding in macOS image buttons. **[Official]**
- The HIG gives no minimum macOS window size; in SwiftUI, put `.frame(minWidth:minHeight:)` on the content.

## 5. Hit targets and control sizes

### 5.1 Minimum control sizes **[Official, HIG Accessibility]**
| Platform | Default | Minimum |
|---|---|---|
| iOS / iPadOS | 44×44 | 28×28 |
| macOS | 28×28 | 20×20 |
| visionOS | 60×60 | 28×28 |
| watchOS | 44×44 | 28×28 |
| tvOS | 66×66 | 56×56 |

- These are hit areas; the visual can be smaller — make up the difference with padding or `.contentShape()`.
- Spacing: about 12pt around bordered components, about 24pt around borderless ones; on visionOS, button centers at least 60pt apart. **[Official]**

### 5.2 macOS control heights **[Measured on macOS 27; Apple's docs give no numbers]**
| ControlSize | Font size | Push button | Pop-up / Segmented | Text field | Checkbox |
|---|---|---|---|---|---|
| mini | 9 | 16 | 16 | 19 | 12 |
| small | 11 | 20 | 20 | 22 | 14 |
| **regular** | 13 | **24** | 24 | 24 | 16 |
| large | 13 | 28 | 28 | 24 | 18 |
| extraLarge | 13 | 36 | 36 | 24 | 18 |

- Version note: SwiftUI's `ControlSize.extraLarge` has existed since iOS 17 / macOS 14; what macOS 26 added is AppKit's `NSControl.ControlSize.extraLarge`.
- Starting in macOS 26, mini through regular are taller than before and stay rounded rectangles; **large and extraLarge become capsules**, with extraLarge meant to emphasize the single most important action. **[Official, WWDC25-310]**
- Dense inspectors can set `prefersCompactControlSizeMetrics = true` to get the old sizes back (regular 20). **[Official + Measured]**
- **Don't hard-code heights**; use Auto Layout / SwiftUI's natural sizes.

### 5.3 iOS controls (visual height) **[Measured on iOS 26.5]**
UIButton medium 34, large 50; `UISwitch` 61×28 (51×31 in older versions); segmented control 31; text field 34; navigation bar 54; tab bar on iPhone 83 (including the home indicator). System components pad their hit areas to 44 on their own.

## 6. Corner radii

### 6.1 Continuous corners
- SwiftUI: `RoundedRectangle(cornerRadius: 12, style: .continuous)`, `.rect(cornerRadius: 12, style: .continuous)`. Current docs already default to continuous, but **always write it explicitly** for consistency across versions. **[Official]**
- UIKit: `layer.cornerCurve = .continuous`; starting in iOS 26 you can use `cornerConfiguration`.

### 6.2 Concentric **[Official]**
- Formula: **inner radius = outer radius − the distance between the two corners**; if it comes out ≤0, use a square corner, and set a floor with minimum.
- Three shapes: fixed, capsule (radius = half the height), and concentric. Nested components should use concentric + a fallback, so they look right both on their own and inside a container.
- Using the same radius inside and out makes the corners "flare" — a very common mistake.
- Standard components in a toolbar are concentric automatically; your custom components should be too.

### 6.3 APIs
| API | Version |
|---|---|
| SwiftUI `ConcentricRectangle()`, `.rect(corners: .concentric)`, `.concentric(minimum: 12)`, `.fixed(24)` | iOS / macOS 26 |
| SwiftUI `.containerShape(RoundedRectangle(...))`: a custom container must declare its shape first so children can compute a concentric radius | Existing |
| UIKit `view.cornerConfiguration = .corners(radius: .containerConcentric(minimum: 12))` | iOS 26 |
| AppKit `NSView.cornerConfiguration` (read-only — **override it in a subclass**), `.uniformCorners(radius: .containerConcentric(8))` | **macOS 27** |

```swift
// SwiftUI: a custom control concentric with its container, minimum radius 12
MyControl()
    .padding(8)
    .background(.tint, in: .rect(corners: .concentric(minimum: 12)))
```

- Fallback for older systems: compute it by hand with `RoundedRectangle(cornerRadius: outer - padding, style: .continuous)`, or use `ContainerRelativeShape`.
- Web: CSS `corner-shape: squircle` is currently supported only in Chromium, not Safari; plain `border-radius` is fine.

## 7. Pitfalls
1. Hard-coded type sizes → Dynamic Type stops working.
2. Carrying iOS type sizes over to macOS (Mac body text is 13, not 17).
3. Checking UIKit line heights against HIG Leading.
4. Hard-coding PingFang TC for Chinese.
5. Manually adding tracking to the system font.
6. Hard-coding 16pt margins; choosing layouts by device / orientation.
7. Trusting readableContentGuide to limit width.
8. Hit targets under 44 (under 60 on visionOS); icon buttons packed too close together.
9. Hard-coding 21 / 22pt control heights on macOS.
10. Using the same radius for nested corners; using `.circular` corners.
11. Colored strips behind controls; important buttons at the very bottom of a macOS window.
12. Calling the 8pt grid an official Apple rule.
