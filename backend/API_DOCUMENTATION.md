# Meeting Summarizer API Documentation

## Overview

The Meeting Summarizer API provides REST endpoints for:
- **Audio transcription** using OpenAI Whisper (local)
- **Text summarization** using Mistral-7B-Instruct LLM (local)
- **Job tracking** for async processing
- **Continuous monitoring** of audio files

All processing happens locally - no external API calls, fully private and offline-capable.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/health` | Health check |
| POST | `/api/summarize` | Summarize text |
| POST | `/api/summarize-file` | Upload .txt file for summarization |
| POST | `/api/transcribe-audio` | Transcribe audio to text |
| POST | `/api/process-audio` | Full pipeline (transcribe + summarize) |
| GET | `/api/jobs/{job_id}` | Get job status |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/stats` | Processing statistics |

---

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

### 4. Transcribe Audio

Transcribe audio file to text only (no summarization).

**Endpoint:** `POST /api/transcribe-audio`

**Supported Formats:** `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.wma`, `.webm`

**Request:** Multipart form data with audio file

**Response:** `200 OK`

```json
{
  "text": "Meeting started at 10 AM. John discussed the Q3 budget...",
  "language": "en",
  "duration": 1847.5,
  "segments_count": 142
}
```

**Error Responses:**

- `400 Bad Request` - Unsupported audio format or invalid file
- `500 Internal Server Error` - Transcription failed

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/transcribe-audio \
  -F "file=@meeting.mp3"
```

---

### 5. Process Audio (Full Pipeline)

Upload audio file for complete processing: transcription + summarization.
Returns a job ID for status tracking.

**Endpoint:** `POST /api/process-audio`

**Supported Formats:** `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`, `.wma`, `.webm`

**Request:** Multipart form data with audio file

**Response:** `200 OK`

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "meeting.mp3",
  "status": "pending",
  "message": "File queued for processing"
}
```

**Processing Flow:**

1. Audio file uploaded and saved to input directory
2. Job created with unique ID
3. File queued for background processing
4. Returns immediately with job ID
5. Client polls `/api/jobs/{job_id}` for status updates

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/process-audio \
  -F "file=@meeting.mp3"

# Response:
# {
#   "job_id": "550e8400-e29b-41d4-a716-446655440000",
#   "filename": "meeting.mp3",
#   "status": "pending",
#   "message": "File queued for processing"
# }

# Check status (see next endpoint)
curl http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000
```

---

### 6. Get Job Status

Get status and results of a processing job.

**Endpoint:** `GET /api/jobs/{job_id}`

**Parameters:**

- `job_id` (path parameter) - UUID of the job

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "meeting.mp3",
  "status": "completed",
  "created_at": "2024-11-02T10:00:00.000000",
  "started_at": "2024-11-02T10:00:05.000000",
  "completed_at": "2024-11-02T10:08:30.000000",
  "transcription": "Meeting started at 10 AM. John discussed Q3 budget allocation...",
  "summary": "* Q3 budget review\n* Revenue targets exceeded by 15%\n* Action items: Bob to prepare detailed report by Friday",
  "error": null,
  "metadata": {
    "uploaded": true
  }
}
```

**Job Status Values:**

- `pending` - Job is waiting in queue
- `transcribing` - Audio is being transcribed
- `summarizing` - Text is being summarized
- `completed` - Processing finished successfully
- `failed` - Processing failed (see `error` field)

**Error Responses:**

- `404 Not Found` - Job ID does not exist

**curl Example:**

```bash
curl http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Polling Pattern:**

```javascript
async function waitForJob(jobId) {
  while (true) {
    const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`);
    const job = await response.json();
    
    if (job.status === 'completed') {
      return job;
    }
    
    if (job.status === 'failed') {
      throw new Error(job.error);
    }
    
    // Wait 5 seconds before checking again
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}
```

---

### 7. List Jobs

List all recent processing jobs.

**Endpoint:** `GET /api/jobs`

**Query Parameters:**

- `limit` (optional) - Maximum number of jobs to return (default: 100)

**Response:** `200 OK`

```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "meeting.mp3",
      "status": "completed",
      "created_at": "2024-11-02T10:00:00.000000",
      "completed_at": "2024-11-02T10:08:30.000000",
      "transcription": "...",
      "summary": "...",
      "error": null,
      "metadata": {}
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "filename": "call.mp3",
      "status": "transcribing",
      "created_at": "2024-11-02T10:10:00.000000",
      "started_at": "2024-11-02T10:10:05.000000",
      "completed_at": null,
      "transcription": null,
      "summary": null,
      "error": null,
      "metadata": {}
    }
  ],
  "total": 2
}
```

**curl Example:**

```bash
# Get last 10 jobs
curl "http://localhost:8000/api/jobs?limit=10"
```

---

### 8. Get Processing Statistics

Get statistics about all processing jobs.

**Endpoint:** `GET /api/stats`

**Response:** `200 OK`

```json
{
  "total": 25,
  "by_status": {
    "pending": 2,
    "transcribing": 1,
    "summarizing": 0,
    "completed": 20,
    "failed": 2
  },
  "queue_size": 3
}
```

**curl Example:**

```bash
curl http://localhost:8000/api/stats
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

### Audio Processing Examples

#### Process Audio File with Job Tracking

```javascript
// Upload audio and track processing
async function processAudioFile(audioFile) {
  // Step 1: Upload file
  const formData = new FormData();
  formData.append('file', audioFile);
  
  const uploadResponse = await fetch('http://localhost:8000/api/process-audio', {
    method: 'POST',
    body: formData
  });
  
  const { job_id } = await uploadResponse.json();
  console.log('Job created:', job_id);
  
  // Step 2: Poll for completion
  while (true) {
    const statusResponse = await fetch(`http://localhost:8000/api/jobs/${job_id}`);
    const job = await statusResponse.json();
    
    console.log('Status:', job.status);
    
    if (job.status === 'completed') {
      return {
        transcription: job.transcription,
        summary: job.summary
      };
    }
    
    if (job.status === 'failed') {
      throw new Error(job.error);
    }
    
    // Wait 5 seconds before checking again
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

// Usage
const fileInput = document.getElementById('audio-input');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    try {
      const result = await processAudioFile(file);
      console.log('Transcription:', result.transcription);
      console.log('Summary:', result.summary);
    } catch (error) {
      console.error('Error:', error);
    }
  }
});
```

#### Transcribe Audio Only

```javascript
// Just transcribe, no summarization
async function transcribeAudio(audioFile) {
  const formData = new FormData();
  formData.append('file', audioFile);
  
  const response = await fetch('http://localhost:8000/api/transcribe-audio', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const result = await response.json();
  return {
    text: result.text,
    language: result.language,
    duration: result.duration,
    segmentsCount: result.segments_count
  };
}

// Usage
const audioFile = document.getElementById('audio-input').files[0];
const transcription = await transcribeAudio(audioFile);
console.log(`Transcribed ${transcription.duration}s of ${transcription.language} audio`);
console.log(transcription.text);
```

### React Audio Processing Component

```jsx
import { useState } from 'react';

function AudioProcessor() {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const uploadAndProcess = async () => {
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/process-audio', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      const data = await response.json();
      setJobId(data.job_id);
      setStatus(data.status);
      
      // Start polling
      pollJobStatus(data.job_id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const pollJobStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/jobs/${id}`);
        const job = await response.json();
        
        setStatus(job.status);
        
        if (job.status === 'completed') {
          clearInterval(interval);
          setResult({
            transcription: job.transcription,
            summary: job.summary
          });
          setLoading(false);
        } else if (job.status === 'failed') {
          clearInterval(interval);
          setError(job.error);
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setError('Failed to check status');
        setLoading(false);
      }
    }, 5000); // Check every 5 seconds
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Audio Meeting Processor</h1>
      
      {/* File input */}
      <div>
        <input 
          type="file" 
          accept=".mp3,.wav,.m4a,.ogg,.flac"
          onChange={handleFileChange}
          disabled={loading}
        />
        <button 
          onClick={uploadAndProcess}
          disabled={!file || loading}
          style={{ marginLeft: '10px' }}
        >
          {loading ? 'Processing...' : 'Process Audio'}
        </button>
      </div>
      
      {/* Status */}
      {jobId && (
        <div style={{ marginTop: '20px' }}>
          <p>Job ID: {jobId}</p>
          <p>Status: <strong>{status}</strong></p>
        </div>
      )}
      
      {/* Error */}
      {error && (
        <div style={{ marginTop: '20px', color: 'red' }}>
          Error: {error}
        </div>
      )}
      
      {/* Results */}
      {result && (
        <div style={{ marginTop: '20px' }}>
          <h2>Transcription:</h2>
          <div style={{ 
            padding: '10px', 
            background: '#f5f5f5', 
            whiteSpace: 'pre-wrap',
            marginBottom: '20px'
          }}>
            {result.transcription}
          </div>
          
          <h2>Summary:</h2>
          <div style={{ 
            padding: '10px', 
            background: '#e8f4f8', 
            whiteSpace: 'pre-wrap'
          }}>
            {result.summary}
          </div>
        </div>
      )}
    </div>
  );
}

export default AudioProcessor;
```

### Python Client Example

```python
import requests
import time

def process_audio_file(file_path):
    """
    Upload audio file and wait for processing to complete.
    
    Args:
        file_path: Path to audio file (mp3, wav, etc.)
        
    Returns:
        dict with 'transcription' and 'summary' keys
    """
    # Upload file
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/process-audio',
            files={'file': f}
        )
    
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.text}")
    
    job_id = response.json()['job_id']
    print(f"Job created: {job_id}")
    
    # Poll for completion
    while True:
        response = requests.get(f'http://localhost:8000/api/jobs/{job_id}')
        job = response.json()
        
        status = job['status']
        print(f"Status: {status}")
        
        if status == 'completed':
            return {
                'transcription': job['transcription'],
                'summary': job['summary']
            }
        
        if status == 'failed':
            raise Exception(f"Processing failed: {job['error']}")
        
        # Wait 5 seconds before checking again
        time.sleep(5)

# Usage
result = process_audio_file('meeting.mp3')
print("\nTranscription:")
print(result['transcription'])
print("\nSummary:")
print(result['summary'])
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

### Text Summarization
- **First Request**: Takes longer (~30-60s) as the LLM model needs to load
- **Subsequent Requests**: Faster (~10-30s) as model stays in memory
- **Concurrent Requests**: Model is shared, requests are processed sequentially
- **Long Conversations**: Automatically chunked and processed in parts

### Audio Processing
- **Transcription Time**: ~8 minutes for 1-hour audio (using `base` Whisper model on 4-core CPU)
- **Summarization Time**: ~2-3 minutes (independent of audio length)
- **Total Time**: ~10-11 minutes for 1-hour audio file
- **Model Options**: 
  - `tiny` (39MB) - Fastest, good quality
  - `base` (74MB) - **Recommended** - Fast, better quality
  - `small` (244MB) - Slower, good quality
  - `medium` (769MB) - Slow, excellent quality
  - `large` (1.5GB) - Slowest, best quality
- **GPU Acceleration**: Use `WHISPER_DEVICE=cuda` for 3-5x faster transcription
- **Queue System**: Audio files processed sequentially (one at a time)

---

## Security Notes

- No authentication required (add if deploying publicly)
- CORS enabled for specified origins only
- All processing happens locally (no data leaves your machine)
- No request logging of conversation content by default
- Audio files saved to server (configure `DELETE_AFTER_PROCESSING` as needed)

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

Reduce context size or use smaller Whisper model:

```bash
# Reduce LLM context
export N_CTX=4096

# Use smaller Whisper model
export WHISPER_MODEL=tiny
```

### Audio processing too slow

```bash
# Use GPU (if available)
export WHISPER_DEVICE=cuda

# Or use smaller/faster model
export WHISPER_MODEL=tiny

# Increase CPU threads for LLM
export N_THREADS=8
```

### Audio file not processing

Check logs for errors:

```bash
tail -f logs/meeting_summarizer.log
```

Common issues:
- Unsupported audio format → Convert to mp3/wav
- Corrupted audio file → Re-export audio
- File too large → Split into smaller chunks

---

## Usage Modes

The backend supports multiple modes:

**API Mode** (default):
```bash
./start.sh api
# or
python api.py
```

**Daemon Mode** (continuous audio processing):
```bash
./start.sh daemon
# Automatically processes audio files dropped in input/ folder
```

**CLI Mode** (text files):
```bash
./start.sh cli conversation.txt
# or
python main.py conversation.txt
```

**Audio CLI Mode** (single audio file):
```bash
./start.sh audio meeting.mp3
```

---

## Additional Resources

- **Audio Processing Guide**: See `AUDIO_PROCESSING.md` for detailed audio features
- **Deployment Guide**: See `DEPLOYMENT.md` for production setup
- **Interactive Docs**: Visit http://localhost:8000/docs for Swagger UI
- **Alternative Docs**: Visit http://localhost:8000/redoc for ReDoc format
