# 派工與串行 fast-forward

## Ready set

Ticket：`pending → running → returned → integrated`，必要時 `blocked`。所有前置已 integrated 且通過必要 regression、有空位、沒有共享修改風險才 ready。每次整合就重新計算；預設最多 2 個 active workers，review／fix 同樣計入。

每張票用唯一 dispatch 與短 [task brief](../templates/handoff.md)，提供需求位置、input SHA、允許範圍、測試契約與獨立 result／log 路徑。同一產品／公開接縫的串行票沿用同一 worker、session、worktree／branch；並行工作各用獨立 worker／worktree／branch。正常派工不寫完整稽核 handoff；本票同步／失敗修復沿用原 session。

## 串行 worker 接下一票

1. 前票已正式交件、停止寫入且經 Main 核對、fast-forward 整合，下一票 ready，才安排接票；worker 不自行連做後票。
2. Main 確認 live worker idle、無背景寫入／測試程序、worktree clean、HEAD 等於前票 output。將該 worker branch `--ff-only` 到最新 integration SHA 作為新 input SHA；無法快轉或狀態不符就保留現場求援，不 reset／clean。仍用原 cwd，不搬動活著的 agent。
3. 還有下一票時固定 compact 一次，依 [transport](transport.md#串行接票的-compact) 確認成功；最後一票不 compact。摘要保留公開介面、測試用法、已接受修正、限制與來源指標，已完成任務標為 done。compact 後核對 Git／配置與新 input 未變。
4. 建立新 dispatch，沿用實際 worker identity／資源，保留前票 dispatch 的 input／output／result；送新 brief，明確宣布前票已整合、新任務取代舊任務。Git、測試與新 brief 是依據，compact 摘要不是驗收或授權。

待命 worker 占用既有 worker 槽位；復用不增加 active worker，且同一 worker 同時只能有一個 dispatch。沒有下一張適合串行接續的票時，Main 可待命或回收它；改派並行工作／不同角色時使用獨立 worker，全新 reviewer 的規則不變。

## Worker 自行同步

1. 完成 related 測試並提交自己的修改，讀取整合分支最新完整 SHA。
2. 在自己的 branch 合入該 SHA；已包含則跳過。無衝突自行完成；有衝突保留 Git 狀態、停止寫入，以失敗 handoff 回 Main，不能挑一邊覆蓋。
3. 在同步後的精確候選 HEAD 跑 [testing.md](testing.md) 的必要 regression；提交、確認 clean，再發布短 result。回交 `synced_target_sha`、output SHA、測試摘要，停止寫入。

Main 不預先為舊起點另開 resolver。真正衝突時，Main 優先把明確處理方向交回原 worker；需要獨立 fixer 才建立新 dispatch。需求／語意不明才詢問使用者。

## Main 收件與整合

- 成功：核對短摘要的 dispatch、output commit、scope、clean worktree、停止寫入與必要測試結果。普通證據可用就採信，不逐票追查 runtime 歷史。
- 失敗：讀詳細 handoff，判斷測試／環境／衝突／需求／权限問題，採最小修復；同根因一次處置後仍無進展就求援，不無限補證。
- 整合分支只有 Main 寫，一次一個。檢查 current integration SHA 是 worker output 的祖先，`--ff-only` 到精確 output，記錄 integrated SHA，沿用該版本的 regression 結果。
- 如果其他票先整合導致 worker 未包含 current integration SHA，請**同一 worker**再同步、跑受影響 regression、更新短摘要；不是產品重做，也不新開無衝突 resolver。原等待回交成果仍保留。
- 不 force reset 整合分支。Main 只執行 Git／測試，不編寫產品或衝突解法；有衝突交 worker。
- 必要驗證失敗時停止基於失敗候選的新派工；已在跑的獨立票可交回。只有正確版本與驗證都成立才解除後續依賴。

所有票 integrated、無 active writer、整合 worktree clean 後，在精確 HEAD 跑 full。通過才進 review；此處只查票務／驗收覆蓋，不提前做全面 code review。
