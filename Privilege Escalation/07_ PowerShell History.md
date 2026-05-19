# 07 — PowerShell History (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 7/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_ PowerShell History.txt](07_ PowerShell History.txt) · [07_ PowerShell History.srt](07_ PowerShell History.srt)

## Concetti chiave

- PowerShell mantiene un **history file** (analogo a `.bash_history` su Linux): **`ConsoleHost_history.txt`**.
- Path standard: `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`.
- Spesso contiene **credenziali in clear-text** quando admin o altri user eseguono comandi (es. `runas`, `New-Object PSCredential`, parametri inline) senza ripulire.
- Vettore tipico: admin/sysadmin usa il PC dell'utente standard per task amministrativi → password resta in history.
- **Per-user**: ogni utente ha il suo history.

## Spiegazione approfondita

### Perché esiste questo vettore
- Sysadmin spesso accedono fisicamente o via RDP a PC utente per installazioni/troubleshooting.
- Usano `runas`, `Invoke-Command`, `PSRemoting`, ecc. → password digitata o passata inline.
- Se il sysadmin **dimentica di chiudere/clearare** la PowerShell session → history persiste sul disco.

### Folder `AppData` nascosto
- `AppData` è hidden by default → in GUI serve abilitare "Show hidden files".
- Da CLI accessibile direttamente.

### Workflow del lab
1. Accesso come `student`.
2. Navigazione a `C:\Users\student\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\`.
3. Apertura `ConsoleHost_history.txt`.
4. Identificazione comando sospetto: il prevenrente user/admin aveva impostato variabili:
   ```powershell
   $username = "Administrator"
   $password = ConvertTo-SecureString "<plaintext>" -AsPlainText -Force
   ```
   La password clear-text resta nel file.
5. Sfruttamento → `runas /user:administrator cmd` con la password recuperata.

### Mitigazione (sicurezza)
- Clearare history: cancellare contenuto del file.
- Configurare PowerShell per **non scrivere history** (`Set-PSReadLineOption -HistorySaveStyle SaveNothing`).

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `cd $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine` | Naviga al folder PS history |
| `cat ConsoleHost_history.txt` | Lettura del file di history |
| `Get-Content (Get-PSReadLineOption).HistorySavePath` | Path dinamico history (clean) |
| `runas.exe /user:administrator cmd` | Elevazione locale con creds trovate |

## Esempi pratici

```powershell
# Step 1 — Verifica utente
whoami
whoami /priv

# Step 2 — Lettura history (path fisso)
cat C:\Users\student\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

# Esempio output rilevante trovato nel lab:
# cd C:\Windows
# clear
# whoami
# Get-Process
# net user
# $env:USERNAME = "Administrator"
# $password = ConvertTo-SecureString "<plaintext_password>" -AsPlainText -Force
# ...

# Step 3 — Sfruttamento
runas.exe /user:administrator cmd
# inserire password recuperata
```

```powershell
# Variante: path universale
$historyPath = (Get-PSReadLineOption).HistorySavePath
Get-Content $historyPath
```

## Punti d'attenzione per l'esame eCPPT

- **Path da memorizzare**: `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`.
- Variabile dinamica equivalente: `$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`.
- **AppData è hidden** — sempre accessibile via CLI anche se non visibile in Explorer.
- È l'**equivalente Windows** di `~/.bash_history` su Linux.
- **Triade Locally Stored Credentials Windows** (chiude la subsection):
  1. **Unattended files** (deploy artifacts)
  2. **Credential Manager** (`cmdkey`)
  3. **PowerShell History** (`ConsoleHost_history.txt`) ← questo video
- All'esame: se vedi una macchina Windows compromessa con shell low-priv → **controlla SEMPRE** questo file.

## Collegamenti con altri video

- Precedente: [[06_Windows Credential Manager]]
- Prossimo: [[08_Exploiting Insecure Service Permissions]] — nuova subsection (service privesc).
- Vettore parallelo Linux: [[014_Locally Stored Credentials]] (file di config con password).
- Strumento automatico che rileva history (parzialmente): [[03_Privilege Escalation with PowerUp]], [[04_Privilege Escalation with Privesc Check]].
