# 08 — AD Enumeration: BloodHound (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 8/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_AD Enumeration_ BloodHound.txt](08_AD Enumeration_ BloodHound.txt) · [08_AD Enumeration_ BloodHound.srt](08_AD Enumeration_ BloodHound.srt)

## Concetti chiave

- **BloodHound** è una single-page web app (Electron) basata su **LinkurIous**, alimentata da un database **Neo4j** e popolata da **data collector** (SharpHound) in C# o PowerShell.
- Usa **graph theory** per evidenziare relazioni di privilegio nascoste in AD e calcolare **shortest path** verso Domain Admin (o altri target).
- Workflow: **SharpHound** raccoglie dati → genera **archivio ZIP** → si carica nella GUI BloodHound → query pre-built dal pannello **Analysis**.
- Collection method `All` raccoglie tutte le info (gruppi, sessioni, ACL, trust, GPO, ecc.).
- Credenziali default Neo4j del lab: `neo4j / Password@123`.
- Query pre-built rilevanti: *Find all Domain Admins*, *Map Domain Trusts*, *List all Kerberoastable Accounts*, *List all AS-REP Roastable Users*, *Find Principals with DCSync Rights*, *Shortest Path from Owned Principals*.

## Spiegazione approfondita

### Cos'è BloodHound
SPA JavaScript (Electron + LinkurIous) con **Neo4j** come backend a grafo. Gli **ingester** (SharpHound) enumerano l'AD via LDAP/SMB/RPC e producono un set di file JSON/CSV zippati. La GUI ingerisce lo zip e applica query Cypher per disegnare grafi che mostrano:
- Relazioni di group membership.
- Sessioni utente attive sui sistemi.
- ACL/ACE e permessi delegati.
- Trust intra/inter-forest.
- Path di attacco verso un target (tipicamente DA).

Sia red team che blue team lo usano: i primi per trovare il path, i secondi per chiuderlo.

### Architettura
```
[SharpHound (C#/PS) collector]  ── enumera AD ──>  ZIP (JSON)
                                                     │
                                                     ▼
                                  [BloodHound GUI] ── ingest ──> [Neo4j DB]
                                                     │
                                                     ▼
                                          Query Cypher / Analysis tab
```

### Workflow eseguito nel lab
1. **Cartella tool**: `C:\Tools\BloodHound\`.
2. Collector path: `BloodHound\Resources\app\Collectors\` (contiene `SharpHound.exe` e `SharpHound.ps1`).
3. Bypass execution policy: `Set-ExecutionPolicy Bypass` (o `powershell -ep bypass`).
4. Import del collector PowerShell: `. .\SharpHound.ps1`.
5. Esecuzione: `Invoke-BloodHound -CollectionMethod All`.
6. Output: file **`.zip`** con timestamp nella directory corrente.
7. Avvio GUI: `BloodHound.exe`.
8. Login Neo4j: `neo4j` / `Password@123`.
9. **Upload Data** (icona a destra) → seleziona lo zip.
10. Attendi import → **Database Info → Refresh** per aggiornare stats.

### Query d'analisi mostrate
Dal tab **Analysis** (pre-built queries):
- **Find all Domain Admins** — output: utenti con DA (es. Elise Guzman, Administrator, ecc.).
- **Map Domain Trusts** — visualizza i trust tra domini.
- **List all Kerberoastable Accounts** — utenti con SPN (target per Kerberoasting). Click sul nodo → si vede il **SPN** specifico (es. servizio Kafka).
- **List all AS-REP Roastable Users** — utenti con `DONT_REQ_PREAUTH=True` (target AS-REP Roasting).
- **Find Principals with DCSync Rights** — utenti con `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`; prerequisito per **DCSync** (preludio al Golden Ticket).
- **Shortest Path to Domain Admins** — calcola il path più corto verso DA.
- **Shortest Paths from Kerberoastable Users / from Owned Principals** — utile dopo aver compromesso un utente.

### Marking utenti come "owned"
Right-click su un nodo utente → **Mark User as Owned**. Questo abilita le query *Shortest Paths from Owned Principals*, fondamentali per scoprire il prossimo step verso DA dal proprio foothold attuale.

### Node Properties
Cliccando su un nodo si vedono:
- `pwdlastset`, `lastlogon` — utili per identificare account stagnanti.
- `samaccountname`, `domain SID`.
- `kerberoastable`, `asrep_roastable` — flag booleani.
- Group membership (diretta + foreign).
- SPN list (per utenti con SPN).

### Edge tipici nel grafo
(Non spiegati esplicitamente nel video ma fondamentali da conoscere): `MemberOf`, `HasSession`, `AdminTo`, `CanRDP`, `GenericAll`, `WriteOwner`, `WriteDACL`, `GetChanges` / `GetChangesAll` (DCSync), `AllowedToDelegate`, `ForceChangePassword`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Set-ExecutionPolicy Bypass` o `powershell -ep bypass` | Permette di caricare `.ps1` non firmati | |
| `. .\SharpHound.ps1` | Import del collector PowerShell | Path: `BloodHound\Resources\app\Collectors\` |
| `Invoke-BloodHound -CollectionMethod All` | Esegue la raccolta completa | Output: zip con JSON |
| `SharpHound.exe -c All` | Equivalente C# del comando sopra | (Alternativa, citata) |
| `BloodHound.exe` | Avvia la GUI | Cartella `BloodHound\` |
| Credenziali Neo4j default lab | `neo4j` / `Password@123` | Specificate nella lab doc |

## Esempi pratici

```powershell
# 1. Setup esecuzione
powershell -ep bypass
cd C:\Tools\BloodHound\BloodHound\Resources\app\Collectors
. .\SharpHound.ps1

# 2. Esecuzione collector
Invoke-BloodHound -CollectionMethod All
# Output esempio: 20250101120000_BloodHound.zip

# 3. Avvio GUI (separato)
cd C:\Tools\BloodHound\BloodHound
.\BloodHound.exe
# Login: neo4j / Password@123
# Upload Data -> seleziona lo zip generato

# 4. Query utili (dal tab Analysis):
#   - Find all Domain Admins
#   - List all Kerberoastable Accounts
#   - List all AS-REP Roastable Users
#   - Find Principals with DCSync Rights
#   - Shortest Paths to Domain Admins
#   - Shortest Paths from Owned Principals
```

```text
# Collection methods di SharpHound (quelli utili):
#   All           - tutto (default per pentest)
#   Default       - group membership + sessioni + trust
#   Session       - solo sessioni utente
#   ACL           - permessi su oggetti
#   Trusts        - solo trust di dominio
#   LoggedOn      - sessioni privilegiate (richiede admin)
```

## Punti d'attenzione per l'esame eCPPT

- **BloodHound componenti**: GUI Electron + Neo4j DB + SharpHound collector. Domanda classica: "che database usa BloodHound?" → Neo4j.
- Il **collection method `All`** è quello che vuoi nella maggior parte dei casi.
- L'output di SharpHound è un **archivio ZIP** che si carica via **Upload Data** nella GUI.
- **Path query fondamentali da conoscere**:
  - *Shortest Paths to Domain Admins* (target finale).
  - *Shortest Paths from Owned Principals* (dopo aver marcato user come owned).
  - *Find all Domain Admins* (chi è DA oggi).
- **Identificare attacchi possibili** via BloodHound:
  - *List all Kerberoastable Accounts* → utenti con **SPN** → target di **Kerberoasting** (video 011).
  - *List all AS-REP Roastable Users* → utenti con **`DONT_REQ_PREAUTH`** → target di **AS-REP Roasting** (video 010).
  - *Find Principals with DCSync Rights* → utenti che possono fare **DCSync** (preludio a **Golden Ticket** — video 014).
- **DCSync rights** = `DS-Replication-Get-Changes` + `DS-Replication-Get-Changes-All`. Memorizza i nomi.
- **Mark as Owned**: il flag che dice a BloodHound da quali nodi calcolare i path "da utente compromesso".
- Differenza con **PowerView** (video 09): BloodHound è **automatizzato e grafico**; PowerView è **manuale, query per query**.
- Edge BloodHound da conoscere almeno a livello concettuale: `AdminTo`, `HasSession`, `MemberOf`, `GenericAll`, `WriteDACL`, `GetChanges`/`GetChangesAll`.

## Collegamenti con altri video

- Precedente: [[07_Password Spraying]]
- Prossimo: [[09_AD Enumeration_ PowerView]] — l'equivalente manuale di BloodHound.
- Target identificati con BloodHound → attacchi: [[010_AS-REP Roasting]] · [[011_Kerberoasting]]
- DCSync rights → [[014_AD Persistence_ Golden Ticket]]
- Methodology dove si colloca l'enumeration: [[06_AD Penetration Testing Methodology]]
