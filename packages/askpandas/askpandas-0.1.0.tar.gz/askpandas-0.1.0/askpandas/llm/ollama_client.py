import requests
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(
        self, model_name: str = "mistral", host: str = "http://localhost:11434"
    ):
        """Initialize Ollama LLM client."""
        self.model_name = model_name
        self.host = host
        self.endpoint = f"{host}/api/generate"

    def generate(self, prompt: str) -> str:
        """Generate response using Ollama."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama failed to generate response: {e}")

    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
