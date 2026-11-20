---
name: correct
description: "Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and add a reviewer rule last. Prove each check fails on a real past mistake. Use for /correct, optionally with the correction the user just made."
disable-model-invocation: true
---

# Correct

The user keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent can't make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Pick the mode

- **With an argument** (the correction the user just made): handle that one class. Check whether it happened before; if the rule is already in `CODING_STANDARDS.md` and nothing mechanical enforces it, it's a repeat, so fix it at a higher level.
- **Without an argument**: scan for every class.

## Find the mistake classes

Read the evidence: review reports in `docs/reviews/`, fix commits that cite a finding ID, recent commits, reverts, agent session logs for this repo, `CODING_STANDARDS.md`, agent instruction files, and comments that explain workarounds. Group the mistakes into classes. A class counts once it has happened twice.

## Pick a level for each class, highest that works

1. **Eliminate it with architecture.** One owner per piece of state, one supported way per task. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy. Call the Skill tool with `codebase-design` for the vocabulary. Read ADRs in the area first.
2. **Enforce it with types** so the bad state can't be written. If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior**, following the `tdd` skill. Fix or delete any test that still passes when the behavior breaks, or that fails when only the internals change.
4. **Add a reviewer rule** to `CODING_STANDARDS.md`, only for judgment calls no check can make. `/code-review` enforces it, but only at review time.

## Checkpoint

Present each class with its evidence, the chosen level, and why a higher level didn't work. Ask which to fix now. A level-1 change bigger than one commit goes to `/improve-codebase-architecture` or `/to-spec` instead of being done here. Flag any fix that contradicts an ADR.

## Fix and prove

Fix the chosen classes. Prove each new check fails on a real past mistake: reapply the old bad code, run the check, see it go red, then restore. Run the same command locally and in CI. Exceptions go on the offending line with a reason and the user's approval. Commit with the `commit` skill, one atomic commit per class.

## Keep the rule table

Keep a table in `CODING_STANDARDS.md` pairing each rule with what enforces it (`architecture`, `type`, `lint: <rule>`, `test: <file>`, `review`). Agent instruction files (`CLAUDE.md`/`AGENTS.md`) carry at most a one-line pointer to it. Drop a rule once its mistake can't happen. Call the Skill tool with `writing-for-agents` before editing the table.

**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work.
