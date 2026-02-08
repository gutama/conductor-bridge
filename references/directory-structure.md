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

## File Resolution Protocol

Conductor uses an index-based file resolution system. To find any file:

1. Read the relevant `index.md` file
2. Look for the link to the file you need
3. Resolve the path relative to the directory containing the index.md

For project-level files, read `conductor/index.md`.
For track-level files, read `conductor/tracks/<track_id>/index.md`.

If an index.md is missing, fall back to the default paths shown above.

## Key File Formats

### product.md

Contains product definition, target audience, primary goals, and high-level features.
Written as Markdown with sections like:

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

- **Core Principles** — fundamental rules (TDD, high coverage, etc.)
- **Task Implementation Protocol** — step-by-step process for each task
- **Commit Protocol** — how to format and structure commits
- **Phase Completion Protocol** — verification steps between phases
- **Git Notes Protocol** — how to annotate commits with summaries

### tracks.md

Registry file listing all tracks and their current status:

```markdown
# Tracks

| ID | Title | Status | Created |
|----|-------|--------|---------|
| feat-auth | User Authentication | ✅ Complete | 2026-01-15 |
| feat-dark-mode | Dark Mode Toggle | 🔄 In Progress | 2026-01-20 |
| fix-nav-bug | Navigation Bug Fix | ⏳ Pending | 2026-01-22 |
```

Status values: ⏳ Pending, 🔄 In Progress, ✅ Complete, ❌ Abandoned

### plan.md (per track)

Actionable task plan with status checkboxes:

```markdown
# Implementation Plan: <Feature Name>

## Phase 1: <Phase Title>
- [ ] Task 1: <Description>
  - [ ] Sub-task 1.1: <Description>
  - [ ] Sub-task 1.2: <Description>
- [ ] Task 2: <Description>

## Phase 2: <Phase Title>
- [ ] Task 3: <Description>
```

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
  "id": "feat-dark-mode",
  "title": "Dark Mode Toggle",
  "description": "Add a dark mode toggle to the settings page",
  "status": "in_progress",
  "created_at": "2026-01-20T10:30:00Z",
  "updated_at": "2026-01-22T14:00:00Z",
  "type": "feature"
}
```

### setup_state.json

Tracks which steps of the setup wizard are complete:

```json
{
  "STEP": "complete",
  "CLASSIFICATION": "brownfield"
}
```

Possible STEP values during setup:
- `"2.1_product_guide"` — product.md created
- `"2.2_product_guidelines"` — product-guidelines.md created
- `"3_tech_stack"` — tech-stack.md created
- `"4_code_styleguides"` — style guides selected
- `"5_workflow"` — workflow.md created
- `"complete"` — setup fully done
