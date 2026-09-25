# Charts and live data (Swift Charts, live values, Gauge, widgets, status colors)

> Evidence: HIG Charts / Charting data / Gauges (unchanged since 2022-09-23), Widgets (2025-12-16 revision), Color / Accessibility; transcripts of WWDC22-110340 / 110342, WWDC23-10037, WWDC24-10155, WWDC25-313, WWDC26-277; Charts / WidgetKit DocC; the author's setup **MacOSX27.0.sdk** (Charts / SwiftUI / SwiftUICore / WidgetKit swiftinterface files, AppKit / Accessibility headers); measurements on the author's setup, macOS 27.0 (`NSHostingView` light/dark rendering, FormatStyle output per locale, contrast calculations). Every Swift example in this file compiles with `xcrun --sdk macosx swiftc -typecheck -target arm64-apple-macos26.0` with 0 errors. Sources: see `SOURCES.md` in the repo

## Contents
1. When to use a chart, and which mark
2. Axes, gridlines, ranges
3. Small spaces (menu bar panels, sparklines, widgets)
4. Color, status colors, and color blindness
5. Interaction and accessibility (Audio Graphs)
6. Swift Charts APIs and availability table
7. Code templates
8. Live values: fonts, animation, formatting, update frequency
9. Gauge and NSLevelIndicator
10. WidgetKit (macOS)
11. Pitfalls

---

## 1. When to use a chart, and which mark **[Official]**

- **Use a chart to highlight what matters in the data**, not to show off the data. If people just need the numbers and no interpretation, use a sortable, searchable list / table.
- **Keep it simple and let people choose whether to see details**. Don't cram all the data into one chart; use progressive disclosure ("small chart → tap for the large chart").
- **Lead with the takeaway, then the chart**: state the point in the title or subtitle (Weather: "Light rain possible within the hour"). This text matters especially for VoiceOver users and people with cognitive disabilities, but it **doesn't replace** the accessibility label.
- **Keep multiple charts of the same data consistent**: same chart type, same colors, annotations, and layout. Change the type only to highlight a difference.
- Prefer familiar charts (bar, line). If a chart is novel, teach people how to read it (e.g., the Activity rings animating in one by one).
- Use 3D charts only when "the shape of the data matters more than exact values" and the data is inherently three-dimensional, and only when interaction improves the experience (WWDC25-313). Monitoring tools almost never need them.

| Data / purpose | Mark | Monitoring-tool example |
|---|---|---|
| Change over time, trends | `LineMark` (optionally with an `AreaMark` fill) | CPU temperature, fan speed trend |
| Category comparison, or each bar is a "total" | `BarMark` (Y starts at 0) | Per-core usage, errors per hour |
| Individual values, outliers or clusters | `PointMark` | Temperature vs. fan speed scatter plot |
| Fixed reference value, threshold, average line | `RuleMark` (with `.annotation`) | 85 °C warning line |
| Trend + emphasis on individual points | `LineMark` + `PointMark` (the combination the HIG recommends) | Trend line with a dot on the latest value |
| Ranges / durations | `RuleMark(xStart:xEnd:y:)` or `RectangleMark` | Service outage windows |
| Part to whole | `SectorMark` (macOS 14+) | Disk space breakdown (use sparingly) |

## 2. Axes, gridlines, ranges **[Official]**

- **Fixed vs. dynamic range**: use a fixed range when the bounds are meaningful for all data (battery 0–100 %); use a dynamic range when the data range varies widely and you want the marks to fill the plot area (step count in Health).
  - For monitoring tools: **percentages are always fixed at 0–100**; temperatures use a fixed, reasonable interval (e.g., 30–110 °C) **[Inferred]**; otherwise the Y axis keeps jumping during live updates, which looks like the values are jumping.
- **The lower bound depends on the mark type**: bar charts start the Y axis at 0 (so heights can be compared); line charts don't have to start at 0, and doing so can flatten important differences (the heart-rate example).
- **Use familiar tick sequences**: 0, 5, 10 reads better than 1, 6, 11.
- **Adjust gridline density to purpose**: for charts where people can interactively inspect values, use fewer gridlines and lighter labels so the data stands out.
- **The data is the most prominent element**; axes and descriptive text only provide context and shouldn't compete with the data.
- **In small spaces, maximize the plot area**: keep Y-axis labels as short as possible; move units into the title; the Y axis can go on the trailing side so the chart's leading edge aligns with other views.
- **Make important changes noticeable**: you can animate changes to marks or axes, but also convey them in other ways for VoiceOver users and people with animations turned off (see §5).

## 3. Small spaces: menu bar panels, sparklines, widgets

- Small static charts **don't need gridlines, labels, or interaction**, because people expect to tap through for details (Stocks thumbnails, Health trend cards, watch complications). **Put small charts higher in the navigation hierarchy as entry points to the large chart** **[Official: WWDC22-110342]**.
- The small chart and the expanded chart should use **the same style, colors, marks, and annotations** **[Official: HIG Charting data]**.
- When there's just one small chart that opens a detailed version, **a single accessibility label summarizing the whole button (including the chart) is enough** **[Official]**.
- Sparkline recipe: `.chartXAxis(.hidden)`, `.chartYAxis(.hidden)`, `.chartLegend(.hidden)`, and always put the current value as text next to it. With a fixed Y range, sparklines in different rows can be compared directly; with a dynamic range, the shape is more visible but rows can't be compared. Make this trade-off deliberately **[Inferred]**.
- **[Measured]** A sparkline with a fixed 0–100 range whose actual values stay between 55 and 80 is nearly flat. To see the shape, narrow the fixed range or switch to a dynamic range.
- For small charts choose `.interpolationMethod(.monotone)`: a smooth curve that doesn't overshoot the actual max / min (`.catmullRom` does) **[Inferred]**.

## 4. Color, status colors, and color blindness

### 4.1 Rules **[Official]**
- **Don't rely on color alone** to distinguish data or convey important information. Pair it with shapes or patterns: Health's blood-pressure chart uses red circles for systolic and black-and-white diamonds for diastolic.
- Separate adjacent color blocks (iPhone Storage's segmented bar leaves a thin gap between every segment).
- Don't use the same color to mean different things; keep status colors consistent across the app.
- Red/green and blue/orange are the most commonly confused; consider letting people customize chart colors.
- Colors carry different cultural meanings (US stocks: green up, red down; Taiwan stocks: the opposite).
- Colors for multiple categories should have **balanced visual weight**, or they imply a hierarchy; colors should be distinguishable by name and contrast well with each other; check with color-blindness filters; adapt to dark mode and Increase Contrast **[Official: WWDC22-110340]**.
- On Liquid Glass, reserve color for status indicators or primary actions **[Official: HIG Color]**.

### 4.2 Contrast of the status colors (HIG 26 system colors; calculated the same way as in `color-materials.md`) **[Measured, calculated]**

| Color | Light on white | Light high-contrast on white | Dark on `#1E1E1E` | Usable as small text in light mode? | Usable as graphics in light mode (WCAG non-text 3:1)? |
|---|---|---|---|---|---|
| Green `#34C759` | 2.22 | 4.54 | 8.25 | ✗ | ✗ |
| Yellow `#FFCC00` | 1.51 | 4.59 | 11.81 | ✗ | ✗ |
| Orange `#FF8D28` | 2.31 | 4.55 | 7.47 | ✗ | ✗ |
| Red `#FF383C` | 3.57 | 4.56 | 4.86 | ✗ (large / bold text OK) | ✓ |
| Blue `#0088FF` | 3.52 | 4.57 | 5.16 | ✗ (large text OK) | ✓ |

- **Conclusion**: in light mode, green / yellow / orange **don't even reach 3:1 as icons** (3:1 is WCAG 1.4.11 **[Third-party]**; the HIG only specifies text contrast). In dark mode all five colors pass.
- **What to do**: triple-encode status as "**color + SF Symbol shape + text**"; keep small text in `.primary` / `label` color and tint only the symbol. Watch out for white text on filled badges: white on green is only 2.22 and on orange 2.31; use black text instead (black on green 9.46, on orange 9.09) or large bold text.
- Suggested pairings **[Inferred; symbol names verified in the SDK]**:

| Status | Color | SF Symbol | Shape difference |
|---|---|---|---|
| Normal | `.green` | `checkmark.circle.fill` | Circle |
| Warning | `.orange` (not yellow: nearly invisible in light mode) | `exclamationmark.triangle.fill` | Triangle |
| Critical | `.red` | `xmark.octagon.fill` | Octagon |
| Unknown / offline | `.secondary` | `questionmark.circle` or `minus.circle` | Outline |

- The system setting Differentiate Without Color: read it in SwiftUI with `@Environment(\.accessibilityDifferentiateWithoutColor)` **[SDK]**. When it's on, always show a symbol or text.
- Custom status colors need four variants: Light / Dark / each with high contrast (see `color-materials.md`).

## 5. Interaction and accessibility **[Official]**

- **Interaction is fine, but important information must not be visible only through interaction** (Stocks shows the trend for the selected period by default; dragging reveals individual values).
- When marks are too small to hit, **make the whole plot area the hit target** so people can scrub across it to see values.
- Support keyboard / Full Keyboard Access / Switch Control: the path along the X axis should make sense; with lots of data, move focus in "groups of values."
- **Swift Charts provides Audio Graphs by default**, and generates accessibility elements for each mark (or group of marks). Customize the title and summary with `accessibilityChartDescriptor(_:)`. If you're not using Audio Graphs, describe the chart type, what each axis represents, and the bounds yourself.
- **Writing accessibility labels**:
  - Give context first (date, location), then the value; don't repeat axis names Audio Graphs already announces.
  - Avoid subjective words (quickly, gradually, almost); state the values.
  - Avoid ambiguous formats: write "June 6," not "6/6"; "60 minutes," not "60m".
  - Describe what the data represents, not the colors.
  - Refer to axes in a consistent order throughout the app.
  - **Hide** the visible axis and tick text from assistive technologies.
  - Depending on the chart's purpose, describe each mark individually or summarize in segments (Maps' elevation chart summarizes by segment; Health's step chart describes each bar).
- Selection on macOS **[Official: WWDC23-10037]**: `chartXSelection(value:)` selects on **pointer hover** by default; `chartXSelection(range:)` selects by **dragging** by default.
- Sonifying live data: `AXLiveAudioGraph.start()` / `updateValue(_:)` (normalized 0–1) / `stop()`, available since macOS 12 **[SDK: AXAudiograph.h]**.
- Post an announcement when the status changes level (normal → overheating): `AccessibilityNotification.Announcement("…").post()`, available since macOS 14 **[SDK]**. Don't announce on every sample.

## 6. Swift Charts APIs and availability table **[SDK: MacOSX27.0]**

| API | macOS | Notes |
|---|---|---|
| `Chart`, `LineMark` / `AreaMark` / `BarMark` / `PointMark` / `RuleMark` / `RectangleMark` | 13.0 | |
| `chartXAxis` / `chartYAxis` (`.hidden` or `AxisMarks { AxisGridLine(); AxisTick(); AxisValueLabel() }`) | 13.0 | `AxisMarks(position: .trailing, values: .stride(by: .minute))` |
| `chartXScale` / `chartYScale(domain:range:type:)` | 13.0 | |
| `chartForegroundStyleScale`, `chartSymbolScale`, `chartLineStyleScale` | 13.0 | Can map with `KeyValuePairs`, e.g. `["Performance": .blue]` |
| `.foregroundStyle(by:)`, `.symbol(by:)`, `.lineStyle(by:)` | 13.0 | Adding all three for multiple series = redundant encoding |
| `.interpolationMethod`, `.annotation(position:alignment:spacing:)`, `chartOverlay`, `chartLegend`, `chartPlotStyle` | 13.0 | |
| `.annotation(…, overflowResolution:)`, `AnnotationOverflowResolution` | 14.0 | Keeps tooltips inside the chart: `.init(x: .fit(to: .chart), y: .disabled)` |
| `chartXSelection(value:)` / `(range:)`, `chartYSelection`, `chartAngleSelection`, `chartGesture` | 14.0 | |
| `chartScrollableAxes`, `chartXVisibleDomain(length:)`, `chartScrollPosition`, `chartScrollTargetBehavior` | 14.0 | For date axes, `length` is in seconds |
| `SectorMark`, `.zIndex` | 14.0 | |
| **Vectorized plots**: `LinePlot` / `AreaPlot` / `BarPlot` / `PointPlot` / `RulePlot` / `RectanglePlot` / `SectorPlot` (take a whole collection + KeyPaths) | 15.0 | For large data sets; the whole group shares one style |
| **Function plotting**: `LinePlot(x:y:) { x in … }`, `AreaPlot(x:yStart:yEnd:) { x in (lo, hi) }` | 15.0 | Parametric variants take `t:` |
| KeyPath versions of `accessibilityLabel/Value/Hidden` (for vectorized plots) | 15.0 | The regular mark versions exist since 13.0 |
| **3D**: `Chart3D`, `SurfacePlot`, `PointMark/RuleMark/RectangleMark(x:y:z:)`, `chart3DPose`, `chartZScale`, `chartZAxisLabel` | 26.0 | Also on visionOS 26; not on tvOS / watchOS |
| `chart3DCameraProjection(.orthographic/.perspective/.automatic)` | 26.0 | **Not available on visionOS** |
| `Chart3DRenderingStyle` (`.flat` / `.volumetric`) | — | **visionOS 26 only** |
| 27: `EmptyView` / `_ConditionalContent` / `TupleContent` conform to `ChartContent`; the old `buildEither` is marked obsoleted in 27 | 27.0 | `Chart`'s init now uses `@ContentBuilder`; `if/else` still compiles as before **[SDK]**; **27 adds no new marks or modifiers** |

- `plotAreaFrame` / `plotAreaSize` are deprecated (macOS 14); use `plotFrame` / `plotSize`.
- **Vectorized vs. marks** **[Official: WWDC24-10155]**: use vectorized plots for large data sets with a uniform style; use `ForEach` with marks when each point needs a different style. With vectorized plots, grouping data by style reduces style switches; drop style modifiers that make no visible difference at high point counts; store derived properties as stored properties, not computed properties.
- Modifier order: **KeyPath-based modifiers must come before the regular value-based ones** **[Official: LinePlot docs]**.

## 7. Code templates

### 7.1 Live temperature trend (sliding window + threshold line + hover readout + Audio Graph)
```swift
import SwiftUI
import Charts
import Accessibility

struct Sample: Identifiable, Hashable {
    var id: Date { time }          // stable id: the same sample keeps the same id across updates
    let time: Date
    let celsius: Double
}

struct LiveTempChart: View {
    let samples: [Sample]           // ring buffer, already trimmed to the last 300 seconds
    var warn: Double = 85
    @State private var selected: Date?

    private var selectedSample: Sample? {
        guard let selected else { return nil }
        return samples.min { abs($0.time.timeIntervalSince(selected)) < abs($1.time.timeIntervalSince(selected)) }
    }
    private var now: Date { samples.last?.time ?? .now }

    var body: some View {
        Chart {
            ForEach(samples) { s in
                AreaMark(x: .value("Time", s.time),
                         yStart: .value("Temperature", 30), yEnd: .value("Temperature", s.celsius))
                    .foregroundStyle(.linearGradient(colors: [.accentColor.opacity(0.25), .clear],
                                                     startPoint: .top, endPoint: .bottom))
                    .interpolationMethod(.monotone)
                LineMark(x: .value("Time", s.time), y: .value("Temperature", s.celsius))
                    .interpolationMethod(.monotone)
                    .lineStyle(StrokeStyle(lineWidth: 1.5))
            }
            RuleMark(y: .value("Warning Threshold", warn))
                .foregroundStyle(.orange)
                .lineStyle(StrokeStyle(lineWidth: 1, dash: [4, 3]))   // dashed = redundant shape cue
                .annotation(position: .top, alignment: .leading, spacing: 2) {
                    Text("Warning \(warn, format: .number) °C").font(.caption2).foregroundStyle(.secondary)
                }
                .accessibilityLabel("Warning Threshold")
                .accessibilityValue("\(Int(warn)) degrees")
            if let s = selectedSample {
                RuleMark(x: .value("Selection", s.time))
                    .foregroundStyle(.secondary.opacity(0.5))
                    .annotation(position: .top, overflowResolution: .init(x: .fit(to: .chart), y: .disabled)) {
                        Text("\(s.celsius, format: .number.precision(.fractionLength(1))) °C")
                            .font(.caption.monospacedDigit())
                            .padding(4)
                            .background(.background.secondary, in: .rect(cornerRadius: 4, style: .continuous))
                    }
                PointMark(x: .value("Time", s.time), y: .value("Temperature", s.celsius)).symbolSize(30)
            }
        }
        .chartYScale(domain: 30...110)                                   // fixed: the Y axis doesn't jump
        .chartXScale(domain: now.addingTimeInterval(-300)...now)          // fixed-width sliding window
        .chartXAxis {
            AxisMarks(values: .stride(by: .minute)) { _ in
                AxisGridLine()
                AxisValueLabel(format: .dateTime.hour().minute())
            }
        }
        .chartYAxis {
            AxisMarks(position: .trailing, values: [40, 60, 80, 100]) { v in
                AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5))
                AxisValueLabel { if let d = v.as(Double.self) { Text("\(Int(d))°") } }
            }
        }
        .chartXSelection(value: $selected)      // macOS: hovering the pointer selects
        .chartLegend(.hidden)
        .accessibilityChartDescriptor(TempChartDescriptor(samples: samples, warn: warn))
        .frame(height: 140)
    }
}

struct TempChartDescriptor: AXChartDescriptorRepresentable {
    let samples: [Sample]
    let warn: Double
    func makeChartDescriptor() -> AXChartDescriptor {
        let t0 = samples.first?.time ?? .now
        let x = AXNumericDataAxisDescriptor(title: "Elapsed Seconds", range: 0...300, gridlinePositions: []) { "\(Int($0)) seconds" }
        let y = AXNumericDataAxisDescriptor(title: "CPU Temperature", range: 30...110, gridlinePositions: [warn]) { "\(Int($0)) degrees Celsius" }
        let series = AXDataSeriesDescriptor(name: "CPU Temperature", isContinuous: true,
            dataPoints: samples.map { .init(x: $0.time.timeIntervalSince(t0), y: $0.celsius) })
        let maxC = samples.map(\.celsius).max() ?? 0
        return AXChartDescriptor(title: "CPU Temperature, Last 5 Minutes",
                                 summary: "Peak \(Int(maxC)) degrees Celsius, warning threshold \(Int(warn)) degrees",
                                 xAxis: x, yAxis: y, additionalAxes: [], series: [series])
    }
}
```
**[Measured]** This code renders correctly on macOS 27 in both light and dark mode: the dashed threshold line, gradient fill, and trailing Y axis all appear. In zh_TW the X-axis labels render as 「下午2:35」, which takes up a lot of width; see Pitfall 10.

### 7.2 Sparkline, per-core bars, multiple series, scrolling history, large data sets, functions, 3D
```swift
import SwiftUI
import Charts

struct Sparkline: View {
    let values: [Double]
    var domain: ClosedRange<Double> = 0...100
    var body: some View {
        Chart(Array(values.enumerated()), id: \.offset) { i, v in
            LineMark(x: .value("i", i), y: .value("v", v))
                .interpolationMethod(.monotone)
                .lineStyle(StrokeStyle(lineWidth: 1.2))
        }
        .chartXAxis(.hidden).chartYAxis(.hidden).chartLegend(.hidden)
        .chartYScale(domain: domain)
        .chartPlotStyle { $0.padding(.vertical, 1) }       // keeps the stroke from being clipped top and bottom
        .frame(width: 60, height: 18)
        .accessibilityElement()
        .accessibilityLabel("Recent Trend")
        .accessibilityValue("Current \(Int(values.last ?? 0)), peak \(Int(values.max() ?? 0))")
    }
}

struct CoreLoad: Identifiable { let id: Int; let pct: Double; let kind: String }
struct CoreBars: View {
    let cores: [CoreLoad]
    var body: some View {
        Chart(cores) { c in
            BarMark(x: .value("Core", "\(c.id)"), y: .value("Usage", c.pct))
                .foregroundStyle(by: .value("Type", c.kind))
        }
        .chartForegroundStyleScale(["Performance": Color.blue, "Efficiency": Color.teal])
        .chartYScale(domain: 0...100)
        .chartYAxis { AxisMarks(values: [0, 50, 100]) { AxisGridLine(); AxisValueLabel() } }
    }
}

struct Reading: Identifiable { let id = UUID(); let time: Date; let value: Double; let sensor: String }
struct MultiSeries: View {
    let data: [Reading]     // note: the id is generated once at creation; don't regenerate it on every render
    var body: some View {
        Chart(data) { r in
            LineMark(x: .value("Time", r.time), y: .value("Temperature", r.value), series: .value("Sensor", r.sensor))
                .foregroundStyle(by: .value("Sensor", r.sensor))
                .symbol(by: .value("Sensor", r.sensor))        // redundant shape
                .lineStyle(by: .value("Sensor", r.sensor))     // redundant line style
        }
        .chartLegend(position: .top, alignment: .leading)
    }
}

struct History: View {
    let samples: [Sample]
    @State private var scrollX: Date = .now
    var body: some View {
        Chart(samples) { LineMark(x: .value("Time", $0.time), y: .value("Temperature", $0.celsius)) }
            .chartScrollableAxes(.horizontal)
            .chartXVisibleDomain(length: 3600)                // show 1 hour at a time (seconds)
            .chartScrollPosition(x: $scrollX)
            .chartScrollTargetBehavior(.valueAligned(matching: DateComponents(minute: 0), majorAlignment: .page))
    }
}

struct BigHistory: View {                                     // macOS 15+
    let samples: [Sample]   // e.g., one sample per second for a day = 86,400 samples
    var body: some View {
        Chart { LinePlot(samples, x: .value("Time", \.time), y: .value("Temperature", \.celsius)) }
    }
}

struct FunctionDemo: View {                                   // macOS 15+
    var body: some View {
        Chart {
            LinePlot(x: "Load", y: "Estimated Temperature") { load in 40 + 0.55 * load }
            AreaPlot(x: "Load", yStart: "Lower Bound", yEnd: "Upper Bound") { load in (38 + 0.5 * load, 42 + 0.6 * load) }
                .foregroundStyle(.gray.opacity(0.2))
        }
        .chartXScale(domain: 0...100)
    }
}

struct Pt3: Identifiable { let id: Int; let x, y, z: Double }
struct ThreeD: View {                                         // macOS 26+
    let pts: [Pt3]
    @State private var pose: Chart3DPose = .default
    var body: some View {
        Chart3D(pts) { p in PointMark(x: .value("x", p.x), y: .value("y", p.y), z: .value("z", p.z)) }
            .chart3DPose($pose)                               // pass a Binding to allow rotating with the mouse
            .chart3DCameraProjection(.perspective)
    }
}
```
**[SDK]** Lowering the target to macOS 15 makes only `ThreeD` fail; lowering it to macOS 14 makes `LinePlot` and `AreaPlot` fail too. If your deployment target is below these versions, wrap them in `if #available`.

### 7.3 Status badge (triple encoding)
```swift
import SwiftUI

enum ThermalLevel: Int, Comparable {
    case normal, warning, critical
    static func < (a: Self, b: Self) -> Bool { a.rawValue < b.rawValue }
    init(celsius: Double, warn: Double = 85, crit: Double = 95) {
        self = celsius >= crit ? .critical : celsius >= warn ? .warning : .normal
    }
    var color: Color { switch self { case .normal: .green; case .warning: .orange; case .critical: .red } }
    var symbol: String {
        switch self {
        case .normal: "checkmark.circle.fill"
        case .warning: "exclamationmark.triangle.fill"
        case .critical: "xmark.octagon.fill"
        }
    }
    var title: LocalizedStringKey { switch self { case .normal: "Normal"; case .warning: "Elevated"; case .critical: "Overheating" } }
}

struct StatusBadge: View {
    let level: ThermalLevel
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: level.symbol).foregroundStyle(level.color)   // only the symbol is tinted
            Text(level.title)                                              // text stays in the label color
        }
        .font(.callout)
        .accessibilityElement(children: .combine)
    }
}
```

## 8. Live values

### 8.1 Fonts and animation **[SDK + Official]**
| Need | API | macOS |
|---|---|---|
| Fixed-width digits that don't jitter sideways | `Text.monospacedDigit()`, `View.monospacedDigit()` | 12.0 |
| | `Font.monospacedDigit()` | 10.15 |
| Rolling-number animation | `.contentTransition(.numericText(countsDown:))` | 13.0 |
| | `.contentTransition(.numericText(value:))` (direction chosen automatically from increase/decrease) | 14.0 |
| Reduce Motion | `@Environment(\.accessibilityReduceMotion)` | — |

```swift
import SwiftUI

struct LiveReadout: View {
    let celsius: Double
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    private var text: String {
        Measurement(value: celsius, unit: UnitTemperature.celsius)
            .formatted(.measurement(width: .abbreviated, usage: .weather,
                                    numberFormatStyle: .number.precision(.fractionLength(0))))
    }
    var body: some View {
        Text(text)
            .font(.system(.title2, design: .rounded, weight: .semibold))
            .monospacedDigit()
            .contentTransition(reduceMotion ? .identity : .numericText(value: celsius))
            .animation(reduceMotion ? nil : .smooth(duration: 0.3), value: celsius)
    }
}
```
- **Keep animation duration shorter than the sampling interval** (for 1-second sampling use ≤0.3 s); otherwise every animation is interrupted by the next sample and it looks like flickering **[Inferred]**.
- Widget animations are at most **2 seconds**; in Always-On the system doesn't play animations (check with `isLuminanceReduced`) **[Official]**.
- Numbers in the menu bar status item: use `monospacedDigit` and **reserve width for the maximum number of digits** (e.g., "100%", "199°"); otherwise whenever the width changes, every menu bar icon to its right shifts too **[Inferred]**.

### 8.2 Formatting (FormatStyle) **[Measured on macOS 27]**
| Code | zh_TW | en_US | de_DE |
|---|---|---|---|
| `Measurement(72.46 °C)` `.measurement(width: .abbreviated, usage: .weather, numberFormatStyle: .number.precision(.fractionLength(0)))` | `72°C` | `162°F` | `72 °C` |
| Same with `usage: .general` + 1 decimal place | `72.5°C` | `162.4°F` | `72,5 °C` |
| `usage: .asProvided` (no conversion) | `72.46°C` | `72.46°C` | `72,46 °C` |
| `width: .wide` + `.asProvided` | `攝氏72.46度` | `72.46 degrees Celsius` | `72,46 Grad Celsius` |
| Fan speed `2450.0.formatted(.number.precision(.fractionLength(0)))` | `2,450` | `2,450` | `2.450` |
| `0.873.formatted(.percent.precision(.fractionLength(0)))` | `87%` | `87%` | `87 %` |
| `12345678.formatted(.number.notation(.compactName))` | `1235萬` | `12M` | `12 Mio.` |
| `Int64(1_530_000_000).formatted(.byteCount(style: .memory))` | `1.42 GB` | `1.42 GB` | `1,42 GB` |

- **For temperatures use `Measurement<UnitTemperature>` + `usage: .weather` or `.general`**; the system converts to °C or °F based on the locale's temperature preference. **[Measured]** The locale keywords `@mu=celsius` / `@mu=fahrenhe` override the region default (`en_US@mu=celsius` outputs °C); the system setting Language & Region › Temperature presumably affects `Locale.current` through this keyword **[Inferred]**.
- Use `.asProvided` with `converted(to:)` only when the user picks the unit inside your app.
- Without an explicit precision, `usage` outputs long decimals like `162.428°F`; **always pass `numberFormatStyle`**.
- Relative time: `Date.formatted(.relative(presentation: .numeric, unitsStyle: .abbreviated))` outputs 「1分鐘前」 in zh_TW.

### 8.3 Update frequency
- Activity Monitor offers **1 s / 2 s / 5 s** (zh_TW: 「頻率高（1秒）」「頻率較高（2秒）」「正常頻率（5秒）」) **[Measured: system strings]**. Monitoring tools can offer the same three steps, defaulting to 2–5 seconds **[Inferred]**.
- Separate sampling frequency from redraw frequency: sampling can run every second; stop updating the UI when the panel isn't visible (menu bar panel closed, window occluded) **[Inferred]**.
- To keep charts from flickering: use stable data ids (timestamps, not a fresh `UUID()` each time); use a fixed-width sliding window on the X axis and a fixed range on the Y axis; keep a fixed number of samples in a ring buffer instead of rebuilding the whole array each time **[Inferred]**.

## 9. Gauge and NSLevelIndicator

### 9.1 HIG **[Official]**
- Keep labels concise, describing the current value and both ends of the range; VoiceOver reads the visible labels.
- A gradient fill along the path can convey purpose (temperature: red to blue).
- macOS also has the **level indicator** (capacity: continuous / discrete; rating; relevance, rarely used). Use the continuous style for large ranges. The default fill is **green**; you can change the fill when the value reaches certain levels, or use tiered to show multiple color bands at once.

### 9.2 SwiftUI `Gauge` styles on macOS (13.0+) **[SDK + Measured]**
| `.gaugeStyle(...)` | macOS | Measured appearance |
|---|---|---|
| `.automatic` | ✓ | AppKit level indicator: green continuous bar + label above + min / max at both ends + value below |
| `.linearCapacity` | ✓ | Same as above, green continuous bar; `.tint(.red)` changes the fill |
| `.accessoryLinear` | ✓ | Bold value + black track + dot indicator (not a fill) |
| `.accessoryLinearCapacity` | ✓ | Thin gray progress bar + label + small gray value |
| `.accessoryCircular` | ✓ | Open arc + dot indicator + centered value + min / max at both ends |
| `.accessoryCircularCapacity` | ✓ | Full ring fill + centered value; `.tint(Gradient(...))` gives a green-yellow-orange-red gradient |
| `.circular`, `.linear` | ✗ | watchOS only |

- **[Measured]** `.automatic`, `.linearCapacity`, `.accessoryLinearCapacity`, and `ProgressView` are backed by AppKit controls, so **`ImageRenderer` can't draw them**; you get a yellow "prohibited" symbol instead. For screenshots or image export, use `NSHostingView`'s `cacheDisplay(in:to:)`, or switch to an accessory style.
- AppKit `NSLevelIndicator` has `warningValue` / `criticalValue`, `fillColor` / `warningFillColor` / `criticalFillColor` (10.13+), and `drawsTieredCapacityLevels`. The default colors are "system-defined and may vary between releases," so **don't hard-code color values** **[SDK headers]**.

```swift
import SwiftUI

struct GaugeDemo: View {
    let pct: Double
    var body: some View {
        HStack {
            Gauge(value: pct, in: 0...100) { Text("CPU") } currentValueLabel: {
                Text("\(Int(pct))").monospacedDigit()
            }
            .gaugeStyle(.accessoryCircularCapacity)
            .tint(Gradient(colors: [.green, .yellow, .orange, .red]))

            Gauge(value: pct, in: 0...100) { Text("CPU") }
                .gaugeStyle(.linearCapacity)
        }
    }
}
```

## 10. WidgetKit (macOS)

### 10.1 What widgets can and can't do **[Official]**
- On the Mac, widgets can live on the **desktop** and in **Notification Center**. Available system families: small / medium / large / extraLarge (macOS 14+). **macOS 27 adds `systemExtraLargePortrait`** **[SDK + WWDC26-277]**; but the HIG table (2025-12 revision) still says the Mac doesn't support it. The two disagree; trust the SDK. None of the accessory families are available on macOS **[SDK]**.
- **Widgets can't update in real time**. Each widget has its own budget; a frequently viewed widget gets roughly **40–70 refreshes a day**, i.e., about **one every 15–60 minutes**; timeline entries should be **at least ~5 minutes apart**. Calling reload while your app is in the foreground doesn't count against the budget, but **frequent reloads may be throttled** (WWDC26). You can call `WidgetCenter.shared.reloadTimelines(ofKind:)` once more when your app goes to the background **[Official: DocC + WWDC26-277]**.
- Since macOS 26 you can use `WidgetConfiguration.pushHandler(_:)` for WidgetKit push updates, but push doesn't replace the timeline **[SDK + Official]**.
- When people may look at the widget more often than you can update it, **show when the data was last updated**; let the system update dates and times automatically (`Text(date, style: .relative)`) so they don't consume your budget. Don't cover stale data with a placeholder **[Official]**.
- During development, turn on **WidgetKit developer mode** to lift the budget limits (WWDC26-277).
- Recommendation for monitoring tools **[Inferred]**: the widget shows only "current status + last updated time + a rough trend"; put per-second live values in a menu bar extra or floating panel.
- Design rules: one widget does one thing; text ≥ **11pt**; standard margins **16pt**, tight margins **11pt** (some contexts use smaller margins, e.g. the Mac desktop and the iPhone/iPad Lock Screen — check the HIG Widgets page); use `ContainerRelativeShape` so content corners match the widget's corners; start the description with a verb ("View CPU temperature and recent trend."), not "This widget…"; placeholders use translucent shapes to represent text and images **[Official]**.
- iPhone widgets shown on the Mac use iOS font sizes; native Mac widgets use macOS sizes, so **check type sizes when sharing code** **[Official: DocC]**.

### 10.2 Rendering modes and Liquid Glass **[SDK + Official]**
| `widgetRenderingMode` | When it appears | What the system does |
|---|---|---|
| `.fullColor` | Mac desktop, Notification Center (default appearance) | Leaves colors unchanged |
| `.accented` | When the user picks the Tinted or Clear appearance | Removes the background, replacing it with a tint or Liquid Glass; splits content into accent and primary groups, both tinted **white** on iOS / macOS; opaque images become solid white |
| `.vibrant` | Mac desktop (when widgets recede into the background), iPhone / iPad Lock Screen | Desaturates and applies vibrancy based on the background; hierarchy via grayscale, with luminance determining contrast |

- **The official docs contradict each other**: the HIG Widgets table says Accented is "Not supported" on the Mac; but the WidgetKit DocC articles "Optimizing your widget for accented rendering mode and Liquid Glass" and "Preparing widgets…" both say the Mac also uses accented and clear glass. On the author's setup, macOS 27's global defaults include `AppleIconAppearanceTintColor` **[Measured]**. **Conclusion: Mac widgets must support all three modes.**
- In `accented` and `vibrant` modes, **status colors disappear** (everything turns white or gray), so status must always be conveyed by SF Symbol shape and text **[Official + Inferred]**.
- APIs (macOS availability): `widgetRenderingMode`, `widgetAccentable(_:)` 13.0; `Image.widgetAccentedRenderingMode(.accented/.desaturated/.accentedDesaturated/.fullColor)` 15.0; `containerBackground(_:for: .widget)`; `showsWidgetContainerBackground`. Use `fullColor` only for media artwork (album covers). `levelOfDetail` isn't available on macOS (iOS / visionOS only).

```swift
import SwiftUI
import WidgetKit

struct TempEntry: TimelineEntry { let date: Date; let celsius: Double; let history: [Double] }

struct TempWidgetView: View {
    let entry: TempEntry
    @Environment(\.widgetRenderingMode) private var mode
    @Environment(\.widgetFamily) private var family
    var body: some View {
        let level = ThermalLevel(celsius: entry.celsius)
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Image(systemName: level.symbol)                         // the shape survives in every mode
                    .foregroundStyle(mode == .fullColor ? level.color : .primary)
                    .widgetAccentable()
                Text("CPU").font(.caption).foregroundStyle(.secondary)
            }
            Text(Measurement(value: entry.celsius, unit: UnitTemperature.celsius),
                 format: .measurement(width: .abbreviated, usage: .weather,
                                      numberFormatStyle: .number.precision(.fractionLength(0))))
                .font(.system(.largeTitle, design: .rounded, weight: .semibold))
                .monospacedDigit()
                .contentTransition(.numericText(value: entry.celsius))
            if family != .systemSmall {
                Sparkline(values: entry.history, domain: 30...110).frame(maxWidth: .infinity)
            }
            Text(entry.date, style: .relative).font(.caption2).foregroundStyle(.secondary)  // last updated time
        }
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

struct TempProvider: TimelineProvider {
    func placeholder(in context: Context) -> TempEntry { .init(date: .now, celsius: 60, history: []) }
    func getSnapshot(in context: Context, completion: @escaping (TempEntry) -> Void) { completion(placeholder(in: context)) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<TempEntry>) -> Void) {
        let e = TempEntry(date: .now, celsius: 60, history: [])
        completion(Timeline(entries: [e], policy: .after(.now.addingTimeInterval(15 * 60))))
    }
}

struct TempWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "cpu-temp", provider: TempProvider()) { TempWidgetView(entry: $0) }
            .configurationDisplayName("CPU Temperature")
            .description("View CPU temperature and recent trend.")
            .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

## 11. Pitfalls

1. **Using a dynamic Y range for live charts**: every new sample makes the ticks jump, and people think the values are changing wildly. Fix percentages at 0–100 and temperatures at a reasonable interval.
2. **Bar charts whose Y axis doesn't start at 0**: height ratios become distorted. Line charts are the opposite: they don't need to start at 0.
3. **Distinguishing status with red/green only**: color-blind users can't tell them apart, and widgets in accented / vibrant mode wash the colors out anyway. Add SF Symbol shapes and text.
4. **Using `.green` / `.orange` / `.yellow` for small text or thin lines in light mode**: contrast is only 1.5–2.3. Keep text in the label color and tint only symbols; make thin lines thicker or dashed.
5. **Chaining two `.foregroundStyle` calls hoping to tint the symbol but not the text**: **[Measured]** the inner one wins, and the whole Label (text included) turns orange. Split into separate `Image` and `Text` and style each.
6. **Regenerating `UUID()` for data `id`s on every render**: Swift Charts treats every point as new data, so the whole chart replays its animation and flickers. Use timestamps as ids.
7. **Animation duration ≥ sampling interval**: the animation never finishes and looks jittery. Use `.identity` when Reduce Motion is on.
8. **Numbers without `monospacedDigit()`**: "1" is narrower than "8", so the whole line shifts sideways as values change; in the menu bar it pushes other icons too.
9. **Hard-coding temperatures as `"\(v)°C"`**: US users see Celsius. Use `Measurement` + `usage: .weather` or `.general`, and always specify precision.
10. **zh_TW time-axis labels are too long** (「下午2:35」); **`.hour(.twoDigits(amPM: .omitted))` renders 14:35 as "02:35"** (12-hour clock with the AM/PM marker dropped, so the time is ambiguous) **[Measured]**. For short sliding windows, use a numeric axis of relative seconds ("−60 s"), or label only the first and last ticks.
11. **Trying to build a per-second widget**: impossible (40–70 refreshes a day, entries at least ~5 minutes apart). Put live values in the menu bar and show "last updated" in the widget.
12. **Testing Mac widgets in full color only**: the HIG table says the Mac doesn't support accented, but DocC says the Mac has tinted / clear too. Preview all three modes in the Xcode canvas.
13. **Exporting views containing `Gauge(.automatic/.linearCapacity)` or `ProgressView` with `ImageRenderer`**: you only get a prohibited symbol.
14. **Using `.gaugeStyle(.circular)` or `.linear`**: these are watchOS only and don't compile on macOS.
15. **Using `ForEach` + `LineMark` for large data sets**: tens of thousands of points will stutter. From macOS 15 use `LinePlot(data, x: .value(…, \.kp), …)`, group data by style, and store derived properties as stored properties.
16. **Using 3D charts for monitoring data**: Apple says 3D suits only three-dimensional data where "shape matters more than values." `chart3DCameraProjection` isn't available on visionOS, and `Chart3DRenderingStyle` is visionOS only.
17. **Tooltips clipped at the chart's edges**: add `overflowResolution: .init(x: .fit(to: .chart), y: .disabled)` to the selection annotation.
18. **Posting a VoiceOver announcement on every sample**: very noisy. Announce with `AccessibilityNotification.Announcement` only when the status changes level.
19. **Visible axis labels not hidden from assistive technologies, plus hand-written per-point labels**: VoiceOver reads everything twice. Swift Charts already provides a default Audio Graph; when customizing, just add the title and summary with `accessibilityChartDescriptor`.
20. **[Measured]** The console may log `Charts: Custom UnitPoint values are not supported in AxisValueLabel's anchor property`. It appeared while rendering this file's examples, but the examples don't set an anchor and the source wasn't pinpointed; rendering is fine, so it can be ignored for now.
