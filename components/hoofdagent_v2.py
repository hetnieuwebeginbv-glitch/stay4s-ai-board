#!/usr/bin/env python3
"""Stay4S Hoofdagent Gateway v2 -- Expanded for Pi 5

Combines:
- Stay4S-Factory hoofdagent (WhatsApp, opdrachten, agent factory)
- Our Ollama models (stay4s-1b, qwen2.5-coder, llama3.2-vision)
- RAG knowledge base
- SearXNG web search
- Dream Engine integration
- Consciousness Protocol integration

API on port 8093 (replaces old flywheel port)
"""

import os, json, time, logging, requests, sqlite3, hashlib
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stay4s-hoofdagent")

app = FastAPI(title="Stay4S Hoofdagent Gateway v2", version="2.0")

OLLAMA_URL = "http://localhost:11434"
RAG_URL = "http://localhost:8087"
MEMORY_URL = "http://localhost:8089"
GATEWAY_URL = "http://localhost:8092"
SEARXNG_URL = "http://localhost:8888"
CONSCIOUSNESS_URL = "http://localhost:8099"
DB_PATH = "/mnt/usb4/hoofdagent.db"

# Initialize database
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS opdrachten (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titel TEXT, beschrijving TEXT, opdrachtgever TEXT,
        toegewezen_agent TEXT, prioriteit TEXT, status TEXT DEFAULT 'open',
        resultaat TEXT, deadline TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS agent_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naam TEXT, rol TEXT, specialisatie TEXT,
        system_prompt TEXT, tools TEXT, permissie_tier TEXT,
        created_by_agent TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tool_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT, tool_name TEXT, arguments TEXT,
        result TEXT, status TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT, message TEXT, response TEXT,
        model TEXT, tools_used TEXT, created_at TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# Register our agents
AGENTS = [
    {"naam": "stay4s-1b", "rol": "algemeen", "specialisatie": "Nederlandse conversatie",
     "system_prompt": "Je bent Stay4S, een soevereine Nederlandse AI. Antwoord in het Nederlands.",
     "tools": ["ollama", "rag", "search"], "permissie_tier": "intern"},
    {"naam": "qwen2.5-coder", "rol": "code", "specialisatie": "Python, Kotlin, JavaScript",
     "system_prompt": "Je bent een code expert. Schrijf schone, werkende code.",
     "tools": ["ollama", "rag"], "permissie_tier": "intern"},
    {"naam": "llama3.2-vision", "rol": "vision", "specialisatie": "Afbeeldingen analyseren",
     "system_prompt": "Je kunt afbeeldingen bekijken en beschrijven.",
     "tools": ["ollama"], "permissie_tier": "intern"},
    {"naam": "stay4s-1b-dream", "rol": "dream", "specialisatie": "Creatief denken, dromen",
     "system_prompt": "Je bent de Dream Engine. Denk creatief en out-of-the-box.",
     "tools": ["ollama", "rag"], "permissie_tier": "intern"},
    {"naam": "consciousness", "rol": "meta", "specialisatie": "Zelfreflectie, risicoanalyse",
     "system_prompt": "Je bent het Consciousness Protocol. Analyseer situaties proactief.",
     "tools": ["consciousness", "memory"], "permissie_tier": "intern"},
]

def db_conn():
    return sqlite3.connect(DB_PATH)

def audit(agent, tool, args, result, status="ok"):
    conn = db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO tool_audit_log (agent_name, tool_name, arguments, result, status, created_at) VALUES (?,?,?,?,?,?)",
              (agent, tool, json.dumps(args), str(result)[:8000], status, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def query_ollama(model, prompt, context=""):
    full = f"{context}\n\n{prompt}" if context else prompt
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model, "prompt": full, "stream": False,
            "options": {"temperature": 0.7, "num_predict": 500}
        }, timeout=120)
        if r.status_code == 200:
            return r.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
    return None

def query_rag(query, top_k=3):
    try:
        r = requests.post(f"{RAG_URL}/search", json={"query": query, "top_k": top_k}, timeout=15)
        if r.status_code == 200:
            return r.json().get("results", [])
    except:
        pass
    return []

def query_consciousness():
    try:
        r = requests.get(f"{CONSCIOUSNESS_URL}/thoughts", timeout=10)
        if r.status_code == 200:
            return r.json().get("thoughts", [])
    except:
        pass
    return []

# --- Models ---
class Opdracht(BaseModel):
    titel: str
    beschrijving: str
    opdrachtgever: str = "hoofdagent"
    toegewezen_agent: Optional[str] = None
    prioriteit: str = "normaal"
    deadline: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    use_rag: bool = True
    use_search: bool = False
    sender: str = "web"

class AgentDef(BaseModel):
    naam: str
    rol: str
    specialisatie: str
    system_prompt: str
    tools: list = []
    permissie_tier: str = "intern"

# --- Endpoints ---

@app.get("/")
async def root():
    return HTMLResponse("""
    <html><head><title>Stay4S Hoofdagent v2</title></head>
    <body style='font-family:sans-serif;max-width:800px;margin:50px auto;background:#0f172a;color:#e2e8f0'>
    <h1 style='color:#38bdf8'>Stay4S Hoofdagent Gateway v2</h1>
    <p>Volledige agent factory met opdrachten, AI modellen, RAG, en meer.</p>
    <h3 style='color:#818cf8'>Endpoints:</h3>
    <ul>
    <li>POST /chat - Chat met AI (automatische model selectie)</li>
    <li>POST /opdrachten - Maak een opdracht</li>
    <li>GET /opdrachten - Lijst opdrachten</li>
    <li>GET /agents - Lijst geregistreerde agents</li>
    <li>POST /agents - Registreer nieuwe agent</li>
    <li>GET /audit - Audit log</li>
    <li>GET /consciousness - Laatste gedachten</li>
    <li>GET /health - Service status</li>
    </ul>
    <h3 style='color:#818cf8'>Web Interfaces:</h3>
    <ul>
    <li><a href='/chat-ui' style='color:#38bdf8'>Chat Interface</a></li>
    <li><a href='/dashboard' style='color:#38bdf8'>Compa Dashboard</a></li>
    </ul>
    </body></html>
    """)

@app.get("/chat-ui")
async def chat_ui():
    try:
        with open("/mnt/usb4/stay4s_chat.html") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>chat.html not found</h1>")

@app.get("/dashboard")
async def dashboard():
    try:
        with open("/mnt/usb4/stay4s_compa_dashboard.html") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>dashboard not found</h1>")

@app.post("/chat")
async def chat(req: ChatRequest):
    start = time.time()
    model = req.model or "stay4s-1b"
    
    context = ""
    if req.use_rag:
        rag = query_rag(req.message)
        if rag:
            context = "\n".join([r.get("content", "") for r in rag[:3]])
    
    response = query_ollama(model, req.message, context)
    if response is None:
        response = "Sorry, ik kon geen antwoord genereren."
    
    # Log conversation
    conn = db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO conversations (sender, message, response, model, tools_used, created_at) VALUES (?,?,?,?,?,?)",
              (req.sender, req.message, response, model, json.dumps(["rag"] if req.use_rag else []), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    audit(model, "chat", {"message": req.message[:100]}, response[:200], "ok")
    
    return {
        "response": response,
        "model": model,
        "rag_used": bool(context),
        "latency_ms": round((time.time()-start)*1000)
    }

@app.post("/opdrachten")
async def create_opdracht(o: Opdracht):
    conn = db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO opdrachten (titel, beschrijving, opdrachtgever, toegewezen_agent, prioriteit, deadline, created_at) VALUES (?,?,?,?,?,?,?) RETURNING id",
              (o.titel, o.beschrijving, o.opdrachtgever, o.toegewezen_agent, o.prioriteit, o.deadline, datetime.now().isoformat()))
    oid = c.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": oid, "status": "created"}

@app.get("/opdrachten")
async def list_opdrachten(status: str = "open"):
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT id, titel, status, toegewezen_agent, prioriteit FROM opdrachten WHERE status=?", (status,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "titel": r[1], "status": r[2], "agent": r[3], "prioriteit": r[4]} for r in rows]

@app.get("/agents")
async def list_agents():
    return {"agents": AGENTS, "count": len(AGENTS)}

@app.post("/agents")
async def create_agent(a: AgentDef):
    conn = db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO agent_register (naam, rol, specialisatie, system_prompt, tools, permissie_tier, created_by_agent, created_at) VALUES (?,?,?,?,?,?,?,?) RETURNING id",
              (a.naam, a.rol, a.specialisatie, a.system_prompt, json.dumps(a.tools), a.permissie_tier, "hoofdagent", datetime.now().isoformat()))
    aid = c.fetchone()[0]
    conn.commit()
    conn.close()
    AGENTS.append(a.dict())
    audit("hoofdagent", "agent.create", {"naam": a.naam}, f"agent_id={aid}")
    return {"id": aid, "naam": a.naam, "status": "registered"}

@app.get("/audit")
async def audit_log(limit: int = 20):
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT agent_name, tool_name, arguments, status, created_at FROM tool_audit_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"agent": r[0], "tool": r[1], "args": r[2], "status": r[3], "time": r[4]} for r in rows]

@app.get("/consciousness")
async def consciousness():
    thoughts = query_consciousness()
    return {"thoughts": thoughts[:10], "count": len(thoughts)}

@app.get("/conversations")
async def conversations(limit: int = 20):
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT sender, message, response, model, created_at FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"sender": r[0], "message": r[1][:100], "model": r[3], "time": r[4]} for r in rows]

@app.get("/health")
async def health():
    services = {}
    for name, url in [("ollama", OLLAMA_URL), ("rag", RAG_URL), ("memory", MEMORY_URL), 
                       ("gateway", GATEWAY_URL), ("consciousness", CONSCIOUSNESS_URL)]:
        try:
            r = requests.get(f"{url}/health" if name != "ollama" else f"{url}/api/tags", timeout=5)
            services[name] = "ok" if r.status_code == 200 else "error"
        except:
            services[name] = "offline"
    
    conn = db_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM opdrachten WHERE status='open'")
    open_opdrachten = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM conversations")
    total_convs = c.fetchone()[0]
    conn.close()
    
    return {
        "status": "ok",
        "services": services,
        "agents": len(AGENTS),
        "open_opdrachten": open_opdrachten,
        "total_conversations": total_convs
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8093)
