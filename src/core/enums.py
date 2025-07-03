# src/core/enums.py
from enum import Enum

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"

class AllModelEnum(str, Enum):
    """
    Union of all model-name enums. Populate this
    with your specific model identifiers if you need
    to restrict to a fixed set of model names.
    """
    # Example placeholders; adjust to your actual model‐names:
    GPT_4O_MINI = "gpt-4o-mini"
    OPENAI_COMPATIBLE = "openai-compatible"
    DEEPSEEK_CHAT = "deepseek-chat"
    HAIKU_3 = "haiku-3"
    GEMINI_20_FLASH = "gemini-2.0-flash"
    LLAMA_31_8B = "llama-3.1-8b"
    # …etc…
