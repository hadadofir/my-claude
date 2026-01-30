# Tool Usage Guide

Best practices for research tools and techniques.

## Web Search

### When to Use
- Initial landscape mapping
- Finding recent developments
- Locating primary sources
- Checking current consensus

### Best Practices
- Use specific, targeted queries
- Try multiple phrasings for important searches
- Check publication dates
- Prefer authoritative domains (.edu, .gov, established institutions)
- Cross-reference claims across multiple sources

### Limitations
- May miss paywalled academic content
- Results can be SEO-gamed
- Recent events may have incomplete coverage

## Web Fetch

### When to Use
- Reading specific articles or documentation
- Extracting structured information from known URLs
- Following up on search results

### Best Practices
- Verify URL credibility before deep reading
- Extract key points rather than reading everything
- Save important content to `sources/` folder

## Sub-Agents

### Explore Agent
**Use for**: Understanding codebase structure, finding files, answering "where is X" questions
**Best for**: Technical research involving code

### Critic Agent (via Task tool)
**Use for**: Challenging conclusions, finding gaps, stress-testing arguments
**Prompt pattern**: "Review this research and identify weaknesses, gaps, and counterarguments: [summary]"

### Research Agent (via Task tool)
**Use for**: Parallel research on sub-topics
**Best for**: Breaking large topics into independent pieces

## File Organization

### Sources Folder
- Save raw notes with source URLs
- Use descriptive filenames: `[source-type]_[topic]_[date].md`
- Include credibility assessment

### Outputs Folder
- One file per format type
- Use templates from `_templates/`
- Include generation date and confidence levels

## Search Strategies

### Breadth-First
1. General query to map landscape
2. Identify key terms and subtopics
3. Targeted queries for each subtopic

### Depth-First
1. Start with authoritative source
2. Follow references
3. Read cited works

### Adversarial
1. Find mainstream view
2. Explicitly search for critics
3. Search for "[topic] criticism" or "[topic] problems"
