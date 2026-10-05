#!/usr/bin/env python3
"""Stay4S Unified AI Gateway - The Decaan Router

Routes user queries to the right model/tool:
- Simple questions -> 1B model (fast, local)
- Code questions -> qwen2.5-coder
- Vision questions -> llama3.2-vision
- Image generation -> image gen server
- Video generation -> video gen server
- Web search -> SearXNG
- RAG -> knowledge base
- Complex reasoning -> 14B model (if available)

API on port 8092
"""

import os, json, time, logging, requests, asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stay4s-gateway")

app = FastAPI(title="Stay4S AI Gateway", version="2.0")

# Service URLs
OLLAMA_URL = "http://localhost:11434"
SEARXNG_URL = "http://localhost:8888"
RAG_URL = "http://localhost:8087"
MEMORY_URL = "http://localhost:8089"
IMAGE_URL = os.environ.get("STAY4S_IMAGE_URL", "http://localhost:7860")
VIDEO_URL = os.environ.get("STAY4S_VIDEO_URL", "http://localhost:7861")

# Model routing rules
ROUTING_RULES = [
    {"keywords": ["code", "python", "javascript", "kotlin", "programmeer", "functie", "bug", "error"], "model": "qwen2.5-coder:7b", "tool": None},
    {"keywords": ["afbeelding", "teken", "genereer foto", "maak plaatje", "image", "draw", "picture"], "model": None, "tool": "image"},
    {"keywords": ["video", "film", "animeer", "animate"], "model": None, "tool": "video"},
    {"keywords": ["zoek", "search", "google", "internet", "laatste nieuws", "wie is", "wat is er"], "model": None, "tool": "search"},
    {"keywords": ["vision", "foto bekijken", "wat zie je", "analyseer afbeelding"], "model": "llama3.2-vision", "tool": None},
    {"keywords": ["scam", "oplichter", "fraude", "phishing", "verdacht"], "model": "stay4s-1b", "tool": "scam"},
]

class ChatRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    context: Optional[str] = None
    use_rag: bool = True
    use_search: bool = False
    stream: bool = False

def route_query(prompt):
    """Decide which model/tool to use based on keywords"""
    prompt_lower = prompt.lower()
    
    for rule in ROUTING_RULES:
        for kw in rule["keywords"]:
            if kw in prompt_lower:
                return rule
    
    # Default: use 1B for short prompts, 14B for long
    if len(prompt) < 100:
        return {"model": "stay4s-1b", "tool": None}
    else:
        return {"model": "stay4s-1b", "tool": None}

def query_ollama(model, prompt, context=""):
    """Query Ollama model"""
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 500}
        }, timeout=120)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama query failed: {e}")
    return None

def query_searxng(query):
    """Query SearXNG for web search"""
    try:
        r = requests.get(f"{SEARXNG_URL}/search", params={"q": query, "format": "json"}, timeout=15)
        if r.status_code == 200:
            results = r.json().get("results", [])[:5]
            return [{"title": x.get("title"), "url": x.get("url"), "content": x.get("content", "")[:200]} for x in results]
    except Exception as e:
        logger.error(f"SearXNG query failed: {e}")
    return []

def query_rag(query):
    """Query RAG for knowledge"""
    try:
        r = requests.post(f"{RAG_URL}/search", json={"query": query, "top_k": 3}, timeout=15)
        if r.status_code == 200:
            return r.json().get("results", [])
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
    return []

@app.post("/chat")
async def chat(req: ChatRequest):
    """Unified chat endpoint with automatic routing"""
    start = time.time()
    
    route = route_query(req.prompt)
    model = req.model or route["model"]
    tool = route["tool"]
    
    logger.info(f"Routing: model={model}, tool={tool}, prompt={req.prompt[:50]}...")
    
    # Handle tool-based requests
    if tool == "search":
        results = query_searxng(req.prompt)
        return {"results": results, "tool": "search", "latency_ms": round((time.time()-start)*1000)}
    
    if tool == "image":
        try:
            r = requests.post(f"{IMAGE_URL}/generate", json={"prompt": req.prompt}, timeout=120)
            if r.status_code == 200:
                return {**r.json(), "tool": "image", "latency_ms": round((time.time()-start)*1000)}
        except Exception as e:
            return {"error": f"Image gen failed: {e}"}
    
    if tool == "video":
        try:
            r = requests.post(f"{VIDEO_URL}/generate", json={"prompt": req.prompt}, timeout=300)
            if r.status_code == 200:
                return {**r.json(), "tool": "video", "latency_ms": round((time.time()-start)*1000)}
        except Exception as e:
            return {"error": f"Video gen failed: {e}"}
    
    # Get RAG context if enabled
    context = req.context or ""
    if req.use_rag:
        rag_results = query_rag(req.prompt)
        if rag_results:
            context = "\n".join([r.get("content", "") for r in rag_results[:3]])
    
    # Query model
    response = query_ollama(model, req.prompt, context)
    
    if response is None:
        response = "Sorry, ik kon geen antwoord genereren. Probeer het opnieuw."
    
    return {
        "response": response,
        "model": model,
        "tool": tool,
        "rag_used": req.use_rag and bool(context),
        "latency_ms": round((time.time()-start)*1000)
    }

@app.get("/health")
async def health():
    """Health check with service status"""
    services = {}
    for name, url in [("ollama", OLLAMA_URL), ("searxng", SEARXNG_URL), ("rag", RAG_URL), ("memory", MEMORY_URL)]:
        try:
            r = requests.get(f"{url}/api/tags" if name == "ollama" else f"{url}/health", timeout=5)
            services[name] = "ok" if r.status_code == 200 else "error"
        except:
            services[name] = "offline"
    
    return {"status": "ok", "services": services}

@app.get("/")
async def root():
    return HTMLResponse("""
    <html><head><title>Stay4S AI Gateway</title></head>
    <body style='font-family: sans-serif; max-width: 800px; margin: 50px auto;'>
    <h1>Stay4S AI Gateway - Decaan Router</h1>
    <p>Automatische routering naar het juiste AI model of tool.</p>
    <h3>Endpoints:</h3>
    <ul>
    <li>POST /chat - Chat met automatische model selectie</li>
    <li>GET /health - Service status</li>
    </ul>
    <h3>Modellen:</h3>
    <ul>
    <li>stay4s-1b - Simpele vragen (snel, lokaal)</li>
    <li>qwen2.5-coder:7b - Code vragen</li>
    <li>llama3.2-vision - Vision/afbeeldingen</li>
    </ul>
    <h3>Tools:</h3>
    <ul>
    <li>SearXNG - Web zoeken</li>
    <li>RAG - Knowledge base</li>
    <li>Image Gen - Afbeelding generatie</li>
    <li>Video Gen - Video generatie</li>
    </ul>
    </body></html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8092)
