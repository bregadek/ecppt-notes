# 03 — Introduction to C2 Frameworks (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 3/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Introduction to C2 Frameworks.txt](03_Introduction to C2 Frameworks.txt) · [03_Introduction to C2 Frameworks.srt](03_Introduction to C2 Frameworks.srt)

## Concetti chiave

- Un **C2 framework** è una **piattaforma software** progettata per gestire, controllare e orchestrare attività su sistemi remoti compromessi.
- I framework sono nati **dopo** la tattica C2 ed hanno integrato nel tempo le funzionalità necessarie a supportarla (evoluzione).
- Funzionalità tipiche obbligatorie: **communication channel (cifrato)**, **remote command execution**, **persistence**, **lateral movement**, **privilege escalation**, **data exfiltration**, **scripting/automation**, **evasion**, **payload development**, **logging/reporting**.
- **Encryption + obfuscation** del canale è il discriminante: se non c'è, **non è davvero un C2 framework**.
- I framework supportano vari protocolli: HTTP/HTTPS, DNS, WebSocket, FTP, SMTP, custom.

## Spiegazione approfondita

### Definizione
> "A C2 framework is a software platform designed for managing, controlling and orchestrating activities on remote systems in an offensive security context."

In ambito etico (pen test/red team) consente di simulare scenari di attacco avanzati per valutare la postura difensiva dell'organizzazione.

### Funzionalità chiave (checklist per valutare un C2)
1. **Establishing communication channels** — su HTTP/HTTPS/DNS/WS/custom, **con encryption nativa** + obfuscation per evitare intercettazione/analisi.
2. **Remote control & command execution** — esecuzione comandi su endpoint compromessi, accesso file, esecuzione script.
3. **Persistence mechanisms** — startup, scheduled tasks, backdoor. Critico per long-term ops (APT). Si controlla via **callback/beacon duration** e **C2 profiles**.
4. **Lateral movement** — capacità di muoversi tra host compromessi, sfruttando credenziali e vuln di rete.
5. **Privilege escalation** — moduli per privesc, oppure capacità di "living off the land" senza tool esterni.
6. **Data exfiltration** — collezione e invio dati al C2 server. Tipicamente in **batch** e su canali alternativi (DNS) per non destare allarmi su monitoring egress.
7. **Automation & scripting** — script tipo MSF resource scripts per automatizzare task ripetuti.
8. **Evasion techniques** — obfuscazione traffico, porte standard, **domain fronting**.
9. **Payload development** — possibilità di generare/modificare payload custom (EXE, PowerShell, Python, HTA, ecc.) per adattarsi al target.
10. **Logging & reporting** — fondamentale per attribuzione attività in team, accountability legale e reporting finale.

### Perché la varietà di payload importa
Su Windows non sempre puoi scaricare un EXE. Servono **PowerShell**, **HTA (`mshta.exe`)**, **macro Office**, **shellcode in-memory** ecc. Esempio: `web_delivery` di MSF è il modello mentale (un web server serve payload PowerShell/HTA, lo si esegue one-liner sul target).

### Perché il logging è critico
Per il red team operator NON è solo "memoria storica": è **accountability**. Se il cliente dice "ci avete fatto danno", il log timestamped attribuisce chi ha eseguito cosa, quando. Si estricano responsabilità legali.

## Comandi & strumenti

Video teorico. Riferimenti operativi:

| Concetto | Esempio concreto |
|---|---|
| **Communication channel** cifrato | HTTPS in Empire/Cobalt Strike, malleable C2 profiles. |
| **Persistence + beacon** | Beacon di Cobalt Strike con `sleep` + `jitter`. |
| **Automation** | Metasploit **resource scripts** (`.rc`). |
| **Payload diversification** | `msfvenom -f` con formati diversi; `PowerShell-Empire` con multi-launcher (PowerShell/HTA/macro/bash). |
| **Logging** | Empire log JSON in `~/.empire/server/data/empire.log`. |

## Esempi pratici

N/A — video teorico. Vedere [[09_ Red Team Ops with PowerShell-Empire]] per esempi reali di queste funzionalità.

## Punti d'attenzione per l'esame eCPPT

- Saper enumerare le **funzionalità minime di un C2 framework**: encryption canale, remote exec, persistence, lateral movement, exfil, logging.
- **Encryption + obfuscation** del canale è non-negoziabile: una "shell" senza encryption non è C2.
- **Staged vs unstaged payload**: lo **stager** è il piccolo dropper che scarica e lancia lo **stage** (il vero payload).
- **In-memory execution** (es. payload PowerShell injected) → tipico di Empire, evita scrittura su disco e bypass di AV signature-based.
- **Exfiltration realistica**: APT staging in `%TEMP%`, compressione (7-Zip), invio in batch a orari off-hours, canale alternativo (DNS).
- **Logging** = obbligo professionale + legale.

## Collegamenti con altri video

- Precedente: [[02_Introduction to Command & Control]]
- Prossimo: [[05_ C2 Framework Terminology]] — vocabolario per parlare di queste funzionalità.
- Deployment & domain fronting: [[06_C2 Deployment & Operation]]
- Scelta framework: [[07_The C2 Matrix - Choosing the Correct C2 Framework]]
- Esempi reali: [[08_Introduction to PowerShell-Empire]] · [[09_ Red Team Ops with PowerShell-Empire]]
