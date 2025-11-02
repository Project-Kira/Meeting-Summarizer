# 🎙️ Meeting Summarizer (Frontend)# 🎙️ Meeting Summarizer (Frontend)



AI-powered meeting transcription and summarization tool. Record meetings, get instant transcriptions using OpenAI Whisper, and receive AI-generated summaries.An AI-powered meeting transcription and summarization tool. This repository contains the **frontend application** built with Next.js. The backend API is implemented separately.



## ✨ Features## ✨ Features



- 🎤 **Browser-based audio recording** - Record directly from your microphone- 🎤 **Browser-based audio recording** - Record directly from your microphone

- 🔊 **Speech-to-Text** - Connects to backend Whisper API for transcription- 🔊 **Speech-to-Text** - Connects to backend Whisper API for transcription

- 🤖 **AI Summarization** - Gets intelligent meeting summaries from backend- 🤖 **AI Summarization** - Gets intelligent meeting summaries from backend

- ⚡ **Real-time feedback** - Live recording timer, audio preview, and processing status- ⚡ **Real-time feedback** - Live recording timer and processing status

- 🎨 **Modern UI** - Beautiful dark theme with smooth animations- 🎨 **Modern UI** - Beautiful dark theme with smooth animations

- 🔍 **Debug mode** - Console logs and audio player to verify everything works- 🚀 **Fast & Lightweight** - Optimized for quick development



## 🚀 Quick Start## 🏗️ Project Structure



### Installation```

Meeting-Summarizer/

```bash├── Frontend/              # Next.js application

cd Frontend│   ├── app/

npm install│   │   ├── layout.js

```│   │   ├── page.js       # Main meeting page with UI

│   │   └── globals.css

### Running│   ├── lib/

│   │   └── api.js        # API integration layer (4 endpoints)

```bash│   ├── package.json

npm run dev│   ├── tailwind.config.js

```│   └── .env.local        # API URL configuration

├── BACKEND_API_SPEC.md   # Backend API documentation (for backend team)

Open http://localhost:3000 (or http://localhost:3001 if 3000 is in use)└── README.md

```

### Usage

## � API Integration

1. Click "Start Meeting" and allow microphone access

2. Speak into your microphoneThe frontend connects to backend via 4 endpoints:

3. Click "End Meeting"

4. Watch the debug info and audio player appear1. **POST** `/meeting/start` - Start new meeting session

5. See transcription and summary appear in text boxes2. **POST** `/meeting/end` - Upload audio and get transcription + summary

3. **GET** `/meeting/{id}` - Get meeting details (optional)

## 📚 Documentation4. **GET** `/` - Health check



### For Frontend DevelopersSee **[BACKEND_API_SPEC.md](./BACKEND_API_SPEC.md)** for complete backend implementation guide.

- **[HOW_TO_SEE_IT_WORKING.md](./HOW_TO_SEE_IT_WORKING.md)** - Complete guide to see your app working with console logs, audio player, and debug features

## 🚀 Quick Start

### For Backend Developers

- **[BACKEND_API_SPEC.md](./BACKEND_API_SPEC.md)** - Complete API specification for implementing the backend### Prerequisites



## 🔌 Backend Connection- **Node.js** (v18 or higher)

- **Backend API** running on `http://localhost:8000` (see BACKEND_API_SPEC.md)

**Endpoint:** `POST http://localhost:8000/process`

### Installation

**Sends:** Audio file (WAV)

```bash

**Receives:**# Navigate to frontend

```jsoncd Frontend

{

  "transcription": "Full meeting text...",# Install dependencies

  "summary": "AI-generated summary..."npm install

}

```# Configure API URL (already set to localhost:8000)

# Edit .env.local if backend is on different URL

Configure backend URL in `Frontend/.env.local`:```

```env

NEXT_PUBLIC_API_URL=http://localhost:8000### Running the Application

```

```bash

## 🛠️ Tech Stackcd Frontend

npm run dev

- Next.js 14 (App Router)```

- Tailwind CSS

- Framer Motion### 🌐 Access the Application

- React Icons

- Browser MediaRecorder APIOpen http://localhost:3000 in your browser



## 📁 Project Structure**Requirements:**

- Backend API must be running on configured URL

```- Browser must support MediaRecorder API (Chrome/Edge recommended)

Meeting-Summarizer/- Microphone permissions granted

├── Frontend/

│   ├── app/## 📖 How to Use

│   │   ├── page.js          # Main UI with recording logic

│   │   ├── layout.js        # App layout1. **Start the Application** - Open http://localhost:3000

│   │   └── globals.css      # Styles2. **Click "Start Meeting"** - Grant microphone permissions

│   ├── lib/3. **Speak into your microphone** - Recording timer shows elapsed time

│   │   └── api.js           # API integration (connects to backend)4. **Click "End Meeting"** - Audio is sent to backend for processing

│   ├── jsconfig.json        # Path alias configuration5. **View Results** - Transcription and AI summary appear in text areas

│   ├── .env.local           # Backend URL config

│   └── package.json## 🔧 Configuration

├── BACKEND_API_SPEC.md      # For backend team

├── HOW_TO_SEE_IT_WORKING.md # For testing/debugging### Frontend Environment Variables

└── README.mdFile: `Frontend/.env.local`

``````env

NEXT_PUBLIC_API_URL=http://localhost:8000

## 🐛 Troubleshooting```



### "Module not found: Can't resolve '@/lib/api'"**Change this if your backend runs on a different URL**

- Fixed! Make sure `jsconfig.json` exists in Frontend folder

### API Integration

### "Failed to fetch Inter font"All API calls are centralized in `Frontend/lib/api.js`:

- Fixed! Font removed, using system fonts instead

```javascript

### Backend connection issuesimport { startMeetingAPI, endMeetingAPI } from '@/lib/api';

- Ensure backend is running on the URL in `.env.local`

- Check browser console (F12) for detailed error messages// Start meeting

- See `HOW_TO_SEE_IT_WORKING.md` for debugging tipsconst result = await startMeetingAPI();

// Returns: { success: true/false, data/error }

## 📄 License

// End meeting

MIT License - see LICENSE file for detailsconst result = await endMeetingAPI(audioBlob, sessionId);

// Returns: { success: true/false, data/error }

---```



**Ready to test! Open F12 console to see detailed logs of what's happening! 🚀**## 🛠️ Tech Stack


- **Next.js 14** - React framework with App Router
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **React Icons** - Icon library
- **Browser MediaRecorder API** - Audio recording

## 🐛 Troubleshooting

### "Failed to fetch" error
- Ensure backend API is running on configured URL
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend CORS allows `http://localhost:3000`

### Microphone not working
- Grant browser microphone permissions
- Use Chrome/Edge for best compatibility
- Check browser console for errors

### "Module not found" errors
```bash
cd Frontend
rm -rf node_modules package-lock.json
npm install
```

### Backend connection issues
- Test backend health: `curl http://localhost:8000`
- Check backend logs for errors
- Verify CORS configuration on backend
- See [BACKEND_API_SPEC.md](./BACKEND_API_SPEC.md) for backend setup

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Frontend/app/page.js` | Main UI component with recording logic |
| `Frontend/lib/api.js` | API integration (4 endpoints) |
| `Frontend/.env.local` | Backend API URL configuration |
| `BACKEND_API_SPEC.md` | Backend API documentation |

## 🎯 For Backend Developers

See **[BACKEND_API_SPEC.md](./BACKEND_API_SPEC.md)** for:
- Complete API endpoint specifications
- Request/response formats
- CORS configuration
- Expected data flow
- Testing instructions

## � Deployment

### Frontend Deployment

**Vercel (Recommended):**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd Frontend
vercel
```

**Environment Variables on Vercel:**
- Set `NEXT_PUBLIC_API_URL` to your production backend URL

**Other Platforms:**
- Build: `npm run build`
- Start: `npm start`
- Configure `NEXT_PUBLIC_API_URL` environment variable

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ for seamless meeting transcription**
Summarizes your meetings in the background
