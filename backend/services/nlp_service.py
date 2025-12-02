# NLP service
"""
NLP Service
Helper functions for natural language processing and command interpretation
"""

from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta


class NLPService:
    """Natural language processing utilities"""
    
    @staticmethod
    def extract_email_number(text: str) -> Optional[int]:
        """
        Extract email number from text like 'delete email #2' or 'reply to the first one'
        
        Args:
            text: Input text
        
        Returns:
            Email number (1-indexed) or None
        """
        # Pattern: #2, number 2, email 2
        patterns = [
            r'#(\d+)',
            r'number\s+(\d+)',
            r'email\s+(\d+)',
            r'message\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Word numbers
        word_to_num = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5
        }
        
        for word, num in word_to_num.items():
            if word in text.lower():
                return num
        
        return None
    
    @staticmethod
    def extract_sender(text: str) -> Optional[str]:
        """
        Extract sender from text like 'from john@example.com' or 'sent by John'
        
        Args:
            text: Input text
        
        Returns:
            Sender name/email or None
        """
        # Email pattern
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        email_match = re.search(email_pattern, text)
        if email_match:
            return email_match.group(0)
        
        # Name after 'from' or 'by'
        name_patterns = [
            r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'sender\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract important keywords from text
        
        Args:
            text: Input text
        
        Returns:
            List of keywords
        """
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'about', 'show', 'get', 
            'find', 'delete', 'reply', 'email', 'emails', 'me', 'my'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter stop words
        keywords = [w for w in words if w not in stop_words]
        
        return list(set(keywords))[:5]  # Return up to 5 unique keywords
    
    @staticmethod
    def parse_time_reference(text: str) -> Optional[str]:
        """
        Parse time references like 'today', 'this week', 'last month'
        
        Args:
            text: Input text
        
        Returns:
            Gmail query string for date filtering
        """
        text_lower = text.lower()
        today = datetime.now()
        
        time_mappings = {
            'today': f"after:{today.strftime('%Y/%m/%d')}",
            'yesterday': f"after:{(today - timedelta(days=1)).strftime('%Y/%m/%d')} before:{today.strftime('%Y/%m/%d')}",
            'this week': f"after:{(today - timedelta(days=7)).strftime('%Y/%m/%d')}",
            'last week': f"after:{(today - timedelta(days=14)).strftime('%Y/%m/%d')} before:{(today - timedelta(days=7)).strftime('%Y/%m/%d')}",
            'this month': f"after:{today.replace(day=1).strftime('%Y/%m/%d')}",
        }
        
        for phrase, query in time_mappings.items():
            if phrase in text_lower:
                return query
        
        return None
    
    @staticmethod
    def build_gmail_query(parameters: Dict) -> str:
        """
        Build Gmail search query from parameters
        
        Args:
            parameters: Dictionary with search parameters
        
        Returns:
            Gmail query string
        """
        query_parts = []
        
        # Sender
        if parameters.get('sender'):
            sender = parameters['sender']
            if '@' in sender:
                query_parts.append(f"from:{sender}")
            else:
                query_parts.append(f"from:{sender}")
        
        # Subject keywords
        if parameters.get('subject_keywords'):
            for keyword in parameters['subject_keywords']:
                query_parts.append(f"subject:{keyword}")
        
        # General query
        if parameters.get('query'):
            query_parts.append(parameters['query'])
        
        # Unread filter
        if parameters.get('unread_only'):
            query_parts.append("is:unread")
        
        # Important filter
        if parameters.get('important'):
            query_parts.append("is:important")
        
        return ' '.join(query_parts)
    
    @staticmethod
    def detect_intent(text: str) -> str:
        """
        Detect user intent from text (fallback when AI parsing fails)
        
        Args:
            text: User input
        
        Returns:
            Intent: read, reply, delete, search, digest, unknown
        """
        text_lower = text.lower()
        
        # Read intents
        if any(word in text_lower for word in ['show', 'list', 'display', 'get', 'fetch', 'read']):
            return 'read'
        
        # Reply intents
        if any(word in text_lower for word in ['reply', 'respond', 'answer', 'write back']):
            return 'reply'
        
        # Delete intents
        if any(word in text_lower for word in ['delete', 'remove', 'trash', 'get rid']):
            return 'delete'
        
        # Search intents
        if any(word in text_lower for word in ['find', 'search', 'look for', 'filter']):
            return 'search'
        
        # Digest intents
        if any(word in text_lower for word in ['digest', 'summary', 'overview', 'summarize']):
            return 'digest'
        
        return 'unknown'
    
    @staticmethod
    def format_email_list(emails: List[Dict]) -> str:
        """
        Format email list for display
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            Formatted string
        """
        if not emails:
            return "No emails found."
        
        formatted = f"Found {len(emails)} email(s):\n\n"
        
        for idx, email in enumerate(emails, 1):
            formatted += f"{idx}. From: {email.get('sender_name', 'Unknown')}\n"
            formatted += f"   Subject: {email.get('subject', 'No Subject')}\n"
            formatted += f"   Date: {email.get('date', 'Unknown')}\n\n"
        
        return formatted
