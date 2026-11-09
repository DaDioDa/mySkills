---
name: slim
description: 把 Claude Code 瘦身成白名單：內建的 skill 與工具預設全關，只開白名單上的。
disable-model-invocation: true
---

# Slim

把 `~/.claude/settings.json` 調成**白名單**狀態：下面白名單上的 skill 與工具開著，其他內建的一律關掉。白名單是唯一的真相來源。想改開關，就改這份清單，再跑一次。

只改 user 層的 `~/.claude/settings.json`。其他鍵（hooks、statusLine、model、language 等）原樣保留。

## 白名單

**工具**

- 檔案與指令：`Bash`、`PowerShell`、`Read`、`Edit`、`Write`、`NotebookEdit`、`Glob`、`Grep`、`Skill`、`ToolSearch`
- 程式碼審查：`ReportFindings`
- 子代理與背景工作：`Agent`、`SendMessage`、`ListAgents`、`TaskCreate`、`TaskUpdate`、`TaskList`、`TaskStop`、`SubagentHandback`、`Monitor`、`ScheduleWakeup`
- 網路：`WebFetch`、`WebSearch`
- 互動：`AskUserQuestion`、`SendFeedback`、`EndConversation`
- Worktree：`EnterWorktree`、`ExitWorktree`

**內建 skill**：`claude-api`、`update-config`

**非內建 skill**：使用者自己的（`~/.claude/skills/<name>/`）和 plugin 帶來的（名稱有 `xxx:` 前綴）全部保留。claude.ai 同步來的 skill 全關。

**MCP**：全關。

## 1. 備份

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-$(date +%Y%m%d-%H%M%S)
```

完成條件：備份檔存在，大小和原檔一樣。

## 2. 盤點

從你自己的 context 列出兩份清單：

- **工具**：已載入的工具定義、system-reminder 裡的延後載入工具名稱，以及所有 `mcp__*` 工具。
- **skill**：skill 清單上的每一個名稱。

逐一標成「保留」或「關閉」：

- 工具：在白名單上就保留，其他關閉。
- skill：名稱有 `:` 的是 plugin，保留。沒有 `:` 的，先看 `~/.claude/skills/<name>/` 有沒有這個資料夾，有就保留。再看 `~/.claude/skills/synced/*/<name>/`，有就是 claude.ai 同步來的，交給第 3 步的 `syncClaudeAiSkills` 關掉。兩個都沒有，就是內建的，照白名單決定。

完成條件：context 裡的**每一個**工具和 skill 都有標記，沒有一個漏掉。

## 3. 寫設定

讀 `~/.claude/settings.json`，合併以下內容。原有的其他項目照樣留著，只加不換：

- 最上層設：`"disableWorkflows": true`、`"disableClaudeAiConnectors": true`、`"syncClaudeAiPlugins": false`、`"syncClaudeAiSkills": false`、`"enableArtifact": false`。`disableClaudeAiConnectors` 關掉 claude.ai 連接器；兩個 `syncClaudeAi*` 關掉 claude.ai 同步來的 plugin（連同它們帶來的 MCP）和 skill。
- `permissions.deny`：
  - 把每個標成「關閉」的工具，用**裸名稱**加進去，例如 `"CronCreate"`。裸名稱會把工具定義整個拿掉；`Bash(rm *)` 這種有範圍的規則只會擋呼叫，定義還是照樣送出。
  - 剩下的 MCP 工具，每個伺服器加一條前綴，例如 `"mcp__claude-in-chrome"`。
  - 白名單上的工具如果出現在這裡，就移除。
- `skillOverrides`：
  - 每個標成「關閉」的內建 skill，設成 `"user-invocable-only"`。這樣模型看不到它，省下一樣多的 tokens，使用者還是可以自己打 `/name` 叫出來。
  - 白名單上的 skill 如果有 override，就移除。

## 4. 驗證

```bash
python -I -c "import json,os; json.load(open(os.path.expanduser('~/.claude/settings.json'), encoding='utf-8')); print('ok')"
```

再檢查兩件事：白名單上的工具沒有出現在 `permissions.deny`，白名單上的 skill 沒有出現在 `skillOverrides`。

完成條件：JSON 讀得進來，兩項檢查都是空的。JSON 壞掉會讓整個檔案的設定失效，所以讀不進來就用第 1 步的備份還原，再重做第 3 步。

## 5. 回報

告訴使用者：

- 這次新增和移除了哪些 deny 規則與 skill override。
- 備份檔的完整路徑。
- 要重開 Claude Code，再打 `/context` 確認 System tools、MCP tools、Skills 三行都變小了。

## 注意

- `ExitPlanMode` 不在白名單。使用者按 Shift+Tab 進 plan mode 時，模型就沒辦法把計畫交出去核准。使用者要用 plan mode，就把 `EnterPlanMode`、`ExitPlanMode` 加進白名單。
- 延後載入的工具平常只送出名字，關掉省得不多。真的省到的，是一直載入的工具和 skill 的描述。
