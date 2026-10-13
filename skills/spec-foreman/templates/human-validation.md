# 請驗收這個版本

- Status: awaiting-human-validation
- Integration branch／exact final HEAD:
- 完成的 tickets／主要行為摘要:
- 如何取得／啟動這個版本（不改使用者原工作目錄）:

## 人類操作

用白話列關鍵操作、預期結果、錯誤／邊界情境與已知限制。不塞長內部狀態或要求人類理解 gate 術語。

## 自動化與 review

- Final full：tested HEAD、命令、實際結果摘要:
- 唯一完整 review 的原 HEAD／結果:
- 之後的 finding → fix commit／相關測試摘要:
- 未解阻塞（必須無，或有使用者明確豁免）／advisory:
- 若有修正：明說「修正已通過測試，未再次 code review」。
- 本 run 暫存目錄：...；接受後將刪除，只保留產品測試、commits／branches／worktrees。

## 請決定

- 接受這個精確 HEAD：completed，輸出完成摘要後清理本 run 暫存；不自動 push／PR／主分支合併。
- 拒絕：提供具體觀察，確認原範圍缺陷或新需求後修、測試、重新交人類；不自動重啟 review。
- 未回覆／暫不決定：維持等待，保留暫存。

若有未解除阻塞，改回報阻塞與下一步，不能要求把未完成成果當作驗收通過。
