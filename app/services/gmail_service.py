"""Gmail service for fetching emails"""

import imaplib
from typing import Dict, Any, Tuple, List
from datetime import datetime, timedelta
from email import message_from_bytes
import email.utils
from email.header import decode_header
from html.parser import HTMLParser
import html
import re


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.ignore_depth = 0
        self.ignore_tags = {'style', 'script', 'head'}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.ignore_tags:
            self.ignore_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.ignore_tags:
            self.ignore_depth = max(0, self.ignore_depth - 1)

    def handle_data(self, d):
        if self.ignore_depth == 0:
            self.result.append(d)

    def get_text(self):
        raw_text = "".join(self.result)
        return html.unescape(raw_text).strip()


def strip_html_tags(html_content: str) -> str:
    """Helper to extract clean text from HTML content, ignoring CSS/JS scripts."""
    try:
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return parser.get_text()
    except Exception:
        # Fallback to simple regex if HTMLParser fails
        text = re.sub('<[^<]+?>', '', html_content)
        return html.unescape(text).strip()


def decode_mime_header(header_value: str) -> str:
    """Helper to decode MIME encoded headers (e.g. subject, sender)."""
    if not header_value:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        decoded_text = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                enc = encoding or 'utf-8'
                try:
                    decoded_text.append(part.decode(enc, errors='ignore'))
                except Exception:
                    decoded_text.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_text.append(part)
        return "".join(decoded_text)
    except Exception:
        return header_value


def extract_part_body(part) -> str:
    """Helper to extract body bytes and decode them based on part charset."""
    charset = part.get_content_charset() or 'utf-8'
    try:
        payload = part.get_payload(decode=True)
        if payload:
            return payload.decode(charset, errors='ignore')
    except Exception as e:
        print(f"[Gmail Service] Error decoding part with charset {charset}: {str(e)}")
        try:
            payload = part.get_payload(decode=True)
            if payload:
                return payload.decode('utf-8', errors='ignore')
        except Exception:
            pass
    return ""


def extract_email_body(msg) -> str:
    """Extract and decode plain text body, falling back to HTML-to-text if no plain text."""
    # 1. Non-multipart
    if not msg.is_multipart():
        content_type = msg.get_content_type()
        body = extract_part_body(msg)
        if content_type == "text/html":
            body = strip_html_tags(body)
        return body

    # 2. Multipart: look for text/plain first
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in disposition:
                continue
            body = extract_part_body(part)
            if body.strip():
                return body

    # 3. Multipart fallback: look for text/html
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in disposition:
                continue
            html_body = extract_part_body(part)
            if html_body.strip():
                return strip_html_tags(html_body)

    return ""


def connect_and_authenticate(email: str, app_password: str) -> Tuple[bool, str, imaplib.IMAP4_SSL | None]:
    """
    Connect to Gmail IMAP server and authenticate.
    
    Flow:
    1. Connect to imap.gmail.com:993 (SSL)
    2. Authenticate with email and app_password
    3. Open INBOX
    
    Args:
        email: Gmail address (e.g., "user@gmail.com")
        app_password: 16-character app-specific password
        
    Returns:
        Tuple of (success: bool, message: str, mail_connection: imaplib.IMAP4_SSL or None)
    """
    try:
        # Step 1: Connect to Gmail IMAP server
        print(f"[Gmail Service] Connecting to imap.gmail.com:993...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        print("[Gmail Service] ✓ Connected successfully (SSL Handshake complete)")
        
        # Step 2: Authenticate
        print(f"[Gmail Service] Authenticating with email: {email}...")
        mail.login(email, app_password)
        print("[Gmail Service] ✓ Authentication successful")
        
        # Step 3: Open INBOX
        print("[Gmail Service] Opening INBOX...")
        status, mailbox_list = mail.select("INBOX")
        if status == "OK":
            print("[Gmail Service] ✓ INBOX opened successfully")
            return True, "Connected Successfully", mail
        else:
            return False, "Failed to open INBOX", None
            
    except imaplib.IMAP4.error as e:
        error_msg = f"Authentication Failed: {str(e)}"
        print(f"[Gmail Service] ✗ {error_msg}")
        return False, error_msg, None
        
    except Exception as e:
        error_msg = f"Connection Error: {str(e)}"
        print(f"[Gmail Service] ✗ {error_msg}")
        return False, error_msg, None


def fetch_email_ids(mail: imaplib.IMAP4_SSL) -> Tuple[bool, List[bytes]]:
    """
    Step 6: Fetch email IDs from INBOX.
    
    Just retrieve message identifiers, don't fetch bodies yet.
    
    Args:
        mail: IMAP connection object (already authenticated and INBOX selected)
        
    Returns:
        Tuple of (success: bool, email_ids: list of bytes)
    """
    try:
        print("[Gmail Service] Step 6: Fetching email IDs from INBOX...")
        status, message_numbers = mail.search(None, "ALL")
        
        if status != "OK":
            print("[Gmail Service] ✗ Failed to fetch email IDs")
            return False, []
        
        email_ids = message_numbers[0].split()
        print(f"[Gmail Service] ✓ Found {len(email_ids)} emails in INBOX")
        
        return True, email_ids
        
    except Exception as e:
        print(f"[Gmail Service] ✗ Error fetching email IDs: {str(e)}")
        return False, []


def filter_last_24_hours(mail: imaplib.IMAP4_SSL, email_ids: List[bytes]) -> Tuple[bool, List[bytes]]:
    """
    Step 7: Filter emails from last 24 hours.
    
    Args:
        mail: IMAP connection object
        email_ids: List of email IDs to filter
        
    Returns:
        Tuple of (success: bool, filtered_email_ids: list)
    """
    try:
        # Calculate 24 hours ago
        now = datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        date_string = twenty_four_hours_ago.strftime("%d-%b-%Y")
        
        print(f"[Gmail Service] Step 7: Filtering emails from last 24 hours...")
        print(f"[Gmail Service] Current time: {now.strftime('%d %b %Y %H:%M:%S')}")
        print(f"[Gmail Service] Fetching emails from: {date_string} onwards")
        
        # Search for emails since 24 hours ago
        status, message_numbers = mail.search(None, f"SINCE {date_string}")
        
        if status != "OK":
            print("[Gmail Service] ✗ Failed to filter by date")
            return False, []
        
        filtered_ids = message_numbers[0].split()
        print(f"[Gmail Service] ✓ Found {len(filtered_ids)} emails in last 24 hours")
        
        if len(filtered_ids) == 0:
            print("[Gmail Service] ℹ No emails from last 24 hours. Using all available emails.")
            return True, email_ids
        
        return True, filtered_ids
        
    except Exception as e:
        print(f"[Gmail Service] ✗ Error filtering by date: {str(e)}")
        # Fall back to all emails if date filtering fails
        return True, email_ids


def fetch_emails(email: str, app_password: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Fetch emails from Gmail inbox after authentication.
    
    Steps:
    1. Connect and authenticate
    2. Open INBOX
    3. Fetch email IDs
    4. Filter by last 24 hours
    5. Fetch email bodies
    
    Args:
        email: Gmail address
        app_password: App-specific password
        max_results: Maximum number of emails to fetch
        
    Returns:
        Dictionary with:
        - success: bool indicating if fetch was successful
        - message: Status message
        - emails: List of emails (empty if failed)
    """
    # Step 1-3: Connect and authenticate + Open INBOX
    success, message, mail = connect_and_authenticate(email, app_password)
    
    if not success:
        return {
            "success": False,
            "message": message,
            "emails": []
        }
    
    try:
        # Step 6: Fetch email IDs only
        success, email_ids = fetch_email_ids(mail)
        if not success or not email_ids:
            print("[Gmail Service] No emails found")
            mail.close()
            mail.logout()
            return {
                "success": True,
                "message": "Connected Successfully",
                "emails": []
            }
        
        # Step 7: Filter by last 24 hours
        success, filtered_ids = filter_last_24_hours(mail, email_ids)
        if not success:
            print("[Gmail Service] Date filtering failed, using all emails")
            filtered_ids = email_ids
        
        # Limit to max_results
        email_ids_to_fetch = filtered_ids[-max_results:] if len(filtered_ids) > max_results else filtered_ids
        
        print(f"[Gmail Service] Fetching {len(email_ids_to_fetch)} emails...")
        emails = []
        
        # Step 8-10: Fetch and extract subject, body, date
        for idx, email_id in enumerate(email_ids_to_fetch, 1):
            try:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = message_from_bytes(response_part[1])
                        
                        # Step 8: Extract Subject
                        raw_subject = msg.get("Subject", "No Subject")
                        subject = decode_mime_header(raw_subject)
                        print(f"[Gmail Service] Step 8 - Subject extracted and decoded: {subject}")
                        
                        raw_sender = msg.get("From", "Unknown Sender")
                        sender = decode_mime_header(raw_sender)
                        
                        date_str = msg.get("Date", "Unknown Date")
                        
                        # Step 9: Extract Email Body (handles text/plain and falls back to text/html)
                        body = extract_email_body(msg)
                        print(f"[Gmail Service] Step 9 - Body extracted ({len(body)} chars)")
                        
                        # Limit body length for processing
                        if len(body) > 2000:
                            body = body[:2000] + "\n\n[Email truncated for display]"
                        
                        # Step 10: Create email object and store in memory
                        email_object = {
                            "subject": subject,
                            "body": body,
                            "date": date_str,
                            "sender": sender
                        }
                        emails.append(email_object)
                        
                        print(f"[Gmail Service] Step 10 - Email object created: {{{subject[:40]}...}}")
                        
                print(f"[Gmail Service] Fetched {idx}/{len(email_ids_to_fetch)} emails")
                
            except Exception as e:
                print(f"[Gmail Service] Error fetching email {email_id}: {str(e)}")
                continue
        
        # Close connection
        mail.close()
        mail.logout()
        print("[Gmail Service] Connection closed")
        
        return {
            "success": True,
            "message": "Connected Successfully",
            "emails": emails
        }
        
    except Exception as e:
        print(f"[Gmail Service] ✗ Error: {str(e)}")
        try:
            mail.close()
            mail.logout()
        except:
            pass
        return {
            "success": False,
            "message": f"Error fetching emails: {str(e)}",
            "emails": []
        }
