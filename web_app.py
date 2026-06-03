from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

# Make local app package importable on Streamlit Cloud/Render
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.services.storage import init_db, list_memories, upsert_memory
from app.services.initiative_engine import InitiativeEngine
from app.models.domain import MemoryTier

APP_NAME = "Jack's AI Chief of Staff"
PASSWORD = os.getenv("APP_PASSWORD", "")

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")


def guard() -> bool:
    if not PASSWORD:
        st.warning("APP_PASSWORD is not set. The app is open to anyone with the URL. Set it before deploying online.")
        return True
    if st.session_state.get("authenticated"):
        return True
    st.title(APP_NAME)
    entered = st.text_input("Password", type="password")
    if st.button("Unlock"):
        if entered == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Nope. Nice try, tiny cyber goblin.")
    return False


def seed_if_empty() -> None:
    init_db()
    if list_memories():
        return
    upsert_memory("identity", "behavioural_profile", {
        "name": "Jack",
        "summary": "Jack benefits from clarity, earned accountability, and evidence-based challenge.",
        "patterns": [
            "Momentum increases when plans become concrete.",
            "Friction rises when uncertainty and sole responsibility combine.",
            "Social uncertainty is a stronger blocker than independent difficulty.",
            "Responds well to sharp, fair, specific challenge backed by evidence.",
            "Trust is built through consistency and relevance, not mystical AI vibes."
        ]
    })
    upsert_memory("goal", "iceland_october", {
        "name": "Iceland trip",
        "description": "Travel to Iceland in October, likely comparing Ring Road vs city-based itinerary and budget.",
        "status": "deferred_intentionally",
        "horizon": "October 2026",
        "review_date": "2026-08-15",
        "next_action": "Research Ring Road costs versus city-based trip after August family holiday.",
        "evidence": ["October selected because of possible late September work trip."]
    })
    upsert_memory("goal", "career_influence", {
        "name": "Career influence project",
        "description": "Increase strategic influence at work: be requested for opinions, experience, and early-stage support by senior colleagues.",
        "status": "active",
        "horizon": "12 months",
        "next_action": "Track influence signals: invitations, requests by name, earlier involvement, senior stakeholder asks."
    })
    upsert_memory("goal", "dating_social_confidence", {
        "name": "Dating and social confidence",
        "description": "Use Bumble and interest-based groups to create more social/dating opportunities while building social exposure tolerance.",
        "status": "active",
        "horizon": "12 months",
        "next_action": "Define a low-pressure first exposure step."
    })
    upsert_memory("goal", "fitness_cardio", {
        "name": "Fitness and cardio",
        "description": "Return to the gym and improve physical fitness/cardio without getting overwhelmed by uncertainty or social exposure.",
        "status": "active",
        "horizon": "12 months",
        "next_action": "Create a first-session gym plan that removes decision-making."
    }, tier=MemoryTier.LOCAL_SENSITIVE.value)
    upsert_memory("observation", "gym_threshold", {
        "category": "threshold_friction",
        "content": "Gym return is blocked by not knowing what to do to progress and discomfort around other people.",
        "evidence": ["User named gym as current avoided thing", "Uncertainty and social exposure are known friction points"],
        "confidence": "high"
    }, tier=MemoryTier.LOCAL_SENSITIVE.value)


def memory_card(memory: dict) -> None:
    payload = memory["payload"]
    title = payload.get("name") or payload.get("title") or memory["key"]
    with st.expander(f"{memory['type'].title()} · {title}"):
        st.caption(f"Tier: {memory['tier']} · Updated: {memory['updated_at']}")
        st.json(payload)


def add_memory_form() -> None:
    with st.form("add_memory"):
        st.subheader("Add a memory / goal / commitment")
        col1, col2 = st.columns(2)
        with col1:
            memory_type = st.selectbox("Type", ["goal", "commitment", "observation", "identity"])
            key = st.text_input("Key", placeholder="e.g. tuscany_car_rental")
        with col2:
            tier = st.selectbox("Privacy tier", ["encrypted_operational", "local_sensitive", "ephemeral"])
            due = st.date_input("Optional due/review date", value=None)
        content = st.text_area("Content", placeholder="What should the AI remember or track?")
        submitted = st.form_submit_button("Save")
    if submitted:
        if not key or not content:
            st.error("Give it a key and content. The AI cannot track a ghost, sadly.")
            return
        payload = {"content": content}
        if memory_type == "goal":
            payload = {"name": key.replace("_", " ").title(), "description": content, "status": "active"}
            if due:
                payload["review_date"] = due.isoformat()
        elif memory_type == "commitment":
            payload = {"title": key.replace("_", " ").title(), "status": "open", "reason": content}
            if due:
                payload["due_date"] = due.isoformat()
        elif memory_type == "observation":
            payload = {"category": "manual", "content": content, "confidence": "medium"}
        upsert_memory(memory_type, key, payload, tier=tier)
        st.success("Saved.")
        st.rerun()


def main() -> None:
    if not guard():
        return
    seed_if_empty()

    st.title(APP_NAME)
    st.caption("V1 online interface: memory, reviews, accountability, and threshold-friction detection.")

    tab_review, tab_memory, tab_add, tab_settings = st.tabs(["Review", "Memory", "Add", "Settings"])

    with tab_review:
        st.header("Initiative Review")
        st.write("Run the current review engine. In production this will run on a schedule and ping you when something matters.")
        if st.button("Run review now", type="primary"):
            interventions = InitiativeEngine().run_review()
            st.session_state["latest_interventions"] = [i.model_dump(mode="json") for i in interventions]
        interventions = st.session_state.get("latest_interventions", [])
        if not interventions:
            st.info("No review run yet in this session. Press the button and let the tiny strategist stretch its legs.")
        for item in interventions:
            st.subheader(item["type"].title())
            st.write(item["message"])
            st.caption(f"Confidence: {item['confidence']}")
            st.write("Recommended action:", item.get("recommended_action") or "None")
            with st.expander("Evidence"):
                for ev in item.get("evidence", []):
                    st.write(f"- {ev}")

    with tab_memory:
        st.header("Memory")
        memories = list_memories()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total memories", len(memories))
        col2.metric("Goals", len([m for m in memories if m["type"] == "goal"]))
        col3.metric("Commitments", len([m for m in memories if m["type"] == "commitment"]))
        col4.metric("Interventions", len([m for m in memories if m["type"] == "intervention"]))
        selected = st.selectbox("Filter", ["all", "goal", "commitment", "observation", "identity", "intervention"])
        for memory in memories:
            if selected == "all" or memory["type"] == selected:
                memory_card(memory)

    with tab_add:
        add_memory_form()
        st.divider()
        st.subheader("Quick actions")
        if st.button("Add Tuscany car rental reminder"):
            upsert_memory("commitment", "tuscany_car_rental", {
                "title": "Research Tuscany car rental",
                "status": "open",
                "due_date": (date.today() + timedelta(days=14)).isoformat(),
                "reason": "Hidden holiday admin task; likely to become more expensive or annoying if ignored. Classic little gremlin task."
            })
            st.success("Added Tuscany car rental reminder.")
            st.rerun()

    with tab_settings:
        st.header("Deployment settings")
        st.write("Set these as environment variables when deploying:")
        st.code("APP_PASSWORD=choose-a-strong-password\nOPENAI_API_KEY=optional-for-next-phase\nDATABASE_URL=sqlite:///data/chief_of_staff.db")
        st.warning("Health and financial data are marked local_sensitive in V1. For a real online deployment, this should be encrypted and ideally kept out of cloud sync unless explicitly authorised.")


if __name__ == "__main__":
    main()
