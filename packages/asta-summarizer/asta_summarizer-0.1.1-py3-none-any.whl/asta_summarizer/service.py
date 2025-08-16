from .models.SummarizationType import SummarizationType
from .prompts.summary_type_prompts import get_summary_prompt_for_type
from .utils import remove_think_tags

from huggingface_hub import InferenceClient
import openai

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SummarizerService:
    """Service for text summarization using various AI models."""

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = os.getenv("SUMMARIZER_API_KEY"),
        provider: Optional[str] = None,
    ) -> None:
        """Initialize the summarizer service.

        Args:
            model: Model name to use for summarization
            base_url: Base URL for OpenAI-compatible API (mutually exclusive with provider)
            api_key: API key for authentication (defaults to SUMMARIZER_API_KEY env var)
            provider: Provider name for HuggingFace InferenceClient (mutually exclusive with base_url)
        """
        self.api_key = api_key or os.getenv("SUMMARIZER_API_KEY")
        if not self.api_key:
            raise ValueError("Summarizer API key is required")
        if not model:
            raise ValueError("Model name is required")
        if base_url and provider:
            raise ValueError(
                "Cannot specify both base_url and provider - they are mutually exclusive"
            )
        if not base_url and not provider:
            raise ValueError("Must specify either base_url or provider")

        self.base_url = base_url
        self.model = model
        self.provider = provider

        # Initialize the appropriate client
        if self.provider:
            self.client = InferenceClient(
                provider=self.provider,
                api_key=self.api_key,
            )
        else:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _load_prompt(self, length: int) -> str:
        if length <= 0:
            raise ValueError("Length must be positive")

        prompt_path = Path(__file__).parent / "prompts" / "main_prompt.txt"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read().strip().format(length=length)
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading prompt file: {e}")
            raise

    async def summarize(
        self,
        text: str,
        length: int = 1000,
        summarization_type: SummarizationType = SummarizationType.DEFAULT,
    ) -> str:
        """Summarize text using the configured model and client."""
        if not text or not text.strip():
            raise ValueError("Text to summarize cannot be empty")
        if length <= 0:
            raise ValueError("Length must be positive")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._load_prompt(length=length)},
                    {
                        "role": "user",
                        "content": f"{get_summary_prompt_for_type(summarization_type)}{text}",
                    },
                ],
            )

            if not response.choices or not response.choices[0].message.content:
                raise Exception("Empty response from API")

            return remove_think_tags(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in summarize: {e}")
            raise
