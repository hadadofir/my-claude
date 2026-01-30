# Research Hub

A structured knowledge base for researching topics and generating learning materials.

## Structure

| Directory | Purpose |
|-----------|---------|
| `_playbook/` | Research methodology and best practices |
| `_meta/` | Cross-topic indexing, tags, and shared insights |
| `_templates/` | Output format templates for consistency |
| `scripts/` | Automation tools for common tasks |
| `skills/` | Reusable prompts for research tasks |
| `topics/` | Individual research topics |

## Quick Start

1. **New topic**: Run `./scripts/new_topic.sh <topic-name>` or ask Claude to create one
2. **Research**: Work interactively or use scripts to gather sources
3. **Generate outputs**: Create summaries, flashcards, deep-dives using templates
4. **Cross-reference**: Tag topics and update `_meta/` for synthesis

## Workflow

```
1. Define topic → 2. Gather sources → 3. Analyze → 4. Generate outputs → 5. Tag & index
```

## Topic Folder Structure

Each topic in `topics/` follows this structure:
```
topics/[topic-name]/
├── README.md       # Overview, status, key takeaways
├── sources/        # Raw notes, links, references
├── outputs/        # Generated learning materials
└── artifacts/      # Diagrams, code samples, images
```
