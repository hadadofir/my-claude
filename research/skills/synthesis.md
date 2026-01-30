# Synthesis Skill

Prompt for finding connections across topics.

## Usage

Periodically run this to discover cross-topic patterns.

---

## Synthesis Prompt Template

```
TASK: Cross-Topic Synthesis

TOPICS TO ANALYZE:
[List topics or "all completed topics"]

PROCESS:
1. Review key takeaways from each topic
2. Look for:
   - Recurring themes or patterns
   - Unexpected connections
   - Contradictions worth exploring
   - Gaps that suggest new research
   - Meta-patterns about knowledge itself

3. Update:
   - _meta/insights.md with findings
   - _meta/glossary.md with shared terms
   - Individual topic READMEs with cross-references

OUTPUT FORMAT:
## Patterns Found
- Pattern: [Description]
  Topics: [List]
  Significance: [Why it matters]

## Connections Discovered
- [Topic A] ↔ [Topic B]: [Nature of connection]

## New Questions
- [Question sparked by synthesis]

## Glossary Additions
- [Term]: [Definition applicable across topics]
```

---

## Periodic Review Prompt

Run monthly or after every 5 topics:

```
Review the research hub and:
1. Identify stale topics needing updates
2. Find orphan topics (no tags, no connections)
3. Suggest topics that would fill knowledge gaps
4. Update _meta/insights.md with any new patterns
5. Clean up or consolidate redundant content
```
