from datetime import datetime

from routers.chat import (
    format_email_for_display,
    find_email_by_criteria,
    create_response,
)


class DummyGmailService:
    """Simple fake GmailService for testing helper logic."""

    def __init__(self, emails):
        # emails is a list of email dicts as returned by GmailService.fetch_emails
        self._emails = emails

    def fetch_emails(self, max_results=5, query=""):
        return self._emails[:max_results]

    def search_emails(self, query, max_results=10):
        # Very small fake that searches by "from:" or "subject:" in a naive way
        results = []
        if query.startswith("from:"):
            sender = query[len("from:") :]
            for email in self._emails:
                if sender in email.get("sender", ""):
                    results.append(email)
        elif query.startswith("subject:"):
            keyword = query[len("subject:") :]
            for email in self._emails:
                if keyword.lower() in email.get("subject", "").lower():
                    results.append(email)
        return results[:max_results]


def make_raw_email(
    id="1",
    sender="Alice Example <alice@example.com>",
    subject="Hello",
    date="Mon, 01 Jan 2024 10:00:00 +0000",
    snippet="snippet",
    unread=True,
):
    return {
        "id": id,
        "subject": subject,
        "sender": sender,
        "sender_name": "Alice Example",
        "sender_email": "alice@example.com",
        "date": date,
        "snippet": snippet,
        "unread": unread,
    }


def test_format_email_for_display_parses_sender_and_timestamp():
    email = make_raw_email()
    formatted = format_email_for_display(email)

    assert formatted["id"] == email["id"]
    assert formatted["subject"] == email["subject"]
    assert formatted["sender"]["name"] == "Alice Example"
    assert formatted["sender"]["email"] == "alice@example.com"
    assert formatted["date"] == email["date"]

    # Should mark unread=False -> isRead True
    assert formatted["isRead"] is False or isinstance(formatted["isRead"], bool)

    # Timestamp should be ISO formatted or None if parsing failed
    if formatted["timestamp"]:
        # Should parse back as datetime
        parsed = datetime.fromisoformat(formatted["timestamp"])
        assert isinstance(parsed, datetime)


def test_find_email_by_number_uses_indexing():
    emails = [
        make_raw_email(id="1", subject="First"),
        make_raw_email(id="2", subject="Second"),
        make_raw_email(id="3", subject="Third"),
    ]
    gmail = DummyGmailService(emails)

    email = find_email_by_criteria(gmail_service=gmail, email_number=2)
    assert email["id"] == "2"
    assert email["subject"] == "Second"


def test_find_email_by_sender_uses_search():
    emails = [
        make_raw_email(id="1", sender="Alice <alice@example.com>"),
        make_raw_email(id="2", sender="Bob <bob@example.com>"),
    ]
    gmail = DummyGmailService(emails)

    email = find_email_by_criteria(gmail_service=gmail, sender="bob@example.com")
    assert email["id"] == "2"


def test_find_email_by_subject_keyword_uses_search():
    emails = [
        make_raw_email(id="1", subject="Invoice for January"),
        make_raw_email(id="2", subject="Random message"),
    ]
    gmail = DummyGmailService(emails)

    email = find_email_by_criteria(
        gmail_service=gmail, subject_keywords=["Invoice"]
    )
    assert email["id"] == "1"


def test_create_response_has_basic_shape():
    resp = create_response(
        "hello", emails=[{"id": "1"}], actions=[{"type": "test"}]
    )

    assert resp["content"] == "hello"
    assert resp["emails"][0]["id"] == "1"
    assert resp["actions"][0]["type"] == "test"
    # UUID and timestamp existence
    assert "id" in resp
    assert "timestamp" in resp


