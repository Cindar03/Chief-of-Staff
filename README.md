# Jack AI Chief of Staff — V1 Scaffold

A privacy-conscious, proactive AI chief-of-staff prototype focused on initiative, accountability, drift detection, threshold crossing, and evidence-based intervention.

This V1 is deliberately small. No shiny nonsense. The goal is to prove the initiative loop:

1. Remember meaningful context
2. Observe current signals
3. Detect drift, opportunities, and threshold friction
4. Intervene consistently with evidence and confidence levels

## What works now

- Local SQLite memory store
- Goal, commitment, observation, and intervention objects
- Behavioural constitution and delegation charter
- Initiative engine with scoring rules
- CLI for logging reflections and running reviews
- FastAPI server endpoints
- OpenAI adapter stub using structured JSON when an API key is present
- Google Calendar/Gmail integration placeholders ready for OAuth implementation

## Quick start

```bash
cd jack_ai_chief_of_staff
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_profile.py
python -m app.cli review
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Privacy model

The app uses memory tiers:

- `local_sensitive`: health, finance, journals, deeply private reflections. Keep local only.
- `encrypted_operational`: goals, tasks, commitments, calendar-derived metadata.
- `ephemeral`: temporary context not retained long-term.

V1 stores locally in SQLite. Before cloud deployment, add encryption-at-rest, secret management, and data export/delete controls.

## Suggested API choices

- LLM: OpenAI Responses API / structured outputs for consistent JSON decisions
- Google Calendar/Gmail: Google Workspace Python quickstarts and OAuth client libraries

See docs/BUILD_PLAN.md for next steps.
