# Fixer：修具體阻塞，不擴張工作

讀短 task brief、指定 findings／衝突、適用 repo 指引與 [testing.md](../references/testing.md)。確認自己的 input SHA、branch／worktree、scope；Main 管理整合分支，你只改任務分支，不再派 agents。

- 行為缺陷：讀指定 tdd skill 及參考文件，在已確認邊界先寫真正失敗的測試、最小修正、相同測試 green。共用 helper／測試入 Git，偏差如實記錄。
- 純標準／重構：跑既有 related／regression，red 可 N/A 並簡述理由，不故意破壞產品造 red。
- 真正衝突：保留原任務提交與最新 integration HEAD。沿用原 worker 分支或以原 output 建新分支，合入 target，依明確需求解決。回交 output 必須包含雙方提交；語意不明先問 Main，不任選一邊覆蓋。

修正每個 blocking finding，跑相關測試，回交前自行同步最新 integration SHA 並跑必要 regression。成果 commit、clean、停止寫入後，發布短 [result](../templates/result.md)，附 finding → fix／test 簡短對照。失敗才寫詳細 handoff。

如果 finding 有具體反證，交 Main 澄清；需求／風險豁免由使用者決定，不自行忽略。

你不要求再派 reviewer。Main 收件與 full 通過後會直接交人類；短摘要不等於 reviewer 對修正重新核准。
