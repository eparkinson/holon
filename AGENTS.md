# Holon Agent Registry

In Holon, an **Agent** is not just a prompt wrapper; it is a specialized microservice. We treat Higher-Order AI models as autonomous entities that possess specific capabilities, knowledge bases, and toolsets.

## 1. The Philosophy: "Wholes" and "Parts"

*   **Looking Inward (The Whole):** An agent like **Perplexity** is a complete system. It manages its own crawling, indexing, and citation logic. You don't micromanage *how* it searches; you just ask for the result.
*   **Looking Outward (The Part):** In a Holon workflow, this powerful system becomes a single node in a larger network, passing its intelligence to a "Manager" agent for synthesis.

---

## 2. Agent Categories

We categorize agents based on their primary function in a workflow.

### 🕵️ The Scouts (Intelligence Providers)
These agents are optimized for **fetching external information**. They typically do not support custom tools but have massive internal capabilities.

| Provider | Agent ID | Best For |
|----------|----------|----------|
| **Perplexity** | `perplexity` | Real-time web research, fact-checking, citation. |
| **xAI** | `grok` | Social sentiment analysis, real-time news from X (Twitter). |
| **Google** | `gemini-grounding` | Search with Google Grounding. |

### 👨‍💼 The Executives (Orchestrators & Tool Users)
These agents are optimized for **reasoning, synthesis, and tool use**. They act as the "Brain" of the operation, taking inputs from Scouts and using MCP tools to execute actions.

| Provider | Agent ID | Best For |
|----------|----------|----------|
| **Anthropic** | `claude` | Complex reasoning, coding, large context synthesis. Excellent MCP support. |
| **OpenAI** | `openai` | General purpose reasoning, structured output (JSON). |
| **Google** | `gemini` | Multimodal analysis (Images/Video). |

### 🛠️ The Specialists (Domain Specific)
*Coming Soon* - Agents tuned for specific verticals.
*   **Jules (Google):** Coding & Refactoring.
*   **Harvey:** Legal research and contract analysis.
*   **Salesforce Agentforce:** CRM interaction.

---

## 3. Configuration

Agents are defined in the `resources` section of your `holon.yaml`.

### Basic Configuration
```yaml
resources:
  - id: researcher
    provider: perplexity
    model: sonar-reasoning
```

### Advanced Configuration (with MCP)
You can "mount" Model Context Protocol (MCP) servers to Executive agents, giving them access to your private data and tools.

```yaml
resources:
  - id: chief_of_staff
    provider: anthropic
    model: claude-3-5-sonnet
    # The agent can now "see" and "use" these tools
    tools: [outlook_mcp, filesystem_mcp]

  # Define the MCP Server resource
  - id: outlook_mcp
    type: mcp-server
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-outlook"]
```

---

## 4. Local & Custom Agents (Experimental)

To support development without API costs, Holon supports local inference.

```yaml
resources:
  - id: local_dev_bot
    provider: ollama
    model: llama3
    base_url: "http://localhost:11434"
```

*Note: Local agents may have limited tool-calling capabilities compared to cloud providers.*

---

## 5. Development Guidelines

### Code Formatting and Linting

Before submitting a pull request, ensure your code is properly formatted and linted to avoid CI failures.

#### CLI (Python)

```bash
cd cli

# Install development dependencies
pip install -e .[dev]

# Format code with Black
black src/

# Check formatting (without modifying files)
black --check src/

# Run Ruff linter
ruff check src/

# Run tests
pytest -v
```

#### Engine (Python)

```bash
cd engine

# Install development dependencies
pip install -e .[dev]

# Format code with Black
black src/ tests/

# Check formatting (without modifying files)
black --check src/ tests/

# Run tests
pytest -v
```

#### Integration Tests

```bash
# From repository root
black tests/
black --check tests/
```

**Pro Tip:** Always run `black --check` before committing to catch formatting issues early. The CI pipeline will fail if code is not properly formatted.
