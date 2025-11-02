# 🔌 Backend API Specification for Meeting Summarizer

This document is for the **backend developer** to implement the API endpoints required by the frontend.

---

## 📋 Overview

The frontend needs **4 API endpoints** to handle meeting recording, transcription, and summarization.

**Base URL:** `http://localhost:8000` (configurable via frontend `.env.local`)

**CORS:** Must allow `http://localhost:3000` (frontend URL)

---

## 🎯 Required Endpoints

### 1. Health Check
**GET** `/`

**Purpose:** Verify API is running

**Request:** None

**Response:**
```json
{
  "message": "Meeting Summarizer API",
  "status": "running"
}
```

**Status Codes:**
- `200 OK` - API is running

---

### 2. Start Meeting
**POST** `/meeting/start`

**Purpose:** Initialize a new meeting session and return a unique session ID

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:** Empty (no body required)

**Response:**
```json
{
  "sessionId": "uuid-v4-string",
  "message": "Meeting started"
}
```

**Example Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Meeting started"
}
```

**Status Codes:**
- `200 OK` - Session created successfully
- `500 Internal Server Error` - Server error

**Notes:**
- Generate a unique UUID for each session
- Store session in memory/database with status: "recording"

---

### 3. End Meeting (Process Audio)
**POST** `/meeting/end`

**Purpose:** Receive audio file, transcribe with Whisper, summarize with AI, and return results

**Request Headers:**
```
Content-Type: multipart/form-data
```

**Request Body (FormData):**
| Field | Type | Description |
|-------|------|-------------|
| `file` | File (audio/wav) | Recorded audio blob from browser |
| `sessionId` | String | UUID from `/meeting/start` |

**Response:**
```json
{
  "sessionId": "uuid-v4-string",
  "transcription": "Full transcription text of the meeting audio...",
  "summary": "AI-generated summary with key points, action items, and decisions...",
  "message": "Meeting processed successfully"
}
```

**Example Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "transcription": "Hello everyone, today we discussed the project timeline. We need to complete the design phase by next week. John will handle the frontend and Sarah will work on the backend. Our deadline is December 1st.",
  "summary": "Key Points:\n- Project timeline discussion\n- Design phase deadline: Next week\n- Team assignments: John (Frontend), Sarah (Backend)\n- Final deadline: December 1st\n\nAction Items:\n- John: Complete frontend design\n- Sarah: Complete backend implementation",
  "message": "Meeting processed successfully"
}
```

**Status Codes:**
- `200 OK` - Processing successful
- `400 Bad Request` - Missing file or sessionId
- `404 Not Found` - Session ID not found
- `500 Internal Server Error` - Processing error

**Processing Steps:**
1. Validate `sessionId` exists
2. Save uploaded audio file
3. Transcribe audio using **OpenAI Whisper**
4. Generate summary using **Mistral AI** or similar LLM
5. Update session status to "completed"
6. Return transcription and summary

---

### 4. Get Meeting Details (Optional)
**GET** `/meeting/{session_id}`

**Purpose:** Retrieve existing meeting details

**Request Headers:**
```
Content-Type: application/json
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | String (UUID) | Meeting session ID |

**Response:**
```json
{
  "sessionId": "uuid-v4-string",
  "status": "completed",
  "transcription": "Full transcription text...",
  "summary": "AI-generated summary...",
  "audio_path": "uploads/uuid.wav",
  "created_at": "2025-11-02T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Meeting found
- `404 Not Found` - Session ID not found

---

## 🔧 Technical Requirements

### CORS Configuration
```python
# Python FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Audio File Handling
- **Format:** WAV (browser MediaRecorder output)
- **Storage:** Save to `uploads/` directory or cloud storage
- **Naming:** Use `{sessionId}.wav` format
- **Cleanup:** Optional - delete after processing or keep for history

### AI Services Required
1. **OpenAI Whisper** - Speech-to-text transcription
   - Model: `base` (fast) or `large` (accurate)
   - Local installation recommended

2. **Mistral AI or equivalent** - Text summarization
   - API: https://api.mistral.ai/v1/chat/completions
   - Model: `mistral-tiny` or `mistral-small`
   - Prompt: "Summarize this meeting with key points and action items"

---

## 📦 Expected Data Flow

```
Frontend                          Backend
   |                                 |
   |---(1) POST /meeting/start----->|
   |<------ { sessionId } -----------|
   |                                 |
   | User records audio...           |
   |                                 |
   |---(2) POST /meeting/end ------->|
   |     (FormData: file, sessionId) |
   |                                 |
   |                        Save audio file
   |                        Whisper transcribe
   |                        Mistral summarize
   |                                 |
   |<---- { transcription, summary }-|
   |                                 |
   | Display results to user         |
```

---

## 🧪 Testing the API

### Test with cURL

**Start Meeting:**
```bash
curl -X POST http://localhost:8000/meeting/start
```

**End Meeting:**
```bash
curl -X POST http://localhost:8000/meeting/end \
  -F "file=@test_audio.wav" \
  -F "sessionId=550e8400-e29b-41d4-a716-446655440000"
```

### Test with Postman
1. **POST** `http://localhost:8000/meeting/start`
2. **POST** `http://localhost:8000/meeting/end`
   - Body type: `form-data`
   - Add key `file` (type: File) - upload WAV file
   - Add key `sessionId` (type: Text) - paste UUID

---

## 📄 Session Storage Schema

Recommended data structure for storing sessions:

```json
{
  "sessions": {
    "550e8400-e29b-41d4-a716-446655440000": {
      "sessionId": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "audio_path": "uploads/550e8400-e29b-41d4-a716-446655440000.wav",
      "transcription": "Meeting transcription text...",
      "summary": "AI-generated summary...",
      "created_at": "2025-11-02T10:30:00Z",
      "completed_at": "2025-11-02T10:32:15Z"
    }
  }
}
```

**Status Values:**
- `recording` - Meeting started, awaiting audio
- `processing` - Audio received, AI processing in progress
- `completed` - Transcription and summary ready
- `error` - Processing failed

---

## ⚠️ Error Handling

Return appropriate error responses:

```json
{
  "error": "Error message here",
  "detail": "Detailed explanation for debugging"
}
```

**Common Errors:**
- Missing file or sessionId → `400 Bad Request`
- Invalid sessionId → `404 Not Found`
- Whisper transcription failed → `500 Internal Server Error`
- AI summarization failed → Use fallback summary

---

## 🚀 Quick Implementation Checklist

- [ ] Set up FastAPI server on port 8000
- [ ] Enable CORS for `http://localhost:3000`
- [ ] Implement `POST /meeting/start` endpoint
- [ ] Implement `POST /meeting/end` endpoint
- [ ] Install OpenAI Whisper library
- [ ] Configure Mistral AI API (or alternative)
- [ ] Create `uploads/` directory for audio files
- [ ] Test all endpoints with frontend
- [ ] Add error handling for all edge cases

---

## 💡 Optional Enhancements

- Add authentication/API keys
- Rate limiting
- Store sessions in database (PostgreSQL, MongoDB)
- Add WebSocket for real-time transcription
- Support multiple audio formats (MP3, M4A)
- Add meeting history endpoint
- Export transcriptions as PDF/TXT

---

## 📞 Frontend Integration

The frontend calls these APIs from `Frontend/lib/api.js`:

```javascript
// Start meeting
const result = await startMeetingAPI();
// Returns: { success: true, data: { sessionId, message } }

// End meeting
const result = await endMeetingAPI(audioBlob, sessionId);
// Returns: { success: true, data: { transcription, summary } }
```

**Environment Variable:**
Frontend reads API URL from: `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

## ✅ Ready to Implement!

This specification contains everything needed to build the backend. Frontend is already configured to consume these endpoints.

**Questions?** Contact the frontend team or refer to `Frontend/lib/api.js` for exact API call implementation.
