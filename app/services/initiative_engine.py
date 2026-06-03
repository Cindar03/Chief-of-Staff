from __future__ import annotations

from datetime import date, datetime
from app.models.domain import Confidence, Intervention, InterventionType
from app.services.storage import list_memories, upsert_memory


class InitiativeEngine:
    """Rule-based V1 engine. LLM reasoning can be layered on top later."""

    def run_review(self) -> list[Intervention]:
        goals = list_memories("goal")
        commitments = list_memories("commitment")
        observations = list_memories("observation")
        interventions: list[Intervention] = []

        interventions.extend(self._detect_deferred_goals(goals))
        interventions.extend(self._detect_open_commitments(commitments))
        interventions.extend(self._detect_threshold_friction(observations, goals))

        for idx, intervention in enumerate(interventions):
            upsert_memory(
                "intervention",
                f"{datetime.utcnow().isoformat()}-{idx}",
                intervention.model_dump(mode="json"),
                tier="encrypted_operational",
            )
        return interventions

    def _detect_deferred_goals(self, goals: list[dict]) -> list[Intervention]:
        results: list[Intervention] = []
        today = date.today().isoformat()
        for goal in goals:
            payload = goal["payload"]
            if payload.get("status") == "deferred_intentionally" and payload.get("review_date"):
                if payload["review_date"] <= today:
                    results.append(
                        Intervention(
                            type=InterventionType.REVIEW,
                            confidence=Confidence.HIGH,
                            message=f"Scheduled review due: {payload['name']} is no longer meant to sit quietly in the cupboard of good intentions.",
                            evidence=[f"Review date reached: {payload['review_date']}", payload.get("description", "")],
                            recommended_action=payload.get("next_action") or "Decide whether to reactivate, revise, or intentionally defer again.",
                        )
                    )
        return results

    def _detect_open_commitments(self, commitments: list[dict]) -> list[Intervention]:
        results: list[Intervention] = []
        today = date.today().isoformat()
        for item in commitments:
            payload = item["payload"]
            due = payload.get("due_date")
            if payload.get("status") == "open" and due and due <= today:
                results.append(
                    Intervention(
                        type=InterventionType.ACCOUNTABILITY,
                        confidence=Confidence.HIGH,
                        message=f"Commitment due: {payload['title']}. Is this complete, intentionally delayed, or quietly turning into fog?",
                        evidence=[f"Due date: {due}", payload.get("reason") or "Open commitment remains unresolved."],
                        recommended_action="Mark complete, set a new date with a reason, or break it into a smaller next action.",
                    )
                )
        return results

    def _detect_threshold_friction(self, observations: list[dict], goals: list[dict]) -> list[Intervention]:
        text = "\n".join([o["payload"].get("content", "") for o in observations]).lower()
        active_goal_text = "\n".join([g["payload"].get("description", "") + " " + g["payload"].get("name", "") for g in goals]).lower()
        results: list[Intervention] = []

        if "gym" in text + active_goal_text and any(k in text for k in ["unclear", "anxious", "people", "judgement", "not knowing"]):
            results.append(
                Intervention(
                    type=InterventionType.THRESHOLD,
                    confidence=Confidence.MEDIUM,
                    message="Possible threshold friction detected around the gym. The blocker may not be motivation; it may be uncertainty plus social exposure. Annoyingly specific, I know.",
                    evidence=["Gym goal mentioned", "Observed friction terms around uncertainty/social exposure"],
                    recommended_action="Create a first-session gym plan that removes decision-making and minimises social uncertainty.",
                )
            )
        return results
