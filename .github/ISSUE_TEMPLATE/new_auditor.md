---
name: New Auditor Proposal
about: Propose a new system or package auditor
title: '[AUDITOR] '
labels: enhancement, auditor
assignees: ''
---

## Auditor Name
What should this auditor be called?

## Auditor Type
- [ ] System Auditor (OS-level security/health)
- [ ] Package Auditor (language/framework packages)
- [ ] Tool Auditor (development tools)
- [ ] Other: ___________

## What Does It Check?
What specific security or health aspect does this auditor monitor?

## Why Is This Important?
What risks does this address? Who needs this?

## Platform Support
Which platforms would this work on?
- [ ] Windows
- [ ] macOS
- [ ] Linux

## Data Sources
How would this auditor collect information?
- Commands to run: `example command`
- Files to read: `/path/to/file`
- APIs to query: `API endpoint`

## Educational Value
What would users learn from this auditor's findings?

## Example Output
What would a finding look like?
```
Example security finding or health status
```

## Risk Assessment
How would this auditor classify risk levels?
- Critical: When X happens
- High: When Y happens
- Medium: When Z happens
- Low: Normal operation

## Implementation Checklist
- [ ] Inherits from `BaseAuditor`
- [ ] Cross-platform or platform-specific
- [ ] Educational content in `docs/concepts/`
- [ ] Unit tests included
- [ ] Follows BIOS auditor template

## Related Auditors
Does this relate to or depend on existing auditors?

## Additional Context
Links, research, or examples
