from app.services.initiative_engine import InitiativeEngine
from app.models.domain import Goal, Observation, Confidence, MemoryTier
from app.services.storage import upsert_memory


def test_threshold_intervention_detected():
    g = Goal(name="Fitness and cardio", description="Return to gym", tier=MemoryTier.LOCAL_SENSITIVE)
    o = Observation(category="threshold", content="Gym feels unclear and involves people around me", confidence=Confidence.HIGH, tier=MemoryTier.LOCAL_SENSITIVE)
    upsert_memory("goal", "test-gym", g.model_dump(mode="json"), g.tier.value)
    upsert_memory("observation", "test-gym-obs", o.model_dump(mode="json"), o.tier.value)
    interventions = InitiativeEngine().run_review()
    assert any(i.type.value == "threshold" for i in interventions)
