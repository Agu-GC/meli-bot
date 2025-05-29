from abc import ABC, abstractmethod

class IRAGService(ABC):
    
    @abstractmethod
    def generate_response(self, user_id: str, user_query: str) -> str:
        """Generate an answer based on the query and retrieved context."""
        pass
