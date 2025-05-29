from abc import ABC, abstractmethod
from api.domain.entities import Conversation

class IConversationRepository(ABC):
    @abstractmethod
    def get_conversation_history(self, user_id: str) -> list[Conversation]:
        """Retrieve a conversation by user ID."""
        pass

    @abstractmethod
    def save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation."""
        pass