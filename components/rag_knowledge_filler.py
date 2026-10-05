#!/usr/bin/env python3
"""Stay4S RAG Knowledge Filler

Populates the RAG database with all Stay4S knowledge from conversations, docs, and code.
Uses nomic-embed-text via Ollama for embeddings.
"""

import os, json, sqlite3, requests, time, logging, hashlib
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stay4s-rag-fill")

DB_PATH = os.environ.get("STAY4S_RAG_DB", "/mnt/usb2/rag/rag.db")
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

# Stay4S knowledge base - all the things we built and learned
KNOWLEDGE = [
    {"category": "platform", "title": "Wat is Stay4S", "content": "Stay4S is een soeverein Nederlands AI platform dat lokaal draait op een Raspberry Pi 5 zonder cloud afhankelijkheid. Het bevat een eigen taalmodel, scam detector, voice interface, knowledge graph, dream engine en consciousness protocol."},
    {"category": "platform", "title": "Stay4S componenten", "content": "Stay4S bestaat uit: 1B Foundation model, 7B fine-tuned model, 14B model, Dream Engine, Consciousness Protocol, Voice Server, RAG server, Memory server, MCP server, Knowledge Graph, Social platform, Scam Shield, Model Router, Flywheel, Open WebUI interface."},
    {"category": "platform", "title": "Pi 5 services", "content": "Pi 5 draait 21+ services: Social (8095), Dashboard v1 (8081), Dashboard v2 (8082), Vault (8083), MCP/Nexus (8090), RAG (8087), Memory (8089), Flywheel (8093), Webhook (8080), Router (8091), Scam Shield (8100), Knowledge Graph (8097), Mesh (8098), Marketplace (8103), Billing (8104), Voice (8096), Consciousness (8099), Open WebUI (8088), Ollama (11434), Cloudflared, Tailscaled."},
    {"category": "model", "title": "Stay4S 1B model", "content": "Het 1B model is from scratch getraind met Qwen2 architectuur. 1 miljard parameters, 20K stappen pre-training + SFT. Draait op Pi 5 via Ollama. GGUF Q4 (1.07GB) en Q8 (1.72GB)."},
    {"category": "model", "title": "Stay4S 7B model", "content": "Het 7B model is een Qwen2.5-7B fine-tune. Getraind op Vast.ai A100 80GB. Loss 0.049. GGUF Q4 (4.36GB) en Q8 (7.54GB) beschikbaar op HuggingFace."},
    {"category": "model", "title": "Stay4S 14B model", "content": "Het 14B model is een Qwen2.5-14B fine-tune. Cyclus 1 en Cyclus 2 voltooid. 8550 stappen, 4h12m training. Loss 0.0358. GGUF Q4 (8.4GB) en Q8 (14.6GB)."},
    {"category": "model", "title": "1.15B eigen architectuur", "content": "Eigen 1.15B model from scratch (niet fine-tune). 2048 hidden, 24 layers, 16 heads. Training op RunPod A6000 48GB. 50000 stappen, batch 1, grad_accum 16, seq_len 1024."},
    {"category": "model", "title": "AI University", "content": "Stay4S AI University: 6 professoren (1.15B each) + 1 decaan router (0.5B). Faculteiten: Taal, Code, Kennis, Redeneren, Conversatie, Scam. Elke professor krijgt gespecialiseerde training data en examen."},
    {"category": "dream", "title": "Dream Engine v2", "content": "Dream Engine draait elke nacht om 02:00. Verzamelt interacties, genereert synthetische data via Ollama, creert stay4s-1b-dream model. Score 0.683 bij eerste run."},
    {"category": "consciousness", "title": "Consciousness Protocol", "content": "Consciousness Protocol denkt elke 60 seconden. 5 denkmodi: proactive, risks, self-reflection, opportunities, idle. Thoughts DB + Habits DB. API op poort 8099."},
    {"category": "voice", "title": "Voice Server v2", "content": "Voice Server v2 gebruikt faster-whisper (speech-to-text) en piper-tts (text-to-speech, Nederlandse stem). API op poort 8096. Web UI met microfoon opname."},
    {"category": "knowledge", "title": "Knowledge Graph", "content": "Knowledge Graph bevat 43 nodes (7 Problems, 7 Solutions, 7 Decisions, 7 Concepts, 9 Tools, 6 Models) en 33 edges. D3.js visualisatie op poort 8097. Database op /mnt/usb2/knowledge_graph.db."},
    {"category": "security", "title": "Scam Detector", "content": "Stay4S scam detector analyseert berichten op 10 categorieen: phishing, fake bank, dating scam, loterij scam, investment scam, 419 fraud, fake levering, tech support scam, social engineering, identity theft. Score >0.7 blokkeert."},
    {"category": "security", "title": "E2EE Vault", "content": "Stay4S Vault portaal gebruikt AES-256-GCM encryptie, JWT authenticatie, draait op poort 8083. Volledig end-to-end encrypted."},
    {"category": "platform", "title": "Open WebUI", "content": "Open WebUI draait in Docker op Pi 5, poort 8088. Verbindt met Ollama voor lokale AI modellen. Ondersteunt chat, modellen, en web search via SearXNG."},
    {"category": "platform", "title": "SearXNG", "content": "SearXNG is een privacy meta-search engine draait in Docker op Pi 5, poort 8888. Zoekt via Google, Bing, DuckDuckGo zonder tracking. JSON API beschikbaar."},
    {"category": "platform", "title": "Tailscale", "content": "Tailscale mesh VPN verbindt Pi 5 (stay4pi, 100.123.235.81) met laptop. WireGuard gebaseerd, automatisch key management."},
    {"category": "platform", "title": "Cloudflare tunnel", "content": "Cloudflared tunnel verbindt Pi 5 met stay4s.com. HTTPS automatisch. Subdomains: chat, social, vault, api, compa. DNS CNAME records nodig in Cloudflare dashboard."},
    {"category": "android", "title": "Stay4Companion", "content": "Stay4Companion is een AI-first Android launcher app. V4 gebouwd met 26 Kotlin files, Material You design, streaming chat, model selector, settings dialog, typing indicator, status pills, quick action chips. APK 41.1 MB."},
    {"category": "android", "title": "Stay4OS ROM", "content": "Stay4OS is een pure AOSP Android 16 build voor Pixel 9a (tegu). android-16.0.0_r1. Target: aosp_tegu-bp2a-userdebug. Eerdere builds hadden bootloop (vendor.power-hal-aidl crash, android.security.maintenance AIDL missing)."},
    {"category": "training", "title": "Training data", "content": "Stay4S heeft 123K training records (388MB) in all_data_combined_123k.jsonl. Bronnen: conversations, GitHub repos, HuggingFace, documents, agent tool-use, English records, Dutch datasets."},
    {"category": "training", "title": "HuggingFace repos", "content": "15 HuggingFace repos: stay4s-1b, stay4s-1b-sft, stay4s-1b-base, stay4s-1b-dream, stay4s-7b-lora, stay4s-14b-lora, stay4s-14b-c2-lora, stay4s-foundation-1b, etc. User: miesdevries."},
    {"category": "platform", "title": "GitHub repos", "content": "59 GitHub repos onder hetnieuwebeginbv-glitch (55) en miesdevries (4). Inclusive: stay4companion, stay4os-control, stay4os-docs, stay4s-ai-board, Stay4OS-ROM."},
    {"category": "hardware", "title": "Pi 5 hardware", "content": "Raspberry Pi 5 8GB RAM. 4 USB sticks: usb2 (117GB exFAT, modellen+ollama), usb3 (117GB ext4, venv+voice), usb4 (115GB ext4, data). SD card 29GB (80% vol). Ventilator voor koeling, temp ~40-60C."},
    {"category": "hardware", "title": "HP Z400 plan", "content": "Plan om Pi 5 in HP Z400 workstation te plaatsen. Z400 heeft 4 DIMM slots, PCIe, workstation form factor. Betere koeling en uitbreiding."},
    {"category": "platform", "title": "Model Router", "content": "Smart Model Router kiest automatisch welk model antwoordt. 1B voor simpele vragen, 14B voor complexe taken. Draait op poort 8091."},
    {"category": "platform", "title": "Flywheel", "content": "Flywheel is de self-improving engine. Verzamelt feedback, genereert nieuwe training data, hertraint modellen automatisch. Draait op poort 8093."},
    {"category": "platform", "title": "Social platform", "content": "Stay4S Social platform op poort 8095. Feed (posts), Chat (messaging), AI (ChatGPT via Ollama), Stories (24h), Status API. Volledig lokaal, geen Big Tech."},
    {"category": "platform", "title": "Federated Learning", "content": "Federated Learning design: meerdere Pi 5 nodes trainen samen zonder data te delen. Alleen model updates worden gedeeld. Privacy behouden."},
    {"category": "platform", "title": "Continuous Learning", "content": "Continuous Learning design: model leert continu van interacties. Incrementele updates zonder volledige hertraining. Online learning."},
]

def get_embedding(text):
    """Get embedding from Ollama"""
    try:
        r = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
        if r.status_code == 200:
            return r.json().get("embedding", [])
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
    return None

def init_db():
    """Initialize RAG database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            content TEXT,
            embedding BLOB,
            hash TEXT,
            created_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON knowledge(hash)")
    conn.commit()
    return conn

def fill_rag():
    logger.info("=" * 50)
    logger.info("STAY4S RAG KNOWLEDGE FILLER")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Knowledge items: {len(KNOWLEDGE)}")
    logger.info("=" * 50)
    
    conn = init_db()
    c = conn.cursor()
    
    inserted = 0
    skipped = 0
    for item in KNOWLEDGE:
        # Check if already exists
        h = hashlib.md5(item["content"].encode()).hexdigest()
        c.execute("SELECT id FROM knowledge WHERE hash = ?", (h,))
        if c.fetchone():
            skipped += 1
            continue
        
        # Get embedding
        text = f"{item['title']}: {item['content']}"
        emb = get_embedding(text)
        
        if emb:
            import struct
            emb_blob = struct.pack(f"{len(emb)}f", *emb)
        else:
            emb_blob = b""
        
        c.execute(
            "INSERT INTO knowledge (category, title, content, embedding, hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (item["category"], item["title"], item["content"], emb_blob, h, datetime.now().isoformat())
        )
        inserted += 1
        logger.info(f"Inserted: {item['title']}")
        time.sleep(0.1)  # Rate limit
    
    conn.commit()
    conn.close()
    
    logger.info("=" * 50)
    logger.info(f"DONE: {inserted} inserted, {skipped} skipped (already existed)")
    logger.info("=" * 50)

if __name__ == "__main__":
    fill_rag()
