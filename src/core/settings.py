# src/core/settings.py

import json
from typing import Any, Annotated

from dotenv import find_dotenv
from pydantic import SecretStr, Field, computed_field, BeforeValidator
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
    """
    Simple validator to ensure a string starts with http:// or https://
    """
    if not (v.startswith("http://") or v.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )

    # App mode & network
    MODE: str | None = None
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    AUTH_SECRET: SecretStr | None = None

    # LLM provider keys
    OPENAI_API_KEY: SecretStr | None = None
    DEEPSEEK_API_KEY: SecretStr | None = None
    ANTHROPIC_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None
    GOOGLE_APPLICATION_CREDENTIALS: SecretStr | None = None
    GROQ_API_KEY: SecretStr | None = None
    USE_AWS_BEDROCK: bool = False
    OLLAMA_MODEL: str | None = None
    OLLAMA_BASE_URL: str | None = None
    USE_FAKE_MODEL: bool = False

    # Agent defaults
    DEFAULT_MODEL: AllModelEnum | None = None
    AVAILABLE_MODELS: set[AllModelEnum] = set()

    # Compatible API (OpenAI‐like)
    COMPATIBLE_MODEL: str | None = None
    COMPATIBLE_API_KEY: SecretStr | None = None
    COMPATIBLE_BASE_URL: str | None = None

    # Extra service keys
    OPENWEATHERMAP_API_KEY: SecretStr | None = None
    SERPAPI_API_KEY: SecretStr | None = None
    TAVILY_API_KEY: SecretStr | None = None

    # LangChain tracing / endpoints
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "default"
    LANGCHAIN_ENDPOINT: Annotated[str, BeforeValidator(check_str_is_http)] = (
        "https://api.smith.langchain.com"
    )
    LANGCHAIN_API_KEY: SecretStr | None = None

    # Langfuse tracing / endpoints
    LANGFUSE_TRACING: bool = False
    LANGFUSE_HOST: Annotated[str, BeforeValidator(check_str_is_http)] = (
        "https://cloud.langfuse.com"
    )
    LANGFUSE_PUBLIC_KEY: SecretStr | None = None
    LANGFUSE_SECRET_KEY: SecretStr | None = None

    # Database
    DATABASE_TYPE: DatabaseType = DatabaseType.SQLITE
    SQLITE_DB_PATH: str = "checkpoints.db"

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None

    MONGO_HOST: str | None = None
    MONGO_PORT: int | None = None
    MONGO_DB: str | None = None
    MONGO_USER: str | None = None
    MONGO_PASSWORD: SecretStr | None = None
    MONGO_AUTH_SOURCE: str | None = None

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: SecretStr | None = None
    AZURE_OPENAI_ENDPOINT: Annotated[str, BeforeValidator(check_str_is_http)] | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_MAP: dict[str, str] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        """
        Populate DEFAULT_MODEL and AVAILABLE_MODELS based on which keys are set,
        and validate any provider‐specific requirements (e.g. Azure deployments).
        """
        api_keys = {
            Provider.OPENAI: self.OPENAI_API_KEY,
            Provider.OPENAI_COMPATIBLE: self.COMPATIBLE_BASE_URL and self.COMPATIBLE_MODEL,
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
        active = [p for p, key in api_keys.items() if key]
        if not active:
            raise ValueError("At least one LLM API key must be provided.")

        for provider in active:
            match provider:
                case Provider.OPENAI:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = OpenAIModelName.GPT_4O_MINI
                    self.AVAILABLE_MODELS.update(OpenAIModelName)
                case Provider.OPENAI_COMPATIBLE:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = OpenAICompatibleName.OPENAI_COMPATIBLE
                    self.AVAILABLE_MODELS.update(OpenAICompatibleName)
                case Provider.DEEPSEEK:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = DeepseekModelName.DEEPSEEK_CHAT
                    self.AVAILABLE_MODELS.update(DeepseekModelName)
                case Provider.ANTHROPIC:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = AnthropicModelName.HAIKU_3
                    self.AVAILABLE_MODELS.update(AnthropicModelName)
                case Provider.GOOGLE:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = GoogleModelName.GEMINI_20_FLASH
                    self.AVAILABLE_MODELS.update(GoogleModelName)
                case Provider.VERTEXAI:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = VertexAIModelName.GEMINI_20_FLASH
                    self.AVAILABLE_MODELS.update(VertexAIModelName)
                case Provider.GROQ:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = GroqModelName.LLAMA_31_8B
                    self.AVAILABLE_MODELS.update(GroqModelName)
                case Provider.AWS:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = AWSModelName.BEDROCK_HAIKU
                    self.AVAILABLE_MODELS.update(AWSModelName)
                case Provider.OLLAMA:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = OllamaModelName.OLLAMA_GENERIC
                    self.AVAILABLE_MODELS.update(OllamaModelName)
                case Provider.FAKE:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = FakeModelName.FAKE
                    self.AVAILABLE_MODELS.update(FakeModelName)
                case Provider.AZURE_OPENAI:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = AzureOpenAIModelName.AZURE_GPT_4O_MINI
                    self.AVAILABLE_MODELS.update(AzureOpenAIModelName)
                    # validate Azure settings
                    if not self.AZURE_OPENAI_API_KEY:
                        raise ValueError("AZURE_OPENAI_API_KEY must be set")
                    if not self.AZURE_OPENAI_ENDPOINT:
                        raise ValueError("AZURE_OPENAI_ENDPOINT must be set")
                    if not self.AZURE_OPENAI_DEPLOYMENT_MAP:
                        raise ValueError("AZURE_OPENAI_DEPLOYMENT_MAP must be set")
                    if isinstance(self.AZURE_OPENAI_DEPLOYMENT_MAP, str):
                        try:
                            self.AZURE_OPENAI_DEPLOYMENT_MAP = json.loads(
                                self.AZURE_OPENAI_DEPLOYMENT_MAP
                            )
                        except Exception as e:
                            raise ValueError(f"Invalid AZURE_OPENAI_DEPLOYMENT_MAP JSON: {e}")
                case _:
                    raise ValueError(f"Unknown provider: {provider}")

    @computed_field
    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    def is_dev(self) -> bool:
        return self.MODE == "dev"


settings = Settings()
