# Comprehensive Code Review

Perform a multi-agent code review combining Git worktrees, parallel analysis, and systematic finding synthesis.

## Arguments

$ARGUMENTS - PR number, branch name, or commit range to review

## Workflow

### Phase 1: Worktree Setup (Critical First Step)

Create an isolated Git worktree before any analysis:

```bash
git worktree add .worktrees/reviews/pr-$identifier origin/$branch
cd .worktrees/reviews/pr-$identifier
```

### Phase 2: Project Type Detection

Identify project types by examining key files:
- `Gemfile` → Rails
- `tsconfig.json` → TypeScript
- `requirements.txt` or `pyproject.toml` → Python

Assign appropriate language-specific reviewers based on detection.

### Phase 3: Parallel Agent Execution

Run ALL or most of these agents at the same time:

#### Universal Agents
- `security-sentinel` - Security vulnerability analysis
- `performance-oracle` - Performance bottleneck detection
- `architecture-strategist` - Architectural compliance
- `code-simplicity-reviewer` - YAGNI and complexity analysis
- `pattern-recognition-specialist` - Pattern and anti-pattern detection

#### Language-Specific Agents
- `kieran-rails-reviewer` (if Rails)
- `dhh-rails-reviewer` (if Rails)
- `kieran-typescript-reviewer` (if TypeScript)
- `kieran-python-reviewer` (if Python)

### Phase 4: Ultra-Thinking Analysis

Deep cognitive phases examining:

#### Stakeholder Perspectives
- Developer experience
- Operations concerns
- Security implications
- Business value

#### Scenario Exploration
- Edge cases
- Concurrent access
- Scale testing
- Failure modes

### Phase 5: Multi-Angle Review

Four perspectives evaluate the code:
1. **Technical Excellence**: Code quality and best practices
2. **Business Value**: Feature completeness and user impact
3. **Risk Management**: Security, performance, and reliability
4. **Team Dynamics**: Maintainability and knowledge sharing

### Phase 6: Finding Synthesis & Todo Creation

#### Severity Categories
- 🔴 **P1 Critical**: Must fix before merge
- 🟡 **P2 Important**: Should fix, can be follow-up
- 🔵 **P3 Nice-to-have**: Suggestions for improvement

#### Todo File Creation

For each finding, create a structured todo file with:
- Issue description
- Affected files
- Effort estimate
- Acceptance criteria

## Output

Summary report listing:
- Created todos by severity
- Key findings summary
- Next steps for triage and resolution
