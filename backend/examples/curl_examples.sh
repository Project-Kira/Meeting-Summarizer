#!/bin/bash
# Example curl commands for API testing

BASE_URL="http://localhost:8000"

echo "=================================="
echo "Meeting Summarizer API - Examples"
echo "=================================="
echo ""

# 1. Create Meeting
echo "1. Creating meeting..."
MEETING_RESPONSE=$(curl -s -X POST "$BASE_URL/meetings" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 Strategy Meeting",
    "metadata": {"department": "Product", "attendees": 4}
  }')

echo "$MEETING_RESPONSE" | jq '.'
MEETING_ID=$(echo "$MEETING_RESPONSE" | jq -r '.id')
echo "Meeting ID: $MEETING_ID"
echo ""

# 2. Ingest Segments
echo "2. Ingesting meeting segments..."

curl -s -X POST "$BASE_URL/ingest/segment" \
  -H "Content-Type: application/json" \
  -d "{
    \"meeting_id\": \"$MEETING_ID\",
    \"speaker\": \"Sarah\",
    \"timestamp_iso\": \"2025-10-31T14:00:00Z\",
    \"text_segment\": \"Welcome everyone to our Q4 strategy meeting. Today we'll discuss our product roadmap, budget allocation, and hiring plans.\"
  }" | jq '.'

curl -s -X POST "$BASE_URL/ingest/segment" \
  -H "Content-Type: application/json" \
  -d "{
    \"meeting_id\": \"$MEETING_ID\",
    \"speaker\": \"Mike\",
    \"timestamp_iso\": \"2025-10-31T14:02:00Z\",
    \"text_segment\": \"Thanks Sarah. From engineering, we're proposing three key initiatives: infrastructure upgrade, new analytics features, and mobile app enhancements.\"
  }" | jq '.'

curl -s -X POST "$BASE_URL/ingest/segment" \
  -H "Content-Type: application/json" \
  -d "{
    \"meeting_id\": \"$MEETING_ID\",
    \"speaker\": \"Lisa\",
    \"timestamp_iso\": \"2025-10-31T14:04:00Z\",
    \"text_segment\": \"We have a budget of 500K for Q4. I recommend we prioritize infrastructure first for security reasons.\"
  }" | jq '.'

curl -s -X POST "$BASE_URL/ingest/segment" \
  -H "Content-Type: application/json" \
  -d "{
    \"meeting_id\": \"$MEETING_ID\",
    \"speaker\": \"Sarah\",
    \"timestamp_iso\": \"2025-10-31T14:06:00Z\",
    \"text_segment\": \"Agreed on the infrastructure priority. Mike, please prepare a detailed plan by November 8th. Lisa, let's schedule a budget review for November 15th.\"
  }" | jq '.'

echo "✓ Segments ingested"
echo ""

# 3. Wait for processing
echo "3. Waiting for initial processing..."
sleep 5

# 4. Get Summary
echo "4. Fetching summary..."
curl -s "$BASE_URL/meetings/$MEETING_ID/summary" | jq '.'
echo ""

# 5. Finalize Meeting
echo "5. Finalizing meeting..."
curl -s -X POST "$BASE_URL/meetings/$MEETING_ID/finalize" | jq '.'
echo ""

# 6. Wait for final summary
echo "6. Waiting for final summary generation..."
sleep 5

# 7. Get Final Summary
echo "7. Fetching final summary..."
curl -s "$BASE_URL/meetings/$MEETING_ID/summary?summary_type=final" | jq '.'
echo ""

# 8. Health Check
echo "8. Checking system health..."
curl -s "$BASE_URL/healthz" | jq '.'
echo ""

echo "=================================="
echo "✓ All API calls completed!"
echo "Meeting ID: $MEETING_ID"
echo "=================================="
