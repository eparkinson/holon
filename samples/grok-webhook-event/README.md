# Grok Webhook Event Handler

## Overview
A specialized event handler that uses Grok (xAI) to analyze social media events received via webhook. Demonstrates constrained prompts and structured output formatting.

## Purpose
- **Syntax Exploration**: Shows webhook triggers, constrained system prompts, and structured JSON output
- **Testing**: Can validate event-driven workflows and agent response formatting
- **Documentation**: Example of production-ready event processing

## Configuration Highlights

### Trigger
- **Type**: `webhook` - HTTP POST endpoint
- **Route**: `/api/v1/events/social-alert` - Specific event endpoint
- **Auth**: Token-based authentication using environment variable
- **Schema**: Documents expected payload structure

### Resources
- **Agent**: Grok Beta (xAI) - Specialized in X (Twitter) real-time data
- **System Prompt**: Heavily constrained with:
  - Clear behavioral rules (fact-focused, no speculation)
  - Required output format (JSON schema)
  - Specific analysis dimensions (sentiment, topics, influence, risk)
  - Action recommendations

### Workflow
- **Step 1**: Agent analyzes event using constrained prompt
- **Step 2**: Validates and formats JSON response with metadata envelope

## Use Case
This configuration would be used for:
1. Social media monitoring systems that detect brand mentions
2. Crisis management systems watching for negative sentiment spikes
3. Influence tracking for marketing campaigns
4. Misinformation detection pipelines

## Example Webhook Call

```bash
curl -X POST https://holon-engine.example.com/api/v1/events/social-alert \
  -H "Authorization: Bearer YOUR_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "brand_mention",
    "event_id": "evt_123abc",
    "timestamp": "2024-01-15T14:30:00Z",
    "content": "Just tried @BrandName new product and it is amazing! #Innovation #TechReview",
    "metadata": {
      "platform": "twitter",
      "author": "@TechInfluencer",
      "followers": 50000,
      "engagement": 120
    }
  }'
```

## Example Response

```json
{
  "event_id": "evt_123abc",
  "processed_at": "2024-01-15T14:30:02Z",
  "handler": "grok-social-analyst",
  "status": "completed",
  "analysis": {
    "sentiment": "POSITIVE",
    "confidence": 0.92,
    "key_topics": ["product launch", "innovation", "tech review"],
    "trending_hashtags": ["#Innovation", "#TechReview"],
    "influential_accounts": ["@TechInfluencer"],
    "misinformation_risk": "LOW",
    "summary": "Highly positive product review from tech influencer with strong engagement. Authentic sentiment from verified source.",
    "recommended_action": "ENGAGE"
  }
}
```

## Notes
- The constrained prompt ensures consistent, structured output
- JSON validation prevents malformed responses
- Environment variables keep credentials secure
- The webhook pattern enables integration with external monitoring tools
