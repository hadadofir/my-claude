# Research Skill

Standard prompt for conducting research on a topic.

## Usage

When starting research on a new topic, use this as a guide.

---

## Research Prompt Template

```
TOPIC: [Topic name]
QUESTION: [Specific question to answer]
DEPTH: [Overview / Working knowledge / Expert-level]
TIME BUDGET: [Quick scan / Standard / Comprehensive]

PROCESS:
1. Read _playbook/methodology.md for process guidance
2. Create topic folder using scripts/new_topic.sh or manually
3. Execute research phases:
   - Scoping: Define boundaries
   - Discovery: Map the landscape
   - Deep Gathering: Collect sources
   - Analysis: Synthesize findings
   - Validation: Run critic sub-agent
   - Output: Generate materials
   - Integration: Update _meta/

QUALITY GATES:
- [ ] Multiple sources consulted
- [ ] Opposing viewpoints sought
- [ ] Critic sub-agent review completed
- [ ] Confidence levels assigned
- [ ] Sources documented

OUTPUT REQUIREMENTS:
- [ ] README.md with overview
- [ ] At least one output format (summary/deep-dive/flashcards/reference)
- [ ] Sources saved with credibility notes
- [ ] Tags assigned
- [ ] _meta/index.md updated
```

---

## Critic Sub-Agent Prompt

After completing research, spawn a sub-agent with:

```
You are a critical reviewer. Your job is to find weaknesses in this research.

RESEARCH SUMMARY:
[Paste summary here]

TASK:
1. Identify unsupported claims
2. Find logical gaps or leaps
3. List counterarguments not addressed
4. Note potential biases
5. Rate overall confidence (High/Medium/Low) with justification
6. Suggest specific improvements

Be rigorous. The goal is to strengthen the research, not validate it.
```
