# 01 — Course Introduction (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 1/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Introduzione al corso **Command & Control (C2 / CNC)** focalizzato sull'uso di **C2 frameworks** in operazioni di red teaming e penetration testing.
- Il corso copre l'intera catena: **cos'è C2 → C2 frameworks → terminologia → deployment/operation → scelta del framework → uso pratico di PowerShell-Empire e Starkiller**.
- Alla fine c'è una sezione di **C2 Framework Labs indipendenti** per pratica hands-on su framework aggiuntivi.
- Prerequisiti: pen testing di base, familiarità con Windows e Linux, conoscenza di Metasploit (o framework equivalenti di exploitation/post-exploitation).
- Il corso fa parte della learning path per la certificazione **eCPPT** ed è tenuto dal Senior Pentest / Red Team Lead di HackerSploit.

## Spiegazione approfondita

### Topic Overview (i 7 blocchi del modulo)
1. **Introduction to Command & Control** — il C2 come **tattica** (in ottica MITRE ATT&CK), non come tool. Inquadramento operativo: cosa significa "fare C2" in un red team.
2. **Introduction to C2 Frameworks** — passaggio da tattica a **tool**: cosa sono, come funzionano, ruolo nelle operazioni red team.
3. **C2 Framework Terminology** — vocabolario condiviso fra framework: listener, stager, agent, beacon, sleep, jitter, ecc.
4. **C2 Deployment & Operation** — modelli di deployment (centralizzato, peer-to-peer), protocolli di comunicazione, infrastruttura.
5. **C2 Matrix — Choosing the Correct C2 Framework** — criteri di selezione basati sui requisiti del red team e sull'ambiente target.
6. **PowerShell-Empire** — introduzione + lab di red team ops con Empire.
7. **Starkiller** — la GUI di Empire usata in lab.

### Prerequisiti dichiarati
- **Pen testing**: conoscenza ed esperienza (livello eJPT o equivalente).
- **OS**: familiarità con Windows e Linux (per interagire con i sistemi compromessi).
- **Exploitation/Post-Exploitation framework**: principalmente **Metasploit**, o framework equivalenti.

### Learning Objectives (la "promessa" dell'istruttore)
1. Comprendere cos'è il **command and control** in ottica red team e offensive.
2. Comprendere cosa sono i **C2 frameworks**, come funzionano, quali funzionalità offrono e che ruolo svolgono.
3. Comprendere i **modelli di comunicazione e i protocolli** usati per progettare/deployare/operare infrastruttura C2.
4. Saper **identificare il C2 framework corretto** in base alla natura dell'engagement e alle feature richieste.
5. Saper **installare, configurare e usare PowerShell-Empire e Starkiller** in ambienti Windows.
6. Acquisire esperienza pratica con vari C2 framework popolari attraverso i lab finali.

## Comandi & strumenti

Video introduttivo: **nessun comando**. Strumenti citati che verranno usati:

| Strumento | Categoria | Scopo |
|---|---|---|
| **PowerShell-Empire (Empire 4)** | C2 framework | Centro del modulo: post-exploitation Windows-centric. |
| **Starkiller** | GUI per Empire | Front-end Electron/Vue.js per PowerShell-Empire. |
| **C2 Matrix** | Risorsa di selezione | Spreadsheet + questionario per scegliere il framework giusto. |
| **MITRE ATT&CK** | Knowledge base | Inquadra C2 come tactic ID **TA0011**. |

## Esempi pratici

N/A. Esempi pratici partono dal video **08 — Introduction to PowerShell-Empire** e **09 — Red Team Ops with PowerShell-Empire**.

## Punti d'attenzione per l'esame eCPPT

- Il modulo C2 è parte integrante della learning path **eCPPT (2024)**: aspettati domande su **terminologia C2** (listener/stager/agent/beacon/sleep/jitter) e su **scelta del framework**.
- Sapere che **C2 = tattica MITRE ATT&CK TA0011**, non solo "il framework".
- PowerShell-Empire è il framework dimostrato in lab: workflow `uselistener → execute → usestager → generate → agents → interact → usemodule` da memorizzare.
- Distinguere **C2 framework** (es. Empire, Cobalt Strike) da **semplice reverse shell** (netcat): C2 ha logging, persistence, encryption, exfiltration, multi-user.

## Collegamenti con altri video

- Prossimo: [[02_Introduction to Command & Control]] — la tattica.
- Frameworks: [[03_Introduction to C2 Frameworks]]
- Terminologia: [[05_ C2 Framework Terminology]]
- Deployment: [[06_C2 Deployment & Operation]]
- Selezione framework: [[07_The C2 Matrix - Choosing the Correct C2 Framework]]
- Lab pratici: [[08_Introduction to PowerShell-Empire]] · [[09_ Red Team Ops with PowerShell-Empire]] · [[010_Red Team Ops with Starkiller]]
- Chiusura: [[011_ Course Conclusion]]
