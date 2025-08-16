import os
import requests
from .base import BaseLLM


class HuggingFaceLLM(BaseLLM):
    def __init__(
        self, model_name: str = "HuggingFaceH4/zephyr-7b-beta", api_key: str = None
    ):
        """Initialize Hugging Face LLM client using the Inference API (online)."""
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HF_API_KEY")
        if not self.api_key:
            # Prompt the user for their API key
            try:
                self.api_key = input("Enter your Hugging Face API key: ").strip()
            except EOFError:
                raise RuntimeError("Hugging Face API key is required to use this LLM.")
            os.environ["HF_API_KEY"] = self.api_key
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.headers = (
            {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )

    def generate(self, prompt: str) -> str:
        """Generate response using Hugging Face Inference API."""
        payload = {"inputs": prompt}
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            # The response format may vary by model; handle common cases
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"][len(prompt) :].strip()
            elif isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"][len(prompt) :].strip()
            else:
                return str(data)
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate response from Hugging Face API: {e}"
            )

    def is_available(self) -> bool:
        """Check if the API is reachable."""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
