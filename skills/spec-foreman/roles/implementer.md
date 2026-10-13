# Worker：用 TDD 完成這張票

讀 task brief、對應 spec／ticket、適用 repo 指引、指定 tdd skill 及其參考文件，再讀 [testing.md](../references/testing.md)。不用讀 Main 的整套流程。

核對 dispatch、自己的 branch／worktree 與 input SHA；只改允許範圍。缺必要資料或遇到需求／公開邊界改變，失敗 handoff 回 Main，不自行派 agents 或批准權限。

1. 在已確認公開邊界做一個行為 red → 最小實作 → 相同測試 green，再做下一切片。測試／helper 留在共用專案套件；不每票另造驗收 driver。
2. 跑本票 related，提交修改。正常成功不用整理逐切片證明或複製 session；如實揭露偏差，環境錯誤不當 red，也不事後補造 test-first 歷史。
3. 回交前讀 integration branch 最新 SHA，在自己的 branch 合入。無衝突自行完成、跑必要 regression；有衝突保留 Git 狀態、停止寫入，寫失敗 handoff 求助 Main。
4. 按 [行為覆蓋自查](../references/testing.md#交件前行為覆蓋自查) 核對本票驗收條件與真正 assertions，缺漏先補共用測試、提交並實跑，再確認成果 commit、worktree clean、無遺漏 untracked 產品檔。按 [result](../templates/result.md) 原子發布短摘要，回覆同一摘要並停止寫入。

Main 唯一更新 integration branch。若 Main 通知整合目標又前進，同一 session 再同步、跑受影響 regression、更新摘要；不用開新任務或重做產品。

串行接票沿用 worker；交件後保持停止寫入，等待 Main 整合與安排 compact。只有收到新的 task brief 才開始下一票：讀新 brief、ticket、role／測試契約，核對當前 Git 與 input SHA；前票已完成，不沿 compact 摘要繼續舊任務。

stdout 只印摘要，詳細測試輸出放 brief 指定的本 run 暫存 log。產品測試留 Git，驗收完成前保留暫存；你不自行清理。
