# 來源

概念改寫自 [cursor/plugins](https://github.com/cursor/plugins) 的 `pstack/skills/recall`（commit `ab69380dd50ee47d426b35cb8369cffdddafc218`），授權為 MIT（Copyright (c) 2026 Lauren Tan），全文見同目錄 `LICENSE`。

與原版的差異：

- 對話紀錄來源從 Cursor 改為 Claude Code、Codex、Pi，並以 git 為主幹。
- 移除對 `why`、`session-pickup`、`automate-me`、`unslop`、`poteto-mode` 的依賴，不查 issue tracker、聊天頻道與錯誤追蹤。
- 不開 subagent，改為只抽必要欄位以控制 context。
- 分成近況與斷點兩種模式，輸出改為繁體中文，狀態標籤改為以 git 為依據。
- 專案範圍除了 cwd，也用分支、Codex git 中繼資料、已刪 worktree 目錄、搬家前舊位置、改過的檔案來判斷。
- 讀 repo 內的本機 issue tracker，比對未合併分支與主線的票狀態；線上 tracker 不讀。

原版內容可用以下指令取回：

```bash
git clone --filter=blob:none https://github.com/cursor/plugins.git
cd plugins
git show ab69380dd50ee47d426b35cb8369cffdddafc218:pstack/skills/recall/SKILL.md
```
