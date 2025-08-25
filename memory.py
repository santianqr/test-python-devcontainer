"""Conversation memory management for WhatsApp AI Agent."""

from typing import Any

from database import Conversation, get_session


class ConversationMemory:
    """Manages conversation history and context."""

    def __init__(self, chat_id: str):
        """Initialize conversation memory for a specific chat."""
        self.chat_id = chat_id

    def add_message(self, user_message: str, assistant_response: str) -> None:
        """Store a conversation turn in the database."""
        session = get_session()
        try:
            conversation = Conversation(
                chat_id=self.chat_id,
                user_message=user_message,
                assistant_response=assistant_response,
            )
            session.add(conversation)
            session.commit()
        finally:
            session.close()

    def get_recent_messages(self, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve recent conversation history."""
        session = get_session()
        try:
            conversations = (
                session.query(Conversation)
                .filter(Conversation.chat_id == self.chat_id)
                .order_by(Conversation.timestamp.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "user_message": conv.user_message,
                    "assistant_response": conv.assistant_response,
                    "timestamp": conv.timestamp.isoformat(),
                }
                for conv in reversed(conversations)  # Reverse to get chronological order
            ]
        finally:
            session.close()

    def build_conversation_context(self, limit: int = 5) -> str:
        """Build conversation context string for the LLM."""
        recent_messages = self.get_recent_messages(limit)

        if not recent_messages:
            return ""

        context = "Previous conversation:\n"
        for msg in recent_messages:
            context += f"User: {msg['user_message']}\n"
            if msg["assistant_response"]:
                context += f"Assistant: {msg['assistant_response']}\n"

        return context

    def get_conversation_summary(self) -> dict[str, Any]:
        """Get conversation statistics and summary."""
        session = get_session()
        try:
            total_messages = session.query(Conversation).filter(Conversation.chat_id == self.chat_id).count()

            latest_message = (
                session.query(Conversation)
                .filter(Conversation.chat_id == self.chat_id)
                .order_by(Conversation.timestamp.desc())
                .first()
            )

            return {
                "chat_id": self.chat_id,
                "total_messages": total_messages,
                "latest_timestamp": (latest_message.timestamp.isoformat() if latest_message else None),
                "has_history": total_messages > 0,
            }
        finally:
            session.close()

    def clear_history(self) -> int:
        """Clear conversation history for this chat."""
        session = get_session()
        try:
            deleted_count = session.query(Conversation).filter(Conversation.chat_id == self.chat_id).delete()
            session.commit()
            return deleted_count
        finally:
            session.close()


def get_all_active_chats() -> list[dict[str, Any]]:
    """Get list of all active chats with recent activity."""
    session = get_session()
    try:
        from sqlalchemy import func

        active_chats = (
            session.query(
                Conversation.chat_id,
                func.count(Conversation.id).label("message_count"),
                func.max(Conversation.timestamp).label("last_activity"),
            )
            .group_by(Conversation.chat_id)
            .order_by(func.max(Conversation.timestamp).desc())
            .all()
        )

        return [
            {
                "chat_id": chat.chat_id,
                "message_count": chat.message_count,
                "last_activity": chat.last_activity.isoformat(),
            }
            for chat in active_chats
        ]
    finally:
        session.close()
