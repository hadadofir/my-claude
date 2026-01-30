# Reference Sheet Generation Prompt

```
Generate a quick reference for [TOPIC] using the template at _templates/reference.md.

INPUT:
- Completed research outputs
- Practical usage patterns

REQUIREMENTS:
- Fits on one screen (no scrolling for essentials)
- Immediately actionable
- Most common use cases covered
- Copy-pasteable commands/syntax
- Decision tree for common choices
- Top 3-5 gotchas prominently listed

DESIGN PRINCIPLES:
- Optimize for scanning, not reading
- Tables over paragraphs
- Code blocks for anything executable
- Bold key terms

TARGET USER:
Someone who has read the deep dive once and needs quick reminders.
Not for learning, for doing.

OUTPUT: Save to outputs/reference.md
```
