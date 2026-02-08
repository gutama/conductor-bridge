# Implementation Protocol

This is the step-by-step protocol for implementing tasks from a Conductor plan.
Follow this exactly when the user says "implement", "continue implementing",
"start the next task", or similar.

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

### Step 4: Commit the Work

Format the commit message following Conductor convention:

```
conductor(<scope>): <description>
```

Where `<scope>` is one of: `feat`, `fix`, `test`, `docs`, `refactor`

Example:
```bash
git add -A
git commit -m "conductor(feat): Add JWT authentication middleware"
```

Capture the commit hash:
```bash
COMMIT_HASH=$(git rev-parse --short HEAD)
```

### Step 5: Attach Git Note

Create a structured summary and attach it as a git note:

```bash
git notes add -m "Task: <task description>
Track: <track_id>
Phase: <phase number>
Changes:
- <file1>: <what changed>
- <file2>: <what changed>
Tests: <pass/fail/skipped>" $COMMIT_HASH
```

### Step 6: Update Plan Status

In `plan.md`, update the completed task:

```
- [x] Task N: Create user authentication middleware (abc1234)
```

The hash in parentheses is the first 7 characters of the commit hash.

### Step 7: Commit Plan Update

```bash
git add conductor/tracks/<track_id>/plan.md
git commit -m "conductor(plan): Mark task '<task name>' as complete"
```

### Step 8: Check for Phase Completion

If all tasks in the current phase are now `[x]`:

1. **Announce** — Tell the user the phase is complete
2. **Run full test suite** — Execute the test command from workflow.md
3. **Report results** — Show the user test results
4. **Create checkpoint** — If tests pass:
   ```bash
   git tag conductor/<track_id>/phase-<N>-complete
   ```
5. **Ask for verification** — Request the user to manually verify
6. **Wait** — Do not proceed to the next phase without user approval

### Step 9: Continue or Stop

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

1. Update `conductor/tracks/<track_id>/metadata.json` — set status to `"complete"`
2. Update `conductor/tracks.md` — mark the track as ✅ Complete
3. Commit: `conductor(plan): Mark track '<track_id>' as complete`
4. Inform the user the track is fully implemented
5. Optionally suggest syncing any changed context back to conductor/ files

## Resuming Work

If the user returns to a project with an in-progress track:

1. Read `conductor/tracks.md` to find the active track
2. Read its `plan.md` to see what's been done and what's next
3. Report the current state: "You're on track X, Phase Y. Tasks A and B are
   done, Task C is next."
4. Ask if they want to continue from where they left off
