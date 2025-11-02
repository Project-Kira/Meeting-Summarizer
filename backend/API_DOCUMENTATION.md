# Meeting Summarizer API Documentation

## Overview

The Meeting Summarizer API provides REST endpoints for summarizing conversation text using a local LLM (Mistral-7B-Instruct). No external API calls, fully private and offline-capable.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Check if the API server is running and get model information.

**Endpoint:** `GET /api/health`

**Response:** `200 OK`

```json
{
  "status": "ok",
  "model_path": "/path/to/model.gguf",
  "version": "1.0.0"
}
```

**curl Example:**

```bash
curl http://localhost:8000/api/health
```

---

### 2. Summarize Text

Summarize conversation text sent as JSON.

**Endpoint:** `POST /api/summarize`

**Request Body:**

```json
{
  "text": "Meeting started at 10 AM. John discussed Q3 budget allocation..."
}
```

**Response:** `200 OK`

```json
{
  "summary": "* Q3 budget discussion\n* Action items assigned\n* Next meeting scheduled",
  "input_length": 1500,
  "estimated_tokens": 375
}
```

**Error Responses:**

- `400 Bad Request` - Empty or invalid text
- `500 Internal Server Error` - Summarization failed

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Meeting started at 10 AM. John discussed Q3 budget allocation. Sarah proposed increasing marketing spend by 15%. Team agreed to review analytics data before next meeting."}'
```

---

### 3. Summarize File

Summarize conversation from an uploaded `.txt` file.

**Endpoint:** `POST /api/summarize-file`

**Request:** `multipart/form-data`

- **file**: Text file (.txt only)

**Response:** `200 OK`

```json
{
  "summary": "* Q3 budget discussion\n* Action items assigned\n* Next meeting scheduled",
  "input_length": 6219,
  "estimated_tokens": 1554
}
```

**Error Responses:**

- `400 Bad Request` - Invalid file type, empty file, or encoding error
- `500 Internal Server Error` - File processing failed

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/summarize-file \
  -F "file=@conversation.txt"
```

---

## Frontend Integration Examples

### JavaScript (Fetch API)

#### Summarize Text

```javascript
async function summarizeText(text) {
  try {
    const response = await fetch('http://localhost:8000/api/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Summarization failed');
    }
    
    const data = await response.json();
    return data.summary;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
const summary = await summarizeText("Meeting text here...");
console.log(summary);
```

#### Summarize File

```javascript
async function summarizeFile(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/api/summarize-file', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'File processing failed');
    }
    
    const data = await response.json();
    return data.summary;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage with file input
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    const summary = await summarizeFile(file);
    console.log(summary);
  }
});
```

### React Example

```jsx
import { useState } from 'react';

function MeetingSummarizer() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
      
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/summarize-file', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
      
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Meeting Summarizer</h1>
      
      {/* Text input */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste conversation text here..."
        rows={10}
        style={{ width: '100%' }}
      />
      
      <button onClick={handleSummarize} disabled={loading || !text.trim()}>
        {loading ? 'Summarizing...' : 'Summarize Text'}
      </button>
      
      {/* File upload */}
      <div style={{ marginTop: '20px' }}>
        <input
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
          disabled={loading}
        />
      </div>
      
      {/* Error display */}
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          Error: {error}
        </div>
      )}
      
      {/* Summary display */}
      {summary && (
        <div style={{ marginTop: '20px', whiteSpace: 'pre-wrap' }}>
          <h2>Summary:</h2>
          <div>{summary}</div>
        </div>
      )}
    </div>
  );
}

export default MeetingSummarizer;
```

---

## Running the API Server

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start the Server

```bash
# Option 1: Using Python
python api.py

# Option 2: Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Production mode (no reload)
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will be available at `http://localhost:8000`

### Interactive API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Configuration

Configure the API using environment variables or by editing `config.py`:

```bash
# Model configuration
export MODEL_PATH="/path/to/model.gguf"
export N_CTX="8192"
export N_THREADS="4"
export N_GPU_LAYERS="0"

# API configuration
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# Logging
export LOG_LEVEL="INFO"
```

Or create a `.env` file:

```env
MODEL_PATH=/path/to/model.gguf
N_CTX=8192
N_THREADS=4
N_GPU_LAYERS=0
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=INFO
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200** - Success
- **400** - Bad Request (invalid input)
- **500** - Internal Server Error

Error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Performance Considerations

- **First Request**: Takes longer (~30-60s) as the model needs to load
- **Subsequent Requests**: Faster (~10-30s) as model stays in memory
- **Concurrent Requests**: Model is shared, requests are processed sequentially
- **Long Conversations**: Automatically chunked and processed in parts

---

## Security Notes

- No authentication required (add if deploying publicly)
- CORS enabled for specified origins only
- All processing happens locally (no data leaves your machine)
- No request logging of conversation content by default

---

## Troubleshooting

### Server won't start

```bash
# Check if port is already in use
lsof -i :8000

# Use different port
uvicorn api:app --port 8001
```

### CORS errors in browser

Add your frontend URL to `API_CORS_ORIGINS` in config:

```python
API_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
```

### Model loading errors

Verify model file exists and path is correct:

```bash
ls -lh models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Out of memory

Reduce context size in config:

```python
N_CTX = 4096  # Instead of 8192
```

---

## CLI vs API Mode

The backend supports both modes:

**CLI Mode** (original):
```bash
python main.py conversation.txt
```

**API Mode** (for frontend):
```bash
python api.py
```

Both use the same underlying summarization engine.
