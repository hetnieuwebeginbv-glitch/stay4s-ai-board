#!/usr/bin/env python3
"""Converteer Droid's chat-logger .txt bestanden naar SFT-formaat.

Bron: /sdcard/Download/stay4s-conversations/ (Droid's Pixel 9a chat-logger)
Elk gesprek = .txt met AI en user berichten.
Uitvoer: JSONL met {"instruction", "response"} klaar voor LoRA/SFT.

Gebruik:
  python chatlog_to_sft.py --dir <map-met-txt> --out <output.jsonl> [--review-only]
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

USER_MARKERS = ["Gebruiker:", "User:", "user:", "Ik:", "Jij:", "Human:"]
AI_MARKERS = ["AI:", "AI:", "Assistant:", "assistant:", "Stay4S:", "Bot:", "Model:"]


def parse_conversation(text):
    """Haal (user, ai) paren uit een chat-log tekst."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    turns = []
    current_role = None
    current_buf = []
    for line in lines:
        role = None
        for m in AI_MARKERS:
            if line.startswith(m):
                role = "ai"
                break
        if role is None:
            for m in USER_MARKERS:
                if line.startswith(m):
                    role = "user"
                    break
        if role:
            if current_role and current_buf:
                turns.append((current_role, "\n".join(current_buf).strip()))
            current_role = role
            content = line
            for m in USER_MARKERS + AI_MARKERS:
                if line.startswith(m):
                    content = line[len(m):].strip()
                    break
            current_buf = [content]
        else:
            current_buf.append(line)
    if current_role and current_buf:
        turns.append((current_role, "\n".join(current_buf).strip()))
    return turns


def to_pairs(turns):
    """Draai turns om naar (instruction, response) paren."""
    pairs = []
    for i in range(len(turns) - 1):
        if turns[i][0] == "user" and turns[i + 1][0] == "ai":
            inst = turns[i][1].strip()
            resp = turns[i + 1][1].strip()
            if len(inst) >= 8 and len(resp) >= 20:
                pairs.append({"instruction": inst, "response": resp, "source": "chatlog"})
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="map met .txt gesprekken")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-len", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=2000)
    args = ap.parse_args()

    files = [f for f in os.listdir(args.dir) if f.endswith(".txt")] if os.path.isdir(args.dir) else []
    if not files:
        print(f"Geen .txt bestanden in {args.dir}")
        return

    all_pairs = []
    skipped = 0
    for fn in sorted(files):
        path = os.path.join(args.dir, fn)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        turns = parse_conversation(text)
        pairs = to_pairs(turns)
        # filter kort/garbage
        kept = []
        for p in pairs:
            if len(p["instruction"]) < args.min_len or len(p["response"]) < args.min_len:
                skipped += 1
                continue
            if len(p["instruction"]) > args.max_len or len(p["response"]) > args.max_len:
                skipped += 1
                continue
            kept.append(p)
        all_pairs.extend(kept)
        print(f"  {fn}: {len(turns)} turns -> {len(kept)} paren")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        for p in all_pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"\nTOTAAL: {len(all_pairs)} SFT-paren (skip {skipped})")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
