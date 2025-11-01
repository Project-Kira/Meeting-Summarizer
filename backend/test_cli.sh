#!/bin/bash
# Quick CLI test for Meeting Summarizer

echo "🧪 Meeting Summarizer CLI Test"
echo "================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "\n${BLUE}1. Health Check${NC}"
if curl -sf http://localhost:8000/healthz > /dev/null; then
    echo -e "${GREEN}✅ Server is healthy${NC}"
    curl -s http://localhost:8000/healthz | python3 -m json.tool
else
    echo -e "${RED}❌ Server is not responding${NC}"
    exit 1
fi

# 2. Create Meeting
echo -e "\n${BLUE}2. Creating Meeting${NC}"
MEETING_RESPONSE=$(curl -s -X POST http://localhost:8000/meetings \
  -H "Content-Type: application/json" \
  -d '{"title":"Automated CLI Test Meeting","metadata":{"test":true,"source":"cli"}}')

MEETING_ID=$(echo "$MEETING_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$MEETING_ID" ]; then
    echo -e "${RED}❌ Failed to create meeting${NC}"
    echo "$MEETING_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Meeting created${NC}"
echo "$MEETING_RESPONSE" | python3 -m json.tool
echo -e "\n${YELLOW}📋 Meeting ID: $MEETING_ID${NC}"

# 3. Add Segments
echo -e "\n${BLUE}3. Adding Segments${NC}"

SEGMENTS=(
  "Alice|Let's start our Q4 planning meeting. We have a lot to cover today."
  "Bob|I agree. First, let's review our revenue numbers. We're up 25% from last quarter."
  "Charlie|That's great news! We should discuss our hiring plans next."
  "Alice|Good point. We need three engineers and two designers by end of month."
  "Bob|I'll work on the job descriptions. Let's finalize everything by Friday."
)

for i in "${!SEGMENTS[@]}"; do
    IFS='|' read -r SPEAKER TEXT <<< "${SEGMENTS[$i]}"
    
    RESULT=$(curl -s -X POST http://localhost:8000/ingest/segment \
      -H "Content-Type: application/json" \
      -d "{
        \"meeting_id\":\"$MEETING_ID\",
        \"speaker\":\"$SPEAKER\",
        \"timestamp_iso\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
        \"text_segment\":\"$TEXT\"
      }")
    
    STATUS=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status','failed'))" 2>/dev/null)
    SEGMENT_ID=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('segment_id','')[:8])" 2>/dev/null)
    
    if [ "$STATUS" = "accepted" ]; then
        echo -e "${GREEN}✅ Segment $((i+1)) added${NC} - $SPEAKER: ${TEXT:0:50}..."
    else
        echo -e "${RED}❌ Failed to add segment $((i+1))${NC}"
    fi
    sleep 0.3
done

# 4. Get Summary
echo -e "\n${BLUE}4. Getting Current Summary${NC}"
SUMMARY=$(curl -s http://localhost:8000/meetings/$MEETING_ID/summary)
if echo "$SUMMARY" | grep -q "summary"; then
    echo -e "${GREEN}✅ Summary retrieved${NC}"
    echo "$SUMMARY" | python3 -m json.tool
else
    echo -e "${YELLOW}⚠️  No summary yet${NC}"
    echo "$SUMMARY" | python3 -m json.tool
fi

# 5. Finalize
echo -e "\n${BLUE}5. Finalizing Meeting${NC}"
FINALIZE_RESULT=$(curl -s -X POST http://localhost:8000/meetings/$MEETING_ID/finalize)
if echo "$FINALIZE_RESULT" | grep -q "finalized"; then
    echo -e "${GREEN}✅ Meeting finalized${NC}"
    echo "$FINALIZE_RESULT" | python3 -m json.tool
else
    echo -e "${RED}❌ Failed to finalize${NC}"
fi

# Wait for final summary
echo -e "\n${YELLOW}⏳ Waiting 3 seconds for final summary generation...${NC}"
sleep 3

# 6. Final Summary
echo -e "\n${BLUE}6. Getting Final Summary${NC}"
FINAL_SUMMARY=$(curl -s http://localhost:8000/meetings/$MEETING_ID/summary)
if echo "$FINAL_SUMMARY" | grep -q "final"; then
    echo -e "${GREEN}✅ Final summary retrieved (type: final)${NC}"
    echo "$FINAL_SUMMARY" | python3 -m json.tool
elif echo "$FINAL_SUMMARY" | grep -q "summary"; then
    echo -e "${YELLOW}⚠️  Summary retrieved but not marked as final yet${NC}"
    echo "$FINAL_SUMMARY" | python3 -m json.tool
else
    echo -e "${RED}❌ No summary available${NC}"
fi

# 7. Health check again to see stats
echo -e "\n${BLUE}7. Final Health Check (with stats)${NC}"
curl -s http://localhost:8000/healthz | python3 -m json.tool

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✅ All tests completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "Meeting ID: ${YELLOW}$MEETING_ID${NC}"
echo -e "\nYou can view this meeting's summary again with:"
echo -e "${BLUE}curl -s http://localhost:8000/meetings/$MEETING_ID/summary | python3 -m json.tool${NC}"
