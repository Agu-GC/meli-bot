import logging
import requests
from requests.exceptions import RequestException
from api.application.interfaces.llm_service import ILLMService

logger = logging.getLogger(__name__)

class LLMService(ILLMService):
    def __init__(self, base_url: str = "localhost", port: int = 11434, model_name: str = "phi3:instruct", timeout: int = 240, prompt_format: str = "<|user|>\n{prompt}<|end|>\n<|assistant|>"):
        self.base_url = f"http://{base_url}:{port}"
        self.model_name = model_name
        self.timeout = timeout
        self.prompt_format = prompt_format
        logger.info(f"Configurando Ollama - Modelo: {model_name}, Endpoint: {self.base_url}, Timeout: {timeout}s")
        
        self._verify_connection()

    def _verify_connection(self):
        """Verify connection to the Ollama service"""
        try:
            health_url = f"{self.base_url}/api/tags"
            response = requests.get(health_url, timeout=5)
            response.raise_for_status()
            logger.info("Connection to Ollama service verified successfully.")
        except RequestException as e:
            logger.error(f"Error connecting to Ollama service: {str(e)}")
            raise ConnectionError("Error connecting to Ollama service") from e

    def _format_prompt(self, prompt: str) -> str:
        """Aplica el formato al prompt según la configuración"""
        return self.prompt_format.replace("{prompt}", prompt)

    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a response from the LLM based on the provided prompt"""
        try:
            if not prompt.strip():
                raise ValueError("the prompt cannot be empty")
            
            formatted_prompt = self._format_prompt(prompt)
            
            logger.info(f"Generating response for prompt: {formatted_prompt[:50]}... (max_tokens={max_tokens})")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": formatted_prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": 1024,
                        "num_batch": 256,
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_gpu": 1,
                        "main_gpu": 0
                    }
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            full_response = data.get("response", "")
            return full_response.replace(formatted_prompt, "").strip()
            
        except ValueError as e:
            logger.error(f"Validation error generating response: {str(e)}")
            raise
        except RequestException as e:
            logger.error(f"Error connecting to LLM service: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating response: {str(e)}", exc_info=True)
            raise