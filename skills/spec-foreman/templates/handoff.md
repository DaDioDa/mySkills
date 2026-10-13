# 短 task brief（Main 派工）

- Dispatch／ticket 或 finding IDs／role:
- Role file／spec snapshot 中的 ticket 位置／repo 指引:
- Worktree／branch／input SHA；串行復用時前票已整合、新任務取代舊任務:
- Integration branch（worker 回交前讀最新 SHA）:
- 目標、驗收條件位置、允许修改範圍／共享契約:
- 共用測試契約／tdd skill 絕對路徑:
- 本票 related／必要 regression 選取（只列共用契約的差異）:
- Result 絕對路徑／暫存 log 目錄:

共用資料用指標，不重複整份 spec、配置、狀態或稽核欄位。配置由 Main 在送任務前核對，worker 不改模型。

成功發布短 result 並停止寫入。失敗／衝突／缺資料才使用 result template 的詳細 failure handoff。Worker 自行同步任務分支，不直接更新 integration branch。
