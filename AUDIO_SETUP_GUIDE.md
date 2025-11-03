# Audio Processing Setup Guide

This guide explains how to set up the backend with full audio processing capabilities (transcription + summarization).

## ✅ What Was Changed

### Backend Changes:
1. **Added `transcription.py`** - Whisper AI integration for audio-to-text
2. **Updated `api.py`** - New `/api/process` endpoint for audio processing
3. **Updated `config.py`** - Added Whisper configuration settings
4. **Updated `requirements.txt`** - Added audio processing dependencies

### Frontend Changes:
1. **Updated `api.js`** - Changed endpoints to match backend:
   - `/process` → `/api/process`
   - `/` → `/api/health` (health check)

---

## 🚀 Installation Steps

### 1. Install System Dependencies (ffmpeg)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### 2. Install Python Dependencies

```bash
cd devMSummarizer/backend
pip install -r requirements.txt
```

This will install:
- `openai-whisper` - Audio transcription AI
- `ffmpeg-python` - Audio processing
- All existing dependencies (FastAPI, llama-cpp-python, etc.)

### 3. Configure Environment Variables (Optional)

Create a `.env` file in the backend directory:

```env
# Whisper Configuration
WHISPER_MODEL=base          # Options: tiny, base, small, medium, large
WHISPER_DEVICE=cpu          # Options: cpu, cuda (for GPU)
WHISPER_LANGUAGE=auto       # Options: auto, en, es, fr, de, etc.

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend URL (for CORS)
API_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Whisper Model Sizes:**
- `tiny` - Fastest, least accurate (~75MB)
- `base` - Good balance (default, ~145MB)
- `small` - Better accuracy (~465MB)
- `medium` - High accuracy (~1.5GB)
- `large` - Best accuracy (~2.9GB)

---

## 🎯 How to Run

### Start Backend:
```bash
cd devMSummarizer/backend
python api.py
```

The server will start on `http://localhost:8000`

### Start Frontend:
```bash
cd devMSummarizer/Frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:3000` (or 5173 for Vite)

---

## 📡 API Endpoints

### 1. **POST /api/process** (NEW - Main Endpoint)
Process audio: transcribe + summarize in one call

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file (wav, mp3, m4a, ogg, flac, etc.)

**Response:**
```json
{
  "transcription": "Hello everyone, today we discussed...",
  "summary": "* Main topic\n* Action items\n* Next steps",
  "language": "en",
  "duration": 120.5
}
```

### 2. **GET /api/health**
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "model_path": "/path/to/mistral-model.gguf",
  "version": "1.0.0"
}
```

### 3. **POST /api/summarize**
Summarize text only (no audio)

**Request:**
```json
{
  "text": "Meeting transcript text here..."
}
```

### 4. **POST /api/summarize-file**
Summarize from text file upload

**Request:**
- Content-Type: `multipart/form-data`
- Body: .txt file

---

## 🔍 Testing

### Test Health Check:
```bash
curl http://localhost:8000/api/health
```

### Test Audio Processing:
```bash
curl -X POST http://localhost:8000/api/process \
  -F "file=@meeting.wav"
```

### Test Text Summarization:
```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long meeting transcript here..."}'
```

---

## 📁 File Structure

```
devMSummarizer/
├── backend/
│   ├── api.py                    # FastAPI server with /api/process endpoint
│   ├── config.py                 # Configuration (includes Whisper settings)
│   ├── transcription.py          # NEW: Whisper integration
│   ├── summarize.py              # Mistral summarization
│   ├── inference.py              # LLM inference
│   ├── requirements.txt          # Updated with audio deps
│   ├── temp_audio/               # Temporary audio storage (auto-created)
│   └── models/                   # LLM model files
│
└── Frontend/
    ├── lib/
    │   └── api.js                # Updated API client
    └── app/
        └── page.js               # Main UI
```

---

## ⚠️ Troubleshooting

### Issue: "ffmpeg not found"
**Solution:** Install ffmpeg (see step 1)

### Issue: Whisper model downloading during first run
**Expected:** Whisper downloads models on first use. This is normal and happens once.

### Issue: CORS errors in browser
**Solution:** Check `API_CORS_ORIGINS` in config.py includes your frontend URL

### Issue: Out of memory
**Solution:** Use a smaller Whisper model (tiny or base) in config

### Issue: Slow transcription
**Solution:** 
- Use smaller Whisper model
- Use GPU if available (set `WHISPER_DEVICE=cuda`)

---

## 🎉 What You Can Do Now

1. **Record audio in browser** → Frontend sends to backend
2. **Backend transcribes audio** → Whisper converts speech to text
3. **Backend summarizes** → Mistral creates summary
4. **Frontend displays both** → Transcription + Summary shown to user

All in ONE API call! 🚀

---

## 📚 Additional Resources

- Whisper Documentation: https://github.com/openai/whisper
- FastAPI Documentation: https://fastapi.tiangolo.com/
- API Documentation: http://localhost:8000/docs (when server is running)
