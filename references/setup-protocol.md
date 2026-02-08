# Setup Protocol

This protocol is for when the user wants to set up Conductor on a project
that doesn't already have a `conductor/` directory, or when setup was
started but not completed (check `conductor/setup_state.json`).

## Pre-Setup Check

1. Check if `conductor/` directory exists
2. If it does, check `conductor/setup_state.json` for the current step
3. If STEP is "complete", setup is done — inform the user
4. If STEP is something else, resume from that step
5. If no conductor/ directory, start fresh

## Project Classification

Determine if this is a greenfield or brownfield project:

**Brownfield indicators** (any of these = brownfield):
- `package.json`, `requirements.txt`, `Cargo.toml`, or equivalent exists
- `src/`, `lib/`, or `app/` directory exists with code files
- `.git/` directory has more than an initial commit
- Functional code files exist (not just README/config)

**Greenfield**: Empty directory or only has README.md / basic config

If brownfield and there are uncommitted changes, warn the user to
commit or stash before proceeding.

## Setup Steps

### Step 1: Create conductor/ directory

```bash
mkdir -p conductor/tracks
mkdir -p conductor/code_styleguides
```

### Step 2.1: Product Definition (product.md)

Interactively ask the user about:
- What is this project/product?
- Who are the target users?
- What are the primary goals?
- What are the key features?

**For brownfield projects**: Analyze the existing codebase first.
Read README.md, package.json (description), and scan the source code
to pre-populate answers. Present your analysis and let the user correct.

Generate `conductor/product.md` with:

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

Present to user for approval. Allow edits.
Save `conductor/setup_state.json`: `{"STEP": "2.1_product_guide"}`

### Step 2.2: Product Guidelines (product-guidelines.md)

Ask about:
- Prose style and tone
- Brand messaging guidelines
- Any visual identity rules
- Content standards

Generate `conductor/product-guidelines.md`.
Save state: `{"STEP": "2.2_product_guidelines"}`

### Step 3: Tech Stack (tech-stack.md)

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
the stack automatically. Present findings and let user confirm/modify.

Generate `conductor/tech-stack.md`.
Save state: `{"STEP": "3_tech_stack"}`

### Step 4: Code Style Guides

Based on the tech stack, recommend appropriate style guides.
Copy or generate style guide files into `conductor/code_styleguides/`.

Common options:
- `typescript.md` — TypeScript/JavaScript conventions
- `python.md` — Python conventions (PEP 8 based)
- `go.md` — Go conventions
- `rust.md` — Rust conventions

Save state: `{"STEP": "4_code_styleguides"}`

### Step 5: Workflow (workflow.md)

This is the most important file. Ask about:
- Do they use TDD? If so, what's the test command?
- Commit message convention (default: Conductor convention)
- Code review process
- Branch strategy
- Preferred CI checks

Generate `conductor/workflow.md` following the template structure:

Key sections to include:
- Core Principles (TDD, code coverage targets, etc.)
- Task Implementation Protocol (step-by-step for each task)
- Commit Protocol (message format, when to commit)
- Phase Completion Protocol (verification steps)
- Non-Interactive & CI-Aware settings

Save state: `{"STEP": "5_workflow"}`

### Step 6: Initialize tracks.md

Create an empty tracks registry:

```markdown
# Tracks

| ID | Title | Status | Created |
|----|-------|--------|---------|

_No tracks yet. Create one with "create a new track"._
```

### Step 7: Create index.md

Create `conductor/index.md` linking to all generated files:

```markdown
# Conductor Project Index

- [Product Guide](./product.md)
- [Product Guidelines](./product-guidelines.md)
- [Tech Stack](./tech-stack.md)
- [Workflow](./workflow.md)
- [Code Style Guides](./code_styleguides/)
- [Tracks Registry](./tracks.md)
- [Tracks Directory](./tracks/)
```

### Step 8: Finalize

1. Update `conductor/setup_state.json`: `{"STEP": "complete", "CLASSIFICATION": "<greenfield|brownfield>"}`
2. Commit everything:
   ```bash
   git add conductor/
   git commit -m "conductor(setup): Initialize Conductor environment"
   ```
3. Inform the user that setup is complete
4. Suggest creating a first track if they have a feature in mind

## Creating a New Track

After setup, when the user wants a new feature:

### Generate Track ID

Use a kebab-case ID with a type prefix:
- Features: `feat-<short-description>` (e.g., `feat-dark-mode`)
- Bug fixes: `fix-<short-description>` (e.g., `fix-login-crash`)
- Refactors: `refactor-<short-description>`

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

### Generate metadata.json

```json
{
  "id": "<track_id>",
  "title": "<Human-Readable Title>",
  "description": "<Brief description>",
  "status": "pending",
  "type": "<feature|bugfix|refactor>",
  "created_at": "<ISO timestamp>",
  "updated_at": "<ISO timestamp>"
}
```

### Create Track index.md

```markdown
# Track: <Title>

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
```

### Register in tracks.md

Add a row to `conductor/tracks.md`:

```
| <track_id> | <Title> | ⏳ Pending | <date> |
```

### Commit and Present

```bash
git add conductor/
git commit -m "conductor(spec): Create track '<track_id>'"
```

Present the spec and plan to the user for review. Only proceed to
implementation after they approve.
