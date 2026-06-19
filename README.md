# CareerRadar AI | Job Email Classifier

An AI-powered job application email classifier that scans your Gmail inbox, filters messages from the last 24 hours, and categorizes them using a LLaMA 3.1 model.

---

## ⚡ Quick Start

### **Option A: Windows Batch File (Easiest)**
1. Open the project folder `C:\Users\ronga\Downloads\job_classifier` in File Explorer.
2. **Double-click** `START.bat`.
3. Open your browser and navigate to **`http://localhost:8080`**.

### **Option B: PowerShell Script**
Run the startup script directly in PowerShell:
```powershell
.\START.ps1
```
Then open: **`http://localhost:8080`**

### **Option C: Manual Commands**
**Terminal 1 (Backend FastAPI on port 8000):**
```powershell
& .\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (UI HTTP Server on port 8080):**
```powershell
cd UI
..\venv\Scripts\Activate.ps1
python server.py
```

---

## 📋 First-Time Setup

If you need to install the environment from scratch:
```powershell
# 1. Create python virtual environment
python -m venv venv

# 2. Activate virtual environment
& .\venv\Scripts\Activate.ps1

# 3. Install required packages
pip install -r requirements.txt

# 4. Configure environment keys
# Verify a .env file exists in the root directory containing:
# GROQ_API_KEY=your_groq_api_key_here
```

---

## 🔍 Verification & Docs

*   **API Docs (Swagger UI):** `http://localhost:8000/docs`
*   **API Health Status:** `http://localhost:8000/` (Returns `{"status":"running"}`)
*   **UI Client:** `http://localhost:8080`

---

## 📁 Project Structure

```
job_classifier/
├── app/                     # Backend FastAPI App
│   ├── main.py             # App entrypoint
│   ├── routes/             # API routes (/api/scan-emails)
│   ├── services/           # Gmail IMAP & AI service connectors
│   └── models/             # Request/Response Pydantic models
├── AI/
│   └── Ai.py               # Groq LLaMA 3.1 interface logic
├── UI/                     # Frontend client
│   ├── index.html          # Web dashboard layout
│   ├── style.css           # Glassmorphic stylesheet
│   ├── script.js           # Client logic & state
│   └── server.py           # HTTP server for UI assets
├── requirements.txt        # Backend dependencies
├── .env                    # API keys (kept gitignored)
├── START.bat               # Windows batch auto-launcher
├── START.ps1               # PowerShell auto-launcher
└── README.md               # Unified project documentation
```

---

## 🐛 Troubleshooting

*   **"GROQ_API_KEY not found"**: Add your Groq API key inside the `.env` file in the root directory.
*   **"Address already in use"**: Port 8000 or 8080 is already occupied. Close background terminal windows or change ports.
*   **Gmail Auth Fails**: Ensure your Gmail account has 2FA enabled and that you generated a **16-character App Password** (not your regular Gmail password).
