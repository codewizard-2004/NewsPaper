# agents.md — Daily Dispatch Agent Pipeline

This document defines the LangGraph agent pipeline that turns raw feed data into a published "edition." It's the contract for Phase 3 of `plan.md`, written now so the frontend's `EditionSchema` (Phase 1) can be designed against it from day one.

> **Environment note:** backend package management is **`uv`**, exclusively. Install deps with `uv add <package>`, run scripts/servers with `uv run ...`, lockfile is `uv.lock` (commit it). Do not introduce `requirements.txt`, `pip install`, or `poetry` — if you're an AI agent implementing this pipeline, this is a hard constraint, not a suggestion.

---

## 1. Pipeline Overview

```
        ┌──────────────┐
        │  Scheduler   │  (cron, 5:30 AM daily)
        └──────┬───────┘
               ▼
   ┌───────────────────────┐
   │   Fetcher Agents (×N)  │  parallel, one per source type
   └───────────┬───────────┘
               ▼
   ┌───────────────────────┐
   │  Dedup / Cluster Agent │
   └───────────┬───────────┘
               ▼
   ┌───────────────────────┐
   │   Summarizer Agent     │
   └───────────┬───────────┘
               ▼
   ┌───────────────────────┐
   │     Editor Agent       │  (section + rank + headline QA)
   └───────────┬───────────┘
               ▼
   ┌───────────────────────┐
   │    Layout / Publish    │  → writes EditionSchema to Firestore
   └───────────────────────┘
```

LangGraph is a good fit here specifically because the graph isn't strictly linear once you add error handling: a failed fetcher shouldn't kill the run, and the editor may need to loop back to the summarizer for stories it wants shortened/expanded. Model it as a graph, not a chain, even though v1's happy path is basically linear.

---

## 2. Shared State (`EditionState`)

```python
class RawArticle(TypedDict):
    id: str                 # hash of URL, used for dedup
    source: str              # "hackernews" | "reddit_programming" | ...
    title: str
    url: str
    author: str | None
    published_at: str        # ISO timestamp
    raw_excerpt: str | None  # RSS description / HN text / reddit selftext
    score: float | None      # source-native signal (HN points, reddit upvotes)

class ClusteredStory(TypedDict):
    cluster_id: str
    articles: list[RawArticle]   # 1+ raw articles covering the same story
    primary_url: str             # best/original source in the cluster

class SummarizedStory(TypedDict):
    cluster_id: str
    headline: str
    dek: str                # one-line subhead
    summary: str             # 3-4 sentence body
    sources: list[dict]      # [{name, url}] for attribution
    read_time_min: int

class EditedStory(SummarizedStory):
    section: str              # "front" | "ai_ml" | "dev_tools" | "startups" | "security" | "big_tech" | "launches" | "misc"
    front_page_rank: int | None   # null unless section == "front"

class EditionState(TypedDict):
    date: str
    settings: UserSettings         # feed + model config, loaded once at graph start
    raw_articles: list[RawArticle]
    clusters: list[ClusteredStory]
    summarized: list[SummarizedStory]
    edited: list[EditedStory]
    errors: list[dict]             # {stage, source, message} — non-fatal, surfaced but doesn't halt
```

`EditionState.edited`, grouped by `section`, is exactly what gets serialized as the frontend's `EditionSchema`. Keep this 1:1 mapping strict — it's what makes Phase 1→Phase 4 integration painless.

---

## 3. Agent Definitions

### 3a. Fetcher Agents
Not really "agents" in the LLM sense — deterministic tool-calling nodes, one per source, run in parallel (`asyncio.gather` inside a LangGraph fan-out). No model calls here; keep them cheap and fast. Each returns `list[RawArticle]`, capped by `settings.max_per_source`.

**Free v1 sources:**

| Source | Access | Notes |
|---|---|---|
| Hacker News | Firebase API (`hacker-news.firebaseio.com`) — free, no key | Pull `/topstories.json`, filter by score threshold |
| Reddit | Free OAuth app (script-type, no cost) — `r/programming`, `r/technology`, `r/webdev` | Rate-limited but generous for 1 daily pull |
| Dev.to | Public REST API, no key required | Good for dev-tools/launch-adjacent posts |
| Lobsters | RSS feed, fully open | Smaller but high signal-to-noise |
| TechCrunch | RSS | |
| The Verge (Tech section) | RSS | |
| Ars Technica | RSS | |
| GitHub Trending | No official API — scrape `github.com/trending` or use a maintained unofficial JSON mirror | Flag as best-effort; wrap in try/except since unofficial |

Explicitly **out of v1** (paid/rate-limited/needs approval): NewsAPI.org (free tier is dev-only, not prod), Product Hunt API (needs app review), Twitter/X API (paid now). Revisit in Phase 6.

Each fetcher is independently toggleable via `settings.enabled_sources` — this is exactly what the frontend Settings → Feed configuration screen controls.

### 3b. Dedup / Cluster Agent
Given `raw_articles`, group ones covering the same underlying story (e.g., a model launch covered by HN, TechCrunch, and Reddit simultaneously). v1 approach: cheap embedding similarity on title+excerpt (can use the same model provider as the rest of the pipeline, or a local sentence-transformer to avoid burning API calls on something this mechanical) + a similarity threshold, not a full LLM call per pair. Output: `list[ClusteredStory]`, picking the highest-score/most-original article as `primary_url`.

### 3c. Summarizer Agent
LLM node. One call per cluster (or batched, model-provider dependent). Prompt responsibilities:
- Write a neutral, non-clickbait headline (the source headline is often bad — this agent's whole value-add is editorial voice)
- One-line dek
- 3–4 sentence summary grounded **only** in the fetched excerpt/title — no fabrication if the excerpt is thin, keep the summary shorter rather than inventing detail
- Always carry forward `sources` list for attribution — this is a hard requirement, not optional (see note below on copyright)

Model used here is whatever `settings.model_config.summarizer` points to (Gemini / OpenAI / Ollama Cloud) — this is the exact hook for the frontend's Model Settings panel.

### 3d. Editor Agent
LLM node, receives all `SummarizedStory` items at once (not one-by-one) so it can make relative judgments — this is the one call that actually needs the full picture. Responsibilities:
- Assign each story a `section`
- Pick front-page stories (cap at `settings.front_page_count`, default 4–5) and rank them
- Sanity-check headlines aren't duplicated across sections

### 3e. Publish
No LLM call. Assembles `EditedStory` list into the final edition document, writes to `editions/{date}` in Firestore, matching the frontend `EditionSchema` exactly.

---

## 4. Model Settings (maps directly to frontend Settings → Model)

```python
class ModelConfig(BaseModel):
    provider: Literal["gemini", "openai", "ollama_cloud"]
    model_name: str          # e.g. "gemini-2.5-flash", "gpt-4o-mini", "llama3.1:70b"
    api_key: str | None      # not needed for ollama_cloud if self-hosted
    temperature: float = 0.3
    max_summary_sentences: int = 4

class UserModelSettings(BaseModel):
    summarizer: ModelConfig
    editor: ModelConfig
    # dedup agent intentionally NOT model-configurable in v1 — keep it deterministic/cheap
```

Route through LangChain's chat model wrappers (`ChatGoogleGenerativeAI`, `ChatOpenAI`, and Ollama's OpenAI-compatible endpoint for Ollama Cloud) so swapping providers is a config change, not a code change. Recommend defaulting to Gemini Flash for cost — this pipeline runs once a day on maybe 40–80 articles, so it's cheap regardless, but Flash-tier models are plenty for summarization/classification tasks like these.

---

## 5. Error Handling
- Fetcher failure → logged to `state.errors`, that source's articles are just absent from that day's edition, pipeline continues
- Summarizer/Editor failure on a single cluster → drop that story, log it, don't fail the whole run
- Total fetch failure (all sources down) → publish step should refuse to overwrite a previous good edition with an empty one; surface an error state the frontend can render ("Today's edition couldn't be generated — showing yesterday's")

## 6. Attribution & Copyright Note
Every published story must retain visible source attribution and a link-out to the original — the agent summarizes, it never reproduces. This isn't just good practice, it's the whole point of the product (it should feel like a curated front page pointing you to real journalism, not a scraper). Bake this into the Summarizer prompt as a hard constraint, and make sure `ArticleCard`/reading-view in the frontend always renders the source name + link prominently, not buried.

## 7. Scheduling Hook
Graph entrypoint is a single `run_edition(date: str)` function, invoked by APScheduler/Cloud Scheduler (Phase 5) or manually via `POST /editions/generate` (Phase 3e) for testing. Keep the graph itself scheduler-agnostic — it shouldn't know or care how it was triggered.
