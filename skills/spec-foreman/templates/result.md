# 成功：短摘要

以下欄位即可，不填完整稽核表。UTF-8 寫 temp file 後 rename 為指定 result；終端回覆同一短摘要。

- Dispatch／ticket 或 finding IDs: ...
- Output commit／branch: ...
- Synced integration target SHA: ...（唯讀角色 N/A）
- 完成內容／finding → fix、test 對照: ...（implementer 附行為覆蓋自查後可定位的 test 名稱／UI check ID 或路徑；缺口放限制欄，不另造覆蓋表）
- Related／regression：命令、tested SHA、exit、實際 passed／failed／skipped 摘要、log 路徑: ...
- Clean／stopped writing: yes
- 已知限制／TDD 偏差: 無或一句話

不要求逐切片表格、session 複本、截图或額外成功 handoff。唯讀 explorer 填來源與事實，Git／TDD 欄 N/A。

# 失敗：詳細 failure handoff

只在無法完成或被阻塞時使用，同樣發布到指定 result path。

- Dispatch／ticket／status: blocked
- Worktree／branch／input／目前 HEAD；dirty 或 merge 狀態:
- 已完成部分與保留的修改／commits:
- 阻塞類型與具體原因（產品、測試工具、環境、衝突、需求、權限、provider）:
- 重現命令／cwd／exit／相關 log 路徑／必要錯誤片段:
- 已嘗試的最小處置與結果:
- 尚未通過的驗收條件／測試:
- 需要 Main 決定或提供什麼:
- Stopped writing: yes

真實產品 red、harness 故障與未跑分開寫；不要貼整份 stdout 或建議無理由重派。失敗之後等待 Main，不自行覆蓋成果／清理證據。
