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
    GPT_4O_MINI         = "gpt-4o-mini"
    GPT_3_5_TURBO       = "gpt-3.5-turbo"
    OPENAI_COMPATIBLE   = "openai-compatible"
    DEEPSEEK_CHAT       = "deepseek-chat"
    HAIKU_3             = "haiku-3"
    GEMINI_20_FLASH     = "gemini-2.0-flash"
    LLAMA_31_8B         = "llama-3.1-8b"
    # …etc…

class OpenAIModelName(str, Enum):
    GPT_4O              = "gpt-4o"
    GPT_4O_MINI    = "gpt-4o-mini"
    GPT_3_5_TURBO       = "gpt-3.5-turbo"
    # add other OpenAI model identifiers here

class OpenAICompatibleName(str, Enum):
    OPENAI_COMPATIBLE   = "openai-compatible"
    OPENAI_GPT_4O     = "openai/gpt-4o"
    OPENAI_GPT_4O_MINI     = "openai/gpt-4o-mini"
    OPENAI_GPT_3_5_TURBO     = "openai/gpt-3.5-turbo"

class DeepseekModelName(str, Enum):
    DEEPSEEK_CHAT       = "deepseek-chat"

class AnthropicModelName(str, Enum):
    CLAUDE_V1           = "claude-v1"
    CLAUDE_V1_3         = "claude-v1.3"

class GoogleModelName(str, Enum):
    BISON               = "bison"
    GEMINI              = "gemini"

class VertexAIModelName(str, Enum):
    GEMINI_20_FLASH     = "gemini-2.0-flash"

class GroqModelName(str, Enum):
    GROQ_1               = "groq-1"

class AWSModelName(str, Enum):
    BEDROCK             = "bedrock"

class OllamaModelName(str, Enum):
    OLLAMA_MODEL        = "ollama-model"

class FakeModelName(str, Enum):
    FAKE_MODEL          = "fake-model"

class AzureOpenAIModelName(str, Enum):
    AZURE_ADA           = "azure-ada"
    AZURE_GPT4          = "azure-gpt4"
