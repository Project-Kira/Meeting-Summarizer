# 🔧 Troubleshooting "Failed to fetch" Error

## ✅ Current Status

**Backend Server**: ✅ Running on port 8000 with CORS enabled
**Frontend Server**: Running on port 8080
**CORS Headers**: ✅ Configured correctly (`access-control-allow-origin: *`)

---

## 🔍 Why "Failed to fetch" Happens

This error typically occurs due to one of these reasons:

1. **Server not running** - Backend is down or crashed
2. **Wrong URL** - Frontend pointing to wrong address
3. **CORS issues** - Server blocking cross-origin requests
4. **Browser cache** - Old frontend code cached
5. **Network issues** - Firewall or connection problems

---

## ✅ Verification Checklist

### 1. Backend is Running ✅
```bash
ps aux | grep run_test_server
# Should show: python run_test_server.py

curl http://localhost:8000/healthz
# Should return: {"status":"healthy",...}
```

### 2. CORS Headers Present ✅
```bash
curl -i http://localhost:8000/meetings -X POST \
  -H "Origin: http://localhost:8080" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
  
# Should see:
# access-control-allow-origin: *
# access-control-allow-credentials: true
```

### 3. Frontend Served via HTTP ✅
```bash
# Check frontend is on http://localhost:8080/
curl -s http://localhost:8080/ | head -5

# NOT file:/// - that causes CORS issues
```

---

## 🔄 Solution: Clear Browser Cache

The most common issue after server restart is **browser cache**.

### Option 1: Hard Refresh
1. Open http://localhost:8080/
2. Press **Ctrl+Shift+R** (Linux/Windows) or **Cmd+Shift+R** (Mac)
3. This forces reload without cache

### Option 2: Clear Cache
1. Open browser DevTools (**F12**)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Incognito/Private Window
1. Open a new incognito/private window
2. Go to http://localhost:8080/
3. This bypasses all cache

### Option 4: Restart Everything
```bash
# Use the restart script
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
./restart_servers.sh

# Then open browser in incognito mode
firefox --private-window http://localhost:8080/
```

---

## 🐛 Debug in Browser Console

1. Open http://localhost:8080/ in browser
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Try to create a meeting
5. Look for errors:

**If you see:**
- `NetworkError` → Backend is down
- `CORS policy` → CORS not configured (but it is!)
- `Failed to fetch` → Could be cache or network
- `404 Not Found` → Wrong endpoint URL
- `Connection refused` → Server not listening

**Also check Network tab:**
- Click **Network** tab in DevTools
- Try creating a meeting
- Look at the request to `/meetings`
- Check:
  - Status code (should be 200)
  - Response headers (should have CORS headers)
  - Request headers (should have Content-Type)

---

## 🔧 Quick Fixes

### Fix 1: Restart Backend with Virtual Environment
```bash
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
pkill -f run_test_server
source venv/bin/activate
python run_test_server.py > server.log 2>&1 &
sleep 3
curl http://localhost:8000/healthz
```

### Fix 2: Restart Frontend Server
```bash
pkill -f 'http.server 8080'
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend/frontend
python3 -m http.server 8080 > /tmp/frontend-server.log 2>&1 &
```

### Fix 3: Use the Restart Script
```bash
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
./restart_servers.sh
```

### Fix 4: Test API Directly
```bash
# Create meeting via curl
curl -X POST http://localhost:8000/meetings \
  -H "Content-Type: application/json" \
  -d '{"title":"Direct API Test"}'

# If this works but frontend doesn't, it's a browser/cache issue
```

---

## 📊 Current Server Status

Based on recent tests:

✅ **Backend API**: WORKING
  - Health endpoint: ✅ Responding
  - POST /meetings: ✅ Working with CORS
  - CORS headers: ✅ Present
  
✅ **Frontend**: SERVING
  - Port 8080: ✅ Accessible
  - HTML file: ✅ Loading
  
⚠️ **Browser**: MIGHT BE CACHED
  - Solution: Hard refresh (Ctrl+Shift+R)
  - Or: Use incognito mode

---

## 🎯 Recommended Steps NOW

1. **Open Firefox in Private/Incognito Mode**
   ```bash
   firefox --private-window http://localhost:8080/
   ```

2. **Open DevTools** (F12)

3. **Try to create a meeting**

4. **Check Console tab** for errors

5. **Check Network tab** to see the request

6. **Report what you see:**
   - Status code?
   - Error message?
   - Request headers?
   - Response?

---

## 📞 Still Not Working?

If you're still seeing "Failed to fetch":

1. Check exact error in browser console
2. Check Network tab for request details
3. Verify backend logs: `tail -f backend/server.log`
4. Try curl to confirm API works
5. Make sure you're at http://localhost:8080/ not file:///

---

## ✅ Expected Working Behavior

When everything works:

1. Go to http://localhost:8080/
2. Enter meeting title
3. Click "Create Meeting"
4. See: "✅ Meeting created: [your title]"
5. See: Meeting ID populated
6. WebSocket connects automatically
7. Can add segments
8. Can view summaries

---

**TL;DR**: Try opening the frontend in **Firefox private window** after making sure both servers are running. This will bypass any cache issues.

```bash
# Verify servers
curl http://localhost:8000/healthz  # Backend
curl -s http://localhost:8080/ | head -5  # Frontend

# Open in private window
firefox --private-window http://localhost:8080/
```
