---
id: research-writer-network
type: network
execution_mode: sequential
agents:
  - researcher
  - writer
---

# Research and Writing Network

This network coordinates a researcher and writer to produce high-quality content.

The workflow:
1. **Researcher** agent receives the query and performs web research
2. **Writer** agent takes the research findings and creates a polished article

This demonstrates sequential agent orchestration where the output of one agent
becomes the input to the next agent in the pipeline.
