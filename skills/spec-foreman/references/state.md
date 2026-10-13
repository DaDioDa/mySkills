# 最小紀錄與暫存生命週期

Main 是 state 唯一寫入者，使用 UTF-8、temp file + 同目錄 rename 更新。Worker 只發布自己的短 result／失敗 handoff；所有路徑絕對、Git SHA 完整。

## 儲存

透過 OS temporary-directory API 建立唯一 `spec-foreman-<random>/` run 目錄，不把流程檔寫進產品或 Git common directory。可用 `tempfile.mkdtemp(prefix="spec-foreman-")`，不要猜跨平台 temp 路徑。

寫 `.owner.json`，包含 `run_id`、`repository_root`、`artifact_directory`，內容與 state 一致。目錄只放 spec 快照、briefs、短 results、failure handoffs、review、測試 logs 與本 run 自建 sessions。Git worktrees、產品測試、使用者資料放在此目錄之外。

原生 CLI 支援獨立 session directory 時可指向本 run 的 sessions 子目錄；否則只記原 session 指標，不複製大型 JSONL，也不宣稱外部 session 會被清理。OS 可能清 temp；告知使用者這不是長期備份。

## State 最小欄位

使用 [state.json](../templates/state.json)：

- Run：ID、repo、artifact path、baseline、integration branch／worktree、candidate／last verified SHA、status、`writers_stopped`（全部 writers／測試程序停下後才 true）。
- 共用配置：kind、provider/model、effort；只保存明確角色覆寫。
- 測試契約：已確認的邊界與來源、tdd 路徑、related／regression／full 的命令與 cwd。
- Tickets：ID、快照中的來源位置、depends_on、shared_resources、status、dispatch ID、integrated SHA。
- Dispatches：ID、ticket／role、brief／result path、pane／agent／session、branch／worktree、input／output SHA、requested／observed 配置與來源、writer stopped。串行接票的新 dispatch 加 `reuse_from_dispatch_id` 與本次成功的 `compaction_source` 指標（session／entry ID 或原生事件）；其餘 dispatch 省略。
- Review：原 review HEAD、report、findings、fix SHAs；不保留多輪 ledger。
- Human：驗收 HEAD、明確決策與回覆來源；created_resources 是 cleanup ownership 的依據。

只在狀態轉換更新；不把驗收條件、commands 或 logs 複製到每個欄位。Result 中已有細節就留路徑。`last_verified_head_sha` 與 candidate 不同時，不宣稱目前版本驗證通過。

串行 dispatch 可指向同一組 worker 資源；前票紀錄與獨立 result 保留，不隨 branch 前進改寫舊 output。`created_resources` 對實際建立的 pane／session／worktree／branch 只登記一次。前票 `writer_stopped` 表示該任務已停寫，不代表復用 worker 永遠停止；run 的 `writers_stopped` 必須核對目前所有 live workers／測試程序。

## 恢復

未清理時先查 state，再對照 live agents、results、Git refs／dirty status；保留已送任務，不重派。串行 worker 的目前 HEAD 對照最新 dispatch，不拿已整合前票 output 誤判；接票中斷時查 input／成功 compact 指標及新 brief 是否已送，不重做已完成操作。缺檔／不一致時查最少必要來源，無法恢復則求援，不從 idle 猜成功。

## 清理

只在使用者明確接受精確 HEAD，且 run 已 completed、所有本 run workers／測試程序停止寫入後清理；blocked、awaiting-human-validation、拒絕或沒有回覆都保留。

1. 先向使用者輸出接受的 branch／HEAD、測試與 review／修正摘要，作為不依賴 temp 的完成回覆；將明確決策寫入 state。
2. 檢查目標是本 run 建立的系統 temp 直屬 `spec-foreman-*` 目錄，marker／state 的 run、repo 與絕對路徑一致；accepted HEAD 等於當前 integration HEAD。
3. 確認該目錄無 worktree／repo、使用者資料、symlink／junction 或外部指向。使用 [cleanup.py](../scripts/cleanup.py)：`python <skill-dir>/scripts/cleanup.py <exact-run-dir>` 先 dry-run，通過後同命令加 `--delete`；只刪這個目錄，不用 wildcard 刪其他 runs。
4. 刪除失敗如實回報路徑，不改動產品、不反覆嘗試破壞性清理。Git branches／worktrees、產品測試及本 run 以外的 sessions 永遠不在此清理範圍；刪那些需另問。

本機舊 runs（例如原 `.git/spec-foreman/`）不遷移或自動清除。這是新 run 的工作規則。
