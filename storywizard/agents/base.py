"""Base agent class with Claude API integration."""

from __future__ import annotations

import json
import logging
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from storywizard.config import PipelineConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """Base class for all Storywizard pipeline agents.

    Each agent has a name, a system prompt defining its role, and can invoke
    Claude to process text and return structured outputs.
    """

    name: str = "BaseAgent"
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def invoke(self, prompt: str, context: str = "") -> str:
        """Call Claude with the agent's system prompt and return text."""
        messages = []
        if context:
            messages.append({"role": "user", "content": context})
            messages.append(
                {"role": "assistant", "content": "Understood. I have the context."}
            )
        messages.append({"role": "user", "content": prompt})

        logger.info("[%s] Invoking Claude (%s)", self.name, self.config.model_name)
        response = self.client.messages.create(
            model=self.config.model_name,
            max_tokens=8192,
            system=self.system_prompt,
            messages=messages,
        )
        text = response.content[0].text
        logger.info("[%s] Response received (%d chars)", self.name, len(text))
        return text

    def invoke_structured(
        self, prompt: str, response_model: type[T], context: str = ""
    ) -> T:
        """Call Claude and parse the response into a Pydantic model.

        Instructs Claude to return valid JSON matching the model schema,
        then parses and validates it.
        """
        schema = json.dumps(response_model.model_json_schema(), indent=2)
        structured_prompt = (
            f"{prompt}\n\n"
            f"Respond with ONLY valid JSON matching this schema:\n"
            f"```json\n{schema}\n```\n"
            f"Do not include any text outside the JSON."
        )

        raw = self.invoke(structured_prompt, context=context)

        # Extract JSON from potential markdown code fences
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last fence lines
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        return response_model.model_validate_json(text)
