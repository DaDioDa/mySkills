# 一次完整 review 報告

- Dispatch／axis: Both | Spec | Standards
- Baseline SHA／review HEAD／spec snapshot:
- Status: complete | incomplete | blocked
- 已審範圍：完整 diff、相關檔案、需求／標準來源摘要:
- 未審必要範圍／限制:

## 驗收條件對照

每張票的每條驗收條件一行：`票 ID／條目：符合 | 不符合（→ finding ID）| 無法判斷（原因）— 證據（file:line 或 test 名稱）`。不符合的一定要有對應 blocking finding。Spec 使用者故事不逐條列，違反時寫進 findings。

## Blocking findings

有證據違反驗收條件、spec、ADR 或硬性規則就列這裡，不因機率低或影響小降級。每個根因一項：ID、需求／標準引用、file／symbol、具體證據／重現、發生機率與影響、建議修正範圍。沒有則寫無；未審完不能聲稱零問題。

## Advisory 與 human checks

只列沒有規則或缺陷證據的主觀建議、人工操作／預期結果及未涵蓋風險，不要求自動修全部主觀重構。

本報告只針對上述 review HEAD；後續修正通過測試後交人類，不自動再次 code review。
