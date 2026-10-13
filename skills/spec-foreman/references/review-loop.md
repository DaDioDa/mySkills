# 一次完整 review → 修正 → Human validation

## 完整 review 只做一次

所有票 integrated、full 通過、writers 停止後，固定 `review_head_sha`。派一個全新唯讀 reviewer，同時檢查 Spec 與 Standards；若使用者明確要求分軸 workers 才分開，仍算同一次完整 review。

範圍是 `baseline_sha → review_head_sha` 完整 diff、相關完整檔案、整份 spec／tickets 與適用 repo 指引；不能只看最後一票。角色使用 [reviewer](../roles/reviewer.md)，報告用 [review](../templates/review.md)。

必要範圍未讀就 incomplete，不把空 findings 當 pass；恢復同一 review 任務完成剩餘範圍，不另起反覆全面 review。Review 期間整合分支凍結；意外寫入立即停下查明，不能把舊報告當成新 HEAD 的 review。

## 只修阻塞問題

Main 合併同根因 findings，區分需求錯誤／功能缺陷／安全／硬性標準與主觀建議。前者是 blocking，後者留給人類，不擴張重構。

把有來源、具體位置或重現依據的 blocking findings 交 [fixer](../roles/fixer.md)。Main 可用現有 spec／測試澄清誤報；真正需求、風險豁免或權限分歧才問使用者，不為文字報告爭議另開仲裁 agent。

Fixer 用 TDD 修行為缺陷，純格式／命名／重構跑既有測試，不製造假 red。按 [execution](execution.md) 自行同步、Main fast-forward，按 [testing](testing.md) 跑相關測試與必要回歸。

## 修正後直接交人類

全部修正整合後，在最終 HEAD 跑 full。Main 核對每個 blocking finding 都有修正與相關驗證，或有使用者明確豁免；這是收件／測試核對，不是再做 code review。

**不自動派第二次完整 reviewer，也不派聚焦 code reviewer。** 同根因修復後仍失敗、修復互相撤銷或無進展就求援；未解阻塞不能包裝成待驗收成功。

驗收包分別列原始 review HEAD 與最終修正 HEAD，說明「原版本完成一次全面 review；後續修正通過測試，未再次 code review」。不宣稱最終 HEAD 已被 reviewer 再次核准。

成功 gate：完整 review 已完成、阻塞 findings 已修正驗證／明確豁免、最終 full 通過、無 active writer。進 `awaiting-human-validation`，用 [human-validation](../templates/human-validation.md) 請人類檢查最終版本。

人類拒絕：區分原範圍缺陷與新需求，確認處理範圍再修、測試、重新交人類；不自動重啟 review。需求重大變更或使用者要求第二次 review，需要新的明確授權，不默默擴張本 run。
