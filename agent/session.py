"""Session management for conversation history."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Message:
    """A single message in the conversation."""

    role: str  # 'user' or 'assistant'
    content: str


@dataclass
class Session:
    """In-memory conversation session."""

    messages: List[Message] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the session."""
        self.messages.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the session."""
        self.messages.append(Message(role="assistant", content=content))

    def get_history(self) -> List[Message]:
        """Get the full conversation history."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()

    def format_for_display(self) -> str:
        """Format the conversation history for display."""
        lines = []
        for msg in self.messages:
            prefix = "User:" if msg.role == "user" else "Assistant:"
            lines.append(f"{prefix} {msg.content}")
        return "\n".join(lines)
