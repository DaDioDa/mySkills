---
name: commit
description: 將 working tree 整理成 atomic commits，並以中文撰寫 Conventional Commits 訊息。
disable-model-invocation: true
---

# Commit

把這次協作的成果整理成 **atomic** commit：一個 commit 只承載一個意圖，訊息說清楚 **why**，而不是複述 diff 的 what。

只有使用者直接呼叫此 skill 時才執行。由主代理直接完成下面五步，不委派給 committer 或其他子代理。

## 1. 讀現況

```bash
git status --short
git status          # 確認沒有 rebase / merge 進行中
git diff            # unstaged
git diff --cached   # staged
git log --oneline -10
```

`git diff` 不含未追蹤檔案；另列出並讀取準備納入的未追蹤檔案。

完成條件：working tree 裡**每一個**變更檔案，你都能說出它屬於哪個意圖。說不出來的檔案，就是第 4 步要問的對象。

不是 git repo，或 `git status` 顯示 rebase / merge 進行中，停下來告訴使用者，不要自己 `git init` 或硬 commit。

## 2. 對照脈絡

拿本次對話做過的事去對 diff：

- 對話中做過、diff 裡也有 → 這是 commit 的主體，訊息以此為準。
- diff 裡有、對話中從沒提過 → 標記為**待確認**。可能是使用者手動改的、其他分支殘留的、或工具自動產生的。
- 對話中說要做、diff 裡卻沒有 → 工作可能沒真的落地，提醒使用者。

這次會話沒有相關脈絡（例如剛開新 session）時，改從 diff 本身與 `git log` 的既有風格推斷意圖，並在第 4 步明說「訊息是純從 diff 推來的」。

## 3. Red flag 稽核

逐一掃過 diff，凡命中就在提案裡標出來：

- 金鑰、token、密碼、`.env`、憑證檔
- debug 殘留：`console.log`、`print()`、`debugger`、被註解掉的舊程式碼
- 與本次意圖無關的檔案：編輯器設定、`.DS_Store`、build 產物、暫存檔
- 大量純格式變動混在邏輯變動裡
- lockfile 變動但沒有對應的 manifest 變動

## 4. 提案並等待確認

把三件事一次列給使用者，然後**停下來**：

1. 要暫存的檔案清單，逐條列出實際路徑；同一檔案分屬多個 commit 時，列明各 commit 包含的區塊
2. 刻意不 add 的檔案，以及理由
3. commit message 草稿全文

diff 含**多個不相關的意圖**時，改成提案多個 atomic commit，逐一列出各自的檔案與訊息，讓使用者決定要不要拆。

第 2、3 步標記出的待確認項與 red flag，在這裡一併提問。使用者回覆前只做唯讀檢查，不修改 working tree、index 或提交紀錄。

## 5. Commit

確認後先檢查 working tree 與 index 是否仍符合核准提案；沒有變動就直接執行，不重做提案。若出現未核准變更或既有 staging 與拆分計畫衝突，停下來確認，不擅自清空或重排使用者的 staging。

### 暫存與提交

- 整檔屬於本次 commit：執行 `git add <逐一列出的路徑>`，路徑必須與核准清單逐字一致。禁止 `git add -A` 或 `git commit -am`。
- 同檔分屬多個 commit：不要整檔 add，也不要為了拆分去改 working tree。從目前 index 版本建立只含本次核准區塊的目標內容，以程式產生 unified diff（例如 Python `difflib.unified_diff`，使用 `a/路徑`、`b/路徑` 標頭），不要手寫 hunk 行數。依序執行：

  ```bash
  git apply --cached --check <patch檔>
  git apply --cached <patch檔>
  ```

  前一個命令成功才執行下一個；每次提交後，下一份 patch 都以更新後的 index 為基準。
- 每個 commit 前檢查 `git diff --cached`，確認僅含本次核准內容；不能只核對檔名。
- 訊息以 UTF-8 寫入暫存檔，再執行 `git commit -F <訊息檔>`，避免跨 shell 的中文與多行引號問題。

### 暫存檔與失敗處理

訊息檔與 patch 一律放在 repository 外的系統暫存目錄，為本次執行建立獨立子目錄（例如 Python `tempfile.TemporaryDirectory`）。成功或失敗都清理自己建立的暫存檔，不在專案根目錄留下 scratch 檔，也不刪除使用者的檔案。

patch 格式錯誤時，由主代理修正並重新執行 `--check`；不要因此重新派工或清空 index。若原因是內容已變動或核准範圍不明，停止並詢問使用者。

pre-commit hook 失敗，把原始輸出貼給使用者並停止提交，待修正後再試，不要用 `--no-verify` 繞過。

完成後跑 `git log -1 --stat` 與 `git status --short`，回報建立的 commit 與剩餘變更。使用者明講之前不要 push。

## 訊息格式

`type(scope): 中文標題`，空行，一段**摘要**。

- type 用 Conventional Commits：`feat` `fix` `refactor` `perf` `docs` `test` `chore` `build` `ci`
- scope 填模組或目錄名，判斷不出來就整個省略
- 標題一行講完這個 commit 的意圖，祈使語氣，句尾不加句號
- 內文寫成一段連貫散文，讀起來像論文摘要：先講原本的問題，再講這次的做法，最後講效果或取捨
- 內文控制在 **100 個中文字以內**。寫完數過再送出，超過就砍掉 diff 讀得出來的 what，只留 why
- breaking change 在摘要後另起 `BREAKING CHANGE:` 段落，不計入這 100 字

```
feat(auth): 加入 refresh token 輪替機制

原本的 refresh token 可無限重用，一旦外洩就等同長期憑證。改為輪替機制，session 記錄輪替次數，用過的 token 一律拒絕，把外洩後的可用視窗壓到單次，並補上 replay 攻擊的回歸測試。
```

commit trailer 沿用 harness 既有規則，這裡不另外指定。
