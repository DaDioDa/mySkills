"""Static consistency checks; these do not exercise a real Herdr scheduler."""

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentTests(unittest.TestCase):
    def test_relative_links_resolve(self):
        for document in ROOT.rglob("*.md"):
            text = document.read_text(encoding="utf-8-sig")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target.split("#")[0]).is_file())

    def test_manual_invocation_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: spec-foreman\n"))
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("description:", text)

    def test_new_state_defaults(self):
        state = json.loads((ROOT / "templates/state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], 2)
        self.assertEqual(state["worker_configuration"]["effort"], "low")
        self.assertEqual(state["limits"]["max_full_reviews"], 1)
        self.assertFalse(state["writers_stopped"])
        self.assertEqual(set(state["test_contract"]) & {"related", "regression", "full"},
                         {"related", "regression", "full"})

    def test_obsolete_policy_not_retained(self):
        for document in ROOT.rglob("*.md"):
            text = document.read_text(encoding="utf-8")
            for phrase in ("最多三輪全面 review", "每輪派遣兩個", "重新全面 review", "每個行為切片一列"):
                with self.subTest(document=document.name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_worker_sync_and_main_only_fast_forward(self):
        text = (ROOT / "references/execution.md").read_text(encoding="utf-8")
        self.assertIn("Worker 自行同步", text)
        self.assertIn("--ff-only", text)
        self.assertIn("同一 worker", text)
        self.assertIn("不新開無衝突 resolver", text)

    def test_pre_delivery_behavior_self_check(self):
        text = (ROOT / "references/testing.md").read_text(encoding="utf-8")
        for phrase in ("首次交件前", "錯誤實作是否也會通過", "assertion",
                       "先補強共用套件", "Main 不事前代設計全部測試",
                       "不新增覆蓋表", "必要測試缺失仍阻塞"):
            self.assertIn(phrase, text)
        implementer = (ROOT / "roles/implementer.md").read_text(encoding="utf-8")
        self.assertIn("行為覆蓋自查", implementer)
        result = (ROOT / "templates/result.md").read_text(encoding="utf-8")
        self.assertIn("可定位的 test 名稱／UI check ID", result)

    def test_serial_worker_reuse_keeps_ticket_boundaries(self):
        text = (ROOT / "references/execution.md").read_text(encoding="utf-8")
        for phrase in ("同一 worker、session、worktree／branch", "每張票用唯一 dispatch",
                       "經 Main 核對", "HEAD 等於前票 output", "新 input SHA",
                       "最後一票不 compact", "全新 reviewer", "不 reset／clean"):
            self.assertIn(phrase, text)
        state = (ROOT / "references/state.md").read_text(encoding="utf-8")
        for phrase in ("reuse_from_dispatch_id", "compaction_source", "只登記一次",
                       "不隨 branch 前進改寫舊 output", "目前所有 live workers"):
            self.assertIn(phrase, state)

    def test_compact_success_required_before_next_ticket(self):
        text = (ROOT / "references/transport.md").read_text(encoding="utf-8")
        for phrase in ('herdr agent prompt <pane-id-or-agent-name> "/compact"',
                       "不夾帶下一票任務", "真正的 slash command", "新增的成功 compaction entry",
                       "type=compaction", "才送下一票", "失敗／取消／結果不明",
                       "不在每票交件後關閉"):
            self.assertIn(phrase, text)
        for document in ROOT.rglob("*.md"):
            content = document.read_text(encoding="utf-8")
            for obsolete in ("跨票使用新 session", "跨票才換新 context",
                             "Start 全新 ticket session", "每張票用唯一 dispatch、獨立 worktree／branch"):
                with self.subTest(document=document.name, phrase=obsolete):
                    self.assertNotIn(obsolete, content)

    def test_no_automatic_post_fix_review(self):
        text = (ROOT / "references/review-loop.md").read_text(encoding="utf-8")
        self.assertIn("不自動派第二次完整 reviewer，也不派聚焦 code reviewer", text)
        self.assertIn("原始 review HEAD", text)
        self.assertIn("最終修正 HEAD", text)

    def test_testing_cadence_and_owned_temp_cleanup_documented(self):
        text = (ROOT / "references/testing.md").read_text(encoding="utf-8")
        for phrase in ("每票", "同步／整合後", "全部完成", "不再跑一遍", "測試與可重用 helper／driver 納入專案 Git"):
            self.assertIn(phrase, text)
        text = (ROOT / "references/state.md").read_text(encoding="utf-8")
        for phrase in (".owner.json", "系統 temp", "symlink／junction", "awaiting-human-validation", "不遷移或自動清除"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
