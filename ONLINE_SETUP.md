# Jack's AI Chief of Staff — Online V1

This version adds a browser interface using FastAPI. It is intentionally simple: memory, seeded behavioural profile, manual review, and accountability interventions.

## Run locally

```bash
pip install -r requirements.txt
APP_PASSWORD="choose-a-password" uvicorn web_server:app --reload
```

Open: `http://127.0.0.1:8000`

## Deploy online — Render

1. Create a private GitHub repository.
2. Upload this folder.
3. In Render, create a new Web Service from the repository.
4. Use Docker deployment.
5. Add environment variables:

```bash
APP_PASSWORD=choose-a-strong-password
OPENAI_API_KEY=optional-for-next-phase
DATABASE_URL=sqlite:///data/chief_of_staff.db
```

6. Deploy.

Important: for persistent storage on Render, add a persistent disk mounted at `/app/data` or use a managed PostgreSQL database.

## Deploy online — Railway/Fly.io

Use the Dockerfile. Set the same environment variables above.

## Privacy warning

This is V1. Do not put detailed financial or health data into a public/free deployment. The app has password protection, but production-grade privacy should include:

- encrypted database storage
- proper user authentication
- secrets manager
- firewall rules
- backups
- access logs
- separate local-only sensitive memory store

## What works now

- Browser dashboard
- Password gate
- Memory viewer
- Manual memory creation
- Seeded Jack behavioural profile
- Review engine
- Gym threshold-friction intervention
- Tuscany car rental quick commitment
- Privacy tier labels

## What comes next

1. OpenAI-backed memory extraction from chat.
2. Google Calendar read-only observer.
3. Scheduled initiative loop.
4. Telegram/push notifications.
5. Approval workflow for any action involving other people.
