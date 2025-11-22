# Triage Code Review Findings

Systematically process code review findings, security audits, and performance analyses into a CLI todo system.

**Important**: NO CODING during triage. Focus on categorization and decision-making only.

## Workflow

### Step 1: Present Findings

Display each issue in standardized format:

```markdown
## Finding #[ID]

**Severity**: P1/P2/P3
**Category**: Security/Performance/Architecture/Quality
**Description**: [Brief description]
**Location**: [File:line]
**Problem Scenario**: [What could go wrong]
**Proposed Solution**: [Recommended fix]
```

### Step 2: Handle User Decisions

Process user responses:

| Response | Action |
|----------|--------|
| `yes` | Create todo file using template |
| `next` | Skip to next item |
| `custom` | Modify details before creating |

### Step 3: Todo File Creation

When approved, create todo with proper naming convention:

```
{id}-pending-{priority}-{description}.md
```

Example: `001-pending-p1-fix-sql-injection.md`

### Todo Template

```yaml
---
id: [next_id]
priority: [p1/p2/p3]
status: pending
category: [category]
created: [date]
---

# [Title]

## Problem Statement
[Description of the issue]

## Proposed Solution
[Recommended approach]

## Technical Details
- **File(s)**: [affected files]
- **Effort**: [small/medium/large]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Step 4: Continue Processing

Work through all items sequentially without waiting for approvals between items.

### Step 5: Final Summary

Report:
- Total items processed
- Todos created
- Items skipped
- Next steps

## Important Requirements

- Determine next issue ID from existing todos
- Use consistent YAML frontmatter for metadata
- Track progress (items completed, remaining, estimated completion time)
- Remove non-relevant todos when "next" is selected
- **Never code during triage sessions**
- Maintain visibility through TodoWrite system
