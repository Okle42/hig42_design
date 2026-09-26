import SwiftUI

// 一個 macOS 風扇監控 app 的設定與清單畫面（待審查）
struct FanListView: View {
    let fans: [Fan]
    @State private var showDelete = false

    var body: some View {
        List(fans) { fan in
            HStack {
                Text(fan.name).font(.system(size: 17))
                Spacer()
                Text("\(fan.rpm) RPM")
                    .font(.system(size: 12))
                    .foregroundColor(Color(red: 0, green: 0.478, blue: 1))   // #007AFF
            }
            .padding()
            .glassEffect()
        }
        .toolbar {
            ToolbarItem {
                Button { } label: { Image(systemName: "gearshape") }   // 開設定
            }
            ToolbarItem {
                Button("清除紀錄") { showDelete = true }
                    .buttonStyle(.glassProminent)
            }
            ToolbarItem {
                Button("匯出...") { }
                    .buttonStyle(.glassProminent)
            }
        }
        .alert("確定要清除嗎？", isPresented: $showDelete) {
            Button("是", role: .destructive) { }
            Button("否") { }
        }
        .animation(.bouncy, value: fans)
    }
}

struct SettingsView: View {
    @State private var threshold = 85.0
    @State private var draft = 85.0

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("偏好設定").font(.system(size: 28, weight: .heavy))
            Slider(value: $draft, in: 60...100)
            Text("溫度門檻：\(Int(draft))°C").foregroundColor(.green)
            HStack {
                Spacer()
                Button("取消") { draft = threshold }
                Button("確定") { threshold = draft }
            }
        }
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 16).fill(Color(white: 0.1)))
        .frame(width: 400, height: 300)
    }
}

struct Fan: Identifiable, Equatable { let id = UUID(); let name: String; let rpm: Int }
