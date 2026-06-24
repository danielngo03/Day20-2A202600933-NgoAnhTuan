"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
import os
from openai import OpenAI

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client using OpenAI SDK (configured for OpenRouter)."""

    def __init__(self):
        settings = get_settings()
        # OpenRouter setup
        self.model = settings.openai_model
        
        api_key = settings.openrouter_api_key or settings.openai_api_key
        base_url = settings.openrouter_base_url or "https://openrouter.ai/api/v1"
        
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        
        content = response.choices[0].message.content or ""
        
        # OpenRouter specific token usage might vary, but typical OpenAI usage format:
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        
        # Cost is tricky since OpenRouter charges per model, setting to 0.0 for now
        cost_usd = 0.0
        
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd
        )
