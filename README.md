# Holon: Orchestrating AI Agents with Markdown Simplicity

**Holon is an open-source Agent Orchestration Engine for Higher-Order AI Agents.**

The landscape of AI automation is evolving rapidly. As our systems become more capable, the challenge is shifting from “how do I use this tool?” to “how can I make all these tools and agents work together?” Holon is built to answer that question—with a focus on **developer experience, transparency, and the power of simple text files**.

## The Vision

**Holon** isn’t just another AI framework. It’s a rethink of how we design, share, and orchestrate AI agents. Instead of wrangling imperative glue code and endless pipelines, Holon lets you define networks of autonomous agents **using nothing more than Markdown documents with YAML metadata**.

### Why Markdown + YAML?

- **Human-Readable:** Your agent’s goals, behaviors, and prompts live alongside its config, in plain English.
- **Portable:** One file contains both documentation and executable specification.
- **Extensible:** Add prompt examples, usage notes, diagrams, and more—your format is as simple or rich as you need.
- **LLM-Ready:** Rich Markdown context enables better utilization and understanding by LLMs themselves.

## 🧠 The Philosophy

The name comes from Arthur Koestler's systems theory, first introduced in his 1967 book *The Ghost in the Machine*. A **Holon** is something that is simultaneously a *whole* and a *part*.

- **Looking Inward:** An Agent (like Perplexity) is a "Whole." It is autonomous, manages its own tools, and owns its research process.
- **Looking Outward:** In this framework, it acts as a "Part." It submits to a protocol to collaborate with other agents.

Holon treats AI models not as text generators that need to be micromanaged with Python scripts, but as **Microservices** that need to be orchestrated.

**The Shift**

| The Old Way (Legacy Frameworks) | The Holon Way (Federated Architecture) |
|--------------------------------|----------------------------------------|
| **Tool Injection:** You manually code a scraper, a PDF parser, and a search connector. | **Service Routing:** You route the "Research" task to Perplexity, which already knows how to search, scrape, and cite. |
| **Fragile Monolith:** If the scraper breaks, your agent dies. | **Robust Federation:** The Service owns the stack. You just handle the input/output contract. |
| **Imperative Python:** `if agent_a_result then call_agent_b()` | **Declarative YAML:** `type: scatter-gather` |

## How Does It Work?

A Holon agent or network is described with a Markdown file containing structured YAML frontmatter:

```markdown
---
id: analyst
type: agent
model: claude-3-5-sonnet
trigger:
  type: schedule
  cron: "0 9 * * *"
tools:
  - postgres_mcp
  - slack_mcp
---

# Data Analyst Agent

You’re an autonomous agent responsible for generating daily business intelligence reports, sharing insights with stakeholders via Slack...
```

- **Frontmatter:** Machine-parsable metadata (id, model, trigger, etc).
- **Markdown Body:** Prompts, goals, instructions, examples—everything the agent needs to know and everything a human needs to understand.

## ⚡ Quick Start

Getting your agent network live is as simple as publishing a blog post.

**1. Install the CLI**

```bash
pip install holon
```

**2. Save your Plan**

Copy the example agent above and save it as `analyst.md`.

**3. Deploy**

```bash
holon deploy analyst.md
```

Holon parses your markdown instructions, checks the required tools, and launches the agent. You'll instantly get a live endpoint and a dashboard to watch your analyst go to work.

## 🏗️ High-Level Architecture

When you run `holon deploy`, the system performs a key transformation: it compiles your Markdown specifications into a robust execution environment.

- **Single Docker Container:** The Holon CLI builds a comprehensive Docker container that encapsulates your entire agent network, runtime dependencies, and tool connectors.
- **Local Execution:** You can run this container purely locally. This means you can test complex agent interactions on your machine with zero cloud latency or cost.
- **Remote Deployment:** Because it's just a standard container, you can deploy your Holon network anywhere—AWS ECS, Google Cloud Run, a DigitalOcean Droplet, or your customized VPS.

Your agent network becomes a single, portable artifact that behaves exactly the same in production as it does on your laptop.

## A Clean Start

This new version of Holon starts from a blank slate. We’ve kept only the essentials so you can shape your agent network, workflows, and knowledge in a format that’s as easy to write as your favorite blog post.

> **Stop Building Glue Code. Start Writing Intelligence.**

---

Ready to help shape the future of agent orchestration? [Get started with Holon](https://github.com/eparkinson/holon), explore example agents, or contribute your own!
