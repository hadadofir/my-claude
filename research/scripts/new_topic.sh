#!/bin/bash

# Creates a new topic folder with standard structure
# Usage: ./new_topic.sh <topic-name>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESEARCH_DIR="$(dirname "$SCRIPT_DIR")"
TOPICS_DIR="$RESEARCH_DIR/topics"
TEMPLATES_DIR="$RESEARCH_DIR/_templates"

if [ -z "$1" ]; then
    echo "Usage: ./new_topic.sh <topic-name>"
    echo "Example: ./new_topic.sh machine-learning"
    exit 1
fi

TOPIC_NAME="$1"
TOPIC_DIR="$TOPICS_DIR/$TOPIC_NAME"

if [ -d "$TOPIC_DIR" ]; then
    echo "Error: Topic '$TOPIC_NAME' already exists at $TOPIC_DIR"
    exit 1
fi

echo "Creating topic: $TOPIC_NAME"

# Create directory structure
mkdir -p "$TOPIC_DIR/sources"
mkdir -p "$TOPIC_DIR/outputs"
mkdir -p "$TOPIC_DIR/artifacts"

# Copy and customize README template
TODAY=$(date +%Y-%m-%d)
sed "s/\[Topic Name\]/$TOPIC_NAME/g; s/\[Date\]/$TODAY/g" \
    "$TEMPLATES_DIR/topic_readme.md" > "$TOPIC_DIR/README.md"

echo "Created topic structure at: $TOPIC_DIR"
echo ""
echo "Next steps:"
echo "1. Edit $TOPIC_DIR/README.md to define your research question"
echo "2. Start gathering sources in $TOPIC_DIR/sources/"
echo "3. Generate outputs using templates in _templates/"

