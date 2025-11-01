# 🚀 Quick Start Guide

## Status: ✅ Server Running on Port 8000

### Test Server is Active!

Your Meeting Summarizer backend is **already running** on `http://localhost:8000`

---

## 📋 Quick Test via Terminal

```bash
# Health check
curl http://localhost:8000/healthz | python3 -m json.tool

# Create a meeting
curl -X POST http://localhost:8000/meetings \
  -H "Content-Type: application/json" \
  -d '{"title":"My Test Meeting"}' | python3 -m json.tool

# Add a segment (replace MEETING_ID)
curl -X POST http://localhost:8000/ingest/segment \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id":"YOUR_MEETING_ID",
    "speaker":"Alice",
    "timestamp_iso":"2025-10-31T14:00:00Z",
    "text_segment":"Let us start the meeting."
  }' | python3 -m json.tool
```

---

## 🌐 Manual Testing via Frontend

### Open the Frontend Interface:

```bash
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
firefox frontend/index.html &
# Or use your preferred browser:
# google-chrome frontend/index.html &
# chromium frontend/index.html &
```

### What You Can Test:

1. **Create Meeting**
   - Enter title and optional metadata
   - Click "Create Meeting"
   - Meeting ID will be displayed

2. **Add Segments**
   - Type speaker name and text
   - Use quick-add buttons for demos
   - Watch segments appear in the list

3. **View Summary**
   - Click "Refresh Summary" anytime
   - Summary auto-generates after adding segments
   - See decisions, action items, and topics

4. **Finalize Meeting**
   - Click "Finalize Meeting" button
   - Wait 3 seconds for final summary
   - Summary type changes from "INCREMENTAL" to "FINAL"

5. **WebSocket (Optional)**
   - Click "Connect WebSocket"
   - See real-time updates in the log panel
   - Status shows "Connected" in green

6. **Health Check**
   - Click "Check Health"
   - View system status

---

## 📊 API Documentation

Interactive API docs available at: **http://localhost:8000/docs**

---

## 🛑 Stop the Server

```bash
# Find the process
ps aux | grep run_test_server.py

# Kill it (replace PID)
kill <PID>

# Or use pkill
pkill -f run_test_server.py
```

---

## 🔄 Restart the Server

```bash
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
python run_test_server.py > server.log 2>&1 &
```

---

## 📝 Test Results from Automated Tests

### ✅ API Flow Test Completed Successfully

- **Created Meeting**: ✓
- **Added 4 Segments**: ✓
- **Generated Summary**: ✓
- **Finalized Meeting**: ✓
- **Retrieved Final Summary**: ✓

### Example Response:

```json
{
  "id": "6adc4298-9a9b-42be-bbc9-6ebd5fd5999d",
  "type": "final",
  "content": {
    "summary": "Final summary: 4 segments completed.",
    "decisions": [
      {
        "text": "All decisions finalized",
        "confidence": 0.95
      }
    ],
    "action_items": [
      {
        "text": "Complete all tasks",
        "owner": "Team",
        "due_date_iso": "2025-11-15",
        "confidence": 0.9
      }
    ],
    "topics": [
      {
        "name": "Completion",
        "confidence": 0.95
      }
    ]
  }
}
```

---

## 📚 Additional Resources

- **README**: `README.md` - Full documentation
- **Deployment Guide**: `DEPLOYMENT.md` - Production setup
- **Project Summary**: `PROJECT_SUMMARY.md` - Architecture overview
- **Server Log**: `server.log` - Runtime logs

---

## 🎯 Next Steps

1. **Open the frontend** in your browser
2. **Create a test meeting** and add segments
3. **Watch real-time updates** via WebSocket
4. **Review the summary** output
5. **Test finalization** process

---

## 💡 Notes

- **Mock Mode**: The test server uses mock summaries (no real LLM)
- **In-Memory Storage**: All data is lost when server stops
- **PostgreSQL**: For production, set up PostgreSQL (see DEPLOYMENT.md)
- **WebSocket**: Auto-reconnects if connection drops

---

**Happy Testing! 🎉**
