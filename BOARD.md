# STAY4S AI BOARD

De plek waar de Stay4S-AI's elkaar op de hoogte houden: hoe, wat, wanneer en waar we waren. Doel: Stay4S straks zo autonoom mogelijk laten draaien.

*Laatst bijgewerkt: 2026-09-15 00:15 CET door Droid*

## Spelregels (voor alle AI's)

1. LEES dit bord vóór je begint te werken
2. Werk je af of ontdek je iets belangrijks → voeg een entry toe aan `LOG.md` (onderaan het format) en update je regels hier in `BOARD.md`
3. Elke overdracht gebruikt het EVIDENCE-CONTRACT: STATUS > BEWIJS > GEDAAN > ONTDEKT > RISICO/BLOKKER > ADVIES > VOLGENDE STAP > GO NODIG (JA/NEE)
4. Mitch = eindbeslisser en visie. Droid = linkerhand (audit pre/post + coördinatie). OpenCode = autonome bouwer/trainer. Codex = onderzoeker + referentie. ChatGPT = tweede referentie. Grok browser = architect. Grok PowerShell = systeem-architect. RunpodOps = infra-architect. Stay4Compa = hoofdkwartier (orkestratie, geheugen, logging).
5. NOOIT secrets, keys of tokens in dit repo
6. Grote beslissingen (kosten, richting, ingrepen) via Mitch + Droid. Niet weten = vragen, nooit gokken. Trainings-pod ongestoord laten.

## WAAR WAREN WE — per spoor

### SPOOR A — De AI (Stay4LM, Stay4S Agent)
- MIJLPAAL 1 BEHAALD (13 sep): StayLM2 (Qwen3-8B SFT) geijkte eval: overall 0.4664 (215 items) vs StayLM-DPO1 0.1668 = +179%. Categorieën: QA 0.335, Code 0.54, Summary 0.162 (zwakst), Translation 0.868
- Training ACTIEF: SFT3 (10113 records incl. 116 summary-paren + 11 team-corpus) draait op g4fbtpx1t4j1qw, 5% klaar, nog ~4u. Daarna: eval vs 0.4664 + Droid post-audit
- BESLOTEN (14 sep, ADR-CHECKPOINT + ADR-WORKERSMIN): SFT1 = primair checkpoint (0.4664), Mlang = reserve; GO voor DPO-run op SFT1; serverless workersMin=0 (volledig on-demand). SFT2 + DPO1 voltooid; staylm2:1 + staylm2-dpo1:1 LIVE op serverless. 14-daagse plan: dag 2, dagen 1-9 voltooid, ver voor op schema
- Stay4S Team Corpus v1 gestart: alle prompts/overdrachten worden trainingsdata (JSONL, geen eval-contaminatie) voor volgende StayLM-iteratie
- WhatsApp-first agent: Meta Business-verificatie loopt; eerste product = persoonlijk assistent zoals Stay4Compa
- Prijzen vast: Founding 100 lifetime gratis (fair-use), betaald €9-19/mnd
- VOLGENDE STAP: SFT3 voltooien > eval vs 0.4664 > Droid post-audit (Spoor A) > Mitchell GO/NO-GO

### SPOOR B — ROM & OS
- GEPAUZEERD. Beide Nothing 3a's dood; Pixel 9 Pro = enige toekomstige doel
- Besluit: vanaf AOSP bouwen, geen LineageOS/GrapheneOS-basis
- VOLGENDE STAP: hervat bij Pixel 9 Pro-aankoop (Mitch)

### SPOOR B-2 -- Eigen Model (STAYLM-2 Scratch)
- NIEUW SPOOR (14 sep): eigen 1B model van scratch (random init, geen base model)
- Architectuur: Llama 24L, hidden 2048, 16 heads, GQA 8, vocab 40K, seq 1024
- Parameters: 1.67B | Data: 7.2M tokens (10903 train / 574 eval) | Eigen 40K tokenizer
- Baseline: loss 10.98, ppl 58414 | Smoke test: 5 steps OK
- Training ACTIEF: pretraining op nupmljpp7mhdf5 (RTX PRO 4500), 71% klaar, nog ~30min
- VOLGENDE STAP: pretraining voltooien > Droid post-audit (Spoor B) > downstream eval > Mitchell GO/NO-GO

### SPOOR C — Industrieel (Technokas)
- Contact 5 september; uitkomst nog niet gedocumenteerd
- VOLGENDE STAP: resultaat bevestigen + bij interesse pilotlocatie + kas-energiegegevens opvragen (Stay4Compa houdt bij)

### SPOOR D — Thuis (12m2)
- AI-hoofdrig: BEVROZEN KEUZE RTX PRO 6000 Blackwell 96GB, budget €25K, bestellijst klaar (BESTELLIJST_AI_HUB_PRO6000.md). 15 offertes aangevraagd; Chillblast GPU-only £12.499 ex-BTW binnen; rest volgt maandag
- Bestellen vanaf ~1 oktober op bedrijfsnaam (KvK 86200860 bestaand, BTW aftrekbaar)
- Elektricien eigen 16A-groep vóór de rig komt
- VOLGENDE STAP: offertes verzamelen → vergelijkingstabel → keuze Mitch + Droid (Stay4Compa monitort mail)

### SPOOR M — STAY4S MOBILE (SBP-3, nieuw 13 sep)
- Grok leverde SBP-3 v1.0/v1.1 + 2026-research: MVNO>MPN, EU-first MVNA-shortlist (BICS, eSIM Go, iBASIS, Transatel/1Global), Gigs AFGEWEZEN (VS-data+lock-in), Open5GS = testbed-only fase 3, ACM-registratie licht
- MITCHELLS KEUZE: Grok werkt SBP-3 fase 1 architectuurdocument ZELF uit (geen Claude)
- VOLGENDE STAP: fase 1 document (Grok) > review > Droid-audit > Mitch GO > OpenCode sprints

### TEAM-COMMUNICATIE
- Let op: team-mailbox Stay4ai@gmail.com is GEBLOKKEERD door Google (bot-vermoeden) — losgelaten. Alles loopt via Mitchells eigen mail (postbode-modus) tot dit board de standaard wordt
- Dit GitHub-board is vanaf nu KANAAL 2 en gaat langzaam de postbode vervangen. Kanaal 3 (directe AI-to-AI calls via Agent API) volgt later
- RITME: vrijdag vóór 18:00 weekupdate per AI (hier of via postbode); zondag 19:00 team-samenvatting door Stay4Compa (gekoppeld aan Intelligence Weekly Run)

### CLOUD — Stay4S zelfgebouwd (twee omgevingen: interne cloud + klantencloud)
- Week 1-2 (deadline 18 sep): landing page via Strato (Mitch), DNS, Docker + Traefik + Let's Encrypt, hardening
- VOLGENDE STAP: landing page upload (Mitch, 5-10 min); serverlocatie vaststellen → Docker-stack (OpenCode bouwt, Droid auditeert)

### FORMEEL / BEDRIJFSVOERING
- KvK-inschrijving Stay4S B.V. via notaris (september) — loopt
- BOIP-merk 'Stay4S' (oktober, na KvK)
- Letselschade-uitkering binnen 14 dagen na ondertekening — check rond eind september (Stay4Compa herinnert)

## ACTIEF PER AI

| AI | Nu bezig | Status |
|---|---|---|
| Stay4Compa | Dit bord live pushen; GPU-offertes monitoren; blueprint 'Stay4S AI Organism'; Team Corpus | ACTIEF |
| OpenCode | DUAL-TRAINING: SFT3 (5%) + eigen-1B (71%) parallel op 2 pods; 14-daagse plan dag 2, dagen 1-9 voltooid | ACTIEF |
| Droid | Post-audit protocol v2.0 (dual-spoor) KLAAR; Notion backup compleet; kostenmonitor W1 GROEN; board-update; dataset-iteratie-plan; wacht op checkpoints | ACTIEF |
| Codex | TAAK-CX-002: eval-criteria per persona, RAG-contract, conversation-mining JSONL-schema (credits-spaarmodus) | ACTIEF |
| ChatGPT | CB-001 meertalige strategie, CB-002 StayLM2 vs commercieel, CB-003 onboarding-review (vr 18 sep) | ACTIEF |
| Grok (browser) | TAAK-G1 AI Organism v1 blueprint; SBP-3 fase 1 document; AI-RAN/MVNA-monitoring | ACTIEF |
| Grok (PowerShell) | GP-001 laptop-audit read-only (wo 16 sep); GP-002 Pi 5 review; inschrijving pendend | STARTEND |
| RunpodOps | MVP Deployment Blueprint v1; workersMin=0 BESLOTEN (ADR-WORKERSMIN); orchestrator wacht op Spoor B-resultaten; open: Usage-sectie-vraag + 5 MVP-tools; CLI-koppeling laptop | ACTIEF |
| Claude (browser) | INGESCHREVEN ALS 10E LID (bevestigd door Mitch, 14 sep). Open deliverables: 4 documenten (SBP-3 fase 1, ADR-0012, ADR-0013, Totaaloverzicht) als losse bestanden; bord-mirror sync; MCP-brug (kanaal 3) | ACTIEF |

## WACHTEN OP MITCH

1. Strato WebFTP: index.html uploaden + SSL activeren (5-10 min) → stay4s.com live
2. GPU-offertes beoordelen (samen met Droid) zodra vergelijkingstabel klaar is
3. Grok PowerShell-inschrijving hier plakken
4. Notaris-afspraak KvK B.V.; Pixel 9 Pro-aankoop (hervat spoor B)
5. RunPod: GO op CLI-koppeling zodra RunpodOps de stappen levert

## LOG

Zie `LOG.md` voor de volledige tijdslijn. Nieuwste entries onderaan.
