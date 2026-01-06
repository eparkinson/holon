# Data Analyst with MCP Tools

## Overview
An autonomous data analyst agent that uses Model Context Protocol (MCP) tools to query databases, analyze data, generate reports, and send notifications - all without human intervention. Demonstrates the power of tool-enabled agents.

## Purpose
- **Syntax Exploration**: Shows MCP tool mounting, scheduled triggers, autonomous workflows, and error handling
- **Testing**: Validates MCP integration and tool-calling capabilities
- **Documentation**: Production example of fully autonomous agent workflows

## Configuration Highlights

### Trigger
- **Type**: `schedule` with cron expression
- **Frequency**: Daily at 9 AM
- **Use Case**: Automated reporting, recurring analysis

### Resources

**Agent with MCP Tools**
- **Model**: Claude 3.5 Sonnet (excellent tool-calling capabilities)
- **Tools**: Three MCP servers mounted
- **Autonomy**: Agent decides when and how to use tools

**MCP Servers Mounted**:

1. **PostgreSQL MCP Server**
   - Access to analytics database
   - Read-only mode (safety)
   - Schema restrictions (public, sales only)

2. **Filesystem MCP Server**
   - Save generated reports
   - Restricted to `/app/reports` directory
   - Allowed operations: read, write, list

3. **Slack MCP Server**
   - Send notifications to team channels
   - Post summary messages
   - Alert on critical findings

### Workflow: Full Autonomy

The agent is given a high-level goal and autonomously:
1. Decides which SQL queries to run
2. Interprets the results
3. Generates insights and recommendations
4. Creates a formatted report
5. Saves it to the filesystem
6. Sends a Slack notification

**No human intervention required.**

## The MCP Advantage

### Without MCP (Traditional Approach)
```python
# You write all this code:
connection = psycopg2.connect(DATABASE_URL)
cursor = connection.cursor()
cursor.execute("SELECT * FROM sales WHERE date > NOW() - INTERVAL '7 days'")
data = cursor.fetchall()

# Process data manually
total_sales = sum(row[2] for row in data)

# Format report manually
report = f"# Sales Report\nTotal: ${total_sales}"

# Save file manually
with open(f"report_{date}.md", "w") as f:
    f.write(report)

# Send to Slack manually
slack_client.chat_postMessage(channel="#sales", text="Report ready!")
```

### With MCP (Holon Approach)
```yaml
# Agent autonomously uses tools:
tools: [postgres_mcp, filesystem_mcp, slack_mcp]

# You just give the goal:
instruction: |
  Generate the daily sales analysis report.
  Query the database, create insights, save the report, and notify the team.
```

The agent figures out:
- Which queries to run
- How to analyze the data
- What format to use
- Where to save the file
- What to say in Slack

## Example Agent Execution

### Agent's Internal Workflow

```
[Agent Thinking]
I need to generate a daily sales analysis report.

[Tool Call 1: postgres_mcp]
Query: SELECT date, SUM(amount) as total 
       FROM sales 
       WHERE date > CURRENT_DATE - INTERVAL '7 days'
       GROUP BY date ORDER BY date

[Result]
2024-01-08: $15,234
2024-01-09: $16,890
2024-01-10: $14,567
... (7 days)

[Analysis]
Week-over-week growth: +8.3%
Average daily: $15,832
Anomaly detected: Drop on 2024-01-10 (weekday, unusual)

[Tool Call 2: postgres_mcp]
Query: SELECT product_name, SUM(amount) as revenue
       FROM sales JOIN products ...
       (gets top products)

[Tool Call 3: filesystem_mcp]
Action: write_file
Path: /app/reports/daily/daily_sales_analysis_2024-01-11.md
Content: (Generated markdown report)

[Tool Call 4: slack_mcp]
Action: send_message
Channel: #sales-analytics
Message: "📊 Daily Sales Analysis Ready!
         
         💰 Total Revenue: $110,821 (+8.3% vs last week)
         🏆 Top Product: Widget Pro ($23,450)
         ⚠️ Note: Sales dip on Jan 10th - investigate
         
         Full report: /reports/daily/daily_sales_analysis_2024-01-11.md"
```

## Generated Report Example

```markdown
# Daily Sales Analysis - 2024-01-11

## Executive Summary
- **Total Revenue**: $110,821 (Last 7 days)
- **Growth**: +8.3% vs previous week
- **Average Daily**: $15,832
- **Transaction Count**: 1,247

## Key Insights
✅ Strong overall growth trend continuing
✅ Widget Pro driving significant revenue
⚠️ Anomalous dip on January 10th requires investigation
📈 Customer acquisition up 12% week-over-week

## Detailed Analysis

### Daily Revenue Trend
| Date       | Revenue   | Transactions | Avg Order |
|------------|-----------|--------------|-----------|
| 2024-01-08 | $15,234   | 178          | $85.58    |
| 2024-01-09 | $16,890   | 192          | $87.97    |
| 2024-01-10 | $14,567   | 165          | $88.29    |
| ...        | ...       | ...          | ...       |

### Top 10 Products by Revenue
1. Widget Pro - $23,450 (21.1% of total)
2. Gadget Plus - $18,920 (17.0% of total)
3. ...

## Recommendations
1. **Investigate Jan 10 dip**: Check for technical issues or marketing campaign end
2. **Increase Widget Pro inventory**: High demand, potential stockout risk
3. **Promote Gadget Plus**: Second-best performer, opportunity for bundling
4. **Monitor customer acquisition**: Healthy growth, ensure quality remains high

## SQL Queries Used
```sql
-- Daily Revenue
SELECT date, SUM(amount) as total ...

-- Top Products
SELECT product_name, SUM(amount) ...
```

---
*Report generated automatically by Holon Data Analyst*
*Generated at: 2024-01-11 09:00:32 UTC*
```

## Use Cases

1. **Daily/Weekly Reports**: Automated business intelligence
2. **Anomaly Detection**: Flag unusual patterns automatically
3. **Database Monitoring**: Check data quality, find outliers
4. **Customer Analytics**: Churn analysis, cohort reports
5. **Inventory Management**: Automated stock level analysis
6. **Financial Reporting**: P&L summaries, expense tracking

## Security & Best Practices

### Database Access
- ✅ Use read-only credentials
- ✅ Restrict to specific schemas
- ✅ No DDL operations (CREATE, DROP, ALTER)
- ✅ Connection string in environment variables

### Filesystem Access
- ✅ Restrict to specific directory
- ✅ Limit file operations (no delete by default)
- ✅ Use absolute paths with validation

### Slack Integration
- ✅ Bot token (not user token)
- ✅ Specific channel permissions
- ✅ Rate limiting awareness

## Error Handling

The configuration includes error handling:
- Slack notification to `#alerts` channel
- Logging for debugging
- Graceful degradation (partial reports if some queries fail)

## Extending the Example

Add more MCP tools:
- **GitHub MCP**: Create issues for anomalies
- **Google Sheets MCP**: Export data to spreadsheets
- **Email MCP**: Send reports to stakeholders
- **Jira MCP**: Create tickets for action items

## Notes

- **Autonomy**: The agent makes all decisions about how to complete the task
- **Transparency**: SQL queries and reasoning are included in reports
- **Reliability**: Scheduled execution ensures consistency
- **Scalability**: Add more analyses without code changes
- **Cost**: Monitor API usage (database queries + Claude API calls)
