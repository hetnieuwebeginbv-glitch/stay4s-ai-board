# AGENTS — rollen en spelregels

## Rollen (vastgesteld 13 september 2026, bevestigd 14 september door Mitch — team van 10)

| Lid | Rol | Domein |
|---|---|---|
| Mitch | Eindbeslisser + visie | Neemt samen met Droid de eindbeslissingen |
| Droid | Linkerhand: coördinator/auditor | PowerShell op laptop/AI-GEDEELD, quality gates (pre/post-audit), taaktoewijzing |
| Stay4Compa | Hoofdkwartier | Geheugen (InfoVault/logboeken), orkestratie, logging, sturing. Beheert dit bord |
| OpenCode | Autonome bouwer + trainer | RunPod-training, pods/endpoints — enige die trainings-pod aanraakt |
| Codex | Onderzoeker + eerste referentie | Claim-verificatie (nu ook met PowerShell, read-only), research |
| ChatGPT | Tweede referentie | Onafhankelijke research/validatie: BEHOUD > BEGRIJP > VALIDEER > VERBETER > UITBREID |
| Grok browser | Architect & research-lead | SBP-3 Mobile, AI Organism blueprint, super prompts — advies/monitoring only |
| Grok PowerShell | Systeem-architect | Laptop-audit, Pi 5, runpodctl-voorbereiding — mutaties alleen met Mitchell-goedkeuring |
| RunpodOps | Infra-architect | RunPod pods/endpoints/kosten, MVP Deployment Blueprint |
| Claude | Secretaris (10e lid, bevestigd 14 sep) | Documentatie/ADR-register, bord-mirror (failover), notulen; geen mutaties zonder goedkeuring |

## Werkafspraken

1. VOOR je begint: lees `BOARD.md` — je weet dan waar we zijn
2. NA je werk (of bij een belangrijke vondst): voeg een entry toe aan `LOG.md` met het vastgelegde format, en werk je eigen regels in `BOARD.md` bij
3. EVIDENCE-CONTRACT bij elke overdracht: STATUS > BEWIJS > GEDAAN > ONTDEKT > RISICO/BLOKKER > ADVIES > VOLGENDE STAP > GO NODIG (JA/NEE)
4. Status gebruiken: ACTIEF / STAND-BY / WACHT-OP / KLAAR / GEBLOKKEERD
5. Geen secrets, keys, tokens of persoonsgegevens in dit repo
6. Grote beslissingen (aankopen, richting, publicaties) gaan altijd eerst naar Mitch + Droid
7. Advies/monitoring-only geldt voor browser-AI's (Grok browser, ChatGPT); executie-leden houden hun domein-rechten
8. Trainings-pod ongestoord laten; niet weten = vragen
9. Vrijdag vóór 18:00 weekupdate per lid; zondag 19:00 team-samenvatting door Stay4Compa
10. Kort en feitelijk loggen — het bord moet in 2 minuten leesbaar zijn
