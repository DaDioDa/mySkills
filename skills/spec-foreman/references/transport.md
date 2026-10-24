# Herdr：短派遣、可靠回收

## 每 run 一次 discovery

確認 `HERDR_ENV=1`，讀已安裝 `herdr --help` 及需要的 group help；CLI 是語法權威。不用 bare `herdr`，不以缺參數的 mutating 命令探索。確認實際 shell、agent CLI flags、runtime 配置來源。

以 caller／明確 ID 查 layout、panes、agents，IDs 從 JSON 取得；不依賴 UI focus。使用 sibling pane、`--no-focus`、明確任務 worktree cwd，避免連續分割得過窄。Split 後等待 shell prompt／foreground shell 就緒，再 start。

## 每 dispatch double-check

1. 從共用配置或明確角色覆寫取得 kind、精確 provider/model、effort；native flags 明確指定，不更改全域預設。
2. 新 worker 才 start session 並取得 pane／agent／session identity；串行接票沿用原 identity／cwd，依 [execution](execution.md#串行-worker-接下一票) 準備。已安裝 CLI help 決定 argv。
3. **送產品任務前**查同一 process／session 的可靠 runtime metadata；不只核對 argv 或 worker 自述。沒有結構化來源才用設定 UI／footer fallback。
4. 把 requested／observed 配置與簡短來源指標記入 dispatch；一致才送任務。不複製完整 session 或多份 configuration 報告。Mismatch／不可證明則阻塞並問，不默默 fallback。

同一票補同步／修復沿用現有 session，不再全套啟動檢查；重啟、身份／配置變動跡象才重新核對。跨票復用仍核對 live identity 與當前配置，但不重做每 run discovery 或 start。

## Claude Code workers

Claude Code 遇到未允許的命令會停下等人確認，Herdr 顯示 `blocked`；Pi 沒有這層確認。權限方式在 [startup](startup.md) 問使用者一次，記入 state `worker_configuration.permission_mode`：

- `auto`（建議）：啟動加 `--permission-mode auto`。
- 允許清單：用 `--allowedTools` 列出。清單必須逐字涵蓋 brief 與測試契約要求的命令寫法，包括導向 log 檔的形式與 `git -C`；派工前拿 brief 裡每條命令對一次。

Worker `blocked` 時，讀畫面確認卡在哪個命令，立刻通知使用者並等待。不按 Esc 拒絕、不替使用者同意、不自行改權限設定。

## 送文字給 agent

`herdr agent prompt` 的文字只能放在命令列參數，shell 會先改寫它。Windows 實測（Git for Windows、Windows PowerShell 5.1）：

- Git Bash 把開頭是 `/` 的參數改成 Windows 路徑：`/compact` 變成 `C:/Program Files/Git/compact`。
- 雙引號內的 `$2`、`$VAR` 會被展開，未定義就變成空字串，不報錯。
- Windows PowerShell 5.1 會刪掉參數裡的 `"`，不報錯。

每次送 prompt：

1. 用檔案寫入工具把完整 prompt 寫進本 run 的 `prompts/<dispatch-id>.md`。路徑寫完整字面值，不用 shell 變數、函式或位置參數組字串。
2. 從 Git Bash 送出，只在這一行加 `MSYS_NO_PATHCONV=1`：

   ```sh
   MSYS_NO_PATHCONV=1 herdr agent prompt <pane-id-or-agent-name> "$(cat <prompt-file>)"
   ```

   其他命令不加，`--cwd /d/...` 這類路徑靠自動轉換。不用 Windows PowerShell 5.1 送 prompt。非 Windows 不需要 `MSYS_NO_PATHCONV=1`，同樣從檔案送。
3. 每個 dispatch 送出後核對一次，不持續盯：從 session 紀錄讀它收到的完整文字，與檔案比對，不截斷；再確認它第一個讀的檔案就是 prompt 裡的 brief 絕對路徑。不一致就停下這個 worker，修正後重送，不讓它自己猜要讀哪份。

## 串行接票的 compact

在前票整合、worker idle／停寫且新 input 已就緒後，使用 `herdr agent prompt` 對原 worker 送真正的 slash command。使用者已實測 Herdr → Pi 的以下方式可執行 compact；Git Bash 必須加 `MSYS_NO_PATHCONV=1`，否則 worker 收到的是 `C:/Program Files/Git/compact`：

```sh
MSYS_NO_PATHCONV=1 herdr agent prompt <pane-id-or-agent-name> "/compact"
```

Target 使用 dispatch 中的明確 pane ID 或唯一 live agent name，不依賴 UI focus；這裡只送 compact，不夾帶下一票任務。這是已確認的 Pi 通道，無需逐票重新探索；其他 agent kind 或版本／能力變動時才核實，不可用則回報 Main，不默默改成新 session。

Pi 也支援 `/compact [instructions]`；需要摘要重點時，把短指示接在 `/compact` 後，依上節寫成檔案再送：前票已完成；保留公開介面與測試用法、已接受修正、限制及來源路徑；下一票以新 brief／當前 Git 為準。compact 縮減上下文但保留摘要／近期訊息，不是清空記憶，也不保證省 token。

查同一 session 在本次操作後新增的成功 compaction entry（Pi 為 `type=compaction`），或同等可靠的原生成功事件，記錄來源指標；舊 entry、timeout、idle／done 不是成功。確認成功、身份／配置與 Git 未變，才送下一票；失敗／取消／結果不明先停留原 worker 回 Main 處理，不盲目重送 compact 或下一票。透過 event wait 回收，不輪詢完整 session。

## 短 prompt

提供 role、task brief、spec／ticket 與測試契約的絕對路徑，以及 result 路徑。Brief 本身只寫任務差異；共用事實用指標，不貼整份流程。

先各送一次任務，再等待任意完成的 worker；不要逐個等待整票完成才送下一位。使用 agent prompt／event／wait，實際 flags 依 CLI；Herdr wait timeout 是毫秒，原生 shell tool timeout 依 schema（常為秒），不可照抄數字。

## 回收

- `done`／`idle` 只代表可收輸入；正式短 result 或失敗 handoff、Git 版本及停止寫入才證明交件。
- Timeout／stalled／連線錯誤不證明未送達。查 live state、結果與 Git，再等待或求援，不盲目重送。
- 正常用 event wait；只有狀態邊界、錯誤才讀少量 terminal。Working 時用 visible，不大量回收 idle-only history。
- Pi 的提問選單在 Herdr 顯示為 `working`，不是 `blocked`，wait 不會因此醒來。所以角色檔禁止 workers 用提問選單，問題一律走失敗 handoff。
- 額度／provider 錯誤與 ticket 完成分開判斷；缺 result 不宣稱完成。
- 更新簡短進度：哪些票執行中／已整合、正在驗證什麼；長等待時避免讓使用者猜是否卡住。

只關本 run 建立、成果已收回且不再待命接票的 pane／agent；同一串行 worker 不在每票交件後關閉。Approval 交使用者，不替其批准，不停 server 或自行升級。Worktrees／branches 與暫存清理分開處理。
