# 03 — Organizational Units (OUs) (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 3/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Organizational Units (OUs).txt](03_Organizational Units (OUs).txt) · [03_Organizational Units (OUs).srt](03_Organizational Units (OUs).srt)

## Concetti chiave

- Le **OU** sono container gerarchici che organizzano utenti, gruppi, computer e altre OU dentro un dominio AD.
- Criteri tipici di organizzazione: **dipartimentale**, **geografico**, **amministrativo**.
- Le OU consentono **delegazione amministrativa** e **linking di GPO** mirate solo agli oggetti contenuti.
- Differenza **OU vs Security Group**: le OU organizzano e supportano GPO/delegation; i security group gestiscono **permessi**.
- Le OU **sono gerarchiche/nestate**; i security group sono tipicamente **flat** (anche se tecnicamente nestabili).
- I cmdlet `Get-ADOrganizationalUnit`, `Get-ADGroup`, `Get-ADUser` permettono di enumerare OU, gruppi e utenti — base per la fase di enumeration AD.

## Spiegazione approfondita

### Cos'è una Organizational Unit
Una OU è un **container** dentro un dominio AD usato per **organizzare** oggetti (user, computer, group, altre OU) in una struttura gerarchica. Non è solo cosmetica: è l'unità di **delegazione amministrativa** e il punto di **ancoraggio delle GPO**. Esempio classico: OU `Employees` con sotto `Finance`, `HR`, `Developers`, ognuna con i propri utenti e computer.

### A cosa servono
1. **Organizzazione logica** secondo struttura aziendale.
2. **Linking di GPO** — una policy applicata su una OU vale solo per gli oggetti di quella OU (non per gli oggetti della OU parent o sorella).
3. **Delegazione amministrativa** — si può dare a un utente il diritto di gestire solo una specifica OU.
4. **Permission scoping** — assegnare permessi mirati a un sottoinsieme di oggetti.

### OU vs Security Group (differenza chiave)
| Aspetto | Organizational Unit | Security Group |
|---|---|---|
| Scopo | Organizzare oggetti, applicare GPO, delegare admin | Controllo accessi e permessi |
| Struttura | Gerarchica/nestata nativa | Tipicamente flat |
| Contiene | User, computer, group, altre OU | User, computer, altri group |
| GPO linkable | Sì | No |
| Membership ereditata | Sì (oggetti dentro OU) | No (devi aggiungere manualmente) |

### Demo — Creazione gerarchia OU
Nel video Alexis costruisce questa gerarchia in ADUC:
```
foobank.inc
└── Employees (OU)
    ├── Finance (OU)
    │   └── John Doe (user)
    └── HR (OU)
```
Da **ADUC**: right-click sul dominio → New → Organizational Unit → check **"Protect container from accidental deletion"** → OK. Poi si annida `Finance` e `HR` dentro `Employees`.

### Demo — Link di una GPO a una OU
1. Server Manager → Tools → **Group Policy Management**.
2. Right-click su OU `Finance` → **Create a GPO in this domain and Link it here** → nome `Finance GPO`.
3. Edit della GPO → Computer Configuration → Windows Settings → Security Settings → Account Policies → Password Policy → **Minimum password length** = 10.
4. Right-click GPO → **Enforced**.
5. Forzare il refresh: `gpupdate /force` (richiede admin).
6. Verifica: creando un nuovo utente nella OU Finance con password < 10 char l'operazione fallisce con violazione policy.

Punto chiave: la GPO si applica **solo agli oggetti in `Finance`**, non a quelli di `Employees` o `HR`.

### Distinguished Name (DN) e gerarchia
Il DN di `John Doe` riflette la gerarchia OU:
```
CN=John Doe,OU=Finance,OU=Employees,DC=foobank,DC=inc
```
Leggendo da sinistra a destra: oggetto → OU di appartenenza diretta → OU parent → componenti dominio. Pattern fondamentale per enumeration e LDAP query.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `Get-ADUser -Filter *` | Enumera tutti gli utenti AD | Mostra DN con catena OU |
| `Get-ADGroup -Filter *` | Enumera tutti i gruppi AD | |
| `Get-ADOrganizationalUnit -Filter *` | Enumera tutte le OU | Mostra `LinkedGroupPolicyObjects` |
| `gpupdate /force` | Forza il refresh delle GPO sul sistema | Serve admin |
| ADUC (Active Directory Users and Computers) | GUI per creare/gestire OU | Tools → Active Directory Users and Computers |
| Group Policy Management Console (GPMC) | Crea, linka, edita GPO | Tools → Group Policy Management |

## Esempi pratici

```powershell
# Enumera utenti e nota la catena OU nel DN
Get-ADUser -Filter *
# Esempio output rilevante:
#   DistinguishedName : CN=John Doe,OU=Finance,OU=Employees,DC=foobank,DC=inc

# Enumera tutti i gruppi AD
Get-ADGroup -Filter *

# Enumera tutte le OU del dominio (mostra anche LinkedGroupPolicyObjects)
Get-ADOrganizationalUnit -Filter *

# Forza l'aggiornamento delle policy
gpupdate /force
```

## Punti d'attenzione per l'esame eCPPT

- Conoscere la **differenza esatta** OU vs Security Group: organizzazione/GPO vs permessi.
- Le **GPO si linkano alle OU** (e a domain/site), **non** ai security group. Domanda ricorrente: "come applico una password policy solo al dipartimento Finance?" → GPO linkata a OU Finance.
- Le OU sono **nestabili**; la GPO della OU parent si propaga via *inheritance* alle child (a meno di block/enforce — concetto da ricordare ma non approfondito nel video).
- Il comando di enumerazione `Get-ADOrganizationalUnit` mostra il campo **`LinkedGroupPolicyObjects`** — utile in pentest per individuare quali OU hanno GPO interessanti.
- Distinguere `OU=` (Organizational Unit) da `CN=` (Common Name, container come `Users`, `Computers`) nei DN. `Users` e `Computers` di default **non sono OU** ma container — quindi non supportano GPO link diretto (eccezione classica nelle domande).
- Saper leggere un DN dalla catena `CN=...,OU=...,OU=...,DC=...,DC=...`.
- `gpupdate /force` è il comando per applicare immediatamente nuove GPO senza aspettare il refresh ciclico (~90 min).
- Concetto di **delegazione amministrativa** sulle OU: una via comune per dare privilegi mirati senza creare Domain Admin.

## Collegamenti con altri video

- Precedente: [[02_Users, Groups & Computers]]
- Prossimo: [[04_Active Directory Authentication]]
- Enumerazione PowerShell delle OU: [[09_AD Enumeration_ PowerView]]
- Visualizzazione grafica della struttura: [[08_AD Enumeration_ BloodHound]]
- Methodology generale: [[06_AD Penetration Testing Methodology]]
