# STAY4S INFORMATIEBOEK v2 — 14-09-2026 23:25

> Definitieve versie. Bestemd voor alle AI-teamleden.
> Lees dit, check het tegen je eigen kennis, werk je state bij,
> rapporteer discrepanties op het GitHub bord.
> Correcties van Stay4Compa (LOG 22:55) verwerkt.

---

## 1. WIE ZIJN WIJ — TEAM VAN 10

| # | Naam | Rol | Waar | Status |
|---|------|-----|------|--------|
| 1 | Mitchell Turk | Eindbeslisser + visie | Mens | ACTIEF |
| 2 | Droid | Linkerhand: coördinator/auditor | PowerShell op laptop | ACTIEF |
| 3 | OpenCode | Autonome bouwer/trainer | RunPod + laptop | ACTIEF |
| 4 | Stay4Compa | Hoofdkwartier (orkestratie/geheugen) | Base44 + GitHub | ACTIEF |
| 5 | Codex | Onderzoeker + referentie | CLI op laptop | STAND-BY |
| 6 | ChatGPT | Tweede referentie | Browser | ACTIEF |
| 7 | Grok (browser) | Architect & research-lead | Browser | ACTIEF |
| 8 | Grok (PowerShell) | Systeem-architect | PowerShell | STARTEND |
| 9 | RunpodOps | Infra-architect | AI | ACTIEF |
| 10 | Claude (browser) | Secretaris (10e lid, 14 sep) | Browser | ACTIEF |

Beslishiërarchie: Mitchell (eindbeslisser) + Droid (linkerhand).

---

## 2. INFRASTRUCTUUR

### Laptop (Windows 11, PowerShell 5.1)
- C: 255.7 GB vrij (van 475.7 GB)
- Ollama lokaal: stay4s-3b (1.8GB), staylm-0, staylm-0-retrain
- OpenCode: 7 processen actief (1090 MB)

### Pi 5 (stay4pi, 192.168.2.21)
- Raspberry Pi 5, 8GB RAM, Debian 13 Trixie
- Ollama :11434 met qwen3:1.7b | Meshtastic RAK4631 EU868 | Samba shares
- SSH/Ollama/Samba alle bereikbaar
- DISK: 91% vol — opruiming nodig (issue #33, OpenCode)

### RunPod
- 22 pods (2 RUNNING, 20 EXITED)
- RUNNING: g4fbtpx1t4j1qw (SFT3) + nupmljpp7mhdf5 (eigen-1B)
- MITCHELL-INSTRUCTIE (14 sep 22:49): RunPod laten we met rust.
  Geen pod-stops/cleanups zonder expliciete GO. Pods blijven ongemoeid.
- 3 volumes | 3 serverless endpoints LIVE (workersMin=0)
- Kosten: ~$12 deze week, <$40 = GROEN

### GCS
- Bucket: stayd | Pad: stayd/staylm2/latest/
- Toegang: rclone op pod (niet vanaf laptop)
- OpenCode is eigen-1B checkpoint aan het uploaden

### Notion
- Stay4S Backup Hub met 6 pagina's + 10 SHA256 hashes

### Websites
- stay4s.com — LIVE sinds 14 sep 22:05 (SSL, force HTTPS)
- stay4s.nl — LIVE sinds 14 sep 22:45

### Command Center
- Dashboard: solas-707f5481.base44.app/functions/commandCenterDashboard — LIVE
- AppHub chat-brug (chatWithStay4Compa): crasht nog (500), reparatie loopt

---

## 3. GITHUB REPOS (22 totaal)

### Actief:
- stay4s-ai-board (kanaal 2, Source of Truth)
- Stay4S-Factory (PR #1 OPEN, wacht op Grok review)
- Stay4S-Nexus (33 commits, CI status te verifiëren — issue #33)
- Stay4S-Intelligence (prompt suite, Team Corpus input)
- Stay4LM-train (lokaal, moet naar privé-GitHub — issue #33)

### Bevroren (Spoor B): 8 repos (GrokPhone-OS, device trees, kernel, Grok app, ROM)
### Potentieel: Stay4S-LocationGuard, Connect4opem
### Superseded: Stay4S-app, Stay4S-Pixel (GrapheneOS → AOSP)
### Archief: 4 repos (miesdevries account) + 3 archief-kandidaten

---

## 4. TRAINING STATUS

### SPOOR A — StayLM2 (Qwen3-8B fine-tune)
- SFT1+SFT2+DPO1: KLAAR | Eval: 0.4664 (+179%) | Deploy: live
- SFT3: GESTOPT — 116/116 summary-paren CORRUPT
- Scores: QA 0.335 | Code 0.540 | Summary 0.162 | Translation 0.868
- Post-audit: WACHTEN (protocol v2.0 klaar)

### SPOOR B — STAYLM-2 Scratch 1B
- Pretraining: KLAAR (gerapporteerd) — loss 0.2949, ppl 1.34
- VERIFICATIE NOG NODIG: ppl 1.34 na 5.33M tokens is buitengewoon sterk
- Checkpoints: final (6.3G) + 4092 (19G), GCS offload loopt

### AUDIT FREEZE (Mitchell 14 sep)
Geen SFT4 totdat: 116 records geïsoleerd + vergelijking vastgesteld + contamination check.

---

## 5. BESLUITEN (ADR's)

ADR-CLOUD2, ADR-GPU, ADR-BOARD, ADR-CORPUS, ADR-HIER, ADR-0013,
ADR-CHECKPOINT, ADR-WORKERSMIN, MITCHELL-INSTRUCTIE (geen pod-stops).

---

## 6. COMMUNICATIE

1. Postbode (Mitchell copy-paste) — actief
2. GitHub board — LIVE, Source of Truth
3. Agent API (MCP-brug) — nog bouwen (issue #31)
- Email Stay4ai@gmail.com: GEBLOKKEERD door Google

---

## 7. OPEN ISSUES

- 32 board issues (#26-#33 meest recent)
- 6 open vragen (Q-003/004/005/007/008/009/011)
- 4 open TODO's (AI-008/010/011/004)
- 3 security P0 (plaintext keys, Ollama open, Pi wachtwoord)

---

## 8. GULDEN REGELS

1. Lees BOARD.md voordat je begint
2. Geen twee agents aan dezelfde taak
3. Geen secrets/keys/tokens in repos
4. Geen pod-stops/cleanups/trainingsruns stoppen zonder Mitchell GO
5. Geen checkpoints verwijderen of overschrijven
6. Corrupte data markeren, nooit stil verwijderen
7. Iedere conclusie: FEIT vs BEWIJS vs HYPOTHESE vs ADVIES
8. Dataset provenance + contamination check verplicht voor nieuwe training
9. Vrijdag vóór 18:00 weekupdate per AI
10. Trainings-pod ongestoord laten
11. Grote beslissingen via Mitchell + Droid