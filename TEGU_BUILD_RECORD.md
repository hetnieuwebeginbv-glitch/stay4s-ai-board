# TEGU_BUILD_RECORD.md — Google Pixel 9a (tegu)

**Canoniek flash- en bouwrecord · SPOOR B (ROM & OS)**
**Aangemaakt:** 20 september 2026, door Stay4Compa ([compa])
**Doel:** veilige eerste flash van de Pixel 9a (tegu) als pipeline-validatie vóór de eigen Stay4ROM-build (vanaf AOSP, RunPod als build-infra).
**Status record:** FASE 0 — pre-flight nog niet afgerond.

---

## 1. Toestelstatus

| Veld | Waarde |
|---|---|
| Toestel | Google Pixel 9a |
| Codename | tegu |
| SoC | Google Tensor G4, 8GB RAM, 128/256GB |
| Eigenaar | Mitchell (Stay4S) |
| Aangeschaft | september 2026 |
| Huidige firmware | _in te vullen: Instellingen > Over de telefoon_ |
| Android-versie op toestel | _in te vullen (vereist: Android 16, nieuwste securitypatch)_ |
| Buildnummer | _in te vullen_ |
| Bootloader-status | _in te vullen: vergrendeld/geопend_ |
| Batterij bij start | _in te vullen (vereist: >50%)_ |

**Regel:** elk uitgevoerd commando + volledige output hieronder loggen. Dit record is de canonieke bron voor alle tegu-flashes; geen flash zonder record.

---

## 2. Referentie-links (canoniek)

**LineageOS 23.2 (Android 16, officiële tegu-support):**
- Info & specs: https://wiki.lineageos.org/devices/tegu/
- Installatie-gids (leidend voor de eerste flash): https://wiki.lineageos.org/devices/tegu/install/
- Downloads (builds + boot/dtbo/vendor_kernel_boot/vendor_boot): https://download.lineageos.org/devices/tegu
- Zelf bouwen: https://wiki.lineageos.org/devices/tegu/build/
- Update naar nieuwere build: https://wiki.lineageos.org/devices/tegu/update/
- Kernel-bron (gs-6.1): https://github.com/LineageOS/android_kernel_google_gs-6.1_manifest

**GrapheneOS (alternatieve referentie):**
- Installatie (CLI): https://grapheneos.org/install/
- WebUSB-installer (werkt in Chrome op de Chromebook): https://grapheneos.org/install/web
- Releases: https://grapheneos.org/releases
- FAQ (waarom Pixels, verified boot): https://grapheneos.org/faq

**Tools & fabrieksimages:**
- ADB/Fastboot-setup Linux: https://wiki.lineageos.org/adb_fastboot_setup/
- Google platform-tools (nieuwe fastboot, vereist voor vendor_kernel_boot): https://developer.android.com/tools/releases/platform-tools
- Google fabrieksimages tegu (rollback): https://developers.google.com/android/images#tegu
- Google full OTA-images tegu (up/downgrade zonder dataverlies): https://developers.google.com/android/ota#tegu

**LineageOS-aandachtspunt Play Integrity:**
- Device integrity / Play Integrity-quirk: https://wiki.lineageos.org/quirks/snet/

---

## 3. Fase 0 — Pre-flight (nog te doen)

1. Toestel op stock minimaal één keer volledig opstarten en elke functie checken.
2. **Firmware-vereiste:** LineageOS-tegu vereist stock **Android 16** met de nieuwste securitypatch vooraf. Zo niet: eerst updaten via Instellingen (of via full OTA-image). Dit is de Nothing-les: nooit flashen op een afwijkende firmware-versie.
3. Op stock: **SMS/bellen/VoLTE/VoWiFi testen** (IMS-provisioning gebeurt op stock; kapot op stock = kapot op LineageOS).
4. **Alle Google-accounts verwijderen** (voorkomt Factory Reset Protection).
5. **OEM-unlock aanzetten** (Instellingen > Over de telefoon > buildnummer 7x tikken > Ontwikkelaarsopties > OEM-ontgrendelen). Toestel verbonden met internet; kan tot 24u na verwijderen van accounts duren.
6. Batterij >50%; back-up van alles wat bewaard moet blijven (unlock wist alles).
7. Chromebook: Instellingen > Geavanceerd > Ontwikkelaars > Linux-ontwikkelomgeving > USB-apparaat beheren > Pixel 9a aanvinken (Crostini USB-passthrough).
8. In Crostini: officiële Google platform-tools downloaden (NIET apt-fastboot — te oud voor de tegu-partities):
   ```
   wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
   unzip platform-tools-latest-linux.zip && cd platform-tools
   ./adb version && ./fastboot --version
   ```

## 4. Fase 1 — Bootloader unlock (eenmalig)

```
./adb devices                      # toestel zichtbaar? anders USB-passthrough checken
./adb -d reboot bootloader
./fastboot devices                 # serie-nr zichtbaar? anders kabel/poort wisselen
./fastboot flashing unlock         # op scherm bevestigen; ALLES WORDT GEWIST
```
Na de wipe: opnieuw opstarten, USB-debugging opnieuw aanzetten, (nogmaals) geen Google-account inlogken.

## 5. Fase 2 — LineageOS-flash (exacte volgorde)

Bestanden vooraf downloaden van https://download.lineageos.org/devices/tegu :
boot.img, dtbo.img, vendor_kernel_boot.img (uit de images-zip), vendor_boot.img (LineageOS Recovery) en de LineageOS 23.2 zip zelf.

```
# 2.1 Extra partities (vereist voor tegu, anders werkt recovery niet)
./fastboot flash boot boot.img
./fastboot flash dtbo dtbo.img
./fastboot flash vendor_kernel_boot vendor_kernel_boot.img

# 2.2 Recovery
./fastboot reboot bootloader
./fastboot flash vendor_boot vendor_boot.img

# 2.3 In recovery booten (Volume-omlaag + Power > Recovery Mode)
# Recovery: "Apply update" > "Apply from ADB"
./adb -d sideload lineage-*.zip     # bevestigen op scherm; "signature verification failed"-vraag alleen bij afwijkende versie verwacht JA antwoorden indien vanzelfde versie

# 2.4 Optioneel: nadat de sideload gedaan is, (optioneel) opnieuw sideload voor gapps/addons NIET voor basistest — puur LineageOS eerst
# 2.5 Reboot naar systeem (eerste boot 2-5 min)
```

**Belangrijk:** iets mislukt = STOPPEN. Niet doorklikken. Foutmelding + volledige output in dit record loggen, dan pas herstarten vanaf de mislukte stap.

## 6. Fase 3 — Verificatie na eerste boot

- [ ] Eerste boot voltooid (< 5 min)
- [ ] Setup wizard doorlopen (geen Google-account)
- [ ] Instellingen > Over de telefoon: Android 16, LineageOS 23.2
- [ ] WiFi, SMS, bellen, VoLTE-test
- [ ] Camera, vingerafdruk, NFC
- [ ] Batterijverbruik 24u observeren (basislijn voor ROM-vergelijking)

**Bekend beperking:** Play Integrity faalt op LineageOS — banking-apps werken (mogelijk) niet. Zie https://wiki.lineageos.org/quirks/snet/ . Voor Stay4ROM wordt dit een eigen keuzepunt (Guardian-/Vault-scope).

## 7. Rollback-plan (altijd paraat)

1. Download de juiste fabrieksimage: https://developers.google.com/android/images#tegu (zelfde of nieuwere build dan de vertrokken firmware).
2. Ontgrendel de bootloader (indien nog vergrendeld) en flash de fabrieksimage via `flash-all` (script uit de Google-zip).
3. **Bootloader alleen opnieuw vergrendelen met een 100% stock-image** (fastboot flashing lock) — anders bestaat brickrisico door verified boot-mismatch.
4. Record: rollback-reden + datum hier noteren.

## 8. Vervolg na geslaagde flash (buiten scope van dit record)

- Pipeline geborgd → Stay4ROM-build vanaf AOSP (RunPod on-demand pod: 64GB RAM / 400GB disk, spin-up build destroy, zie INFRA-wisselbesluit 9 sep).
- Kernbron: LineageOS-tegu als referentie voor partitie-indeling, vendor-blobs en kernel; kernel-bron: https://github.com/LineageOS/android_kernel_google_gs-6.1_manifest
- Eigen device tree: android_device_google_tegu (nieuw repo, docs-standaard per repo).
- Eerste custom service na reproduceerbare basis: AetherCoreService (opvolging GuardianService, VaultService, GlyphService, MeshmaticService).

---

*Wijzigingen in dit record altijd met commit-prefix [compa] / [grok] / [mitchell] en een LOG.md-regel.*
