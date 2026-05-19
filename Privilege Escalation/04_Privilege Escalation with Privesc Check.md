# 04 — Privilege Escalation with PrivescCheck (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 4/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Privilege Escalation with Privesc Check.txt](04_Privilege Escalation with Privesc Check.txt) · [04_Privilege Escalation with Privesc Check.srt](04_Privilege Escalation with Privesc Check.srt)

## Concetti chiave

- **PrivescCheck** è uno script PowerShell **alternativo a PowerUp** per identificare automaticamente vulnerabilità di privesc su Windows.
- **Indipendente da PowerSploit** (sviluppo separato, autore: itm4n).
- Funzione principale: **`Invoke-PrivescCheck`**.
- Genera un **report completo** con severity (low/medium/high) per ogni potenziale vulnerabilità.
- Più **comprensivo** di PowerUp (più check) ma **più lento** (1-2 min vs pochi secondi).

## Spiegazione approfondita

### Categorie di check eseguite
- Hijackable DLLs
- BitLocker status
- Credential Guard configuration
- **Locally stored credentials** (incluso WinLogon → `CredsWinlogon`)
- Service permissions
- Registry autoruns
- Scheduled tasks
- Path inquoting
- Patch level e altro

### Workflow del lab
1. Accesso al target come `student` (low-priv).
2. Verifica privilegi (`whoami /priv`, `net localgroup administrators`).
3. Navigazione a `PrivescCheck` directory.
4. Esecuzione one-liner: bypass EP + import + invoke.
5. Lettura del report → trovata vulnerabilità `CredsWinlogon` severity **medium** (credenziali WinLogon clear-text).
6. Sfruttamento con `runas /user:administrator cmd`.

### Confronto PowerUp vs PrivescCheck

| Aspetto | PowerUp | PrivescCheck |
|---|---|---|
| Framework | PowerSploit | Standalone |
| Funzione | `Invoke-PrivescAudit` | `Invoke-PrivescCheck` |
| Velocità | Veloce (secondi) | Lento (1-2 min) |
| Output | Lista vulnerabilità | Report dettagliato con severity |
| Preferenza istruttore | Sì (Alexis lo usa di default) | Alternativa |

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `whoami /priv` | Verifica token privileges |
| `net localgroup administrators` | Lista admin locali |
| `powershell -ep bypass` | Bypass execution policy |
| `. .\PrivescCheck.ps1; Invoke-PrivescCheck` | Import + esecuzione one-liner |
| `runas.exe /user:administrator cmd` | Elevazione locale con credenziali trovate |

## Esempi pratici

```powershell
# Verifica utente non privilegiato
whoami
whoami /priv
net localgroup administrators

# Esecuzione PrivescCheck (one-liner)
cd C:\Users\student\Desktop\PrivescCheck
powershell -ep bypass
. .\PrivescCheck.ps1; Invoke-PrivescCheck

# Output rilevante:
# [CredsWinlogon] Severity: Medium
# DefaultUserName: Administrator
# DefaultPassword: <cleartext>

# Sfruttamento
runas.exe /user:administrator cmd
# inserire password
whoami     # administrator
whoami /priv
```

## Punti d'attenzione per l'esame eCPPT

- **PrivescCheck** è il "backup" di PowerUp: se uno script non trova nulla, prova l'altro.
- Funzione esatta: **`Invoke-PrivescCheck`** (NON `Invoke-PrivescAudit`).
- È **standalone** — NON serve PowerSploit installato.
- Test interessante da ricordare: **`CredsWinlogon`** (stesso vettore visto nel video 03).
- Il report mostra severity → utile per **prioritizzare** vettori in scenari complessi.
- L'esame eCPPT può presentare entrambi gli script: sapere quale comando esegue ciascuno è essenziale.
- Limitazione: lo script **non sfrutta**, identifica soltanto → il pen tester deve poi decidere il vettore.

## Collegamenti con altri video

- Precedente: [[03_Privilege Escalation with PowerUp]] — strumento equivalente.
- Prossimo: [[05_ Unattended Installation Files]] — primo vettore manuale di credential reuse.
- Tutti i video successivi della sezione Windows: PrivescCheck può identificare le stesse vulnerabilità (services, autoruns, DLL, ecc.).
