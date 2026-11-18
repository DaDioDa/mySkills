# Reviewer：一次完整、唯讀 review

讀 brief，核對 baseline／review HEAD、spec 快照與適用 repo 指引。產品樹唯讀，只寫本次 review 報告，不修程式、不派 Herdr workers。疑問寫進報告；不用提問選單或任何等人在本視窗回答的工具，Main 看不到。

## 照 code-review skill 審

讀 brief 給的 code-review skill（mattpocock-skills 的 `code-review`）絕對路徑，照它的流程做 Standards 與 Spec 兩軸 review，審查範圍與 finding 的判斷都以 skill 為準。下列幾點和 skill 不同時，以本檔為準：

- **Fixed point：** 用 brief 的 baseline SHA，不問人。`git rev-parse HEAD` 必須等於 brief 的 review HEAD，不相等就寫 blocked 並停止。
- **Spec 來源：** 用 brief 的 spec 快照與 ticket 位置。不查 issue tracker；`docs/agents/issue-tracker.md` 不存在時，也不要求使用者執行 setup。
- **Sub-agents：** 可以照 skill 開兩個 sub-agents 平行審兩軸，但只能用你所在 CLI 內建的 sub-agent，不透過 Herdr 開 pane。Sub-agents 同樣唯讀、不提問。CLI 沒有 sub-agent 功能時，在同一 session 依序審兩軸。
- **字數：** skill 給 sub-agent 的 400 字上限只限制 findings，驗收條件對照不受此限。
- **輸出：** 不用 skill 的回覆格式，改寫進 [review template](../templates/review.md)。兩軸的 findings 分開列，不合併、不重排。

## 報告

驗收條件對照逐張票、逐條寫符合／不符合與證據指標，不符合的一定有對應 finding。每條一行，不要求巨型證明矩陣。Finding 附 skill 要求的引用（標準條文或 spec 原文）與位置；未執行的命令標 proposed。

讀完 diff 才 complete；否則寫 incomplete／blocked 與剩餘範圍，不能以零 finding 表示 pass。分 blocking／advisory 由 Main 決定，你不用分。

這是本 run 唯一一次全面 code review。修正後由測試與人類驗收把關，你不自動要求下一輪或聚焦 review。報告記錄本次精確 HEAD，不能背書尚未讀過的後續修正。
