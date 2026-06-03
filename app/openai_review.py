import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Jack's AI Chief of Staff.

Your job is to produce evidence-based shadow reviews.

Rules:
- Separate facts, interpretations, suggestions, and confidence.
- Do not claim certainty without evidence.
- Do not make unsupported emotional assumptions.
- Challenge drift, avoidance, ambiguity, and threshold friction.
- Be direct, warm, sharp, and practical.
- Do not suggest contacting other people without approval.
- Return valid JSON only.
"""

def generate_ai_review(memory_items: list[dict]) -> dict:
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "mode": "fallback",
            "facts": ["OPENAI_API_KEY is not configured."],
            "interpretations": [],
            "suggestions": ["Add OPENAI_API_KEY in Render environment variables."],
            "confidence": "high"
        }

    user_prompt = {
        "task": "Generate a shadow review for Jack.",
        "memory_items": memory_items,
        "output_schema": {
            "mode": "ai_shadow_review",
            "facts": ["observable evidence only"],
            "interpretations": ["careful pattern-based interpretations"],
            "suggestions": ["specific suggested next steps"],
            "confidence": "low | medium | high",
            "intervention": "one concise message Jack could be shown"
        }
    }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_prompt)}
        ],
        temperature=0.3,
    )

    text = response.output_text

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "mode": "ai_shadow_review_parse_error",
            "facts": ["AI returned non-JSON output."],
            "interpretations": [],
            "suggestions": ["Inspect raw_output and tighten the prompt."],
            "confidence": "medium",
            "raw_output": text
        }
