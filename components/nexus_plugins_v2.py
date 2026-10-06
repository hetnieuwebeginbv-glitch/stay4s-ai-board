#!/usr/bin/env python3
"""Stay4S Nexus Plugins v2 -- GitHub, RunPod, HuggingFace connectors

These plugins extend the Nexus platform with external service integration.
"""

import os, json, logging, requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus-plugins")

app = FastAPI(title="Stay4S Nexus Plugins v2", version="2.0")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
RUNPOD_KEY = os.environ.get("RUNPOD_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

class PluginRequest(BaseModel):
    action: str
    params: dict = {}

# 1. GitHub Plugin
@app.post("/github")
async def github_plugin(req: PluginRequest):
    action = req.action
    params = req.params
    
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    if action == "list_repos":
        owner = params.get("owner", "hetnieuwebeginbv-glitch")
        r = requests.get(f"https://api.github.com/users/{owner}/repos?per_page=100", headers=headers, timeout=15)
        repos = [{"name": x["name"], "desc": x.get("description",""), "updated": x["updated_at"]} for x in r.json()[:20]]
        return {"repos": repos, "count": len(repos)}
    
    elif action == "list_files":
        owner = params.get("owner", "hetnieuwebeginbv-glitch")
        repo = params.get("repo", "")
        path = params.get("path", "")
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers, timeout=15)
        if r.status_code == 200:
            files = [{"name": x["name"], "size": x.get("size",0), "type": x["type"]} for x in r.json()]
            return {"files": files}
        return {"error": r.text[:200]}
    
    elif action == "read_file":
        owner = params.get("owner", "hetnieuwebeginbv-glitch")
        repo = params.get("repo", "")
        path = params.get("path", "")
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers, timeout=15)
        if r.status_code == 200:
            import base64
            content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="replace")
            return {"content": content[:5000], "name": r.json()["name"]}
        return {"error": r.text[:200]}
    
    elif action == "push_file":
        owner = params.get("owner", "hetnieuwebeginbv-glitch")
        repo = params.get("repo", "")
        path = params.get("path", "")
        content = params.get("content", "")
        message = params.get("message", "Stay4S auto push")
        import base64
        body = {"message": message, "content": base64.b64encode(content.encode()).decode()}
        r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers, json=body, timeout=15)
        return {"status": r.status_code, "ok": r.status_code == 201}
    
    return {"error": f"Unknown action: {action}"}

# 2. RunPod Plugin
@app.post("/runpod")
async def runpod_plugin(req: PluginRequest):
    action = req.action
    params = req.params
    headers = {"Authorization": RUNPOD_KEY}
    
    if action == "list_pods":
        body = {"query": 'query { myself { pods { id name desiredStatus machine { gpuTypeId } } } }'}
        r = requests.post("https://api.runpod.io/graphql", headers=headers, json=body, timeout=15)
        if r.status_code == 200:
            pods = r.json().get("data",{}).get("myself",{}).get("pods",[])
            return {"pods": [{"id": p["id"], "name": p["name"], "status": p["desiredStatus"]} for p in pods]}
        return {"error": r.text[:200]}
    
    elif action == "stop_pod":
        pod_id = params.get("pod_id", "")
        body = {"query": f'mutation {{ podStop(input: {{podId: "{pod_id}"}}) {{ id desiredStatus }} }}'}
        r = requests.post("https://api.runpod.io/graphql", headers=headers, json=body, timeout=15)
        return r.json()
    
    elif action == "start_pod":
        pod_id = params.get("pod_id", "")
        body = {"query": f'mutation {{ podResume(input: {{podId: "{pod_id}"}}) {{ id desiredStatus }} }}'}
        r = requests.post("https://api.runpod.io/graphql", headers=headers, json=body, timeout=15)
        return r.json()
    
    return {"error": f"Unknown action: {action}"}

# 3. HuggingFace Plugin
@app.post("/huggingface")
async def huggingface_plugin(req: PluginRequest):
    action = req.action
    params = req.params
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    if action == "list_models":
        user = params.get("user", "miesdevries")
        r = requests.get(f"https://huggingface.co/api/models?author={user}", timeout=15)
        if r.status_code == 200:
            models = [{"id": m["id"], "downloads": m.get("downloads",0)} for m in r.json()]
            return {"models": models, "count": len(models)}
        return {"error": r.text[:200]}
    
    elif action == "list_files":
        repo = params.get("repo", "miesdevries/stay4s-1b")
        r = requests.get(f"https://huggingface.co/api/models/{repo}", timeout=15)
        if r.status_code == 200:
            data = r.json()
            files = [{"name": k, "size": v.get("size",0)} for k,v in data.get("siblings",{}).items()] if isinstance(data.get("siblings"), dict) else [{"name": s.get("rfilename","")} for s in data.get("siblings",[])]
            return {"files": files}
        return {"error": r.text[:200]}
    
    elif action == "download_url":
        repo = params.get("repo", "miesdevries/stay4s-1b")
        filename = params.get("filename", "")
        return {"url": f"https://huggingface.co/{repo}/resolve/main/{filename}"}
    
    return {"error": f"Unknown action: {action}"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "plugins": ["github", "runpod", "huggingface"],
        "github_configured": bool(GITHUB_TOKEN),
        "runpod_configured": bool(RUNPOD_KEY),
        "hf_configured": bool(HF_TOKEN)
    }

@app.get("/")
async def root():
    return {
        "service": "Stay4S Nexus Plugins v2",
        "plugins": ["github", "runpod", "huggingface"],
        "endpoints": ["/github", "/runpod", "/huggingface", "/health"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8095)
