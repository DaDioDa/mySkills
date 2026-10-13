# spec-foreman：輕量工頭

以短 prompt 為骨架：派指定模型／effort 逐票 TDD，能並行就並行，核對實際配置；一次完整 review，修正並驗證後交人類。

從 `herdr_drone/` 在 Herdr managed pane 啟動：

```sh
pi --skill ./skills/spec-foreman
```

```text
/skill:spec-foreman spec=path/to/spec.md tickets=path/to/tickets/ model=<精確 provider/model> effort=low
```

這是給 Main 的指示，不是內建 argv parser。也可以自然語言提供路徑與模型。未指定 effort 預設 low，所有 workers 共用配置，明確覆寫才分角色；每次派遣核對實際生效模型／effort。Main 本身的模型不由此 skill 更改。

## 工作流

```text
一次確認需求／測試契約／配置
  → workers 依前置與共享修改風險並行 TDD（預設最多 2 位）
  → worker 自行同步最新整合版本、測試、行為覆蓋自查
  → 無衝突短摘要；衝突／失敗才詳細 handoff 求助 Main
  → Main 串行 fast-forward（同 HEAD 回歸不重跑）
  → 同產品／接縫串行下一票：沿用 worker／worktree／branch，compact 成功後接新 brief
  → 所有票完成、完整套件通過
  → 一次完整 Spec + Standards review（預設一位 reviewer）
  → 修阻塞問題、驗證修正、完整套件通過
  → human validation（不再自動 code review）
  → 人類接受精確 HEAD，清理本 run 暫存
```

**測試節奏：每票 related；同步／整合後必要 regression；所有票與 review 修正完成後 full。** 共用專案測試由 TDD 累積並保留在 Git，不每票重造 driver。Review 不代替測試，修正後也不宣稱經過第二次 review。

Worker 首次交件前自查驗收條件與真正 assertions，問「錯誤實作是否也會通過？」缺漏先補共用測試。成功只保留短測試指標與限制，不新增覆蓋表、逐切片證明／補證包；Main 遇到具體矛盾才讀必要細節。

串行接票保留 worker／session 與固定 cwd，但每票 dispatch／input／output／result 獨立；Main 整合前不開始後票。還有下一票時固定 compact 一次並確認成功，最後一票不做；compact 是摘要而非清空 context，也不保證更便宜。並行工作各自隔離，reviewer 仍是全新 session。

事件等待不忙碌輪詢，timeout 不重派，done 不當交件。下一次 run 分別觀察首次交件缺漏／補測往返，以及 worker 復用的耗時／usage，不用 assertions 數量代替品質。

## 暫存與限制

流程紀錄在系統 temp 的獨立 run 目錄，未驗收／失敗保留；接受後只刪本 run 暫存。產品、Git worktrees／branches、其他 runs／sessions 不刪。OS 清 temp 可能影响恢復，不把它當長期備份。

本機 commits／整合獲此流程授權；不 push、開 PR、合併主分支或清理使用者修改。這是文件型 skill，不是 sandbox／確定性 scheduler；唯讀、停止寫入與版本核對仍需實際執行。

`references/` 給 Main 按階段讀；workers 只讀當次 role、短 brief、需求與共用測試契約。舊 `herdrskill.md`、`implement-spec.md` 是設計來源，不是此版執行規則，不修改。

## 靜態與清理安全檢查

從本 skill 目錄執行：

```sh
python -m unittest discover -s tests -p "test_*.py" -v
```

[scenarios.md](tests/scenarios.md) 是需另行演練的行為情境，不宣稱靜態檢查等於真實 Herdr 驗證。
