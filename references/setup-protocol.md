# Setup Protocol

This protocol is for when the user wants to set up Conductor on a project
that doesn't already have a `conductor/` directory, or when setup was
started but not completed (check `conductor/setup_state.json`).

## Pre-Setup Check

1. Check if `conductor/` directory exists
2. If it does, check `conductor/setup_state.json` for the `last_successful_step` field
3. If step is `"3.3_initial_track_generated"`, setup is done — inform the user
4. If step is something else, resume from the next step after it
5. If no conductor/ directory, start fresh

**Resume mapping:**
- `""` or missing → Start from Step 1 (Project Classification)
- `"2.1_product_guide"` → Resume at Step 2.2 (Product Guidelines)
- `"2.2_product_guidelines"` → Resume at Step 2.3 (Tech Stack)
- `"2.3_tech_stack"` → Resume at Step 2.4 (Code Style Guides)
- `"2.4_code_styleguides"` → Resume at Step 2.5 (Workflow)
- `"2.5_workflow"` → Resume at Step 3.0 (Initial Track Generation)
- `"3.3_initial_track_generated"` → Setup complete, inform user

## Project Classification

Determine if this is a greenfield or brownfield project:

**Brownfield indicators** (any of these = brownfield):
- `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, or equivalent exists
- `src/`, `lib/`, or `app/` directory exists with code files
- `.git/` directory exists with more than an initial commit
- `git status --porcelain` shows uncommitted changes
- Functional code files exist (not just README/config)

**Greenfield**: Empty directory or only has README.md / basic config, no
dependency manifests, no source code directories.

If brownfield and there are uncommitted changes, warn the user to
commit or stash before proceeding.

### Brownfield Pre-Analysis

For brownfield projects, before asking interactive questions:

1. **Request permission** for a read-only scan to analyze the project
2. **Analyze codebase:**
   - Read README.md first (if exists)
   - Respect `.gitignore` and `.geminiignore` patterns
   - Use `git ls-files` to efficiently list relevant files
   - Prioritize manifest files (package.json, requirements.txt, etc.)
   - For large files (>1MB), read only first and last 20 lines
3. **Extract and infer:**
   - Tech stack from manifest files
   - Architecture from directory structure (top 2 levels)
   - Project goal from README header or package.json description
4. **Present findings** to user for confirmation/correction

## Setup Steps

### Step 1: Initialize

For greenfield projects:
- Run `git init` if no `.git/` directory exists
- Ask: "What do you want to build?"
- Create `conductor/` directory and `conductor/tracks/`
- Write user's response to `conductor/product.md` under `# Initial Concept`
- Initialize state file: `{"last_successful_step": ""}`

For brownfield projects:
- Proceed directly with codebase analysis results

### Step 2.1: Product Definition (product.md)

Interactively ask the user about (max 5 questions, one at a time):
- What is this project/product?
- Who are the target users?
- What are the primary goals?
- What are the key features?

**For brownfield projects**: Use code analysis to pre-populate answers.
Present analysis and let the user correct.

**Question format:**
- Classify each question as "Additive" (multiple answers) or "Exclusive Choice" (single answer)
- Provide 3 suggested answers based on context
- Always include "Type your own answer" and "Autogenerate and review" options
- If user selects auto-generate, stop asking and infer remaining details

Generate `conductor/product.md`:

```markdown
# Product Guide: <Project Name>

## Initial Concept
<Description>

## Target Audience
<Who uses this>

## Primary Goals
- **Goal 1:** <description>
- **Goal 2:** <description>

## Key Features
- <Feature 1>
- <Feature 2>
```

Present to user for approval. Allow edits via confirmation loop.
Save state: `{"last_successful_step": "2.1_product_guide"}`

### Step 2.2: Product Guidelines (product-guidelines.md)

Ask about (max 5 questions, one at a time):
- Prose style and tone
- Brand messaging guidelines
- Any visual identity rules
- Content standards

Generate `conductor/product-guidelines.md`.
Save state: `{"last_successful_step": "2.2_product_guidelines"}`

### Step 2.3: Tech Stack (tech-stack.md)

Ask about (or detect from brownfield project):
- Programming language(s) and version(s)
- Frameworks
- Database
- Testing tools
- Package manager
- Build tools
- CI/CD
- Deployment target

**For brownfield**: Parse package.json, requirements.txt, etc. to detect
the stack automatically. Present findings for confirmation.
**CRITICAL:** Document the *existing* tech stack, not propose changes.

Generate `conductor/tech-stack.md`.
Save state: `{"last_successful_step": "2.3_tech_stack"}`

### Step 2.4: Code Style Guides

Based on the tech stack, recommend appropriate style guides.

Available style guide templates (from Conductor extension):
- `general.md` — General coding conventions
- `typescript.md` — TypeScript/JavaScript conventions
- `javascript.md` — JavaScript conventions
- `python.md` — Python conventions (PEP 8 based)
- `go.md` — Go conventions
- `dart.md` — Dart conventions
- `cpp.md` — C++ conventions
- `csharp.md` — C# conventions
- `html-css.md` — HTML/CSS conventions

For brownfield: auto-select based on detected tech stack, ask for confirmation.
For greenfield: recommend based on chosen tech stack, let user customize.

Create `conductor/code_styleguides/` and copy selected guides.
Save state: `{"last_successful_step": "2.4_code_styleguides"}`

### Step 2.5: Workflow (workflow.md)

This is the most important file. Ask about:

1. "The default required test code coverage is >80%. Do you want to change this?"
2. "Do you want to commit changes after each task or after each phase?"
   - Default: After each task (recommended)
3. "Do you want to use git notes or the commit message to record the task summary?"
   - Default: Git Notes (recommended)

The workflow template includes:
- **Guiding Principles** — Plan is source of truth, TDD, high coverage, CI-aware
- **Standard Task Workflow** — Red/Green/Refactor phases, commit protocol, git notes
- **Phase Completion Verification** — Test coverage check, manual verification, checkpoints
- **Quality Gates** — Tests pass, coverage, style, docs, security, mobile
- **Commit Guidelines** — Conventional commit format with type/scope/description
- **Definition of Done** — Comprehensive checklist
- **Emergency Procedures** — Critical bugs, data loss, security breach

Generate `conductor/workflow.md` based on user choices.
Save state: `{"last_successful_step": "2.5_workflow"}`

### Step 2.6: Finalization

1. Create `conductor/index.md`:
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

2. Summarize all actions taken during setup

## Step 3.0: Initial Track Generation

### 3.1 Generate Product Requirements (Greenfield only)

Ask sequential questions (max 5) about:
- User stories
- Functional requirements
- Non-functional requirements

### 3.2 Propose Initial Track

Analyze product.md and tech-stack.md to propose a single initial track:
- **Greenfield**: Usually an MVP track
- **Brownfield**: Maintenance or targeted enhancement

Present for user approval. If declined, ask for clarification.

### 3.3 Create Track Artifacts

1. Initialize `conductor/tracks.md`:
```markdown
# Project Tracks

This file tracks all major tracks for the project.

---

- [ ] **Track: <Track Description>**
  *Link: [./tracks/<track_id>/](./tracks/<track_id>/)*
```

2. Generate track ID: `<shortname>_YYYYMMDD`
3. Create `conductor/tracks/<track_id>/` directory
4. Generate and write: metadata.json, spec.md, plan.md, index.md
5. Save state: `{"last_successful_step": "3.3_initial_track_generated"}`

### 3.4 Final Announcement

1. Commit all files: `conductor(setup): Add conductor setup files`
2. Inform user setup is complete
3. Suggest running implementation next

## Creating a New Track (Post-Setup)

### Generate Track ID

Use a kebab-case short name with date suffix:
- `<shortname>_YYYYMMDD` format (e.g., `darkmode_20260214`)

### Create Track Directory

```bash
mkdir -p conductor/tracks/<track_id>
```

### Generate spec.md

Through interactive discussion with the user, create the specification.
Include: overview, requirements, user stories, acceptance criteria,
technical approach, and out-of-scope items.

### Generate plan.md

Break down the spec into phases and tasks. Each phase should be a
logical unit of work that can be verified independently.

Guidelines for good plans:
- 2-5 phases per track
- 2-6 tasks per phase
- Tasks should be completable in a single focused session
- Sub-tasks for complex items
- Include testing tasks explicitly if TDD
- **CRITICAL:** Each phase MUST end with a manual verification meta-task:
  `- [ ] Task: Conductor - User Manual Verification '<Phase Name>' (Protocol in workflow.md)`

### Generate metadata.json

```json
{
  "track_id": "<track_id>",
  "type": "<feature|bugfix|refactor>",
  "status": "new",
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>",
  "description": "<Brief description>"
}
```

### Create Track index.md

```markdown
# Track <track_id> Context

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
```

### Register in tracks.md

Add entry to `conductor/tracks.md`:

```markdown
- [ ] **Track: <Track Description>**
  *Link: [./tracks/<track_id>/](./tracks/<track_id>/)*
```

### Commit and Present

```bash
git add conductor/
git commit -m "conductor(spec): Create track '<track_id>'"
```

Present the spec and plan to the user for review. Only proceed to
implementation after they approve.
