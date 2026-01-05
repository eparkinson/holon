# Holon

> **Stop Building Tools. Start Orchestrating Services.**

Holon is an open-source **Agent Orchestration Engine** for Higher-Order AI Agents. It allows developers to compose autonomous, "batteries-included" agent services (like Perplexity, Grok, and Jules) into complex workflows using a declarative configuration syntax, rather than writing imperative glue code.

---

## 🧠 The Philosophy

The name comes from Arthur Koestler's systems theory, first introduced in his 1967 book *The Ghost in the Machine*. A **Holon** is something that is simultaneously a *whole* and a *part*.

- **Looking Inward:** An Agent (like Perplexity) is a "Whole." It is autonomous, manages its own tools, and owns its research process.
- **Looking Outward:** In this framework, it acts as a "Part." It submits to a protocol to collaborate with other agents.

Holon treats AI models not as text generators that need to be micromanaged with Python scripts, but as **Microservices** that need to be orchestrated.

---

## ⚡ The Shift

| The Old Way (Legacy Frameworks) | The Holon Way (Federated Architecture) |
|--------------------------------|----------------------------------------|
| **Tool Injection:** You manually code a scraper, a PDF parser, and a search connector. | **Service Routing:** You route the "Research" task to Perplexity, which already knows how to search, scrape, and cite. |
| **Fragile Monolith:** If the scraper breaks, your agent dies. | **Robust Federation:** The Service owns the stack. You just handle the input/output contract. |
| **Imperative Python:** `if agent_a_result then call_agent_b()` | **Declarative YAML:** `type: scatter-gather` |

---

## 🔗 Interfaces & Triggers

A Holon Network is inert until stimulated. Holon provides standard connectors to trigger your agentic workflows via 5 core interfaces. These are defined in your configuration, allowing the same logic to run via CLI, API, or Chat.

### 1. Headless Automation (CLI & Cron)

Run deep research tasks overnight or trigger workflows via CI/CD pipelines.

```yaml
# holon.yaml
trigger:
  type: schedule
  cron: "0 6 * * *" # Run every morning at 6 AM
  input_context: "Daily Market Research for ticker: $NVDA"
```

**Usage:** `holon run workflow.yaml --headless`

### 2. REST API Gateway

Expose your Holon Network as a microservice.

- **Process Mode:** Trigger a specific, rigid workflow (e.g., "Onboarding Flow").
- **Prompt Mode:** Accept a raw prompt and route it dynamically.

```yaml
trigger:
  type: webhook
  route: "/api/v1/analyze"
  auth_token: ${API_SECRET}
```

**Usage:** `POST /api/v1/analyze { "topic": "React 19" }`

### 3. Enterprise ChatOps (Slack / Teams / WhatsApp)

Integrate the Holon Network directly into your team's communication channels. The framework handles the WebSocket connections and message history context.

```yaml
trigger:
  type: adapter
  platform: slack
  channel: "#engineering-intel"
  mode: "mention" # Only wake up when @Holon is tagged
```

### 4. Custom Web Interface

Embed a Holon workflow into your own SaaS or internal dashboard using the React/Vue SDK. Supports streaming responses and "Human-in-the-Loop" pauses.

```yaml
trigger:
  type: websocket
  cors: ["*.mycompany.com"]
```

### 5. Social & Event Watchers

Passive monitoring triggers that wake up the network based on external signals.

```yaml
trigger:
  type: watcher
  source: twitter_stream
  keywords: ["@MyCompany", "MyProduct Bug"]
  action: "trigger_incident_response_workflow"
```

---

## 🚀 Quick Start Configuration

Holon uses **HolonDSL**—a YAML-based schema to define your Agent Organization.

```yaml
version: "1.0"
project: "Market-Intelligence-Brief"

# 1. INPUT INTERFACE
trigger:
  type: slack
  channel: "#market-news"

# 2. THE FEDERATION (The "Wholes")
resources:
  - id: researcher
    provider: perplexity
    model: sonar-reasoning
  - id: sentiment_analyst
    provider: grok
    model: grok-beta
  - id: strategist
    provider: claude
    model: 3-5-sonnet

# 3. THE WORKFLOW (The "Parts")
workflow:
  type: sequential
  steps:
    # SCATTER: Run Research and Social analysis in parallel
    - id: gather_intelligence
      type: scatter-gather
      parallel_tasks:
        - agent: researcher
          instruction: "Find technical specs for {trigger.input}."
        - agent: sentiment_analyst
          instruction: "What is the sentiment regarding {trigger.input}?"
      
    # GATHER & SYNTHESIZE
    - id: draft_strategy
      agent: strategist
      inputs: [gather_intelligence.results]
      instruction: "Draft a strategy report based on these findings."
```

---

## 🏗 Architecture

Holon operates as a **Control Plane** (or *NeuroPlane*) for intelligence.

- **The Gateway:** A unified API adapter that handles the "Handshake" between different providers. It ensures that Grok's output is formatted correctly before being passed to Jules.
- **The Router:** Determines which workflow to trigger based on the input interface (API vs. Slack vs. Cron).
- **The Blackboard:** A shared state manager that allows agents to collaborate asynchronously without direct dependency.

### Supported Patterns

Holon natively supports the 5 Core Collaboration Patterns:

| Pattern | Description |
|---------|-------------|
| **Chain** | Sequential Handoffs |
| **Scatter-Gather** | Parallel execution & synthesis |
| **Debate** | Iterative loops (Builder vs. Critic) for code/security |
| **Blackboard** | Event-driven shared state |
| **Dynamic** | Runtime delegation (The "Manager" decides who to call) |

---

## 🔌 The "Batteries Included" Registry

Holon is built to connect with **Agent Services**, not just LLMs.

| Category | Services |
|----------|----------|
| **Research** | Perplexity, Google Gemini (Grounding) |
| **Coding** | Jules (Google), Devin, GitHub Copilot Workspace |
| **Social** | Grok (xAI) |
| **Data** | Julius AI, ChatGPT Data Analyst |
| **Legal** | Harvey, CoCounsel |
| **Enterprise** | Salesforce Agentforce, Microsoft 365 Copilot |

### 🛠️ Model Context Protocol (MCP) Support

Holon natively supports the **Model Context Protocol (MCP)**. This allows you to mount standard tools (Postgres, GitHub, Slack) to any agent in your workflow without writing custom integration code.

```yaml
resources:
  - id: db_agent
    provider: claude
    model: 3-5-sonnet
    # Connect standard MCP servers
    tools: [postgres_mcp]

  - id: postgres_mcp
    type: mcp-server
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
```

---

## 📂 Project Structure

Holon is organized as a monorepo to ensure unified versioning and atomic updates across the stack.

```text
holon/
├── cli/                 # Python (Typer) - The developer command line tool
│   ├── pyproject.toml
│   └── src/
├── engine/              # Python (FastAPI) - The core orchestration service
│   ├── pyproject.toml
│   └── src/
├── web/                 # React (Vite + DeepChat) - The dashboard & chat UI
│   ├── package.json
│   └── src/
├── samples/             # Example holon.yaml configurations
├── docs/               # Design specifications and architecture docs
└── docker-compose.yaml  # Orchestrates Engine + Web for local dev
```

---

## License

MIT License.

---

> **Holon** — *The Whole is Greater than the Sum of its Parts.*