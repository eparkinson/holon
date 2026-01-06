# Holon Configuration Examples

This directory contains sample `holon.yaml` configurations demonstrating various patterns, integrations, and use cases. These examples showcase the Holon DSL syntax and serve as starting points for your own agent workflows.

## 📚 Examples by Complexity

### 🟢 Beginner - Basic Concepts

#### 1. [Basic Gemini Chat](./basic-gemini-chat/)
**Concepts**: Websocket trigger, single agent, simple workflow

The simplest possible configuration - a Gemini agent accessible via web chat interface.
- **Trigger**: WebSocket (real-time chat)
- **Agents**: 1 (Google Gemini)
- **Pattern**: Direct interaction
- **Use Case**: Chat sandbox, interactive assistant

#### 2. [Slack Gemini Chat](./slack-gemini-chat/)
**Concepts**: Chat adapter, platform integration, threading

Same as Basic Gemini but integrated into Slack workspace.
- **Trigger**: Slack adapter (mentions and DMs)
- **Agents**: 1 (Google Gemini)
- **Pattern**: Direct interaction with platform features
- **Use Case**: Team assistant, enterprise chat integration

### 🟡 Intermediate - Multi-Agent Patterns

#### 3. [Grok Webhook Event Handler](./grok-webhook-event/)
**Concepts**: Webhook triggers, constrained prompts, structured output

Event-driven social media analysis with constrained JSON output.
- **Trigger**: Webhook (HTTP POST)
- **Agents**: 1 (xAI Grok)
- **Pattern**: Event processing with structured response
- **Use Case**: Social monitoring, brand tracking, sentiment analysis

#### 4. [Multi-Agent Intelligence Summary](./multi-agent-summary/)
**Concepts**: Scatter-gather pattern, parallel execution, synthesis

Gemini and Grok analyze text in parallel, Claude synthesizes findings.
- **Trigger**: Webhook with reply-to callback
- **Agents**: 3 (Gemini, Grok, Claude)
- **Pattern**: Scatter-Gather (parallel → synthesis)
- **Use Case**: Content review, multi-perspective analysis

#### 5. [Personal Chief of Staff](./assistant/)
**Concepts**: MCP tools, conversational context, multiple integrations

Personal assistant with access to Outlook, Todoist, and filesystem.
- **Trigger**: Slack adapter
- **Agents**: 1 (Claude with MCP tools)
- **Pattern**: Tool-enabled agent
- **Use Case**: Personal productivity, email/calendar management

### 🔴 Advanced - Complex Workflows

#### 6. [Code Review Debate](./code-review-debate/)
**Concepts**: Debate pattern, iterative loops, adversarial collaboration

Builder and Critic engage in multi-round debate, Tech Lead decides.
- **Trigger**: Webhook (GitHub PR)
- **Agents**: 3 (Claude instances with different personas)
- **Pattern**: Debate (iterative adversarial dialogue)
- **Use Case**: Code review, quality assurance, security audit

#### 7. [Data Analyst with MCP Tools](./data-analyst-mcp/)
**Concepts**: Scheduled execution, autonomous workflows, MCP tools

Fully autonomous data analyst that queries databases, generates reports, and sends notifications.
- **Trigger**: Schedule (cron)
- **Agents**: 1 (Claude with PostgreSQL, Filesystem, Slack MCP)
- **Pattern**: Autonomous tool-enabled workflow
- **Use Case**: Daily reporting, business intelligence, automated analysis

#### 8. [Daily News Briefing](./news/)
**Concepts**: Scheduled trigger, map pattern, parallel research

Perplexity and Grok research topics in parallel, Claude compiles a briefing.
- **Trigger**: Schedule (daily at 7 AM)
- **Agents**: 3 (Perplexity, Grok, Claude)
- **Pattern**: Scatter-Gather with Map (parallel research)
- **Use Case**: News aggregation, research automation

## 🎯 Finding the Right Example

### By Trigger Type
- **WebSocket** (Real-time chat): `basic-gemini-chat`
- **Webhook** (HTTP API): `grok-webhook-event`, `multi-agent-summary`, `code-review-debate`
- **Slack Adapter**: `slack-gemini-chat`, `assistant`
- **Schedule** (Cron): `data-analyst-mcp`, `news`

### By Agent Count
- **Single Agent**: `basic-gemini-chat`, `slack-gemini-chat`, `grok-webhook-event`, `data-analyst-mcp`, `assistant`
- **Multiple Agents**: `multi-agent-summary` (3), `code-review-debate` (3), `news` (3)

### By Pattern
- **Direct Interaction**: `basic-gemini-chat`, `slack-gemini-chat`
- **Scatter-Gather** (Parallel): `multi-agent-summary`, `news`
- **Debate** (Iterative): `code-review-debate`
- **Tool-Enabled**: `assistant`, `data-analyst-mcp`

### By Use Case
- **Chat/Conversation**: `basic-gemini-chat`, `slack-gemini-chat`, `assistant`
- **Event Processing**: `grok-webhook-event`
- **Content Analysis**: `multi-agent-summary`, `code-review-debate`
- **Automated Reports**: `data-analyst-mcp`, `news`

## 🛠️ Core Collaboration Patterns

Holon supports 5 core collaboration patterns (see examples):

1. **Chain** (Sequential) - Used in all examples for step sequencing
2. **Scatter-Gather** (Parallel) - `multi-agent-summary`, `news`
3. **Debate** (Iterative) - `code-review-debate`
4. **Blackboard** (Event-driven) - Coming soon
5. **Dynamic** (Runtime routing) - Coming soon

## 📖 Configuration Structure

Every `holon.yaml` follows this structure:

```yaml
version: "1.0"
project: "Your-Project-Name"

# 1. INPUT INTERFACE (How the workflow is triggered)
trigger:
  type: webhook | schedule | adapter | websocket
  # ... trigger-specific config

# 2. THE FEDERATION (Agents and MCP Tools)
resources:
  - id: agent_name
    provider: anthropic | openai | gemini | grok | perplexity
    model: model-name
    tools: [optional_mcp_servers]
    system_prompt: "Optional system context"
  
  - id: mcp_server_name
    type: mcp-server
    command: "npx"
    args: [...]

# 3. THE WORKFLOW (Orchestration Logic)
workflow:
  type: sequential | scatter-gather | debate
  steps:
    - id: step_name
      agent: agent_id
      instruction: "Task for the agent"
```

## 🚀 Getting Started

1. **Browse Examples**: Start with the beginner examples
2. **Read READMEs**: Each example has detailed documentation
3. **Copy & Modify**: Use examples as templates for your use case
4. **Test Locally**: Run with `./scripts/holon_local.sh`
5. **Iterate**: Adjust prompts, add agents, change patterns

## 🧪 Testing These Examples

These configurations are designed for:
- **Syntax Exploration**: Understanding the Holon DSL
- **Testing Infrastructure**: Validating engine features
- **Documentation**: Reference examples for users

**Note**: Examples may not be fully functional out-of-the-box as they:
- Require API keys (set as environment variables)
- May reference non-existent endpoints
- Demonstrate syntax rather than working systems

To make an example work:
1. Set required environment variables (`ANTHROPIC_API_KEY`, etc.)
2. Configure external services (Slack tokens, database connections)
3. Adjust endpoints and credentials as needed

## 📚 Additional Resources

- **[AGENTS.md](../AGENTS.md)**: Agent registry and capabilities
- **[README.md](../README.md)**: Main project documentation
- **[docs/](../docs/)**: Design specifications and architecture

## 💡 Contributing

Want to add a new example? Great! Consider:
- **Novelty**: Does it demonstrate a new pattern or use case?
- **Clarity**: Is it well-documented and easy to understand?
- **Complexity**: Does it fit into the progression (beginner → advanced)?
- **Validity**: Is the YAML syntactically correct?

See contribution guidelines in the main README.

---

**Questions or feedback?** Open an issue or discussion on GitHub.
