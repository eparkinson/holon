# Multi-Agent Intelligence Summary

## Overview
A sophisticated three-agent workflow that demonstrates the "Scatter-Gather" pattern: Gemini and Grok analyze text in parallel, then Claude synthesizes their findings into a unified summary. Results are sent back via a webhook callback.

## Purpose
- **Syntax Exploration**: Demonstrates scatter-gather parallelism, multi-agent coordination, and webhook callbacks
- **Testing**: Validates parallel task execution and result aggregation
- **Documentation**: Production-grade example of collaborative intelligence

## Configuration Highlights

### Trigger
- **Type**: `webhook` with reply-to callback pattern
- **Payload**: Includes `reply_to_url` for asynchronous response delivery
- **Use Case**: Long-running analysis that responds asynchronously

### Resources
Three specialized agents with distinct roles:

1. **Gemini (Technical Analyst)**
   - Focus: Technical accuracy, clarity, structure
   - Model: gemini-1.5-pro
   - Strength: Multimodal analysis, web grounding

2. **Grok (Social Analyst)**
   - Focus: Tone, sentiment, audience, trends
   - Model: grok-beta
   - Strength: Real-time social context from X (Twitter)

3. **Claude (Chief Intelligence Officer)**
   - Focus: Synthesis and actionable recommendations
   - Model: claude-3-5-sonnet
   - Strength: Long context, reasoning, synthesis

### Workflow Architecture

```
Input Text
    |
    v
[Scatter-Gather]
    ├─> [Gemini: Technical Analysis]
    └─> [Grok: Social Analysis]
         |
         v
    [Claude: Synthesis]
         |
         v
    [HTTP POST to reply_to_url]
```

**Step 1**: Parallel Analysis (Scatter-Gather)
- Both agents receive the same text
- They analyze from different perspectives simultaneously
- Results are collected when both complete

**Step 2**: Synthesis
- Claude receives both analysis outputs
- Identifies consensus and contradictions
- Creates actionable recommendations

**Step 3**: Callback
- Complete analysis posted to `reply_to_url`
- Includes all three outputs for transparency

## Use Cases

1. **Content Review Pipeline**: Analyze blog posts, marketing copy, or documentation
2. **Compliance Checking**: Ensure content meets technical AND social standards
3. **Risk Assessment**: Identify both technical flaws and social backlash risks
4. **Quality Assurance**: Multi-dimensional validation before publication

## Example Webhook Call

```bash
curl -X POST https://holon-engine.example.com/api/v1/analyze/text \
  -H "Authorization: Bearer YOUR_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_789xyz",
    "text": "We are excited to announce our new AI-powered feature that will revolutionize how you work. Using cutting-edge machine learning, we can now predict your needs before you even know them!",
    "reply_to_url": "https://your-app.example.com/api/callbacks/analysis",
    "metadata": {
      "content_type": "marketing_copy",
      "target_audience": "enterprise_users",
      "channel": "email_campaign"
    }
  }'
```

## Example Response (Sent to reply_to_url)

```json
{
  "request_id": "req_789xyz",
  "status": "completed",
  "timestamp": "2024-01-15T14:35:42Z",
  "analysis": {
    "technical": {
      "accuracy": "Medium - Claims are vague and unsubstantiated",
      "clarity": "Low - 'revolutionize' and 'predict needs' lack specificity",
      "recommendations": ["Add concrete examples", "Quantify benefits", "Explain the ML approach"]
    },
    "social": {
      "sentiment": "POSITIVE but potentially concerning",
      "audience_reception": "Privacy-conscious users may be alarmed by 'predict needs before you know them'",
      "recommendations": ["Tone down prediction claims", "Emphasize user control", "Address privacy proactively"]
    },
    "synthesis": {
      "overall_assessment": "Enthusiastic but needs refinement for enterprise audience",
      "key_concerns": [
        "Technical claims lack credibility without evidence",
        "Privacy implications not addressed",
        "Tone may seem overselling to enterprise users"
      ],
      "recommendations": [
        "Replace 'revolutionize' with specific, measurable improvements",
        "Add transparency about data usage and user control",
        "Include customer testimonials or pilot results",
        "Reframe 'predict needs' as 'intelligent suggestions based on your patterns'",
        "Add a FAQ or link addressing privacy and data security"
      ]
    }
  },
  "metadata": {
    "agents_used": ["gemini-1.5-pro", "grok-beta", "claude-3-5-sonnet"],
    "processing_time_ms": 4230
  }
}
```

## Notes

- **Parallelism**: Gemini and Grok run simultaneously, reducing total processing time
- **Transparency**: All three outputs are returned, not just the synthesis
- **Asynchronous**: The reply-to pattern allows for long-running analysis without blocking
- **Scalability**: Can easily add more parallel analyzers (e.g., legal, technical SEO)
- **Error Handling**: (Not shown) Production version should handle agent failures gracefully
