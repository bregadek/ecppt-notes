# 06 — AD Penetration Testing Methodology (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 6/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_AD Penetration Testing Methodology.txt](06_AD Penetration Testing Methodology.txt) · [06_AD Penetration Testing Methodology.srt](06_AD Penetration Testing Methodology.srt)

## Concetti chiave

- L'**AD Penetration Testing** simula attacchi reali per individuare vulnerabilità, debolezze e misconfigurazioni nell'infrastruttura AD.
- Esistono diverse **AD Kill Chain**; quella più specifica include: Reconnaissance → Domain Enumeration → Local Privilege Escalation → Admin Recon → Lateral Movement → Domain Privilege Escalation → Cross-Trust Attacks → Persistence/Exfiltration.
- Il corso adotta l'**assumed breach**: si parte da accesso già ottenuto a un sistema del dominio; **non** copre l'initial compromise.
- Fasi coperte: **Host recon → Domain enumeration → Privilege escalation → Lateral movement → Persistence**.
- Tecniche per fase: Password Spraying, BloodHound/PowerView, Kerberoasting/AS-REP Roasting, Pass-the-Hash/Pass-the-Ticket, Silver/Golden Ticket.
- Risorsa raccomandata: **Orange Cyber Defense (OCD) Active Directory Mind Maps** — flow chart contestuale di tecniche e tool.

## Spiegazione approfondita

### Cos'è l'AD Penetration Testing
Processo di security assessment che valuta la postura di sicurezza dell'infrastruttura AD di un'organizzazione. Si simulano attacchi reali per scoprire vulnerabilità, configurazioni errate e debolezze sfruttabili.

### Le due AD Kill Chain presentate
Alexis mostra due varianti:

#### Kill chain "generica"
External Reconnaissance → Compromise system → Internal Recon → Local PrivEsc → Compromised Credentials → Admin Recon → Remote Code Execution → Domain Admin Credentials → Domain Dominance → RCE → AD Recon → Local PrivEsc → Asset Access → Exfiltration.

#### Kill chain "AD-specific" (quella usata nel corso)
Reconnaissance → **Domain Enumeration** → Local PrivEsc → Admin Reconnaissance → **Lateral Movement** → **Domain Privilege Escalation** → **Cross-Trust Attacks** → (ciclo che si ripete) → **Persistence / Exfiltration**.

### Scope del corso — Assumed Breach
**Importante:** il corso **non copre l'initial compromise**. Si assume di aver già un foothold su un sistema del dominio. Le fasi affrontate sono:
1. **Host reconnaissance**
2. **Domain enumeration**
3. **Domain privilege escalation**
4. **Lateral movement**
5. **Persistence**

### Tecniche per fase

#### Initial Compromise (citato, non coperto)
- **Password spraying** — credenziali comuni/leaked contro molti account (sì coperto nel video 07!).
- **Brute force** — CrackMapExec, Evil-WinRM, Hydra.
- **Phishing** — credential harvesting.
- **Network poisoning** — LLMNR/NBT-NS poisoning, ARP spoofing, **SMB Relay** (coperti nel corso *Network Penetration Testing*).

#### AD Enumeration
- **PowerView** (manuale, PowerShell, LDAP queries).
- **BloodHound** (automatica, grafo, evidenzia shortest path a Domain Admin).
- Obiettivo: enumerare oggetti, attributi, permessi, group membership, sessioni, **attack path** verso DA.

#### Privilege Escalation (in contesto AD)
- **Kerberoasting** — target: service account con SPN; estrae TGS, crack offline della password.
- **AS-REP Roasting** — target: utenti con `DONT_REQUIRE_PREAUTH`; estrae AS-REP, crack offline.
- (Tecnicamente più post-exploitation che privesc, ma trattate qui.)

#### Lateral Movement
- **Pass-the-Hash** — riuso di hash NTLM rubati.
- **Pass-the-Ticket** — riuso di TGT/TGS Kerberos rubati, senza conoscere la password in chiaro.

#### Persistence
- **Silver Ticket** — forgia TGS per uno specifico servizio, non richiede la password dell'account ma il suo NTLM hash.
- **Golden Ticket** — forgia TGT arbitrario per qualsiasi utente, richiede l'hash dell'account **`KRBTGT`**.

### Risorsa esterna: OCD Mind Maps
Alexis mostra il sito **Orange Cyber Defense Active Directory Mind Maps** (file SVG zoomabile). Funge da **flow chart contestuale**: ogni nodo è uno scenario (es. "hai un valid username" → opzioni: password spray con CME/SprayHound/enum4linux, AS-REP roasting, ecc.). Per ogni tecnica elenca i comandi esatti dei tool (CrackMapExec, SprayHound, impacket `GetNPUsers.py`, Rubeus, Responder, `python WSUS.py`, ecc.). Raccomandato per consultazione durante engagement reali.

## Comandi & strumenti

| Strumento / tecnica | Fase | Note dal video |
|---|---|---|
| **CrackMapExec (CME)** | Recon, password spray, lateral | Esempio mostrato: `cme smb <DC_IP> -u userlist -p passlist` |
| **SprayHound** | Password spray | Citato nelle mind maps |
| **Evil-WinRM** | Brute force / accesso WinRM | Citato |
| **Hydra** | Brute force generico | Citato |
| **impacket `GetNPUsers.py`** | AS-REP Roasting | Citato |
| **Rubeus** | Kerberos attacks (kerberoast, asreproast, ticket abuse) | Citato |
| **Responder** | LLMNR/NBT-NS poisoning, NTLMv1/v2 capture | Citato |
| **`python WSUS.py`** | WSUS relay attack | Citato (mind map) |
| **PowerView** | Enumeration manuale via PowerShell | Coperto nel video 09 |
| **BloodHound** | Enumeration automatica con grafo | Coperto nel video 08 |
| **Mimikatz** | Credential dump, ticket forge | Implicito per Silver/Golden ticket |
| **OCD AD Mind Maps** | Reference per scelta tecnica | https://orangecyberdefense.com (mind map SVG) |

## Esempi pratici

```bash
# Esempio mostrato (mind map OCD) — password spray con CrackMapExec
cme smb <DC_IP> -u <userlist.txt> -p <passlist.txt>
```
(Esempi dettagliati di ogni tecnica nei video successivi.)

## Punti d'attenzione per l'esame eCPPT

- **Memorizzare l'ordine delle fasi AD-specifica**: Recon → Domain Enumeration → Local PrivEsc → Admin Recon → Lateral Movement → Domain PrivEsc → Cross-Trust → Persistence. L'esame fa domande del tipo "dato questo stato, qual è la prossima azione?".
- **Assumed Breach** = punto di partenza standard nei lab eCPPT AD: hai già credenziali low-priv o un foothold; il task è scalare a Domain Admin.
- **Mapping tecnica → fase**:
  - Password Spraying / Brute Force / Phishing / Poisoning → Initial Access.
  - PowerView / BloodHound → Enumeration.
  - Kerberoasting / AS-REP Roasting → Privilege Escalation (in contesto AD).
  - Pass-the-Hash / Pass-the-Ticket → Lateral Movement.
  - Silver Ticket / Golden Ticket → Persistence.
- **Kerberoasting** target = service account **con SPN**.
- **AS-REP Roasting** target = utenti con `DONT_REQUIRE_PREAUTH`.
- **Pass-the-Hash** = NTLM-based. **Pass-the-Ticket** = Kerberos-based.
- **Silver vs Golden**: Silver forgia **TGS** per **un servizio** (serve hash dell'account servizio); Golden forgia **TGT** arbitrario (serve hash di **`KRBTGT`**).
- L'**attack path verso Domain Admin** è l'obiettivo finale in ogni lab AD.
- Conoscere l'esistenza di tool come **CrackMapExec/NetExec, Rubeus, impacket suite (GetNPUsers, GetUserSPNs, secretsdump, psexec), BloodHound, PowerView, Mimikatz, Responder** — sono il vocabolario base dell'esame.

## Collegamenti con altri video

- Precedente: [[05_Trees, Forests & Trusts]]
- Prossimo: [[07_Password Spraying]] — prima tecnica pratica del corso.
- Enumeration: [[08_AD Enumeration_ BloodHound]] · [[09_AD Enumeration_ PowerView]]
- Privilege Escalation Kerberos: [[010_AS-REP Roasting]] · [[011_Kerberoasting]]
- Lateral Movement: [[012_AD Lateral Movement_ Pass-the-Hash]] · [[013_AD Lateral Movement_ Pass-the-Ticket]]
- Persistence: [[014_AD Persistence_ Golden Ticket]] · [[015_AD Persistence_ Silver Ticket]]
