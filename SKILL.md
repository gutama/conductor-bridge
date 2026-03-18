---
name: conductor-bridge
description: >
  Work with existing Gemini Conductor environments from Claude Code. Use this skill whenever
  you detect a `conductor/` directory in the project root, or the user mentions "conductor",
  "tracks", "plan.md", "spec.md", "implement the track", "conductor status", "conductor setup",
  "conductor review", "conductor revert", or any context-driven development workflow. This skill
  teaches Claude Code how to read Conductor's context files (product.md, tech-stack.md, workflow.md),
  understand track plans, implement tasks from plan.md, update task statuses, follow the project's
  defined workflow (e.g. TDD), create new tracks with specs and plans, review completed work,
  revert tracks/phases/tasks via git history, and make properly formatted git commits with git notes.
  Also trigger when the user says "continue implementing", "what's the next task", "check conductor
  status", "create a new track", "revert the track", "review the track", or references any
  conductor track by ID.
---

# Conductor Bridge for Claude Code

This skill enables Claude Code to work seamlessly with projects that use Google's
[Gemini Conductor](https://github.com/gemini-cli-extensions/conductor) — a context-driven
development framework (v0.4.1) that stores project knowledge, specs, and plans as versioned
Markdown files in a `conductor/` directory.

**Philosophy:** "Measure twice, code once." Conductor follows a strict protocol:
**Context -> Spec & Plan -> Implement**. It treats context as a managed artifact alongside
code, making the repository a single source of truth that drives every agent interaction.

## When to use this skill

- A `conductor/` directory exists in the project root
- The user wants to continue implementing a Conductor plan
- The user asks about project status, tracks, or plans
- The user wants to create a new track (feature/bug/refactor)
- The user wants to set up Conductor on a new or existing project
- The user wants to review completed work against guidelines
- The user wants to revert a track, phase, or task

## Quick Start Protocol

When you detect a `conductor/` directory or the user mentions Conductor:

1. **Load context** — Read conductor/index.md (or key files directly), then workflow + tech-stack
2. **Understand the plan** — Read conductor/tracks.md, find the active track and its plan.md
3. **Work through tasks** — Implement tasks following the project's workflow (TDD if specified)
4. **Update status** — Mark tasks complete in plan.md with commit hashes, attach git notes

## Universal File Resolution Protocol

Conductor uses an index-based file resolution system:

1. **Identify Index** — For project context: `conductor/index.md`. For a track: `conductor/tracks/<track_id>/index.md`
2. **Check Index** — Read the index and look for a link with a matching label
3. **Resolve Path** — Resolve links relative to the directory containing the index.md
4. **Fallback** — If the index is missing, use default paths (listed below)
5. **Verify** — Confirm the resolved file exists on disk

**Default Paths (Project):**
- Product Definition: `conductor/product.md`
- Product Guidelines: `conductor/product-guidelines.md`
- Tech Stack: `conductor/tech-stack.md`
- Workflow: `conductor/workflow.md`
- Tracks Registry: `conductor/tracks.md`
- Tracks Directory: `conductor/tracks/`
- Code Style Guides: `conductor/code_styleguides/`
- Setup State: `conductor/setup_state.json`

**Default Paths (Track):**
- Specification: `conductor/tracks/<track_id>/spec.md`
- Implementation Plan: `conductor/tracks/<track_id>/plan.md`
- Metadata: `conductor/tracks/<track_id>/metadata.json`

## Conductor Directory Structure

```
project-root/
├── conductor/
│   ├── index.md                  # Master index linking to all context files (read FIRST)
│   ├── product.md                # Product definition, users, goals, features
│   ├── product-guidelines.md     # Brand standards, prose style, visual identity
│   ├── tech-stack.md             # Language, frameworks, database, tooling
│   ├── workflow.md               # Team workflow rules (TDD, commits, coverage, etc.)
│   ├── setup_state.json          # Setup wizard progress tracking
│   ├── code_styleguides/         # Language-specific style guides
│   │   └── <language>.md         # e.g., typescript.md, python.md, go.md
│   ├── tracks.md                 # Registry of all tracks with status
│   └── tracks/                   # Individual feature/bug/refactor tracks
│       └── <track_id>/
│           ├── index.md          # Links to track files
│           ├── spec.md           # Feature specification
│           ├── plan.md           # Actionable task list with status markers
│           └── metadata.json     # Track metadata (id, status, timestamps)
├── GEMINI.md                     # Gemini CLI context file (may exist)
└── ... (rest of project)
```

---

## Core Workflows

### 1. Loading Project Context

Before doing ANY work, always load the project context:

```
1. Read conductor/index.md (or conductor/product.md if no index)
2. Read conductor/tech-stack.md — understand the stack and constraints
3. Read conductor/workflow.md — understand the team's workflow rules (TDD? coverage? commits?)
4. Read conductor/tracks.md — understand active tracks
5. If conductor/code_styleguides/ has relevant guides, read those too
```

This context shapes everything: coding style, testing approach, commit conventions, allowed technologies.

**CRITICAL:** The agent must NOT introduce technologies not documented in tech-stack.md without explicit user approval.

### 2. Checking Status (`conductor status`)

When the user asks "what's the status" or "conductor status":

1. Read `conductor/tracks.md` to list all tracks and their statuses
2. Find any in-progress track (marked `[~]` or `🔄 In Progress`)
   - Parse both `- [ ] **Track:` (current format) and `## [ ] Track:` (legacy format)
3. Read that track's `plan.md` to show current progress
4. Report: which phase is active, which tasks are done/pending/in-progress, what's next
5. Show aggregate metrics: total phases, tasks, completion percentage

### 3. Implementing Tasks (`conductor implement`)

Read `references/implementation-protocol.md` for the detailed step-by-step protocol.

#### Pre-Implementation: Load Context

Before writing any code:
1. Read `conductor/workflow.md` — the team's development process
2. Read `conductor/tech-stack.md` — allowed technologies and versions
3. Read `conductor/tracks.md` — find the active (in-progress) track
4. Read `conductor/tracks/<active_track>/plan.md` — the task list
5. Read `conductor/tracks/<active_track>/spec.md` — the feature specification
6. If relevant, read code style guides from `conductor/code_styleguides/`

#### Finding the Next Task

In the active track's `plan.md`:
1. Scan for the first task marked `[~]` (in-progress) — resume it
2. If no in-progress task, find the first task marked `[ ]` (pending)
3. Tasks within a phase must be completed in order
4. Phases must be completed in order
5. Never skip ahead to a later phase while an earlier one has pending tasks

#### Task Implementation Loop

For each task:

**Step 1: Mark In-Progress**
Update `plan.md` to mark the current task as `[~]`:
```
- [~] Task N: Create user authentication middleware
```
Save the file (don't commit yet).

**Step 2: Understand the Task**
Read the task description and sub-tasks. Cross-reference with spec.md, tech-stack.md, and existing code.

**Step 3: Follow the Workflow**
Check `conductor/workflow.md` for the implementation methodology.

**If TDD is specified:**
1. **Red phase** — Write a failing test first
   - Create test file if needed
   - Write tests that define expected behavior
   - Run tests and confirm they FAIL
   - Do NOT proceed until you have failing tests
2. **Green phase** — Write minimal code to pass
   - Implement just enough to pass the failing tests
   - Run tests and confirm all tests PASS
3. **Refactor phase** (optional)
   - Clean up implementation
   - Ensure tests still pass

**If no TDD:**
1. Implement the task following the project's conventions
2. Write tests if the workflow requires them
3. Run any defined test/lint commands

**Step 4: Verify Coverage**
Run coverage reports. Target: >80% coverage for new code (or whatever workflow.md specifies).

**Step 5: Document Deviations**
If implementation differs from tech stack:
- STOP implementation
- Update `tech-stack.md` with the new design
- Add dated note explaining the change
- Resume implementation

**Step 6: Commit the Work**
```bash
git add -A
git commit -m "conductor(<scope>): <description>"
COMMIT_HASH=$(git rev-parse --short HEAD)
```

Where `<scope>` is one of: `feat`, `fix`, `test`, `docs`, `refactor`, `style`, `chore`

**Step 7: Attach Git Note**
```bash
git notes add -m "Task: <task description>
Track: <track_id>
Phase: <phase number>
Changes:
- <file1>: <what changed>
- <file2>: <what changed>
Tests: <pass/fail/skipped>" $(git log -1 --format="%H")
```

**Step 8: Update Plan Status**
In `plan.md`, update the completed task with the first 7 chars of the commit hash:
```
- [x] Task N: Create user authentication middleware (abc1234)
```

**Step 9: Commit Plan Update**
```bash
git add conductor/tracks/<track_id>/plan.md
git commit -m "conductor(plan): Mark task '<task name>' as complete"
```

**Step 10: Check for Phase Completion**
If all tasks in the current phase are now `[x]`:

1. **Announce** — Tell the user the phase is complete
2. **Ensure test coverage** — Check that all code files changed in this phase have corresponding tests. Create missing tests.
3. **Run full test suite** — Execute the test command from workflow.md. Prefix with `CI=true` for non-interactive execution.
4. **Handle failures** — If tests fail, attempt to fix (max 2 attempts). If still failing, stop and ask user.
5. **Propose manual verification** — Generate step-by-step manual verification plan:
   - For frontend: start dev server, open browser, confirm visual elements
   - For backend: run curl commands, confirm responses
6. **Await user confirmation** — Do NOT proceed without explicit user approval
7. **Create checkpoint commit:**
   ```bash
   git commit -m "conductor(checkpoint): Checkpoint end of Phase <N>"
   ```
8. **Attach verification report as git note** to the checkpoint commit
9. **Update plan.md** — Append checkpoint hash to the phase heading: `[checkpoint: <sha>]`
10. **Commit plan update:**
    ```bash
    git commit -m "conductor(plan): Mark phase '<Phase Name>' as complete"
    ```

**Step 11: Continue or Stop**
- If the user asked to "implement all" or "continue", move to the next task
- If the user asked for just one task, stop and report
- If ambiguity or clarification is needed, stop and ask

#### Track Completion

When ALL phases in a plan are complete:

1. Update `conductor/tracks/<track_id>/metadata.json` — set status to `"complete"`
2. Update `conductor/tracks.md` — mark the track as `[x]` / `✅ Complete`
3. Commit: `chore(conductor): Mark track '<track_id>' as complete`
4. **Documentation Sync** — Analyze the spec and propose updates to:
   - `product.md` (if features significantly change product description)
   - `tech-stack.md` (if technology choices shifted)
   - `product-guidelines.md` (only for strategic rebranding — with strict warnings)
   All changes require explicit user confirmation before applying. Commit approved changes: `docs(conductor): Synchronize docs for track '<track_id>'`
5. **Track Cleanup** — Offer options: review, archive to `conductor/archive/`, delete, or skip
6. Inform the user the track is fully implemented

#### Handling Failures

- **Test failures:** Report clearly, attempt fix (max 2 attempts), then ask user
- **Missing context:** Check conductor/ files first, then ask user. Never guess.
- **Merge conflicts:** Prefer more recent/complete version, preserve status markers, report to user

### 4. Creating a New Track (`conductor newTrack`)

When the user wants a new feature, bug fix, or refactor:

**Step 1: Validate Setup**
Verify core files exist: product.md, tech-stack.md, workflow.md. If missing, direct user to run setup first.

**Step 2: Gather Track Description**
Accept from user argument or ask interactively. Infer type: feature, bugfix, or refactor.

**Step 3: Check for Duplicates**
Read tracks.md and check for existing tracks with similar names. Reject duplicates.

**Step 4: Build Specification Interactively**
Ask batched questions (up to 4 related questions per prompt) to build the spec. Use classification:
- **Additive** questions: for scope, features, requirements (multiple answers allowed)
- **Exclusive Choice** questions: for singular decisions (single answer)

Always offer "auto-generate" option to skip remaining questions. Do not repeat questions in chat; wait for user responses before proceeding.

**Step 5: Generate Track Artifacts**

Before writing any files, draft the spec and plan and present them to the user for approval. Only write files to disk after the user approves the drafts.

a. **Generate Track ID**: `<shortname>_YYYYMMDD` format (e.g., `darkmode_20260214`)

b. **Create directory**: `conductor/tracks/<track_id>/`

c. **Create spec.md:**
```markdown
# Specification: <Feature Name>

## Overview
<What this feature does and why>

## Requirements
### Functional Requirements
- FR1: <requirement>

### Non-Functional Requirements
- NFR1: <requirement>

## User Stories
- As a <user>, I want <action> so that <benefit>

## Acceptance Criteria
- [ ] Criteria 1

## Technical Approach
<How this will be implemented>

## Out of Scope
<What this does NOT include>
```

d. **Create plan.md:**
```markdown
# Implementation Plan: <Feature Name>

## Phase 1: <Phase Title>
- [ ] Task 1: <Description>
  - [ ] Sub-task 1.1: <Description>
  - [ ] Sub-task 1.2: <Description>
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: <Phase Title>
- [ ] Task 2: <Description>
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
```

**CRITICAL:** If workflow.md specifies TDD, each feature task must have "Write Tests" sub-task followed by "Implement Feature" sub-task.

**CRITICAL:** Each phase MUST end with a manual verification meta-task.

Guidelines for good plans:
- 2-5 phases per track
- 2-6 tasks per phase
- Tasks should be completable in a single focused session
- Include testing tasks explicitly if TDD

e. **Create metadata.json:**
```json
{
  "track_id": "<track_id>",
  "type": "feature",
  "status": "new",
  "created_at": "2026-02-14T10:30:00Z",
  "updated_at": "2026-02-14T10:30:00Z",
  "description": "<Brief description>"
}
```

f. **Create index.md:**
```markdown
# Track <track_id> Context

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
```

g. **Register in tracks.md:**
```markdown
- [ ] **Track: <Track Description>**
  *Link: [./tracks/<track_id>/](./tracks/<track_id>/)*
```

h. **Commit:**
```bash
git add conductor/
git commit -m "conductor(spec): Create track '<track_id>'"
```

**Step 6: Present for Approval**
Show the spec and plan to the user for review. Only proceed to implementation after they approve.

### 5. Setting Up Conductor (`conductor setup`)

Read `references/setup-protocol.md` for the full interactive setup procedure.

**Overview of setup steps:**

1. **Project Classification** — Detect brownfield (existing code) vs greenfield (new project)
   - Brownfield indicators: package.json, src/, .git with history, dependency files
   - For brownfield: analyze codebase (README, manifests, source structure) to pre-populate context
   - For brownfield: warn about uncommitted changes

2. **Product Definition** (`conductor/product.md`) — Interactive Q&A about project goals, users, features
3. **Product Guidelines** (`conductor/product-guidelines.md`) — Prose style, brand, visual identity
4. **Tech Stack** (`conductor/tech-stack.md`) — Languages, frameworks, databases, testing, CI/CD
   - For brownfield: auto-detect from package.json/requirements.txt/etc.
5. **Code Style Guides** (`conductor/code_styleguides/`) — Select appropriate guides for the stack
6. **Workflow** (`conductor/workflow.md`) — TDD, commit strategy, coverage targets, phase verification
   - Default: 80% coverage, commit after each task, git notes for summaries
7. **Create index.md** — Master index linking all files
8. **Initialize tracks.md** — Empty registry
9. **Initial Track Generation** — Interactively create the first track with spec and plan
10. **Finalize** — Commit everything: `conductor(setup): Add conductor setup files`

Setup progress is tracked in `conductor/setup_state.json`:
```json
{"last_successful_step": "<step_id>"}
```

Step values: `""`, `"2.1_product_guide"`, `"2.2_product_guidelines"`, `"2.3_tech_stack"`, `"2.4_code_styleguides"`, `"2.5_workflow"`, `"3.3_initial_track_generated"`

If setup was interrupted, resume from the last successful step.

### 6. Reviewing Work (`conductor review`)

When the user wants to review completed work:

1. **Validate setup** — Ensure core files exist (tracks.md, product.md, tech-stack.md, workflow.md, product-guidelines.md)
2. **Identify scope** — Find the target track (from user input or auto-detect in-progress track)
3. **Analyze changes** — Retrieve diffs (complete for <300 lines, chunked for larger changes)
4. **Verify against plan** — Check that implementations match plan.md tasks
5. **Check style adherence** — Validate against code_styleguides/ and product-guidelines.md
6. **Security review** — Check for common vulnerabilities
7. **Test coverage** — Execute test suite and verify coverage targets
8. **Generate report** — Categorize findings by severity: Critical / High / Medium / Low
   - Include file locations, context, and suggested fixes in diff format
9. **Post-review actions** — Offer: auto-fix, manual remediation, or proceed to next track

### 7. Reverting Work (`conductor revert`)

When the user wants to undo a track, phase, or task:

1. **Validate setup** — Ensure tracks.md exists and is not empty
2. **Target selection** — Accept specific target or show interactive menu:
   - Prioritize in-progress items (`[~]`)
   - Fall back to 5 most recently completed items (`[x]`)
3. **Git reconciliation** — Find ALL commits associated with the target:
   - Implementation commits (code changes)
   - Plan-update commits (status changes in plan.md)
   - Track creation commits (for full track reverts)
   - Handle "ghost" commits from rewritten history (rebase/squash)
4. **Present execution plan** — Show exact commits to be reverted, in reverse order
5. **Get final confirmation** — User must explicitly approve
6. **Execute reverts** — `git revert --no-edit <sha>` for each commit (most recent first)
7. **Handle conflicts** — If merge conflicts occur, halt and guide user through resolution
8. **Verify plan state** — Ensure plan.md is correctly updated after reverts

---

## Plan Format Reference

Plans use checkbox-style status markers organized into phases and tasks:

```markdown
# Implementation Plan: <Feature Name>

## Phase 1: Core Setup
- [x] Task 1: Initialize project structure (abc1234)
- [~] Task 2: Create database schema
  - [x] Sub-task 2.1: Define user model (def5678)
  - [ ] Sub-task 2.2: Define product model
- [ ] Task 3: Set up API routes
- [ ] Task: Conductor - User Manual Verification 'Core Setup' (Protocol in workflow.md)

## Phase 2: Feature Implementation [checkpoint: ghi9012]
- [ ] Task 4: Build user authentication
- [ ] Task: Conductor - User Manual Verification 'Feature Implementation' (Protocol in workflow.md)
```

**Status markers:**
- `[ ]` — Pending (not started)
- `[~]` — In progress
- `[x]` — Complete (append first 7 chars of commit hash in parentheses)

**Phase checkpoint:** When a phase is complete, its heading gets: `[checkpoint: <sha>]`

## Tracks Registry Format

```markdown
# Project Tracks

- [x] **Track: User Authentication**
  *Link: [./tracks/auth_20260115/](./tracks/auth_20260115/)*
- [~] **Track: Dark Mode Toggle**
  *Link: [./tracks/darkmode_20260120/](./tracks/darkmode_20260120/)*
- [ ] **Track: Navigation Bug Fix**
  *Link: [./tracks/navfix_20260122/](./tracks/navfix_20260122/)*
```

Track status markers: `[ ]` Pending, `[~]` In Progress, `[x]` Complete

Alternative table format (older versions):
```markdown
| ID | Title | Status | Created |
|----|-------|--------|---------|
| feat-auth | User Authentication | ✅ Complete | 2026-01-15 |
| feat-dark-mode | Dark Mode Toggle | 🔄 In Progress | 2026-01-20 |
```

Status emoji values: ⏳ Pending, 🔄 In Progress, ✅ Complete, ❌ Abandoned

## Commit Message Convention

All Conductor-related commits follow this format:
```
conductor(<scope>): <description>
```

**Scopes:** `feat`, `fix`, `test`, `docs`, `refactor`, `style`, `chore`, `plan`, `spec`, `setup`, `checkpoint`

**Examples:**
- `conductor(feat): Add user authentication endpoint`
- `conductor(test): Add unit tests for auth middleware`
- `conductor(plan): Mark task 'Create user model' as complete`
- `conductor(plan): Mark phase 'Core Setup' as complete`
- `chore(conductor): Mark track 'auth_20260115' as complete`
- `docs(conductor): Synchronize docs for track 'auth_20260115'`
- `conductor(spec): Create track 'darkmode_20260120'`
- `conductor(setup): Add conductor setup files`
- `conductor(checkpoint): Checkpoint end of Phase 1`

## Git Notes Protocol

After committing a task, attach a structured summary as a git note:

```bash
git notes add -m "Task: <task description>
Track: <track_id>
Phase: <phase number>
Changes:
- <file1>: <what changed>
- <file2>: <what changed>
Tests: <pass/fail/skipped>" $(git log -1 --format="%H")
```

For phase checkpoint commits, attach a verification report including:
- Automated test command and results
- Manual verification steps
- User's confirmation

## Quality Gates

Before marking any task complete, verify:
- All tests pass
- Code coverage meets requirements (>80% default, or per workflow.md)
- Code follows project's code style guidelines
- No linting or static analysis errors
- No security vulnerabilities introduced
- Documentation updated if needed

## Key Principles

- **Read context before coding** — Always understand the project's conventions first
- **Plan before implement** — Never skip the spec/plan phase for new features
- **Follow the workflow** — If workflow.md says TDD, do TDD. Follow commit conventions.
- **Human in the loop** — Always get user approval at phase boundaries and before major actions
- **Update as you go** — Keep plan.md current; don't batch status updates
- **Respect the stack** — Use only technologies defined in tech-stack.md unless explicitly approved
- **Validate every tool call** — After every file read/write or shell command, verify success. If any tool call fails, halt immediately and report the failure to the user before awaiting further instruction
- **Non-interactive & CI-aware** — Use `CI=true` for watch-mode tools to ensure single execution
- **Batch interactive questions** — When asking the user multiple questions (e.g., during setup or newTrack), batch up to 4 related questions together rather than asking one at a time

## Resuming Work

If the user returns to a project with an in-progress track:

1. Read `conductor/tracks.md` to find the active track
2. Read its `plan.md` to see what's been done and what's next
3. Report the current state: "You're on track X, Phase Y. Tasks A and B are
   done, Task C is next."
4. Ask if they want to continue from where they left off

## Detection Script

The project includes `scripts/detect_conductor.py` for quick environment detection:

```bash
python3 scripts/detect_conductor.py [project_root]
```

Returns JSON with: existence, setup status, active/pending tracks, next task, and context file inventory.
