# src/core/llm.py

from functools import cache
from typing import TypeAlias

from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_community.chat_models import FakeListChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from src.core.settings import settings
from src.schema.models import (
    AllModelEnum,
    AnthropicModelName,
    AWSModelName,
    AzureOpenAIModelName,
    DeepseekModelName,
    FakeModelName,
    GoogleModelName,
    GroqModelName,
    OllamaModelName,
    OpenAICompatibleName,
    OpenAIModelName,
    VertexAIModelName,
)

# -----------------------------------------------------------------------------
# Build lookup table: model-enum → API model name string
# -----------------------------------------------------------------------------
_MODEL_TABLE = (
    {m: m.value for m in OpenAIModelName}
    | {m: m.value for m in OpenAICompatibleName}
    | {m: m.value for m in AzureOpenAIModelName}
    | {m: m.value for m in DeepseekModelName}
    | {m: m.value for m in AnthropicModelName}
    | {m: m.value for m in GoogleModelName}
    | {m: m.value for m in VertexAIModelName}
    | {m: m.value for m in GroqModelName}
    | {m: m.value for m in AWSModelName}
    | {m: m.value for m in OllamaModelName}
    | {m: m.value for m in FakeModelName}
)

# -----------------------------------------------------------------------------
# Union type for returned model clients
# -----------------------------------------------------------------------------
ModelT: TypeAlias = (
    AzureChatOpenAI
    | ChatOpenAI
    | ChatAnthropic
    | ChatGoogleGenerativeAI
    | ChatVertexAI
    | ChatGroq
    | ChatBedrock
    | ChatOllama
    | FakeListChatModel
)

# -----------------------------------------------------------------------------
# Factory: pick the right client based on enum, with OpenRouter → OpenAI fallback
# -----------------------------------------------------------------------------
@cache
def get_model(model_name: AllModelEnum) -> ModelT:
    api_model_name = _MODEL_TABLE.get(model_name)
    if not api_model_name:
        raise ValueError(f"Unsupported model: {model_name}")

    # === 1a) GPT-3.5 Turbo (explicit) ===
    if model_name == AllModelEnum.GPT_3_5_TURBO:
        return ChatOpenAI(
            model=api_model_name,
            temperature=0.5,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )

    # === 1) OpenAI direct ===
    if model_name in OpenAIModelName:
        return ChatOpenAI(
            model=api_model_name,
            temperature=0.5,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )

    # === 2) OpenAI-Compatible (OpenRouter) w/ fallback to real OpenAI ===
    if model_name in OpenAICompatibleName:
        # a) Try OpenRouter first
        if settings.COMPATIBLE_BASE_URL and settings.COMPATIBLE_API_KEY:
            try:
                return ChatOpenAI(
                    model=api_model_name,
                    temperature=0.5,
                    streaming=True,
                    api_key=settings.COMPATIBLE_API_KEY,
                    base_url=settings.COMPATIBLE_BASE_URL,
                )
            except Exception:
                # on any error, fall through to (b)
                pass
        # b) Fallback to official OpenAI
        return ChatOpenAI(
            model=api_model_name,
            temperature=0.5,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )

    # === 3) Azure OpenAI ===
    if model_name in AzureOpenAIModelName:
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            deployment_name=api_model_name,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0.5,
            streaming=True,
            timeout=60,
            max_retries=3,
        )

    # === 4) DeepSeek ===
    if model_name in DeepseekModelName:
        return ChatOpenAI(
            model=api_model_name,
            temperature=0.5,
            streaming=True,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )

    # === 5) Anthropic ===
    if model_name in AnthropicModelName:
        return ChatAnthropic(model=api_model_name, temperature=0.5, streaming=True)

    # === 6) Google Bard ===
    if model_name in GoogleModelName:
        return ChatGoogleGenerativeAI(
            model=api_model_name, temperature=0.5, streaming=True
        )

    # === 7) Google Vertex AI ===
    if model_name in VertexAIModelName:
        return ChatVertexAI(model=api_model_name, temperature=0.5, streaming=True)

    # === 8) Groq ===
    if model_name in GroqModelName:
        return ChatGroq(
            model=api_model_name,
            temperature=0.0 if model_name.name.startswith("LLAMA_GUARD") else 0.5,
        )

    # === 9) AWS Bedrock ===
    if model_name in AWSModelName:
        return ChatBedrock(model_id=api_model_name, temperature=0.5)

    # === 10) Ollama ===
    if model_name in OllamaModelName:
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            temperature=0.5,
            base_url=settings.OLLAMA_BASE_URL or None,
        )

    # === 11) Fake/Test model ===
    if model_name in FakeModelName:
        return FakeListChatModel(responses=["This is a test response from the fake model."])

    # Should never happen
    raise ValueError(f"Unsupported model: {model_name}")
