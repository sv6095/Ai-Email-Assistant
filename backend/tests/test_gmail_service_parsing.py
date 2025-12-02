from services.gmail_service import GmailService


class DummyMessagesResource:
    """Minimal fake for service.users().messages() chain used by GmailService."""

    def __init__(self, messages_map):
        # messages_map: id -> message dict
        self._messages_map = messages_map

    def list(self, userId, maxResults, q):
        # Return all message ids up to maxResults; query is ignored for unit test
        ids = [{"id": msg_id} for msg_id in list(self._messages_map.keys())[:maxResults]]
        return DummyRequest({"messages": ids})

    def get(self, userId, id, format):
        return DummyRequest(self._messages_map[id])

    def delete(self, userId, id):
        # For delete_email; we just record that delete was called
        self._messages_map.pop(id, None)
        return DummyRequest({})

    def modify(self, userId, id, body):
        # For mark_as_read / mark_as_unread; just return success
        return DummyRequest({"id": id, "body": body})

    def send(self, userId, body):
        # For send_email / send_reply; echo back id and threadId
        return DummyRequest({"id": "sent-id", "threadId": body.get("threadId")})


class DummyUsersResource:
    def __init__(self, messages_map):
        self._messages = DummyMessagesResource(messages_map)

    def messages(self):
        return self._messages


class DummyGmailApiService:
    def __init__(self, messages_map):
        self._users = DummyUsersResource(messages_map)

    def users(self):
        return self._users


class DummyCredentials:
    """Placeholder credentials to satisfy GmailService __init__ signature."""
    pass


class DummyGmailService(GmailService):
    """Subclass GmailService to inject our fake Gmail API service."""

    def __init__(self, messages_map):
        # Skip parent __init__ to avoid calling googleapiclient.build
        self.service = DummyGmailApiService(messages_map)
        self.user_id = "me"


def make_payload(headers, body_data, mime_type="text/plain", snippet=""):
    return {
        "payload": {
            "headers": headers,
            "body": {"data": body_data} if body_data is not None else {},
            "mimeType": mime_type,
        },
        "snippet": snippet,
        "labelIds": ["INBOX", "UNREAD"],
        "threadId": "thread-1",
    }


def test_get_email_details_parses_headers_and_body_base64_plaintext(monkeypatch):
    import base64

    body_text = "Hello, this is a test email body."
    encoded_body = base64.urlsafe_b64encode(body_text.encode("utf-8")).decode("utf-8")

    headers = [
        {"name": "Subject", "value": "Test Subject"},
        {"name": "From", "value": 'Alice Example <alice@example.com>'},
        {"name": "Date", "value": "Mon, 01 Jan 2024 10:00:00 +0000"},
        {"name": "To", "value": "me@example.com"},
    ]

    messages_map = {
        "msg-1": make_payload(headers=headers, body_data=encoded_body, snippet="snippet text")
    }

    gmail = DummyGmailService(messages_map)

    email = gmail.get_email_by_id("msg-1")

    assert email["id"] == "msg-1"
    assert email["subject"] == "Test Subject"
    assert email["sender"] == 'Alice Example <alice@example.com>'
    assert email["sender_name"] == "Alice Example"
    assert email["sender_email"] == "alice@example.com"
    assert email["to"] == "me@example.com"
    assert email["body"] == body_text
    assert email["unread"] is True


def test_extract_body_falls_back_to_snippet_when_no_body_data(monkeypatch):
    headers = [
        {"name": "Subject", "value": "No Body"},
        {"name": "From", "value": "nobody@example.com"},
    ]
    snippet = "fallback snippet"
    messages_map = {
        "msg-2": make_payload(headers=headers, body_data="", snippet=snippet)
    }

    gmail = DummyGmailService(messages_map)
    email = gmail.get_email_by_id("msg-2")

    # When body can't be decoded, GmailService should fall back to snippet
    assert email["body"] == snippet


def test_parse_sender_handles_plain_email():
    gmail = DummyGmailService({})
    name, email_addr = gmail._parse_sender("plain@example.com")
    assert name == "plain@example.com"
    assert email_addr == "plain@example.com"


def test_mark_as_read_and_unread_use_modify():
    headers = [
        {"name": "Subject", "value": "Mark Read"},
        {"name": "From", "value": "mark@example.com"},
    ]
    messages_map = {
        "msg-3": make_payload(headers=headers, body_data="", snippet="snippet")
    }
    gmail = DummyGmailService(messages_map)

    result_read = gmail.mark_as_read("msg-3")
    assert result_read == {"id": "msg-3", "status": "marked_read"}

    result_unread = gmail.mark_as_unread("msg-3")
    assert result_unread == {"id": "msg-3", "status": "marked_unread"}


def test_delete_email_removes_message_from_store():
    headers = [
        {"name": "Subject", "value": "Delete Me"},
        {"name": "From", "value": "del@example.com"},
    ]
    messages_map = {
        "msg-4": make_payload(headers=headers, body_data="", snippet="snippet")
    }
    gmail = DummyGmailService(messages_map)

    response = gmail.delete_email("msg-4")
    assert response["status"] == "deleted"
    assert "msg-4" not in messages_map


