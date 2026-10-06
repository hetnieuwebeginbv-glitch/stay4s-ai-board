#!/usr/bin/env python3
"""Stay4S Nexus Connectors v2 -- Expanded plugin system

New connectors for the Nexus platform:
1. Ollama connector - query local AI models
2. RAG connector - search knowledge base
3. SearXNG connector - web search
4. HuggingFace connector - download/upload models
5. GitHub connector - repo management
6. RunPod connector - GPU pod management
7. WhatsApp connector - send/receive messages
8. Voice connector - speech-to-text, text-to-speech
9. Image gen connector - generate images
10. Video gen connector - generate videos
"""

import os, json, logging, requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus-connectors")

app = FastAPI(title="Stay4S Nexus Connectors v2", version="2.0")

OLLAMA_URL = "http://localhost:11434"
RAG_URL = "http://localhost:8087"
SEARXNG_URL = "http://localhost:8888"
HOOFDAGENT_URL = "http://localhost:8093"
VOICE_URL = "http://localhost:8096"
IMAGE_URL = "http://localhost:7860"
VIDEO_URL = "http://localhost:7861"

class ConnectorRequest(BaseModel):
    action: str
    params: dict = {}

# 1. Ollama Connector
@app.post("/ollama")
async def ollama_connector(req: ConnectorRequest):
    action = req.action
    params = req.params
    
    if action == "list_models":
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        return r.json()
    elif action == "generate":
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": params.get("model", "stay4s-1b"),
            "prompt": params.get("prompt", ""),
            "stream": False,
            "options": {"temperature": params.get("temperature", 0.7)}
        }, timeout=120)
        return r.json()
    elif action == "chat":
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": params.get("model", "stay4s-1b"),
            "messages": params.get("messages", []),
            "stream": False
        }, timeout=120)
        return r.json()
    return {"error": f"Unknown action: {action}"}

# 2. RAG Connector
@app.post("/rag")
async def rag_connector(req: ConnectorRequest):
    if req.action == "search":
        r = requests.post(f"{RAG_URL}/search", json={
            "query": req.params.get("query", ""),
            "top_k": req.params.get("top_k", 5)
        }, timeout=15)
        return r.json()
    elif req.action == "add":
        r = requests.post(f"{RAG_URL}/add", json={
            "content": req.params.get("content", ""),
            "title": req.params.get("title", ""),
            "category": req.params.get("category", "general")
        }, timeout=15)
        return r.json()
    return {"error": f"Unknown action: {req.action}"}

# 3. SearXNG Connector
@app.post("/search")
async def search_connector(req: ConnectorRequest):
    r = requests.get(f"{SEARXNG_URL}/search", params={
        "q": req.params.get("query", ""),
        "format": "json"
    }, timeout=15)
    return r.json()

# 4. Hoofdagent Connector
@app.post("/hoofdagent")
async def hoofdagent_connector(req: ConnectorRequest):
    if req.action == "chat":
        r = requests.post(f"{HOOFDAGENT_URL}/chat", json={
            "message": req.params.get("message", ""),
            "model": req.params.get("model"),
            "use_rag": req.params.get("use_rag", True)
        }, timeout=120)
        return r.json()
    elif req.action == "opdracht":
        r = requests.post(f"{HOOFDAGENT_URL}/opdrachten", json={
            "titel": req.params.get("titel", ""),
            "beschrijving": req.params.get("beschrijving", ""),
            "toegewezen_agent": req.params.get("agent"),
            "prioriteit": req.params.get("prioriteit", "normaal")
        }, timeout=15)
        return r.json()
    elif req.action == "list_opdrachten":
        r = requests.get(f"{HOOFDAGENT_URL}/opdrachten", timeout=10)
        return r.json()
    return {"error": f"Unknown action: {req.action}"}

# 5. Voice Connector
@app.post("/voice")
async def voice_connector(req: ConnectorRequest):
    if req.action == "transcribe":
        # Forward to voice server
        r = requests.post(f"{VOICE_URL}/transcribe", json={
            "audio": req.params.get("audio", "")
        }, timeout=30)
        return r.json()
    elif req.action == "speak":
        r = requests.post(f"{VOICE_URL}/speak", json={
            "text": req.params.get("text", "")
        }, timeout=30)
        return r.json()
    return {"error": f"Unknown action: {req.action}"}

# 6. Image Gen Connector
@app.post("/image")
async def image_connector(req: ConnectorRequest):
    if req.action == "generate":
        try:
            r = requests.post(f"{IMAGE_URL}/generate", json={
                "prompt": req.params.get("prompt", ""),
                "width": req.params.get("width", 512),
                "height": req.params.get("height", 512)
            }, timeout=120)
            return r.json()
        except:
            return {"error": "Image server not running (starts after training)"}
    return {"error": f"Unknown action: {req.action}"}

# 7. Video Gen Connector
@app.post("/video")
async def video_connector(req: ConnectorRequest):
    if req.action == "generate":
        try:
            r = requests.post(f"{VIDEO_URL}/generate", json={
                "prompt": req.params.get("prompt", ""),
                "num_frames": req.params.get("num_frames", 32)
            }, timeout=300)
            return r.json()
        except:
            return {"error": "Video server not running (starts after training)"}
    return {"error": f"Unknown action: {req.action}"}

# 8. System Status Connector
@app.get("/status")
async def system_status():
    services = {}
    for name, url in [("ollama", OLLAMA_URL), ("rag", RAG_URL), ("searxng", SEARXNG_URL),
                       ("hoofdagent", HOOFDAGENT_URL), ("voice", VOICE_URL)]:
        try:
            r = requests.get(f"{url}/health" if name != "ollama" else f"{url}/api/tags", timeout=5)
            services[name] = "ok" if r.status_code == 200 else "error"
        except:
            services[name] = "offline"
    
    # Add image/video status
    services["image_gen"] = "pending"  # starts after training
    services["video_gen"] = "pending"
    
    return {
        "status": "ok",
        "services": services,
        "connectors": ["ollama", "rag", "search", "hoofdagent", "voice", "image", "video"]
    }

@app.get("/")
async def root():
    return {
        "service": "Stay4S Nexus Connectors v2",
        "connectors": ["ollama", "rag", "search", "hoofdagent", "voice", "image", "video"],
        "endpoints": ["/ollama", "/rag", "/search", "/hoofdagent", "/voice", "/image", "/video", "/status"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8094)
