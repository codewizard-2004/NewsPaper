# plan.md — Daily Dispatch (working name)
### An AI-agent-curated, newspaper-styled daily tech digest

> Codename suggestion: **The Daily Dispatch** / **Broadsheet** / **Inkwell** — rename freely, used only as a placeholder below.

## Product Vision
Every morning, an agent pipeline reads the tech world's news, clusters and summarizes it the way a human editor would, lays it out into sections (Front Page, Startups, AI/ML, Dev Tools, Big Tech, Security, Launches), and hands you a static "edition" — something you flip through once with your tea, not scroll infinitely.

**v1 scope is deliberately narrow:**
- Free feed sources only (no paid news APIs)
- Single user (you), no multi-tenant concerns yet
- One edition per day, generated once (no live refresh mid-day)
- Frontend built first against **mock data**, backend wired in afterward

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite, Tailwind CSS, Framer Motion (page transitions), Zustand (state) |
| Backend | FastAPI |
| Backend package manager | **uv** (not pip/poetry/conda) — all install/run commands use `uv add` / `uv run` |
| Agent orchestration | LangGraph (stateful graph) + LangChain (model/tool wrappers) |
| Data store | Firebase Firestore (editions, articles, user settings) |
| Auth | Firebase Auth (email or Google sign-in — single user for v1, but do it properly) |
| Scheduling | APScheduler (local/dev) → Cloud Scheduler + Cloud Run/Functions (prod) |
| Models | Gemini (default), OpenAI, Ollama Cloud — user-selectable per agent role |

---

## Phase 0 — Foundations
**Goal:** repo and tooling exist, nothing product-y yet.

- [ ] Monorepo layout: `/frontend`, `/backend`, shared `/docs` (this plan + agents.md live here)
- [ ] Frontend: Vite + React + TS (recommend TS given placement prep — interviewers like seeing it), Tailwind configured, ESLint/Prettier
- [ ] Backend: FastAPI skeleton, **package manager is `uv` — not pip/poetry/conda.** Init with `uv init backend`, add deps with `uv add fastapi langgraph langchain firebase-admin ...`, run with `uv run uvicorn app.main:app --reload`. Commit the generated `uv.lock`. (Calling this out explicitly so any AI coding agent working on this repo doesn't default to `pip install` / `requirements.txt` / poetry.)
- [ ] pre-commit, ruff (add both via `uv add --dev ruff pre-commit`)
- [ ] Firebase project created (Firestore + Auth enabled, test mode rules)
- [ ] `.env.example` for both frontend and backend (never commit real keys)
- [ ] Decide on design language now (serif masthead font, column grid, light/dark) — see Phase 1

---

## Phase 1 — Frontend v1 (Newspaper Shell, mock data) — **START HERE**
**Goal:** a fully navigable, good-looking newspaper UI running entirely on a static mock JSON "edition" — no backend calls yet. This is the phase we're detailing first below.

### 1a. Project setup
- [ ] Vite React-TS app, Tailwind, path aliases (`@/components`, `@/lib`, etc.)
- [ ] Font pairing: serif for headlines/masthead (e.g. "Playfair Display" / "Source Serif 4"), clean sans for body/UI (e.g. "Inter")
- [ ] Global layout shell: masthead (title, date, "Vol. N, No. N" flavor text), section nav, page container
- [ ] Mock edition JSON shaped exactly like the future API response (see `EditionSchema` below) — this is the contract between frontend and backend, lock it early

### 1b. Newspaper layout / design system
- [ ] `Masthead` — title, current date, weather-strip style tagline (optional), section tabs
- [ ] `FrontPage` — hero story (largest), 2–3 secondary stories, column-based grid (CSS Grid, newspaper-column feel — `columns-3` + `break-inside-avoid` or manual grid spans)
- [ ] `Section` — per-category page (AI/ML, Dev Tools, Startups, Security, Big Tech, Launches, Misc)
- [ ] `ArticleCard` — headline, dek/subhead, byline (source + author if available), read-time, thumbnail if source provides one
- [ ] Typography system: consistent scale for kicker / headline / dek / body / caption

### 1c. Sliding / paging navigation
- [ ] Decide interaction model: **horizontal page-turn** (front page → section 1 → section 2 → …) vs **swipe-up feed of pages**. Recommend horizontal, book-like, since it matches "opening a newspaper."
- [ ] Implement with Framer Motion `drag="x"` + snap points, or evaluate `react-pageflip` for an actual page-curl effect (nice-to-have, not core)
- [ ] Keyboard support (←/→), trackpad swipe, mobile touch swipe
- [ ] Page indicator (dots or section tab highlight, like a table of contents)

### 1d. Article select / zoom
- [ ] Tap/click a headline → modal or dedicated reading view zooms in (shared-element transition via Framer Motion `layoutId`)
- [ ] Reading view: full summary (agent-generated), "read original ↗" link out to source, source attribution clearly shown (this matters — see note in agents.md about not overstepping on copyright)
- [ ] Close → zoom back out to exact page position (don't just pop a generic modal, preserve spatial context — that's what makes it feel like a newspaper, not a listicle)

### 1e. Settings
- [ ] `Settings` page/drawer, two tabs:
  - **Feed configuration**: toggle sources on/off (checklist — see source list in agents.md), max articles per section, categories to include/exclude
  - **Model settings**: provider select (Gemini / OpenAI / Ollama Cloud), API key input (masked, stored securely — local-only for now, Firebase-backed later), model name override, temperature/summary-length sliders
- [ ] Settings persisted to `localStorage` for now, shaped identically to the future Firestore `user_settings` doc so swapping the storage backend later is a one-line change

### Definition of done for Phase 1
You can `npm run dev`, see a realistic front page with mock articles, page through sections, click into an article and zoom, and open Settings and toggle things (even if they don't do anything real yet).

---

## Phase 2 — Backend Foundations
**Goal:** FastAPI + Firebase skeleton that can store and serve an edition, no agents yet.

- [ ] FastAPI app structure: `routers/`, `services/`, `models/` (Pydantic schemas matching frontend's `EditionSchema`)
- [ ] Firebase Admin SDK wired up (service account, Firestore client)
- [ ] Firestore collections: `editions/{date}`, `users/{uid}/settings`, `sources` (static config or user-editable)
- [ ] Endpoints: `GET /editions/latest`, `GET /editions/{date}`, `GET /settings`, `PUT /settings`
- [ ] Firebase Auth middleware (verify ID token on protected routes)
- [ ] Seed one hand-written mock edition into Firestore so frontend can swap from local JSON → real API with zero UI changes

---

## Phase 3 — Agent Pipeline v1
**Goal:** the actual "newspaper editor" — a LangGraph pipeline that produces a real edition from free sources. Full detail in **agents.md**.

- [ ] Source connectors (Phase 3a): Hacker News API, Reddit (r/programming, r/technology), Dev.to API, RSS (TechCrunch, The Verge, Ars Technica, Lobsters)
- [ ] Dedup/cluster agent (Phase 3b): collapse the "5 sources covering the same launch" problem
- [ ] Summarizer agent (Phase 3c): per-article dek + 3–4 sentence summary, model-agnostic via LangChain
- [ ] Editor agent (Phase 3d): assigns section, ranks front-page-worthiness, writes headline if source headline is bad/clickbaity
- [ ] Publish step (Phase 3e): writes final `EditionSchema` doc to Firestore
- [ ] Manual trigger endpoint: `POST /editions/generate` (for testing before scheduling exists)

---

## Phase 4 — Integration
**Goal:** frontend stops using mock data, uses the real thing end to end.

- [ ] Frontend `lib/api.ts` client, swap mock JSON import for `GET /editions/latest`
- [ ] Firebase Auth on frontend (sign-in screen, token attached to API calls)
- [ ] Settings page writes to `PUT /settings` instead of localStorage (localStorage becomes just an optimistic cache)
- [ ] Loading/error/empty states (what does the UI show at 5am before today's edition exists yet?)

---

## Phase 5 — Scheduling & Automation
**Goal:** it just happens every morning without you touching anything.

- [ ] APScheduler cron in dev; Cloud Scheduler → Cloud Run job (or Cloud Function) in prod, e.g. 5:30 AM IST trigger
- [ ] Idempotency: re-running for the same date shouldn't duplicate/corrupt the edition
- [ ] Failure handling: if a source is down or a model call fails, pipeline should degrade gracefully (skip that source) not fail the whole edition
- [ ] Optional: push notification / email when today's edition is ready

---

## Phase 6 — v1.1 Polish (post-launch, not blocking v1)
- [ ] Archive view (flip back through past editions — the "old newspaper stack" fantasy)
- [ ] Personalization: lightly weight sections based on what you actually open
- [ ] More sources (Product Hunt, GitHub Trending, arXiv cs.AI digest)
- [ ] Offline reading (cache today's edition)
- [ ] "Print" / export today's edition as a shareable image or PDF

---

## Suggested build order (practical, not phase-numeric)
Since you said "let's start with frontend for a change": **do all of Phase 1 fully on mock data first.** It's the highest-leverage phase because it (a) is the part you'll actually look at every morning, (b) forces you to finalize `EditionSchema`, which everything else downstream depends on, and (c) is genuinely fun/portfolio-worthy on its own even before the backend exists.
