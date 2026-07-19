# plan.md — Daily Dispatch (working name)
### An AI-agent-curated, newspaper-styled daily tech digest

> Codename suggestion: **The Daily Dispatch** / **Broadsheet** / **Inkwell** — rename freely, used only as a placeholder below.

## Product Vision
Every morning, an agent pipeline reads the tech world's news, clusters and summarizes it the way a human editor would, lays it out into sections (Front Page, Startups, AI/ML, Dev Tools, Big Tech, Security, Launches), and hands you a static "edition" — something you flip through once with your tea, not scroll infinitely.

**v1 scope is deliberately narrow:**
- Free feed sources only (no paid news APIs)
- Single user (you), no multi-tenant concerns yet
- One edition per day, generated once (no live refresh mid-day)

## Build Order — Frontend-First
**This is a hard sequencing rule, not just a suggestion: Part A (Frontend) is built and considered done, running entirely on mock data, before any Part B (Backend) work starts.** No backend scaffolding, no Firebase wiring, no agent pipeline work until Part A's definition of done is met. This keeps focus, and it means the entire product experience — the part you'll actually judge every morning — is nailed down before a single line of backend code depends on it.

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

# PART A — Frontend (build this fully before touching backend)

## Phase 0 — Frontend Foundations
**Goal:** repo and tooling exist, nothing product-y yet. (Backend/Firebase project creation is explicitly deferred to Part B — don't set it up yet, even though it's quick, to keep the sequencing honest.)

- [ ] Monorepo layout: `/frontend`, `/backend` (empty for now), shared `/docs` (this plan + agents.md live here)
- [ ] Frontend: Vite + React + TS (recommend TS given placement prep — interviewers like seeing it), Tailwind configured, ESLint/Prettier
- [ ] `.env.example` for frontend only for now
- [ ] Decide on design language now (serif masthead font, column grid, light/dark) — see Phase 1

---

## Phase 1 — Newspaper Shell (mock data) — **START HERE**
**Goal:** a fully navigable, good-looking newspaper UI running entirely on a static mock JSON "edition."

Implementation note: this pass uses hand-authored React/CSS for the shell, paging, and modal transitions so the mock-data experience is complete without introducing extra UI dependencies yet.

### 1a. Project setup
- [ ] Vite React-TS app, Tailwind, path aliases (`@/components`, `@/lib`, etc.)
- [x] Font pairing: serif for headlines/masthead (e.g. "Playfair Display" / "Source Serif 4"), clean sans for body/UI (e.g. "Inter")
- [x] Global layout shell: masthead (title, date, "Vol. N, No. N" flavor text), section nav, page container
- [x] Mock edition JSON shaped exactly like the future API response (see `EditionSchema` in `agents.md`) — this is the contract between frontend and backend, lock it early. Write 2–3 mock editions (different dates) so paging/archive UI has real variety to render, not just one fixture.

### 1b. Newspaper layout / design system
- [x] `Masthead` — title, current date, weather-strip style tagline (optional), section tabs
- [x] `FrontPage` — hero story (largest), 2–3 secondary stories, column-based grid (CSS Grid, newspaper-column feel — `columns-3` + `break-inside-avoid` or manual grid spans)
- [x] `Section` — per-category page (AI/ML, Dev Tools, Startups, Security, Big Tech, Launches, Misc)
- [x] `ArticleCard` — headline, dek/subhead, byline (source + author if available), read-time, thumbnail if source provides one
- [x] Typography system: consistent scale for kicker / headline / dek / body / caption

### 1c. Sliding / paging navigation
- [x] Decide interaction model: **horizontal page-turn** (front page → section 1 → section 2 → …) vs **swipe-up feed of pages**. Recommend horizontal, book-like, since it matches "opening a newspaper."
- [ ] Implement with Framer Motion `drag="x"` + snap points, or evaluate `react-pageflip` for an actual page-curl effect (nice-to-have, not core)
- [x] Keyboard support (←/→), trackpad swipe, mobile touch swipe
- [x] Page indicator (dots or section tab highlight, like a table of contents)

### 1d. Article select / zoom
- [x] Tap/click a headline → modal or dedicated reading view zooms in (shared-element transition via Framer Motion `layoutId`)
- [x] Reading view: full summary (agent-generated, mocked for now), "read original ↗" link out to source, source attribution clearly shown (this matters — see note in agents.md about not overstepping on copyright)
- [x] Close → zoom back out to exact page position (don't just pop a generic modal, preserve spatial context — that's what makes it feel like a newspaper, not a listicle)

### 1e. Settings
- [x] `Settings` page under the masthead, two tabs:
  - **Feed configuration**: toggle sources on/off (checklist — see source list in agents.md), max articles per section, categories to include/exclude
  - **Model settings**: provider select (Gemini / OpenAI / Ollama Cloud), API key input (masked), model name override, temperature/summary-length sliders
- [x] Settings persisted to `localStorage`, shaped identically to the future Firestore `user_settings` doc so swapping the storage backend later (Part B) is a one-line change, not a redesign
- [x] Settings actually take visible effect on the mock data (e.g. toggling a source off filters mock articles tagged with that source, changing "max articles per section" actually truncates) — this matters even without a backend, since it's how you validate the settings UI is wired correctly before there's a real pipeline to test against

### Definition of done for Phase 1
`npm run dev` shows a realistic front page with mock articles, pages through sections, click-to-zoom into an article works with spatial continuity, and Settings changes visibly affect what's rendered from the mock data.

---

## Phase 2 — Frontend Polish & Completeness (still mock data)
**Goal:** finish everything that can be built and judged without a backend, so Part B only has to plug real data into an already-finished UI.

- [x] Archive view: flip back through the 2–3 mock past editions (validates the date-based navigation model before real historical data exists)
- [x] Loading / empty / error states, built against simulated conditions (e.g. a mock "no edition yet" state, a mock "generation failed" state) — these are real UI states Part B will trigger for real, so design them now
- [x] Responsive pass: mobile swipe behavior, tablet, desktop — newspaper metaphor should hold up at all sizes
- [ ] Light/dark mode if not already decided in Phase 0
- [x] Accessibility pass: focus states, keyboard nav through pages and modal, reasonable contrast
- [ ] "Print" / export today's (mock) edition as a shareable image — nice portfolio flourish, purely frontend
- [x] Basic auth screen UI (sign-in with Google/email) — build the screen and flow now with a fake/stubbed auth state; wire to real Firebase Auth in Part B

### Definition of done for Phase 2 (= Definition of done for Part A)
The paper UI is demo-able end-to-end on mock data alone for the core flow (open app → sign in → read front page → page through sections → zoom an article → change settings → browse archive). The remaining original-stack polish items are Framer Motion/page-curl, dark mode, and export.

Status: roughly 85% of Part A is now implemented and build-verified, with the white-paper broadsheet flow done.

---

# PART B — Backend (do not start until Part A is fully complete)

## Phase 3 — Backend Foundations
**Goal:** FastAPI + Firebase skeleton that can store and serve an edition, no agents yet.

- [ ] Firebase project created (Firestore + Auth enabled, test mode rules) — this is the first Part B step, deliberately not done earlier
- [ ] Backend: FastAPI skeleton, **package manager is `uv` — not pip/poetry/conda.** Init with `uv init backend`, add deps with `uv add fastapi langgraph langchain firebase-admin ...`, run with `uv run uvicorn app.main:app --reload`. Commit the generated `uv.lock`. (Calling this out explicitly so any AI coding agent working on this repo doesn't default to `pip install` / `requirements.txt` / poetry.)
- [ ] pre-commit, ruff (add both via `uv add --dev ruff pre-commit`)
- [ ] `.env.example` for backend
- [ ] FastAPI app structure: `routers/`, `services/`, `models/` (Pydantic schemas matching frontend's `EditionSchema` — pull this directly from what Part A already locked in)
- [ ] Firebase Admin SDK wired up (service account, Firestore client)
- [ ] Firestore collections: `editions/{date}`, `users/{uid}/settings`, `sources` (static config or user-editable)
- [ ] Endpoints: `GET /editions/latest`, `GET /editions/{date}`, `GET /settings`, `PUT /settings`
- [ ] Firebase Auth middleware (verify ID token on protected routes)
- [ ] Seed one hand-written real edition into Firestore so frontend can swap from local JSON → real API with zero UI changes

---

## Phase 4 — The Multi-Agent Newsroom (LangGraph v1)
**Goal:** A hierarchical LangGraph multi-agent system that simulates a physical newsroom. Full detail in **agents.md**.

- [ ] Fetcher Tools (4a): Hacker News API, Reddit (r/programming, r/technology), Dev.to API, RSS (TechCrunch, The Verge, Ars Technica, Lobsters) exposed as LangChain tools.
- [ ] The Chief Editor (Supervisor Agent) (4b): Orchestrates the graph. Determines layout needs (e.g., "I need 4 AI articles"), dispatches tasks to Desks, reviews drafts for quality, assigns priority ranking (`importance` span), and approves publication.
- [ ] The Section Desks (Worker Agents) (4c): e.g., AI/ML Desk, Security Desk, Puzzles Desk. Each agent receives a beat, uses Fetcher Tools to hunt for news autonomously, groups related stories, and writes the article.
- [ ] Byline / Pen Name Engine (4d): Dynamically assigns author names based on the LLM powering that specific desk (e.g., "G. Flash, AI Correspondent" or "C. GPT, Senior Editor").
- [ ] Publish step (4e): Compiles all approved drafts into the final `EditionSchema` and writes to Firestore.
- [ ] Manual trigger endpoint: `POST /editions/generate` (for testing before scheduling exists)

---

## Phase 5 — Integration
**Goal:** frontend stops using mock data, uses the real thing end to end. This is where Part A and Part B meet — if `EditionSchema` was locked properly in Phase 1, this phase should be almost entirely plumbing, not redesign.

- [ ] Frontend `lib/api.ts` client, swap mock JSON import for `GET /editions/latest`
- [ ] Wire the Phase 2 auth screen to real Firebase Auth (token attached to API calls)
- [ ] Settings page writes to `PUT /settings` instead of localStorage (localStorage becomes just an optimistic cache)
- [ ] Swap in the real loading/error/empty states designed in Phase 2 for the real conditions that trigger them
- [ ] Archive view reads real past editions instead of the 2–3 mock ones

---

## Phase 6 — Scheduling & Automation
**Goal:** it just happens every morning without you touching anything.

- [ ] APScheduler cron in dev; Cloud Scheduler → Cloud Run job (or Cloud Function) in prod, e.g. 5:30 AM IST trigger
- [ ] Idempotency: re-running for the same date shouldn't duplicate/corrupt the edition
- [ ] Failure handling: if a source is down or a model call fails, pipeline should degrade gracefully (skip that source) not fail the whole edition
- [ ] Optional: push notification / email when today's edition is ready

---

## Phase 7 — v1.1 Polish (post-launch, not blocking v1)
- [ ] Personalization: lightly weight sections based on what you actually open
- [ ] More sources (Product Hunt, GitHub Trending, arXiv cs.AI digest)
- [ ] Offline reading (cache today's edition)
- [ ] Real historical archive beyond whatever's accumulated naturally since launch
