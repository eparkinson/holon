#!/bin/bash
# Phase 1 Validation Script
# This script runs all the sanity checks described in docs/tasks/01-phase.md

set -e

echo "========================================"
echo "Phase 1 Implementation Validation"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PASS_COUNT=0
TOTAL_COUNT=0

function test_check() {
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    echo -n "[$TOTAL_COUNT] $1... "
}

function test_pass() {
    PASS_COUNT=$((PASS_COUNT + 1))
    echo -e "${GREEN}✓ PASS${NC}"
}

function test_fail() {
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Error: $1"
}

# Test 1: Version Command
test_check "Version command"
if holon version > /dev/null 2>&1; then
    test_pass
else
    test_fail "holon version failed"
fi

# Test 2: Deploy command with valid file
test_check "Deploy command (valid file)"
if holon deploy test/samples/01_echo/echo.md > /dev/null 2>&1; then
    test_pass
else
    test_fail "Failed to deploy echo.md"
fi

# Test 3: Deploy command with invalid file
test_check "Deploy command (error handling)"
if holon deploy nonexistent.md 2>&1 | grep -q "Error"; then
    test_pass
else
    test_fail "Did not produce expected error"
fi

# Test 4: Parser API
test_check "Parser API (Python)"
if python3 -c "from holon.parser import Parser; Parser.parse_file('test/samples/01_echo/echo.md')" > /dev/null 2>&1; then
    test_pass
else
    test_fail "Parser API test failed"
fi

# Test 5: All sample agents
test_check "All sample agents parse"
ALL_PARSE=true
for sample in test/samples/01_echo/echo.md \
              test/samples/02_collaborators/researcher.md \
              test/samples/02_collaborators/writer.md \
              test/samples/03_complex_network/manager.md \
              test/samples/03_complex_network/architect.md \
              test/samples/03_complex_network/po.md; do
    if ! holon deploy "$sample" > /dev/null 2>&1; then
        ALL_PARSE=false
        break
    fi
done
if [ "$ALL_PARSE" = true ]; then
    test_pass
else
    test_fail "Not all sample agents parsed successfully"
fi

# Test 6: Automated test suite
test_check "Automated test suite (pytest)"
if pytest tests/ -q > /dev/null 2>&1; then
    test_pass
else
    test_fail "pytest tests failed"
fi

# Test 9: Invalid configuration error handling
test_check "Invalid config error handling"
cat > /tmp/invalid_agent.md << 'EOF'
---
type: agent
---
# Test Agent
Missing required 'id' and 'model' fields.
EOF
if holon deploy /tmp/invalid_agent.md 2>&1 | grep -q "Error"; then
    test_pass
else
    test_fail "Did not produce expected error for invalid config"
fi

# Test 10: Empty prompt error handling
test_check "Empty prompt error handling"
cat > /tmp/empty_prompt.md << 'EOF'
---
id: test-agent
type: agent
model: gpt-4o
---

EOF
if holon deploy /tmp/empty_prompt.md 2>&1 | grep -q "Error"; then
    test_pass
else
    test_fail "Did not produce expected error for empty prompt"
fi

echo ""
echo "========================================"
echo "Results: $PASS_COUNT/$TOTAL_COUNT tests passed"
echo "========================================"

if [ $PASS_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}✅ All tests passed! Phase 1 is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the implementation.${NC}"
    exit 1
fi
