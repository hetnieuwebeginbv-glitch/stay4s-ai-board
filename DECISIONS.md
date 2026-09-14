# BESLUITENREGISTER (ADR's)

| ID | Titel | Status | Datum |
|---|---|---|---|
| ADR-0011A | LineageOS 23.2/Android 16 als target Stay4ROM (Nothing 3a) | Superseded door ADR-AOSP | 28 jul |
| ADR-AOSP | ROM vanaf AOSP - geen LineageOS/GrapheneOS-basis; externe deps expliciet loggen | Accepted | 9 sep |
| - | Referentiehardware wisselt naar Pixel 9 Pro; echte flash met bewijs = hoofddoel | Accepted | 7 sep |
| - | Eigen desktop/server/AI-node i.p.v. cloud-GPU huren | Accepted | 7 sep |
| ADR-0012 | Stay4Net prive AI-mobiel netwerk (WireGuard+Headscale, Reticulum-mesh, Transatel) | Proposed | 11 sep |
| SBP-3 F1 | Stay4S Mobile fase 1 (architectuur, datamodel, API-contracten, MVNA-shortlist) | Fase 1 compleet - fase 2 wacht op GO | 13 sep |
| ADR-CLOUD2 | Twee gescheiden clouds: Interne Cloud + Klantencloud (beide Stay4S-eigendom) | Accepted | 9 sep |
| ADR-GPU | AI-hoofdrig: RTX PRO 6000 Blackwell 96GB, budget EUR 25.000 | Accepted | 12 sep |
| ADR-BOARD | GitHub-board live als kanaal 2 (open leesbaar, geen secrets; postbode verdwijnt geleidelijk) | Accepted | 13 sep |
| ADR-CORPUS | Team-prompts/overdrachten worden trainingsdata (Stay4S Team Corpus v1) | Accepted | 13 sep |
| ADR-HIER | Decision-hierarchy: Mitchell (eindbeslisser) + Droid (linkerhand) | Accepted | 13 sep |
| ADR-0013 | Begrensde autonomie voor AI-leden binnen de quality-gate pipeline | Accepted - GO door Mitchell + Droid 14 sep; uitzondering: nog geen vaste kostendrempel voor harde hekken; overige hekken (flash-acties, device tree/kernel, naam/merk, klantdata/privacy, externe communicatie) onverkort | 14 sep |
| ADR-CHECKPOINT | Primair StayLM2-checkpoint: SFT1 (staylm2:1, overall 0.4664, beste domein-scores); Mlang (0.3715) = reserve voor meertalige lijn; GO voor DPO-run op SFT1 | Accepted - Mitchell 14 sep | 14 sep |
| ADR-WORKERSMIN | staylm2-serverless endpoint: workersMin = 0 - volledig on-demand, geen vaste kosten; cold start acceptabel tijdens beta | Accepted - Mitchell 14 sep | 14 sep |

*Bron: Claude-browser board-backup + Stay4Compa logboek (13 sep 2026).*
