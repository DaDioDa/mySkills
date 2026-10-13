# 行為演練情境（不是已跑過的 Herdr integration tests）

使用可丟棄 repo／模擬回覆演練；操作真實 Herdr 必須在 managed pane，且由使用者啟動。靜態／清理安全測試用 `python -m unittest discover -s tests -p "test_*.py" -v`，不等於已演練以下調度行為。

| 情境 | 預期行為 |
|---|---|
| 非 Herdr／非 Git／dirty 使用者內容 | 停止或問具體處置，不操控外部 session、不自動清理 |
| 缺測試契約 | 一次确认公開邊界、工具與三層命令；需要時第一張必要票建共用套件 |
| 模型未覆寫 effort | 所有 workers 使用同一指定精確模型與 low，不自動升級 reviewer |
| Runtime 配置不符／不可核實 | 任務前阻塞，不把 argv 當生效證據 |
| A、B 獨立，C 依賴 A | A 整合驗證後有空位立即派 C，不等 B；共享契約有風險則串行 |
| Worker 正常完成 | related、同步後 regression 通過；行為覆蓋自查後只發布短測試指標／限制，不造覆蓋表或逐切片證明 |
| 測試全綠，但 assertions 只證明部分需求 | worker 交件前發現缺漏／錯誤實作仍會過，補共用測試並實跑，不把名稱/count 當覆蓋 |
| 同產品／接縫的串行下一票 ready | 前票停寫且 Main 整合後，clean worker branch ff 到新 input；同 worker／cwd compact 成功後才送新 brief，每票 dispatch/result 獨立 |
| Compact 失敗／取消／舊 entry／idle | 保留 worker 與成果，回 Main 處理；不送下一票、不盲目重送或當成功 |
| 最後一票交件／並行工作／完整 review | 最後一票不 compact；並行各有獨立 worker；reviewer 使用全新 session |
| 復用資源與歷史結果 | created_resources 只登記一次；前票 output/result 保留，run 停寫狀態核對目前 live workers |
| Worker 起點過時但無衝突 | worker 自行同步，不開 resolver；Main ff 到同版本不重跑回歸 |
| A 先整合，B 的 target 過時 | 同 B session 再同步／必要 regression，再 ff，不覆蓋 A |
| 真正 merge conflict | 停寫、failure handoff 回 Main；Main 明確方向交 worker，語意不明問人類 |
| 證據矛盾／harness 失敗 | 查具體 log、修共用測試，不把錯誤當產品 red 或廣泛重造補證包 |
| TDD 粒度／先後偏差 | 如實披露，不補造歷史；一般流程偏差功能通過後記錄繼續，嚴格 gate／虛假聲明阻塞 |
| 只有 exit 0／關鍵 skipped | 不通過；核對必要測試真的有跑 |
| Timeout／done 無結果／provider 額度 | 核對 live／短結果／Git，不重送、不當成功 |
| 尚有未整合票 | 不提前 code review，不把未做票當 finding |
| 全票完成 | 精確 HEAD full，通過後一次完整 Spec + Standards review |
| Review 有 blocking findings | 修正、相關測試／回歸、最後 full，直接交人類；不第二次 code review |
| Advisory／需求爭議 | 主觀重構不自動修；真正需求／風險決策交人類 |
| 無法完整 review／修復無進展 | 保留成果與具體阻塞，不無限開 reviewers／fixers |
| 修正後 HEAD 改變 | 驗收包區分 review 原 HEAD 與 final HEAD，不聲稱修正版已 review |
| 無修正、相同 final HEAD | 沿用該 HEAD full，不多跑一次 |
| 人類未回覆／拒絕 | 保留暫存，不 completed；拒絕先確認修復範圍，不自動重啟 review |
| 人類接受精確 HEAD | 停止本 run writers；短完成回覆後，只刪 marker／state 匹配的 temp run |
| 清理目標是其他 run／repo／symlink／junction | 拒絕刪除；保留產品測試、Git worktrees／branches、外部 sessions |
| Main compact／恢復 | 短 state＋result＋Git／live 核對，保留已送任務，不重派；串行接票查最新 dispatch／compact 指標與新 brief 是否已送，不重做已完成操作 |

成功的判斷是正確版本與必要測試／人類決策，而不是文件數量、assertions 總數或終端 idle。
