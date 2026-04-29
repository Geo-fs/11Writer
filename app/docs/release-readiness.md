# Release Readiness

## Purpose

This checklist is for the current multi-agent local wave on `main`. It defines when the active mixed worktree is ready to be consolidated into scoped commits and pushed safely.

Use this together with:

- `app/docs/repo-workflow.md`
- `app/docs/active-agent-worktree.md`
- `app/docs/commit-groups.current.md`
- `app/docs/validation-matrix.md`

This is a release-readiness gate, not a commit authorization by itself.

## Quick dry run

Use the repo-local dry-run script before staging:

```bash
python scripts/release_dry_run.py
python scripts/release_dry_run.py --json
python scripts/release_dry_run.py --strict
```

What it checks:

- git branch and status counts
- ownership grouping summary
- high-collision changed files
- unknown changed-file count
- staged and untracked counts
- secret and junk filename/content red flags
- generated/build/cache file red flags
- validation guidance by changed ownership group
- known tooling caveats such as `windows-playwright-launch-permission`

What it does not do:

- it does not stage files
- it does not commit files
- it does not push
- it does not replace manual diff review

Interpretation:

- readable output is advisory
- `--strict` is useful as a release gate and is expected to fail while the current multi-agent worktree is still mixed

## Status categories

### Ready

Use `Ready` when all of these are true:

- worktree has been inventoried and grouped by task
- no secrets or junk are staged
- required validation for each intended commit group passed
- client lint and build are green for the consolidated frontend scope
- relevant backend focused tests are green
- shared high-collision files were reviewed manually
- push plan is scoped and uses selective staging only

### Blocked

Use `Blocked` when any of these are true:

- build is broken
- lint is broken
- relevant backend or domain tests are failing
- unresolved type errors remain
- worktree grouping is unclear
- shared-file hunks are still mixed and unreviewed
- secrets, local DBs, logs, caches, or build artifacts are staged or about to be staged

### Acceptable known issue

Use `Acceptable known issue` only when the issue is documented and not app-logic failure. Current examples:

- Windows Playwright browser launch failure classified as `windows-playwright-launch-permission`
- Vite chunk-size warning when build completes successfully
- domain smoke skipped due environment/tooling issue with a clear note in the commit or release report

## Worktree inventory

Checklist:

- run `git status --short --branch`
- review `git diff --stat`
- confirm the branch is still `main`
- confirm the worktree is grouped using `app/docs/commit-groups.current.md`
- confirm no one is attempting to commit mixed-agent changes in one pass
- optionally run `python scripts/release_dry_run.py`

## Secret and junk audit

Checklist:

- confirm no `.env` files are staged
- confirm no local SQLite databases are staged
- confirm no logs are staged
- confirm no caches are staged
- confirm no build artifacts are staged
- confirm no Playwright artifacts or local browser traces are staged
- confirm no private keys, tokens, or credential files are staged

Practical checks:

- `git status --short`
- review staged file list before every commit
- compare against `.gitignore` expectations

## Agent and task grouping review

Checklist:

- review `app/docs/commit-groups.current.md`
- confirm each planned commit maps to one commit group
- confirm dependencies between groups are respected
- confirm Gather registry work is isolated from Connect workflow docs
- confirm geospatial backend and frontend are split when shared files would otherwise complicate staging
- confirm smoke harness changes are either isolated or explicitly reviewed as shared

## Shared-file hunk review

These files require explicit manual review before any commit:

- `app/client/src/features/app-shell/AppShell.tsx`
- `app/client/src/features/layers/LayerPanel.tsx`
- `app/client/src/features/inspector/InspectorPanel.tsx`
- `app/client/src/lib/store.ts`
- `app/client/src/lib/queries.ts`
- `app/client/src/styles/global.css`
- `app/client/scripts/playwright_smoke.mjs`
- `app/server/tests/run_playwright_smoke.py`
- `app/server/tests/smoke_fixture_app.py`

Checklist:

- confirm diff hunks are reviewed manually
- confirm shared files are not auto-staged into a domain commit
- use `git add -p` when hunk-splitting is practical
- if ownership is unclear, hold the file for a later reconciliation commit

## Validation by group

Checklist:

- review `app/docs/validation-matrix.md`
- run only the validations that match the commit group being prepared
- record command results for each group
- if a group modifies shared shell or type files, include client lint/build after hunk staging

Minimum expectations:

- Connect/tooling:
  - syntax or docs diff review as applicable
- Gather/source registry:
  - JSON validation
- Geospatial backend:
  - focused backend tests plus compileall
- Geospatial frontend:
  - client lint and build, plus backend tests when API contracts changed
- Aerospace:
  - client lint and build
- Marine:
  - marine contracts plus client lint/build
- Features/Webcam:
  - reference/webcam tests plus client lint/build
- Shared smoke harness:
  - preflight syntax or diff review, then focused smoke only in a healthy environment

## Full local sanity check

Run this only when several groups are already reconciled and a broader push is being prepared.

Checklist:

- run the full local sanity block from `app/docs/validation-matrix.md`
- confirm client lint passes
- confirm client build passes
- confirm targeted backend suites pass
- confirm remaining known issues are documented

## Smoke harness status

Checklist:

- decide whether smoke is required for this release wave
- review `app/server/tests/run_playwright_smoke.py` and `app/server/tests/smoke_fixture_app.py` changes separately from domain code when practical
- decide whether focused smoke should run locally or on another machine
- do not classify `spawn EPERM` on this Windows machine as automatic app failure

Decision guidance:

- `Blocked` if smoke logic itself is broken by code changes
- `Acceptable known issue` if browser launch is blocked by `windows-playwright-launch-permission` and the rest of the validation scope is green

## Build and lint status

Checklist:

- run client lint for any group touching frontend code
- run client build for any group touching frontend code
- mark the wave `Blocked` if lint fails
- mark the wave `Blocked` if build fails
- treat Vite chunk-size warnings as acceptable only if build completes

## Documentation review

Checklist:

- confirm docs match the implemented behavior
- confirm new docs do not overclaim readiness or global coverage
- confirm task-specific docs are grouped with the right commit
- confirm workflow docs, commit grouping, validation matrix, and release readiness docs remain mutually consistent

## Commit sequencing

Checklist:

- use selective staging only
- do not use `git add .`
- confirm one logical task per commit
- confirm commit messages match the staged scope
- after each commit, re-run `git status --short`

Recommended sequence:

1. Connect docs and workflow
2. Gather source registry docs and JSON
3. Geospatial backend
4. Geospatial frontend
5. Aerospace
6. Marine
7. Features/Webcam
8. Shared smoke harness
9. Shared shell, panel, store, query, style, and type reconciliation

## Push readiness

Checklist:

- all intended commits exist locally
- remaining worktree state is understood
- no accidental staged files remain
- no secrets or junk are staged
- no force push is planned
- remote target is still `origin/main`
- final validation notes are ready to report

## Post-push verification

Checklist:

- run `git status --short --branch`
- confirm local branch is aligned with `origin/main`
- verify expected commit sequence is on the branch
- verify no extra accidental commit was created
- verify the remote branch reflects the intended commit messages
- record any deferred known issues

## Commit report template

Use this template for each eventual commit report:

```text
Commit group:
Files staged:
Validation run:
Known caveats:
Commit message:
Follow-up:
Push status:
```
