# 02 — Introduction to Command & Control (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 2/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Introduction to Command & Control.txt](02_Introduction to Command & Control.txt) · [02_Introduction to Command & Control.srt](02_Introduction to Command & Control.srt)

## Concetti chiave

- **Command & Control (C2 / CNC)** è la **struttura di comunicazione** usata da un attaccante per controllare e coordinare attività su sistemi compromessi.
- Nel **MITRE ATT&CK** è la tactic **TA0011** — include metodi, protocolli e infrastruttura per comandi, raccolta dati e gestione.
- Non confondere **C2 (tactic)** con **C2 framework (tool)**: i framework sono l'implementazione tecnica della tattica.
- Obiettivi C2 dal punto di vista dell'operatore: comunicazione **stable & reliable**, **remote command execution**, **persistence**, **defense evasion**, **data exfiltration**.
- Componenti base: **C2 server** (hub centrale) + **C2 agent/implant** (eseguito sull'host compromesso) + **communication channel** (HTTP/HTTPS/DNS/WebSocket/custom).
- Best practice: **mai connettersi direttamente** al C2 server (es. SSH). Si usa un client remoto (es. Empire client) attraverso VPN per ridurre attribuibilità.

## Spiegazione approfondita

### Definizione
> "C2 refers to the communication structure used by attackers to remotely control and coordinate activities across compromised systems."

Encompass methods, protocols, infrastruttura per inviare comandi, ricevere dati e gestire operazioni in modo coordinato.

### Dal C2 (tactic) ai C2 frameworks
I C2 frameworks **non hanno preceduto** la tattica: prima è nato il "modo di fare", poi gli strumenti hanno implementato la funzionalità necessaria. Differenza fondamentale rispetto a una **reverse shell con netcat**: il C2 framework offre nativamente exfiltration, logging, multi-user, encryption, evasion.

### Componenti C2 (infrastruttura tipica)
- **C2 server**: hub centralizzato che riceve i beacon e instrada i comandi. Hostabile on-premise, in cloud o come hidden service Tor.
- **C2 agent/implant**: software sul sistema compromesso che si connette al server e facilita remote execution e data transmission.
- **Communication channel**: HTTP, HTTPS, DNS, WebSocket, FTP, SSH, custom encrypted, ecc.
- **Operator interface**: client (CLI o GUI) che si collega remotamente al server.

### Ruolo del C2 nel red teaming
1. **Centralized coordination** — gestione di molteplici host compromessi da un unico punto.
2. **Persistence & remote access** — connessione mantenuta nel tempo, anche dopo reboot.
3. **Lateral movement** — pivot tra sistemi, escalation, attacco multistage.
4. **Complex attack scenarios** — exfiltration, privesc, evasion combinati.
5. **Adversary emulation** — replicare TTP di APT specifici (es. APT29).
6. **Blue team testing / purple teaming** — verificare detection e response.

### Perché segregare l'operatore dal server
Se l'IR identifica l'IP del C2 server, indagheranno. Connettersi direttamente espone l'identità. Pattern corretto: **operatore → VPN → C2 client remoto → C2 server**.

## Comandi & strumenti

Video teorico: nessun comando. Strumenti citati come **esempi** di C2:

| Tool | Note |
|---|---|
| **Metasploit Framework** | Tecnicamente È un C2 framework (anche se usato perlopiù in pen testing). |
| **PowerShell-Empire** | Esempio di C2 framework "classico" trattato nel modulo. |
| **MITRE ATT&CK** (Command and Control - TA0011) | Knowledge base che cataloga tecniche C2. |

## Esempi pratici

N/A — video teorico. Esempi concreti in [[08_Introduction to PowerShell-Empire]] in poi.

## Punti d'attenzione per l'esame eCPPT

- **Definizione di C2** memorizzata: "struttura di comunicazione per remote control e coordination" — non solo "il tool".
- **Componenti**: C2 server, C2 agent/implant, communication channel.
- **C2 ≠ reverse shell** singola: il discriminante è la presenza di exfil, logging, multi-user, encryption nativa.
- **MITRE ATT&CK Tactic**: C2 = **TA0011**. Le tecniche correlate includono Application Layer Protocol (T1071), Encrypted Channel (T1573), Domain Fronting (T1090.004), DNS Tunneling.
- Capire che **Metasploit è un C2** (anche se usato in pen test standard) è una possibile trick question.
- **OPSEC dell'operatore**: VPN + client remoto, mai SSH diretto sul C2 server.

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_Introduction to C2 Frameworks]] — dai concetti agli strumenti.
- Terminologia dei componenti: [[05_ C2 Framework Terminology]]
- Modelli di deployment / canali / domain fronting: [[06_C2 Deployment & Operation]]
- Esempi: [[08_Introduction to PowerShell-Empire]] · [[09_ Red Team Ops with PowerShell-Empire]]
