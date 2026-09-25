# Color, materials, dark mode, and contrast

> Research machine: macOS 27.0, iOS 26.5 Simulator, Safari 27 (2026-09). Sources: see `SOURCES.md` in the repo.

## Contents
1. Principles
2. System colors (unified table, iOS 26 / macOS 26 and later)
3. Semantic colors (iOS / macOS)
4. SwiftUI usage and accent color
5. Materials
6. Dark mode
7. Contrast
8. Pitfalls

---

## 1. Principles **[Official]**
- **Don't hard-code system color values.** The HIG explicitly says the actual values of system colors change between releases; iOS 26 replaced almost all of them.
- Custom colors need **four variants**: Light, Dark, Light High Contrast, and Dark High Contrast (check High Contrast in the Asset Catalog). Even if your app only has one appearance, provide light + dark, because Liquid Glass switches between light and dark based on the content beneath it.
- Don't redefine what a semantic color means (don't use `separator` as a text color, or `secondaryLabel` as a background).
- Don't rely on color alone to convey information (red-green color blindness); add an icon, shape, or text. Colors carry different cultural meanings (Taiwan's stock market shows gains in red and losses in green — the opposite of the US).
- Don't offer an in-app light/dark toggle (the HIG explicitly says to avoid this); follow the system. Web tool pages may allow a manual `data-theme` override.

## 2. System colors (unified across both platforms since iOS 26 / iPadOS 26 / macOS 26; unchanged in macOS 27 per measurement) **[Official + Measured]**

| Name | Light | Dark | High Contrast Light | High Contrast Dark |
|---|---|---|---|---|
| Red | `#FF383C` | `#FF4245` | `#E9152D` | `#FF6165` |
| Orange | `#FF8D28` | `#FF9230` | `#C55300` | `#FFA056` |
| Yellow | `#FFCC00` | `#FFD600` | `#A16A00` | `#FEDF43` |
| Green | `#34C759` | `#30D158` | `#008932` | `#4AD968` |
| Mint | `#00C8B3` | `#00DAC3` | `#008575` | `#54DFCB` |
| Teal | `#00C3D0` | `#00D2E0` | `#008198` | `#3BDDEC` |
| Cyan | `#00C0E8` | `#3CD3FE` | `#007EAE` | `#6DD9FF` |
| Blue | `#0088FF` | `#0091FF` | `#1E6EF4` | `#5CB8FF` |
| Indigo | `#6155F5` | `#6D7CFF` | `#564ADE` | `#A7AAFF` |
| Purple | `#CB30E0` | `#DB34F2` | `#B02FC2` | `#EA8DFF` |
| Pink | `#FF2D55` | `#FF375F` | `#E7124D` | `#FF8AC4` |
| Brown | `#AC7F5E` | `#B78A66` | `#956D51` | `#DBA679` |
| Gray | `#8E8E93` | iOS `#8E8E93` / macOS `#98989D` | `#6C6C70` | `#AEAEB2` |

iOS gray 2–6 (not on macOS):
| | Light | Dark |
|---|---|---|
| systemGray2 | `#AEAEB2` | `#636366` |
| systemGray3 | `#C7C7CC` | `#48484A` |
| systemGray4 | `#D1D1D6` | `#3A3A3C` |
| systemGray5 | `#E5E5EA` | `#2C2C2E` |
| systemGray6 | `#F2F2F7` | `#1C1C1E` |

- Classic values from older releases (iOS 15–18 / macOS 12–15): blue `#007AFF` / `#0A84FF`, red `#FF3B30`, green `#34C759` (macOS `#28CD41`), orange `#FF9500`. Use these only when you need to "support pre-iOS 18" or want "classic Apple colors"; the full table is in the research files.
- **Three blues coexist** (measured on macOS 27): iOS `link` is still `#007AFF`; macOS `controlAccentColor` (with the Multicolor setting) is `#007AFF`; SwiftUI `Color.accentColor` / `Color.blue` is `#0088FF`. Apple hasn't explained why. **Native apps should always use the APIs; web pages should pick one set and state which version it comes from.**

## 3. Semantic colors

### 3.1 iOS (UIColor, measured in the iOS 26.5 Simulator)
| UIColor | Light | Dark (base) | Dark elevated |
|---|---|---|---|
| `label` | `#000000` | `#FFFFFF` | Same |
| `secondaryLabel` | `#3C3C43` α0.60 | `#EBEBF5` α0.60 | Same |
| `tertiaryLabel` | `#3C3C43` α0.30 | `#EBEBF5` α0.30 | Same |
| `quaternaryLabel` | `#3C3C43` α0.18 | `#EBEBF5` α0.16 | Same |
| `separator` | `#3C3C43` α0.12 | `#545458` α0.50 | Same |
| `opaqueSeparator` | `#C6C6C8` | `#38383A` | Same |
| `link` | `#007AFF` | `#0984FF` | Same |
| `systemBackground` | `#FFFFFF` | **`#000000`** | `#1C1C1E` |
| `secondarySystemBackground` | `#F2F2F7` | `#1C1C1E` | `#2C2C2E` |
| `tertiarySystemBackground` | `#FFFFFF` | `#2C2C2E` | `#3A3A3C` |
| `systemGroupedBackground` | `#F2F2F7` | `#000000` | `#1C1C1E` |
| `secondarySystemGroupedBackground` | `#FFFFFF` | `#1C1C1E` | `#2C2C2E` |
| `tertiarySystemGroupedBackground` | `#F2F2F7` | `#2C2C2E` | `#3A3A3C` |
| `systemFill` | `#787880` α0.20 | α0.36 | Same |
| `secondarySystemFill` | `#787880` α0.16 | α0.32 | Same |
| `tertiarySystemFill` | `#767680` α0.12 | α0.24 | Same |
| `quaternarySystemFill` | `#747480` α0.08 | `#767680` α0.18 | Same |

- In high contrast, the alpha of secondary / tertiary / quaternary label increases (light 0.80 / 0.70 / 0.55, dark 0.70 / 0.55 / 0.40) and background layers get darker; separator and link don't change.
- Elevated backgrounds are used in sheets, popovers, and multitasking windows, and the system switches to them automatically; custom backgrounds break this distinction.
- If you have a grouped table, use the three `systemGroupedBackground` levels; otherwise use the three `systemBackground` levels.

### 3.2 macOS (NSColor, measured on macOS 27)
| NSColor | Light | Dark |
|---|---|---|
| `labelColor` | `#000000` α0.847 | `#FFFFFF` α0.847 |
| `secondaryLabelColor` | `#000000` α0.498 | `#FFFFFF` α0.549 |
| `tertiaryLabelColor` | `#000000` α0.259 | `#FFFFFF` α0.247 |
| `quaternaryLabelColor` | `#000000` α0.098 | `#FFFFFF` α0.098 |
| `linkColor` | `#0068DA` | `#419CFF` |
| `windowBackgroundColor` | `#FFFFFF` | `#1E1E1E` |
| `controlBackgroundColor` | `#FFFFFF` | `#1E1E1E` |
| `underPageBackgroundColor` | `#F6F6F6` | `#282828` |
| `separatorColor` | `#000000` α0.098 | `#FFFFFF` α0.098 |
| `selectedContentBackgroundColor` | `#0064E1` | `#0059D1` |
| `unemphasizedSelectedContentBackgroundColor` | `#DCDCDC` | `#464646` |
| `selectedTextBackgroundColor` | `#B3D7FF` | `#3F638B` |
| `alternatingContentBackgroundColors` | `#FFFFFF` / `#F4F5F5` | `#1E1E1E` / `#FFFFFF` α0.047 |
| `systemFill` / secondary / tertiary | `#000000` α0.098 / 0.078 / 0.047 | `#FFFFFF`, same alphas |

- **macOS labels are "black / white + alpha"; iOS labels are "`#3C3C43` / `#EBEBF5` + alpha". Don't mix the two platforms.**
- **The macOS dark window background is `#1E1E1E`, not pure black**; don't use iOS's pure-black background for a Mac-style web page.
- Selection colors, the focus ring, and `controlAccentColor` change with the user's system accent color; the table shows the default (Multicolor) values.

## 4. SwiftUI usage and accent color

| Need | Code |
|---|---|
| Foreground hierarchy | `.foregroundStyle(.primary / .secondary / .tertiary / .quaternary)`; **these keep vibrancy on materials** — switch to a concrete color (`.red`) and you lose it |
| System colors | `Color.red` … `Color.brown`, `Color.gray` |
| Platform semantic colors | iOS `Color(.secondarySystemBackground)`; macOS `Color(nsColor: .windowBackgroundColor)` |
| App accent color | `Color.accentColor`; to recolor a whole subtree use `.tint(_:)` (the `.accentColor(_:)` modifier is deprecated) |
| Background hierarchy | `.background(.background)`, `.background(.background.secondary)` |

Accent color **[Official]**:
- The `AccentColor` color set in the Asset Catalog; build setting "Global Accent Color Name". Remember to check High Contrast.
- **macOS applies your app's accent only when the user's system accent color is set to Multicolor**; otherwise the user's chosen color overrides it. This is by design, not a bug. Reserve fixed colors for logos or sidebar icons with a fixed meaning.
- `NSColor.controlAccentColor` is the user's system accent color, not your app's.
- On Liquid Glass, the system applies the accent color to the **background** of prominent buttons.

## 5. Materials

### 5.1 Two kinds of material **[Official, HIG Materials]**
- **Liquid Glass**: functional layer only; see `liquid-glass.md`.
- **Standard materials**: structural separation within the content layer. **Choose by meaning, not by how the color looks** (system settings change a material's appearance). Text on a material should always use vibrant colors (system label / fill / separator). Thicker materials give better contrast; thinner ones preserve more of the background context.

### 5.2 iOS
- SwiftUI: `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial` (default), `.thickMaterial`, `.ultraThickMaterial`, `.bar` (system toolbar style).
- UIKit: `UIBlurEffect.Style.systemUltraThinMaterial … systemChromeMaterial`; don't use the old `.light/.dark/.extraLight` in new code.
- Vibrancy: **don't put `quaternaryLabel` on thin / ultraThin** (contrast is too low).

### 5.3 macOS `NSVisualEffectView`
| material | Use |
|---|---|
| `.sidebar` | Sidebars (on macOS 26+, use the split view's glass sidebar — **don't add your own**) |
| `.titlebar` | Custom title bar extensions |
| `.menu` / `.popover` | Custom menu-like overlays / popover-style windows |
| `.hudWindow` | Dark HUD panels (media, inspectors) |
| `.headerView` | Sticky table headers |
| `.sheet` / `.windowBackground` / `.contentBackground` | Their corresponding locations |
| `.underWindowBackground` | Whole-window background that shows the desktop through |
| `.selection` | Custom selection highlight |
| ~~`.light/.dark/.mediumLight/.ultraDark/.appearanceBased`~~ | **Deprecated; don't adapt to dark mode** |

- `blendingMode`: `.behindWindow` (blurs the desktop / other windows) vs. `.withinWindow` (blurs only content in the same window — use this for toolbars).
- `state`: follows the window's active state by default; **set floating panels to `.active`** so they always look active.
- Vibrancy: override `allowsVibrancy` to return true on **leaf** views; once a parent enables it, children can't turn it off, and colored content gets washed out.
- AppKit automatically creates visual effect views for title bars, popovers, and source lists; you don't need to add them yourself.

## 6. Dark mode **[Official]**
1. It isn't an inversion: dark values are mostly brighter and more saturated.
2. iOS has two sets of backgrounds, base (`#000000`) and elevated (starting at `#1C1C1E`); macOS windows are `#1E1E1E`.
3. Use pure black only for the bottommost full-screen background; overlays should always use elevated grays.
4. Illustrations on white backgrounds "glow" in dark mode; dim them or make a dark version, and use the Asset Catalog to combine the light / dark versions into one named image.
5. Put appearance-dependent color setup somewhere that gets called again (NSView `updateLayer()` / `draw(_:)`; UIView `traitCollectionDidChange` or the iOS 17+ trait registration APIs). `CGColor` doesn't update automatically — **don't set `layer.backgroundColor = color.cgColor` in init and forget about it**.
6. macOS lets you set an `NSAppearance` on a single view / window (e.g., pinning a print preview to `.aqua`).
7. Testing: test light / dark × Increase Contrast × Reduce Transparency, both separately and combined; dark + Increase Contrast sometimes actually lowers contrast. Forcing `NSAppearance(named: .accessibilityHighContrastAqua)` in code **has no effect** (measured: it returns `.aqua`); you have to actually turn on the system setting or use Xcode's Environment Overrides.

## 7. Contrast

### 7.1 Requirements **[Official, HIG Accessibility]**
| Text | Minimum contrast |
|---|---|
| ≤17pt, regular weight | **4.5:1** |
| ≥18pt, or any bold | **3:1** |

If the default palette can't meet these, at least provide a higher-contrast version when Increase Contrast is on. For custom foreground / background pairs, the HIG recommends aiming for 7:1, especially for small text.

### 7.2 Actual contrast of system colors (computed with the WCAG formula)
| Combination | Contrast | Verdict |
|---|---|---|
| `#0088FF` (iOS 26 blue) text on white | 3.52 | ✗ Not for small text |
| `#007AFF` (old blue / iOS link) on white | 4.02 | ✗ Not for small text |
| `#1E6EF4` (high-contrast blue) on white | 4.57 | ✓ |
| macOS `linkColor` `#0068DA` on white | 5.26 | ✓ |
| apple.com link `#0066CC` on white | 5.57 | ✓ |
| `#34C759` green on white | 2.22 | ✗ Can't be used as a text color |
| `#FF8D28` orange on white | 2.31 | ✗ |
| `#FF383C` red on white | 3.57 | ✗ Not for small text |
| High-contrast red / green / orange / yellow on white | 4.54–4.59 | ✓ (Apple deliberately tuned them to just pass) |
| iOS `secondaryLabel` light (composited `#8A8A8E`) on white | 3.44 | ✗ Not for small text |
| macOS `secondaryLabelColor` light on white | 3.95 | ✗ Not for small text |
| White text on a `#0088FF` filled button | 3.52 | Large / bold text only (system buttons are 17pt semibold, so they pass) |

**Bottom line**: in light mode, the system accent colors are only suitable for fills, icons, large text, and decoration. For **small text meant to be read**, use `label`, macOS `linkColor`, or a darker custom color (e.g., `#0066CC`). Secondary label also falls short of 4.5 in light mode, so don't use it for critical information. Web pages should provide a `prefers-contrast: more` version that uses the values from the high-contrast columns directly.

## 8. Pitfalls
1. Hard-coding `#007AFF` as "Apple blue".
2. Using system accent colors for small text.
3. Custom colors with only light / dark and no high-contrast variants.
4. Mixing iOS and macOS semantic colors; pure-black backgrounds on Mac-style web pages.
5. Tinting a whole row of buttons on glass; tinting the symbol instead of the background.
6. Using Liquid Glass on the content layer.
7. Choosing materials by how the color looks; using deprecated NSVisualEffectView materials.
8. Enabling `allowsVibrancy` on a parent; using concrete colors on materials so vibrancy disappears.
9. Setting `cgColor` in init so it doesn't follow appearance changes.
10. Offering an in-app light/dark toggle (native apps).
11. Simply inverting colors for dark mode; leaving white-background illustrations untouched.
12. Trying to override the accent color the user chose on macOS with a custom accent.
