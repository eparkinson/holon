# Agent Collaboration Styles

This document outlines the different patterns for agent collaboration and context sharing in Holon networks. These patterns define how agents communicate, make decisions, and share information within a network.

---

## Context Sharing Patterns

Context sharing determines what conversation history and information each agent can access.

### 1. Isolated (Default)

**Use Case:** Independent agents with no need to share context.

**Behavior:** Each agent maintains its own conversation history and cannot see other agents' interactions.

**Metadata:**
```yaml
# No additional metadata needed - this is the default
context_mode: isolated
```

**Example:** Simple chatbot, standalone calculator agent.

---

### 2. Pipeline

**Use Case:** Sequential workflows where each agent builds on the previous one's output.

**Behavior:** Each agent receives only the output from its immediate upstream agent(s). No access to full conversation history.

**Metadata:**
```yaml
# Implicit through downstream relationships
context_mode: pipeline
```

**Example:** Research → Writer → Editor pipeline.

---

### 3. Hierarchical

**Use Case:** Manager-worker pattern where a coordinating agent needs visibility into subordinate work.

**Behavior:** Manager agent maintains full context of its own conversations plus read access to downstream agents' outputs. Downstream agents remain isolated from each other.

**Metadata:**
```yaml
context_mode: hierarchical
context_access:
  - self
  - architect  # Can read architect's interactions
  - po         # Can read po's interactions
```

**Example:** Engineering manager overseeing architect and product owner.

---

### 4. Shared Pool

**Use Case:** Team collaboration where all members need visibility into the full discussion.

**Behavior:** All agents in the network share a common context pool. Any agent can see the entire conversation history.

**Metadata:**
```yaml
context_mode: shared
context_pool: design_session  # Named pool identifier
```

**Example:** Design review meeting with multiple specialists.

---

### 5. Selective Sharing

**Use Case:** Complex networks where specific agents need to share context but remain isolated from others.

**Behavior:** Agents explicitly declare which other agents' contexts they can access.

**Metadata:**
```yaml
context_mode: selective
context_access:
  - self
  - security_agent  # Can see security agent's context
  - compliance_agent  # Can see compliance agent's context
```

**Example:** Architect needing to reference security and compliance requirements.

---

## Collaboration Patterns

Collaboration patterns define how multiple agents interact to make decisions or produce outputs.

### 1. Command & Control (Default)

**Use Case:** Clear hierarchy where one agent delegates to others.

**Behavior:** A primary agent receives input, delegates tasks to downstream agents, and consolidates their responses.

**Metadata:**
```yaml
collaboration: command
downstream:
  - architect
  - po
```

**Flow:**
```
User → Manager → [Architect, PO] → Manager → User
```

**Example:** Project manager delegating to specialists.

---

### 2. Consensus / Round Table

**Use Case:** Democratic decision-making among peer agents.

**Behavior:** All agents discuss and must reach agreement (or threshold) before proceeding. Multiple rounds of discussion possible.

**Metadata:**
```yaml
collaboration: consensus
peers:
  - architect
  - tech_lead
  - security_expert
consensus_threshold: 0.66  # 66% agreement required
max_rounds: 3              # Maximum discussion rounds
```

**Flow:**
```
User → Topic → [Round 1: All agents discuss] → [Round 2: Refine] → Consensus → User
```

**Example:** Architecture review board making design decisions.

---

### 3. Parallel Process & Merge

**Use Case:** Independent work streams that need to be combined.

**Behavior:** Multiple agents work simultaneously on the same input, then outputs are merged using a strategy.

**Metadata:**
```yaml
collaboration: parallel
downstream:
  - architect
  - po
  - tech_lead
merge_strategy: aggregate  # Options: aggregate, vote, best_of, synthesize
```

**Merge Strategies:**
- `aggregate`: Combine all outputs into structured sections
- `vote`: Select the best output via voting (requires criteria)
- `best_of`: Use quality scoring to select top output
- `synthesize`: Create new output combining best elements

**Example:** Multiple researchers providing information on different aspects of a topic.

---

### 4. Peer Review

**Use Case:** Quality assurance through staged reviews.

**Behavior:** Primary agent produces output, which is then reviewed by one or more reviewers. May iterate until approval.

**Metadata:**
```yaml
collaboration: review
reviewers:
  - senior_architect
  - security_expert
max_iterations: 2
approval_threshold: 1  # All reviewers must approve
```

**Flow:**
```
User → Producer → Reviewer(s) → [Approve/Reject] → [If reject: iterate] → User
```

**Example:** Code review, document approval workflows.

---

### 5. Debate / Adversarial

**Use Case:** Explore different perspectives to reach robust conclusions.

**Behavior:** Agents take opposing positions and debate. A moderator synthesizes the discussion.

**Metadata:**
```yaml
collaboration: debate
participants:
  - optimist_agent
  - critic_agent
  - realist_agent
moderator: synthesis_agent
rounds: 3
```

**Flow:**
```
User → Topic → [Debate Round 1] → [Debate Round 2] → [Debate Round 3] → Moderator Synthesis → User
```

**Example:** Investment decision analysis, risk assessment.

---

### 6. Sequential Chain

**Use Case:** Assembly line processing with strict ordering.

**Behavior:** Each agent processes and passes to the next in a predefined sequence.

**Metadata:**
```yaml
collaboration: sequential
chain:
  - researcher
  - writer
  - editor
  - publisher
```

**Flow:**
```
User → Agent1 → Agent2 → Agent3 → Agent4 → User
```

**Example:** Content creation pipeline.

---

## Combining Patterns

Patterns can be combined for sophisticated workflows:

### Example: Hierarchical Manager with Consensus Team

```yaml
# manager.md
---
id: manager
type: agent
model: o1-preview
trigger:
  type: chat
collaboration: command
context_mode: hierarchical
downstream:
  - design_team
  - implementation_team
---

# design_team.md
---
id: design_team
type: agent
model: claude-3-5-sonnet
collaboration: consensus
context_mode: shared
context_pool: design_discussion
peers:
  - architect
  - ux_designer
  - product_owner
consensus_threshold: 0.75
max_rounds: 2
---
```

**Flow:**
```
User → Manager → Design Team (consensus) → Manager
              ↓
              → Implementation Team → Manager → User
```

---

## Implementation Notes

### Phase 1 (Current POC)
- ✅ **Isolated** context (default single-agent behavior)
- ✅ **Command** collaboration (implicit in current samples)

### Phase 2 (Planned)
- **Pipeline** context via downstream relationships
- **Hierarchical** context for manager patterns
- **Parallel** collaboration with basic aggregation

### Phase 3 (Future)
- **Shared Pool** context with named pools
- **Consensus** collaboration with voting mechanisms
- **Review** collaboration with approval workflows
- **Debate** collaboration with turn management

### Phase 4 (Advanced)
- **Selective** context with fine-grained permissions
- Advanced merge strategies (synthesize, vote, best_of)
- Dynamic collaboration pattern switching
- Custom collaboration patterns via plugins

---

## Best Practices

1. **Start Simple:** Begin with isolated/pipeline contexts and command collaboration. Add complexity only when needed.

2. **Match Pattern to Use Case:**
   - Hierarchical tasks → Command collaboration
   - Expert panels → Consensus collaboration
   - Quality assurance → Review collaboration
   - Decision analysis → Debate collaboration

3. **Context Efficiency:** Shared contexts consume more tokens. Use selective sharing to reduce costs.

4. **Limit Rounds:** Set reasonable `max_rounds` limits to prevent endless loops and control costs.

5. **Clear Roles:** In consensus/debate patterns, ensure each agent has a distinct perspective or expertise area.

6. **Test Incrementally:** Validate simple networks before adding complex collaboration patterns.

---

## Future Considerations

- **Dynamic Routing:** Agents that can choose which downstream agent to invoke based on context
- **Conditional Collaboration:** Switch collaboration patterns based on task complexity
- **Learning Patterns:** Agents that improve collaboration based on past outcomes
- **External Integration:** Collaboration with human reviewers or external systems
