# 010 — Red Team Ops with Starkiller (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 10/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_Red Team Ops with Starkiller.txt](010_Red Team Ops with Starkiller.txt) · [010_Red Team Ops with Starkiller.srt](010_Red Team Ops with Starkiller.srt)

## Concetti chiave

- **Starkiller** = GUI **Electron + Vue.js** ufficiale per **PowerShell-Empire**, mantenuta da **BC Security**.
- È un **front-end**: si collega via **REST API** al server Empire (default `localhost:1337`).
- Stesso lab del video 09 — stesso flusso (listener → stager → agent → moduli), ma in versione visuale.
- **Credenziali default**: `empire_admin / password123` (in passato `admin / empireadmin`).
- Sidebar con: **Listeners, Stagers, Agents, Modules, Credentials, Reporting, Users, Plugins, Settings**.
- **Funzionalità extra rispetto al CLI**:
  - **Interactive agent shell** con risultati quasi istantanei nel pannello.
  - **File browser** integrato (navigazione filesystem del target, download diretto).
  - **Process browser**.
  - **Chat widget** per **multiplayer / collaborative ops**.
  - **Task log** centralizzato con autore (`who ran it`) — utile per red team report.
- **Plugins inclusi**: `csharpserver` (compilazione C#), `websockify`, `socks_proxy_server` (reverse shell stager).
- Demo con **Wireshark** per visualizzare i **callback HTTP** del beacon ogni 5s e l'effetto del **jitter** (0.0–1.0, randomizza la cadenza).

## Spiegazione approfondita

### Avvio
1. Server Empire come per la CLI: `sudo powershell-empire server`.
2. Avvio GUI dal menu Kali → **Starkiller** (o `starkiller` da terminale).
3. Login → endpoint default `localhost:1337` → credenziali `empire_admin / password123`.

### Layout
- **Settings**: dark/light mode, chat widget toggle, API token, cambio password utente.
- **Users**: creazione account per altri operatori (`redteam1`, `redteam2`) — multiplayer remoto.
- **Plugins**: lista plugin pre-pacchettizzati, start/stop con pulsante Submit.

### Setup operativo (riprende il lab del video 09)
- **Listeners → Create → Type: http** → form con `Host`, `Port=8888`, `DefaultDelay=5`, `DefaultJitter=0.0`, header server, ecc. → Submit → "running".
- **Stagers → Create → multi/launcher** → Listener `http`, Language `powershell`, opzionale obfuscation → Submit → tasto **Copy to clipboard** (output non stampato come in CLI).
- Incollare il one-liner nella shell SMB del target → callback istantaneo.
- **Agents** → riga nuova con tutti i metadati (hostname, internal IP, user, integrity, last seen).
- **View** sull'agent → console con campo comandi (es. `whoami`, `systeminfo`) → arrow per espandere output → upload/download file → clear queued tasks → pop-out.

### Moduli da GUI
- **Modules** → ricerca per categoria (es. `situational_awareness/winenum`, `situational_awareness/get_computer_details`, `situational_awareness/antivirusproduct`).
- Si può **incatenare** moduli sul tab Agents → View → ricerca → Submit. Agent eredita la selezione (no `set Agent`).
- Errori tipici visti nel video: `local variable module_code referenced before assignment` su moduli che non hanno parametri obbligatori configurati — si supera scegliendo un modulo alternativo (`winenum` come fallback).

### File browser
- View agent → tab **File Browser** → click su directory → l'agent risponde al prossimo beacon → tree popolato → click su file → **Download** → trasferito al server Empire.

### Tasks log
- Tab **Tasks** (o sotto-tab dell'agent) → tabella `TaskID | User | Command | Status` → drop-down per vedere comando e output → audit completo della session.

### Tuning beacon (con Wireshark)
- Wireshark su `eth1` → filtro `ip.src == <target_ip>` → si vedono i callback HTTP ogni **5s**.
- Modifica `DefaultDelay = 10` sull'agent/listener → callback ogni 10s.
- Modifica `DefaultJitter = 0.5` (50%) → randomizza la cadenza fra `delay*(1-jitter)` e `delay*(1+jitter)` → traffic pattern meno periodico → **OPSEC**.

## Comandi & strumenti

```bash
# Avvio Empire server (obbligatorio prima di Starkiller)
sudo powershell-empire server

# Avvio GUI
starkiller
```

| Azione GUI | Equivalente CLI |
|---|---|
| Listeners → Create → http | `uselistener http; set ...; execute` |
| Stagers → Create → multi/launcher | `usestager multi/launcher; set Listener http; execute` |
| Agents → View → command box | `interact <agent>; shell <cmd>` |
| Modules → search → Submit | `usemodule <path>; set ...; execute` |
| Tasks tab | `history` |
| Credentials tab | `creds` |
| Users tab | `add user` server-side |

| Plugin | Funzione |
|---|---|
| `csharpserver` | Compila stager/moduli C# (Roslyn) |
| `websockify` | Bridge WebSocket per comunicazioni custom |
| `socks_proxy_server` | Reverse shell SOCKS via stager |

## Esempi pratici

```text
# Flusso GUI (mirror del video 09)
1) Server: sudo powershell-empire server
2) Login Starkiller -> empire_admin / password123
3) Listeners > Create > http, Host=<kali>, Port=8888, Submit
4) (Fuori) impacket-smbexec administrator:'pwd'@demo.ine.local
5) Stagers > Create > multi/launcher (Listener=http) > Copy to clipboard
6) Incollare nel prompt SMB -> agent appare in Agents
7) Agents > View > shell whoami / systeminfo
8) Modules > situational_awareness/network/winenum > Submit
9) File Browser > C:\Users\Administrator\Desktop > Download
10) Tasks > log audit
11) (Opt) Wireshark + tweak Delay/Jitter su agent
```

## Punti d'attenzione per l'esame eCPPT

- **Starkiller è solo un front-end**: tutta la logica (listener, beacon, moduli) sta sul **server Empire**. Spegnendo il server, la GUI è inutile.
- **Porta 1337** = REST API a cui si connette Starkiller (default `localhost:1337`).
- **Credenziali default** = `empire_admin / password123` (cambiare in produzione).
- **Multiplayer**: più operatori connessi simultaneamente con account distinti — la GUI offre chat e attribuzione dei task.
- **Delay + Jitter** sono parametri OPSEC chiave: aumentare jitter rende il traffic meno detectable da SIEM che cercano pattern periodici.
- **File Browser e Tasks log** sono i vantaggi reali rispetto alla CLI: ricordarli come differenziatori in domande "perché usare la GUI?".
- **Stager copy-paste**: la GUI non stampa il one-liner, va copiato con tasto destro / pulsante Copy.
- Quando un modulo va in errore "local variable ... referenced before assignment", spesso manca un parametro obbligatorio o l'agent non è settato.

## Collegamenti con altri video

- Precedente: [[09_ Red Team Ops with PowerShell-Empire]] — stesso lab via CLI (versione estesa con pivoting MSF).
- Teoria base: [[08_Introduction to PowerShell-Empire]].
- Architettura C2 client-server: [[06_C2 Deployment & Operation]].
- Conclusione del modulo: [[011_ Course Conclusion]].
