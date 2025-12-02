# Chat router
"""
Chat API endpoints for processing natural language commands and actions
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from utils.jwt import get_current_user, get_gmail_credentials
from services.gmail_service import GmailService
from services.gemini_service import GeminiService
from services.nlp_service import NLPService

router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize services (these are stateless)
gemini_service = GeminiService()
nlp_service = NLPService()


class MessageRequest(BaseModel):
    message: str


class ActionRequest(BaseModel):
    type: str
    emailId: Optional[str] = None
    payload: Optional[Dict] = None


def get_gmail_service(user: dict = Depends(get_current_user)) -> GmailService:
    """Get Gmail service instance for authenticated user"""
    credentials = get_gmail_credentials(user)
    return GmailService(credentials)


# Helper Functions 

def create_response(content: str, emails: Optional[List[Dict]] = None, 
                   actions: Optional[List[Dict]] = None) -> Dict:
    """Create standardized response format"""
    return {
        "id": str(uuid.uuid4()),
        "content": content,
        "emails": emails or [],
        "actions": actions or [],
        "timestamp": datetime.utcnow().isoformat()
    }


def format_email_for_display(email: Dict) -> Dict:
    """Format raw email data for display"""
    sender_name = email.get("sender_name", "Unknown")
    sender_email = email.get("sender_email") or email.get("sender", "")
    if isinstance(sender_email, str) and "<" in sender_email:
        # Parse sender email from "Name <email>" format
        import re
        match = re.search(r'<(.+?)>', sender_email)
        if match:
            sender_email = match.group(1)
    
    # Parse date and create timestamp
    email_date = email.get("date", "")
    timestamp = None
    if email_date:
        try:
            from email.utils import parsedate_to_datetime
            date_obj = parsedate_to_datetime(email_date)
            timestamp = date_obj.isoformat()
        except (ValueError, TypeError, AttributeError):
            # If parsing fails, use the raw date string
            pass
    
    return {
        "id": email["id"],
        "subject": email.get("subject", "No Subject"),
        "sender": {
            "name": sender_name,
            "email": sender_email if isinstance(sender_email, str) else ""
        },
        "date": email_date,
        "timestamp": timestamp,
        "snippet": email.get("snippet", ""),
        "isRead": not email.get("unread", False)
    }


def enrich_emails_with_summaries(emails: List[Dict]) -> List[Dict]:
    """Add AI summaries to email list"""
    enriched = []
    for email in emails:
        formatted = format_email_for_display(email)
        formatted["summary"] = gemini_service.summarize_email(
            email.get("body", "") or email.get("snippet", ""),
            max_sentences=2
        )
        enriched.append(formatted)
    return enriched


def prepare_reply_actions(emails: List[Dict]) -> List[Dict]:
    """Create action buttons for reply generation"""
    actions = []
    
    # Add "Generate Replies for All" action
    if len(emails) > 1:
        actions.append({
            "id": "generate-all-replies",
            "type": "generate_replies",
            "label": "Generate Replies for All",
            "payload": {
                "emailIds": [email["id"] for email in emails],
                "emails": emails
            }
        })
    
    # Add individual reply actions
    for idx, email in enumerate(emails, 1):
        actions.append({
            "id": f"reply-{email['id']}",
            "type": "reply",
            "label": f"Reply to #{idx}",
            "emailId": email["id"],
            "payload": {
                "subject": email["subject"],
                "sender": email["sender"]
            }
        })
    
    return actions


def find_email_by_criteria(
    gmail_service: GmailService,
    email_number: Optional[int] = None,
    sender: Optional[str] = None,
    subject_keywords: Optional[List[str]] = None,
    user_message: str = ""
) -> Optional[Dict]:
    """Find email using various criteria"""
    target_email = None
    
    # By email number
    if email_number:
        emails = gmail_service.fetch_emails(max_results=email_number)
        if len(emails) >= email_number:
            return emails[email_number - 1]
    
    # By sender
    if sender:
        query = f"from:{sender}"
        emails = gmail_service.search_emails(query, max_results=1)
        if emails:
            return emails[0]
    
    # By subject keyword
    if subject_keywords:
        query = f"subject:{subject_keywords[0]}"
        emails = gmail_service.search_emails(query, max_results=1)
        if emails:
            return emails[0]
    
    # Try NLP extraction as fallback
    if not target_email:
        email_number = nlp_service.extract_email_number(user_message)
        if email_number:
            emails = gmail_service.fetch_emails(max_results=email_number)
            if len(emails) >= email_number:
                return emails[email_number - 1]
        
        sender = nlp_service.extract_sender(user_message)
        if sender:
            query = f"from:{sender}"
            emails = gmail_service.search_emails(query, max_results=1)
            if emails:
                return emails[0]
    
    return None


# Main Endpoints

@router.post("/message")
async def process_message(
    request: MessageRequest,
    user: dict = Depends(get_current_user),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Process natural language message and execute appropriate action"""
    try:
        user_message = request.message.strip()
        
        # Parse command using Gemini
        parsed = gemini_service.parse_command(user_message)
        action = parsed.get("action", "unknown")
        params = parsed.get("parameters", {})
        
        # Handle different actions
        action_handlers = {
            "read": lambda: handle_read_emails(gmail_service, params),
            "reply": lambda: handle_reply_request(gmail_service, user_message, params),
            "delete": lambda: handle_delete_request(gmail_service, user_message, params),
            "search": lambda: handle_search_emails(gmail_service, params),
            "digest": lambda: handle_daily_digest(gmail_service, params),
            "categorize": lambda: handle_categorize_emails(gmail_service, params),
        }
        
        handler = action_handlers.get(action)
        if handler:
            return await handler()
        
        # Default: try to read emails or provide helpful response
        user_msg_lower = user_message.lower()
        if any(word in user_msg_lower for word in ["email", "emails", "inbox", "messages", "digest", "categorize"]):
            if "digest" in user_msg_lower:
                return await handle_daily_digest(gmail_service, params)
            elif "categorize" in user_msg_lower or "group" in user_msg_lower:
                return await handle_categorize_emails(gmail_service, params)
            return await handle_read_emails(gmail_service, {"count": 5})
        
        return create_response(
            "I can help you with your emails! Try:\n\n"
            "• \"Show me my last 5 emails\"\n"
            "• \"Categorize my emails\"\n"
            "• \"Give me today's email digest\"\n"
            "• \"Generate replies for my emails\"\n"
            "• \"Delete email number 2\""
        )
    
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.post("/action")
async def handle_action(
    request: ActionRequest,
    user: dict = Depends(get_current_user),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Handle specific actions like sending replies or deleting emails"""
    try:
        action_handlers = {
            "send_reply": lambda: handle_send_reply(gmail_service, request.emailId, request.payload or {}),
            "delete": lambda: handle_delete_email(gmail_service, request.emailId),
            "generate_replies": lambda: handle_generate_all_replies(gmail_service, request.payload or {}),
            "reply": lambda: handle_reply_request(
                gmail_service, "", request.payload or {}, email_id=request.emailId
            ),
        }
        
        handler = action_handlers.get(request.type)
        if not handler:
            raise HTTPException(status_code=400, detail=f"Unknown action type: {request.type}")
        
        if request.type == "reply" and not request.emailId:
            raise HTTPException(status_code=400, detail="Email ID is required for reply action")
        
        return await handler()
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error handling action: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to handle action: {str(e)}")


# Email Handlers 

async def handle_read_emails(gmail_service: GmailService, params: Dict) -> Dict:
    """Read and summarize emails"""
    count = params.get("count", 5)
    emails = gmail_service.fetch_emails(max_results=count)
    
    if not emails:
        return create_response("No emails found in your inbox.")
    
    emails_with_summaries = enrich_emails_with_summaries(emails)
    
    content = f"I found {len(emails_with_summaries)} email(s) in your inbox:\n\n"
    for idx, email in enumerate(emails_with_summaries, 1):
        content += f"**Email #{idx}**\n"
        content += f"From: {email['sender']['name']} ({email['sender']['email']})\n"
        content += f"Subject: {email['subject']}\n"
        content += f"Summary: {email['summary']}\n\n"
    
    actions = prepare_reply_actions(emails_with_summaries)
    return create_response(content, emails_with_summaries, actions)


async def handle_categorize_emails(gmail_service: GmailService, params: Dict) -> Dict:
    """Fetch and categorize emails into groups"""
    count = params.get("count", 20)
    emails = gmail_service.fetch_emails(max_results=count)
    
    if not emails:
        return create_response("No emails found to categorize.")
    
    # Create email list for categorization API
    email_list_for_categorization = []
    email_id_to_email = {}
    
    for email in emails:
        email_id = email["id"]
        email_id_to_email[email_id] = email
        email_list_for_categorization.append({
            "id": email_id,
            "sender_name": email.get("sender_name", "Unknown"),
            "sender": email.get("sender", ""),
            "subject": email.get("subject", "No Subject"),
            "snippet": email.get("snippet", "")[:100]
        })
    
    # Categorize using AI
    categories = gemini_service.categorize_emails(email_list_for_categorization)
    
    # Map categories to full email objects
    categorized = {
        "Work": [],
        "Promotions": [],
        "Personal": [],
        "Urgent": [],
        "Other": []
    }
    
    category_map = {
        "work": "Work",
        "promotions": "Promotions",
        "personal": "Personal",
        "urgent": "Urgent",
        "other": "Other"
    }
    
    for cat_name, email_ids in categories.items():
        mapped_name = category_map.get(cat_name.lower(), "Other")
        for email_id in email_ids:
            if email_id in email_id_to_email:
                original_email = email_id_to_email[email_id]
                formatted = format_email_for_display(original_email)
                formatted["category"] = cat_name.lower()
                categorized[mapped_name].append(formatted)
    
    # Generate summaries for each category
    content = "📧 **Smart Inbox Grouping**\n\n"
    for category, cat_emails in categorized.items():
        if cat_emails:
            content += f"**{category}** ({len(cat_emails)} emails)\n"
            for email in cat_emails[:5]:  # Show first 5 per category
                content += f"• {email['subject']} - {email['sender']['name']}\n"
            if len(cat_emails) > 5:
                content += f"  ... and {len(cat_emails) - 5} more\n"
            content += "\n"
    
    all_emails = [email for emails_list in categorized.values() for email in emails_list]
    return create_response(content, all_emails)


async def handle_daily_digest(gmail_service: GmailService, params: Dict) -> Dict:
    """Generate daily email digest"""
    # Fetch today's emails
    today = datetime.now()
    query = f"after:{today.strftime('%Y/%m/%d')}"
    emails = gmail_service.search_emails(query, max_results=50)
    
    if not emails:
        return create_response("No emails found for today.")
    
    # Prepare emails for digest
    email_list = []
    for email in emails:
        formatted = format_email_for_display(email)
        formatted["summary"] = gemini_service.summarize_email(
            email.get("body", "") or email.get("snippet", ""),
            max_sentences=1
        )
        email_list.append(formatted)
    
    # Generate digest using AI (pass emails directly - generate_digest handles formatting)
    digest_text = gemini_service.generate_digest(emails)
    
    content = f"📅 **Today's Email Digest** ({len(emails)} emails)\n\n{digest_text}"
    
    return create_response(content, email_list[:10])  # Include top 10 emails


async def handle_reply_request(
    gmail_service: GmailService,
    user_message: str,
    params: Dict,
    email_id: Optional[str] = None
) -> Dict:
    """Generate reply for email(s)"""
    user_msg_lower = user_message.lower()
    
    # Check if user wants replies for all emails
    if any(phrase in user_msg_lower for phrase in ["all", "these", "them", "my emails", "the emails"]):
        emails = gmail_service.fetch_emails(max_results=5)
        if not emails:
            return create_response("No emails found to generate replies for.")
        
        emails_data = [format_email_for_display(email) for email in emails]
        for email, email_data in zip(emails, emails_data):
            email_data["body"] = email.get("body", "") or email.get("snippet", "")
        
        return await handle_generate_all_replies(gmail_service, {"emails": emails_data})
    
    # Find target email
    target_email = None
    if email_id:
        target_email = gmail_service.get_email_by_id(email_id)
    
    if not target_email:
        target_email = find_email_by_criteria(
            gmail_service,
            email_number=params.get("email_number"),
            sender=params.get("sender"),
            subject_keywords=params.get("subject_keywords"),
            user_message=user_message
        )
    
    if not target_email:
        emails = gmail_service.fetch_emails(max_results=1)
        if not emails:
            return create_response("No emails found to reply to.")
        target_email = emails[0]
    
    # Generate reply
    reply_text = gemini_service.generate_reply(
        email_body=target_email.get("body", "") or target_email.get("snippet", ""),
        sender_name=target_email.get("sender_name", "the sender"),
        tone=params.get("tone", "professional"),
        context=params.get("reply_context")
    )
    
    sender_name = target_email.get("sender_name", "Unknown")
    subject = target_email.get("subject", "No Subject")
    
    actions = [{
        "id": f"send-reply-{target_email['id']}",
        "type": "send_reply",
        "label": "Send Reply",
        "emailId": target_email["id"],
        "payload": {
            "replyText": reply_text,
            "subject": subject,
            "sender": sender_name
        },
        "requiresConfirmation": True,
        "confirmTitle": "Send Reply?",
        "confirmDescription": f"Send this reply to {sender_name}?"
    }]
    
    content = f"Here's a suggested reply to \"{subject}\" from {sender_name}:\n\n**Suggested Reply:**\n{reply_text}"
    
    return create_response(
        content,
        [format_email_for_display(target_email)],
        actions
    )


async def handle_delete_request(
    gmail_service: GmailService,
    user_message: str,
    params: Dict
) -> Dict:
    """Handle delete email request"""
    target_email = find_email_by_criteria(
        gmail_service,
        email_number=params.get("email_number"),
        sender=params.get("sender"),
        subject_keywords=params.get("subject_keywords"),
        user_message=user_message
    )
    
    if not target_email:
        return create_response(
            "**I couldn't find the email you want to delete.**\n\n"
            "**Here are some ways to delete emails:**\n\n"
            "**1. By Number:**\n"
            "   \"Delete email number 2\"\n"
            "   (First view your emails to see the numbers)\n\n"
            "**2. By Sender:**\n"
            "   \"Delete the latest email from john@example.com\"\n\n"
            "**3. By Subject:**\n"
            "   \"Delete email with subject 'Invoice'\"\n\n"
            "**Tip:** Say \"Show me my emails\" first to see what you have, then you can delete by number!"
        )
    
    sender_name = target_email.get("sender_name", "Unknown")
    subject = target_email.get("subject", "No Subject")
    
    actions = [{
        "id": f"delete-{target_email['id']}",
        "type": "delete",
        "label": "Delete Email",
        "emailId": target_email["id"],
        "payload": {"subject": subject, "sender": sender_name},
        "requiresConfirmation": True,
        "confirmTitle": "Permanently Delete Email?",
        "confirmDescription": f"This will permanently delete \"{subject}\" from {sender_name}. This action cannot be undone.",
        "confirmLabel": "Delete Permanently",
        "cancelLabel": "Cancel"
    }]
    
    content = f"I found the email you want to delete:\n\n**From:** {sender_name}\n**Subject:** {subject}\n\nPlease confirm to delete this email."
    
    return create_response(
        content,
        [format_email_for_display(target_email)],
        actions
    )


async def handle_generate_all_replies(gmail_service: GmailService, payload: Dict) -> Dict:
    """Generate replies for multiple emails"""
    emails_data = payload.get("emails", [])
    email_ids = payload.get("emailIds", [])
    
    # Fetch emails by ID if needed
    if not emails_data and email_ids:
        emails_data = []
        for email_id in email_ids:
            email = gmail_service.get_email_by_id(email_id)
            if email:
                formatted = format_email_for_display(email)
                formatted["body"] = email.get("body", "") or email.get("snippet", "")
                emails_data.append(formatted)
    
    if not emails_data:
        return create_response("No emails found to generate replies for.")
    
    # Generate replies
    emails_with_replies = []
    actions = []
    content = "Here are the suggested replies for your emails:\n\n"
    
    for idx, email_info in enumerate(emails_data, 1):
        email_id = email_info.get("id")
        
        # Fetch full email if body is missing
        if not email_info.get("body"):
            email = gmail_service.get_email_by_id(email_id)
            if email:
                email_info["body"] = email.get("body", "") or email.get("snippet", "")
        
        sender_name = email_info.get("sender", {}).get("name", "Unknown") if isinstance(email_info.get("sender"), dict) else "Unknown"
        email_body = email_info.get("body", "")
        
        if not email_body:
            continue
        
        reply_text = gemini_service.generate_reply(
            email_body=email_body,
            sender_name=sender_name,
            tone="professional"
        )
        
        subject = email_info.get("subject", "No Subject")
        content += f"**Email #{idx}: {subject}**\n"
        content += f"From: {sender_name}\n"
        content += f"Suggested Reply:\n{reply_text}\n\n"
        
        email_info["replyText"] = reply_text
        emails_with_replies.append(email_info)
        
        actions.append({
            "id": f"send-reply-{email_id}",
            "type": "send_reply",
            "label": f"Send Reply #{idx}",
            "emailId": email_id,
            "payload": {"replyText": reply_text, "subject": subject, "sender": sender_name},
            "requiresConfirmation": True,
            "confirmTitle": "Send Reply?",
            "confirmDescription": f"Send this reply to {sender_name}?"
        })
    
    return create_response(content, emails_with_replies, actions)


async def handle_send_reply(gmail_service: GmailService, email_id: str, payload: Dict) -> Dict:
    """Send a reply email"""
    reply_text = payload.get("replyText", "")
    if not reply_text:
        raise HTTPException(status_code=400, detail="Reply text is required")
    
    try:
        gmail_service.send_reply(email_id, reply_text)
        return create_response("✅ Reply sent successfully! Your message has been delivered.")
    except Exception as e:
        return create_response(f"❌ Failed to send reply: {str(e)}")


async def handle_delete_email(gmail_service: GmailService, email_id: str) -> Dict:
    """Delete an email"""
    try:
        gmail_service.delete_email(email_id)
        return create_response("✅ Email permanently deleted successfully!")
    except Exception as e:
        return create_response(f"❌ Failed to delete email: {str(e)}")


async def handle_search_emails(gmail_service: GmailService, params: Dict) -> Dict:
    """Search for emails"""
    query = params.get("query", "")
    count = params.get("count", 10)
    
    if not query:
        return await handle_read_emails(gmail_service, {"count": count})
    
    emails = gmail_service.search_emails(query, max_results=count)
    if not emails:
        return create_response(f"No emails found matching your search: {query}")
    
    emails_with_summaries = enrich_emails_with_summaries(emails)
    
    content = f"I found {len(emails_with_summaries)} email(s) matching your search:\n\n"
    for idx, email in enumerate(emails_with_summaries, 1):
        content += f"**Email #{idx}**\n"
        content += f"From: {email['sender']['name']} ({email['sender']['email']})\n"
        content += f"Subject: {email['subject']}\n"
        content += f"Summary: {email['summary']}\n\n"
    
    return create_response(content, emails_with_summaries)
