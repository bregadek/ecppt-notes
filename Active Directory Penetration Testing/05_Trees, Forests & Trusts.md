# 05 — Trees, Forests & Trusts (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 5/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_Trees, Forests & Trusts.txt](05_Trees, Forests & Trusts.txt) · [05_Trees, Forests & Trusts.srt](05_Trees, Forests & Trusts.srt)

## Concetti chiave

- **Domain** = boundary amministrativo, di replicazione e di autenticazione/autorizzazione per un set di oggetti.
- **Tree** = gerarchia di domini che **condividono un namespace contiguo** con il parent (es. `contoso.com`, `emea.contoso.com`, `na.contoso.com`).
- **Forest** = collezione di uno o più tree; **condivide schema, configuration partition, global catalog**, e i gruppi **Enterprise Admins / Schema Admins**.
- **Trust** = meccanismo che permette agli utenti di un dominio di accedere alle risorse di un altro dominio.
- Tipi di trust trattati: **directional** (trusting → trusted) e **transitive** (estesa oltre due domini).
- I domini child in un tree creano di default un **two-way transitive trust** col parent.
- Tutti i domini di una forest si fidano tra loro; un **forest trust** estende la fiducia fuori dalla foresta.

## Spiegazione approfondita

### Domain (revisione gerarchica)
Un dominio è simultaneamente:
- **Administrative boundary** — applichi policy a un gruppo di oggetti.
- **Replication boundary** — i DC replicano i dati all'interno del dominio.
- **Authentication/authorization boundary** — limita lo scope d'accesso alle risorse.

Esempi: `contoso.com`, `foobank.inc` (quello del nostro lab).

### Tree (Domain Tree)
Un tree è una **gerarchia di domini in AD DS** che **condividono un namespace contiguo** con un parent domain. 

Esempio:
```
contoso.com                      ← parent / root
├── emea.contoso.com             ← child (Europe/Middle East/Africa)
└── na.contoso.com               ← child (North America)
```
Caratteristiche:
- Namespace **contiguo** col parent (suffisso DNS).
- I child possono avere ulteriori child (nesting illimitato).
- Per default ogni child crea un **two-way transitive trust** col parent.

### Forest
Una forest è una **collezione di uno o più tree**. Anche un singolo dominio è tecnicamente una forest a un solo tree. Tutti i domini in una forest condividono:
- **Schema comune** (definizione classi/attributi AD).
- **Configuration partition comune**.
- **Global Catalog comune** per le ricerche cross-domain.
- **Trust automatici** tra tutti i domini della forest.
- I gruppi **Enterprise Admins** e **Schema Admins** sono forest-wide.

Una forest può ospitare tree con namespace **non contigui** (es. `contoso.com` + `fabrikam.com` nella stessa forest).

### Trust
Un trust è il meccanismo che consente a utenti di un dominio di accedere a risorse di un altro dominio.

#### Trust direzionali (one-way vs two-way)
- **Trusting domain** = quello che concede l'accesso alle sue risorse.
- **Trusted domain** = quello i cui utenti vengono accettati.
- La direzione di **trust** va da **trusting → trusted** (il trusting "si fida del" trusted).
- Le **richieste di accesso** vanno invece in direzione opposta (gli utenti del trusted accedono al trusting).
- Un trust **two-way** è la combinazione di due trust one-way reciproci.

#### Trust transitive
La relazione si estende oltre i due domini iniziali. Se A si fida di B e B si fida di C, allora con un trust transitivo A si fida implicitamente anche di C. **Tutti i trust interni a una forest sono transitive e two-way** by default.

#### Forest trust
Estende la fiducia **fuori dalla forest**. Permette agli utenti di una forest di accedere a risorse di un'altra forest. Importante in ottica offensiva: i forest trust sono il modo principale per fare lateral movement cross-forest.

### Sintesi visiva
```
Forest
├── Tree 1 (contoso.com)
│   ├── contoso.com           (root domain)
│   ├── emea.contoso.com      (child)
│   └── na.contoso.com        (child)
└── Tree 2 (fabrikam.com)
    └── fabrikam.com
```
Tutti i domini di questa forest si trustano a vicenda (transitive). Un forest trust con un'altra forest esterna permetterebbe ulteriori scenari di accesso cross-forest.

## Comandi & strumenti

N/A in questo video — è una panoramica concettuale, nessuna demo né comando.

## Esempi pratici

N/A in questo video.

## Punti d'attenzione per l'esame eCPPT

- **Domain vs Tree vs Forest** — differenza netta da memorizzare:
  - Domain = singola unità admin/replication/auth.
  - Tree = gerarchia di domini con namespace **contiguo**.
  - Forest = uno o più tree (namespace anche **non contigui**) con schema/config/GC condivisi.
- **Schema, Configuration partition, Global Catalog**: condivisi a livello di **forest**, non di tree.
- I gruppi **Enterprise Admins** e **Schema Admins** sono **forest-wide** (Domain Admins è invece domain-wide — collegamento al video 02).
- **Tutti i trust intra-forest sono two-way transitive di default**. Una domanda d'esame classica: "se A.contoso.com si fida di emea.contoso.com e quest'ultimo di na.contoso.com, A si fida di na?" → Sì, per transitività.
- **Direzione del trust vs direzione dell'accesso**: il trust va da trusting → trusted, l'accesso degli utenti va in senso opposto. Trick frequente nelle domande.
- **Forest trust** = unico modo per condividere risorse fuori dalla forest. Non è transitivo automaticamente verso altre forest collegate dalla forest target.
- Compromettere un **Enterprise Admin** dà controllo su **tutta la forest**, mentre compromettere un Domain Admin dà controllo solo su **un dominio**.
- Il **Global Catalog** memorizza un subset replicato di tutti gli oggetti della forest — ricercabile cross-domain. Tipicamente ospitato sui DC e accessibile via LDAP sulla porta 3268.

## Collegamenti con altri video

- Precedente: [[04_Active Directory Authentication]]
- Prossimo: [[06_AD Penetration Testing Methodology]] — inizia la parte offensive.
- Enumeration dei trust: [[08_AD Enumeration_ BloodHound]] · [[09_AD Enumeration_ PowerView]]
- Persistence forest-wide: [[014_AD Persistence_ Golden Ticket]] (forgia TGT trust-wide)
