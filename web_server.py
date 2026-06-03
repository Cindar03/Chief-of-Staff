from __future__ import annotations

import html
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.openai_review import generate_ai_review

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.models.domain import MemoryTier
from app.services.initiative_engine import InitiativeEngine
from app.services.storage import init_db, list_memories, upsert_memory

APP_NAME = "Jack's AI Chief of Staff"
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
AUTH_COOKIE = "chief_of_staff_auth"

app = FastAPI(title=APP_NAME)


def page(title: str, body: str) -> HTMLResponse:
    css = """
    body{font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;}
    header{padding:24px 32px;background:#111827;border-bottom:1px solid #334155;}
    main{padding:28px 32px;max-width:1100px;margin:auto;}
    a{color:#93c5fd;text-decoration:none;margin-right:18px;} a:hover{text-decoration:underline;}
    .card{background:#111827;border:1px solid #334155;border-radius:16px;padding:20px;margin:16px 0;box-shadow:0 10px 30px rgba(0,0,0,.2);}
    .muted{color:#94a3b8}.pill{display:inline-block;background:#1e293b;border:1px solid #475569;border-radius:999px;padding:4px 10px;margin:2px;font-size:13px;}
    button,.btn{background:#2563eb;color:white;border:0;border-radius:10px;padding:10px 14px;font-weight:650;cursor:pointer;} button:hover,.btn:hover{background:#1d4ed8;text-decoration:none;}
    input,textarea,select{width:100%;box-sizing:border-box;margin:8px 0 14px;background:#020617;color:#e2e8f0;border:1px solid #475569;border-radius:10px;padding:10px;}
    textarea{min-height:120px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.metric{font-size:30px;font-weight:800;}
    pre{white-space:pre-wrap;background:#020617;border:1px solid #334155;border-radius:10px;padding:12px;overflow:auto}.danger{color:#fecaca}.ok{color:#bbf7d0}
    """
    nav = "<a href='/'>Review</a><a href='/memory'>Memory</a><a href='/add'>Add</a><a href='/settings'>Settings</a>"
    return HTMLResponse(f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{html.escape(title)}</title><style>{css}</style></head><body><header><h1>{APP_NAME}</h1><div>{nav}</div></header><main>{body}</main></body></html>""")


def authed(request: Request) -> bool:
    if not APP_PASSWORD:
        return True
    return request.cookies.get(AUTH_COOKIE) == APP_PASSWORD


def require_auth(request: Request):
    if authed(request):
        return None
    return RedirectResponse("/login", status_code=303)


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


@app.get('/login', response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    return page("Login", """<div class='card'><h2>Unlock</h2><form method='post' action='/login'><input type='password' name='password' placeholder='Password'><button>Unlock</button></form></div>""")


@app.post('/login')
def login(password: str = Form(...)) -> Response:
    if APP_PASSWORD and password != APP_PASSWORD:
        return page("Login failed", "<div class='card'><p class='danger'>Wrong password. The tiny cyber goblin remains outside.</p><a href='/login'>Try again</a></div>")
    resp = RedirectResponse('/', status_code=303)
    resp.set_cookie(AUTH_COOKIE, password, httponly=True, samesite='lax')
    return resp


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    redirect = require_auth(request)
    if redirect: return redirect
    seed_if_empty()
    body = """
    <div class='card'><h2>Initiative Review</h2><p class='muted'>Run the current review engine. Later this becomes scheduled and proactive.</p><form method='post' action='/review'><button>Run review now</button></form></div>
    <div class='card'><h2>What this version does</h2><p>It remembers goals, commitments and observations, then looks for review dates, open commitments, and threshold friction. No glitter. Actual spine.</p></div>
    """
    return page("Review", body)


@app.post('/review', response_class=HTMLResponse)
def review(request: Request):
    redirect = require_auth(request)
    if redirect: return redirect
    seed_if_empty()
    interventions = InitiativeEngine().run_review()

    memory_items = []

for item in interventions:
    memory_items.append({
        "type": item.type.value,
        "message": item.message,
        "recommended_action": item.recommended_action,
        "confidence": item.confidence.value,
        "evidence": item.evidence
    })

ai_review = generate_ai_review(memory_items)

    if not interventions:
        content = "<p>No interventions. Suspiciously peaceful. Enjoy it while it lasts.</p>"
    else:
        cards = []
        for item in interventions:
            evidence = ''.join(f"<li>{html.escape(ev)}</li>" for ev in item.evidence)
            cards.append(f"""
            <div class='card'><h2>{html.escape(item.type.value.title())}</h2>
            <span class='pill'>Confidence: {html.escape(item.confidence.value)}</span>
            <p>{html.escape(item.message)}</p>
            <p><strong>Recommended action:</strong> {html.escape(item.recommended_action or 'None')}</p>
            <h3>Evidence</h3><ul>{evidence}</ul></div>
            """)
        content = ''.join(cards)
    return page("Review results", f"<a class='btn' href='/'>Back</a>{content}")


@app.get('/memory', response_class=HTMLResponse)
def memory(request: Request, filter: Optional[str] = None):
    redirect = require_auth(request)
    if redirect: return redirect
    seed_if_empty()
    memories = list_memories(filter if filter and filter != 'all' else None)
    all_m = list_memories()
    metrics = f"""
    <div class='grid'>
      <div class='card'><div class='metric'>{len(all_m)}</div><div class='muted'>Total memories</div></div>
      <div class='card'><div class='metric'>{len([m for m in all_m if m['type']=='goal'])}</div><div class='muted'>Goals</div></div>
      <div class='card'><div class='metric'>{len([m for m in all_m if m['type']=='commitment'])}</div><div class='muted'>Commitments</div></div>
      <div class='card'><div class='metric'>{len([m for m in all_m if m['type']=='intervention'])}</div><div class='muted'>Interventions</div></div>
    </div>"""
    filters = ''.join(f"<a href='/memory?filter={f}'>{f}</a>" for f in ['all','goal','commitment','observation','identity','intervention'])
    cards = []
    for m in memories:
        cards.append(f"<div class='card'><h3>{html.escape(m['type'].title())} · {html.escape(str(m['key']))}</h3><p class='muted'>Tier: {html.escape(m['tier'])} · Updated: {html.escape(m['updated_at'])}</p><pre>{html.escape(str(m['payload']))}</pre></div>")
    return page("Memory", metrics + f"<div class='card'>{filters}</div>" + ''.join(cards))


@app.get('/add', response_class=HTMLResponse)
def add_page(request: Request):
    redirect = require_auth(request)
    if redirect: return redirect
    body = """
    <div class='card'><h2>Add memory / goal / commitment</h2>
    <form method='post' action='/add'>
      <label>Type</label><select name='memory_type'><option>goal</option><option>commitment</option><option>observation</option><option>identity</option></select>
      <label>Key</label><input name='key' placeholder='e.g. tuscany_car_rental'>
      <label>Privacy tier</label><select name='tier'><option>encrypted_operational</option><option>local_sensitive</option><option>ephemeral</option></select>
      <label>Optional due/review date</label><input type='date' name='due'>
      <label>Content</label><textarea name='content'></textarea>
      <button>Save</button>
    </form></div>
    <div class='card'><h2>Quick action</h2><form method='post' action='/quick-tuscany'><button>Add Tuscany car rental reminder</button></form></div>
    """
    return page("Add", body)


@app.post('/add')
def add_memory(request: Request, memory_type: str = Form(...), key: str = Form(...), tier: str = Form(...), content: str = Form(...), due: str = Form(default="")):
    redirect = require_auth(request)
    if redirect: return redirect
    if not key or not content:
        return page("Missing details", "<div class='card'><p class='danger'>Give it a key and content. The AI cannot track a ghost, sadly.</p><a href='/add'>Back</a></div>")
    payload = {"content": content}
    if memory_type == "goal":
        payload = {"name": key.replace("_", " ").title(), "description": content, "status": "active"}
        if due: payload["review_date"] = due
    elif memory_type == "commitment":
        payload = {"title": key.replace("_", " ").title(), "status": "open", "reason": content}
        if due: payload["due_date"] = due
    elif memory_type == "observation":
        payload = {"category": "manual", "content": content, "confidence": "medium"}
    upsert_memory(memory_type, key, payload, tier=tier)
    return RedirectResponse('/memory', status_code=303)


@app.post('/quick-tuscany')
def quick_tuscany(request: Request):
    redirect = require_auth(request)
    if redirect: return redirect
    upsert_memory("commitment", "tuscany_car_rental", {
        "title": "Research Tuscany car rental",
        "status": "open",
        "due_date": (date.today() + timedelta(days=14)).isoformat(),
        "reason": "Hidden holiday admin task; likely to become more expensive or annoying if ignored. Classic little gremlin task."
    })
    return RedirectResponse('/memory?filter=commitment', status_code=303)


@app.get('/settings', response_class=HTMLResponse)
def settings(request: Request):
    redirect = require_auth(request)
    if redirect: return redirect
    body = """
    <div class='card'><h2>Deployment settings</h2>
    <p>Set these environment variables when deploying:</p>
    <pre>APP_PASSWORD=choose-a-strong-password
OPENAI_API_KEY=optional-for-next-phase
DATABASE_URL=sqlite:///data/chief_of_staff.db</pre>
    <p class='danger'>Do not put detailed health or financial data into this V1 cloud deployment. Password protection is not the same as production-grade privacy. Tiny but important distinction, naturally.</p>
    </div>
    """
    return page("Settings", body)
