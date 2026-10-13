# 給另一台電腦的 Pi agent：安裝 GPT / OpenAI status line

## 目標與範圍

將這份資料夾中的 status line 安裝為該電腦使用者的全域 Pi footer。保留對方現有的模型、provider、主題、其他套件及憑證設定；只替換 statusLine 和對應的 pi-statusline 套件宣告。

這是來源電腦正在使用的腳本與已安裝套件快照，不是重寫版。來源環境為 Pi 0.99.1、Node 22.23.2、pi-statusline package.json 版本 0.0.2；vendor 的 README 可能比實際程式舊，原始碼才是準據。無需連網下載 statusline 套件。

## 安裝步驟

1. 在這份資料夾讀取 `install.mjs`、`statusline-openai.mjs`，以及 `vendor/pi-statusline/src/`，確認安裝與執行行為。執行 `node --version`、`pi --version`，確認 Pi 可啟動，Node 至少 22.19。缺少 Pi 時依目標電腦的官方安裝方式安裝，不自動改動既有 Pi 版本。
2. 檢查全域 `~/.pi/agent/settings.json` 和目前專案的 `.pi/settings.json`，以及手動載入的 extensions。若已從其他本機路徑或 Git 載入 pi-statusline，先確認後移除重複宣告；安裝腳本只自動替換 npm:pi-statusline 與本安裝目的路徑。若有另一個 setFooter 擴充套件，先協調保留哪個，避免互相覆蓋。若設定了非預設 `PI_CODING_AGENT_DIR`，停止自動安裝：這份 vendor 擴充套件的 config.ts 仍固定讀取 ~/.pi/agent/settings.json，需另行適配。
3. 在本資料夾執行：
   ```sh
   node install.mjs
   ```
   完成條件：指令成功輸出 Installed、Package、Backup 三個路徑。腳本會先備份原設定、同名腳本及目的套件（若存在），將快照複製到使用者目錄，再合併設定。settings.json 解析失敗時會停止，請修正 JSON 後重試。備份可能含目標電腦原設定中的秘密，留在該電腦即可，不要上傳。
4. 請使用者重新啟動 Pi。OpenAI 額度需要該電腦自己的 OpenAI Codex OAuth 登入；未登入時請使用者透過 Pi `/login` 選擇 OpenAI Codex 完成登入。API key 登入不等同 ChatGPT 訂閱額度登入。**不複製來源電腦 auth.json，也不將任何 token 顯示到輸出或文件。**
5. 驗收：進入互動式 Pi，確認 footer 顯示當前模型、思考等級、Ctx、目錄；Git repo 中應有分支。以 OpenAI Codex 登入且 usage endpoint 可用時，應另外顯示 OpenAI 5h / 7d（實際標籤依伺服器回覆）、已使用百分比與重置倒數。切換模型或思考等級、完成一個 turn 後應更新。

## 顯示與限制

- 彩色單行：模型 + thinking、Ctx 10 格進度條、OpenAI 短期／長期額度、資料夾、Git branch。
- 百分比表示 **已使用**，不是剩餘額度。
- OpenAI usage 查詢讀取目標電腦 ~/.pi/agent/auth.json 的 openai-codex access/accountId，只送至 https://chatgpt.com/backend-api/wham/usage；不會自行刷新 OAuth token。
- 查詢 timeout 8 秒，statusLine command timeout 10 秒。成功結果在 ~/.pi/agent/cache/openai-codex-usage.json 快取 30 秒。
- usage 是非公開穩定 API，可能因服務變更、帳戶方案、過期登入或網路而無法取得；此時略過 OpenAI 區段，其餘資訊仍顯示。
- 不是每秒刷新：隨 session、turn、模型、thinking 等事件更新，倒數在下一次 refresh 才改變。
- vendor 擴充套件會在該電腦 ~/.pi/agent/statusline-transcripts 產生本地 transcript adapter。移轉包沒有攜帶來源對話，但此擴充套件執行後會產生目標電腦的對話資料，應視為私密資料。

## 排錯與回復

- 全部不顯示：確認 local package 宣告有效、沒有重複 footer 擴充套件、重啟 Pi，檢查專案 `.pi/settings.json` 是否覆蓋 statusLine，以及 Pi 啟動時的 extension 載入錯誤。
- 只有 OpenAI 額度缺少：請使用者確認 OpenAI Codex 登入狀態與網路；不要印出 auth.json。成功快取可短暫保留舊資訊。
- 跨版本載入失敗：保留錯誤訊息，核對目標 Pi Extension API；不要直接安裝最新版 npm 套件取代快照，否則不再是原環境複製。
- 回復：關閉 Pi，從安裝輸出的 Backup 路徑還原 settings.json、原腳本和原本地套件（若有）。若備份後曾改過其他設定，只還原 packages 中相關宣告及 statusLine。原本不存在 settings.json 時，移除新加的宣告即可。安裝新增的 statusline-openai.mjs 和 statusline-packages/pi-statusline 可在確認不被引用後刪除。

## 回報給使用者

回報 Pi/Node 版本、安裝與備份路徑、是否驗收 footer、是否驗收 OpenAI 額度。若未能開啟互動 UI，明確區分「腳本測試通過」與「UI 尚未驗證」。
