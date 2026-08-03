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
| 4 | Editor node | ✅ Done | 100% |
| 5 | Journalist nodes | ✅ Done | 100% |
| 6 | Publisher node | ✅ Done | 100% |
| 7 | Integration & scheduling | ✅ Done | 100% |
| 8 | Hardening & polish | 🔄 In progress | 25% |

**Overall: ~85%**

_Updated 2026-08-03 — Phases 1-7 complete; Phase 8 started. A Firebase service account
(`FIREBASE_SERVICE_ACCOUNT` in `.env`, file git-ignored) unblocks live Firestore access, and
the full pipeline now runs end-to-end for real: `run.py --date 2026-08-03` wrote
`issues/2026-08-03` (AI/ML + Misc with DSA + comic), marked 22 stories in `seen_stories`,
consumed a DSA question, and advanced comic continuity. The Publisher is idempotent
(`read_issue(date)` guard verified live). The frontend subscribes to `issues/{today}` and
adapts the sections/items doc to its `DummyEdition` render model (bundled `dummy.json` demo
fallback, Live/Demo masthead badge)._

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
  run.py                    # entrypoint: build + invoke graph; --dry-run runs the full graph
                            #   but the Publisher is stubbed (no Firestore write / image spend)
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
- [x] `nodes/editor.py` — single LLM call (task `edit`) against `fresh_stories`; selects a
      **target range per page** (not a fixed count, e.g. 3–10), categorizes into
      `front_page`, `aiml_page`, `security_page`, `misc_page`. Never pads thin days.
      - The model answers with *indices* into `fresh_stories` (via `call_llm_structured`),
        so fabricated stories are structurally impossible. Degrades to a deterministic
        keyword bucket if the LLM call fails (provider outage never kills the issue).
      - Ollama's `json_schema` structured-output method is unreliable (models answer in
        prose); `call_llm_structured` forces `method="function_calling"` for the ollama
        provider. Live: 25 fresh → front_page=6, aiml_page=6, security_page=1, misc_page=8. ✅
- [x] Emit `categorized: Dict[str, List[dict]]` — deterministic output, `with_structured_output`.
- [x] Enforce: editor must not invent stories not present in `fresh_stories`.

### Phase 5 — Journalists (parallel fan-out/fan-in)
**Goal:** full article text with ratings for every assigned story.
- [x] 4 journalist nodes via `build_journalist(page)` in `nodes/journalist.py` behind target
      `front_page`, `aiml_page`, `security_page`, `misc_page`.
      [x] Each writes full `body` per article + emits `confidence_rating` + `importance_rating`
          via one structured `write` call per article (`ArticleDraft`); headline stays the
          source title (deterministic, no drift).
- [x] Journalists call `search_tool` only when the Research snippet is insufficient — defined
      concretely as `research_snippet_sufficient(story)`: summary word count < 8 AND not
      (non-empty AND >= 2 independent sources). `agent/tools/search_tool.py` wraps DuckDuckGo
      (`ddgs`), normalized to `{title, url, snippet}`, `[]` on failure.
- [x] Misc journalist extra jobs (inside `build_journalist("misc_page")`):
      `get_next_dsa_question()` / `mark_dsa_used(id)` and `get_comic_state()` /
      `save_comic_state(synopsis)` for continuity (via `firebase/dsa.py` + `firebase/comic.py`).
      Both degrade to a logged skip (with an entry in `state.errors`) when Firestore is
      unreachable.
- [x] Accumulate articles into shared `items` state via `operator.add` reducer (journalist
      failures land in `errors`, also `operator.add` — never fatal).
      - Live: 19 articles written for 19 assigned stories; DSA + comic skipped cleanly
        (no Firebase credentials in dev). ✅

### Phase 6 — Publisher (confidence, thin-sections, images, publish)
**Goal:** one complete `issues/{date}` written; seen-marked.
- [x] Drop articles below confidence threshold (config) — `PUBLISHER_CONFIDENCE_THRESHOLD`
      (default 0.5) in `agent/core/config.py`; DSA/comic always pass.
- [x] Thin-section handling: fold sub-minimum pages into `misc_page` via
      `PUBLISHER_MIN_PAGE_ITEMS` (default 3) — the ONLY place page structure changes;
      journalists never reassign pages.
- [x] Image search tool (`agent/tools/image_search_tool.py`, DuckDuckGo images) called only
      for articles at/above `PUBLISHER_IMAGE_IMPORTANCE` (default 7.0); a miss leaves
      `image_url=None`, never fails the issue.
- [x] Compose final issue doc per `data model` (sections[{name, items[{type, ...}]}]) and
      `write_issue(date, doc)` + `mark_published` for every published story (internal `page`/
      `url` fields stripped before writing). Write + seen-mark degrade to logged errors when
      Firestore is unreachable — the issue is still composed into state.
      - Live: 18 articles -> confidence filter -> 3 sections [Front page=4, AI/ML=4, Misc=4],
        Security absent (thin day), write skipped cleanly (no creds in dev). ✅

### Phase 7 — Integration & scheduling
- [x] Frontend subscribes to `issues/{today}` via `onSnapshot` (`frontend/src/lib/issues.ts`),
      replacing the mock-only import. The backend `sections/items` doc is adapted to the
      frontend's `DummyEdition` render model by a pure transformer
      (`frontend/src/lib/adapter.ts`, unit-tested): section → page template (front /
      three-column / stack), `importance_rating` 0–10 → `ArticleImportance` 1–5, bodies →
      paragraphs, `dsa_question`/`comic` items become kickered brief stories on the Misc page,
      sources derive from item names (known-homepage map). Falls back to `public/dummy.json`
      (bundled demo edition) while the live doc is missing/unreachable; masthead shows a
      Live/Demo badge.
- [x] Thin/missing pages handled by the transformer: a section with no items is omitted, and
      page numbers re-sequence (matching the Publisher's thin-day folding).
- [x] `kernel-gazette.service` + `kernel-gazette.timer` — 6:30am daily systemd run
      (`OnCalendar=*-*-* 06:30:00`, `Persistent=true`), runs `backend/.venv/bin/python run.py`
      via `EnvironmentFile` (`.env`).
- [x] Idempotency: Publisher's `_publish` checks `read_issue(date)` first and skips (no
      duplicate/clobber) when the issue already exists; a failed lookup degrades to "not
      published" so an offline Firestore never blocks a first write. Unit-tested.

### Phase 8 — Hardening & polish
- [x] Firebase service-account wired (`backend/newspaper-ee07b-…-adminsdk-*.json`, git-ignored,
      referenced from `.env` via `FIREBASE_SERVICE_ACCOUNT`). Live end-to-end demonstrated:
      full pipeline wrote `issues/2026-08-03` (2 sections, 22 stories, DSA + comic), marked
      22 `seen_stories`, consumed one DSA question, advanced `comic_state` to day 2. Fixed the
      Firestore `where` positional-args deprecation (`firebase/dsa.py`).
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