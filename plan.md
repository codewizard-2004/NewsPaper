# plan.md — The Kernel Gazette

### A daily tech newspaper, printed every morning at 6:30am

> **Motto: "All the Bits Fit to Print."**

## Progress

| Phase | Area | Status | % |
|---|---|---|---|
| 0 | Knock-out old system | ✅ Done | 100% |
| 1 | Backend skeleton + provider abstraction | ✅ Done | 100% |
| 2 | Firestore layer + run entrypoint | ✅ Done | 100% |
| 3 | Research + Filter nodes | ✅ Done | 100% |
| 4 | Editor node | ⬜ Not started | 0% |
| 5 | Journalist nodes | ⬜ Not started | 0% |
| 6 | Publisher node | ⬜ Not started | 0% |
| 7 | Integration & scheduling | ⬜ Not started | 0% |
| 8 | Hardening & polish | ⬜ Not started | 0% |

**Overall: ~40%**

_Updated 2026-08-02 — Phases 1-3 complete: packages, Firestore, seeding, and a live
research+filter (`--dry-run` fetches + clusters 6 sources, dedups against `seen_stories`).
Phase 4 (Editor) next._

The authoritative contract for this repo is **`agents.md`** — it defines the graph flow, the
data model, and the hard "do / don't" rules. This plan is the sequenced work breakdown to build
it. **If `agents.md` and this file disagree, `agents.md` wins.**

---

## Product Vision

Every morning an agent pipeline reads yesterday's tech news (`Research → Filter → Editor →
four journalists → Publisher`), researches, dedups, writes it up newspaper-style, and publishes
one browser tab you open with your tea. No feed, no algorithm, no scrolling.

**Scope (unchanged from v1):**
- Free feed sources only
- Single reader, no multi-tenant concerns
- One issue per day, generated once at 6:30am
- Firebase Firestore is both the output store and the state layer between runs

## The Graph (from `agents.md`)

```
START → [Research] → [Filter] → [Editor] → [FrontPage journalist] ─┐
                                          → [AI/ML journalist]  ├─→ [Publisher] → Firestore → END
                                          → [Security journalist]  │
                                          → [Misc journalist]  ────┘    (misc owns DSA + comic state)
```

**Linear spine:** Research → Filter → Editor → Publisher.
**Four journalists** are a parallel fan-out/fan-in between Editor and Publisher.

### Node responsibilities (one purpose each)

| Node | Purpose | LLM? | Firestore access |
|---|---|---|---|
| **Research** | Parallel fan-out across 6 sources + same-day merge/dedup (`cluster_sources`) | no | — |
| **Filter** | Drop already-published stories via `seen_stories` (cross-day dedup) | no | read `seen_stories` |
| **Editor** | Selects a target *range* per page (not fixed count), categorizes; never pads thin days | yes (edit) | — |
| **Front / AI/ML / Security / Misc journalist** | Write full article text + `confidence_rating` + `importance_rating`; call search tool only when the research snippet is insufficient | yes (write) | Misc also owns `dsa_bank` + `comic_state` |
| **Publisher** | Confidence filter, fold thin sections into Misc, fetch images (importance threshold), publish issue + mark seen | no | write `issues/{date}`, write `seen_stories` |

**Firestore ownership — strict:**
- Filter reads `seen_stories` only.
- Misc journalist owns `dsa_bank` + `comic_state`.
- Publisher is the only writer of `issues` and `seen_stories`.
- Nothing else touches Firestore.

### Provider abstraction

Every call goes through `agent/core/llm.py` → `call_llm(prompt, *, task, model, system)` where
`task ∈ {research, edit, write, rate}`. Each task has a default provider (resolved in
`agent/core/config.py`). Providers: Gemini (Free Flash-Lite), OpenAI, Anthropic (Haiku), Ollama
Cloud. **No local model dependency.**

---

## Backend Layout (target)

```
backend/
  run.py                    # entrypoint: build + invoke graph; --dry-run for research→editor only
  kernel-gazette.timer       # systemd 6:30am daily
  kernel-gazette.service     # calls run.py
  agent/
    core/
      config.py              # task -> (provider, model) map, ProviderConfig, resolve_config()
      llm.py                 # provider-agnostic call_llm()
    schema/
      story.py               # Story, Categorized (pydantic)
      issue.py               # Issue, IssueSection, ArticleItem|DSAItem|ComicItem (pydantic)
    graph/
      state.py               # GazetteState TypedDict + build_initial_state()
      graph.py               # StateGraph assembly + fan-out/fan-in edges (topology is stable)
    nodes/
      research.py
      filter.py              # drops already-published (cross-day dedup)
      editor.py
      journalist.py          # build_journalist(node/page): one body for all four buckets
      publisher.py
    tools/
      base.py                  # shared HTTP helpers + SourceRecord
      sources.py               # fetch_all_sources(): runs all 6 in parallel
      hacker_news.py reddit.py devto.py github.py techcrunch.py theverge.py
      search_tool.py           # journalist fallback only (Phase 5)
      image_search_tool.py     # publisher-only (Phase 6)
  firebase/
    firebase.py              # the ONLY module importing firebase_admin; exports firebase/firestore/db + story_hash
    seen.py                  # seen_stories
    issues.py                # issues
    dsa.py                   # dsa_bank
    comic.py                 # comic_state
  pyproject.toml             # package manager: uv ONLY
```

---

## Phases

### Phase 0 — Knock-out the current system
**Goal:** every file from the old 9-desk "Daily Dispatch" newsroom is gone, so nothing confuses
   the new skeleton.
- [x] Delete `backend/app/` (old `graph/`, `routers/`, `models/`, `services/`, `nodes/*_desk.py`).
- [x] Delete old frontend integration (`public/dummy.json`, `lib/api.ts` if referencing old shapes).
- [x] Re-name all remaining "Daily Dispatch" strings → "The Kernel Gazette".
- [x] Leave `agents.md` as the single source of truth for the new design.

### Phase 1 — Backend skeleton & provider abstraction (no graph yet)
**Goal:** `uv run python run.py --dry-run --debug` prints a confirmation; `call_llm()` works for
    all 4 tasks.
- [x] `pyproject.toml` under `backend/` — **`uv` only**, trimmed to the Gazette deps (langgraph,
      langchain-core, google-genai, openai, anthropic, firebase-admin, python-dotenv, feedparser,
      ddgs, duckduckgo-search); unused FastAPI/extra LLM wrappers removed.
- [x] `agent/core/config.py` — env-driven `task → (provider, model)` map + defaults; `.env.example` expanded.
- [x] `agent/core/llm.py` — `call_llm(prompt, *, task, model=None, system=None)` via `_build_chat_model`.
- [x] `run.py` — entrypoint with `--smoke`, `--dry-run`, `--debug`, `--task` flags.
- [ ] Smoke test each task with a real one-line call and a `--debug` flag (no graph yet).
      - Validated live against Gemini (`gemini-3.5-flash-lite`) for all 4 tasks; OpenAI provider
        override confirmed (`gpt-4o-mini` → "OK!"). `ruff check` clean. ✅

### Phase 2 — Firestore access layer + run entry point
**Goal:** the filing cabinet exists and is reachable only through the `firebase/` package.
- [x] `firebase/` package — `firebase.py` (service-account init; the ONLY module importing
      `firebase_admin`) + per-collection modules: `seen.py`, `issues.py`, `dsa.py`, `comic.py`.
      Expose: `get_seen(url)`, `mark_published(url, date)`, `read_issue(date)`,
      `write_issue(date, doc)`, `get_next_dsa_question()`, `mark_dsa_used(id)`,
      `get_comic_state()`, `save_comic_state(synopsis)`.
- [x] Collections seeded: `seed.py` + `fixtures/` (`dsa_bank.json` with 25 questions,
      `comic_state.json`, `issue.json` with a date placeholder). Run
      `uv run python seed.py --dry-run` to inspect, `uv run python seed.py` to write to
      Firestore. `seen_stories` intentionally starts empty — it's an append-only log the
      Publisher fills over time. Verify at the console (see note below).
- [x] `run.py` — CLI with `--dry-run` (research → filter → editor only, skip LLM/image spend)
      and normal mode; wraps a `build_graph().invoke(initial_state)`.
      - Graph scaffolding done: `agent/graph/` linear spine + Editor→(4 journalists)→Publisher
        fan-out/in, all stub bodies in `agent/nodes/`; `--dry-run` and full run both execute. ✅

### Phase 3 — Research + Filter (deterministic, no LLM)
**Goal:** `--dry-run` shows freshly researched, deduped, un-published stories.
- [x] `agent/tools/` package — `base.py` (shared HTTP + `SourceRecord`), one module per
      source (`hacker_news.py`, `reddit.py`, `devto.py`, `github.py`, `techcrunch.py`,
      `theverge.py`), and `sources.py` (`fetch_all_sources`) aggregating all 6 in parallel.
      Each returns normalized `{source,title,url,score,summary}`.
- [x] `nodes/research.py` — parallel fan-out across the 6 tools, then same-day merge: clusters
      same-event titles via `cluster_same_day()` emitting `cluster_sources: [str]`,
      `cluster_sources_semaphores` → `raw_stories`. Deterministic, no LLM.
- [x] `nodes/filter.py` — pure Firestore lookup via `firebase/seen.get_seen()`; drops any raw
      story whose canonical url/hash already exists in `seen_stories` → `fresh_stories`.
      Degrades to keep-all when Firestore is unavailable (no creds / offline).
      - Real run: 25 clustered stories, ~6s end-to-end. ✅

### Phase 4 — Editor (the only editorial judgment)
**Goal:** `--dry-run` now shows a categorized, ranged selection.
- [ ] `nodes/editor.py` — single LLM call (task `edit`) against `fresh_stories`; selects a
      **target range per page** (not a fixed count, e.g. 3–10), categorizes into
      `front_page`, `aiml_page`, `security_page`, `misc_page`. Never pads thin days.
- [ ] Emit `categorized: Dict[str, List[dict]]` — deterministic output, `with_structured_output`.
- [ ] Enforce: editor must not invent stories not present in `fresh_stories`.

### Phase 5 — Journalists (parallel fan-out/fan-in)
**Goal:** full article text with ratings for every assigned story.
- [ ] 4 journalist nodes via `build_journalist(page)` in `nodes/journalist.py` behind target
      `front_page`, `aiml_page`, `security_page`, `misc_page`.
      [ ] Each writes full `body` per article + emits `confidence_rating` + `importance_rating`.
- [ ] Journalists call `search_tool` only when the Research snippet is insufficient — define the
      trigger concretely (e.g. snippet < N words, or a required fact missing) as a helper
      `research_snippet_sufficient(story)`.
- [ ] Misc journalist extra jobs (inside `build_journalist("misc_page")`):
      `get_next_dsa_question()` / `mark_dsa_used(id)` and `get_comic_state()` /
      `save_comic_state(synopsis)` for continuity (via `firebase/dsa.py` + `firebase/comic.py`).
- [ ] Accumulate articles into shared `articles` state via `operator.add` reducer.

### Phase 6 — Publisher (confidence, thin-sections, images, publish)
**Goal:** one complete `issues/{date}` written; seen-marked.
- [ ] Drop articles below confidence threshold (config).
- [ ] Thin-section handling: fold sub-minimum pages into `misc_page` — the ONLY place page
      structure changes; journalists never reassign pages.
- [ ] Image search tool for articles above importance threshold only.
- [ ] Compose final issue doc per `data model` (sections[{name, items[{type, ...}]}]) and
      `write_issue(date, doc)` + `mark_seen` for every published story.

### Phase 7 — Integration & scheduling
- [ ] Frontend `firebase.js` subscribes to `issues/{today}` via `onSnapshot`; replace mock import.
- [ ] `App.jsx` handles missing/thin sections and renders `article`/`dsa_question`/`comic`
      through the right component (`StoryCard`, `DsaBox`, `ComicPanel`).
- [ ] `kernel-gazette.service` + `.timer` for 6:30am systemd run.
- [ ] Idempotency: re-running for an already-published date must not duplicate.

### Phase 8 — Hardening & polish
- [ ] Graceful degradation when a source is down or a model fails (skip, don't fail the issue).
- [ ] Cold dips on model providers; call-timeouts and retries per task.
- [ ] Optional: `--notify` hook / slack webhook when today's issue is ready.

---

## Definition of Done
`uv run python run.py` produces a complete `issues/{today}` with 1–4 sections, every item
typed, DSA + comic continuity intact, story cross-day duplication prevented, nothing fabricated
for padding, and `npm run dev` renders today's issue live from Firestore with a correct
thin-day layout.

## Rules that are not negotiable (from `agents.md`)
- **Same-day dedup lives in Research; cross-day de-dup in Filter.** Never combine them.
- **Editor only places page assignments.** Shape changes only in **Publisher**.
- **Journalists must not call search unconditionally** — only on insufficient snippets.
- **Only `firebase/` touches Firestore** (and within it only `firebase.py` imports
  `firebase_admin`); only Publisher updates `issues` + `seen`.
- **No local/models** — every provider is a hosted API call.