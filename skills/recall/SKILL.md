---
name: recall
description: 從 git 與 Claude Code／Codex／Pi 的對話紀錄，重建使用者在目前專案的工作脈絡，產出一份當前狀態簡報。用於「最近做了什麼」「過去兩週做了什麼」「上次做到哪」「幫我回想進度」。
disable-model-invocation: true
---

# Recall

使用者要開工或接續工作前，你幫使用者重建**這個專案**最近的工作脈絡，回一份精簡的繁體中文簡報：現在在哪、卡在哪、下一步做什麼。

git 是主幹，記錄「實際改了什麼」，而且不會消失。對話紀錄補上 git 看不到的東西：為什麼這樣改、討論過但還沒動手的事、反覆卡住的問題。兩邊衝突時，以 git 為準。

只讀這個專案、這段時間需要的東西，夠了就停。

## 1. 判斷模式與範圍

從使用者的話判斷模式：

- **近況模式**：「最近做了什麼」「這週」「過去兩週」。預設往回 7 天；使用者講了天數或週數就照講的。輸出依工作線分組。
- **斷點模式**：「上次做到哪」「我停在哪」。目標是最近一次工作階段，加上目前 git 的未 commit 狀態與所在分支。

收集專案的識別資料：

- repo 根目錄：`git rev-parse --show-toplevel`，以及它的資料夾名稱 `<repo>`
- 所有 worktree 路徑：`git worktree list --porcelain`
- 現存分支：`git branch --format='%(refname:short)'`
- remote：`git remote -v`

一個工作階段只要符合下列**任一條**，就屬於這個專案。比對路徑前先正規化：反斜線轉斜線、去掉結尾斜線、不分大小寫（Windows）。

1. cwd 等於 repo 根目錄或任一 worktree 路徑，或位在它們底下。
2. cwd 位在 `<repo>-worktrees/` 或 `<repo>/.claude/worktrees/` 底下（已刪除的 worktree 不在 `git worktree list` 裡，靠這條找回）。
3. 工作階段記錄的分支（Claude Code 每行的 `gitBranch`、Codex `session_meta` 的 `git.branch`）是這個 repo 的現存分支。`main`、`master`、`HEAD` 太通用，這條只認其他名稱。
4. Codex `session_meta` 的 `git.repository_url` 等於這個 repo 的某個 remote，或 `git.commit_hash` 在這個 repo 裡存在（`git cat-file -e <hash>`）。
5. cwd 的最後一段和 `<repo>` 完全同名，而且那個路徑現在已不存在。這是 repo 搬家前的舊位置，git 不記錄搬家。
6. 工作階段改過的檔案，去掉 cwd 前綴後在目前 repo 裡存在：至少命中 2 個，且命中數佔它改過的檔案一半以上。

已知會漏的：分支已刪、目錄命名沒有規則、又沒改過檔案的 worktree 工作階段。資料夾名稱只是開頭相同（例如 `<repo>_old`）的，不符合第 2、5 條，不要用前綴比對硬湊。

不是 git repo 時，用目前目錄當唯一路徑，只套第 1 條，照樣往下做（見第 3 步的備註）。

完成標準：用一行講出模式、日期範圍、專案路徑與 worktree 數，例如「近況模式，2026-10-13 ~ 10-27，範圍 mySkills（含 2 個 worktree）」，然後直接往下做，不必等回覆。

## 2. 讀 git 與 issue tracker

在 repo 根目錄跑，近況模式把 `<since>` 換成起始日期：

- `git status --short --branch`、`git stash list`
- `git log --all --since=<since> --date=short --format='%h %ad %d %s'`
- `git branch -vv`，以及 `git branch --no-merged <主線>`，找出還沒併回主線的分支
- 需要時用 `git show --stat <hash>` 看某個 commit 動了哪些檔案。只在某條工作線的狀態只能從 diff 判斷時才讀 diff 內容。

斷點模式只需要 status、stash、目前分支，加上最後幾個 commit。

**issue tracker**：看 repo 的 `AGENTS.md`／`CLAUDE.md` 有沒有指定 issue tracker。

- 指定的是 repo 裡的檔案（例如 `.scratch/<feature>/issues/*.md`）：先讀它指向的格式說明，照說明找出票檔與狀態行。狀態行實際寫法常和說明不同，`Status:` 與 `**Status:** done` 兩種都要能比對。
  - 對每個未合併分支，用 `git diff --name-only <主線>...<branch> -- <tracker 目錄>` 找出兩邊不同的票檔，再用 `git show <主線>:<路徑>` 與 `git show <branch>:<路徑>` 比對狀態行，不用切換分支。狀態不同的票，列進 Threads，例如「票 26–29 在 `origin-gps` 是 done，main 仍是 ready-for-agent，尚未合併」。
  - 主線上還沒 done、且所屬 feature 目錄在範圍內有 commit 的票，也列出來。
- 指定的是線上 tracker（GitHub、GitLab、Linear 等）：不去查，在簡報最後一行註明「issue tracker 在線上，未讀」。
- 沒有指定：跳過。

完成標準：每個未合併分支都比對過票的狀態，或確認 repo 沒有本機 tracker。

## 3. 讀對話紀錄

三種工具的紀錄都是 JSONL，一行一筆。檔案常有幾 MB，大部分是工具輸出與 token 統計。

**怎麼讀：**

- 一律臨時寫 `python -I -X utf8 -c '...'`（或 grep）只抽出下表列的欄位，`cat`、Read、`head` 整個 JSONL 都不行。沒有 `python` 指令的機器（例如 macOS）改用 `python3`。
- 一定要加 `-X utf8`，否則中文在 Windows 終端機（cp950）印出來會直接報錯。`-I` 會忽略 `PYTHONIOENCODING`，設環境變數沒用。開檔用 `encoding='utf-8', errors='replace'`；解析壞行只接 `ValueError`，裸 `except:` 會吃掉 generator 的 `GeneratorExit`。
- 先用檔案修改時間篩掉範圍外的檔案（`find ... -mtime -N`），再打開剩下的檔案，照第 1 步的條件判斷是否屬於這個專案。
- 排除目前這個對話本身：你正在執行的那個工具（Claude Code、Codex 或 Pi）底下，修改時間最新、內容是這次 recall 的那個檔案。
- 由主對話自己讀，不開 subagent。

**分兩段讀**，因為兩週的量全抽出來常有上萬字：

1. **總覽**：每個工作階段印一行，包含日期、工具、cwd、符合第 1 步哪一條、標題（Claude Code 用 `aiTitle`，其他用第一句使用者訊息的前 60 字）、使用者訊息數、改過的檔案數。只有一兩句寒暄（「hi」「你好」）的工作階段直接丟掉。
2. **細讀**：從總覽挑出需要的工作階段，抽使用者訊息、agent 回覆、改過的檔案，每段截到約 300 字，但有兩個例外：
   - 每個工作階段的**最後一則 agent 回覆**一律保留，上限約 700 字。工作階段的結果（「已裝好」「測試通過」）通常在這裡。
   - **compact 摘要**（Claude Code `isCompactSummary:true` 的訊息）開頭幾百字是固定樣板。從 `Summary:` 之後開始讀，依小節名稱（不是編號，編號和標題後的括號會變）抽 `Pending Tasks`、`Current Work`、`Optional Next Step`、`Errors and fixes`，每節截到約 400 字。

   近況模式挑每條工作線最新的一兩個工作階段細讀；斷點模式只細讀那一個。

**subagent 開的工作階段**：Pi 和 Codex 的 subagent 會寫成獨立的檔案，cwd 也一樣。第一句是 agent 寫的任務說明（例如「Implement the spec at …」「請唯讀探索 …」「任務：…只做 prototype」），而不是使用者口吻。這類工作階段併到同一時段的主工作階段，不當成獨立工作線。

| 工具 | 位置 | 專案判斷用的欄位 | 要抽的內容 | 要跳過的 |
|---|---|---|---|---|
| Claude Code | `~/.claude/projects/*/*.jsonl`（子資料夾裡的是 subagent，跳過） | 每行的 `cwd`、`gitBranch` | `type:"ai-title"` 的 `aiTitle`（工作階段標題）；`type:"user"` 且 `message.content` 是字串或含 `text` 區塊的使用者訊息；`isCompactSummary:true` 的摘要；`type:"assistant"` 的 `text` 區塊；`tool_use` 中 `Edit`／`Write`／`MultiEdit` 的 `input.file_path` | `isMeta:true`、`isSidechain:true`、`tool_result`、`thinking`、`api-request*`、`cost-state` 等其他 type；以 `<command-`、`<system-reminder>`、`<local-command`、`<task-notification>` 開頭的文字。同一段對話被續接或 fork 時，會出現內容相同、標題相同的檔案，只讀較新的那個 |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | 第一行 `session_meta` 的 `payload.cwd`、`payload.git`（不一定有） | `response_item` 中 `payload.type:"message"`、`role:"user"` 的 `input_text`；`event_msg` 中 `payload.type:"task_complete"` 的 `last_agent_message`；`custom_tool_call` 的 `input` 裡 `*** Update File:`／`*** Add File:` 後面的路徑（`input` 常是包在 JS 字串裡的 patch，路徑到真正換行或字面上的 `\n` 為止） | `role:"developer"`；以 `# AGENTS.md`、`<environment_context>`、`<INSTRUCTIONS>` 開頭的 user 訊息；`reasoning`、`token_count`、`*_output`、`world_state` |
| Pi | `~/.pi/agent/sessions/--<slug>--/*.jsonl` | 第一行 `type:"session"` 的 `cwd` | `type:"message"` 中 `message.role` 是 `user` 或 `assistant` 的 `text` 區塊；assistant `toolCall` 中 `edit`／`write` 的 `arguments.path` | `role:"system"`、`role:"toolResult"`、`model_change`、`thinking_level_change` |

格式和表上對不起來時（欄位改名、多了新 type），先抽樣幾行看結構再調整，並在簡報最後一行註明哪個工具的紀錄沒讀成功。某個工具在範圍內沒有紀錄也是一種結果，不用特別說明。

**斷點模式**：三個工具合起來，取這個專案最近的一個工作階段。如果它只有一兩句問答、沒有實際進展，就往前再取一個。

**不是 git repo 時**：簡報開頭註明「這個目錄沒有 git，以下狀態來自對話紀錄，未經驗證」，狀態標籤改用 `[agent 回報完成]` 和 `[只有討論，未動工]`。

完成標準：總覽涵蓋範圍內每個屬於這個專案的工作階段；每條工作線至少細讀過一個工作階段，且讀到了它的最後一則回覆。

## 4. 對齊與分組

把對話紀錄裡提到的工作，對到 git 裡的 commit、分支、未 commit 的變更與票的狀態：

- 對話裡說做完了，git 也有對應 commit：已完成。
- 對話裡說做完了，git 找不到：照 git 判斷，可能還沒 commit，或根本沒做。
- 分支上做完了，主線還沒有（commit 或票的狀態只在分支上）：標 `[進行中 <branch>]`，並寫明尚未合併。
- 對話裡討論過，git 完全沒痕跡：只有討論，未動工。這類最容易被忘記，一定要列。
- 做了又 revert，或同一個問題換了好幾種解法：放進 Problems，讓下次從上次失敗的地方接著做。

完成標準：每條工作線都有恰好一個狀態標籤。

## 5. 輸出

依序四段，用繁體中文：

- **Capsule**：最多 5 點，這個專案整體在做什麼、目前在哪。
- **Threads**：每條工作線一行，開頭恰好一個狀態標籤：
  - `[已 commit <hash>]`
  - `[進行中 <branch>]`：在分支上，還沒併回主線
  - `[未 commit]`：工作目錄裡有改動
  - `[已 revert <hash>]`
  - `[只有討論，未動工]`

  斷點模式只列目前那一條。
- **Problems**：最多 5 點，反覆出現的卡關、做了又撤掉的嘗試。沒有就省略這段。
- **Next move**：一個最具體的下一步，例如要跑的指令、要改的檔案、要做的決定。

寫法：

- 每點一行，只寫事實，結尾停在 Next move。
- 引用時附來源：commit 寫 hash，票寫檔名或編號，對話寫「工具 + 日期」，例如「Codex 10-20」。
- 一個畫面放不下時，先刪細節，保留每條工作線。
- 只寫這個專案的內容。
