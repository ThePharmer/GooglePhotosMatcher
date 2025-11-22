# Generate Custom Claude Code Command

This command helps you create new slash commands in `.claude/commands/` to automate development tasks.

## Command Structure Template

Commands should follow a markdown format with clear sections:
- Goal statement
- Sequential steps with specific details
- Success criteria checkboxes

## Key Capabilities to Leverage

When creating commands, consider these capabilities:

### File Operations
- Reading, editing, and searching code
- Creating and modifying files

### Development Tools
- Bash commands
- Specialized agents
- Testing frameworks

### Web/API Integrations
- GitHub operations
- Browser automation
- External service APIs

### External Services
- Monitoring platforms
- Productivity tools

## Best Practices

1. **Be specific and clear** - detailed instructions yield better results
2. **Break complex tasks** into manageable phases
3. **Reference existing code patterns** as examples
4. **Define testable success criteria** upfront
5. **Use deliberate planning** for intricate problems

## Implementation Pattern

Effective commands follow this workflow:
1. Research existing patterns
2. Plan the approach
3. Implement following conventions
4. Verify with tests and linting
5. Optionally commit changes

## Dynamic Placeholders

Use placeholders to make commands flexible:
- `$ARGUMENTS` - User-provided arguments
- XML tags for structured prompts

## Example Command Structure

```markdown
# Command Name

## Goal
[Clear statement of what this command accomplishes]

## Steps

### Step 1: Research
[Research existing patterns and context]

### Step 2: Plan
[Outline the approach]

### Step 3: Implement
[Execute the implementation]

### Step 4: Verify
[Run tests and validation]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```
