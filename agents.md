# agents.md — Daily Dispatch Agent Pipeline

This document defines the LangGraph agent pipeline that turns raw feed data into a published "edition." It's the contract for Phase 3 of `plan.md`, written now so the frontend's `EditionSchema` (Phase 1) can be designed against it from day one.

> **Environment note:** backend package management is **`uv`**, exclusively. Install deps with `uv add <package>`, run scripts/servers with `uv run ...`, lockfile is `uv.lock` (commit it). Do not introduce `requirements.txt`, `pip install`, or `poetry` — if you're an AI agent implementing this pipeline, this is a hard constraint, not a suggestion.

---

## 1. Pipeline Overview: The Multi-Agent Newsroom

We use a **Hierarchical Supervisor Pattern** in LangGraph. Instead of a linear data pipeline, we simulate a physical newsroom where a Chief Editor orchestrates various specialized Desk Agents.

```text
        ┌──────────────┐
        │  Scheduler   │  (cron, 5:30 AM daily)
        └──────┬───────┘
               ▼
   ┌───────────────────────┐
   │ Chief Editor (Admin)  │  (Supervisor Node: Plans layout, reviews, ranks)
   └─────┬───────────▲─────┘
         │           │
         ▼           │
   ┌───────────────────────┐
   │    Section Desks      │  (Worker Nodes running in parallel)
   │  - AI & ML Desk       │  (Uses tools to search HN/Reddit, dedups, writes)
   │  - Security Desk      │
   │  - Puzzles Desk       │
   │  - Economics Desk     │
   └───────────────────────┘
               │ (Once all drafts approved)
               ▼
   ┌───────────────────────┐
   │    Layout / Publish   │  → formats `dummy.json` and writes to Firestore
   └───────────────────────┘
```

---

## 2. Shared State (`NewsroomState`)

```python
class DraftArticle(TypedDict):
    section: str             # "ai_ml" | "security" | "puzzles" | etc.
    headline: str
    dek: str                 # one-line subhead
    summary: str             # 3-4 sentence body
    sources: list[dict]      # [{name, url}] for attribution
    read_time_min: int
    author_byline: str       # e.g., "G. Flash, AI Correspondent"
    status: str              # "pending_review" | "approved" | "rejected"
    feedback: str | None     # Chief Editor's notes if rejected
    front_page_rank: int | None # Assigned by Chief Editor if approved

class NewsroomState(TypedDict):
    date: str
    settings: dict                 # feed + model config, loaded once at graph start
    assignments: list[dict]        # e.g. [{"desk": "ai_ml", "count": 2}]
    drafts: list[DraftArticle]     # Articles submitted by the desks
    errors: list[dict]             # {desk, source, message} — non-fatal
```

`NewsroomState.drafts` (once all are `"approved"`) gets compiled by the Publisher step into the final frontend `EditionSchema`.

---

## 3. Agent Definitions

### 3a. The Chief Editor (Supervisor Agent)
The central routing node. 
- **Planning:** Wakes up, looks at the target layout, and dispatches assignments to the Desks.
- **Review:** Evaluates submitted `DraftArticles`. If a draft is poor quality, hallucinates, or misses the point, it sets `status="rejected"`, populates `feedback`, and routes the graph back to that specific Desk to try again.
- **Layout & Ranking:** Once all drafts are `"approved"`, it assigns the `front_page_rank` and `importance` scores (1-5) which dictates the grid span on the frontend.

### 3b. The Section Desks (Worker Agents)
Each desk (AI, Security, Education, Puzzles, etc.) is a specialized worker node with its own system prompt dictating its tone and "beat".
- **Autonomy:** They use Fetcher Tools to hunt for news autonomously based on their beat.
- **Synthesis:** They group related stories together (deduplication) and write the article based *only* on the fetched content.
- **Personality:** e.g., the `puzzles_desk` generates a daily DSA puzzle. The `obituary_desk` writes satirical eulogies for deprecated tech.

### 3c. Fetcher Tools (The "Scrapers")
Deterministic functions exposed to the Desk Agents as LangChain tools.
- Hacker News API (Free)
- Reddit (Free OAuth script)
- Dev.to API (Free)
- RSS Feeds (TechCrunch, Lobsters, The Verge)
- *Note: Agents must gracefully handle tool failures.*

---

## 4. Model Settings & Byline Strategy

We playfully break the fourth wall. Each Desk is assigned an LLM, and that LLM writes under a "Journalistic Pen Name" that proudly displays its architecture.

```python
class ModelConfig(BaseModel):
    provider: Literal["gemini", "openai", "ollama_cloud", "groq"]
    model_name: str          # e.g. "gemini-2.5-flash", "gpt-4o", "llama3.1:70b"
    pen_name: str            # e.g. "G. Flash", "C. GPT", "Unit 7 (Llama)"
    role: str                # e.g. "Senior AI Correspondent"
```

The `author_byline` on the `ArticleCard` in the frontend will render this combination, providing a built-in meta-experiment to see which models write the best articles for which desks.

---

## 5. Error Handling
- **Tool Failure:** Logged to `state.errors`, the Desk tries a different source.
- **Draft Rejection Loop Limit:** The Chief Editor should have a max retry limit (e.g., 2 retries per article) to prevent infinite loops. If it fails, that article is dropped.
- **Total Failure:** If all sources are down, the publish step refuses to overwrite the database.

## 6. Attribution & Copyright Note
Every published story must retain visible source attribution and a link-out to the original — the agent summarizes, it never reproduces. This is a hard constraint in every Desk Agent's system prompt.

## 7. Scheduling Hook
Graph entrypoint is a single `run_edition(date: str)` function, invoked by APScheduler/Cloud Scheduler or manually via `POST /editions/generate` for testing.
