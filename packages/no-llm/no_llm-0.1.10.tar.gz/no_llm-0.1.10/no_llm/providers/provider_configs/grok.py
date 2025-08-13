from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_ai.providers.openai import OpenAIProvider as PydanticOpenAIProvider

from no_llm.providers.env_var import EnvVar
from no_llm.providers.provider_configs.openai import OpenAIProvider


class GrokProvider(OpenAIProvider):
    """Grok provider configuration"""

    type: Literal["grok"] = "grok"  # type: ignore
    id: str = "grok"
    name: str = "Grok"
    api_key: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$GROK_API_KEY"),
        description="Name of environment variable containing API key",
    )
    base_url: str | None = Field(default="https://api.x.ai/v1", description="Base URL for Grok API")

    def to_pydantic(self) -> PydanticOpenAIProvider:
        return PydanticOpenAIProvider(
            api_key=str(self.api_key),
            base_url=str(self.base_url),
        )
