import json
import urllib.request
import urllib.parse
from langchain_core.tools import tool
import feedparser

@tool(description="Fetches the top stories currently trending on Hacker News.")
def fetch_hacker_news_top(limit: int = 5) -> str:
    """
    Fetches the top stories currently trending on Hacker News.
    Always use this tool if you need breaking tech news.
    Returns a JSON string containing the title, URL, and score of the top stories.
    """
    try:
        # Get top 50 story IDs
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyDispatch/1.0'})
        with urllib.request.urlopen(req) as response:
            story_ids = json.loads(response.read().decode())[:limit]
            
        stories = []
        for sid in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
            s_req = urllib.request.Request(story_url, headers={'User-Agent': 'DailyDispatch/1.0'})
            with urllib.request.urlopen(s_req) as s_res:
                story_data = json.loads(s_res.read().decode())
                # Only care about real links, not Ask HN or polls for now
                if story_data.get('url'):
                    stories.append({
                        "title": story_data.get('title'),
                        "url": story_data.get('url'),
                        "score": story_data.get('score'),
                        "source": "Hacker News"
                    })
        return json.dumps(stories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch Hacker News: {str(e)}"})

@tool(description="Fetches the top stories currently trending on r/technology and r/programming on Reddit.")
def fetch_reddit_technology(limit: int = 5) -> str:
    """
    Fetches the top stories currently trending on r/technology and r/programming on Reddit.
    Returns a JSON string containing the title, URL, score, and source.
    """
    try:
        stories = []
        for subreddit in ["technology", "programming"]:
            url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
            req = urllib.request.Request(url, headers={'User-Agent': 'DailyDispatch/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                if post.get("url"):
                    stories.append({
                        "title": post.get("title"),
                        "url": post.get("url"),
                        "score": post.get("score"),
                        "source": f"Reddit r/{subreddit}"
                    })
        return json.dumps(stories[:limit*2], indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch Reddit: {str(e)}"})

@tool(description="Fetches the top trending articles on Dev.to.")
def fetch_dev_to_articles(limit: int = 5) -> str:
    """
    Fetches the top trending articles on Dev.to.
    Returns a JSON string containing the title, URL, score, and source.
    """
    try:
        url = f"https://dev.to/api/articles?top=1&per_page={limit}"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyDispatch/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        stories = []
        for post in data:
            if post.get("url"):
                stories.append({
                    "title": post.get("title"),
                    "url": post.get("url"),
                    "score": post.get("public_reactions_count"),
                    "source": "Dev.to"
                })
        return json.dumps(stories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch Dev.to: {str(e)}"})

@tool(description="Fetches the most popular newly created repositories on GitHub.")
def fetch_github_trending(limit: int = 5) -> str:
    """
    Fetches the most popular newly created repositories on GitHub.
    Returns a JSON string containing the title, URL, description, and score.
    """
    try:
        # Search for repos created recently, sorted by stars
        from datetime import datetime, timedelta
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"https://api.github.com/search/repositories?q=created:>{last_week}&sort=stars&order=desc&per_page={limit}"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyDispatch/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        stories = []
        for repo in data.get("items", []):
            stories.append({
                "title": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "score": repo.get("stargazers_count"),
                "source": "GitHub Trending"
            })
        return json.dumps(stories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch GitHub: {str(e)}"})

@tool(description="Fetches the latest articles from TechCrunch RSS feed.")
def fetch_techcrunch_rss(limit: int = 5) -> str:
    """
    Fetches the latest articles from TechCrunch RSS feed.
    Returns a JSON string containing the title, URL, and summary of the top stories.
    """
    try:
        feed = feedparser.parse("https://techcrunch.com/feed/")
        stories = []
        for entry in feed.entries[:limit]:
            stories.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "summary": entry.get("summary", "")[:200] + "...",
                "source": feed.feed.get("title", "TechCrunch")
            })
        return json.dumps(stories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch TechCrunch RSS: {str(e)}"})

@tool(description="Fetches the latest articles from The Verge RSS feed.")
def fetch_theverge_rss(limit: int = 5) -> str:
    """
    Fetches the latest articles from The Verge RSS feed.
    Returns a JSON string containing the title, URL, and summary of the top stories.
    """
    try:
        feed = feedparser.parse("https://www.theverge.com/rss/index.xml")
        stories = []
        for entry in feed.entries[:limit]:
            stories.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "summary": entry.get("summary", "")[:200] + "...",
                "source": feed.feed.get("title", "The Verge")
            })
        return json.dumps(stories, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch The Verge RSS: {str(e)}"})

@tool(description="Searches for an image using DuckDuckGo based on a search query.")
def fetch_image_duckduckgo(query: str) -> dict:
    """
    Searches for an image using DuckDuckGo.
    Returns a dictionary containing src, alt, caption, and credit.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().images(keywords=query, max_results=1)
        if results:
            img = results[0]
            return {
                "src": img.get("image"),
                "alt": img.get("title", "Image result"),
                "caption": img.get("title", ""),
                "credit": img.get("source", "DuckDuckGo Image Search")
            }
        return {}
    except Exception as e:
        print(f"Image search failed: {e}")
        return {}
