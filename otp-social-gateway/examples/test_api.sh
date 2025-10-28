#!/bin/bash
# Test script for OTP Social Gateway API

BASE_URL="http://localhost:55155"
CHAT_ID="${1:-123456789}"  # Use first argument or default

echo "========================================"
echo "OTP Social Gateway - API Test Suite"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$RESPONSE" | grep -q '"status":"ok"'; then
    echo -e "${GREEN}✅ PASS${NC} - Service is healthy"
    echo "$RESPONSE" | jq .
else
    echo -e "${RED}❌ FAIL${NC} - Service is not healthy"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# Test 2: Send Valid OTP
echo "Test 2: Send Valid OTP"
echo "--------------------"
OTP=$(printf "%06d" $((RANDOM % 1000000)))
RESPONSE=$(curl -s -X POST "$BASE_URL/send-otp" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"$CHAT_ID\",
    \"otp\": \"$OTP\",
    \"expire_seconds\": 30
  }")

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ PASS${NC} - OTP sent successfully"
    echo "$RESPONSE" | jq .
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - OTP send may have failed (check if bot token is configured)"
    echo "$RESPONSE" | jq .
fi
echo ""

# Test 3: Invalid OTP (too short)
echo "Test 3: Validation - OTP Too Short"
echo "--------------------"
RESPONSE=$(curl -s -X POST "$BASE_URL/send-otp" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"$CHAT_ID\",
    \"otp\": \"12\",
    \"expire_seconds\": 30
  }")

if echo "$RESPONSE" | grep -q 'otp must be 4-8 digits'; then
    echo -e "${GREEN}✅ PASS${NC} - Validation working correctly"
else
    echo -e "${RED}❌ FAIL${NC} - Validation not working"
fi
echo "$RESPONSE" | jq .
echo ""

# Test 4: Invalid expire_seconds
echo "Test 4: Validation - Invalid Expire Seconds"
echo "--------------------"
RESPONSE=$(curl -s -X POST "$BASE_URL/send-otp" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"$CHAT_ID\",
    \"otp\": \"123456\",
    \"expire_seconds\": 100
  }")

if echo "$RESPONSE" | grep -q 'expire_seconds must be between'; then
    echo -e "${GREEN}✅ PASS${NC} - Validation working correctly"
else
    echo -e "${RED}❌ FAIL${NC} - Validation not working"
fi
echo "$RESPONSE" | jq .
echo ""

# Test 5: Rate Limiting
echo "Test 5: Rate Limiting (sending 6 OTPs quickly)"
echo "--------------------"
SUCCESS_COUNT=0
RATE_LIMITED=false

for i in {1..6}; do
    OTP=$(printf "%06d" $((RANDOM % 1000000)))
    RESPONSE=$(curl -s -X POST "$BASE_URL/send-otp" \
      -H "Content-Type: application/json" \
      -d "{
        \"chat_id\": \"rate_limit_test_$CHAT_ID\",
        \"otp\": \"$OTP\",
        \"expire_seconds\": 10
      }")
    
    if echo "$RESPONSE" | grep -q 'Rate limit exceeded'; then
        RATE_LIMITED=true
        echo "Request $i: Rate limited ✓"
        break
    elif echo "$RESPONSE" | grep -q '"success":true'; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "Request $i: Success"
    else
        echo "Request $i: Failed (other reason)"
    fi
    sleep 0.2
done

if [ "$RATE_LIMITED" = true ]; then
    echo -e "${GREEN}✅ PASS${NC} - Rate limiting is working (limited after $SUCCESS_COUNT successful requests)"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - No rate limit triggered after 6 requests"
fi
echo ""

# Test 6: Metrics
echo "Test 6: Prometheus Metrics"
echo "--------------------"
RESPONSE=$(curl -s "$BASE_URL/metrics")
if echo "$RESPONSE" | grep -q 'otp_sent_total'; then
    echo -e "${GREEN}✅ PASS${NC} - Metrics endpoint working"
    echo "OTP Metrics:"
    echo "$RESPONSE" | grep '^otp_'
else
    echo -e "${RED}❌ FAIL${NC} - Metrics not available"
fi
echo ""

# Test 7: OpenAPI Docs
echo "Test 7: OpenAPI Documentation"
echo "--------------------"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - OpenAPI docs available at $BASE_URL/docs"
else
    echo -e "${RED}❌ FAIL${NC} - OpenAPI docs not accessible (HTTP $STATUS)"
fi
echo ""

echo "========================================"
echo "Test Suite Complete"
echo "========================================"
echo ""
echo "📝 Note: To fully test OTP delivery:"
echo "   1. Get your Telegram chat_id (see README.md)"
echo "   2. Set TELEGRAM_BOT_TOKEN in .env"
echo "   3. Run: ./test_api.sh YOUR_CHAT_ID"
echo "   4. Check Telegram for OTP message"
echo "   5. Message should auto-delete after 30 seconds"