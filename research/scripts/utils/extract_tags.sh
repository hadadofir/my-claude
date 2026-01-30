#!/bin/bash

# Extracts all unique tags from topic READMEs
# Usage: ./extract_tags.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESEARCH_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
TOPICS_DIR="$RESEARCH_DIR/topics"

echo "Tags in use:"
echo "------------"

grep -rh "Tags:" "$TOPICS_DIR"/*/README.md 2>/dev/null | \
    grep -oE '#[a-zA-Z0-9-]+' | \
    sort | uniq -c | sort -rn

