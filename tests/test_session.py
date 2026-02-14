"""Tests for session management."""

from agent.session import Message, Session


def test_session_add_messages():
    """Test adding messages to session."""
    session = Session()

    session.add_user_message("Hello")
    session.add_assistant_message("Hi there!")

    assert len(session.messages) == 2
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Hello"
    assert session.messages[1].role == "assistant"
    assert session.messages[1].content == "Hi there!"


def test_session_get_history():
    """Test getting conversation history."""
    session = Session()
    session.add_user_message("Test")

    history = session.get_history()

    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Test"


def test_session_clear():
    """Test clearing session."""
    session = Session()
    session.add_user_message("Test")
    session.clear()

    assert len(session.messages) == 0


def test_session_format_for_display():
    """Test formatting session for display."""
    session = Session()
    session.add_user_message("Hello")
    session.add_assistant_message("Hi!")

    formatted = session.format_for_display()

    assert "User: Hello" in formatted
    assert "Assistant: Hi!" in formatted
