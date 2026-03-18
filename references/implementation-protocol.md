# Implementation Protocol

This is the step-by-step protocol for implementing tasks from a Conductor plan.
Follow this exactly when the user says "implement", "continue implementing",
"start the next task", or similar.

## System Directive

Validate the success of every tool call (file read, file write, shell command).
If any tool call fails, halt immediately and inform the user before awaiting
further instruction. Never proceed past a failed operation.

## Pre-Implementation: Load Context

Before writing any code, always read these files:

1. `conductor/workflow.md` — the team's development process (TDD? commit conventions?)
2. `conductor/tech-stack.md` — allowed technologies and versions
3. `conductor/tracks.md` — find the active (in-progress) track
4. `conductor/tracks/<active_track>/plan.md` — the task list
5. `conductor/tracks/<active_track>/spec.md` — the feature specification

If `conductor/code_styleguides/` has relevant style guides for the project's
language, read those too.

## Finding the Next Task

In the active track's `plan.md`:

1. Scan for the first task marked `[~]` (in-progress) — resume it
2. If no in-progress task, find the first task marked `[ ]` (pending)
3. Tasks within a phase must be completed in order
4. Phases must be completed in order
5. Never skip ahead to a later phase while an earlier one has pending tasks

## Task Implementation Loop

For each task:

### Step 1: Mark In-Progress

Update `plan.md` to mark the current task as `[~]`:

```
- [~] Task N: Create user authentication middleware
```

Save the file (don't commit yet — wait until the task is done).

### Step 2: Understand the Task

Read the task description and any sub-tasks. Cross-reference with:
- The spec.md for requirements context
- The tech-stack.md for technology constraints
- Existing code to understand patterns and conventions

### Step 3: Follow the Workflow

Check `conductor/workflow.md` for the implementation methodology.

**If TDD is specified:**

1. **Red phase** — Write a failing test first
   - Create test file if it doesn't exist
   - Write tests that define the expected behavior
   - Run the test suite and confirm the new tests FAIL
   - Do not proceed until you have failing tests

2. **Green phase** — Write minimal code to pass
   - Implement just enough to make the failing tests pass
   - Run the test suite and confirm all tests PASS

3. **Refactor phase** (optional)
   - Clean up the implementation
   - Ensure tests still pass after refactoring

**If no TDD:**

1. Implement the task following the project's conventions
2. Write tests if the workflow requires them
3. Run any defined test/lint commands

### Step 4: Verify Coverage

Run coverage reports using the project's chosen tools. For example:
```bash
pytest --cov=app --cov-report=html          # Python
CI=true npm test -- --coverage              # Node.js
go test -cover ./...                        # Go
```

Target: >80% coverage for new code (or whatever workflow.md specifies).

### Step 5: Document Deviations

If implementation differs from tech stack:
- **STOP** implementation
- Update `tech-stack.md` with the new design
- Add dated note explaining the change
- Resume implementation

### Step 6: Commit the Work

Format the commit message following Conductor convention:

```
conductor(<scope>): <description>
```

Where `<scope>` is one of: `feat`, `fix`, `test`, `docs`, `refactor`, `style`, `chore`

Example:
```bash
git add -A
git commit -m "conductor(feat): Add JWT authentication middleware"
```

Capture the commit hash:
```bash
COMMIT_HASH=$(git rev-parse --short HEAD)
```

### Step 7: Attach Git Note

Create a structured summary and attach it as a git note:

```bash
git notes add -m "Task: <task description>
Track: <track_id>
Phase: <phase number>
Changes:
- <file1>: <what changed>
- <file2>: <what changed>
Tests: <pass/fail/skipped>" $(git log -1 --format="%H")
```

### Step 8: Update Plan Status

In `plan.md`, update the completed task:

```
- [x] Task N: Create user authentication middleware (abc1234)
```

The hash in parentheses is the first 7 characters of the commit hash.

### Step 9: Commit Plan Update

```bash
git add conductor/tracks/<track_id>/plan.md
git commit -m "conductor(plan): Mark task '<task name>' as complete"
```

### Step 10: Check for Phase Completion

If all tasks in the current phase are now `[x]`:

1. **Announce** — Tell the user the phase is complete and the verification protocol has begun

2. **Ensure Test Coverage for Phase Changes:**
   - Determine phase scope: find the previous phase's checkpoint SHA from plan.md
   - List changed files: `git diff --name-only <previous_checkpoint_sha> HEAD`
   - For each code file (exclude .json, .md, .yaml), verify a corresponding test exists
   - If a test file is missing, create one. Analyze existing test files first to match naming conventions and style.

3. **Run Full Test Suite:**
   - Announce the exact shell command before executing
   - Use `CI=true` prefix for non-interactive execution (e.g., `CI=true npm test`)
   - If tests fail, attempt to fix (maximum 2 attempts)
   - If still failing after 2 attempts, stop and ask user for guidance

4. **Propose Manual Verification Plan:**
   - Analyze product.md, product-guidelines.md, and plan.md for user-facing goals
   - Generate step-by-step verification instructions:
     - **Frontend:** Start dev server, open browser URL, confirm visual elements
     - **Backend:** Run curl/HTTP commands, confirm responses and status codes

5. **Await User Confirmation:**
   - Ask: "Does this meet your expectations? Please confirm with yes or provide feedback."
   - PAUSE — do NOT proceed without explicit user approval

6. **Create Checkpoint:**
   ```bash
   git commit -m "conductor(checkpoint): Checkpoint end of Phase <N>"
   ```

7. **Attach Verification Report as Git Note:**
   - Include: automated test command/results, manual verification steps, user confirmation

8. **Update Plan with Checkpoint:**
   - Append checkpoint SHA to the phase heading: `[checkpoint: <sha>]`
   - Commit: `conductor(plan): Mark phase '<Phase Name>' as complete`

### Step 11: Continue or Stop

After completing a task (and optionally a phase):

- If the user asked to "implement all" or "continue", move to the next task
- If the user asked for just one task, stop and report
- If you encounter ambiguity or a task that needs clarification, stop and ask

## Handling Failures

### Test Failures

If tests fail during implementation:

1. Report the failure clearly to the user
2. Attempt to fix (maximum 2 attempts)
3. If still failing after 2 attempts, stop and ask the user for guidance
4. Never mark a task as complete if tests are failing

### Missing Context

If a task references something not in the codebase or spec:

1. Check if it's defined elsewhere in the conductor/ files
2. If not, ask the user for clarification
3. Never guess or make assumptions about undefined requirements

### Merge Conflicts

If you encounter conflicts in conductor files:

1. Always prefer the more recent/complete version
2. For plan.md, ensure status markers are preserved
3. Report the conflict resolution to the user

## Track Completion

When all phases in a plan are complete:

1. Update `conductor/tracks/<track_id>/metadata.json` — set status to `"complete"`, update `updated_at`
2. Update `conductor/tracks.md` — mark the track as `[x]` complete
3. Commit: `chore(conductor): Mark track '<track_id>' as complete`

4. **Documentation Sync** — Analyze the spec and propose updates to project context:
   - `product.md` — if features significantly change the product description
   - `tech-stack.md` — if technology choices shifted during implementation
   - `product-guidelines.md` — only for strategic rebranding (with strict warnings)
   - All changes require explicit user confirmation before applying
   - Commit approved changes: `docs(conductor): Synchronize docs for track '<track_id>'`

5. **Track Cleanup** — Offer the user options:
   - **Review** — Run the review protocol
   - **Archive** — Move to `conductor/archive/`
   - **Delete** — Permanently remove (with irreversible action warning)
   - **Skip** — Leave for later

6. Inform the user the track is fully implemented

## Resuming Work

If the user returns to a project with an in-progress track:

1. Read `conductor/tracks.md` to find the active track
2. Read its `plan.md` to see what's been done and what's next
3. Report the current state: "You're on track X, Phase Y. Tasks A and B are
   done, Task C is next."
4. Ask if they want to continue from where they left off
