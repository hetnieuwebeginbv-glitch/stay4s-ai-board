#!/usr/bin/env python3
"""Stay4S Web Search Proxy v2 - Uses DDG API + SearXNG public instances"""

import json, logging, requests
from fastapi import FastAPI, Query
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stay4s-search")

app = FastAPI(title="Stay4S Search Proxy v2", version="2.0")

def search_ddg_api(query, limit=5):
    """Search via DuckDuckGo Instant Answer API"""
    try:
        r = requests.get("https://api.duckduckgo.com/", params={
            "q": query, "format": "json", "no_html": 1, "skip_disambig": 1
        }, headers={"User-Agent": "Stay4S/1.0"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = []
            if data.get("Abstract"):
                results.append({"title": data.get("Heading", query), "url": data.get("AbstractURL", ""), "content": data["Abstract"][:200]})
            for topic in data.get("RelatedTopics", [])[:limit]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({"title": topic["Text"][:60], "url": topic.get("FirstURL", ""), "content": topic["Text"][:200]})
                elif isinstance(topic, dict) and "Topics" in topic:
                    for sub in topic["Topics"][:2]:
                        if isinstance(sub, dict) and sub.get("Text"):
                            results.append({"title": sub["Text"][:60], "url": sub.get("FirstURL", ""), "content": sub["Text"][:200]})
            return results[:limit]
    except Exception as e:
        logger.error(f"DDG API failed: {e}")
    return []

def search_searxng_public(query, limit=5):
    """Search via public SearXNG instance"""
    instances = ["https://searx.be/search", "https://search.sapti.me/search", "https://searx.tiekoetter.com/search"]
    for instance in instances:
        try:
            r = requests.get(instance, params={"q": query, "format": "json"}, 
                           headers={"User-Agent": "Stay4S/1.0"}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                results = []
                for item in data.get("results", [])[:limit]:
                    results.append({"title": item.get("title", ""), "url": item.get("url", ""), "content": item.get("content", "")[:200]})
                if results:
                    return results
        except:
            continue
    return []

@app.get("/search")
async def search(q: str = Query(...)):
    """Search via DDG API + SearXNG public instances"""
    ddg = search_ddg_api(q)
    searx = search_searxng_public(q) if len(ddg) < 3 else []
    
    all_results = ddg + searx
    # Deduplicate by URL
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    
    return {"results": unique, "query": q, "count": len(unique)}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "stay4s-search-proxy-v2"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7862)
