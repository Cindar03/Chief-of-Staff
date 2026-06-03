from __future__ import annotations

import json
from openai import OpenAI
from app.core.config import settings
from app.services.constitution import JACK_CONSTITUTION, DELEGATION_CHARTER


class LLMUnavailable(Exception):
    pass


class OpenAIReasoner:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise LLMUnavailable("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def extract_memories(self, user_text: str) -> dict:
        """Return structured memory candidates from a user reflection."""
        prompt = f"""
You are Jack's AI Chief of Staff. Extract durable memories only.

Constitution:
{JACK_CONSTITUTION}

Delegation charter:
{DELEGATION_CHARTER}

User text:
{user_text}

Return JSON with keys: goals, commitments, observations. Each value must be a list.
"""
        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt,
            text={"format": {"type": "json_object"}},
        )
        return json.loads(response.output_text)
