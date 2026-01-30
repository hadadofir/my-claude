# Flashcards Generation Prompt

```
Generate flashcards for [TOPIC] using the template at _templates/flashcards.md.

INPUT:
- Research notes and outputs
- Key concepts to memorize

REQUIREMENTS:
- 10-20 cards for standard topics
- Mix of:
  - Definition cards (What is X?)
  - Explanation cards (Why does X happen?)
  - Application cards (When would you use X?)
  - Comparison cards (What's the difference between X and Y?)
- Progressive difficulty (basic → advanced)
- One concept per card
- Answers should be concise but complete

CARD QUALITY RULES:
- Question should not contain the answer
- Avoid yes/no questions
- Make questions specific, not vague
- Include context if needed to disambiguate

OUTPUT: Save to outputs/flashcards.md
```
