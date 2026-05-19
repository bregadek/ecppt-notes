# 09 — AD Enumeration: PowerView (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 9/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_AD Enumeration_ PowerView.txt](09_AD Enumeration_ PowerView.txt) · [09_AD Enumeration_ PowerView.srt](09_AD Enumeration_ PowerView.srt)

## Concetti chiave

- **PowerView** è uno script PowerShell (parte di PowerSploit) per **enumerazione AD manuale** via LDAP — l'equivalente "a mano" di BloodHound.
- Sapere fare enum manuale è fondamentale: i tool automatici nascondono **come** l'info viene ottenuta.
- Categorie di enum coperte: **Domain info**, **Domain Policy**, **Domain Controllers**, **Users**, **Computers**, **Groups**, **Shares**, **GPOs**, **OUs**, **Trusts**, **Forest**, **ACL/ACE**, **Kerberoastable & AS-REP roastable users**.
- Lab: stesso ambiente del video BloodHound (~495 utenti, dominio `research.security.local` + forest trust con `tech.local`).
- Comandi chiave: `Get-Domain`, `Get-DomainPolicy`, `Get-DomainController`, `Get-DomainUser`, `Get-NetComputer`, `Get-NetGroup`, `Find-DomainShare`, `Get-NetGPO`, `Get-NetOU`, `Get-NetDomainTrust`, `Get-NetForestTrust`, `Get-ObjectAcl`, `Find-InterestingDomainAcl`.

## Spiegazione approfondita

### Setup
```powershell
powershell -ep bypass
cd C:\Tools\
. .\PowerView.ps1
```

### Domain info
```powershell
Get-Domain                              # info dominio corrente
Get-Domain -Domain security.local       # info parent domain
Get-DomainSID                           # SID del dominio
```
Output utile: nome dominio, DC name (`prod.research.security.local`), domain functional level (es. 2012R2), parent.

### Domain Policy
```powershell
Get-DomainPolicy                                  # policy completa
(Get-DomainPolicy)."System Access"                # solo password/system access
(Get-DomainPolicy)."Kerberos Policy"              # solo Kerberos
```
Cosa cercare: `MinimumPasswordLength` basso (insecure), `ClearTextPassword=0`, `MaxTicketAge`, `MaxRenewAge`.

### Domain Controllers
```powershell
Get-DomainController
Get-DomainController -Domain security.local
```

### User enumeration
```powershell
Get-DomainUser                                                              # tutti gli utenti
Get-DomainUser | Select SamAccountName, ObjectSID                           # filter compatto
Get-DomainUser -Identity devon_hood                                         # singolo utente
Get-DomainUser -Identity devon_hood -Properties displayname,memberof,objectsid,useraccountcontrol | Format-List
```

### Computer enumeration
```powershell
Get-NetComputer                                                # tutti i computer
Get-NetComputer | Select Name                                  # solo nomi
Get-NetComputer -Domain security.local | Select CN, OperatingSystem
```

### Group enumeration
```powershell
Get-NetGroup                                                   # tutti i gruppi
Get-NetGroup | Select Name                                     # solo nomi
Get-NetGroup "Domain Admins"                                   # dettagli gruppo specifico
Get-NetGroupMember "Domain Admins" | Select MemberName         # membri di Domain Admins
Get-NetGroup -UserName Elise_Guzman | Select Name              # gruppi di cui un utente è membro
```

### Share enumeration
```powershell
Find-DomainShare -ComputerName prod.research.security.local -Verbose
Find-DomainShare -ComputerName prod.research.security.local -CheckShareAccess   # solo share leggibili
Get-NetShare                                                                     # share locali
```

### GPO / OU
```powershell
Get-NetGPO | Select DisplayName
Get-NetOU | Select Name, DistinguishedName
```

### Trust & Forest
```powershell
Get-NetDomainTrust                                # trust del dominio corrente
Get-NetForest                                     # info foresta corrente
Get-NetForestTrust                                # mappa forest trust
Get-NetForestDomain                               # domini nella foresta corrente
Get-NetForestDomain -Forest tech.local            # domini in una foresta trusted
Get-DomainTrustMapping                            # mappa completa trust
```
Nel lab viene mostrato un **bi-directional forest trust** tra `security.local` e `tech.local`.

### ACL / ACE enumeration
ACL = Access Control List, contiene ACE (Access Control Entry). Ogni ACE = security principal + permessi + flag inheritance/explicit.
```powershell
Get-ObjectAcl -SamAccountName "Users" -ResolveGUIDs

Find-InterestingDomainAcl -ResolveGUIDs |
  Select IdentityReferenceName, ObjectDN, ActiveDirectoryRights
```
`Find-InterestingDomainAcl` filtra automaticamente le ACE "interessanti" per un attaccante (WriteDACL, GenericAll, ForceChangePassword, ecc.).

### Kerberoastable & AS-REP Roastable
```powershell
# Kerberoastable (utenti con SPN)
Get-DomainUser -SPN | Select SamAccountName, ServicePrincipalName

# AS-REP Roastable (utenti con DONT_REQ_PREAUTH)
Get-DomainUser -PreauthNotRequired | Select SamAccountName, UserAccountControl
```
Queste due query producono direttamente le liste di target per i video 010 e 011.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `. .\PowerView.ps1` | Import del modulo | Da `C:\Tools\` |
| `Get-Domain` | Info dominio corrente | |
| `Get-DomainSID` | SID dominio | |
| `Get-DomainPolicy` | Password/Kerberos policy | Usa `.System Access` / `."Kerberos Policy"` |
| `Get-DomainController` | Lista DC | `-Domain <name>` per altri domini |
| `Get-DomainUser` | Enum utenti | `-Identity`, `-Properties`, `-SPN`, `-PreauthNotRequired` |
| `Get-NetComputer` | Enum computer | `-Domain`, `Select Name,OperatingSystem` |
| `Get-NetGroup` | Enum gruppi | Filtra per nome con `"Domain Admins"` |
| `Get-NetGroupMember` | Membri di un gruppo | Target classico: Domain Admins |
| `Find-DomainShare` | Share di rete | `-ComputerName`, `-CheckShareAccess` |
| `Get-NetShare` | Share locali host | |
| `Get-NetGPO` | Enum GPO | `Select DisplayName` |
| `Get-NetOU` | Enum OU | |
| `Get-NetDomainTrust` | Trust del dominio | |
| `Get-NetForest` / `Get-NetForestTrust` / `Get-NetForestDomain` | Enum foresta e trust forest-wide | |
| `Get-DomainTrustMapping` | Mappa completa trust | |
| `Get-ObjectAcl -ResolveGUIDs` | ACL di un oggetto | |
| `Find-InterestingDomainAcl -ResolveGUIDs` | ACE potenzialmente abusabili | Equivalente concettuale agli edge "abuse" di BloodHound |

## Esempi pratici

```powershell
# Workflow completo enumerazione "minima ma efficace"

# 0. Setup
powershell -ep bypass
. .\PowerView.ps1

# 1. Mappare ambiente
Get-Domain
Get-DomainController
Get-DomainPolicy | Select -ExpandProperty "System Access"

# 2. Trovare i target ad alto privilegio
Get-NetGroupMember "Domain Admins" | Select MemberName
Get-NetGroupMember "Enterprise Admins" | Select MemberName

# 3. Trovare utenti attaccabili via Kerberos
Get-DomainUser -SPN | Select SamAccountName, ServicePrincipalName
Get-DomainUser -PreauthNotRequired | Select SamAccountName

# 4. Mappa trust (per cross-domain / cross-forest)
Get-NetDomainTrust
Get-NetForestTrust
Get-DomainTrustMapping

# 5. Cercare ACL abusabili
Find-InterestingDomainAcl -ResolveGUIDs |
  Select IdentityReferenceName, ObjectDN, ActiveDirectoryRights

# 6. Share leggibili (potenziale data exposure)
Find-DomainShare -ComputerName prod.research.security.local -CheckShareAccess
```

## Punti d'attenzione per l'esame eCPPT

- **PowerView è il "manuale" di BloodHound** — quando l'esame ti chiede "come trovi gli utenti Kerberoastable senza BloodHound" → `Get-DomainUser -SPN`.
- **`-SPN`** = filtro per Kerberoastable. **`-PreauthNotRequired`** = filtro per AS-REP Roastable. Da memorizzare a memoria.
- Differenza naming `Get-Domain*` (oggetti AD via LDAP, PowerView v3) vs `Get-Net*` (legacy alias). Entrambi funzionano e sono usati nel video.
- `Get-NetGroupMember "Domain Admins"` = primo comando in ogni AD pentest.
- **Domain Policy** importanti: `MinimumPasswordLength`, `ClearTextPassword`, `MaxTicketAge` (Kerberos).
- **ACL enumeration** — concetto da conoscere:
  - **ACL** = lista ordinata di **ACE**.
  - **ACE** = (security principal, permessi, allow/deny, inherited/explicit).
  - `Find-InterestingDomainAcl` trova ACE come **GenericAll, WriteDACL, WriteOwner, ForceChangePassword, GetChanges/GetChangesAll** — ognuna abusabile per privilege escalation.
- **Trust enumeration** — sapere distinguere domain trust (`Get-NetDomainTrust`) da forest trust (`Get-NetForestTrust`). Il lab mostra un **bi-directional forest trust** con `tech.local`.
- **`Find-DomainShare -CheckShareAccess`** = solo share su cui il current user ha read access (utile per evitare denied noise).
- L'enumeration **non richiede privilegi alti**: un domain user qualsiasi può leggere via LDAP la quasi totalità degli oggetti AD. È il vero punto debole di AD.
- Comando per UAC flags: `Get-DomainUser -Properties UserAccountControl` → contiene flag come `DONT_REQ_PREAUTH`, `TRUSTED_FOR_DELEGATION`, ecc.

## Collegamenti con altri video

- Precedente: [[08_AD Enumeration_ BloodHound]] — versione automatica.
- Prossimo: [[010_AS-REP Roasting]] — usa direttamente `Get-DomainUser -PreauthNotRequired`.
- [[011_Kerberoasting]] — usa direttamente `Get-DomainUser -SPN`.
- ACL abusabili → vedere edge graph: [[08_AD Enumeration_ BloodHound]]
- Methodology: [[06_AD Penetration Testing Methodology]]
