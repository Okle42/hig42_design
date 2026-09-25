# 圖表與即時數據（Swift Charts、即時數值、Gauge、Widget、狀態色）

> 證據出處：HIG Charts／Charting data／Gauges（2022-09-23 起未改）、Widgets（2025-12-16 版）、Color／Accessibility；WWDC22-110340／110342、WWDC23-10037、WWDC24-10155、WWDC25-313、WWDC26-277 逐字稿；Charts／WidgetKit DocC；作者環境 **MacOSX27.0.sdk**（Charts／SwiftUI／SwiftUICore／WidgetKit swiftinterface、AppKit／Accessibility 標頭）；作者環境 macOS 27.0 實測（`NSHostingView` 淺深色渲染、FormatStyle 各 locale 輸出、對比計算）。本檔所有 Swift 範例都用 `xcrun --sdk macosx swiftc -typecheck -target arm64-apple-macos26.0` 編過，0 錯誤。來源清單見 repo 的 `SOURCES.md`

## 目錄
1. 什麼時候用圖表、用哪種 mark
2. 軸、格線、範圍
3. 小空間（menu bar 面板、sparkline、widget）
4. 顏色、狀態色與色盲
5. 互動與無障礙（Audio Graphs）
6. Swift Charts API 與版本表
7. 程式碼範本
8. 即時數值：字型、動畫、格式、更新頻率
9. Gauge 與 NSLevelIndicator
10. WidgetKit（macOS）
11. 坑

---

## 1. 什麼時候用圖表、用哪種 mark【官方】

- **用圖表是為了凸顯資料裡的重點**，不是為了展示資料。只是要給數字、不需要解讀的話，用可排序、可搜尋的 list／table。
- **保持簡單，細節讓使用者自己選擇要不要看**。不要把所有資料塞進一張圖；用「小圖→點開大圖」逐步揭露。
- **先給結論再給圖**：標題或副標題直接寫重點（天氣 app：「一小時內可能下小雨」）。這段文字對 VoiceOver 使用者和有認知障礙的人特別重要，但**不能取代** accessibility label。
- **同一份資料的多張圖要保持一致**：同一種圖表類型、同樣的顏色、標註和版面。只有要凸顯差異時才換類型。
- 優先用常見圖表（長條、折線）。新奇的圖表要教使用者怎麼看（例如 Activity 圓環逐一出現的動畫）。
- 3D 圖只在「資料的形狀比精確數值重要」、而且本來就是三維資料時用，並且只有在互動能改善體驗時才用（WWDC25-313）。監控工具幾乎用不到。

| 資料／目的 | Mark | 監控工具的例子 |
|---|---|---|
| 隨時間變化、看趨勢 | `LineMark`（可加 `AreaMark` 填色） | CPU 溫度、風扇轉速走勢 |
| 分類比較，或每段是「總和」 | `BarMark`（Y 從 0 起） | 每顆核心使用率、每小時錯誤數 |
| 個別數值、找離群值或分群 | `PointMark` | 溫度對轉速的散佈圖 |
| 固定參考值、門檻、平均線 | `RuleMark`（加 `.annotation`） | 85 °C 警告線 |
| 趨勢＋強調個別點 | `LineMark` ＋ `PointMark`（HIG 建議的組合） | 走勢線加最新值圓點 |
| 區間／持續時間 | `RuleMark(xStart:xEnd:y:)` 或 `RectangleMark` | 服務停機時段 |
| 部分與整體 | `SectorMark`（macOS 14 起） | 磁碟空間分配（少用） |

## 2. 軸、格線、範圍【官方】

- **固定範圍 vs 動態範圍**：上下限對所有資料都有意義時用固定範圍（電池 0–100 %）；資料範圍變動很大、希望 mark 填滿繪圖區時用動態範圍（健康 app 步數）。
  - 監控工具建議：**百分比一律 0–100 固定**；溫度用固定的合理區間（例如 30–110 °C）【推論】，否則即時更新時 Y 軸會一直跳，看起來像數值在跳。
- **下限依 mark 類型決定**：長條圖的 Y 下限用 0（才能比較高度）；折線圖不一定要從 0 開始，從 0 開始反而會把重要差異壓扁（心率的例子）。
- **刻度用常見序列**：0、5、10 比 1、6、11 好讀。
- **格線密度依用途調整**：可以互動查看數值的圖，就用少一點格線、淡一點的標籤，讓資料最顯眼。
- **資料最顯眼**，軸和說明文字只提供背景資訊，不要和資料搶注意力。
- **小空間裡盡量加寬繪圖區**：Y 軸標籤越短越好；單位移到標題；Y 軸可以放到尾端（trailing），讓圖的前緣和其他 view 對齊。
- **重要變化要讓人注意到**：mark 或軸改變時可以加動畫，但也要用其他方式讓 VoiceOver 和關閉動畫的使用者知道（見 §5）。

## 3. 小空間：menu bar 面板、sparkline、widget

- 小型靜態圖**不需要格線、標籤、互動**，因為使用者預期點一下就能看到細節（Stocks 縮圖、健康 app 趨勢卡片、手錶複雜功能）。**小圖放在導覽層級較高的位置，當作進入大圖的入口**【官方 WWDC22-110342】。
- 小圖和展開後的大圖要用**同樣的樣式、顏色、mark、標註**【官方 HIG Charting data】。
- 只放一個小圖、點開會看到詳細版時，**整個按鈕（含小圖）用一個 accessibility label 概括即可**【官方】。
- sparkline 寫法：`.chartXAxis(.hidden)`、`.chartYAxis(.hidden)`、`.chartLegend(.hidden)`，旁邊一定要放目前數值的文字。Y 軸範圍用固定值的話，不同列的 sparkline 可以直接比較；用動態範圍的話，形狀比較明顯但不能跨列比較。這兩種取捨都要明確選擇【推論】。
- 【實測】sparkline 用 0–100 的固定範圍、但實際值只在 55–80 之間時，線幾乎是平的。要看形狀的話就縮小固定範圍，或改用動態範圍。
- 小圖選 `.interpolationMethod(.monotone)`：曲線平滑，但不會衝過實際的最大／最小值（`.catmullRom` 會）【推論】。

## 4. 顏色、狀態色與色盲

### 4.1 規則【官方】
- **不要只靠顏色**區分資料或傳達重要資訊。要搭配形狀或圖樣：健康 app 的血壓圖用紅色圓形代表收縮壓，黑白菱形代表舒張壓。
- 相鄰的色塊之間要加分隔（iPhone 儲存空間的分段長條，每段之間都留一條細空隙）。
- 同一個顏色不要代表不同意思；狀態色在整個 app 要一致。
- 紅綠、藍橘最容易混淆；可以考慮讓使用者自訂圖表配色。
- 色彩的文化意涵不同（美股綠漲紅跌，台股相反）。
- 多個分類的顏色要**視覺重量平衡**，否則會暗示主從關係；顏色要能用名稱區分、彼此對比夠高；用色盲濾鏡檢查；要適應深色模式和增加對比【官方 WWDC22-110340】。
- Liquid Glass 上的顏色只留給狀態指示或主要動作【官方 HIG Color】。

### 4.2 狀態三色的對比（HIG 26 系統色；計算方式同 `color-materials.md`）【實測計算】

| 色 | 淺色 on 白 | 淺色高對比 on 白 | 深色 on `#1E1E1E` | 淺色能當小字？ | 淺色能當圖形（WCAG 非文字 3:1）？ |
|---|---|---|---|---|---|
| Green `#34C759` | 2.22 | 4.54 | 8.25 | ✗ | ✗ |
| Yellow `#FFCC00` | 1.51 | 4.59 | 11.81 | ✗ | ✗ |
| Orange `#FF8D28` | 2.31 | 4.55 | 7.47 | ✗ | ✗ |
| Red `#FF383C` | 3.57 | 4.56 | 4.86 | ✗（大字／粗體可） | ✓ |
| Blue `#0088FF` | 3.52 | 4.57 | 5.16 | ✗（大字可） | ✓ |

- **結論**：淺色模式下，綠／黃／橘**連當圖示都不夠 3:1**（3:1 是 WCAG 1.4.11【第三方】，HIG 只規定文字對比）。深色模式五色都夠。
- **做法**：狀態用「**顏色＋SF Symbol 形狀＋文字**」三重編碼；小字維持 `.primary`／`label` 色，只有符號上色。填色徽章上白字要注意：白字 on 綠只有 2.22、on 橘 2.31，要改用黑字（黑字 on 綠 9.46、on 橘 9.09）或大粗字。
- 建議配對【推論，符號名稱已在 SDK 驗證】：

| 狀態 | 顏色 | SF Symbol | 形狀差異 |
|---|---|---|---|
| 正常 | `.green` | `checkmark.circle.fill` | 圓形 |
| 警告 | `.orange`（不用黃：淺色模式幾乎看不見） | `exclamationmark.triangle.fill` | 三角形 |
| 危險 | `.red` | `xmark.octagon.fill` | 八角形 |
| 未知／離線 | `.secondary` | `questionmark.circle` 或 `minus.circle` | 空心 |

- 系統設定「不以顏色來區分」（Differentiate Without Color）：SwiftUI 用 `@Environment(\.accessibilityDifferentiateWithoutColor)` 讀取【SDK】。開啟時一定要顯示符號或文字。
- 自訂狀態色要給 Light／Dark／高對比共四個變體（見 `color-materials.md`）。

## 5. 互動與無障礙【官方】

- **可以互動，但重要資訊不能只靠互動才看得到**（Stocks 預設就顯示所選期間的走勢，拖曳才看個別值）。
- mark 太小不好點時，**把整個繪圖區當作點擊範圍**，讓使用者掃過去就能看到數值。
- 支援鍵盤／全面鍵盤操控／切換控制：沿 X 軸走的路徑要合理；資料量大時，讓焦點以「一組數值」為單位移動。
- **Swift Charts 預設就有 Audio Graphs**，也會幫每個 mark（或每組 mark）產生 accessibility element。可以用 `accessibilityChartDescriptor(_:)` 自訂標題和摘要。沒用 Audio Graphs 的話，要自己說明圖表類型、每個軸代表什麼、上下限。
- **accessibility label 的寫法**：
  - 先講背景資訊（日期、地點），再講數值；不要重複 Audio Graphs 已經說過的軸名。
  - 不用主觀詞（快速、逐漸、幾乎），直接講數值。
  - 不用有歧義的格式：「6 月 6 日」不寫「6/6」，「60 分鐘」不寫「60m」。
  - 描述資料代表什麼，不要描述顏色。
  - 整個 app 提到軸的順序要一致。
  - 看得到的軸和刻度文字要對輔助技術**隱藏**。
  - 依圖表目的決定要逐一描述每個 mark，還是分段摘要（地圖 app 的海拔圖分段摘要；健康 app 的步數逐根描述）。
- macOS 上的選取【官方 WWDC23-10037】：`chartXSelection(value:)` 預設是**游標懸停**選取；`chartXSelection(range:)` 預設是**拖曳**選取。
- 即時資料的聲音呈現：`AXLiveAudioGraph.start()`／`updateValue(_:)`（0–1 正規化）／`stop()`，macOS 12 起可用【SDK AXAudiograph.h】。
- 狀態跳級（正常→過熱）時發布公告：`AccessibilityNotification.Announcement("…").post()`，macOS 14 起可用【SDK】。不要每次取樣都公告。

## 6. Swift Charts API 與版本表【SDK MacOSX27.0】

| API | macOS 起 | 備註 |
|---|---|---|
| `Chart`、`LineMark`／`AreaMark`／`BarMark`／`PointMark`／`RuleMark`／`RectangleMark` | 13.0 | |
| `chartXAxis`／`chartYAxis`（`.hidden` 或 `AxisMarks { AxisGridLine(); AxisTick(); AxisValueLabel() }`） | 13.0 | `AxisMarks(position: .trailing, values: .stride(by: .minute))` |
| `chartXScale`／`chartYScale(domain:range:type:)` | 13.0 | |
| `chartForegroundStyleScale`、`chartSymbolScale`、`chartLineStyleScale` | 13.0 | 可以用 `KeyValuePairs` 對應，例如 `["效能核心": .blue]` |
| `.foregroundStyle(by:)`、`.symbol(by:)`、`.lineStyle(by:)` | 13.0 | 多序列時三個都加＝冗餘編碼 |
| `.interpolationMethod`、`.annotation(position:alignment:spacing:)`、`chartOverlay`、`chartLegend`、`chartPlotStyle` | 13.0 | |
| `.annotation(…, overflowResolution:)`、`AnnotationOverflowResolution` | 14.0 | 讓 tooltip 不超出圖表範圍：`.init(x: .fit(to: .chart), y: .disabled)` |
| `chartXSelection(value:)`／`(range:)`、`chartYSelection`、`chartAngleSelection`、`chartGesture` | 14.0 | |
| `chartScrollableAxes`、`chartXVisibleDomain(length:)`、`chartScrollPosition`、`chartScrollTargetBehavior` | 14.0 | 日期軸的 `length` 單位是秒 |
| `SectorMark`、`.zIndex` | 14.0 | |
| **向量化 plot**：`LinePlot`／`AreaPlot`／`BarPlot`／`PointPlot`／`RulePlot`／`RectanglePlot`／`SectorPlot`（接整個集合＋KeyPath） | 15.0 | 大量資料點用；整組共用同一種樣式 |
| **函式繪圖**：`LinePlot(x:y:) { x in … }`、`AreaPlot(x:yStart:yEnd:) { x in (lo, hi) }` | 15.0 | 參數式另有 `t:` 版本 |
| `accessibilityLabel/Value/Hidden` 的 KeyPath 版本（給 vectorized plot） | 15.0 | 一般 mark 的版本 13.0 就有 |
| **3D**：`Chart3D`、`SurfacePlot`、`PointMark/RuleMark/RectangleMark(x:y:z:)`、`chart3DPose`、`chartZScale`、`chartZAxisLabel` | 26.0 | visionOS 26 也可用；tvOS／watchOS 不可用 |
| `chart3DCameraProjection(.orthographic/.perspective/.automatic)` | 26.0 | **visionOS 不可用** |
| `Chart3DRenderingStyle`（`.flat`／`.volumetric`） | — | **只有 visionOS 26** |
| 27：`EmptyView`／`_ConditionalContent`／`TupleContent` 符合 `ChartContent`；舊的 `buildEither` 在 27 標示 obsoleted | 27.0 | `Chart` 的 init 改用 `@ContentBuilder`，`if/else` 寫法照舊可編【SDK】；**27 沒有新的 mark 或 modifier** |

- `plotAreaFrame`／`plotAreaSize` 已棄用（macOS 14），改用 `plotFrame`／`plotSize`。
- **Vectorized vs Mark**【官方 WWDC24-10155】：資料量大、整組樣式相同時用 vectorized plot；每個點要不同樣式時用 `ForEach` 加 mark。用 vectorized plot 時，把資料依樣式分組可以減少樣式切換；資料點多時看不出差別的樣式修飾直接省略；轉換用的屬性存成 stored property，不要用 computed property。
- modifier 順序：**KeyPath 版本的 modifier 要放在一般數值版本之前**【官方 LinePlot 文件】。

## 7. 程式碼範本

### 7.1 即時溫度走勢（滑動視窗＋門檻線＋懸停讀值＋Audio Graph）
```swift
import SwiftUI
import Charts
import Accessibility

struct Sample: Identifiable, Hashable {
    var id: Date { time }          // 穩定 id：同一筆資料每次更新都是同一個 id
    let time: Date
    let celsius: Double
}

struct LiveTempChart: View {
    let samples: [Sample]           // ring buffer，已裁成最近 300 秒
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
                AreaMark(x: .value("時間", s.time),
                         yStart: .value("溫度", 30), yEnd: .value("溫度", s.celsius))
                    .foregroundStyle(.linearGradient(colors: [.accentColor.opacity(0.25), .clear],
                                                     startPoint: .top, endPoint: .bottom))
                    .interpolationMethod(.monotone)
                LineMark(x: .value("時間", s.time), y: .value("溫度", s.celsius))
                    .interpolationMethod(.monotone)
                    .lineStyle(StrokeStyle(lineWidth: 1.5))
            }
            RuleMark(y: .value("警告門檻", warn))
                .foregroundStyle(.orange)
                .lineStyle(StrokeStyle(lineWidth: 1, dash: [4, 3]))   // 虛線＝形狀冗餘
                .annotation(position: .top, alignment: .leading, spacing: 2) {
                    Text("警告 \(warn, format: .number) °C").font(.caption2).foregroundStyle(.secondary)
                }
                .accessibilityLabel("警告門檻")
                .accessibilityValue("\(Int(warn)) 度")
            if let s = selectedSample {
                RuleMark(x: .value("選取", s.time))
                    .foregroundStyle(.secondary.opacity(0.5))
                    .annotation(position: .top, overflowResolution: .init(x: .fit(to: .chart), y: .disabled)) {
                        Text("\(s.celsius, format: .number.precision(.fractionLength(1))) °C")
                            .font(.caption.monospacedDigit())
                            .padding(4)
                            .background(.background.secondary, in: .rect(cornerRadius: 4, style: .continuous))
                    }
                PointMark(x: .value("時間", s.time), y: .value("溫度", s.celsius)).symbolSize(30)
            }
        }
        .chartYScale(domain: 30...110)                                   // 固定：Y 軸不會跳
        .chartXScale(domain: now.addingTimeInterval(-300)...now)          // 固定寬度的滑動視窗
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
        .chartXSelection(value: $selected)      // macOS：游標懸停就會選取
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
        let x = AXNumericDataAxisDescriptor(title: "經過秒數", range: 0...300, gridlinePositions: []) { "\(Int($0)) 秒" }
        let y = AXNumericDataAxisDescriptor(title: "CPU 溫度", range: 30...110, gridlinePositions: [warn]) { "攝氏 \(Int($0)) 度" }
        let series = AXDataSeriesDescriptor(name: "CPU 溫度", isContinuous: true,
            dataPoints: samples.map { .init(x: $0.time.timeIntervalSince(t0), y: $0.celsius) })
        let maxC = samples.map(\.celsius).max() ?? 0
        return AXChartDescriptor(title: "最近 5 分鐘 CPU 溫度",
                                 summary: "最高攝氏 \(Int(maxC)) 度，警告門檻 \(Int(warn)) 度",
                                 xAxis: x, yAxis: y, additionalAxes: [], series: [series])
    }
}
```
【實測】這段程式在 macOS 27 的淺色和深色模式都渲染正常：虛線門檻線、漸層填色、尾端 Y 軸都有出現。zh_TW 的 X 軸標籤會顯示成「下午2:35」，很佔寬度，見坑 10。

### 7.2 Sparkline、每核心長條、多序列、歷史捲動、大量資料、函式、3D
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
        .chartPlotStyle { $0.padding(.vertical, 1) }       // 線寬不被上下裁切
        .frame(width: 60, height: 18)
        .accessibilityElement()
        .accessibilityLabel("最近走勢")
        .accessibilityValue("目前 \(Int(values.last ?? 0))，最高 \(Int(values.max() ?? 0))")
    }
}

struct CoreLoad: Identifiable { let id: Int; let pct: Double; let kind: String }
struct CoreBars: View {
    let cores: [CoreLoad]
    var body: some View {
        Chart(cores) { c in
            BarMark(x: .value("核心", "\(c.id)"), y: .value("使用率", c.pct))
                .foregroundStyle(by: .value("類型", c.kind))
        }
        .chartForegroundStyleScale(["效能核心": Color.blue, "節能核心": Color.teal])
        .chartYScale(domain: 0...100)
        .chartYAxis { AxisMarks(values: [0, 50, 100]) { AxisGridLine(); AxisValueLabel() } }
    }
}

struct Reading: Identifiable { let id = UUID(); let time: Date; let value: Double; let sensor: String }
struct MultiSeries: View {
    let data: [Reading]     // 注意：id 在建立時產生一次，不要每次 render 都重新產生
    var body: some View {
        Chart(data) { r in
            LineMark(x: .value("時間", r.time), y: .value("溫度", r.value), series: .value("感測器", r.sensor))
                .foregroundStyle(by: .value("感測器", r.sensor))
                .symbol(by: .value("感測器", r.sensor))        // 形狀冗餘
                .lineStyle(by: .value("感測器", r.sensor))     // 線型冗餘
        }
        .chartLegend(position: .top, alignment: .leading)
    }
}

struct History: View {
    let samples: [Sample]
    @State private var scrollX: Date = .now
    var body: some View {
        Chart(samples) { LineMark(x: .value("時間", $0.time), y: .value("溫度", $0.celsius)) }
            .chartScrollableAxes(.horizontal)
            .chartXVisibleDomain(length: 3600)                // 一次看 1 小時（秒）
            .chartScrollPosition(x: $scrollX)
            .chartScrollTargetBehavior(.valueAligned(matching: DateComponents(minute: 0), majorAlignment: .page))
    }
}

struct BigHistory: View {                                     // macOS 15+
    let samples: [Sample]   // 例：一天每秒一筆 = 86,400 筆
    var body: some View {
        Chart { LinePlot(samples, x: .value("時間", \.time), y: .value("溫度", \.celsius)) }
    }
}

struct FunctionDemo: View {                                   // macOS 15+
    var body: some View {
        Chart {
            LinePlot(x: "負載", y: "預估溫度") { load in 40 + 0.55 * load }
            AreaPlot(x: "負載", yStart: "下限", yEnd: "上限") { load in (38 + 0.5 * load, 42 + 0.6 * load) }
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
            .chart3DPose($pose)                               // 傳 Binding 才能用滑鼠旋轉
            .chart3DCameraProjection(.perspective)
    }
}
```
【SDK】把 target 降到 macOS 15 時，只有 `ThreeD` 會報錯；降到 macOS 14 時，`LinePlot` 和 `AreaPlot` 也會報錯。deployment target 低於這些版本就要包 `if #available`。

### 7.3 狀態徽章（三重編碼）
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
    var title: LocalizedStringKey { switch self { case .normal: "正常"; case .warning: "偏高"; case .critical: "過熱" } }
}

struct StatusBadge: View {
    let level: ThermalLevel
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: level.symbol).foregroundStyle(level.color)   // 只有符號上色
            Text(level.title)                                              // 文字維持 label 色
        }
        .font(.callout)
        .accessibilityElement(children: .combine)
    }
}
```

## 8. 即時數值

### 8.1 字型與動畫【SDK＋官方】
| 需求 | API | macOS 起 |
|---|---|---|
| 數字寬度固定、不左右抖動 | `Text.monospacedDigit()`、`View.monospacedDigit()` | 12.0 |
| | `Font.monospacedDigit()` | 10.15 |
| 數字滾動動畫 | `.contentTransition(.numericText(countsDown:))` | 13.0 |
| | `.contentTransition(.numericText(value:))`（依數值增減自動決定方向） | 14.0 |
| 減少動態效果 | `@Environment(\.accessibilityReduceMotion)` | — |

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
- **動畫時長要比取樣間隔短**（1 秒取樣就用 ≤0.3 秒）；否則動畫會一直被下一筆打斷，看起來像閃爍【推論】。
- Widget 動畫最長 **2 秒**；Always-On 狀態下系統不播動畫（用 `isLuminanceReduced` 判斷）【官方】。
- Menu bar 狀態列的數字：`monospacedDigit` 加上**以最大位數預留寬度**（例如 "100%"、"199°"），否則寬度一變，右邊所有選單列圖示都會跟著位移【推論】。

### 8.2 格式（FormatStyle）【實測 macOS 27】
| 寫法 | zh_TW | en_US | de_DE |
|---|---|---|---|
| `Measurement(72.46 °C)` `.measurement(width: .abbreviated, usage: .weather, numberFormatStyle: .number.precision(.fractionLength(0)))` | `72°C` | `162°F` | `72 °C` |
| 同上 `usage: .general`＋1 位小數 | `72.5°C` | `162.4°F` | `72,5 °C` |
| `usage: .asProvided`（不換算） | `72.46°C` | `72.46°C` | `72,46 °C` |
| `width: .wide`＋`.asProvided` | `攝氏72.46度` | `72.46 degrees Celsius` | `72,46 Grad Celsius` |
| 轉速 `2450.0.formatted(.number.precision(.fractionLength(0)))` | `2,450` | `2,450` | `2.450` |
| `0.873.formatted(.percent.precision(.fractionLength(0)))` | `87%` | `87%` | `87 %` |
| `12345678.formatted(.number.notation(.compactName))` | `1235萬` | `12M` | `12 Mio.` |
| `Int64(1_530_000_000).formatted(.byteCount(style: .memory))` | `1.42 GB` | `1.42 GB` | `1,42 GB` |

- **溫度要用 `Measurement<UnitTemperature>`＋`usage: .weather` 或 `.general`**，系統會依 locale 的溫度偏好自動換成 °C 或 °F。【實測】locale 關鍵字 `@mu=celsius`／`@mu=fahrenhe` 會覆蓋地區預設值（`en_US@mu=celsius` 會輸出 °C）；系統設定「語言與地區 › 溫度」應該就是透過這個關鍵字影響 `Locale.current`【推論】。
- 使用者在 app 內自己選單位時，才用 `.asProvided` 搭配 `converted(to:)`。
- `usage` 沒有指定精度時會輸出 `162.428°F` 這種長小數，**一定要給 `numberFormatStyle`**。
- 相對時間：`Date.formatted(.relative(presentation: .numeric, unitsStyle: .abbreviated))` 在 zh_TW 會輸出「1分鐘前」。

### 8.3 更新頻率
- 活動監視器提供的選項是 **1 秒／2 秒／5 秒**（zh_TW：「頻率高（1秒）」「頻率較高（2秒）」「正常頻率（5秒）」）【實測系統字串】。監控工具可以照這三檔提供，預設值設 2–5 秒【推論】。
- 取樣頻率和重繪頻率要分開：取樣可以 1 秒一次；面板沒有顯示時（menu bar 面板關閉、視窗被遮住）就停止更新 UI【推論】。
- 圖表不閃爍的做法：資料 id 要穩定（用時間戳，不要每次產生新的 `UUID()`）；X 軸用固定寬度的滑動視窗、Y 軸用固定範圍；用 ring buffer 保留固定筆數，不要每次重建整個陣列【推論】。

## 9. Gauge 與 NSLevelIndicator

### 9.1 HIG【官方】
- 標籤要簡潔，說明目前值和範圍兩端；VoiceOver 會讀出看得到的標籤。
- 可以用漸層填滿路徑來傳達用途（溫度：紅到藍）。
- macOS 另有 **level indicator**（capacity：連續／分段；rating；relevance 很少用）。範圍大就用連續樣式。預設填色是**綠色**；數值到達特定程度時可以換填色，或用 tiered 一次顯示多段顏色。

### 9.2 SwiftUI `Gauge` 在 macOS（13.0 起）的樣式【SDK＋實測】
| `.gaugeStyle(...)` | macOS | 實測外觀 |
|---|---|---|
| `.automatic` | ✓ | AppKit level indicator：綠色連續條＋上方標籤＋兩端 min／max＋下方數值 |
| `.linearCapacity` | ✓ | 同上，綠色連續條；`.tint(.red)` 可以換填色 |
| `.accessoryLinear` | ✓ | 粗體數值＋黑色軌道＋圓點指示（不是填滿式） |
| `.accessoryLinearCapacity` | ✓ | 灰色細進度條＋標籤＋灰色小數值 |
| `.accessoryCircular` | ✓ | 開口圓弧＋圓點指示＋中央數值＋兩端 min／max |
| `.accessoryCircularCapacity` | ✓ | 完整圓環填滿＋中央數值；`.tint(Gradient(...))` 可以做綠黃橘紅漸層 |
| `.circular`、`.linear` | ✗ | 只有 watchOS 可用 |

- 【實測】`.automatic`、`.linearCapacity`、`.accessoryLinearCapacity`、`ProgressView` 背後是 AppKit 控制項，**`ImageRenderer` 畫不出來**，只會出現黃底禁止符號。要截圖或匯出圖片時，改用 `NSHostingView` 的 `cacheDisplay(in:to:)`，或改用 accessory 樣式。
- AppKit `NSLevelIndicator` 有 `warningValue`／`criticalValue`、`fillColor`／`warningFillColor`／`criticalFillColor`（10.13 起）、`drawsTieredCapacityLevels`。預設顏色「由系統定義，會因版本而異」，所以**不要寫死色碼**【SDK 標頭】。

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

## 10. WidgetKit（macOS）

### 10.1 能做什麼、不能做什麼【官方】
- Mac 上 widget 可以放在**桌面**和**通知中心**。system family 可用 small／medium／large／extraLarge（macOS 14 起）。**macOS 27 新增 `systemExtraLargePortrait`**【SDK＋WWDC26-277】；但 HIG（2025-12 版）的表格仍寫 Mac 不支援，兩者不一致，以 SDK 為準。accessory 系列在 macOS 都不能用【SDK】。
- **Widget 不能即時更新**。每個 widget 有自己的預算，常看的 widget 每天大約 **40–70 次**，約等於 **15–60 分鐘更新一次**；timeline entry 之間**至少間隔約 5 分鐘**。app 在前景時呼叫 reload 不扣預算，但**頻繁 reload 可能被節流**（WWDC26）。app 進背景時可以再呼叫一次 `WidgetCenter.shared.reloadTimelines(ofKind:)`【官方 DocC＋WWDC26-277】。
- macOS 26 起可以用 `WidgetConfiguration.pushHandler(_:)` 走 WidgetKit push 更新，但 push 不能取代 timeline【SDK＋官方】。
- 使用者可能比你更新得還頻繁地查看 widget 時，要**顯示資料最後更新時間**；日期時間讓系統自動更新（`Text(date, style: .relative)`），不要佔用更新預算。不要用 placeholder 蓋住舊資料【官方】。
- 開發時打開 **WidgetKit developer mode** 可以解除預算限制（WWDC26-277）。
- 監控工具的建議【推論】：widget 只顯示「目前狀態＋最後更新時間＋粗略走勢」；即時的秒級數值放在 menu bar extra 或浮動面板。
- 設計規則：一個 widget 只做一件事；文字 ≥ **11pt**；邊距標準 **16pt**，緊湊時 **11pt**（部分情境邊距更小，例如 Mac 桌面與 iPhone／iPad 鎖定畫面，以 HIG Widgets 為準）；用 `ContainerRelativeShape` 讓內容圓角對齊 widget 圓角；說明文字用動詞開頭（「查看 CPU 溫度與最近走勢。」），不要寫「這個 widget 會…」；placeholder 用半透明形狀代表文字和圖片【官方】。
- iPhone 的 widget 放到 Mac 上時會用 iOS 的字型尺寸；原生 Mac widget 用 macOS 尺寸，**共用程式碼時要檢查字級**【官方 DocC】。

### 10.2 Rendering mode 與 Liquid Glass【SDK＋官方】
| `widgetRenderingMode` | 何時出現 | 系統會做什麼 |
|---|---|---|
| `.fullColor` | Mac 桌面、通知中心（預設外觀） | 不改顏色 |
| `.accented` | 使用者選「染色」或「清透」外觀時 | 移除背景，換成染色效果或 Liquid Glass；分成 accent 群組和 primary 群組，在 iOS／macOS 都染成**白色**；不透明圖片變純白 |
| `.vibrant` | Mac 桌面（widget 退到背景時）、iPhone／iPad 鎖定畫面 | 去飽和，依背景做 vibrancy；用灰階表現層次，亮度決定對比 |

- **官方文件互相矛盾**：HIG Widgets 的表格寫 Mac 的 Accented 是「Not supported」；但 WidgetKit DocC《Optimizing your widget for accented rendering mode and Liquid Glass》和《Preparing widgets…》都說 Mac 也用 accented 和 clear glass。作者環境 macOS 27 的全域設定有 `AppleIconAppearanceTintColor`【實測】。**結論：Mac widget 三種模式都要支援。**
- 在 `accented` 和 `vibrant` 模式下，**狀態色會消失**（全部變白或變灰），所以狀態一定要靠 SF Symbol 形狀和文字表達【官方＋推論】。
- API（macOS 起）：`widgetRenderingMode`、`widgetAccentable(_:)` 13.0；`Image.widgetAccentedRenderingMode(.accented/.desaturated/.accentedDesaturated/.fullColor)` 15.0；`containerBackground(_:for: .widget)`；`showsWidgetContainerBackground`。`fullColor` 只用在媒體圖（專輯封面）。`levelOfDetail` 在 macOS 不可用（只有 iOS／visionOS）。

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
                Image(systemName: level.symbol)                         // 形狀在任何模式都保留
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
            Text(entry.date, style: .relative).font(.caption2).foregroundStyle(.secondary)  // 最後更新時間
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
            .configurationDisplayName("CPU 溫度")
            .description("查看 CPU 溫度與最近走勢。")
            .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

## 11. 坑

1. **Y 軸用動態範圍做即時圖**：每筆新資料都讓刻度跳動，使用者會以為數值在劇烈變化。百分比固定 0–100，溫度固定合理區間。
2. **長條圖 Y 軸不從 0 開始**：高度比例失真。折線圖則相反，不必從 0 開始。
3. **只用紅綠區分狀態**：色盲看不出來，widget 在 accented／vibrant 模式下也會把顏色洗掉。要加 SF Symbol 形狀和文字。
4. **淺色模式用 `.green`／`.orange`／`.yellow` 當小字或細線**：對比只有 1.5–2.3。文字用 label 色，只給符號上色；細線改成加粗或加虛線。
5. **連寫兩次 `.foregroundStyle` 想讓符號有色、文字無色**：【實測】內層的設定會贏，整個 Label（含文字）都變橘色。要把 `Image` 和 `Text` 拆開，分別設定。
6. **資料的 `id` 每次 render 都重新產生 `UUID()`**：Swift Charts 會把所有點當成新資料，整張圖重播動畫、閃爍。用時間戳當 id。
7. **動畫時長 ≥ 取樣間隔**：動畫永遠播不完，看起來在抖。Reduce Motion 開啟時改用 `.identity`。
8. **數字沒加 `monospacedDigit()`**：「1」比「8」窄，數值跳動時整行左右晃；在 menu bar 會連帶推動其他圖示。
9. **溫度寫死 `"\(v)°C"`**：美國使用者看到的是攝氏。用 `Measurement`＋`usage: .weather` 或 `.general`，而且一定要指定精度。
10. **zh_TW 的時間軸標籤太長**（「下午2:35」）；**用 `.hour(.twoDigits(amPM: .omitted))` 會把 14:35 顯示成「02:35」**（12 小時制又省略上下午，時間有歧義）【實測】。短時間的滑動視窗改用相對秒數的數值軸（「−60 秒」），或只標頭尾兩個刻度。
11. **想做秒級 widget**：做不到（每天 40–70 次、entry 至少間隔約 5 分鐘）。即時數值放 menu bar，widget 顯示「最後更新時間」。
12. **Mac widget 只測 full color**：HIG 表格說 Mac 不支援 accented，但 DocC 說 Mac 也有 tinted／clear。三種模式都要在 Xcode canvas 預覽。
13. **用 `ImageRenderer` 匯出含 `Gauge(.automatic/.linearCapacity)`、`ProgressView` 的畫面**：只會畫出禁止符號。
14. **用 `.gaugeStyle(.circular)` 或 `.linear`**：這兩種只有 watchOS 可用，macOS 編不過。
15. **大量資料點用 `ForEach` 加 `LineMark`**：幾萬筆就會卡。macOS 15 起改用 `LinePlot(data, x: .value(…, \.kp), …)`，資料依樣式分組，轉換用的屬性存成 stored property。
16. **3D 圖用在監控數據**：Apple 說 3D 只適合「形狀比數值重要」的三維資料。`chart3DCameraProjection` 在 visionOS 不可用，`Chart3DRenderingStyle` 只有 visionOS 可用。
17. **tooltip 超出圖表範圍被裁切**：選取的 annotation 要加 `overflowResolution: .init(x: .fit(to: .chart), y: .disabled)`。
18. **每次取樣都發 VoiceOver 公告**：很吵。只在狀態跳級時用 `AccessibilityNotification.Announcement` 公告。
19. **看得到的軸標籤沒對輔助技術隱藏、自己又逐點寫 label**：VoiceOver 會重複念。Swift Charts 已經有預設的 Audio Graph，自訂時用 `accessibilityChartDescriptor` 補標題和摘要即可。
20. 【實測】Console 可能出現 `Charts: Custom UnitPoint values are not supported in AxisValueLabel's anchor property`。渲染本檔範例時出現過，但範例裡沒有設定 anchor，來源沒有定位出來；畫面正常，可以先忽略。
