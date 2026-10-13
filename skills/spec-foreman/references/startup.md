# 一次準備，然後開工

1. 確認 `HERDR_ENV=1` 與實際 shell。未在 Herdr managed pane 就停止；不從外部操控使用者 session。
2. 查 repository、branch／HEAD 與 dirty status。非 Git 或有使用者未提交內容，先問處置；可用 clean baseline 開工時，不做額外初始化或提交。固定完整 `baseline_sha`，建立本機整合分支與獨立整合 worktree，保留使用者原工作目錄。
3. 讀指定 spec／tickets；找不到或候選不明才問。不自行拆票或吸收新增需求。保存一份需求快照，記錄來源／hash；tickets 用快照中的位置指標，不複製成多份文件。
4. 檢查 ticket IDs、依賴無 cycle／未知前置，標記共享檔案／介面風險。只用本機 integrated 狀態計算 ready set，預設並行上限 2；有空位立即補派，不等無關票。
5. 依 [testing.md](testing.md) 確認精簡測試契約；沿用 spec 已批准的邊界。缺少時集中提出並確認一次。沒有測試基礎設施就由第一張必要 ticket 建立，作為其他相關票前置，Main 不自行寫產品測試。
6. 找到可讀的 tdd skill 絕對路徑，workers 需讀其參考文件。從專案設定找到測試／build／lint／typecheck 命令，跑適用的 baseline 檢查。已知失敗明確記錄並取得處置，不假装成功；新專案沒有套件則標記待建立。
7. 使用者指定的 kind／精確 provider/model 適用所有 workers；effort 未指定時 low。角色覆寫才另外記錄，不要求填六角色矩陣。模型缺失、不支援 effort 或指定版本不可用才問，不默默替換。依 [transport.md](transport.md) 確認啟動與 runtime 核對方法，CLI discovery 每 run 做一次，版本／能力變動才重查。
8. 依 [state.md](state.md) 建立唯一系統暫存 run 目錄與精簡 state，告知使用者絕對路徑。需要 explorer 時才派，沿用共用配置；不要為例行檔案查找新增 session。

完成條件：需求／依賴、已確認測試契約、baseline、環境及 worker 配置可用；否則回報具體阻塞，不派產品實作。
