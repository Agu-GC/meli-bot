from abc import ABC, abstractmethod

class ILLMService(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a response based on the given prompt and optional context."""
        pass
