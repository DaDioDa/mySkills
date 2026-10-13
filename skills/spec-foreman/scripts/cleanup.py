"""Clean an accepted run's owned OS-temp artifacts; never Git worktrees or refs."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


REPARSE_POINT = 0x400


def is_link_like_attributes(attributes):
    return bool(attributes & REPARSE_POINT)


def is_link_like(path):
    return path.is_symlink() or is_link_like_attributes(
        getattr(path.lstat(), "st_file_attributes", 0)
    )


def read_record(path):
    try:
        record = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Cannot read ownership/acceptance record: {path.name}") from exc
    if not isinstance(record, dict):
        raise ValueError(f"Invalid record: {path.name}")
    return record


def git(repository, *args):
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *args], check=True,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("Cannot verify repository/version; artifacts retained") from exc
    return result.stdout.strip()


def cleanup_run(directory, *, delete=False):
    requested = Path(directory).absolute()
    if not requested.is_dir() or is_link_like(requested):
        raise ValueError("Run directory missing or is a link/reparse point")
    root = requested.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if root.parent != temp_root or not root.name.startswith("spec-foreman-"):
        raise ValueError("Target must be a dedicated spec-foreman-* OS-temp directory")

    # Check before reading records, so linked records/directories cannot authorize deletion.
    def unreadable(error):
        raise ValueError("Cannot inspect all artifacts; retained") from error

    for parent, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
        for name in dirs + files:
            path = Path(parent) / name
            if name.lower() == ".git" or is_link_like(path):
                raise ValueError("Git tree or link/reparse point found; artifacts retained")

    marker = read_record(root / ".owner.json")
    state = read_record(root / "state.json")
    for key in ("run_id", "repository_root", "artifact_directory"):
        if not isinstance(marker.get(key), str) or not marker[key] or marker[key] != state.get(key):
            raise ValueError(f"Ownership mismatch: {key}")
    if Path(marker["artifact_directory"]).resolve() != root:
        raise ValueError("Ownership path does not match target")

    human = state.get("human_validation")
    if not isinstance(human, dict):
        raise ValueError("Human acceptance missing")
    accepted = human.get("accepted_head_sha")
    if (state.get("status") != "completed" or state.get("writers_stopped") is not True
            or human.get("decision") != "accepted" or not human.get("response_reference")):
        raise ValueError("Explicit acceptance/completion/stopped writers required")
    if not isinstance(accepted, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", accepted):
        raise ValueError("Accepted HEAD must be a full Git SHA")
    if any(sha != accepted for sha in (human.get("head_sha"), state.get("integration_head_sha"),
                                       state.get("last_verified_head_sha"))):
        raise ValueError("Accepted/current/verified versions differ")

    repo = Path(marker["repository_root"]).resolve()
    worktree_value = state.get("integration_worktree")
    branch = state.get("integration_branch")
    if not isinstance(worktree_value, str) or not isinstance(branch, str) or not branch:
        raise ValueError("Integration worktree/branch missing")
    worktree = Path(worktree_value).resolve()
    if root == repo or root in repo.parents or root == worktree or root in worktree.parents:
        raise ValueError("Repository/worktree must be outside artifact directory")
    if git(repo, "rev-parse", "--verify", f"refs/heads/{branch}") != accepted:
        raise ValueError("Integration branch has changed since acceptance")
    if git(worktree, "rev-parse", "HEAD") != accepted or git(worktree, "status", "--porcelain"):
        raise ValueError("Integration worktree differs or has uncommitted changes")
    if git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir") != git(
            worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"):
        raise ValueError("Integration worktree belongs to another repository")

    result = {"artifact_directory": str(root), "accepted_head_sha": accepted, "deleted": False}
    if delete:
        # Caller must stop all writers before this check; this is not a concurrent-write sandbox.
        shutil.rmtree(root)
        result["deleted"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="Exact owned run directory; no wildcards")
    parser.add_argument("--delete", action="store_true", help="Delete after validation; default is dry-run")
    args = parser.parse_args()
    try:
        print(json.dumps(cleanup_run(args.directory, delete=args.delete), ensure_ascii=True))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Cleanup refused/failed: {exc}\n")


if __name__ == "__main__":
    main()
