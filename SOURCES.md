# Sources

Every rule in this skill carries an evidence tag. This file lists the public sources behind them, grouped by topic. No text is copied from these sources; see each link for the original.

## How facts were verified

- **Apple documentation & HIG**: fetched as DocC JSON (`https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`, `…/documentation/<framework>/<symbol>.json`), snapshot of September 2026.
- **SDK**: API names and availability checked against the Xcode 27.0 SDK (`.swiftinterface` files and AppKit/UIKit headers); every code sample in the skill was type-checked with `swiftc -typecheck` for macOS 26 / iOS 26 targets.
- **Measured**: values such as control heights, semantic colors, fonts and CJK fallback were measured on macOS 27.0 and the iOS 26.5 Simulator.
- **Traditional Chinese terminology**: counted from the Traditional Chinese (zh-TW) UI of macOS 27.
- **Web**: apple.com values were observed from public pages' computed styles (September 2026). Browser support from MDN browser-compat-data.
- **Independent cross-checks**: two rounds by a separate reviewer; round 1 sampled 68 claims (10 wrong, all fixed), round 2 sampled 27 claims (8 wrong, all fixed).

## Typography, layout, hit targets, corner radius

**Official / standards**

- <https://developer.apple.com/design/human-interface-guidelines/typography>
- <https://developer.apple.com/design/human-interface-guidelines/layout>
- <https://developer.apple.com/design/human-interface-guidelines/accessibility>
- <https://developer.apple.com/design/human-interface-guidelines/buttons>
- <https://developer.apple.com/design/human-interface-guidelines/toolbars>
- <https://developer.apple.com/design/human-interface-guidelines/spatial-layout>
- <https://developer.apple.com/design/human-interface-guidelines/windows>
- <https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo>
- <https://developer.apple.com/design/human-interface-guidelines/design-principles>
- <https://developer.apple.com/videos/play/wwdc2025/356/>
- <https://developer.apple.com/videos/play/wwdc2025/310/>
- <https://developer.apple.com/videos/play/wwdc2026/221/>
- <https://developer.apple.com/fonts/>
- <https://developer.apple.com/documentation/swiftui/dynamictypesize>
- <https://developer.apple.com/wwdc26/guides/ios/>
- <https://developer.apple.com/documentation/swiftui/font/width>
- <https://developers.apple.com/design/human-interface-guidelines/macos/visual-design/typography/>
- <https://developer.apple.com/documentation/swiftui/text/tracking>
- <https://developer.apple.com/design/human-interface-guidelines/sf-symbols>
- <https://developer.apple.com/documentation/swiftui/view/typesettinglanguage(_:isenabled>
- <https://www.w3.org/TR/clreq/>
- <https://webkit.org/blog/18325/webkit-features-for-safari-27-0/>
- <https://developer.apple.com/documentation/uikit/uiview/directionallayoutmargins>
- <https://developer.apple.com/documentation/uikit/uiviewcontroller/systemminimumlayoutmargins>
- <https://developer.apple.com/documentation/uikit/uiview/readablecontentguide>
- <https://developer.apple.com/forums/thread/812856>
- <https://developer.apple.com/design/human-interface-guidelines/multitasking>
- <https://developer.apple.com/documentation/swiftui/controlsize>
- <https://developer.apple.com/documentation/appkit/nscontrol/controlsize-swift.enum>
- <https://developer.apple.com/documentation/swiftui/roundedrectangle/init(cornerradius:style>
- <https://developer.apple.com/documentation/swiftui/shape/rect(cornerradius:style>
- <https://developer.apple.com/documentation/swiftui/edge/corner/style/concentric(minimum>
- <https://developer.apple.com/documentation/swiftui/concentricrectangle>
- <https://developer.apple.com/documentation/uikit/uicornerconfiguration-swift.struct>
- <https://developer.apple.com/documentation/appkit/nsviewcornerconfiguration>
- <https://webkit.org/blog/3709/using-the-system-font-in-web-content/>

**Third-party**

- <https://useyourloaf.com/blog/changing-root-view-layout-margins/>
- <https://useyourloaf.com/blog/readable-content-guides/>
- <https://superdesign.dev/blog/apple-design-system>
- <https://uxcel.com/lessons/layout-fundamentals-spacing-482>
- <https://squircle.js.org/blog/squircles-in-css>

## Color, materials, dark mode, contrast

**Official / standards**

- <https://developer.apple.com/design/human-interface-guidelines/color>
- <https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json>
- <https://web.archive.org/web/20240922044208/https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json>
- <https://developer.apple.com/documentation/swiftui/color/accentcolor>
- <https://developer.apple.com/documentation/xcode/specifying-your-apps-color-scheme>
- <https://developer.apple.com/documentation/bundleresources/information-property-list/nsaccentcolorname>
- <https://www.apple.com/api-www/global-elements/global-header/v1/assets/globalheader.css>
- <https://www.apple.com/ac/localnav/9/styles/ac-localnav.built.css>
- <https://github.com/WebKit/WebKit/blob/main/Source/WebCore/css/CSSValueKeywords.in>
- <https://developer.apple.com/design/human-interface-guidelines/materials>
- <https://developer.apple.com/design/human-interface-guidelines/dark-mode>
- <https://developer.apple.com/documentation/appkit/nsvisualeffectview>
- <https://developer.apple.com/documentation/appkit/nsvisualeffectview/material-swift.enum>
- <https://developer.apple.com/documentation/appkit/nsvisualeffectview/blendingmode-swift.enum>
- <https://developer.apple.com/documentation/appkit/nsvisualeffectview/state-swift.enum>
- <https://developer.apple.com/documentation/swiftui/material>
- <https://developer.apple.com/documentation/uikit/uiblureffect/style>
- <https://developer.apple.com/documentation/uikit/uivibrancyeffectstyle>
- <https://developer.apple.com/documentation/swiftui/glass>
- <https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in>
- <https://developer.apple.com/documentation/appkit/nscolor/controlaccentcolor>
- <https://developer.apple.com/documentation/uikit/supporting-dark-mode-in-your-interface>
- <https://developer.apple.com/documentation/appkit/choosing-a-specific-appearance-for-your-macos-app>
- <https://developer.apple.com/documentation/updates/swiftui>
- <https://developer.apple.com/documentation/updates/uikit>
- <https://developer.apple.com/documentation/updates/appkit>
- <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency>
- <https://caniuse.com/mdn-css_types_color_system-color_accentcolor_accentcolortext>

**Third-party**

- <https://www.cultofmac.com/news/liquid-glass-changes-ios-27-macos-27>

## Liquid Glass (iOS/macOS 26 → 27)

**Official / standards**

- <https://developer.apple.com/design/human-interface-guidelines/changelog>
- <https://developer.apple.com/design/whats-new/>
- <https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass>
- <https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views>
- <https://developer.apple.com/documentation/bundleresources/information-property-list/uidesignrequirescompatibility>
- <https://developer.apple.com/documentation/updates>
- <https://developer.apple.com/design/human-interface-guidelines/>

## Components, motion, SF Symbols, UI writing

**Official / standards**

- <https://developer.apple.com/videos/play/wwdc2026/289/>
- <https://developer.apple.com/documentation/swiftui/scene/windowresizability>
- <https://developer.apple.com/documentation/swiftui/settings>
- <https://developer.apple.com/videos/play/wwdc2026/269/>
- <https://developer.apple.com/documentation/swiftui/menubarextra>
- <https://developer.apple.com/videos/play/wwdc2026/272/>
- <https://developer.apple.com/documentation/swiftui/utilitywindow>
- <https://developer.apple.com/documentation/swiftui/view/keyboardshortcut(_:modifiers>
- <https://developer.apple.com/videos/play/wwdc2026/271/>
- <https://developer.apple.com/documentation/swiftui/animation/default>
- <https://developer.apple.com/sf-symbols/>
- <https://support.apple.com/guide/applestyleguide/c-apsgb744e4a3/web>
- <https://support.apple.com/guide/applestyleguide/welcome/web>
- <https://developer.apple.com/videos/wwdc2026/>

## Apple-style web

**Official / standards**

- <https://www.apple.com/>
- <https://www.apple.com/v/homepage/a/styles/main.built.css>
- <https://www.apple.com/v/macbook-air/z/built/styles/main.built.css>

## Charts & live data

**Official / standards**

- <https://developer.apple.com/design/human-interface-guidelines/charts>
- <https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html>
- <https://developer.apple.com/videos/play/wwdc2022/110340/>
- <https://developer.apple.com/videos/play/wwdc2026/277/>
- <https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date>
- <https://developer.apple.com/documentation/charts/creating-a-chart-using-swift-charts>
- <https://developer.apple.com/documentation/charts/linemark>
- <https://developer.apple.com/documentation/charts/rulemark>
- <https://developer.apple.com/documentation/charts/lineplot>
- <https://developer.apple.com/documentation/charts/chart3d>
- <https://developer.apple.com/documentation/charts/surfaceplot>
- <https://developer.apple.com/documentation/charts/customizing-axes-in-swift-charts>
- <https://developer.apple.com/documentation/charts/vectorizedchartcontent>
- <https://developer.apple.com/documentation/accessibility/axchartdescriptor>
- <https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor>
- <https://developer.apple.com/documentation/swiftui/gauge>
- <https://developer.apple.com/documentation/foundation/measurementformatunitusage>
- <https://developer.apple.com/design/human-interface-guidelines/charting-data>
- <https://developer.apple.com/design/human-interface-guidelines/gauges>
- <https://developer.apple.com/design/human-interface-guidelines/widgets>
- <https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass>
- <https://developer.apple.com/documentation/widgetkit/preparing-widgets-for-additional-contexts-and-appearances>
- <https://developer.apple.com/documentation/widgetkit/animating-data-updates-in-widgets-and-live-activities>
- <https://developer.apple.com/documentation/widgetkit/updating-widgets-with-widgetkit-push-notifications>
- <https://developer.apple.com/documentation/charts/visualizing-your-app-s-data>
- <https://developer.apple.com/videos/play/wwdc2022/110342/>
- <https://developer.apple.com/videos/play/wwdc2023/10037/>
- <https://developer.apple.com/videos/play/wwdc2024/10155/>
- <https://developer.apple.com/videos/play/wwdc2025/313/>

## Notifications, permissions, background apps

**Official / standards**

- <https://developer.apple.com/design/human-interface-guidelines/notifications>
- <https://developer.apple.com/design/human-interface-guidelines/managing-notifications>
- <https://developer.apple.com/design/human-interface-guidelines/privacy>
- <https://developer.apple.com/design/human-interface-guidelines/onboarding>
- <https://developer.apple.com/design/human-interface-guidelines/launching>
- <https://developer.apple.com/design/human-interface-guidelines/app-icons>
- <https://developer.apple.com/design/human-interface-guidelines/icons>
- <https://developer.apple.com/design/human-interface-guidelines/images>
- <https://developer.apple.com/design/human-interface-guidelines/the-menu-bar>
- <https://developer.apple.com/design/human-interface-guidelines/dock-menus>
- <https://developer.apple.com/app-store/review/guidelines/>
- <https://developer.apple.com/videos/play/wwdc2021/10091/>
- <https://developer.apple.com/videos/play/wwdc2025/220/>
- <https://developer.apple.com/videos/play/wwdc2025/361/>
- <https://web.archive.org/web/2021id_/https://developer.apple.com/design/human-interface-guidelines/macos/extensions/menu-bar-extras/>

**Third-party**


## Accessibility

**Official / standards**

- <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels>
- <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voiceover-evaluation-criteria>
- <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/voice-control-evaluation-criteria>
- <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria>
- <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/sufficient-contrast-evaluation-criteria>
- <https://developer.apple.com/videos/play/wwdc2023/10035/>
- <https://developer.apple.com/videos/play/wwdc2026/220/>

## Cross-check round 1

## Cross-check round 2

