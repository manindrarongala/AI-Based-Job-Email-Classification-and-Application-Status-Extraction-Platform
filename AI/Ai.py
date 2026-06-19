import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_and_extract_job_email(email_subject: str, email_body: str) -> Dict[str, Any]:
    """
    Classifies if an email is job-related and extracts job information.
    
    Args:
        email_subject: The email subject line
        email_body: The full email body text to analyze
        
    Returns:
        Dictionary with:
        - is_job_related: Boolean indicating if email is job-related
        - company_name: Extracted company name (None if not job-related)
        - job_role: Extracted job role (None if not job-related)
        - application_status: Extracted application status (None if not job-related)
    """
    
    system_prompt = """You are an email classification system.

Given an email subject and email body:

1. Determine whether the email is related to a job application, recruiting process, interview, assessment, rejection, offer, recruiter outreach, or application update.

2. If the email is job-related, extract:
   - company_name: The name of the company
   - job_role: The job role or title
   - application_status: The current status of the application

3. If the email is not job-related, mark it as not job-related.

Return only valid JSON.

Status must be one of:
APPLIED
INTERVIEW
ASSESSMENT
REJECTED
OFFER
FOLLOW_UP
UNKNOWN

Response format:
{
  "is_job_related": true/false,
  "company_name": "string or null",
  "job_role": "string or null",
  "application_status": "APPLIED|INTERVIEW|ASSESSMENT|REJECTED|OFFER|FOLLOW_UP|UNKNOWN or null"
}"""

    user_message = f"""Email Subject: {email_subject}

Email Body:
{email_body}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0,
    )
    
    response_text = response.choices[0].message.content
    result = json.loads(response_text)
    
    return result


# Example usage
if __name__ == "__main__":
    # Test email examples
    test_emails = [
        {
            "subject": "Application Received - Senior Software Engineer at TechCorp Inc.",
            "body": """Hi John,

We are pleased to inform you that we have received your application for the Senior Software Engineer position at TechCorp Inc. Your resume was impressive, and we would like to move forward to the next round of interviews.

Please let us know your availability for a technical interview next week.

Best regards,
HR Team"""
        },
        {
            "subject": "Let's grab lunch tomorrow",
            "body": """Hey John,

Just checking in to see if you want to grab lunch tomorrow at noon? Let me know!

Thanks,
Mike"""
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:100]}...")
        result = classify_and_extract_job_email(email['subject'], email['body'])
        print(f"Result: {json.dumps(result, indent=2)}")
