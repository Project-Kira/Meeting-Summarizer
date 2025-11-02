# 🚀 Frontend Setup & Run Guide

## Quick Start

### 1️⃣ Install Dependencies

```bash
cd Frontend
npm install
```

### 2️⃣ Configure API URL (Optional)

Edit `Frontend/.env.local` if your backend is not on `http://localhost:8000`:

```env
NEXT_PUBLIC_API_URL=http://your-backend-url:port
```

### 3️⃣ Start Frontend

```bash
npm run dev
```

### 4️⃣ Open Browser

Visit: **http://localhost:3000**

---

## ⚠️ Important

**Backend Required:** This frontend needs a backend API running. 

See **[BACKEND_API_SPEC.md](../BACKEND_API_SPEC.md)** for backend implementation details.

---

## 🧪 Quick Test

1. Ensure backend is running and accessible
2. Open http://localhost:3000
3. Click "Start Meeting"
4. Allow microphone access
5. Speak for a few seconds
6. Click "End Meeting"
7. Wait for transcription and summary

---

## 🐛 Troubleshooting

### "Failed to fetch" error
```bash
# Test if backend is running
curl http://localhost:8000

# If not working, check:
# 1. Backend is started
# 2. NEXT_PUBLIC_API_URL in .env.local is correct
# 3. Backend CORS allows http://localhost:3000
```

### Module errors
```bash
cd Frontend
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

---

## 📦 Build for Production

```bash
cd Frontend
npm run build
npm start
```

---

## 📁 Project Structure

```
Frontend/
├── app/
│   ├── page.js          # Main meeting UI
│   ├── layout.js        # App layout
│   └── globals.css      # Tailwind styles
├── lib/
│   └── api.js           # API integration (4 endpoints)
├── package.json
├── .env.local           # API URL config
└── tailwind.config.js
```

---

## 🔌 API Endpoints Used

All in `lib/api.js`:

1. **POST** `/meeting/start` - Start session
2. **POST** `/meeting/end` - Process audio
3. **GET** `/meeting/{id}` - Get meeting (optional)
4. **GET** `/` - Health check

See [BACKEND_API_SPEC.md](../BACKEND_API_SPEC.md) for details.
