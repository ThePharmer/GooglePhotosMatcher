# Create GitHub Issue

Transform feature ideas and bug reports into well-organized GitHub issues that align with project standards.

## Arguments

$ARGUMENTS - Description of the feature or bug to plan

## Workflow

### Phase 1: Research (Parallel)

Run three agents simultaneously to gather context:

1. **repo-research-analyst**: Understand project conventions and existing patterns
2. **best-practices-researcher**: Gather external best practices and documentation
3. **framework-docs-researcher**: Research framework-specific guidance

### Phase 2: Determine Detail Level

Choose the appropriate level based on task complexity:

#### MINIMAL
- Ideal for straightforward bugs or small improvements
- Includes: problem statement, basic acceptance criteria, essential context only

#### MORE (Default)
- Suited for most features and complex bugs
- Adds: background, technical considerations, success metrics, dependencies, implementation suggestions

#### A LOT
- For major features and architectural changes
- Provides: phased implementation plans, alternative approaches, extensive specifications, resource requirements, risk mitigation

### Phase 3: Format the Issue

#### Structure
- Proper heading hierarchy
- Syntax-highlighted code blocks
- Task lists for trackable items
- Collapsible sections for lengthy content

#### Cross-References
- Issue numbers (#)
- Commit SHAs
- GitHub permalinks

### Phase 4: AI Development Considerations

When applicable, include:
- Which tools assisted research
- Emphasis on comprehensive testing
- Flag AI-generated code requiring human review

## Pre-Submission Checklist

- [ ] Searchable title
- [ ] Accurate labels
- [ ] Working references
- [ ] Measurable acceptance criteria
- [ ] ERD diagrams for data model changes (optional)

## Output

Create the issue using the GitHub CLI or output formatted markdown for manual creation.
