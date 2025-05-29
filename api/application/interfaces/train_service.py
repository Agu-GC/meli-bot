from abc import ABC, abstractmethod

class ITrainService(ABC):
    @abstractmethod
    def train(self, user_id: str, user_query: str) -> None:
        """Train the model with the company information."""
        pass
