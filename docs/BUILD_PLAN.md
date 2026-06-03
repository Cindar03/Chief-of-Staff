# Build Plan

## Phase 1: Local proof

Goal: Prove the initiative loop before building a full app.

1. Run local memory store.
2. Seed Jack's constitution, charter, goals, and behavioural observations.
3. Log reflections via CLI/API.
4. Run initiative reviews.
5. Tune intervention quality.

## Phase 2: LLM memory extraction

Use OpenAI structured outputs to extract goals, commitments, observations, and possible interventions from reflections. Structured outputs reduce brittle parsing and help maintain consistency.

## Phase 3: Calendar observation

Add read-only Google Calendar access first.

Signals to detect:
- no focus blocks for active goals
- overloaded days
- no recovery windows
- approaching travel/admin dates
- free evenings that could support social/gym goals

Only after trust is proven: enable private focus-block creation.

## Phase 4: Gmail observation

Start with metadata/snippets only.

Signals to detect:
- unanswered important threads
- difficult conversations possibly being delayed
- work opportunities related to influence project

Do not send email without approval.

## Phase 5: Notification layer

Use Telegram or Discord first. Mobile app comes later. Do not build cosmetics before initiative works.

## Phase 6: Security hardening

- Encrypt local database
- Separate local_sensitive storage
- Add audit log
- Add export/delete controls
- Add OAuth token encryption
- Add permission review screen
