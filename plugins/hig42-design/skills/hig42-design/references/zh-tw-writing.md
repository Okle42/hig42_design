# Traditional Chinese (zh-TW) UI writing — and English UI rules

> The Traditional Chinese terminology is based on frequency counts of the actual strings in the macOS 27 Traditional Chinese UI (compiled by the author), which is more reliable than third-party sites. Sources: see `SOURCES.md` in the repo, §11–12

## 1. Writing principles **[Official: HIG Writing]**
- Be clear and cut every word you can; **put the most important information first**.
- **Use verbs for buttons and links**; don't be cute (「傳送」 beats 「衝啦！」); never write 「按這裡」 ("click here") for a link.
- Keep wording consistent across multi-step flows: start with 「開始使用」 → middle steps 「繼續」 or 「下一步」 (pick one) → end with 「完成」.
- **Avoid possessives** (「喜好項目」 beats 「你的喜好項目」); **don't use 「我們」 ("we")** (「無法載入內容」 beats 「我們無法載入內容」).
- Write for the device: on touch devices say 「點一下」 (tap); on the Mac say 「按一下」 (click).
- Error messages explain how to fix the problem, without blame and without 「哎呀」 ("oops"); placeholders show an example (「name@example.com」).
- Settings labels describe what happens when the setting is on.

## 2. Traditional Chinese conventions **[System strings]**
| Rule | Evidence | Examples |
|---|---|---|
| **Ellipsis is 「⋯」 (U+22EF)**, not 「…」 (U+2026) or 「...」 | zh_TW strings: 「⋯」 1,339 times, 「…」 0 times | 設定⋯、列印⋯、載入中⋯ |
| **No space between Chinese and Latin letters or digits** | Adjacent 7,554 times vs. spaced 49 times | 關於這台Mac、輸出為PDF⋯、%@設定 |
| **Full-width punctuation** | 「，」 2,851 vs. 「,」 72; 「：」 1,001 | 輸出為：、色盤的新名稱： |
| **Quotation marks are 「」** | 3,773 times; “” almost never used | 隱藏「%@」、沒有「%@」的結果 |
| Parentheses are mostly full-width （） | 575 vs. 77 | |
| Chinese has no letter case | — | English title / sentence case rules don't apply |
| `%@` sits directly against Chinese text | — | 關於%@、結束%@、%@輔助說明 |

- Taiwanese web writing often puts a space between Chinese and Latin text, but **that is not the Apple UI convention**; to look like Apple, don't add the space. The few exceptions (「使用 Touch ID」, 「1 分鐘」) don't need to be imitated deliberately.
- Simplified Chinese uses 「…」 and 「退出」; don't copy Simplified Chinese conventions into Traditional Chinese.

## 3. When to add an ellipsis **[Official]**
- Menu items: add 「⋯」 to actions that need more information to complete (they open another interface for input or a choice): 打開⋯、重新命名⋯、輸出⋯、列印⋯、設定⋯.
- Buttons: add 「⋯」 when the button opens another window, view, or app.
- **Don't add it** to: 儲存 (Save), 關閉 (Close), 複製 (Duplicate), 打開最近使用過的檔案 (Open Recent).
- Omit the 「⋯」 when referring to the command in body text.

## 4. Common terminology (Apple's official Traditional Chinese translations)

### 4.1 The most commonly mistranslated
| English | ✅ Apple zh-TW | ❌ Common mistranslation |
|---|---|---|
| OK | **好** | 確定 |
| Copy | **拷貝** | 複製 (「複製」 is Duplicate) |
| Undo | **還原** | 復原、撤銷 |
| Quit %@ | **結束%@** | 退出 (Simplified Chinese) |
| Settings… | **設定⋯** | 偏好設定 (old name through macOS 12) |
| View (menu) | **顯示方式** | 檢視 |
| Help (menu) | **輔助說明** | 說明、幫助 |
| Minimize | **縮到最小** | 最小化 |
| Learn More | **更多內容** | 了解更多 |
| Open… (macOS menu) | **打開⋯** | 開啟 (common on iOS; macOS menus use 「打開」) |
| Import… / Export… | **輸入⋯ / 輸出⋯** | 匯入 / 匯出 |
| Inspector | **檢閱器** | 檢查器 |
| Sidebar | **側邊欄** | 側欄 |

### 4.2 Buttons and common terms
| English | zh-TW | English | zh-TW |
|---|---|---|---|
| Cancel | 取消 | Done | 完成 |
| Delete | 刪除 | Remove | 移除 |
| Add | 加入 | Save / Save As… | 儲存 / 儲存為⋯ |
| Don't Save | 不儲存 | Revert To | 回復成 |
| Keep / Discard | 保留 / 捨棄 | Replace | 取代 |
| Apply | 套用 | Continue | 繼續 |
| Pause / Stop | 暫停 / 停止 | Try Again | 再試一次 |
| Not Now | 稍後再說 | Allow / Don't Allow | 允許 / 不允許 |
| Back / Next | 返回 / 下一步 (flows), 下一個 (items) | Close | 關閉 |
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
| Keyboard Shortcuts | 鍵盤快速鍵 | Yes / No | 是 / 否 (avoid in alerts) |

### 4.3 Menus and windows
| English | zh-TW |
|---|---|
| About %@ | 關於%@ |
| %@ Settings (Settings window title) | %@設定 |
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

### 4.4 Nouns
設定、一般、進階、外觀、通知、隱私權與安全性、帳號、選單列、Dock、視窗、工具列、密碼 (Settings, General, Advanced, Appearance, Notifications, Privacy & Security, Account, Menu Bar, Dock, Window, Toolbar, Password).

## 5. English UI (when writing English UI text) **[Official]**
| Element | Capitalization |
|---|---|
| Menu titles, menu items | Title case, drop a / an / the |
| Buttons | Title case, start with a verb (HIG Buttons page; the Alerts page says sentence case, so Apple contradicts itself; follow the system's actual title case) |
| Alert title | Complete sentence → sentence case + period; fragment → title case, no punctuation |
| Alert message | Sentence case, complete sentences |
| Panel titles, table column headers, segmented control labels | Nouns, title case; no colon after column headers |
| Slider labels | Sentence case + colon |

- Title case: capitalize the first and last words; capitalize nouns, verbs, adjectives, and adverbs regardless of length; **capitalize prepositions of five or more letters** (About, Between) and lowercase those of four or fewer; capitalize the preposition in a phrasal verb (Start Up, Turn On).
- Write "OK," not "okay"; for instructions use "choose" (choose File > New), not "click on"; since macOS 13 it's called Settings.
- The English ellipsis is the single character 「…」 (U+2026, Option-;), not three periods.
