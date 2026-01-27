# Multi-Agent Network Orchestration Guide

This guide explains how to create and run multi-agent networks in Holon, enabling complex workflows where multiple AI agents collaborate autonomously.

## Table of Contents

1. [Overview](#overview)
2. [Network Definition Format](#network-definition-format)
3. [Execution Modes](#execution-modes)
4. [Agent Relationships](#agent-relationships)
5. [Examples](#examples)
6. [HTTP API Usage](#http-api-usage)

## Overview

A Holon network is a coordinated group of agents that work together to accomplish complex tasks. Networks are defined in Markdown files with YAML frontmatter, just like individual agents.

**Key Benefits:**
- **Specialized Expertise**: Each agent can focus on what it does best
- **Parallel Execution**: Run multiple agents simultaneously for faster results
- **Sequential Workflows**: Chain agents together for multi-step processes
- **Reusability**: Compose networks from existing agent definitions

## Network Definition Format

A network is defined using `type: network` in the YAML frontmatter:

```markdown
---
id: research-writer-network
type: network
execution_mode: sequential
agents:
  - researcher
  - writer
---

# Research and Writing Network

This network coordinates research and writing tasks.

1. The researcher finds and analyzes information
2. The writer creates polished content from the research
```

### Required Fields

- **`id`**: Unique identifier for the network
- **`type`**: Must be set to `"network"`
- **`agents`**: List of agent IDs or file paths to include in the network

### Optional Fields

- **`execution_mode`**: How agents execute (default: `sequential`)
  - `sequential`: Agents run one after another
  - `parallel`: All agents run simultaneously
  - `conditional`: Agents run based on conditions (planned)

- **`input_mapping`**: Map network inputs to specific agents
- **`output_mapping`**: Map agent outputs to network outputs

## Execution Modes

### Sequential Execution

Agents execute one at a time, with each agent's output becoming the next agent's input.

```yaml
---
id: pipeline-network
type: network
execution_mode: sequential
agents:
  - data-collector
  - data-analyzer
  - report-generator
---
```

**Use cases:**
- Multi-step data processing pipelines
- Workflows where each step builds on the previous
- Quality control chains (draft → review → finalize)

### Parallel Execution

All agents run simultaneously with the same input, and their outputs are synthesized.

```yaml
---
id: multi-perspective-network
type: network
execution_mode: parallel
agents:
  - technical-analyst
  - business-analyst
  - user-experience-analyst
---
```

**Use cases:**
- Getting multiple perspectives on the same problem
- Parallel research from different sources
- Ensemble approaches for better results

## Agent Relationships

Individual agents can declare their relationships to other agents using `upstream` and `downstream` fields:

```yaml
---
id: researcher
type: agent
model: perplexity-sonar-reasoning
downstream:
  - writer
---
```

```yaml
---
id: writer
type: agent
model: claude-3-5-sonnet
upstream:
  - researcher
---
```

These relationships help the network determine execution order in sequential mode.

## Examples

### Example 1: Research and Writing Pipeline

**Network Definition** (`network.md`):
```markdown
---
id: research-writer-network
type: network
execution_mode: sequential
agents:
  - researcher
  - writer
---

# Research and Writing Network

Coordinates research and content creation for high-quality articles.
```

**Researcher Agent** (`researcher.md`):
```markdown
---
id: researcher
type: agent
model: perplexity-sonar-reasoning
tools:
  - web_search
downstream:
  - writer
---

# Research Assistant

You are an autonomous research assistant.
Use your web_search tool to find accurate, recent information.
Output your findings as structured bullet points with citations.
```

**Writer Agent** (`writer.md`):
```markdown
---
id: writer
type: agent
model: claude-3-5-sonnet
upstream:
  - researcher
---

# Technical Writer

You are a skilled technical writer.
Transform research findings into polished, engaging content.
Maintain accuracy while making complex topics accessible.
```

**Running the Network:**
```bash
holon test network.md
```

### Example 2: Parallel Analysis Network

**Network Definition:**
```markdown
---
id: multi-analyst-network
type: network
execution_mode: parallel
agents:
  - security-analyst
  - performance-analyst
  - code-quality-analyst
---

# Code Review Network

Performs comprehensive code review from multiple perspectives simultaneously.
```

This executes all three analysts in parallel and combines their insights.

### Example 3: Complex Business Intelligence Network

```markdown
---
id: business-intelligence-network
type: network
execution_mode: sequential
agents:
  - data-collector
  - trend-analyzer
  - report-generator
  - stakeholder-communicator
---

# Business Intelligence Pipeline

End-to-end business intelligence workflow:
1. Collect data from various sources
2. Analyze trends and patterns
3. Generate comprehensive reports
4. Communicate insights to stakeholders
```

## HTTP API Usage

Networks can be deployed as production services using the HTTP API server:

### Starting the Server

```bash
holon serve /path/to/agents --host 0.0.0.0 --port 8000
```

### Execute a Network via API

```bash
curl -X POST "http://localhost:8000/networks/research-writer-network/execute" \
  -H "Content-Type: application/json" \
  -d '{"input": "Write an article about quantum computing"}'
```

**Response:**
```json
{
  "output": "# Quantum Computing: The Future of Computation\n\n...",
  "network_id": "research-writer-network",
  "execution_id": "research-writer-network_2024-01-27T10:30:00",
  "agent_outputs": {
    "researcher": "Key findings about quantum computing:\n- Superposition allows...",
    "writer": "# Quantum Computing: The Future of Computation\n\n..."
  },
  "timestamp": "2024-01-27T10:30:15.123Z"
}
```

### List Available Networks

```bash
curl http://localhost:8000/networks
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Best Practices

1. **Keep Agents Focused**: Each agent should have a clear, specific role
2. **Use Sequential for Dependencies**: When output of one agent feeds another
3. **Use Parallel for Independence**: When agents analyze the same input differently
4. **Document Workflows**: Explain the network's purpose in the markdown body
5. **Test Individually First**: Verify each agent works before combining into networks
6. **Handle Errors Gracefully**: Networks continue even if individual agents fail

## Troubleshooting

### Network Won't Load

- Ensure all referenced agents exist and are valid
- Check that agent IDs match the referenced names
- Verify YAML frontmatter is properly formatted

### Sequential Execution Order Wrong

- Check `upstream`/`downstream` relationships in agent definitions
- Ensure there are no circular dependencies
- Remember: agents without dependencies execute first

### Parallel Execution Too Slow

- Check if agents are CPU/memory intensive
- Consider rate limits on API calls
- Monitor network latency for remote services

## Advanced Topics

### Custom Output Synthesis

When using parallel execution, the network synthesizes outputs by concatenating them with headers. You can customize this by implementing custom synthesis logic in your network runtime.

### State Sharing

Agents in a network can share state through the network's execution context. This is automatically managed by the NetworkRuntime.

### Conditional Execution

Conditional execution mode (planned) will allow agents to run based on the results of previous agents, enabling dynamic workflows.

## Next Steps

- Explore the [sample networks](../tests/samples/02_collaborators/)
- Learn about [agent deployment](deployment.md)
- Read the [API documentation](api.md)
- See the [complete roadmap](PLAN.md)
