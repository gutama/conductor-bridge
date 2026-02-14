# Conductor Directory Structure Reference

## Project Root Layout

A project with Conductor set up has this structure at the root:

```
project-root/
├── conductor/                    # All Conductor context and plans
│   ├── index.md                  # Master index linking to all context files
│   ├── product.md                # Product definition
│   ├── product-guidelines.md     # Brand and content standards
│   ├── tech-stack.md             # Technical preferences and stack
│   ├── workflow.md               # Development workflow (TDD, commits, etc.)
│   ├── setup_state.json          # Setup wizard progress tracking
│   ├── code_styleguides/         # Language-specific coding style guides
│   │   └── <language>.md         # e.g., typescript.md, python.md
│   ├── tracks.md                 # Registry of all tracks with status
│   └── tracks/                   # Directory containing all tracks
│       ├── <track-id>/           # One directory per track
│       │   ├── index.md          # Track index linking to its files
│       │   ├── spec.md           # Feature specification
│       │   ├── plan.md           # Actionable task plan
│       │   └── metadata.json     # Track metadata (timestamps, status)
│       └── <another-track-id>/
│           └── ...
├── GEMINI.md                     # Gemini CLI context file (may exist)
└── ... (rest of project)
```

## Universal File Resolution Protocol

Conductor uses an index-based file resolution system. To find any file:

1. **Identify Index** — Determine the relevant index file:
   - **Project Context:** `conductor/index.md`
   - **Track Context:**
     a. Resolve and read the **Tracks Registry** (via Project Context)
     b. Find the entry for the specific `<track_id>`
     c. Follow the link provided in the registry to locate the track's folder
     d. The index file is `<track_folder>/index.md`
     e. **Fallback:** If not registered yet, use `conductor/tracks/<track_id>/index.md`

2. **Check Index** — Read the index file and look for a link with a matching or
   semantically similar label

3. **Resolve Path** — If a link is found, resolve its path **relative to the
   directory containing the index.md file**
   - Example: If `conductor/index.md` links to `./workflow.md`, the full path is
     `conductor/workflow.md`

4. **Fallback** — If the index file is missing or the link is absent, use the
   default paths shown above

5. **Verify** — Confirm the resolved file actually exists on disk

## Key File Formats

### index.md (Project)

```markdown
# Project Context

## Definition
- [Product Definition](./product.md)
- [Product Guidelines](./product-guidelines.md)
- [Tech Stack](./tech-stack.md)

## Workflow
- [Workflow](./workflow.md)
- [Code Style Guides](./code_styleguides/)

## Management
- [Tracks Registry](./tracks.md)
- [Tracks Directory](./tracks/)
```

### product.md

Contains product definition, target audience, primary goals, and high-level features.

```markdown
# Product Guide: <Project Name>

## Initial Concept
<Description of the project>

## Target Audience
<Who uses this>

## Primary Goals
- **Goal 1:** Description
- **Goal 2:** Description

## Key Features
- Feature A
- Feature B
```

### product-guidelines.md

Brand and content standards: prose style, messaging, visual identity.

### tech-stack.md

Defines the allowed technologies. The agent must not introduce technologies
that aren't documented here without explicit approval.

```markdown
# Tech Stack

## Language
- TypeScript 5.x

## Framework
- Next.js 14 (App Router)

## Database
- PostgreSQL with Prisma ORM

## Testing
- Jest + React Testing Library

## Package Manager
- pnpm
```

### workflow.md

Defines the development process the agent must follow. Key sections:

- **Guiding Principles** — Plan is source of truth, TDD, high coverage, CI-aware
- **Standard Task Workflow** — Red/Green/Refactor TDD cycle, commit protocol, git notes
- **Phase Completion Verification and Checkpointing Protocol** — Test coverage, manual verification, checkpoint commits
- **Quality Gates** — Tests, coverage, style, docs, security, mobile
- **Commit Guidelines** — Conventional commit format with type/scope/description
- **Definition of Done** — Comprehensive checklist
- **Testing Requirements** — Unit, integration, mobile testing
- **Code Review Process** — Self-review checklist
- **Emergency Procedures** — Critical bugs, data loss, security breach
- **Deployment Workflow** — Pre-deployment, deployment, post-deployment

### tracks.md

Registry file listing all tracks and their current status.

**Current format (v0.3.0):**
```markdown
# Project Tracks

This file tracks all major tracks for the project.

---

- [x] **Track: User Authentication**
  *Link: [./tracks/auth_20260115/](./tracks/auth_20260115/)*
- [~] **Track: Dark Mode Toggle**
  *Link: [./tracks/darkmode_20260120/](./tracks/darkmode_20260120/)*
- [ ] **Track: Navigation Bug Fix**
  *Link: [./tracks/navfix_20260122/](./tracks/navfix_20260122/)*
```

Status markers: `[ ]` Pending, `[~]` In Progress, `[x]` Complete

**Older table format:**
```markdown
# Tracks

| ID | Title | Status | Created |
|----|-------|--------|---------|
| feat-auth | User Authentication | ✅ Complete | 2026-01-15 |
| feat-dark-mode | Dark Mode Toggle | 🔄 In Progress | 2026-01-20 |
```

Status emoji values: ⏳ Pending, 🔄 In Progress, ✅ Complete, ❌ Abandoned

### plan.md (per track)

Actionable task plan with status checkboxes:

```markdown
# Implementation Plan: <Feature Name>

## Phase 1: <Phase Title>
- [x] Task 1: <Description> (abc1234)
- [~] Task 2: <Description>
  - [x] Sub-task 2.1: <Description> (def5678)
  - [ ] Sub-task 2.2: <Description>
- [ ] Task 3: <Description>
- [ ] Task: Conductor - User Manual Verification '<Phase Title>' (Protocol in workflow.md)

## Phase 2: <Phase Title> [checkpoint: ghi9012]
- [ ] Task 4: <Description>
- [ ] Task: Conductor - User Manual Verification '<Phase Title>' (Protocol in workflow.md)
```

Status markers:
- `[ ]` — Pending (not started)
- `[~]` — In progress
- `[x]` — Complete (append first 7 chars of commit hash in parentheses)

Phase checkpoint: `[checkpoint: <sha>]` appended to phase heading when phase is complete.

Each phase MUST end with a manual verification meta-task.

### spec.md (per track)

Feature specification with sections:

```markdown
# Specification: <Feature Name>

## Overview
<What this feature does and why>

## Requirements
### Functional Requirements
- FR1: <requirement>
- FR2: <requirement>

### Non-Functional Requirements
- NFR1: <requirement>

## User Stories
- As a <user>, I want <action> so that <benefit>

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Technical Approach
<How this will be implemented>

## Out of Scope
<What this does NOT include>
```

### metadata.json (per track)

```json
{
  "track_id": "darkmode_20260120",
  "type": "feature",
  "status": "new",
  "created_at": "2026-01-20T10:30:00Z",
  "updated_at": "2026-01-22T14:00:00Z",
  "description": "Add a dark mode toggle to the settings page"
}
```

Status values: `"new"`, `"in_progress"`, `"completed"`, `"cancelled"`
Type values: `"feature"`, `"bugfix"`, `"refactor"`

### setup_state.json

Tracks which step of the setup wizard was last completed:

```json
{
  "last_successful_step": "complete"
}
```

Possible step values during setup:
- `""` — just started, no steps complete
- `"2.1_product_guide"` — product.md created
- `"2.2_product_guidelines"` — product-guidelines.md created
- `"2.3_tech_stack"` — tech-stack.md created
- `"2.4_code_styleguides"` — style guides selected
- `"2.5_workflow"` — workflow.md created
- `"3.3_initial_track_generated"` — initial track created, setup complete

### index.md (per track)

```markdown
# Track <track_id> Context

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
```

## Available Code Style Guide Templates

The Conductor extension ships with these style guide templates:
- `general.md` — General coding conventions
- `typescript.md` — TypeScript conventions
- `javascript.md` — JavaScript conventions
- `python.md` — Python conventions (PEP 8 based)
- `go.md` — Go conventions
- `dart.md` — Dart conventions
- `cpp.md` — C++ conventions
- `csharp.md` — C# conventions
- `html-css.md` — HTML/CSS conventions
