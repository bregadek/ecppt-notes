# 01 — Introduction (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 1/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Durata video:** 11:11 · **Fonte appunti:** [01_Introduction.txt](01_Introduction.txt) · [01_Introduction.srt](01_Introduction.srt)

## Concetti chiave

- Il corso è un'**introduzione completa al penetration testing di Active Directory**, dal primer architetturale fino alle persistence techniques.
- È strutturato seguendo l'**AD Kill Chain**: Primer → Methodology → Enumeration → Privilege Escalation → Lateral Movement → Persistence.
- L'enumerazione viene affrontata **sia automatica** (BloodHound) **sia manuale** (PowerView).
- Le tecniche di Privilege Escalation in AD ruotano intorno a **Kerberos**: Kerberoasting e AS-REP Roasting.
- Lateral movement specifico AD: **Pass-the-Hash** e **Pass-the-Ticket** (diverso dal modulo generico "Lateral Movement & Pivoting").
- Persistence: **Silver Ticket** e **Golden Ticket** — abuso del TGT/TGS Kerberos.

## Spiegazione approfondita

### Topic Overview (i 6 blocchi del corso)
1. **Active Directory Primer** — fondamenta: cos'è AD, perché esiste, componenti (domain controller, domain, OU, forest, tree, trust, GPO). Base teorica indispensabile prima di passare alla parte offensiva.
2. **AD Penetration Testing Methodology** — fasi tipiche di un AD pentest, integrazione nell'AD Kill Chain.
3. **AD Enumeration** — raccolta di info su utenti, gruppi, permessi, trust. Strumento principale **BloodHound** per la parte grafica/automatica e **PowerView** per quella manuale via PowerShell.
4. **AD Privilege Escalation** — focus su attacchi Kerberos:
   - **Kerberoasting**: estrazione di ticket TGS di service account, crack offline.
   - **AS-REP Roasting**: attacco su utenti con `DONT_REQUIRE_PREAUTH`.
5. **AD Lateral Movement** — Pass-the-Hash (riuso hash NTLM) e Pass-the-Ticket (riuso ticket Kerberos) calati nel contesto AD.
6. **AD Persistence** — Golden Ticket (forgia TGT con la chiave del KRBTGT) e Silver Ticket (forgia TGS per un servizio specifico).

### Prerequisiti (da chi parla il corso)
- **Networking**: IP, subnetting, routing, TCP/UDP/HTTP/DNS.
- **OS fundamentals**: Windows e Linux, CLI, file system, processi, permessi.
- **Exploitation & Post-Exploitation** su Windows (idealmente livello eJPT o equivalente).
- **Targeting di servizi Windows**: SMB, RDP, WinRM.
- **Tool comuni**: Metasploit, Nmap; nozioni di metodologia di pentest.

### Learning Objectives (cosa saprai fare alla fine del corso)
- Comprendere architettura AD: domains, DC, forest, trust, OU, GPO.
- Conoscere la **AD pentesting methodology** end-to-end.
- Saper **enumerare** un AD con BloodHound e PowerView.
- Saper eseguire **Kerberoasting** e **AS-REP Roasting** per privilege escalation.
- Saper eseguire **Pass-the-Hash** e **Pass-the-Ticket** per lateral movement.
- Saper piazzare **Silver Ticket** e **Golden Ticket** per persistenza.

## Comandi & strumenti

Questo video è introduttivo e **non** introduce comandi. Gli strumenti citati e che vedremo nei prossimi video:

| Strumento | Categoria | Scopo |
|---|---|---|
| **BloodHound** | Enumeration | Mappa grafica di relazioni AD (utenti, gruppi, ACL, sessioni); evidenzia attack path verso Domain Admin. |
| **PowerView** | Enumeration | Modulo PowerShell per enum AD manuale via LDAP. |
| **Rubeus / Impacket (`GetUserSPNs.py`, `GetNPUsers.py`)** | Kerberos attacks | Kerberoasting, AS-REP roasting (introdotti nei video successivi). |
| **Mimikatz** | Credential dump, ticket forge | Dump LSASS, Golden/Silver Ticket. |
| **CrackMapExec / NetExec** | Recon & lateral movement | Spray, pass-the-hash, validazione credenziali in massa. |

## Esempi pratici

N/A in questo video introduttivo. Esempi concreti partono dal video **02 — Users, Groups & Computers**.

## Punti d'attenzione per l'esame eCPPT

- L'esame eCPPT (formato 2024, **45 domande a risposta multipla** in ambiente pratico) include in modo significativo **scenari AD**.
- Devi sapere **distinguere** tra:
  - Kerberoasting (target: service account con SPN) vs AS-REP Roasting (target: utenti con preauth disabilitata).
  - Pass-the-Hash (riuso hash NTLM) vs Pass-the-Ticket (riuso ticket Kerberos).
  - Golden Ticket (forgia TGT, richiede hash di `krbtgt`) vs Silver Ticket (forgia TGS, richiede hash dell'account del servizio).
- Il corso è basato sull'**AD Kill Chain**: memorizzane le fasi nell'ordine, una domanda d'esame ricorrente è "qual è la prossima azione corretta dato questo scenario".
- I prerequisiti dichiarati (eJPT + nozioni di exploitation Windows) sono gli stessi noti come *baseline* dell'eCPPT.

## Collegamenti con altri video

- Prossimo: [[02_Users, Groups & Computers]] — primo video del **AD Primer**.
- Methodology globale: [[06_AD Penetration Testing Methodology]]
- Strumenti di enumerazione: [[08_AD Enumeration_ BloodHound]] · [[09_AD Enumeration_ PowerView]]
- Kerberos attacks: [[010_AS-REP Roasting]] · [[011_Kerberoasting]]
- Lateral movement AD: [[012_AD Lateral Movement_ Pass-the-Hash]] · [[013_AD Lateral Movement_ Pass-the-Ticket]]
- Persistence: [[014_AD Persistence_ Golden Ticket]] · [[015_AD Persistence_ Silver Ticket]]
