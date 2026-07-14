"""LLM Provider service for multi-provider LLM support."""

import logging
import json
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class LLMService:
    """Service for interacting with various LLM providers."""

    def __init__(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM service."""
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the selected LLM provider."""
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "cohere":
            self._init_cohere()
        elif self.provider == "huggingface":
            self._init_huggingface()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = self.model or "gpt-3.5-turbo"
            logger.info(f"✅ OpenAI initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Error initializing OpenAI: {e}")
            raise

    def _init_cohere(self):
        """Initialize Cohere client."""
        try:
            import cohere
            self.client = cohere.Client(api_key=self.api_key)
            self.model = self.model or "command"
            logger.info(f"✅ Cohere initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Error initializing Cohere: {e}")
            raise

    def _init_huggingface(self):
        """Initialize HuggingFace Inference API client."""
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(api_key=self.api_key)
            self.model = self.model or "mistralai/Mistral-7B-Instruct-v0.1"
            logger.info(f"✅ HuggingFace initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Error initializing HuggingFace: {e}")
            raise

    def _init_ollama(self):
        """Initialize Ollama local client."""
        try:
            import requests
            self.client = requests.Session()
            self.base_url = "http://localhost:11434"
            self.model = self.model or "llama2"
            logger.info(f"✅ Ollama initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"❌ Error initializing Ollama: {e}")
            raise

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_message: Optional[str] = None
    ) -> str:
        """Generate text using the LLM."""
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, temperature, max_tokens, system_message)
            elif self.provider == "cohere":
                return self._generate_cohere(prompt, temperature, max_tokens)
            elif self.provider == "huggingface":
                return self._generate_huggingface(prompt, temperature, max_tokens)
            elif self.provider == "ollama":
                return self._generate_ollama(prompt, temperature, max_tokens, system_message)
        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            raise

    def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_message: Optional[str]
    ) -> str:
        """Generate using OpenAI."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def _generate_cohere(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Cohere."""
        response = self.client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model=self.model
        )
        return response.generations[0].text

    def _generate_huggingface(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using HuggingFace Inference API."""
        response = self.client.text_generation(
            prompt=prompt,
            model=self.model,
            temperature=temperature,
            max_new_tokens=max_tokens
        )
        return response

    def _generate_ollama(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_message: Optional[str]
    ) -> str:
        """Generate using Ollama local model."""
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"

        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "temperature": temperature,
                "num_predict": max_tokens,
                "stream": False
            }
        )
        result = response.json()
        return result.get("response", "")


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service(provider: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMService:
    """Get or create LLM service."""
    global _llm_service
    if _llm_service is None or _llm_service.provider != provider:
        _llm_service = LLMService(provider, api_key, model)
    return _llm_service
