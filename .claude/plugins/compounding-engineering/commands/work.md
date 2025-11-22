# Execute Work Plan

Systematically analyze work documents and execute plans through structured phases.

## Arguments

$ARGUMENTS - Path to work document or GitHub issue URL

## Workflow

### Phase 1: Environment Setup

Prepare the Git environment:

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/[descriptive-name]

# Optional: Create isolated worktree
git worktree add .worktrees/feature/[name] -b feature/[name]
```

### Phase 2: Document Analysis

Thoroughly analyze the input document:

1. **Identify all deliverables and requirements**
2. **Extract success criteria**
3. **Note any constraints or dependencies**
4. **Identify risks and unknowns**

Convert findings into a structured task breakdown with implementation details.

### Phase 3: Systematic Execution

Execute tasks in priority order based on dependencies:

```
For each task:
  1. Mark task as in_progress (TodoWrite)
  2. Implement the task
  3. Run quality assurance:
     - Tests (pytest, jest, rspec, etc.)
     - Linting (eslint, rubocop, flake8, etc.)
     - Type checking (mypy, tsc, etc.)
  4. Fix any issues found
  5. Mark task as completed (TodoWrite)
  6. Proceed to next task
```

### Phase 4: Completion

Final validation and submission:

1. **Verify all deliverables are present**
2. **Run full test suite**
3. **Run all linters**
4. **Commit changes with descriptive message**
5. **Create pull request**

## Quality Assurance Commands

### Python
```bash
pytest
flake8 .
mypy .
```

### TypeScript/JavaScript
```bash
npm test
npm run lint
npm run typecheck
```

### Ruby/Rails
```bash
bundle exec rspec
bundle exec rubocop
```

## Key Principles

- **Dependency Management**: Always respect task dependencies
- **Progress Tracking**: Update TodoWrite after each task
- **Incremental Validation**: Run tests after each significant change
- **Clear Commits**: One logical change per commit

## Output

Upon completion:
- Summary of completed tasks
- Test results
- Pull request URL (if created)
- Any remaining issues or follow-ups
