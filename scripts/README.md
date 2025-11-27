# Development Scripts

This directory contains scripts to make development easier and automate common tasks.

## 🚀 Quick Start

### One-Command Development Startup

**Linux/Mac:**
```bash
./scripts/start_dev.sh
```

**Windows:**
```bash
scripts\start_dev.bat
```

This will:
1. ✅ Start ngrok tunnel
2. ✅ Automatically update LINE webhook URL
3. ✅ Start FastAPI development server
4. ✅ Display all relevant URLs

## 📜 Available Scripts

### `start_dev.sh` / `start_dev.bat`

**Purpose:** All-in-one development startup script

**What it does:**
- Kills any existing ngrok processes
- Starts ngrok tunnel on port 8000
- Waits for ngrok to initialize
- Automatically updates LINE webhook URL via API
- Starts the FastAPI server with hot reload
- Shows all relevant URLs (FastAPI, ngrok inspector, API docs)

**Requirements:**
- `.env` file with valid credentials
- `NGROK_AUTHTOKEN` set in `.env`
- `LINE_CHANNEL_ACCESS_TOKEN` set in `.env`
- ngrok installed and in PATH
- Python 3.7+ with required packages

**Usage:**
```bash
# Linux/Mac
./scripts/start_dev.sh

# Windows
scripts\start_dev.bat
```

**Output:**
```
========================================
IMIGO LINE Bot - Development Startup
========================================

🧹 Cleaning up existing ngrok processes...
🚀 Starting ngrok tunnel...
⏳ Waiting for ngrok to initialize...
📡 Updating LINE webhook URL...
✅ Found ngrok URL: https://abc123.ngrok.io
✅ LINE webhook updated successfully!
🧪 Testing webhook endpoint...
✅ Webhook test successful!

========================================
✅ Development environment ready!
========================================
FastAPI: http://localhost:8000
ngrok Inspector: http://localhost:4040
API Docs: http://localhost:8000/api/docs
========================================
```

**Stop the server:**
Press `Ctrl+C` to stop both the FastAPI server and ngrok

---

### `update_line_webhook.py`

**Purpose:** Manually update LINE webhook URL with current ngrok URL

**What it does:**
- Fetches the current ngrok public URL from ngrok's local API
- Updates LINE Messaging API webhook endpoint
- Tests the webhook connection

**Requirements:**
- ngrok must be running on port 4040
- `LINE_CHANNEL_ACCESS_TOKEN` in `.env`

**Usage:**
```bash
# Start ngrok first
ngrok http 8000

# Then run the script
python scripts/update_line_webhook.py
```

**Manual Usage (without start_dev.sh):**

If you prefer to run components separately:

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Update webhook
python scripts/update_line_webhook.py

# Terminal 3: Start FastAPI
python -m uvicorn main:app --reload
```

---

## 🔧 Troubleshooting

### "ngrok not found"
Install ngrok:
```bash
# Mac
brew install ngrok

# Linux
snap install ngrok

# Windows
# Download from https://ngrok.com/download
```

### "NGROK_AUTHTOKEN not set"
1. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
2. Add to `.env`:
   ```
   NGROK_AUTHTOKEN=your_token_here
   ```

### "LINE webhook update failed"
Check:
1. `LINE_CHANNEL_ACCESS_TOKEN` is correct in `.env`
2. Your LINE channel is properly configured
3. You have permissions to update the webhook

### "Port 8000 already in use"
Kill any existing processes:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### ngrok shows "ERR_NGROK_108"
Your ngrok session limit might be exceeded. With free tier:
- Only 1 ngrok process at a time
- Run `pkill ngrok` (Linux/Mac) or `taskkill /F /IM ngrok.exe` (Windows)

---

## 💡 Tips

### View ngrok Traffic
Open http://localhost:4040 to see:
- All incoming requests
- Request/response details
- Replay requests
- Debug webhook issues

### Check Webhook Status
```bash
# The script automatically tests the webhook
# Or manually test via LINE Console:
# https://developers.line.biz/console/ > Your Channel > Messaging API > Webhook settings
```

### Use with Docker
If running in Docker, update `start_dev.sh` to use `docker-compose` instead of uvicorn:
```bash
docker-compose up
```

---

## 📚 Additional Resources

- [ngrok Documentation](https://ngrok.com/docs)
- [LINE Messaging API Reference](https://developers.line.biz/en/reference/messaging-api/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
