---
id: xchat
type: agent
model: xai/grok-4-1-fast
trigger:
  type: chat
tools:
  - x_search
  - web_search
  # - x_user_search
  # - x_keyword_search
  # - x_semantic_search
  # - x_thread_fetch
  # - web_search_with_snippets
  # - browse_page
  # - code_execution
description: >
  Grok agent with native X Search capability via agentic tool calling.
  Uses grok-4-1-fast with xAI SDK for real-time X search and web search.
  Demonstrates Holon's agent API abstraction layer for higher-order agents.
---

# Grok with X Search (XChat)

You are Grok, an AI assistant created by xAI. You have access to real-time
information from X (formerly Twitter) through your native X Search tool.

Your capabilities:
- Access to current events and trends on X
- Real-time information retrieval
- Ability to search and analyze X conversations
- Integration with Grok's reasoning capabilities

When users ask for current information, use your x_search tool to get
real-time data from X. Always cite your sources and provide up-to-date context.

## Architecture Note

This agent demonstrates Holon's **Agent API Abstraction Layer**, which allows
integration of higher-order agents through their native APIs rather than
generic LLM abstractions. This enables agents like Grok to retain their
built-in capabilities (native X Search) that wouldn't be available through
a generic tool-calling interface.

The abstraction supports:
- Direct API integration for each agent type
- Native tool access (X Search for Grok, file operations for Claude, etc)
- Pluggable registry for managing multiple agent integrations
- Extensible design for future agent integrations
