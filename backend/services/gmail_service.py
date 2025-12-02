# Gmail service
"""
Gmail API Service
Handles all Gmail operations: fetch, send, delete emails
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
from typing import List, Dict, Optional
import re


class GmailService:
    """Gmail API operations"""
    
    def __init__(self, credentials: Credentials):
        """Initialize Gmail service with user credentials"""
        self.service = build('gmail', 'v1', credentials=credentials)
        self.user_id = 'me'
    
    def fetch_emails(self, max_results: int = 5, query: str = "") -> List[Dict]:
        """
        Fetch emails from inbox
        
        Args:
            max_results: Number of emails to fetch (default: 5)
            query: Gmail search query (e.g., "is:unread", "from:john@example.com")
        
        Returns:
            List of email dictionaries with id, sender, subject, body, date
        """
        try:
            # List messages
            results = self.service.users().messages().list(
                userId=self.user_id,
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full details for each message
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            raise Exception(f"Failed to fetch emails: {str(error)}")
    
    def get_email_by_id(self, message_id: str) -> Optional[Dict]:
        """
        Get a single email by its ID
        
        Args:
            message_id: Email message ID
        
        Returns:
            Email dictionary or None if not found
        """
        return self._get_email_details(message_id)
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed information for a specific email"""
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract headers
            subject = self._get_header(headers, 'Subject') or '(No Subject)'
            sender = self._get_header(headers, 'From') or 'Unknown Sender'
            date = self._get_header(headers, 'Date') or ''
            to = self._get_header(headers, 'To') or ''
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Parse sender name and email
            sender_name, sender_email = self._parse_sender(sender)
            
            return {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': subject,
                'sender': sender,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'to': to,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'unread': 'UNREAD' in message.get('labelIds', [])
            }
            
        except HttpError as error:
            print(f"Error fetching email {message_id}: {error}")
            return None
    
    def _get_header(self, headers: List[Dict], name: str) -> Optional[str]:
        """Extract specific header value"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = self._decode_body(part['body'].get('data', ''))
                    break
                elif part['mimeType'] == 'text/html' and not body:
                    body = self._decode_body(part['body'].get('data', ''))
        else:
            # Simple message
            body = self._decode_body(payload['body'].get('data', ''))
        
        return body or payload.get('snippet', '')
    
    def _decode_body(self, data: str) -> str:
        """Decode base64 email body"""
        if not data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            # Remove HTML tags if present
            return re.sub('<[^<]+?>', '', decoded)
        except Exception as e:
            print(f"Error decoding body: {e}")
            return ""
    
    def _parse_sender(self, sender: str) -> tuple:
        """Parse sender name and email from 'Name <email>' format"""
        match = re.match(r'(.+?)\s*<(.+?)>', sender)
        if match:
            return match.group(1).strip('"'), match.group(2)
        return sender, sender
    
    def send_email(self, to: str, subject: str, body: str, thread_id: str = None) -> Dict:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Optional thread ID for replies
        
        Returns:
            Sent message details
        """
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = {'raw': raw_message}
            
            # Add thread ID for replies
            if thread_id:
                send_message['threadId'] = thread_id
            
            # Send
            sent = self.service.users().messages().send(
                userId=self.user_id,
                body=send_message
            ).execute()
            
            return {
                'id': sent['id'],
                'thread_id': sent.get('threadId'),
                'status': 'sent'
            }
            
        except HttpError as error:
            print(f"Error sending email: {error}")
            raise Exception(f"Failed to send email: {str(error)}")
    
    def send_reply(self, original_email_id: str, reply_body: str) -> Dict:
        """
        Send a reply to an existing email
        
        Args:
            original_email_id: ID of email to reply to
            reply_body: Reply text
        
        Returns:
            Sent reply details
        """
        try:
            # Get original email details
            original = self.service.users().messages().get(
                userId=self.user_id,
                id=original_email_id,
                format='full'
            ).execute()
            
            headers = original['payload'].get('headers', [])
            
            # Extract reply information
            original_sender = self._get_header(headers, 'From')
            original_subject = self._get_header(headers, 'Subject')
            thread_id = original.get('threadId')
            
            # Ensure "Re:" prefix
            reply_subject = original_subject
            if not reply_subject.startswith('Re:'):
                reply_subject = f"Re: {reply_subject}"
            
            # Send reply
            return self.send_email(
                to=original_sender,
                subject=reply_subject,
                body=reply_body,
                thread_id=thread_id
            )
            
        except HttpError as error:
            print(f"Error sending reply: {error}")
            raise Exception(f"Failed to send reply: {str(error)}")
    
    def delete_email(self, message_id: str) -> Dict:
        """
        Permanently delete email
        
        Args:
            message_id: ID of email to delete
        
        Returns:
            Success status
        """
        try:
            self.service.users().messages().delete(
                userId=self.user_id,
                id=message_id
            ).execute()
            
            return {
                'id': message_id,
                'status': 'deleted',
                'message': 'Email permanently deleted'
            }
            
        except HttpError as error:
            print(f"Error deleting email: {error}")
            raise Exception(f"Failed to delete email: {str(error)}")
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search emails with Gmail query syntax
        
        Args:
            query: Gmail search query
                Examples:
                - "from:john@example.com"
                - "subject:invoice"
                - "is:unread"
                - "after:2024/01/01"
        
        Returns:
            List of matching emails
        """
        return self.fetch_emails(max_results=max_results, query=query)
    
    def mark_as_read(self, message_id: str) -> Dict:
        """Mark email as read"""
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return {'id': message_id, 'status': 'marked_read'}
            
        except HttpError as error:
            raise Exception(f"Failed to mark as read: {str(error)}")
    
    def mark_as_unread(self, message_id: str) -> Dict:
        """Mark email as unread"""
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            
            return {'id': message_id, 'status': 'marked_unread'}
            
        except HttpError as error:
            raise Exception(f"Failed to mark as unread: {str(error)}")
