#!/usr/bin/env python3
"""Convert Droid .factory session JSONL files to SFT training data.

Reads session files from .factory/sessions/ and extracts user/AI conversation pairs.
Output: JSONL with {"instruction", "response"} format for training.
"""
import json, os, glob, sys, re

SESSION_DIR = r"C:\Users\Gebruiker\.factory\sessions\-C-Users-Gebruiker"
OUTPUT = r"C:\Users\Gebruiker\droid_conversations_sft.jsonl"

def extract_text(content):
    """Extract text from message content (can be string or list of dicts)"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    t = item.get("text", "")
                    # Skip system reminders and tool definitions
                    if "<system-reminder>" in t or "Deferred tools:" in t:
                        continue
                    if len(t) > 5:
                        texts.append(t)
        return "\n".join(texts)
    return ""

def process_session(filepath):
    """Extract user/AI pairs from a session file"""
    pairs = []
    user_msg = None
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
            except:
                continue
            
            if entry.get("type") != "message":
                continue
            
            msg = entry.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Skip tool calls, system messages
            if role not in ("user", "assistant"):
                continue
            
            text = extract_text(content)
            if not text or len(text) < 10:
                continue
            
            # Clean up text
            text = re.sub(r'<system-reminder>.*?</system-reminder>', '', text, flags=re.DOTALL)
            text = re.sub(r'<execute>.*?</execute>', '', text, flags=re.DOTALL)
            text = text.strip()
            
            if not text or len(text) < 10:
                continue
            
            if role == "user":
                if user_msg is None:
                    user_msg = text
            elif role == "assistant" and user_msg is not None:
                # We have a pair
                if len(user_msg) >= 10 and len(text) >= 20:
                    pairs.append({
                        "instruction": user_msg[:2000],
                        "response": text[:4000],
                        "source": "droid_session"
                    })
                user_msg = None
    
    return pairs

def main():
    files = glob.glob(os.path.join(SESSION_DIR, "*.jsonl"))
    print(f"Found {len(files)} session files")
    
    all_pairs = []
    for fpath in sorted(files):
        pairs = process_session(fpath)
        if pairs:
            all_pairs.extend(pairs)
            fname = os.path.basename(fpath)
            print(f"  {fname[:20]}...: {len(pairs)} pairs")
    
    # Filter: remove duplicates, too short, or garbage
    seen = set()
    unique = []
    for p in all_pairs:
        h = hash(p["instruction"][:100] + p["response"][:100])
        if h not in seen and len(p["instruction"]) >= 10 and len(p["response"]) >= 20:
            seen.add(h)
            unique.append(p)
    
    print(f"\nTotal: {len(all_pairs)} pairs -> {len(unique)} unique")
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for p in unique:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"Written: {OUTPUT} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
