---
name: commit
description: Stage and commit the working tree as atomic commits, with a Conventional Commits message written in 中文. Trigger proactively whenever the working tree is dirty and a unit of work has just finished — no need to wait for the user to ask; an explicit commit / 提交 / 存檔 request also fires it.
---

# Commit

把這次協作的成果整理成 **atomic** commit：一個 commit 只承載一個意圖，訊息說清楚 **why**，而不是複述 diff 的 what。

使用者沒開口也可以起這個 skill：看到一個工作段落收尾、`git status` 是髒的，就主動走這套流程。第 4 步一定停下來等使用者確認提案，所以主動觸發永遠不會擅自 commit。

依序執行下面五步。

## 1. 讀現況

```bash
git status --short
git diff            # unstaged
git diff --cached   # staged
git log --oneline -10
```

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

1. 要 `git add` 的檔案清單，逐條列出實際路徑
2. 刻意不 add 的檔案，以及理由
3. commit message 草稿全文

diff 含**多個不相關的意圖**時，改成提案多個 atomic commit，逐一列出各自的檔案與訊息，讓使用者決定要不要拆。

第 2、3 步標記出的待確認項與 red flag，在這裡一併提問。使用者回覆前不要動 git。

## 5. Commit

```bash
git add <逐一列出的路徑>
git commit -F <訊息檔>
```

訊息寫到 scratchpad 目錄再用 `-F` 傳入。中文加多行用 `-m` 串，在 PowerShell 與 bash 的引號規則不同，`-F` 兩邊都穩。

`git add` 的路徑要跟第 4 步提案的清單逐字一致，用 `git add -A` 或 `git commit -am` 會把沒提案過的檔案一起帶進去。

pre-commit hook 失敗，把原始輸出貼給使用者並停下來修，不要用 `--no-verify` 繞過。

commit 完跑 `git log -1 --stat` 回報結果。使用者明講之前不要 push。

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
