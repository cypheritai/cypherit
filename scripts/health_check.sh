#!/bin/bash
# CypherIt Pre-Deployment Health Check
# Run this BEFORE pushing changes to ensure nothing is broken

set -e

BASE_URL="${1:-https://www.cypherit.ai}"
PASS=0
FAIL=0

echo "🔍 CypherIt Health Check"
echo "========================"
echo "Target: $BASE_URL"
echo ""

# Test 1: Health endpoint
echo -n "1. Health endpoint... "
HEALTH=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
    echo "✅ PASS"
    ((PASS++))
else
    echo "❌ FAIL (status: $HEALTH)"
    ((FAIL++))
fi

# Test 2: Demos endpoint
echo -n "2. Demos loading... "
DEMO_COUNT=$(curl -s "$BASE_URL/demos" | jq '.demos | length')
if [ "$DEMO_COUNT" -ge 1 ]; then
    echo "✅ PASS ($DEMO_COUNT demos)"
    ((PASS++))
else
    echo "❌ FAIL (no demos loaded)"
    ((FAIL++))
fi

# Test 3: Extract functionality
echo -n "3. Extract working... "
EXTRACT=$(curl -s "$BASE_URL/extract" -X POST -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=0HBA9Nov17Q", "max_steps": 2}')
TITLE=$(echo "$EXTRACT" | jq -r '.title // empty')
STEPS=$(echo "$EXTRACT" | jq '.steps | length // 0')
if [ -n "$TITLE" ] && [ "$STEPS" -ge 1 ]; then
    echo "✅ PASS (\"$TITLE\", $STEPS steps)"
    ((PASS++))
else
    ERROR=$(echo "$EXTRACT" | jq -r '.detail // "unknown error"')
    echo "❌ FAIL ($ERROR)"
    ((FAIL++))
fi

# Test 4: Timestamps present
echo -n "4. Timestamps extracted... "
HAS_TS=$(echo "$EXTRACT" | jq '.steps[0].timestamp // empty')
if [ -n "$HAS_TS" ] && [ "$HAS_TS" != "null" ]; then
    echo "✅ PASS ($HAS_TS)"
    ((PASS++))
else
    echo "❌ FAIL (no timestamps)"
    ((FAIL++))
fi

# Test 5: Video ID present
echo -n "5. Video ID in response... "
VID=$(echo "$EXTRACT" | jq -r '.video_id // empty')
if [ -n "$VID" ] && [ "$VID" != "null" ]; then
    echo "✅ PASS ($VID)"
    ((PASS++))
else
    echo "❌ FAIL (no video_id)"
    ((FAIL++))
fi

echo ""
echo "========================"
echo "Results: $PASS passed, $FAIL failed"

if [ "$FAIL" -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED - Safe to deploy!"
    exit 0
else
    echo "⚠️ SOME CHECKS FAILED - Fix before deploying!"
    exit 1
fi
