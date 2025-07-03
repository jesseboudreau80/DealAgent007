# src/core/enums.py

from enum import Enum

class Provider(str, Enum):
    OPENAI               = "openai"
    OPENAI_COMPATIBLE    = "openai_compatible"
    DEEPSEEK             = "deepseek"
    ANTHROPIC            = "anthropic"
    GOOGLE               = "google"
    VERTEXAI             = "vertexai"
    GROQ                 = "groq"
    AWS                  = "aws"
    OLLAMA               = "ollama"
    FAKE                 = "fake"
    AZURE_OPENAI         = "azure_openai"

class DatabaseType(str, Enum):
    SQLITE   = "sqlite"
    POSTGRES = "postgres"

class AllModelEnum(str, Enum):
    """
    Union of all model-name enums. Populate this
    with your specific model identifiers if you need
    to restrict to a fixed set of model names.
    """
    GPT_4O_MINI         = "gpt-4o-mini"
    OPENAI_COMPATIBLE   = "openai-compatible"
    DEEPSEEK_CHAT       = "deepseek-chat"
    HAIKU_3             = "haiku-3"
    GEMINI_20_FLASH     = "gemini-2.0-flash"
    LLAMA_31_8B         = "llama-3.1-8b"
    # …etc…
