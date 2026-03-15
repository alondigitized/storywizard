"""Base agent class with Claude CLI integration."""

from __future__ import annotations

import json
import logging
import subprocess
import time
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from storywizard.config import PipelineConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2.0  # seconds


class BaseAgent:
    """Base class for all Storywizard pipeline agents.

    Each agent has a name, a system prompt defining its role, and can invoke
    Claude via the local CLI to process text and return structured outputs.
    Includes retry logic for transient errors and JSON parse/validation retries.
    """

    name: str = "BaseAgent"
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    def invoke(self, prompt: str, context: str = "") -> str:
        """Call Claude CLI with the agent's system prompt and return text.

        Retries up to MAX_RETRIES times on transient errors with
        exponential backoff.
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n{prompt}"

        logger.info("[%s] Invoking Claude CLI (%s)", self.name, self.config.model_name)

        cmd = [
            "claude", "-p",
            "--output-format", "text",
            "--model", self.config.model_name,
            "--system-prompt", self.system_prompt,
        ]

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = subprocess.run(
                    cmd,
                    input=full_prompt,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"Claude CLI exited with code {result.returncode}: "
                        f"{result.stderr.strip()}"
                    )
                text = result.stdout.strip()
                logger.info("[%s] Response received (%d chars)", self.name, len(text))
                return text
            except subprocess.TimeoutExpired as e:
                last_error = e
                wait = RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "[%s] CLI timeout (attempt %d/%d), retrying in %.1fs",
                    self.name, attempt, MAX_RETRIES, wait,
                )
                time.sleep(wait)
            except RuntimeError as e:
                last_error = e
                wait = RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "[%s] CLI error (attempt %d/%d), retrying in %.1fs: %s",
                    self.name, attempt, MAX_RETRIES, wait, e,
                )
                time.sleep(wait)

        raise RuntimeError(
            f"[{self.name}] Failed after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    def invoke_structured(
        self, prompt: str, response_model: type[T], context: str = ""
    ) -> T:
        """Call Claude and parse the response into a Pydantic model.

        Instructs Claude to return valid JSON matching the model schema,
        then parses and validates it. Retries on JSON parse or validation
        failures up to MAX_RETRIES times.
        """
        schema = json.dumps(response_model.model_json_schema(), indent=2)
        structured_prompt = (
            f"{prompt}\n\n"
            f"Respond with ONLY valid JSON matching this schema:\n"
            f"```json\n{schema}\n```\n"
            f"Do not include any text outside the JSON."
        )

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            raw = self.invoke(structured_prompt, context=context)
            text = self._extract_json(raw)

            try:
                return response_model.model_validate_json(text)
            except (ValidationError, ValueError) as e:
                last_error = e
                logger.warning(
                    "[%s] JSON parse/validation failed (attempt %d/%d): %s",
                    self.name, attempt, MAX_RETRIES, e,
                )
                # Append error context to prompt for next attempt
                structured_prompt = (
                    f"{prompt}\n\n"
                    f"Your previous response was not valid JSON. Error: {e}\n\n"
                    f"Respond with ONLY valid JSON matching this schema:\n"
                    f"```json\n{schema}\n```\n"
                    f"Do not include any text outside the JSON."
                )

        raise RuntimeError(
            f"[{self.name}] Failed to get valid structured response after "
            f"{MAX_RETRIES} attempts: {last_error}"
        ) from last_error

    @staticmethod
    def _extract_json(raw: str) -> str:
        """Extract JSON from potential markdown code fences."""
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text
