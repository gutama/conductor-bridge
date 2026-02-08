---
name: conductor-bridge
description: >
  Work with existing Gemini Conductor environments from Claude Code. Use this skill whenever
  you detect a `conductor/` directory in the project root, or the user mentions "conductor",
  "tracks", "plan.md", "spec.md", "implement the track", "conductor status", "conductor setup",
  or any context-driven development workflow. This skill teaches Claude Code how to read
  Conductor's context files (product.md, tech-stack.md, workflow.md), understand track plans,
  implement tasks from plan.md, update task statuses, follow the project's defined workflow
  (e.g. TDD), and make properly formatted git commits. Also trigger when the user says
  "continue implementing", "what's the next task", "check conductor status", or references
  any conductor track by ID.
---

# Conductor Bridge for Claude Code

This skill enables Claude Code to work seamlessly with projects that use Google's
[Gemini Conductor](https://github.com/gemini-cli-extensions/conductor) — a context-driven
development framework that stores project knowledge, specs, and plans as versioned Markdown
files in a `conductor/` directory.

## When to use this skill

- A `conductor/` directory exists in the project root
- The user wants to continue implementing a Conductor plan
- The user asks about project status, tracks, or plans
- The user wants to create a new track (feature/bug) using the Conductor protocol
- The user wants to set up Conductor on an existing project

## Quick Start Protocol

When you detect a `conductor/` directory or the user mentions Conductor:

1. **Load context** — Read the conductor directory index and key context files
2. **Understand the plan** — Find the active track and its plan.md
3. **Work through tasks** — Implement tasks following the project's workflow
4. **Update status** — Mark tasks complete in plan.md and commit properly

## Conductor Directory Structure

Read `references/directory-structure.md` for the full layout. The key files:

```
conductor/
├── index.md              # Links to all context files (read this FIRST)
├── product.md            # Product definition, users, goals
├── product-guidelines.md # Standards, prose style, brand
├── tech-stack.md         # Language, frameworks, database, tooling
├── workflow.md           # Team workflow rules (TDD, commits, etc.)
├── code_styleguides/     # Language-specific style guides
├── tracks.md             # Registry of all tracks with status
└── tracks/               # Individual feature/bug tracks
    └── <track_id>/
        ├── index.md      # Links to track files
        ├── spec.md       # Feature specification
        ├── plan.md       # Actionable task list with status markers
        └── metadata.json # Track metadata
```

## Core Workflows

### Loading Project Context

Before doing any work, always load the project context:

```
1. Read conductor/index.md (or conductor/product.md if no index)
2. Read conductor/tech-stack.md — understand the stack
3. Read conductor/workflow.md — understand the team's workflow rules
4. Read conductor/tracks.md — understand active tracks
```

This context shapes everything: coding style, testing approach, commit conventions.

### Checking Status

When the user asks "what's the status" or "conductor status":

1. Read `conductor/tracks.md` to list all tracks and their statuses
2. Find any in-progress track
3. Read that track's `plan.md` to show current progress
4. Report: which phase is active, which tasks are done/pending/in-progress

### Implementing Tasks from plan.md

Read `references/implementation-protocol.md` for the detailed step-by-step protocol.

The high-level flow:

1. Read `conductor/workflow.md` to understand the team's development process
2. Read the active track's `plan.md`
3. Find the next pending task (marked `[ ]`)
4. Mark it in-progress `[~]`
5. Follow the workflow (if TDD: write test → fail → implement → pass)
6. Commit with proper message format: `conductor(<scope>): <description>`
7. Mark task complete `[x]` with commit hash
8. Update plan.md and commit the update
9. If phase is complete, run verification protocol
10. Move to next task

### Creating a New Track

When the user wants a new feature or bug fix:

1. Read project context (product.md, tech-stack.md)
2. Discuss requirements with user
3. Generate a track ID (e.g., `feat-dark-mode` or `fix-login-bug`)
4. Create `conductor/tracks/<track_id>/spec.md` — the specification
5. Create `conductor/tracks/<track_id>/plan.md` — the actionable plan
6. Create `conductor/tracks/<track_id>/metadata.json`
7. Register the track in `conductor/tracks.md`
8. Present spec and plan for user approval before implementing

### Setting Up Conductor on a New/Existing Project

Read `references/setup-protocol.md` for the full interactive setup procedure.

## Plan Format

Plans use checkbox-style status markers organized into phases and tasks:

```markdown
## Phase 1: Core Setup
- [x] Task 1: Initialize project structure (abc1234)
- [~] Task 2: Create database schema
  - [x] Sub-task 2.1: Define user model (def5678)
  - [ ] Sub-task 2.2: Define product model
- [ ] Task 3: Set up API routes

## Phase 2: Feature Implementation
- [ ] Task 4: Build user authentication
```

Status markers:
- `[ ]` — Pending (not started)
- `[~]` — In progress
- `[x]` — Complete (append first 7 chars of commit hash)

## Commit Message Convention

All Conductor-related commits follow this format:

```
conductor(<scope>): <description>
```

Scopes: `feat`, `fix`, `test`, `docs`, `refactor`, `plan`, `spec`, `setup`

Examples:
- `conductor(feat): Add user authentication endpoint`
- `conductor(test): Add unit tests for auth middleware`
- `conductor(plan): Mark task 'Create user model' as complete`

## Git Notes

After committing a task, attach a summary as a git note:

```bash
git notes add -m "<summary of changes>" <commit_hash>
```

## Phase Verification Protocol

When all tasks in a phase are complete:

1. Announce that the phase is complete
2. Run the full test suite (check workflow.md for the test command)
3. If tests pass, create a checkpoint commit
4. Ask the user for manual verification
5. Only proceed to the next phase after user approval

## Key Principles

- **Read context before coding** — Always understand the project's conventions first
- **Plan before implement** — Never skip the spec/plan phase for new features
- **Follow the workflow** — If workflow.md says TDD, do TDD. If it says specific commit conventions, follow them
- **Human in the loop** — Always get user approval at phase boundaries
- **Update as you go** — Keep plan.md current; don't batch status updates
- **Respect the stack** — Use only technologies defined in tech-stack.md unless explicitly approved
