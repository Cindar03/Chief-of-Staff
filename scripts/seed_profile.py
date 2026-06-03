import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import date
from app.models.domain import Goal, Commitment, Observation, Confidence, MemoryTier
from app.services.storage import init_db, upsert_memory

init_db()

goals = [
    Goal(
        name="Iceland October 2026",
        description="Travel to Iceland later this year, potentially compare Ring Road self-drive vs a shorter city-based trip.",
        status="deferred_intentionally",
        horizon="October 2026",
        review_date="2026-08-15",
        next_action="Research Ring Road costs vs city-based itinerary, including budget and car rental implications.",
    ),
    Goal(
        name="Career influence project",
        description="Increase strategic influence at work; be requested for opinions and experience by higher-level colleagues.",
        next_action="Track influence signals: invited earlier, requested by name, asked for judgement, involved in strategic discussion.",
    ),
    Goal(
        name="Social confidence and dating",
        description="Use Bumble and explore clubs/groups linked to interests to create more social and dating opportunities.",
        next_action="Define monthly social opportunity target and identify interest-based groups.",
    ),
    Goal(
        name="Fitness and cardio",
        description="Return to the gym, improve cardio, get fitter physically, and reduce breathlessness.",
        next_action="Create a simple first-session gym plan to reduce uncertainty and social threshold friction.",
        tier=MemoryTier.LOCAL_SENSITIVE,
    ),
]

for g in goals:
    upsert_memory("goal", g.name, g.model_dump(mode="json"), g.tier.value)

commitment = Commitment(
    title="Research Tuscany car rentals",
    due_date="2026-07-15",
    reason="Car rental is a hidden stressor and should not become a late-stage admin trap.",
)
upsert_memory("commitment", commitment.title, commitment.model_dump(mode="json"), commitment.tier.value)

observations = [
    Observation(category="behavioural_pattern", content="Momentum increases when plans become concrete and paid/booked.", confidence=Confidence.HIGH),
    Observation(category="behavioural_pattern", content="Friction increases when uncertainty and sole responsibility combine.", confidence=Confidence.HIGH),
    Observation(category="threshold", content="Gym has uncertainty around what to do and social exposure around other people.", confidence=Confidence.HIGH, tier=MemoryTier.LOCAL_SENSITIVE),
    Observation(category="trust", content="Trust is built through consistency, accuracy, relevance, and evidence-backed suggestions.", confidence=Confidence.HIGH),
]

for idx, o in enumerate(observations):
    upsert_memory("observation", f"seed-{idx}-{date.today().isoformat()}", o.model_dump(mode="json"), o.tier.value)

print("Seeded Jack AI Chief of Staff profile.")
