import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cleanup.py"
spec = importlib.util.spec_from_file_location("cleanup", SCRIPT)
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


class CleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix="foreman-test-repo-")
        cls.repo = Path(cls.fixture.name).resolve()
        cls.git("init", "--quiet")
        cls.git("symbolic-ref", "HEAD", "refs/heads/integration")
        (cls.repo / "product.txt").write_text("preserve me", encoding="utf-8")
        cls.git("add", "product.txt")
        cls.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "--quiet", "-m", "baseline")
        cls.sha = cls.git("rev-parse", "HEAD").strip()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.check_output(["git", "-C", str(cls.repo), *args], text=True)

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="spec-foreman-")).resolve()
        self.marker = {"run_id": "test-run", "repository_root": str(self.repo),
                       "artifact_directory": str(self.root)}
        self.state = {**self.marker, "status": "completed", "writers_stopped": True,
                      "integration_branch": "integration",
                      "integration_worktree": str(self.repo),
                      "integration_head_sha": self.sha,
                      "last_verified_head_sha": self.sha,
                      "human_validation": {"decision": "accepted", "head_sha": self.sha,
                                           "accepted_head_sha": self.sha,
                                           "response_reference": "explicit test acceptance"}}
        self.save()
        (self.root / "run.log").write_text("temporary evidence", encoding="utf-8")

    def tearDown(self):
        if self.root.exists():
            shutil.rmtree(self.root)

    def save(self):
        (self.root / ".owner.json").write_text(json.dumps(self.marker), encoding="utf-8")
        (self.root / "state.json").write_text(json.dumps(self.state), encoding="utf-8")

    def test_dry_run_preserves_artifacts(self):
        result = cleanup.cleanup_run(self.root)
        self.assertFalse(result["deleted"])
        self.assertTrue((self.root / "run.log").exists())

    def test_delete_owned_completed_run_only(self):
        result = cleanup.cleanup_run(self.root, delete=True)
        self.assertTrue(result["deleted"])
        self.assertFalse(self.root.exists())
        self.assertEqual((self.repo / "product.txt").read_text(), "preserve me")

    def test_pending_rejected_rejected_and_missing_acceptance(self):
        for status, decision in [("awaiting-human-validation", None), ("blocked", None),
                                 ("completed", "rejected"), ("completed", None)]:
            with self.subTest(status=status, decision=decision):
                self.state["status"] = status
                self.state["human_validation"]["decision"] = decision
                self.save()
                with self.assertRaises(ValueError):
                    cleanup.cleanup_run(self.root, delete=True)
                self.assertTrue(self.root.exists())

    def test_writers_not_stopped(self):
        self.state["writers_stopped"] = False
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_marker_mismatch(self):
        self.marker["run_id"] = "another-run"
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_missing_marker(self):
        (self.root / ".owner.json").unlink()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_accepted_head_mismatch(self):
        self.state["human_validation"]["accepted_head_sha"] = "0" * 40
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_no_verified_final_head(self):
        self.state["last_verified_head_sha"] = "0" * 40
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_missing_response_reference(self):
        self.state["human_validation"]["response_reference"] = None
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_nested_git_tree_rejected(self):
        (self.root / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_external_directory_rejected(self):
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.repo, delete=True)
        self.assertTrue((self.repo / "product.txt").exists())

    def test_nested_artifact_directory_rejected(self):
        nested = self.root / "spec-foreman-nested"
        nested.mkdir()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(nested, delete=True)

    def test_reparse_point_detection(self):
        self.assertTrue(cleanup.is_link_like_attributes(0x400))
        self.assertFalse(cleanup.is_link_like_attributes(0x20))

    def test_symlink_rejected(self):
        link = self.root / "outside"
        try:
            link.symlink_to(self.repo, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation unavailable on this platform")
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)

    def test_windows_junction_rejected(self):
        if os.name != "nt":
            self.skipTest("Windows junction test")
        link = self.root / "outside-junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(self.repo)],
                                capture_output=True)
        if result.returncode:
            self.skipTest("Junction creation unavailable")
        try:
            self.assertTrue(cleanup.is_link_like(link))
            with self.assertRaises(ValueError):
                cleanup.cleanup_run(self.root, delete=True)
            self.assertTrue((self.repo / "product.txt").exists())
        finally:
            link.rmdir()

    def test_other_run_preserved(self):
        sibling = Path(tempfile.mkdtemp(prefix="spec-foreman-"))
        try:
            sentinel = sibling / "preserve.txt"
            sentinel.write_text("another run", encoding="utf-8")
            cleanup.cleanup_run(self.root, delete=True)
            self.assertEqual(sentinel.read_text(), "another run")
        finally:
            shutil.rmtree(sibling)

    def test_dirty_integration_worktree_rejected(self):
        product = self.repo / "product.txt"
        try:
            product.write_text("uncommitted user change", encoding="utf-8")
            with self.assertRaises(ValueError):
                cleanup.cleanup_run(self.root, delete=True)
            self.assertTrue(self.root.exists())
        finally:
            product.write_text("preserve me", encoding="utf-8")

    def test_accepted_version_not_at_branch(self):
        self.state["integration_head_sha"] = "0" * 40
        self.state["last_verified_head_sha"] = "0" * 40
        self.state["human_validation"].update(head_sha="0" * 40, accepted_head_sha="0" * 40)
        self.save()
        with self.assertRaises(ValueError):
            cleanup.cleanup_run(self.root, delete=True)


if __name__ == "__main__":
    unittest.main()
