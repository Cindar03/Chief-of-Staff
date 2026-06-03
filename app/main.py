from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from app.models.domain import Observation, Confidence
from app.services.initiative_engine import InitiativeEngine
from app.services.storage import init_db, list_memories, upsert_memory

app = FastAPI(title="Jack AI Chief of Staff", version="0.1.0")


class ReflectionRequest(BaseModel):
    text: str


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/memory")
def memory(type: str | None = None) -> list[dict]:
    return list_memories(type)


@app.post("/reflect")
def reflect(req: ReflectionRequest) -> dict:
    obj = Observation(category="manual_reflection", content=req.text, confidence=Confidence.MEDIUM)
    upsert_memory("observation", f"api-{obj.created_at.isoformat()}", obj.model_dump(mode="json"), obj.tier.value)
    return {"stored": True, "observation": obj.model_dump(mode="json")}


@app.post("/review")
def review() -> dict:
    interventions = InitiativeEngine().run_review()
    return {"count": len(interventions), "interventions": [i.model_dump(mode="json") for i in interventions]}
