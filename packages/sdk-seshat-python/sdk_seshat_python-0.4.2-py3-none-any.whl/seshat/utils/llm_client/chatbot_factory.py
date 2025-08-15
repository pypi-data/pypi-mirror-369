import os
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Callable, Dict

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel


@dataclass
class LLMConfig:
    model_name: str
    provider: str


class LLMProvider(StrEnum):
    OPENAI = "openai"


class OpenAIModels(StrEnum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"


class AvailableLLMs(Enum):
    GPT_4O = LLMConfig(model_name=OpenAIModels.GPT_4O, provider=LLMProvider.OPENAI)
    GPT_4O_MINI = LLMConfig(
        model_name=OpenAIModels.GPT_4O_MINI, provider=LLMProvider.OPENAI
    )
    GPT_4 = LLMConfig(model_name=OpenAIModels.GPT_4, provider=LLMProvider.OPENAI)
    GPT_3_5_TURBO = LLMConfig(
        model_name=OpenAIModels.GPT_3_5_TURBO, provider=LLMProvider.OPENAI
    )
    GPT_4_1 = LLMConfig(model_name=OpenAIModels.GPT_4_1, provider=LLMProvider.OPENAI)
    GPT_4_1_MINI = LLMConfig(
        model_name=OpenAIModels.GPT_4_1_MINI, provider=LLMProvider.OPENAI
    )
    GPT_4_1_NANO = LLMConfig(
        model_name=OpenAIModels.GPT_4_1_NANO, provider=LLMProvider.OPENAI
    )


def _create_openai_client(model: OpenAIModels, **kwargs) -> BaseChatModel:
    return ChatOpenAI(
        model=model,
        api_key=os.environ.get("OPENAI_API_KEY"),
        **kwargs,
    )


class LLMClientFactory:
    """Factory class for creating LLM clients based on model name."""

    _provider_handlers: Dict[str, Callable] = {
        LLMProvider.OPENAI: _create_openai_client
    }

    @classmethod
    def register_provider(cls, provider: str, handler_func: Callable):
        cls._provider_handlers[provider] = handler_func

    @classmethod
    def create(cls, model_name: AvailableLLMs, **kwargs) -> BaseChatModel:
        model_config = model_name.value

        if model_config.provider in cls._provider_handlers:
            return cls._provider_handlers[model_config.provider](
                model_config.model_name, **kwargs
            )

        raise ValueError(f"Provider {model_config.provider} is not implemented.")
