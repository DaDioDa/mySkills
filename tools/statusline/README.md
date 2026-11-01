# Statusline 可攜包

**只打包目前 pi 與 Claude Code 的 statusline；第三方 extensions 僅列在 `EXTENSIONS.md`，不含插件原始碼、node_modules、subagent 定義或完整個人設定。**

## 內容

- `pi/agent/statusline-openai.mjs`：pi statusline。
- `pi/agent/extensions/tokps/index.ts`、`stats.mjs`：pi statusline 的必要 tok/s 統計相依。
- `pi/settings.statusline.json`：pi statusLine 設定範本。
- `claude/statusline-command.sh`：Claude Code statusline。
- `claude/settings.statusline.json`：Claude Code statusLine 設定範本。
- `EXTENSIONS.md`：目前使用的插件名稱、作者、來源、安裝指令。

## 還原 pi statusline

1. 安裝 pi、Node.js，並執行 `pi install npm:pi-statusline`。
2. 將 `pi/agent/` 裡的內容複製到新電腦的 `~/.pi/agent/`，保留目錄結構。
3. 將以下 **statusLine 欄位合併** 到 `~/.pi/agent/settings.json`（不要覆蓋其他設定），替換成新電腦的實際路徑：

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "node \"C:/Users/你的帳號/.pi/agent/statusline-openai.mjs\"",
       "timeoutMs": 10000,
       "refreshIntervalMs": 1000
     }
   }
   ```

4. 重新啟動 pi。登入 openai-codex 後，才能查詢 OpenAI 額度；tok/s 在有新回應後顯示。

若使用 `PI_CODING_AGENT_DIR`，請改用該目錄。

## 還原 Claude Code statusline

1. 安裝 Git for Windows（Bash 5+）。
2. 將 `claude/statusline-command.sh` 複製到 `~/.claude/`。
3. 將以下欄位合併到 `~/.claude/settings.json`，按實際位置修改路徑：

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "\"C:/Program Files/Git/bin/bash.exe\" \"C:/Users/你的帳號/.claude/statusline-command.sh\""
     }
   }
   ```

4. 重新啟動 Claude Code。

## 注意

- 修改前先備份新電腦的既有設定與同名檔案。
- 範本中的 `__PI_AGENT_DIR__`、`__GIT_BASH__`、`__CLAUDE_DIR__` 是佔位字串，必須替換後才能使用。
- 不包含登入憑證、API 金鑰、對話紀錄、快取或舊 tok/s 統計。
- 來源 pi 版本為 1.4.0。尚未在另一台電腦實測還原。
