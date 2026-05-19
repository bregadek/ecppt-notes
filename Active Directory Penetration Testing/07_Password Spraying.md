# 07 — Password Spraying (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 7/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_Password Spraying.txt](07_Password Spraying.txt) · [07_Password Spraying.srt](07_Password Spraying.srt)

## Concetti chiave

- **Password Spraying** = provare **una password (o pochissime) contro molti utenti**, opposto di brute force / credential stuffing.
- Strategia per **evadere il lockout**: 1 password per account, attesa tra i tentativi (rispetta l'**observation window** della policy).
- Target tipici: VPN, webmail, SSO, **Active Directory**.
- Lab: assumed breach — RDP su Windows Server 2012 come utente `student`.
- Tool usati: **PowerView** (`Get-DomainUser`) per username enumeration, **DomainPasswordSpray** per il spray vero e proprio.
- Risultato dimostrato: utente `Johnny` aveva password `123456`.

## Spiegazione approfondita

### Cos'è il Password Spraying
Tecnica con cui l'attaccante prova ad autenticarsi usando **una lista curata di password comuni** (o **una sola password**) contro **molti account**. Le password possono venire da:
- Liste di password comuni (`rockyou.txt`, top-100).
- Password "stagionali" o aziendali probabili (`Summer2024!`, `<Company>123`).
- Credenziali ottenute da un breach precedente (in quel caso → password reuse attack).

### Differenza con tecniche simili
- **Brute force** = molte password contro **un singolo utente** (rumoroso, scatta il lockout).
- **Credential Stuffing** = password già compromesse contro **utenti specifici** già noti.
- **Password Spraying** = 1 (o poche) password contro **molti utenti** (basso rumore per account → evita lockout).

### Quando si usa
- **Esterno**: VPN, OWA, ADFS, applicazioni SaaS internet-facing.
- **Interno** (caso del lab): attaccante con foothold che cerca di **estendere l'accesso** lateralmente.

### Evitare il lockout
- Provare **una password per account per ciclo**.
- **Attendere** tra cicli (almeno il valore della **observation window** della Domain Password Policy — nel lab è 30 min).
- DomainPasswordSpray legge automaticamente la policy e propone un wait time adeguato.

### Scenario del lab
- Assumed breach: RDP come `student` su una Windows Server 2012 workstation joined al dominio.
- Tool path: `C:\Tools\` (contiene PowerView e altri AD pentesting tools).
- Task:
  1. Enumerare utenti del dominio.
  2. Lanciare il password spray.
  3. Verificare le credenziali ottenute.

### Workflow eseguito nel video
1. Apri PowerShell.
2. Bypass execution policy: `powershell -ep bypass` (in realtà si imposta inline).
3. Import del modulo PowerView.
4. Enumerazione utenti: `Get-DomainUser | Select-Object -ExpandProperty cn | Out-File users.txt`.
5. Import di DomainPasswordSpray.
6. Esecuzione spray: `Invoke-DomainPasswordSpray -UserList users.txt -Password 123456 -Verbose`.
7. Il tool segnala l'observation window (30 min) e chiede conferma → `Y`.
8. Output mostra l'utente `Johnny` come success con la password `123456`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `powershell -ep bypass` | Bypass dell'execution policy per caricare script | Necessario per importare PowerView/DPS |
| `. .\PowerView.ps1` | Import del modulo PowerView | Path: `C:\Tools\...` |
| `Get-DomainUser | Select-Object -ExpandProperty cn | Out-File users.txt` | Estrae lista username del dominio | Funzione PowerView |
| `Get-ADUser -Filter *` | Alternativa con cmdlet ufficiale RSAT | Citato come opzione |
| `net user /domain` | Enumerazione utenti via comando nativo | Citato come opzione |
| `. .\DomainPasswordSpray.ps1` | Import dello script di spraying | Path: `Tools\Scripts\Credentials\` |
| `Invoke-DomainPasswordSpray -UserList users.txt -Password <pwd> -Verbose` | Esegue lo spray | Legge la password policy del dominio |
| **DomainPasswordSpray** (Dafthack) | Tool dedicato | Repo: github.com/dafthack/DomainPasswordSpray |
| **PowerView** | Module PowerShell per enum AD | Trattato nel video 09 |

## Esempi pratici

```powershell
# 1. Bypass execution policy e import PowerView
powershell -ep bypass
. .\PowerView.ps1

# 2. Enumera utenti del dominio e salva in users.txt
Get-DomainUser | Select-Object -ExpandProperty cn | Out-File users.txt
type users.txt

# 3. Import del tool di spray
. .\DomainPasswordSpray.ps1

# 4. Esegui il password spray con la password "123456"
Invoke-DomainPasswordSpray -UserList users.txt -Password 123456 -Verbose

# Output rilevante:
# [*] Password policy observation window: 30 minutes
# [*] Spraying against 6 accounts (Confirm? Y)
# [+] SUCCESS! User:Johnny Password:123456
```

```powershell
# Alternativa: spray con una lista di password (un account per password per ciclo)
Invoke-DomainPasswordSpray -UserList users.txt -PasswordList passwords.txt -Verbose
```

## Punti d'attenzione per l'esame eCPPT

- **Definizione chiave**: password spraying = **1 password / molti utenti**. NON è brute force.
- Sapere **perché** si fa così: evitare il **lockout** della Domain Password Policy.
- L'attributo della policy da rispettare si chiama **observation window** (e **lockout threshold**); DomainPasswordSpray la legge automaticamente.
- Conoscere il flusso PowerView: **`Get-DomainUser`** per estrarre username (l'enumerazione vera si vede nel video 09).
- Conoscere il tool **DomainPasswordSpray** (di Dafthack) e il suo cmdlet `Invoke-DomainPasswordSpray`. Flag chiave: `-UserList`, `-Password`, `-PasswordList`, `-Verbose`.
- Alternative valide menzionate nelle mind maps OCD: **CrackMapExec** (`cme smb <DC_IP> -u userlist -p password`), **SprayHound**, **kerbrute** (non citato nel video ma da conoscere).
- Per evitare lockout reale in engagement: usare **password singola** con attese tra cicli, mai liste lunghe contro tutti i user in rapido fuoco.
- L'enumeration username può essere fatta anche **senza credenziali** via Kerberos pre-auth (kerbrute) — non mostrato qui ma classica domanda.
- Il primo step di un AD pentest sotto assumed breach è quasi sempre: **enumera utenti → spray con password comuni / aziendali**.

## Collegamenti con altri video

- Precedente: [[06_AD Penetration Testing Methodology]]
- Prossimo: [[08_AD Enumeration_ BloodHound]]
- Enumerazione utenti approfondita: [[09_AD Enumeration_ PowerView]]
- Dopo aver trovato valid creds → ulteriori attacchi: [[010_AS-REP Roasting]] · [[011_Kerberoasting]]
