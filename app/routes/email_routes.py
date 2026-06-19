"""Email classification routes"""

from fastapi import APIRouter, HTTPException
from app.models.request_model import (
    ScanEmailsRequest,
    ScanEmailsResponse,
    JobEmailResult
)
from app.services.gmail_service import fetch_emails
from app.services.ai_service import classify_emails_batch, filter_job_related_emails

router = APIRouter(prefix="/api", tags=["email"])


@router.post("/scan-emails", response_model=ScanEmailsResponse)
async def scan_emails(request: ScanEmailsRequest):
    """
    Scan emails from Gmail inbox and classify for job relevance.
    
    Complete Flow:
    1. Connect to Gmail IMAP (imap.gmail.com:993)
    2. Authenticate with email/password
    3. Open INBOX
    4. Fetch email IDs
    5. Filter by last 24 hours
    6. Extract subject (test: can backend read subjects?)
    7. Extract plain text body (ignore HTML/attachments)
    8. Create email objects
    9. Step 11: Send each email to AI
    10. Step 12: Filter job-related emails
    11. Step 13: Build final response
    
    Request body:
    - email: Gmail address (e.g., "user@gmail.com")
    - app_password: 16-character app-specific password
    
    Returns (Step 13 - Final Response):
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
    """
    try:
        # Fetch emails from Gmail (Steps 1-10: Connection, Auth, INBOX, Fetch, Filter, Extract)
        print("\n[Endpoint] ===== STEP 1-10: EMAIL FETCHING =====")
        result = fetch_emails(
            email=request.email,
            app_password=request.app_password,
            max_results=10
        )
        
        # Check if connection/authentication succeeded
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["message"])
        
        emails = result["emails"]
        
        if not emails:
            print("[Endpoint] No emails found")
            return ScanEmailsResponse(
                total_emails=0,
                job_related_count=0,
                job_emails=[]
            )
        
        # Step 11: Send each email to AI for classification
        print("\n[Endpoint] ===== STEP 11: AI CLASSIFICATION =====")
        classified_emails = classify_emails_batch(emails)
        
        # Step 12: Filter job-related emails
        print("\n[Endpoint] ===== STEP 12: FILTER JOB EMAILS =====")
        job_emails = filter_job_related_emails(classified_emails)
        
        # Step 13: Build final response
        print("\n[Endpoint] ===== STEP 13: BUILD FINAL RESPONSE =====")
        job_email_results = []
        
        for email in job_emails:
            result = JobEmailResult(
                company=email.get("company"),
                role=email.get("role"),
                status=email.get("status"),
                subject=email.get("subject"),
                body=email.get("body")
            )
            job_email_results.append(result)
            print(f"[Endpoint] Step 13 - Added: {email['company']} - {email['role']}")
        
        response = ScanEmailsResponse(
            total_emails=len(emails),
            job_related_count=len(job_email_results),
            job_emails=job_email_results
        )
        
        print(f"\n[Endpoint] ✓ COMPLETE: {len(job_email_results)} job emails found out of {len(emails)} total")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Endpoint] ✗ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify")
async def classify_email():
    """Classify an email for job relevance"""
    pass
