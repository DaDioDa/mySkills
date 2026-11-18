# 一次完整 review 報告

- Dispatch／axis: Both | Spec | Standards
- Baseline SHA／review HEAD／spec snapshot:
- Status: complete | incomplete | blocked
- 已審範圍：完整 diff、需求／標準來源摘要:
- 未審範圍／限制:

## 驗收條件對照

每張票的每條驗收條件一行：`票 ID／條目：符合 | 不符合（→ finding ID）| 無法判斷（原因）— 證據（file:line 或 test 名稱）`。不符合的一定要有對應 finding。

## Standards

照 code-review skill 的 Standards 軸，每項附 ID、位置與引用。兩軸分開列，不合併、不重排。

- Hard violations：違反 repo 文件規則，引用檔案與規則。沒有則寫無。
- Judgement calls：smell baseline 與其他判斷。沒有則寫無。

## Spec

照 code-review skill 的 Spec 軸，每項附 ID、位置與 spec 原文引用。

- 缺漏或部分實作:
- 範圍外行為:
- 看似實作但做錯:

## Human checks

人工操作／預期結果及未涵蓋風險。

本報告只針對上述 review HEAD；後續修正通過測試後交人類，不自動再次 code review。
