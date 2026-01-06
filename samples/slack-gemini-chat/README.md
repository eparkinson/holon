# Slack Gemini Assistant

## Overview
A Gemini-powered AI assistant that integrates directly into Slack, responding to mentions and direct messages in your workspace.

## Purpose
- **Syntax Exploration**: Demonstrates chat adapter configuration, thread handling, and platform-specific formatting
- **Testing**: Validates Slack integration and conversational workflows
- **Documentation**: Real-world example of enterprise chat integration

## Configuration Highlights

### Trigger
- **Type**: `adapter` with platform `slack`
- **Channel**: Specific channel (`#ai-assistant`) or workspace-wide
- **Mode**: `mention` - Only responds when @mentioned (reduces noise)
- **Features**:
  - Thread responses keep conversations organized
  - Typing indicator provides user feedback
  - Direct message support for private queries

### Resources
- **Agent**: Google Gemini 1.5 Pro
- **System Prompt**: Tailored for Slack environment
  - Professional but friendly tone
  - Slack markdown formatting
  - Concise responses (Slack users prefer brevity)
  - Context-aware (knows it's in a work chat)

### Workflow
**Step 1**: Process the message
- Agent receives message content
- Includes thread context if responding in a thread
- User information for personalization

**Step 2**: Log interaction (optional)
- Analytics for usage tracking
- Helps measure adoption and effectiveness

## Use Cases

1. **Team Assistant**: Answer questions, provide definitions, explain concepts
2. **Brainstorming Partner**: Help teams ideate and problem-solve
3. **Writing Helper**: Draft messages, improve copy, check grammar
4. **Knowledge Base**: Quick answers without leaving Slack
5. **Onboarding Support**: Help new team members get up to speed

## Setup Requirements

### Slack App Configuration
You'll need to create a Slack App with:
- **Bot Token Scopes**:
  - `chat:write` - Send messages
  - `channels:history` - Read channel messages
  - `groups:history` - Read private channel messages  
  - `im:history` - Read direct messages
  - `app_mentions:read` - Detect @mentions
  - `users:read` - Get user information

- **Event Subscriptions**:
  - `app_mention` - When @mentioned
  - `message.im` - Direct messages to bot

- **Environment Variables**:
  ```bash
  SLACK_BOT_TOKEN=xoxb-your-bot-token
  SLACK_SIGNING_SECRET=your-signing-secret
  ```

## Example Interactions

### Mention in Channel

**User**: `@GeminiBot what's the difference between REST and GraphQL?`

**Bot Response** (in thread):
```
Great question! Here's a quick comparison:

*REST (Representational State Transfer)*:
• Multiple endpoints for different resources
• Standard HTTP methods (GET, POST, PUT, DELETE)
• Can lead to over-fetching or under-fetching data

*GraphQL*:
• Single endpoint for all queries
• Client specifies exactly what data it needs
• Reduces over-fetching and round trips

*When to use REST*: Simple CRUD operations, caching important
*When to use GraphQL*: Complex data requirements, mobile apps

Need me to dive deeper into any aspect?
```

### Direct Message

**User**: `Can you help me write a professional out-of-office message?`

**Bot Response**:
```
Of course! Here's a template you can customize:

_Subject: Out of Office - [Your Name]_

Thank you for your email. I am currently out of office from [Start Date] to [End Date] with limited access to email.

*For urgent matters:*
• Please contact [Backup Person] at [email/slack]

*For non-urgent matters:*
• I will respond when I return on [Return Date]

Best regards,
[Your Name]

Want me to adjust the tone or add anything specific?
```

### Thread Response

**User**: `@GeminiBot explain dependency injection`

**Bot**: _(Initial explanation)_

**User**: `Can you give a Python example?`

**Bot**: _(Provides Python code example, maintaining thread context)_

## Slack Formatting Reference

The bot uses Slack's markdown formatting:
- `*bold*` for emphasis
- `_italic_` for subtle emphasis
- `` `code` `` for inline code
- ````code block```` for multi-line code
- `• Bullet points` for lists
- `> Blockquotes` for quotes

## Benefits Over Direct LLM Access

1. **Context**: Integrated into team's workflow
2. **Shared**: Entire team can benefit from responses
3. **Discoverable**: Conversations are searchable in Slack
4. **Permissioned**: Respects Slack's access controls
5. **Threaded**: Keeps workspace organized

## Notes

- The bot only responds when mentioned (reduces spam)
- Thread context is maintained for multi-turn conversations
- Analytics logging helps track usage and ROI
- Can be extended with tools (calendar, docs, etc.) via MCP
