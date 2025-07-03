# src/core/settings.py

import json
from typing import Any
from dotenv import find_dotenv
from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import (
    Provider,
    AllModelEnum,
    OpenAIModelName,
    OpenAICompatibleName,
    DeepseekModelName,
    AnthropicModelName,
    GoogleModelName,
    VertexAIModelName,
    GroqModelName,
    AWSModelName,
    OllamaModelName,
    FakeModelName,
    AzureOpenAIModelName,
    DatabaseType,
)

def check_str_is_http(v: str) -> str:
    if not (v.startswith("http://") or v.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")
    return v

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_prefix="",
        validate_default=True,
    )

    # LLM provider keys
    OPENAI_API_KEY: SecretStr | None = None
    COMPATIBLE_BASE_URL: str | None = None
    COMPATIBLE_MODEL: str | None = None
    DEEPSEEK_API_KEY: SecretStr | None = None
    ANTHROPIC_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None
    GOOGLE_APPLICATION_CREDENTIALS: SecretStr | None = None
    GROQ_API_KEY: SecretStr | None = None
    USE_AWS_BEDROCK: bool = False
    OLLAMA_MODEL: str | None = None
    OLLAMA_BASE_URL: str | None = None
    USE_FAKE_MODEL: bool = False
    AZURE_OPENAI_API_KEY: SecretStr | None = None

    @computed_field
    def api_keys(self) -> dict[Provider, Any]:
        return {
            Provider.OPENAI: self.OPENAI_API_KEY,
            Provider.OPENAI_COMPATIBLE: (self.COMPATIBLE_BASE_URL and self.COMPATIBLE_MODEL),
            Provider.DEEPSEEK: self.DEEPSEEK_API_KEY,
            Provider.ANTHROPIC: self.ANTHROPIC_API_KEY,
            Provider.GOOGLE: self.GOOGLE_API_KEY,
            Provider.VERTEXAI: self.GOOGLE_APPLICATION_CREDENTIALS,
            Provider.GROQ: self.GROQ_API_KEY,
            Provider.AWS: self.USE_AWS_BEDROCK,
            Provider.OLLAMA: self.OLLAMA_MODEL,
            Provider.FAKE: self.USE_FAKE_MODEL,
            Provider.AZURE_OPENAI: self.AZURE_OPENAI_API_KEY,
        }

    # …any other settings you have below…
