import re

from services.nlp_service import NLPService


def test_extract_email_number_from_hash_pattern():
    text = "Please delete email #3 from my inbox."
    assert NLPService.extract_email_number(text) == 3


def test_extract_email_number_from_words():
    text = "Reply to the second one, not the first."
    assert NLPService.extract_email_number(text) == 2


def test_extract_email_number_not_found():
    text = "Just show me my inbox"
    assert NLPService.extract_email_number(text) is None


def test_extract_sender_from_email_address():
    text = "Show messages from alice@example.com this week"
    assert NLPService.extract_sender(text) == "alice@example.com"


def test_extract_sender_from_name_after_from():
    text = "Show me emails from John Doe today"
    assert NLPService.extract_sender(text) == "John Doe"


def test_extract_keywords_filters_stop_words_and_dedupes():
    text = "Show me all important work emails about invoices and payments"
    keywords = NLPService.extract_keywords(text)

    # Should contain core topic words
    assert "important" in keywords or "work" in keywords
    assert "invoices" in keywords or "payments" in keywords

    # Should not contain generic stop words
    for stop in ["show", "email", "emails", "me"]:
        assert stop not in keywords

    # Should be at most 5 unique keywords
    assert len(keywords) <= 5


def test_detect_intent_read_vs_reply_vs_delete_vs_search_vs_digest():
    assert NLPService.detect_intent("Show me my last 5 emails") == "read"
    assert NLPService.detect_intent("Please reply to this message") == "reply"
    assert NLPService.detect_intent("Delete that email forever") == "delete"
    assert NLPService.detect_intent("Search for invoices from ACME") == "search"
    assert NLPService.detect_intent("Give me a digest of today's emails") == "digest"
    assert NLPService.detect_intent("This is some random text") == "unknown"


