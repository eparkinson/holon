# Code Review Debate

## Overview
An advanced code review system using the "Debate" pattern - a Builder (constructive) and Critic (skeptical) engage in iterative dialogue, with a Tech Lead making the final decision. Demonstrates multi-round agent interaction.

## Purpose
- **Syntax Exploration**: Shows the Debate pattern, iterative loops, and complex multi-agent coordination
- **Testing**: Validates multi-round workflows and agent state management
- **Documentation**: Production example of adversarial collaboration for quality assurance

## Configuration Highlights

### Trigger
- **Type**: `webhook` receiving pull request data
- **Use Case**: Integration with GitHub, GitLab, or custom CI/CD

### Resources
Three agents with opposing perspectives:

1. **Code Builder** (Constructive)
   - Role: Suggest improvements, best practices
   - Perspective: Optimistic, solution-oriented
   - Output: Actionable improvements with code examples

2. **Security Critic** (Skeptical)
   - Role: Find vulnerabilities and edge cases
   - Perspective: Skeptical, risk-focused
   - Output: Security issues, performance concerns, anti-patterns

3. **Tech Lead** (Judge)
   - Role: Final decision maker
   - Perspective: Balanced, prioritizes concerns
   - Output: APPROVE / REQUEST_CHANGES / COMMENT

### Workflow: The Debate Pattern

The workflow implements an iterative debate:

```
Round 1: Initial Review
    ├─> Builder: Constructive review
    └─> Critic: Security audit
         |
         v
Round 2: Builder Rebuttal
    Builder responds to Critic's concerns
    Provides fixes for valid issues
         |
         v
Round 3: Critic Evaluation
    Critic evaluates Builder's fixes
    Confirms if issues resolved
         |
         v
Final: Tech Lead Decision
    Synthesizes all perspectives
    Makes final call
    Posts review to PR
```

## Why the Debate Pattern?

### Benefits
1. **Higher Quality**: Multiple perspectives catch more issues
2. **Balanced Feedback**: Neither too harsh nor too lenient
3. **Learning**: Builder and Critic challenge each other
4. **Reduced Bias**: No single agent makes the decision
5. **Transparency**: All reasoning is visible

### When to Use
- High-stakes code (security, payments, data handling)
- Critical infrastructure changes
- Public API changes
- Complex algorithms requiring verification

### When NOT to Use
- Simple bug fixes or typos
- Documentation-only changes
- Time-sensitive hotfixes
- Low-risk refactoring

## Example Flow

### Input Code
```python
@app.route('/user/<user_id>')
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return jsonify(result)
```

### Round 1: Initial Reviews

**Builder Review**:
```
IMPROVEMENTS NEEDED:
1. Add error handling for database failures
2. Add type hints for better code clarity
3. Use proper HTTP status codes
4. Add logging for debugging

SUGGESTED CODE:
@app.route('/user/<int:user_id>')
def get_user(user_id: int) -> Response:
    try:
        # ... improved code
```

**Critic Review**:
```
🚨 CRITICAL SECURITY VULNERABILITY - SQL INJECTION
The code is vulnerable to SQL injection (CWE-89).

ISSUE: String interpolation in SQL query allows arbitrary SQL execution
SEVERITY: CRITICAL
CVE REFERENCE: Similar to CVE-2021-XXXXX

EXPLOIT EXAMPLE:
GET /user/1; DROP TABLE users--
```

### Round 2: Builder Rebuttal

```
ACKNOWLEDGED - Critic is correct about SQL injection.

PROPOSED FIX:
Use parameterized queries:
query = "SELECT * FROM users WHERE id = ?"
result = db.execute(query, (user_id,))

This addresses the critical security concern while maintaining functionality.
```

### Round 3: Critic Evaluation

```
PROPOSED FIX: ADEQUATE

The parameterized query resolves the SQL injection vulnerability.

REMAINING CONCERNS:
1. Still missing authentication check
2. No rate limiting
3. Sensitive user data exposure risk

SEVERITY: Medium (original Critical issue resolved)
```

### Final: Tech Lead Decision

```
DECISION: REQUEST_CHANGES

CRITICAL ISSUES (must fix before merge):
✓ SQL injection - Builder's fix approved (parameterized query)
✗ Authentication missing - Add @require_auth decorator
✗ Sensitive data exposure - Filter response fields

RECOMMENDED IMPROVEMENTS (for follow-up):
- Add rate limiting
- Implement proper logging
- Add OpenAPI documentation

APPROVED SUGGESTIONS:
- Error handling from Builder
- Type hints from Builder

SUMMARY:
The SQL injection fix is solid, but authentication must be added before merge.
Consider filtering user data fields to prevent information disclosure.
```

## Integration Example

### GitHub Webhook
```bash
curl -X POST https://holon.example.com/api/v1/code-review \
  -H "Authorization: Bearer SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "pull_request_url": "https://github.com/org/repo/pull/123",
    "code_diff": "...",
    "language": "python",
    "author": "developer",
    "description": "Add user endpoint"
  }'
```

### CI/CD Integration
```yaml
# .github/workflows/code-review.yml
on: pull_request

jobs:
  holon-review:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Holon Review
        run: |
          curl -X POST $HOLON_URL/api/v1/code-review \
            -H "Authorization: Bearer $HOLON_TOKEN" \
            -d @pr_data.json
```

## Notes

- **Cost**: Three Claude API calls + iterative rounds = higher cost
- **Time**: ~30-60 seconds total (parallel + sequential rounds)
- **Quality**: Significantly higher than single-agent review
- **Customization**: Adjust system prompts for your team's standards
- **Scalability**: Consider rate limits for high-volume repos
