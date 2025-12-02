# Gemini service
import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional


class GeminiService:
    """Gemini AI operations"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    def summarize_email(self, email_body: str, max_sentences: int = 2) -> str:
        """
        Summarize email content
        
        Args:
            email_body: Full email text
            max_sentences: Maximum sentences in summary
        
        Returns:
            Concise summary
        """
        prompt = f"""Summarize this email in {max_sentences} sentences or less. 
Be concise and highlight the main point or action needed.

Email:
{email_body}

Summary:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini summarization error: {e}")
            return "Unable to generate summary"
    
    def generate_reply(
        self, 
        email_body: str, 
        sender_name: str, 
        tone: str = "professional",
        context: str = None
    ) -> str:
        """
        Generate email reply
        
        Args:
            email_body: Original email content
            sender_name: Name of sender
            tone: Reply tone (professional, friendly, brief)
            context: Additional context or instructions
        
        Returns:
            Generated reply text
        """
        tone_instructions = {
            "professional": "Write a professional and courteous reply.",
            "friendly": "Write a warm and friendly reply.",
            "brief": "Write a very brief reply (1-2 sentences)."
        }
        
        instruction = tone_instructions.get(tone, tone_instructions["professional"])
        
        # Clear guidance for the model about what a good reply should look like.
        prompt = f"""{instruction}

Write a reply that is:
- Context aware (based directly on the original email content)
- Clear and professional
- Ready to send as-is (no placeholders like "[YOUR NAME]" or "[INSERT DETAILS]")
- Action-oriented where appropriate (e.g., next steps, confirmations, or follow-ups)
- Polite and concise, avoiding unnecessary repetition of the original email

Original email from {sender_name}:
{email_body}

{f'Additional context: {context}' if context else ''}

Write only the reply body. Do not include greetings like "Dear..." or signatures. 
Do not add your own sign-off/signature. Be helpful, specific, and concise.

Reply:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini reply generation error: {e}")
            return "I'd be happy to help. Could you provide more details?"
    
    def parse_command(self, user_input: str) -> Dict:
        """
        Parse natural language command into structured action
        
        Args:
            user_input: User's natural language input
        
        Returns:
            Dictionary with action type and parameters
        """
        prompt = f"""Parse this email command into structured JSON.

Command: "{user_input}"

Return ONLY valid JSON in this exact format:
{{
  "action": "read" | "reply" | "delete" | "search" | "digest" | "categorize" | "unknown",
  "parameters": {{
    "count": 5,
    "query": "",
    "sender": "",
    "subject_keywords": [],
    "email_number": null,
    "tone": "professional",
    "reply_context": ""
  }}
}}

Rules:
- action "read": Show/list/display emails
- action "reply": Generate/write reply
- action "delete": Remove/trash emails
- action "search": Find specific emails
- action "digest": Summary/overview of emails (daily digest, today's digest)
- action "categorize": Group/categorize/group emails into categories
- Extract numbers for "count" or "email_number"
- Extract sender names/emails for "sender"
- Extract keywords from subject mentions

JSON:"""
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean markdown formatting if present
            json_text = json_text.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(json_text)
            return parsed
        except Exception as e:
            print(f"Gemini command parsing error: {e}")
            # Return default structure
            return {
                "action": "unknown",
                "parameters": {
                    "count": 5,
                    "query": user_input
                }
            }
    
    def categorize_emails(self, emails: List[Dict]) -> Dict[str, List[str]]:
        """
        Categorize emails into groups
        
        Args:
            emails: List of email objects with id, subject, sender, snippet
        
        Returns:
            Dictionary mapping categories to email IDs
        """
        # Prepare email summaries for AI
        email_summaries = []
        for email in emails:
            email_summaries.append({
                'id': email['id'],
                'from': email.get('sender_name', email.get('sender', 'Unknown')),
                'subject': email.get('subject', 'No Subject'),
                'preview': email.get('snippet', '')[:100]
            })
        
        prompt = f"""Categorize these {len(emails)} emails into appropriate categories.

Emails:
{json.dumps(email_summaries, indent=2)}

Return ONLY valid JSON in this format:
{{
  "urgent": ["email_id1", "email_id2"],
  "work": ["email_id3"],
  "personal": ["email_id4"],
  "promotions": ["email_id5"],
  "other": ["email_id6"]
}}

Categories:
- urgent: Requires immediate attention, deadlines, important
- work: Work-related, professional correspondence
- personal: Personal messages from individuals
- promotions: Marketing, newsletters, promotional content
- other: Everything else

JSON:"""
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            json_text = json_text.replace('```json', '').replace('```', '').strip()
            
            categories = json.loads(json_text)
            return categories
        except Exception as e:
            print(f"Gemini categorization error: {e}")
            # Return all as "other"
            return {"other": [email['id'] for email in emails]}
    
    def generate_digest(self, emails: List[Dict]) -> str:
        """
        Generate daily digest summary
        
        Args:
            emails: List of emails to summarize
        
        Returns:
            Formatted digest text
        """
        # Prepare email data
        email_data = []
        for email in emails:
            email_data.append({
                'from': email.get('sender_name', email.get('sender', 'Unknown')),
                'subject': email.get('subject', 'No Subject'),
                'preview': email.get('snippet', '')[:150]
            })
        
        prompt = f"""Create a comprehensive daily email digest from these {len(emails)} emails.

Emails:
{json.dumps(email_data, indent=2)}

Include:
1. Quick overview (how many emails, general themes)
2. Key emails that need attention (list 3-5 most important)
3. Suggested actions or follow-ups
4. Any urgent matters

Format in clear sections with headers. Be concise but informative.

Digest:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini digest generation error: {e}")
            return f"Daily Digest: You have {len(emails)} emails. Unable to generate detailed summary."
    
    def analyze_sentiment(self, email_body: str) -> Dict:
        """
        Analyze email sentiment
        
        Args:
            email_body: Email content
        
        Returns:
            Sentiment analysis (positive, negative, neutral) with confidence
        """
        prompt = f"""Analyze the sentiment of this email.

Email:
{email_body}

Return ONLY valid JSON:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation"
}}

JSON:"""
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            json_text = json_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(json_text)
        except Exception as e:
            print(f"Gemini sentiment analysis error: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Unable to analyze"
            }
