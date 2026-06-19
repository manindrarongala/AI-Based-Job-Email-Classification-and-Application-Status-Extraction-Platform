# Job Email Classifier - UI

A simple, beautiful web interface to scan and classify job-related emails from your Gmail inbox.

## Features

- 📧 Clean, modern UI for Gmail authentication
- 🔍 Scans emails from the last 24 hours
- 🤖 AI-powered job email classification
- 💼 Extracts company, role, and application status
- ⚡ Real-time processing with visual feedback
- 📱 Responsive design (works on desktop and mobile)

## Quick Start

### Prerequisites

- Backend server running on `http://localhost:8000`
- Python 3.7+ (for the UI server)

### Running the UI

**Option 1: Using the Python server (recommended)**

```bash
cd UI
python server.py
```

Then open: `http://localhost:8080`

**Option 2: Open directly in browser**

```bash
# Simply open the HTML file
open index.html
# or
start index.html
```

> ⚠️ Note: Direct file opening may have CORS issues. Use the Python server for best results.

## How to Use

1. **Enter Gmail Credentials:**
   - Email: Your Gmail address (e.g., `user@gmail.com`)
   - App Password: 16-character app-specific password

2. **Click "Scan Emails"**
   - The system will connect to your Gmail inbox
   - Scan emails from the last 24 hours
   - Classify each email using AI

3. **View Results**
   - Total emails scanned
   - Job-related emails found
   - Company, role, and application status

## Getting an App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable 2-Factor Authentication (if not already enabled)
3. Go to **Security** → **App passwords**
4. Select **Mail** and **Windows Computer**
5. Copy the 16-character password
6. Paste it into the App Password field

## File Structure

```
UI/
├── index.html      # Main HTML page
├── style.css       # Styling
├── script.js       # API communication & logic
├── server.py       # Python HTTP server
└── README.md       # This file
```

## Architecture

```
┌─────────────┐
│   UI (8080) │
└──────┬──────┘
       │ POST /api/scan-emails
       │
┌──────▼──────────────────┐
│  Backend FastAPI (8000) │
└──────┬──────────────────┘
       │
       └─→ Gmail IMAP
           └─→ AI Classification
```

## Troubleshooting

### "Failed to Load Page"
- Make sure the backend is running: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### "Authentication Failed"
- Double-check your Gmail and app password
- Ensure 2-Factor Authentication is enabled on your Gmail account
- Generate a new app password from Google Account Settings

### No emails showing
- Might be no job-related emails in the last 24 hours
- Check your Gmail inbox directly

### CORS Error
- Use the Python server instead of opening the HTML file directly
- Run: `python server.py`

## Backend Integration

The UI communicates with the backend via:

```javascript
POST http://localhost:8000/api/scan-emails
{
  "email": "user@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx"
}
```

Response:
```json
{
  "total_emails": 5,
  "job_related_count": 2,
  "job_emails": [
    {
      "company": "Amazon",
      "role": "SDE Intern",
      "status": "INTERVIEW",
      "subject": "Interview Invitation"
    },
    {
      "company": "Google",
      "role": "Software Engineer",
      "status": "ASSESSMENT",
      "subject": "Online Assessment"
    }
  ]
}
```

## Support

For issues or questions, check the backend logs and ensure:
- ✅ Backend is running
- ✅ Gmail credentials are correct
- ✅ 2FA is enabled on Gmail
- ✅ App password is correctly generated
