# Apple-style web (App-style and Marketing-style)

> apple.com values were measured on 2026-09-24 with puppeteer `getComputedStyle` and by downloading and analyzing 9 CSS files. Sources: see `SOURCES.md` in the repo
> Ready-to-use CSS: `assets/apple-web-base.css`

## Contents
1. First, tell them apart: App-style vs Marketing-style web
2. Licensing: allowed / not allowed
3. Fonts
4. App-style components
5. Marketing-style (apple.com) values
6. Frosted glass
7. Dark mode and preference queries
8. Motion
9. Chinese typography
10. "AI-generated look" anti-patterns → the Apple way
11. Pitfalls

---

## 1. App-style vs Marketing-style web

| | App-style web (tool pages, dashboards, settings pages) | Marketing-style web (product pages, landing pages) |
|---|---|---|
| Basis | HIG | apple.com |
| Type sizes | macOS 13px or iOS 17px body; hierarchy via weight and gray levels | 17px body, 48–80px headlines |
| Layout | Grouped lists, sidebar, hairline separators, leading-aligned | Generous whitespace (160px above/below sections), full-bleed color blocks, hero may be centered |
| Blue | System blue `#0088FF` / dark `#0091FF` (for small link text use `#0066CC` or macOS `#0068DA`) | Buttons `#0071E3`, links `#0066CC`, links on dark sections `#2997FF` |
| Dark mode | **Follow the system** (`prefers-color-scheme`), optionally with a `data-theme` override | apple.com does not follow the system; the design decides which sections are dark |

Don't mix the two. When a user says "make an Apple-style tool page," that means App-style web.

## 2. Licensing **[Official]**

| Item | ✅ Allowed | ❌ Not allowed |
|---|---|---|
| SF fonts | In CSS, use `-apple-system`, `BlinkMacSystemFont`, `system-ui`, `ui-*`, or `"SF Pro Text"` to **reference the system font already on the user's machine** | Shipping SF font files via `@font-face` on a website or in Electron; hotlinking `apple.com/wss/fonts`; using SF for non-Apple-platform designs |
| SF Symbols | Only inside native Apple-platform apps | Exporting SVGs for websites, web apps, or slide decks; using them in app icons or logos (including anything confusingly similar) |
| Apple Design Resources (Figma kit) | Mockups of Apple-platform apps | Extracting graphics to use as web assets |
| Apple trademarks | Compatibility statements such as "Works with iPhone" | Using the  logo (including the U+F8FF character), Apple product photos, or pages that could be mistaken for official Apple pages |
| Design vocabulary | Capsule buttons, grouped lists, frosted-glass nav bars, color values, spacing (general design elements) | Copying apple.com's CSS files, HTML, or images verbatim |

Basis: the SF font license says "solely for creating mock-ups… may not embed"; Apple Design Resources License 2B prohibits use in "website content"; Xcode and Apple SDKs Agreement §2.10 restricts SF Symbols to developing Apple-platform apps.

**Icon alternatives**: draw your own SVGs, or use an open-source icon library (Lucide ISC, Phosphor MIT, Heroicons MIT, Tabler MIT) as inline SVG, keeping the license notice. Style: monochrome 1.5–2px strokes, round caps, same color as the text.

## 3. Fonts

### 3.1 Browser behavior **[Measured + Official BCD]**
| Keyword | Safari | Chrome | Notes |
|---|---|---|---|
| `-apple-system` | ✅ | ❌ not recognized | |
| `BlinkMacSystemFont` | — | ✅ (Mac) | How Chrome reaches SF |
| `system-ui` | ✅ | ✅ | Universal, but Latin glyphs can look bad in Windows CJK locales; put it later in the stack |
| `ui-rounded` / `ui-serif` / `ui-monospace` | ✅ | ❌ | Always pair with a named font fallback |

### 3.2 Recommended stack (Traditional Chinese)
```css
--font-text: -apple-system, BlinkMacSystemFont, "Segoe UI Variable Text", "Segoe UI",
             "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", system-ui,
             "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
--font-rounded: ui-rounded, "SF Pro Rounded", var(--font-text);
```
Also set `<html lang="zh-Hant-TW">` so the system falls back to PingFang **TC** (omitting it, or writing `zh-CN`, can get you Simplified Chinese glyph forms).

### 3.3 Letter spacing **[Measured in Chrome]**
- The system font **already has tracking built in at body sizes; add none at ≤21px**.
- English headlines ≥28px: add `-0.01em`; ≥48px: add `-0.012em` to `-0.016em`.
- **Don't copy apple.com's positive headline tracking** (+0.011em etc.); that compensates for their web font.
- **Chinese is always `letter-spacing: 0`** (apple.com itself declares `body:lang(zh){letter-spacing:0em}`).

## 4. App-style components

### 4.1 Color
Use the tokens in `assets/apple-web-base.css` (system colors, semantic colors, dark, and high contrast are all included). Key points:
- iOS-style background: grouped `#F2F2F7` + white groups; dark `#000` + `#1C1C1E`.
- **macOS-style background**: window `#FFFFFF` / dark `#1E1E1E` (not pure black); labels use black/white + alpha (0.847 / 0.498).
- In light mode, system tint colors lack contrast as small text (blue is 3.52:1); use `#0066CC` for small link text.

### 4.2 Inset grouped list
| Item | Classic iOS 13–18 | iOS 26 style |
|---|---|---|
| Group corner radius | 10px | ~24px **[Third-party: Framework7]** |
| Minimum row height | 44px | ~52px **[Third-party]** |
| Side margins / row padding | 16px | 16px |
| Separators | 0.5px, **starting at the text's leading edge** (inset), none after the last row | Same |
| Section header / footer | 13px secondary color; all caps through iOS 18, regular case from iOS 26 | Same |

```css
.row + .row::before {            /* separator starts at the content's leading edge */
  content: ""; position: absolute; top: 0; right: 0; left: var(--row-inset, 16px);
  border-top: .5px solid var(--separator);
}
```

### 4.3 Switch
- **On Safari 17.4+, just use the native `<input type="checkbox" switch>`**; it renders as a system switch (other browsers fall back to a checkbox).
- Custom-drawn sizes: classic iOS 51×31 with a 27 knob; iOS 26 is 61×28 **[Measured]**; macOS `NSSwitch` 54×24. The default "on" color is green.
- HIG: use switches only in list rows; inside macOS grouped forms use the mini switch.

### 4.4 Other
- Segmented control: iOS height 31; macOS regular 24. Gray track (fill color), 2px inset, selected segment is a white capsule + very faint shadow.
- macOS-style sidebar: ~220px wide, 28px rows, 6px-radius selection background, 13px text, 11px 600 tertiary-gray group headers.
- Use `font-variant-numeric: tabular-nums` for numbers.
- Don't give every number on a dashboard its own card: use one grouped container with separators between rows.

## 5. Marketing-style (apple.com) values **[Measured]**

### 5.1 Type scale (desktop 1069–1440px)
| Role | size / line-height | weight | English tracking |
|---|---|---|---|
| Section headline | 80px / 1.05 | 600 | -0.015em |
| Hero headline | 64px / 1.0625 | 600 | -0.009em |
| Secondary headline | 48px / 1.0835 | 600 | -0.003em |
| Eyebrow (product name) | 28px / 1.1429 | 600 | +0.007em |
| Intro / lede | 21px / 1.381 | 400 (product pages: 600 + gray `#86868B`) | +0.011em |
| Body | 17px / 1.4706 | 400 | -0.022em |
| Small body | 14px / 1.4286 | 400 | -0.016em |
| Footnote | 12px / 1.3333 | 400 | -0.01em |

- Headlines almost always use 600, never 700/800; primary button text is 400.
- Chinese version `:lang(zh)`: all tracking reset to zero, larger headline line-heights (80px headline 1.0875, 28px eyebrow 1.25), `quotes: "「" "」"`, no italics.

### 5.2 Layout
- Content width: 980px at ≥1069px; 692px at 735–1068px; 87.5% at ≤734px.
- Product-page sections have 160px top/bottom whitespace; full-bleed product tiles on the home page are separated by 12px white gaps, alternating `#000` and `#F5F5F7` backgrounds.

### 5.3 Buttons
| Kind | Style |
|---|---|
| Primary | Background `#0071E3` (hover `#0076DF`), white text, 980px radius (capsule), padding 11px 21px, 17px / 400 |
| Secondary | Transparent, `#0066CC` text and 1px border |
| Small | padding 8px 15px, 14px |

Links are `#0066CC`, no underline, no "→".

### 5.4 Palette
| Use | Light | Dark |
|---|---|---|
| Background | `#FFFFFF` | `#000000` |
| Primary text | `#1D1D1F` | `#F5F5F7` |
| Secondary text | `#6E6E73` | `#86868B` |
| Tertiary text | `#86868B` (only 3.62:1 on white; large text only) | `#6E6E73` |
| Gray section background | `#F5F5F7` | `#1D1D1F` |
| Border | `#D2D2D7` | `#424245` |
| Link | `#0066CC` | `#2997FF` |

## 6. Frosted glass

- **Use it only for nav bars / toolbars floating over content**, never for cards.
- apple.com nav bar values: `backdrop-filter: saturate(180%) blur(20px)` + background `rgba(250,250,252,.8)` (dark `rgba(22,22,23,.8)`); when unsupported, falls back to `.92` / `.88` opacity.
- Prefixes: Safari 18+ works unprefixed; to support iOS 17 and earlier, write both (`-webkit-backdrop-filter`). Wrap in `@supports`, with a high-opacity background as the fallback.
- **Don't chase Liquid Glass refraction**: the community's SVG displacement filter (`backdrop-filter: url(#f)`) **only works in Chromium; Safari shows nothing**, and it's GPU-heavy. On the web do standard frosted glass only, at most adding a 1px translucent white inner border.
- Reduce transparency: write both `@media (prefers-contrast: more)` and `(prefers-reduced-transparency: reduce)`, switching to an opaque background (**Safari doesn't support `prefers-reduced-transparency`**; in testing it behaves like an invalid query. The former is mandatory; the latter only helps in Chrome).

## 7. Dark mode and preference queries
- `<meta name="color-scheme" content="light dark">` + `:root { color-scheme: light dark; }` so scrollbars and form controls switch too, and to avoid a white flash.
- Tool pages follow the system: `@media (prefers-color-scheme: dark)`, and allow a manual override via `:root[data-theme="dark"|"light"]`.
- Always handle `prefers-reduced-motion`; when you use color, handle `prefers-contrast: more` (apply high-contrast color values directly).
- The `AccentColor` system color keyword doesn't give you the user's macOS accent color (both Safari and Chrome return a fixed value to prevent fingerprinting); define your own blue.
- CSS color names like `-apple-system-blue` only work in WebKit on Apple platforms and are non-standard; use them only as progressive enhancement, always preceded by a regular color value.

## 8. Motion
- Marketing-style: apple.com most often uses `cubic-bezier(.4, 0, .6, 1)`, 240–320ms.
- App-style: springs. A sampled `linear()` version (Safari 17.2+) is `--ease-spring` in `assets/apple-web-base.css`; fall back to `cubic-bezier(.25, .1, .3, 1)` when unsupported.
- Durations: micro-interactions (switch, hover) 150–250ms; panels / sheets 350–500ms.
- Don't fade-and-slide-up every section on entry, and don't give every card a hover animation.
- Always write `@media (prefers-reduced-motion: reduce)`, replacing movement with a fade or an instant change.

## 9. Chinese typography
| Item | Recommendation |
|---|---|
| `lang` | `zh-Hant-TW` (matches `:lang(zh)`) |
| Letter spacing | 0; apply English negative tracking only to `:not(:lang(zh))` |
| Body line-height | Marketing pages 1.47; long text on tool pages 1.6–1.75 |
| Headline line-height | 3–8% taller than English |
| Quotes | `quotes: "「" "」" "『" "』"` |
| Italics | Not used for Chinese |
| Chinese–Latin spacing | `text-autospace: normal` (Safari 18.4+, Chrome 140+; the initial value adds no space, so you must set it yourself). Note: Apple's native UI strings put no space between Chinese and Latin text; whether body copy on the web should auto-space depends on context, but UI labels should not |
| Line breaking | `line-break: strict` |
| Headline balancing | `text-wrap: balance`; body `text-wrap: pretty` |
| Weight | Chinese at 600 is already heavy; headlines 600, body 400, avoid 700+ (Windows synthesizes fake bold) |

## 10. "AI-generated look" anti-patterns → the Apple way

| "AI-generated look" | The Apple way |
|---|---|
| Purple-blue / indigo→violet gradient backgrounds, gradient text | Large solid fields (white / `#F5F5F7` / black); color comes from the content itself; one accent blue only |
| Three equal-width feature cards (icon + title + two lines) | One section says one thing: a big headline + one large image or one number; if you need side-by-side, use unequal columns |
| Emoji as icons | No icons, or monochrome line SVGs; **SF Symbols are not allowed** |
| Inter + the same large radius on everything + a shadow on every card | System font; radius by hierarchy (buttons capsule, cards 18–28px, groups 10–26px, small controls 6–8px); **almost no shadows**, layer with background contrast (white cards on `#F5F5F7`) |
| All-caps, letter-spaced eyebrows | Eyebrow is the product name itself, regular case, Semibold |
| Every paragraph centered | Hero may be centered; body text, tool pages, and settings pages are always leading-aligned with a max width |
| Glassmorphism cards floating over gradients | Frosted glass only for floating nav bars; content areas use solid color |
| 700/800 bold everywhere, one word of the headline in a different color | Headlines 600, body 400; secondary info in gray, not smaller-and-bolder |
| "Get started →" buttons with arrows | Blue capsule buttons with a clear verb; secondary actions as text links |
| `#111` pretending to be black, `#FAFAFA` pretending to be white | Text black `#1D1D1F`, dark-section background `#000`, white `#FFF`, gray sections `#F5F5F7` |
| Vague copy ("Unlock your potential") | Short, specific, rhythmic; headlines often end with a period |
| English negative tracking on Chinese, line-height 1.0 | Chinese tracking 0, headline line-height ≥1.09, body 1.5–1.7 |
| One gradient card per KPI on dashboards | One grouped container with separators between rows; numbers in tabular-nums |

**Conflict with the frontend-design guidance**: Anthropic's design guidance recommends avoiding default system fonts, but **the essence of the Apple style is the system font**; this is a deliberate brand choice. The difference lies in getting optical sizes, tracking curves, the 600/400 hierarchy, and gray secondary text right.

## 11. Pitfalls
1. Embedding SF via `@font-face` or hotlinking apple.com fonts; using SF Symbols on the web.
2. Writing only `-apple-system`, so Chrome users get Times (add `BlinkMacSystemFont`).
3. No `lang` set, so Chinese text gets Simplified glyph forms.
4. Negative tracking on Chinese; copying apple.com's positive headline tracking.
5. Mixing App-style and Marketing-style web (80px headlines on a settings page, 13px grouped lists on a product page).
6. Using `#0088FF` or `#86868B` for small text (insufficient contrast).
7. Frosted-glass cards; chasing SVG refraction; no opaque fallback.
8. Tool pages that don't follow system dark mode; forgetting `color-scheme`.
9. No `prefers-reduced-motion`.
10. Using iOS pure-black dark backgrounds on a Mac-style web page.
