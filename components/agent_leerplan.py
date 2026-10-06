#!/usr/bin/env python3
"""Zelfgroeidend agent-leertakenpakket generator.

Leest de agent-data (rollen, records) + eval-resultaten, en bouwt een
levend takenpakket dat automatisch:
  1. De agent-suite bijhoudt (getraind/bezig/gepland, scores)
  2. Nieuwe leertaken afleidt uit eval-zwaktes
  3. Meegroeit met elke nieuwe training

Output: AGENT_LEERPLAN.md (in 00_CENTRAAL + AI-GEDEELD)
Gebruik: python agent_leerplan.py
"""
import datetime
import json
import os

HOME = r"C:\Users\Gebruiker"
CENTRAAL = os.path.join(HOME, "stay4os-docs", "00_CENTRAAL")
AI_GEDEELD = os.path.join(HOME, "AI-GEDEELD")
OUT = os.path.join(CENTRAAL, "AGENT_LEERPLAN.md")

# De agent-suite (handmatig bijgehouden, wordt uitgebreid)
AGENTS = [
    {
        "rol": "domein",
        "data": "agent_domein_v2.jsonl",
        "records": 9080,
        "status": "KLAAR",
        "score": 63,
        "sterk": ["algemeen 90%", "rekenen 90%"],
        "zwak": ["instructie 17%", "taal 28%"],
        "model": "/workspace/runs/domein-v2-agent-lora-20260925/domein-v2-agent-merged-fp16",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260925-domeinv2/domein-v2-agent-q8.gguf",
        "opmerking": "V2 met 9080 records — beste Stay4S-domein-kennis",
    },
    {
        "rol": "domein-v1",
        "data": "agent_domein.jsonl",
        "records": 122,
        "status": "ARCHIEF",
        "score": 65,
        "sterk": ["algemeen 90%", "rekenen 90%"],
        "zwak": ["instructie 17%", "taal 39%"],
        "model": "vervangen door v2",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260924-domein/domein-agent-q8.gguf",
        "opmerking": "v1 gearchiveerd — v2 heeft meer records",
    },
    {
        "rol": "summarizer",
        "data": "agent_summarizer.jsonl",
        "records": 7418,
        "status": "KLAAR",
        "score": 64,
        "sterk": ["algemeen 90%", "rekenen 90%"],
        "zwak": ["instructie 17%", "taal 28%"],
        "model": "/workspace/runs/summarizer-agent-lora-20260924/summarizer-agent-merged-fp16",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260924-summarizer/summarizer-agent-q8.gguf",
        "opmerking": "2e beste — grootste dataset",
    },
    {
        "rol": "researcher",
        "data": "agent_researcher.jsonl",
        "records": 7418,
        "status": "KLAAR",
        "score": 63,
        "sterk": ["rekenen 90%", "algemeen 70%"],
        "zwak": ["instructie 17%", "taal 50%"],
        "model": "/workspace/runs/researcher-agent-lora-20260924/researcher-agent-merged-fp16",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260924-researcher/researcher-agent-q8.gguf",
        "opmerking": "Onderzoek + taal",
    },
    {
        "rol": "coder",
        "data": "agent_coder.jsonl",
        "records": 2770,
        "status": "KLAAR",
        "score": 61,
        "sterk": ["rekenen 90%", "algemeen 70%"],
        "zwak": ["instructie 17%", "taal 39%"],
        "model": "/workspace/runs/coder-agent-lora-20260923/coder-agent-merged-fp16",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260923-coder/coder-agent-q8.gguf",
        "opmerking": "Code-expert",
    },
    {
        "rol": "reken",
        "data": "agent_reken.jsonl",
        "records": 3711,
        "status": "KLAAR",
        "score": 58,
        "sterk": ["algemeen 90%", "rekenen 70%"],
        "zwak": ["instructie 17%", "taal 39%"],
        "model": "/workspace/runs/reken-agent-lora-20260923/reken-agent-merged-fp16",
        "gguf": "gs://stayd/staylm2/qwen3-4b-lora-20260923-reken/reken-agent-q8.gguf",
        "opmerking": "Reken-expert",
    },
]

# Referentie-scores (uit eigen-eval)
REFERENTIES = {
    "stay4s-lora": 57,
    "cyc7-sft": 32,
    "cyc6-sft": 2,
}

# Leerregels: zwaktes -> concrete taken
LEERREGELS = {
    "instructie": "Meer instructie-paren genereren (volg-opdrachten, stapsgewijze taken)",
    "taal": "Taal-paren uitbreiden (grammatica, herformulering, schrijfstijlen)",
    "code": "Meer code-voorbeelden toevoegen (complexere algoritmes, debugging)",
    "rekenen": "Meer reken-paren (breuken, procenten, meerstaps-berekeningen)",
}


def main():
    now = datetime.datetime.now().strftime("%d sep %Y %H:%M")

    lines = []
    lines.append("# 🤖 AGENT-LEERPLAN — zelfgroeidend takenpakket")
    lines.append(f"## {now} — automatisch gegenereerd, groeit met elke training")
    lines.append("")
    lines.append("> Doel: een suite van gespecialiseerde Stay4S-agents (LoRA op Qwen3-4B).")
    lines.append("> Elk model = 1 expertrol. Dit plan groeit mee: nieuwe data → nieuwe taken.")
    lines.append("")
    lines.append("## 🏆 Ranglijst (eigen-eval, 30 items)")
    lines.append("")
    lines.append("| Agent | Score | Status |")
    lines.append("|---|---|---|")

    # sorteer op score
    ranked = sorted([a for a in AGENTS if a["score"] is not None], key=lambda x: -x["score"])
    for a in ranked:
        lines.append(f"| **{a['rol']}** | **{a['score']}%** | {a['status']} |")
    for a in AGENTS:
        if a["score"] is None:
            lines.append(f"| {a['rol']} | — | {a['status']} |")
    for name, score in REFERENTIES.items():
        lines.append(f"| {name} (ref) | {score}% | referentie |")

    lines.append("")
    lines.append("## 📋 Agent-suite (volledige staat)")
    lines.append("")
    lines.append("| Rol | Records | Status | Sterk | Zwak | Opmerking |")
    lines.append("|---|---|---|---|---|---|")
    for a in AGENTS:
        sterk = ", ".join(a["sterk"]) if a["sterk"] else "—"
        zwak = ", ".join(a["zwak"]) if a["zwak"] else "—"
        lines.append(f"| {a['rol']} | {a['records']} | {a['status']} | {sterk} | {zwak} | {a['opmerking']} |")

    lines.append("")
    lines.append("## 🎯 AUTO-GENERAALDE LEERTAKEN (uit eval-zwaktes)")
    lines.append("")
    lines.append("Deze taken worden afgeleid uit de gemeten zwaktes. Elke KLAAR-agent levert nieuwe taken op.")
    lines.append("")
    zwaktes = set()
    for a in AGENTS:
        if a["status"] == "KLAAR":
            for w in a["zwak"]:
                cat = w.split()[0]
                zwaktes.add(cat)
    for cat in sorted(zwaktes):
        if cat in LEERREGELS:
            lines.append(f"- **[leer-{cat}]** {LEERREGELS[cat]}")
    if not zwaktes:
        lines.append("- Nog geen zwaktes gemeten (wacht op eerste evals).")

    lines.append("")
    lines.append("## 🔄 VOLGENDE TRAININGEN (autonome volgorde)")
    lines.append("")
    lines.append("| # | Agent | Data | Records | Wanneer |")
    lines.append("|---|---|---|---|---|")
    volgorde = []
    for a in AGENTS:
        if a["status"] in ("TRAINT", "GEPLAND", "WACHT-DATA"):
            volgorde.append((a["rol"], a["data"], a["records"], "nu" if a["status"] == "TRAINT" else "gepland"))
    if volgorde:
        for n, (rol, data, rec, w) in enumerate(volgorde, 1):
            lines.append(f"| {n} | {rol} | {data} | {rec} | {w} |")
    else:
        lines.append("| — | **Alle 5 agents KLAAR** | — | — | 🎉 suite compleet — volgende: datarefresh of nieuwe rollen |")
    lines.append("")
    lines.append("## 💡 ZELFGROEI-MECHANISME")
    lines.append("")
    lines.append("1. **Training klaar** → eval op 30 items → score + zwaktes vastgelegd")
    lines.append("2. **Zwaktes** → nieuwe leertaken (zie boven) → data-uitbreiding")
    lines.append("3. **Nieuwe data** (chatlogs, werklogs, Q&A) → nieuwe rollen of datarefresh")
    lines.append("4. **Dashboard** toont de suite live (Modellen-tab)")
    lines.append("5. **Elke Nieuwe Agent** voegt een rij toe aan dit plan + ranglijst")
    lines.append("")
    lines.append("## 📁 Data-posities")
    lines.append("")
    lines.append("- Agent-data: `/workspace/staylm2_data/agent_*.jsonl` (volume)")
    lines.append("- Runs: `/workspace/runs/*-agent-lora-*`")
    lines.append("- Evals: `/workspace/eigen-eval/eval_*-agent*.jsonl`")
    lines.append("- GGUF (GCS): `gs://stayd/staylm2/qwen3-4b-lora-*`")
    lines.append("- Pi 5 (live): Ollama-modellen + agent-server :8090")
    lines.append("")
    lines.append("---")
    lines.append("*Gegenereerd door agent_leerplan.py — herdraaien na elke training om het plan te laten groeien.*")

    content = "\n".join(lines)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(content)
    os.makedirs(AI_GEDEELD, exist_ok=True)
    with open(os.path.join(AI_GEDEELD, "AGENT_LEERPLAN.md"), "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"AGENT_LEERPLAN geschreven: {len(AGENTS)} agents, {OUT}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
