#!/bin/bash
# Automated API test

API="http://localhost:8000"
G='\033[0;32m' B='\033[0;34m' Y='\033[1;33m' R='\033[0;31m' N='\033[0m'

echo -e "${B}🧪 API Test${N}\n"

# 1. Health
echo -e "${B}1. Health Check${N}"
curl -sf $API/healthz > /dev/null && echo -e "${G}✅ Healthy${N}" || { echo -e "${R}❌ Failed${N}"; exit 1; }

# 2. Create Meeting
echo -e "\n${B}2. Create Meeting${N}"
RESP=$(curl -s -X POST $API/meetings -H "Content-Type: application/json" \
  -d '{"title":"Test Meeting","metadata":{"test":true}}')
MID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
[ -n "$MID" ] && echo -e "${G}✅ Created${N} (ID: ${MID:0:8}...)" || { echo -e "${R}❌ Failed${N}"; exit 1; }

# 3. Add Segments
echo -e "\n${B}3. Add Segments${N}"
SEGS=(
  "Alice|Let's discuss Q4 planning and our revenue targets for next quarter."
  "Bob|Great. Our numbers show 25% growth. We should focus on hiring next."
  "Charlie|Agreed. We need three engineers and two designers by month end."
  "Alice|Perfect. Let's finalize job descriptions and post by Friday."
  "Bob|I'll handle that. We should also discuss the new office space."
)

for i in "${!SEGS[@]}"; do
  IFS='|' read -r S T <<< "${SEGS[$i]}"
  R=$(curl -s -X POST $API/ingest/segment -H "Content-Type: application/json" \
    -d "{\"meeting_id\":\"$MID\",\"speaker\":\"$S\",\"timestamp_iso\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"text_segment\":\"$T\"}")
  echo "$R" | grep -q "accepted" && echo -e "${G}✅ Seg $((i+1))${N}: $S" || echo -e "${R}❌ Seg $((i+1))${N}"
  sleep 0.2
done

# 4. Get Summary
echo -e "\n${B}4. Get Summary${N}"
SUMM=$(curl -s $API/meetings/$MID/summary)
echo "$SUMM" | grep -q "summary" && echo -e "${G}✅ Retrieved${N}" || echo -e "${Y}⚠️  Pending${N}"
echo "$SUMM" | python3 -m json.tool 2>/dev/null | head -15

# 5. Finalize
echo -e "\n${B}5. Finalize${N}"
FIN=$(curl -s -X POST $API/meetings/$MID/finalize)
echo "$FIN" | grep -q "finalized" && echo -e "${G}✅ Finalized${N}" || echo -e "${R}❌ Failed${N}"

echo -e "\n${Y}⏳ Waiting for final summary...${N}"
sleep 3

# 6. Final Summary
echo -e "\n${B}6. Final Summary${N}"
FINAL=$(curl -s $API/meetings/$MID/summary)
echo "$FINAL" | python3 -m json.tool 2>/dev/null | head -20
echo "$FINAL" | grep -q "final" && echo -e "\n${G}✅ All tests passed!${N}" || echo -e "\n${Y}⚠️  Check summary${N}"
