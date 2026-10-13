# Pi GPT Status Line 移轉包

將整個資料夾或 `PiStatusLine.zip` 帶到另一台電腦；zip 請先解壓縮。

給那台 Pi agent 的指令：

> 請讀取這個資料夾的 HANDOFF.md，依照交接步驟幫我安裝相同的 GPT / OpenAI status line，保留我原有的其他設定。

內容：
- `statusline-openai.mjs`：原機正在使用的自訂顯示腳本。
- `vendor/pi-statusline/`：原機已安裝的擴充套件完整快照。
- `install.mjs`：跨平台安裝、備份與合併設定；在目標電腦執行 `node install.mjs`。
- `HANDOFF.md`：安裝、驗收、排錯和還原交接。
- `test.mjs`：執行 `node test.mjs`，使用暫存 home 測試，不碰真實憑證或網路。

移轉包不含 auth.json、API key、usage cache 或來源對話紀錄。另一台電腦要使用自己的 OpenAI Codex 登入。

已在來源電腦通過腳本語法與隔離測試；目標電腦的實際 Pi footer 仍需依 HANDOFF.md 驗收。
