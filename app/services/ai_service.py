"""AI service for email classification"""

import sys
from pathlib import Path

# Add parent directory to path to import from AI module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI.Ai import classify_and_extract_job_email
from typing import Dict, Any, List


def classify_email(email_subject: str, email_body: str) -> Dict[str, Any]:
    """
    Classify email and extract job information.
    
    Args:
        email_subject: Email subject line
        email_body: Email body content
        
    Returns:
        Dictionary with classification and extracted fields
    """
    try:
        print(f"[AI Service] Step 11 - Sending to AI: {email_subject[:50]}...")
        result = classify_and_extract_job_email(email_subject, email_body)
        is_job = result.get("is_job_related", False)
        print(f"[AI Service] Step 11 - AI Response: is_job_related={is_job}")
        return result
    except Exception as e:
        print(f"[AI Service] ✗ Classification error: {str(e)}")
        return {
            "is_job_related": False,
            "company_name": None,
            "job_role": None,
            "application_status": None,
            "error": str(e)
        }


def classify_emails_batch(emails: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Step 11: Classify multiple emails in batch.
    Loop through each email and send to AI.
    
    Args:
        emails: List of dicts with 'subject', 'body', 'date', 'sender' keys
        
    Returns:
        List of classified email results
    """
    print(f"\n[AI Service] Step 11: Starting batch classification for {len(emails)} emails...")
    classified = []
    
    for idx, email in enumerate(emails, 1):
        print(f"\n[AI Service] Email {idx}/{len(emails)}")
        result = classify_email(
            email.get("subject", ""),
            email.get("body", "")
        )
        classified.append({
            "subject": email.get("subject", ""),
            "body": email.get("body", ""),  # Send full body to frontend
            "date": email.get("date", ""),
            "sender": email.get("sender", ""),
            "is_job_related": result.get("is_job_related", False),
            "company": result.get("company_name"),
            "role": result.get("job_role"),
            "status": result.get("application_status")
        })
    
    print(f"\n[AI Service] ✓ Batch classification complete")
    return classified


def filter_job_related_emails(classified_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Step 12: Filter results - keep only job-related emails.
    
    Args:
        classified_emails: List of classified email results
        
    Returns:
        List containing only job-related emails
    """
    print(f"\n[AI Service] Step 12: Filtering job-related emails...")
    
    job_related = [
        email for email in classified_emails 
        if email.get("is_job_related", False)
    ]
    
    print(f"[AI Service] Step 12 - Total: {len(classified_emails)}, Job-related: {len(job_related)}")
    
    return job_related
