import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from app.graph.state import NewsroomState
from app.graph.schema.models import DraftArticle
from app.models.edition import EditionSchema, EditionSource, EditionCategory, Page, ArticleStory, Author, Source, Image

console = Console()

STATIC_SOURCES = [
    {"id": "hackernews", "name": "Hacker News", "url": "https://news.ycombinator.com/", "description": "Community discussion and launch radar"},
    {"id": "reddit_programming", "name": "Reddit /r/programming", "url": "https://www.reddit.com/r/programming/", "description": "Developer discussion and tooling chatter"},
    {"id": "reddit_technology", "name": "Reddit /r/technology", "url": "https://www.reddit.com/r/technology/", "description": "General technology and policy discussion"},
    {"id": "devto", "name": "Dev.to", "url": "https://dev.to/", "description": "Practical engineering write-ups"},
    {"id": "lobsters", "name": "Lobsters", "url": "https://lobste.rs/", "description": "High-signal engineering links"},
    {"id": "techcrunch", "name": "TechCrunch", "url": "https://techcrunch.com/", "description": "Startups, launches, and funding coverage"},
    {"id": "the_verge", "name": "The Verge", "url": "https://www.theverge.com/tech", "description": "Consumer tech and platform coverage"},
    {"id": "ars_technica", "name": "Ars Technica", "url": "https://arstechnica.com/", "description": "Technical reporting and platform analysis"},
    {"id": "github_trending", "name": "GitHub Trending", "url": "https://github.com/trending", "description": "Projects gaining traction today"},
]

STATIC_CATEGORIES = [
    {"id": "front", "title": "Front Page", "description": "The lead stories of the day"},
    {"id": "ai_ml", "title": "AI / ML", "description": "Model launches, prompting, and inference economics"},
    {"id": "dev_tools", "title": "Dev Tools", "description": "Editor, CLI, and workflow tooling"},
    {"id": "startups", "title": "Startups", "description": "Early-stage launches and operating lessons"},
    {"id": "security", "title": "Security", "description": "Identity, hardening, and privacy coverage"},
    {"id": "big_tech", "title": "Big Tech", "description": "Platform shifts and product policy"},
    {"id": "launches", "title": "Launches", "description": "Product reveals and release notes"},
    {"id": "misc", "title": "Misc", "description": "Notes that do not fit a clean desk"},
    {"id": "education", "title": "Education", "description": "Bootcamps, universities, and learning resources"},
    {"id": "business", "title": "Business", "description": "Startups, venture capital, and market trends"},
]

DESK_TO_CATEGORY = {
    "front_desk": "front",
    "ai_ml_desk": "ai_ml",
    "security_desk": "security",
    "education_desk": "education",
    "economics_desk": "business",
    "classifieds_desk": "misc",
    "weather_puzzles_desk": "misc",
    "obituaries_births_desk": "misc",
    "sports_desk": "misc",
}

PAGE_CONFIGS = [
    {"template": "front", "title": "Front Page", "deck": "The lead stories of the day."},
    {"template": "three-column", "title": "AI & Machine Learning", "deck": "Frontier models, inference economics, and research breakthroughs."},
    {"template": "split", "title": "Security", "deck": "Identity, hardening, privacy coverage, and cybersecurity."},
    {"template": "three-column", "title": "Education", "deck": "Bootcamps, CS Degrees, and learning resources."},
    {"template": "split", "title": "Business & Economy", "deck": "Startups, venture capital, and market trends."},
    {"template": "stack", "title": "Miscellany", "deck": "Notes, puzzles, classifieds, and dispatches."},
]

CATEGORY_TO_PAGE = {
    "front": 0,
    "ai_ml": 1,
    "security": 2,
    "education": 3,
    "business": 4,
    "misc": 5,
    "dev_tools": 0,
    "startups": 4,
    "big_tech": 0,
    "launches": 1,
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text[:60]


def generate_id(draft: DraftArticle) -> str:
    category = DESK_TO_CATEGORY.get(draft.section, "misc")
    slug = slugify(draft.headline)[:40]
    return f"{category}-{slug}"


def make_timestamp(date_str: str, hour: int, minute: int) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        dt = datetime.now()
    minute = min(minute, 59)
    dt = dt.replace(hour=min(hour, 23), minute=minute, second=0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    return dt.isoformat()


def assign_layout_hint(importance: int | None, index: int) -> str:
    if importance == 5:
        return "hero"
    elif importance == 4 and index < 3:
        return "feature"
    elif importance == 3 and index == 0:
        return "feature"
    return "brief"


def build_article_story(draft: DraftArticle, page_num: int, article_index: int, date_str: str) -> ArticleStory:
    category = DESK_TO_CATEGORY.get(draft.section, "misc")
    content = draft.body_paragraphs if draft.body_paragraphs else [draft.summary]
    authors = [Author(name=draft.author_byline, role="AI Correspondent", aiGenerated=True)]
    sources = [Source(name=s.name, url=s.url, note=s.note) for s in draft.sources]
    source_ids = [slugify(s.name) for s in draft.sources]
    images = [Image(src=img.src, alt=img.alt, caption=img.caption, credit=img.credit) for img in draft.images]
    hour = 5 + (article_index * 2) // 60
    minute = 30 + (article_index * 2) % 60
    return ArticleStory(
        id=generate_id(draft),
        page=page_num,
        category=category,
        importance=draft.importance if draft.importance else 3,
        title=draft.headline,
        subtitle=draft.dek,
        kicker=draft.kicker,
        authors=authors,
        sourceIds=source_ids,
        sources=sources,
        images=images,
        content=content,
        tags=draft.tags,
        publishedAt=make_timestamp(date_str, hour, minute),
        readTimeMin=draft.read_time_min,
        layoutHint=None,
    )


def publish_node(state: NewsroomState) -> Dict[str, Any]:
    console.print()
    console.print(Panel(
        "[bold magenta]📰  LAYOUT & PUBLISH DESK[/bold magenta]\n"
        "Assembling the final edition from approved drafts...",
        border_style="magenta",
        subtitle="🔧 Production",
    ))

    drafts = state.get("drafts", [])
    approved = [d for d in drafts if d.status == "approved"]

    if not approved:
        console.print(Panel(
            "[red]❌ No approved drafts to publish![/red]",
            border_style="red",
            title="Publish Error",
        ))
        return {"errors": [{"desk": "publisher", "message": "No approved drafts available"}]}

    # ── Article compilation table ───────────────────────────────────────────
    compile_table = Table(
        title=f"📄 Compiling {len(approved)} Article(s)",
        box=box.ROUNDED,
        border_style="magenta",
    )
    compile_table.add_column("#", style="dim", width=3)
    compile_table.add_column("Category", style="cyan")
    compile_table.add_column("Page Name", style="yellow")
    compile_table.add_column("Headline", style="bold", max_width=45)
    compile_table.add_column("Page", justify="center")
    compile_table.add_column("Template", style="blue")
    compile_table.add_column("Layout", style="green")
    compile_table.add_column("Paras")

    # ── Build article stories grouped by page ───────────────────────────────
    articles_by_page: Dict[int, List[ArticleStory]] = {}
    for i, draft in enumerate(approved):
        category = DESK_TO_CATEGORY.get(draft.section, "misc")
        page_idx = CATEGORY_TO_PAGE.get(category, 5)
        page_num = page_idx + 1
        story = build_article_story(draft, page_num, i, state.get("date", ""))
        articles_by_page.setdefault(page_idx, []).append(story)

    # ── Assign per-page layout hints ─────────────────────────────────────────
    for page_idx, stories in articles_by_page.items():
        for pos, story in enumerate(stories):
            story.layoutHint = assign_layout_hint(story.importance, pos)

    # ── Render compile table ─────────────────────────────────────────────────
    entry_idx = 0
    for page_idx in sorted(articles_by_page.keys()):
        cfg = PAGE_CONFIGS[page_idx]
        for story in articles_by_page[page_idx]:
            paras = str(len(story.content))
            compile_table.add_row(
                str(entry_idx),
                story.category,
                cfg["title"],
                story.title[:44],
                str(story.page),
                cfg["template"],
                story.layoutHint or "—",
                paras,
            )
            entry_idx += 1

    console.print(compile_table)

    # ── Build pages ─────────────────────────────────────────────────────────
    pages: List[Page] = []
    for page_idx in sorted(articles_by_page.keys()):
        cfg = PAGE_CONFIGS[page_idx]
        pages.append(Page(
            page=page_idx + 1,
            template=cfg["template"],
            title=cfg["title"],
            deck=cfg["deck"],
            articles=articles_by_page[page_idx],
        ))

    volume = 1
    issue = 1

    # ── Final edition ───────────────────────────────────────────────────────
    edition = EditionSchema(
        volume=volume,
        issue=issue,
        issueDate=state.get("date", datetime.now().strftime("%Y-%m-%d")),
        sources=[EditionSource(**s) for s in STATIC_SOURCES],
        categories=[EditionCategory(**c) for c in STATIC_CATEGORIES],
        pages=pages,
    )

    edition_dict = edition.model_dump(mode="json")

    # ── Summary panel ───────────────────────────────────────────────────────
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold", justify="right")
    summary.add_column()
    summary.add_row("Volume", f"{volume}.{issue}")
    summary.add_row("Date", edition.issueDate)
    summary.add_row("Pages", str(len(pages)))
    summary.add_row("Articles", str(len(approved)))
    summary.add_row("Sources", str(len(edition.sources)))
    summary.add_row("Categories", str(len(edition.categories)))

    console.print(Panel(
        summary,
        border_style="green",
        title="✅ Edition Complete",
        subtitle="📰 The Daily Dispatch",
    ))

    # ── Page layout preview ─────────────────────────────────────────────────
    console.print()
    console.print("[bold]📖 Page Layout:[/bold]")
    for p in pages:
        art_titles = "\n".join(f"  {a.layoutHint or '•':>8} | {a.title[:55]}" for a in p.articles)
        console.print(f"  [cyan]Page {p.page}[/cyan] — [bold]{p.title}[/bold] ({p.template})")
        console.print(art_titles)

    return {"compiled_edition": edition_dict}
