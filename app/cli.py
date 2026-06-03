from __future__ import annotations

import argparse
from rich.console import Console
from rich.panel import Panel
from app.models.domain import Goal, Commitment, Observation, Confidence
from app.services.initiative_engine import InitiativeEngine
from app.services.llm import LLMUnavailable, OpenAIReasoner
from app.services.storage import init_db, list_memories, upsert_memory

console = Console()


def cmd_review(_: argparse.Namespace) -> None:
    interventions = InitiativeEngine().run_review()
    if not interventions:
        console.print("No interventions. Suspiciously peaceful. Enjoy it.")
        return
    for item in interventions:
        console.print(Panel.fit(
            f"[bold]{item.type.value.upper()}[/bold] | confidence: {item.confidence.value}\n\n{item.message}\n\n[bold]Evidence[/bold]: {', '.join(item.evidence)}\n[bold]Recommended action[/bold]: {item.recommended_action}",
            title="Chief of Staff Intervention"
        ))


def cmd_memory(args: argparse.Namespace) -> None:
    memories = list_memories(args.type)
    for memory in memories:
        console.print(Panel.fit(str(memory["payload"]), title=f"{memory['type']}::{memory['key']}"))


def cmd_reflect(args: argparse.Namespace) -> None:
    text = args.text
    try:
        extracted = OpenAIReasoner().extract_memories(text)
        for goal in extracted.get("goals", []):
            obj = Goal(**goal)
            upsert_memory("goal", obj.name, obj.model_dump(mode="json"), obj.tier.value)
        for commitment in extracted.get("commitments", []):
            obj = Commitment(**commitment)
            upsert_memory("commitment", obj.title, obj.model_dump(mode="json"), obj.tier.value)
        for idx, observation in enumerate(extracted.get("observations", [])):
            obj = Observation(**observation)
            upsert_memory("observation", f"reflection-{idx}-{obj.created_at.isoformat()}", obj.model_dump(mode="json"), obj.tier.value)
        console.print("Reflection processed with OpenAI extraction.")
    except LLMUnavailable:
        obj = Observation(category="manual_reflection", content=text, confidence=Confidence.MEDIUM)
        upsert_memory("observation", f"manual-{obj.created_at.isoformat()}", obj.model_dump(mode="json"), obj.tier.value)
        console.print("No API key set, so I stored this as a manual observation. Sensible little local goblin mode.")


def main() -> None:
    init_db()
    parser = argparse.ArgumentParser(description="Jack AI Chief of Staff CLI")
    sub = parser.add_subparsers(required=True)

    review = sub.add_parser("review", help="Run initiative review")
    review.set_defaults(func=cmd_review)

    memory = sub.add_parser("memory", help="List memories")
    memory.add_argument("--type", default=None)
    memory.set_defaults(func=cmd_memory)

    reflect = sub.add_parser("reflect", help="Log a reflection")
    reflect.add_argument("text")
    reflect.set_defaults(func=cmd_reflect)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
