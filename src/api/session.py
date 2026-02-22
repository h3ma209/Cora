"""
Conversation Session Manager for Cora
Manages chat history and context for multi-turn conversations
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from src.config import MAX_TURNS


class ConversationSession:
    """Represents a single conversation session with history"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.metadata = {}
        # New fields for enhanced memory
        self.summary = ""  # High-level conversation summary
        self.entities = {}  # Extracted entities (Name, Phone, Issue, etc.)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history"""
        now = datetime.now()
        # Calculate relative time string (e.g. "T+0m", "T+5m")
        delta = now - self.created_at
        minutes = int(delta.total_seconds() / 60)
        time_str = f"T+{minutes}m"

        message = {
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": now.isoformat(),
            "relative_time": time_str,
            "metadata": metadata or {},
        }
        self.messages.append(message)
        self.last_activity = now

    def get_history(self, max_turns: int = MAX_TURNS) -> List[Dict]:
        """Get recent conversation history (limited to last N turns)"""
        # Return last N pairs of user-assistant messages
        return self.messages[-(max_turns * 2) :]

    def get_context_string(self, max_turns: int = MAX_TURNS) -> str:
        """Format conversation history as a context string for the LLM"""

        context_parts = []

        # 1. Add Summary if available (Memory Compression)
        if self.summary:
            context_parts.append(f"PREVIOUS SUMMARY:\n{self.summary}\n")

        # 2. Add Extracted Entities if available
        if self.entities:
            context_parts.append("KNOWN DETAILS:")
            for k, v in self.entities.items():
                context_parts.append(f"- {k}: {v}")
            context_parts.append("")

        # 3. Add Recent History with Timestamps
        history = self.get_history(max_turns)
        if not history:
            return "\n".join(context_parts)

        context_parts.append("RECENT CONVERSATION:")
        for msg in history:
            role = "Customer" if msg["role"] == "user" else "You"
            time_tag = f"[{msg.get('relative_time', 'T+?m')}]"
            context_parts.append(f"{time_tag} {role}: {msg['content']}")

        # context_parts.append("\nCurrent question:")
        return "\n".join(context_parts)

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired due to inactivity"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    """Manages multiple conversation sessions"""

    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = session_timeout_minutes

    def create_session(self) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id)
        return session_id

    def get_session(self, session_id: Optional[str] = None) -> ConversationSession:
        """Get existing session or create new one"""
        # Clean up expired sessions first
        self._cleanup_expired_sessions()

        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired(self.session_timeout):
                return session
            else:
                # Session expired, remove it
                del self.sessions[session_id]

        # Create new session
        new_session_id = self.create_session()
        return self.sessions[new_session_id]

    def add_message(
        self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None
    ):
        """Add a message to a session"""
        if session_id in self.sessions:
            self.sessions[session_id].add_message(role, content, metadata)

    def get_session_history(
        self, session_id: str, max_turns: int = MAX_TURNS
    ) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].get_history(max_turns)
        return []

    def _cleanup_expired_sessions(self):
        """Remove expired sessions to free memory"""
        expired = [
            sid
            for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        for sid in expired:
            del self.sessions[sid]
            print(f"Cleaned up expired session: {sid}")

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        self._cleanup_expired_sessions()
        return len(self.sessions)


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(session_timeout_minutes=120)
    return _session_manager
