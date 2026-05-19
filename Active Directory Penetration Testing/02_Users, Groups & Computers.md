# 02 — Users, Groups & Computers (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 2/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Users, Groups & Computers.txt](02_Users, Groups & Computers.txt) · [02_Users, Groups & Computers.srt](02_Users, Groups & Computers.srt)

## Concetti chiave

- I **security principals** sono le entità (utenti, gruppi, computer, servizi) a cui Windows assegna permessi via *security descriptors*.
- I **domain users** sono account centralizzati in AD, identificati da username/password e usabili per autenticarsi a qualsiasi macchina joined al dominio.
- I **gruppi** sono di due tipi: **Security Groups** (gestione permessi/accesso risorse) e **Distribution Groups** (solo email, niente security).
- Gruppi predefiniti chiave: **Domain Admins**, **Enterprise Admins**, **Server Operators**, **Backup Operators**, **Account Operators**, **Domain Users**, **Domain Computers**, **Domain Controllers**.
- I **computer accounts** rappresentano le macchine joined al dominio e stabiliscono una *trust relationship* con esso.
- Demo: setup di un DC (Windows Server 2019) → installazione **AD DS** → promozione a Domain Controller → creazione foresta `foobank.inc`.
- L'opzione di account **"Do not require Kerberos preauthentication"** è ciò che espone un utente all'**AS-REP Roasting** (visto nei video successivi).

## Spiegazione approfondita

### Security Principals
Sono entità del Windows Security Infrastructure che possono essere referenziate in ACL e a cui possono essere assegnate permission. Includono **users, groups, computers e services**. Sono centrali nel controllo accessi via security descriptors.

### Domain Users
Rappresentano persone fisiche che interagiscono con la rete. Ogni utente ha un account univoco in AD, identificato da username + password, con attributi accessori (nome completo, email, telefono, dipartimento, job title). Si usano per autenticazione, autorizzazione e management. Gli admin li gestiscono via *Active Directory Users and Computers* (ADUC) o PowerShell.

### Groups
Collezioni di user account, computer account o altri gruppi, usate per applicare permessi/policy in modo aggregato. Due tipologie:
- **Security groups** — gestiscono i permessi sulle risorse di rete. Sono i gruppi rilevanti in ottica offensiva.
- **Distribution groups** — usati solo come liste di distribuzione email; nessuna security permission.

#### Gruppi di sicurezza built-in più rilevanti
- **Domain Admins** — controllo amministrativo completo sul dominio. Creato automaticamente all'installazione del dominio. È il target principale di ogni AD pentest.
- **Enterprise Admins** — privilegi su **tutti** i domini della foresta. Forest-wide.
- **Server Operators** — gestione DC e member server del dominio.
- **Backup Operators** — backup/restore di DC e member server. Spesso sfruttabili per leggere file sensibili.
- **Account Operators** — possono creare/modificare user, group e computer account.
- **Domain Users** — il gruppo di default per tutti gli utenti del dominio.
- **Domain Computers** — tutti i computer joined al dominio.
- **Domain Controllers** — gruppo a cui appartengono tutti i DC.

### Computer Accounts
Ogni macchina joined al dominio (workstation, laptop, server) ha un computer account identificato da un nome univoco. Al join viene stabilita una *trust relationship* sicura che permette al computer di autenticare utenti e accedere a risorse di rete. Gli attributi memorizzati includono nome, OS, ultima login, stato di membership.

### Demo — Setup di un Domain Controller
Il video mostra l'intero workflow di setup, utile per costruirsi un lab personale:

1. Rinomina del computer in `DC01` (System Properties → Change → restart).
2. Server Manager → **Manage → Add Roles and Features**.
3. Role-based or feature-based installation → server pool `DC01` → seleziona **Active Directory Domain Services** → Install.
4. Notifica post-deployment: **Promote this server to a domain controller**.
5. Opzione **Add a new forest** → root domain name `foobank.inc`.
6. Forest/Domain functional level: Windows Server 2016 (default).
7. Domain controller capabilities: **DNS server** + **Global Catalog**.
8. Imposta password **DSRM** (Directory Services Restore Mode) — master password per il recovery del dominio.
9. NetBIOS name: default `FOOBANK`.
10. Path default per **NTDS** database / log / SYSVOL (il famoso `ntds.dit` da cui si dumpano le credenziali).
11. Install → reboot automatico → al riavvio il sistema è DC della foresta `foobank.inc`.

### Demo — Creazione utente e privilege assignment
Da **Active Directory Users and Computers** (Server Manager → Tools → ADUC):
- Si naviga la gerarchia: Domain root → containers (Builtin, Computers, Domain Controllers OU, ForeignSecurityPrincipals, Managed Service Accounts, Users).
- Right click su Users → New → User → first name + last name + UPN (es. `alexis.a@foobank.inc`).
- Si imposta la password, **uncheck "User must change password at next logon"** e check **"Password never expires"** (Alexis sottolinea: *queste sono esattamente le vulnerabilità che cercheremo*).
- Il nuovo utente viene aggiunto a **Domain Admins** via tab *Member Of* → Add → check names → OK.

### Demo — Account Options pericolose
Nelle proprietà account dell'utente, Alexis fa notare due opzioni *security-relevant* da ricordare:
- **"Use only Kerberos DES encryption types"** — encryption deboli.
- **"Do not require Kerberos preauthentication"** → espone l'account all'**AS-REP Roasting**.

### Autenticazione domain vs local
- Login locale: solo username + password.
- Login domain: serve specificare `DOMAIN\username` (es. `FOOBANK\alexis.a`) oppure UPN `alexis.a@foobank.inc`.
- Da PowerShell, `net user` mostra **solo account locali**; `net user /domain` mostra utenti di dominio.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `hostname` | Mostra il nome del computer | Usato per verificare il rename in DC01 |
| `net user` | Lista account **locali** | Non mostra utenti di dominio |
| `net user /domain` | Lista utenti **di dominio** | Funziona solo se la macchina è joined |
| `Get-ADUser -Filter *` | Enumera tutti gli utenti AD via PowerShell | Mostra SID, UPN, object class, DN |
| Server Manager → Add Roles and Features | Installa AD DS | GUI standard di setup |
| ADUC (Active Directory Users and Computers) | Gestione GUI di utenti, gruppi, OU, computer | Server Manager → Tools |
| Group Policy Management | Edita le GPO (es. password policy) | Computer Configuration → Windows Settings → Security Settings → Local Policies |

## Esempi pratici

```powershell
# Verifica stato locale prima del setup AD
hostname            # DC01
net user            # solo account locali
net user /domain    # nessun dominio configurato (errore o vuoto)

# Dopo aver promosso il server a DC
Get-ADUser -Filter *
# Ritorna Administrator e i domain users creati (es. alexis.a) con SID e UPN
```

```text
# Login interattivo via RDP come domain user
Username: FOOBANK\alexis.a       (oppure alexis.a@foobank.inc)
Password: <password>
```

## Punti d'attenzione per l'esame eCPPT

- Sapere cosa sono i **security principals** e che includono **users, groups, computers, services**.
- Distinguere **Security Group** da **Distribution Group** — solo i primi gestiscono permessi.
- Memorizzare i gruppi privilegiati built-in e cosa permettono:
  - **Domain Admins** = full control sul dominio.
  - **Enterprise Admins** = full control su **tutta la foresta**.
  - **Backup Operators** spesso target privesc (può leggere SAM/SYSTEM).
  - **Account Operators** può creare/modificare account → utile per persistence.
- L'opzione **"Do not require Kerberos preauthentication"** è il prerequisito per **AS-REP Roasting** — collegamento diretto con il video 010.
- Differenza autenticazione locale (`username`) vs dominio (`DOMAIN\user` o UPN `user@domain`).
- `net user` vs `net user /domain` — domanda classica.
- Il file **`ntds.dit`** (database AD) sta nel path configurato in fase di promozione → è il file da target nei dump credenziali (es. `secretsdump.py`, `ntdsutil`).
- Differenza tra **container** (Users, Computers) e **OU** (Domain Controllers è una OU, non un container — vedi video 03).

## Collegamenti con altri video

- Precedente: [[01_Introduction]]
- Prossimo: [[03_Organizational Units (OUs)]] — estende la gerarchia di AD.
- Authentication: [[04_Active Directory Authentication]]
- L'opzione preauth → [[010_AS-REP Roasting]]
- Enumerazione di utenti/gruppi: [[08_AD Enumeration_ BloodHound]] · [[09_AD Enumeration_ PowerView]]
