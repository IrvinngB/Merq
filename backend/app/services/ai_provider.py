"""
AI Provider Module
Handles connections to different AI backends (Gemini, Ollama).
"""

import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from ollama import Client

# Force load .env
load_dotenv()

# Logger setup
def log_provider(msg):
    print(f"[AI PROVIDER] {msg}", flush=True)

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(self, prompt: str, json_mode: bool = False) -> str:
        """Generate content from the provider."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass


class GeminiProvider(AIProvider):
    """Google Gemini Provider."""
    
    def __init__(self):
        self._api_key = os.getenv("GEMINI_API_KEY", "")
        self._model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._client = None
        self._available = False
        
        if self._api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model_name)
                self._available = True
                log_provider(f"Gemini initialized ({self._model_name})")
            except ImportError:
                log_provider("Gemini skipped: google-generativeai package not installed")
            except Exception as e:
                log_provider(f"Gemini initialization error: {e}")
        else:
            log_provider("Gemini skipped: No API Key found")

    @property
    def name(self) -> str:
        return "Gemini"

    @property
    def is_available(self) -> bool:
        return self._available and self._client is not None

    def generate(self, prompt: str, json_mode: bool = False) -> str:
        if not self.is_available:
            raise ConnectionError("Gemini is not available")
            
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 4096,
        }
        
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
            
        response = self._client.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text


class OllamaProvider(AIProvider):
    """Ollama Local Provider."""
    
    def __init__(self):
        self._host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._model_name = os.getenv("OLLAMA_MODEL", "gemma2")
        self._client = Client(host=self._host)
        # Ollama is always considered "available" to try connecting
        log_provider(f"Ollama configured ({self._host})")

    @property
    def name(self) -> str:
        return "Ollama"

    @property
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, json_mode: bool = False) -> str:
        response = self._client.generate(
            model=self._model_name,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 4096,
            }
        )
        return response["response"]


class AIGateway:
    """
    Gateway to manage AI providers with fallback strategy.
    Default: Gemini -> Ollama
    """
    
    def __init__(self):
        self.gemini = GeminiProvider()
        self.ollama = OllamaProvider()

    def generate(self, prompt: str, json_mode: bool = False) -> tuple[str, str]:
        """
        Generate content using available providers.
        Returns: (response_text, provider_name)
        """
        # Try Gemini
        if self.gemini.is_available:
            try:
                log_provider("Using Gemini...")
                response = self.gemini.generate(prompt, json_mode)
                return response, self.gemini.name
            except Exception as e:
                log_provider(f"Gemini failed: {e}. Falling back...")
        
        # Fallback to Ollama
        try:
            log_provider("Using Ollama...")
            response = self.ollama.generate(prompt, json_mode)
            return response, self.ollama.name
        except Exception as e:
            log_provider(f"Ollama failed: {e}")
            raise e
