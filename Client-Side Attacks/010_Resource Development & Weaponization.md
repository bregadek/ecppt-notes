# 010 — Resource Development & Weaponization (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 10/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_Resource Development & Weaponization.txt](010_Resource Development & Weaponization.txt) · [010_Resource Development & Weaponization.srt](010_Resource Development & Weaponization.srt)

## Concetti chiave

- **Resource Development** (MITRE ATT&CK) = acquisire/costruire risorse (infrastruttura, exploit, script, payload).
- **Weaponization** (Lockheed Cyber Kill Chain) = combinare exploit + backdoor in **payload deliverable** (es. macro embedded in `.docm`).
- I termini provengono dalla **strategia militare**, adottati in cybersecurity.
- **MITRE ATT&CK** = knowledge base di TTPs di APT reali, struttura: **Tactics → Techniques → Sub-techniques → Procedures**.
- **Cyber Kill Chain (Lockheed Martin)** = 7 fasi: Reconnaissance, **Weaponization**, Delivery, Exploitation, Installation, C2, Actions on Objectives.
- Sequenza logica: **Recon → Resource Development → Weaponization → Delivery → Execution**.
- Distinzione operativa: dev VBA macro = resource dev; embed macro in `.docm` con obfuscation/AV evasion = weaponization.

## Spiegazione approfondita

### Definizioni
- **Resource Development** — gather/build tools, knowledge, infrastructure (domains, VPS, exploit code, custom scripts, social eng tactics).
- **Weaponization** — coupling exploit + backdoor in payload deliverable (es. macro embedded in doc, obfuscated, anti-AV).

### MITRE ATT&CK
- **A**dversarial **T**actics **T**echniques & **C**ommon **K**nowledge.
- Knowledge base globale di attacchi reali catalogati per **TTPs**.
- Matrici: Enterprise (Pre, Windows, Linux, macOS, Cloud), Mobile (Android/iOS), ICS.
- **Pre-matrix tactics**: Reconnaissance, **Resource Development** (TA0042).
- Esempio sub-technique: `T1583.003 Acquire Infrastructure: Virtual Private Server` con procedures di gruppi come Lapsus$, Dragonfly.
- Pen tester usa MITRE per **adversary emulation** (emulare specifico APT).

### Cyber Kill Chain (Lockheed Martin)
7 fasi sequenziali:
1. Reconnaissance
2. **Weaponization**
3. Delivery
4. Exploitation
5. Installation
6. Command & Control
7. Actions on Objectives

Confronto: dove MITRE dice "Resource Development", Cyber Kill Chain dice "Weaponization" → ma in realtà **weaponization in CKC** = combinare risorse in payload deliverable, non gathering.

### Differenze chiave (Resource Dev vs Weaponization)

| Aspetto | Resource Development | Weaponization |
|---|---|---|
| Focus | Acquisire tool/info/infrastructure | Trasformare in payload deliverable |
| Stage | Precede weaponization | Dopo resource dev |
| Attività | Recon tool, script dev, dominio, VPS | Crafting payload, obfuscation, AV evasion |
| Output | Tool/info raw | Payload pronto per delivery |

### Adapted Client-Side Methodology (Alexis Ahmed)
Combina MITRE + CKC, specifica per client-side:
1. **Planning & Reconnaissance**
2. **Resource Development** (sviluppa VBA, PowerShell, dropper, loader; testa)
3. **Weaponization** (embed in `.docm`, obfuscate, AV evasion)
4. **Delivery** (Gophish phishing email)
5. **Execution / Initial Access**

### Esempio applicato
- Recon: target Acme Corp HR, Office 2016.
- Resource Dev: scrivi VBA dropper PowerShell + test su Office 2016 VM.
- Weaponization: embed in `Invoice.docm`, MacroPack obfuscation, MOTW removal, AMSI bypass.
- Delivery: Gophish, pretext "Invoice review".
- Execution: vittima apre → macro lancia PS dropper → reverse shell.

## Comandi & strumenti

| Risorsa | Scopo |
|---|---|
| **MITRE ATT&CK** (`attack.mitre.org`) | Knowledge base TTPs APT |
| **Cyber Kill Chain** (Lockheed) | Framework 7 fasi attacco |
| **Unified Kill Chain** | Variante più granulare (citata) |
| VBA editor (Office Developer tab) | Resource dev macro |
| MacroPack / msfvenom | Weaponization |
| Gophish | Delivery |

## Esempi pratici

```text
# Esempio mappatura TTP per macro phishing campaign:
Recon              -> T1589 Gather Victim Identity (employee emails)
Resource Dev       -> T1587 Develop Capabilities (custom macro)
                   -> T1583.001 Acquire Domain
                   -> T1583.003 Acquire VPS
Initial Access     -> T1566.001 Spearphishing Attachment
Execution          -> T1204.002 User Execution: Malicious File
Defense Evasion    -> T1027 Obfuscated Files
```

## Punti d'attenzione per l'esame eCPPT

- **MITRE vs CKC**: MITRE = Resource Development, CKC = Weaponization. Sapere che semanticamente **non sono identici**: RD = acquisire, W = combinare in payload.
- Memorizzare i **7 step della Cyber Kill Chain**.
- Memorizzare il **flusso Adapted methodology**: Recon → Resource Dev → Weaponization → Delivery → Execution.
- **TA0042 Resource Development** è una **pre-attack tactic** nel MITRE.
- Sapere che **adversary emulation** = simulare APT specifico via MITRE TTPs.
- Possibile domanda: "In quale fase del CKC sviluppi la macro VBA?" → **Weaponization** (combina con doc).
- Possibile domanda: "Acquisire un dominio rientra in quale tactic MITRE?" → **Resource Development**.

## Collegamenti con altri video

- Precedente: [[09_Phishing with Gophish - Part 2]]
- Prossimo: [[011_VBA Macro Fundamentals]] — inizio resource development concreto.
- Weaponization dei doc: [[018_Pretexting Phishing Documents]]
- MacroPack automation: [[021_Automating Macro Development with MacroPack - Part 1]]
- Delivery finale: [[024_Initial Access Via Spear Phishing Attachment]]
