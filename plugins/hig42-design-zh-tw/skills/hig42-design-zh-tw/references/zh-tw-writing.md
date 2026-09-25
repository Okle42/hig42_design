# 介面文字：繁體中文（台灣）與英文規則

> 繁中用語依 macOS 27 繁體中文介面的實際用字統計（作者整理），比第三方網站可靠。來源清單見 repo 的 `SOURCES.md` §11–12

## 1. 寫作原則【官方 HIG Writing】
- 清楚、能少一字就少一字；**重要資訊放前面**。
- **按鈕與連結用動詞**；不要太可愛（「傳送」勝過「衝啦！」）；連結不寫「按這裡」。
- 多步驟流程用詞一致：開始「開始使用」→ 中間「繼續」或「下一步」（擇一）→ 結束「完成」。
- **少用所有格**（「喜好項目」勝過「你的喜好項目」）；**不用「我們」**（「無法載入內容」勝過「我們無法載入內容」）。
- 依裝置寫：觸控裝置說「點一下」，Mac 說「按一下」。
- 錯誤訊息說明怎麼修，不責怪、不說「哎呀」；placeholder 給範例（「name@example.com」）。
- 設定標籤描述「開啟時會做什麼」。

## 2. 繁中慣例【系統字串統計】
| 規則 | 證據 | 範例 |
|---|---|---|
| **省略號用「⋯」(U+22EF)**，不是「…」(U+2026) 或「...」 | zh_TW 字串「⋯」1339 次、「…」0 次 | 設定⋯、列印⋯、載入中⋯ |
| **中英、中數之間不加空格** | 緊貼 7554 處 vs 有空格 49 處 | 關於這台Mac、輸出為PDF⋯、%@設定 |
| **全形標點** | 「，」2851 vs「,」72；「：」1001 | 輸出為：、色盤的新名稱： |
| **引號用「」** | 3773 次，幾乎不用 “” | 隱藏「%@」、沒有「%@」的結果 |
| 括號多用全形（） | 575 vs 77 | |
| 中文沒有大小寫 | — | 英文 title／sentence case 規則不適用 |
| `%@` 直接黏在中文旁 | — | 關於%@、結束%@、%@輔助說明 |

- 台灣網路寫作常見「中英之間加空格」，但**那不是 Apple UI 的慣例**；要像 Apple 就不加。少數例外（「使用 Touch ID」「1 分鐘」）不必刻意模仿。
- 簡中用「…」和「退出」，繁中不要照抄簡中。

## 3. 省略號何時加【官方】
- 選單項目：需要更多資訊才能完成的動作（會開另一個介面讓人輸入或選擇）加「⋯」：打開⋯、重新命名⋯、輸出⋯、列印⋯、設定⋯。
- 按鈕：會開啟另一個視窗、view 或 app 的加「⋯」。
- **不加**：儲存、關閉、複製（Duplicate）、打開最近使用過的檔案。
- 內文提到該指令時不帶「⋯」。

## 4. 常用用語對照（Apple 繁中官方譯法）

### 4.1 最容易翻錯的
| English | ✅ Apple 繁中 | ❌ 常見錯譯 |
|---|---|---|
| OK | **好** | 確定 |
| Copy | **拷貝** | 複製（「複製」是 Duplicate） |
| Undo | **還原** | 復原、撤銷 |
| Quit %@ | **結束%@** | 退出（簡中） |
| Settings… | **設定⋯** | 偏好設定（macOS 12 以前的舊稱） |
| View（選單） | **顯示方式** | 檢視 |
| Help（選單） | **輔助說明** | 說明、幫助 |
| Minimize | **縮到最小** | 最小化 |
| Learn More | **更多內容** | 了解更多 |
| Open…（macOS 選單） | **打開⋯** | 開啟（iOS 常見，macOS 選單用「打開」） |
| Import… / Export… | **輸入⋯ / 輸出⋯** | 匯入 / 匯出 |
| Inspector | **檢閱器** | 檢查器 |
| Sidebar | **側邊欄** | 側欄 |

### 4.2 按鈕與通用詞
| English | 繁中 | English | 繁中 |
|---|---|---|---|
| Cancel | 取消 | Done | 完成 |
| Delete | 刪除 | Remove | 移除 |
| Add | 加入 | Save / Save As… | 儲存 / 儲存為⋯ |
| Don't Save | 不儲存 | Revert To | 回復成 |
| Keep / Discard | 保留 / 捨棄 | Replace | 取代 |
| Apply | 套用 | Continue | 繼續 |
| Pause / Stop | 暫停 / 停止 | Try Again | 再試一次 |
| Not Now | 稍後再說 | Allow / Don't Allow | 允許 / 不允許 |
| Back / Next | 返回 / 下一步（流程）、下一個（項目） | Close | 關閉 |
| Show / Hide | 顯示 / 隱藏 | Edit | 編輯 |
| Search | 搜尋 | Share… | 分享⋯ |
| Select All / Deselect All | 全選 / 取消全選 | Clear | 清除 |
| Refresh / Reload | 重新整理 / 重新載入 | Reset / Restore Defaults | 重置 / 回復預設值 |
| Enabled / Disabled | 已啟用 / 已停用 | On / Off | 開啟 / 關閉 |
| Options | 選項 | Default | 預設值 |
| None | 無 | Untitled | 未命名 |
| Loading… | 載入中⋯ | No Results | 沒有結果 |
| Error / Warning | 錯誤 / 警告 | Get Started | 開始使用 |
| Welcome to %@ | 歡迎使用%@ | Sign In / Sign Out | 登入 / 登出 |
| Get Info | 取得資訊 | Status | 狀態 |
| Update / Install | 更新 / 安裝 | Sort By | 排序方式 |
| **Open at Login** | **在登入時打開** | **Show in Menu Bar** | **在選單列中顯示** |
| Keyboard Shortcuts | 鍵盤快速鍵 | Yes / No | 是 / 否（alert 避免用） |

### 4.3 選單與視窗
| English | 繁中 |
|---|---|
| About %@ | 關於%@ |
| %@ Settings（設定視窗標題） | %@設定 |
| Services | 服務 |
| Hide %@ / Hide Others / Show All | 隱藏%@ / 隱藏其他 / 顯示全部 |
| Quit and Keep Windows | 結束並保留視窗 |
| File / Edit / Format / View / Window / Help | 檔案 / 編輯 / 格式 / 顯示方式 / 視窗 / 輔助說明 |
| New Window / New Tab | 新增視窗 / 新增標籤頁 |
| Open Recent / Clear Menu | 打開最近使用過的檔案 / 清除選單 |
| Close All / Close Window | 關閉全部 / 關閉視窗 |
| Duplicate / Rename… / Move To… | 複製 / 重新命名⋯ / 搬移到⋯ |
| Page Setup… / Print… | 設定頁面⋯ / 列印⋯ |
| Redo | 重做 |
| Cut / Paste / Paste and Match Style | 剪下 / 貼上 / 貼上並符合樣式 |
| Find… / Find and Replace… / Find Next | 尋找⋯ / 尋找與取代⋯ / 尋找下一個 |
| Show/Hide Toolbar / Customize Toolbar… | 顯示／隱藏工具列 / 自訂工具列⋯ |
| Show/Hide Sidebar / Inspector | 顯示／隱藏側邊欄 / 檢閱器 |
| Enter / Exit Full Screen | 進入全螢幕 / 離開全螢幕 |
| Zoom | 縮放 |
| Bring All to Front | 將此程式所有視窗移至最前 |
| Show Fonts / Show Colors | 顯示字體 / 顯示顏色 |

### 4.4 名詞
設定、一般、進階、外觀、通知、隱私權與安全性、帳號、選單列、Dock、視窗、工具列、密碼。

## 5. 英文介面（寫英文 UI 時）【官方】
| 元件 | 大小寫 |
|---|---|
| 選單標題、選單項目 | Title case，拿掉 a／an／the |
| 按鈕 | Title case、動詞開頭（HIG buttons 頁；alerts 頁寫 sentence case，Apple 自相矛盾，採系統實際的 title case） |
| Alert 標題 | 完整句 → sentence case＋句號；片語 → title case 無標點 |
| Alert 說明 | Sentence case、完整句 |
| Panel 標題、表格欄標題、segmented 標籤 | 名詞、title case，欄標題不加冒號 |
| Slider 標籤 | Sentence case＋冒號 |

- Title case：首尾字大寫；名詞／動詞／形容詞／副詞不論長短都大寫；**五個字母以上的介系詞大寫**（About、Between），四個以下小寫；片語動詞的介系詞大寫（Start Up、Turn On）。
- 寫「OK」不寫 okay；指令用 choose（choose File > New），不說 click on；macOS 13 起叫 Settings。
- 英文省略號用單一字元「…」(U+2026，Option-;)，不用三個句點。
