# 04 — Active Directory Authentication (Active Directory Penetration Testing)

> **Modulo:** Active Directory Penetration Testing · **Video:** 4/15
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Active Directory Authentication.txt](04_Active Directory Authentication.txt) · [04_Active Directory Authentication.srt](04_Active Directory Authentication.srt)

## Concetti chiave

- AD supporta più protocolli di autenticazione: **Kerberos** (primario/raccomandato), **NTLM / Net-NTLM** (legacy), **LDAP** (non trattato nel video).
- **Kerberos** è basato su **ticket cifrati** ed è ticket-based, fornisce **mutual authentication** e **SSO**.
- Il **KDC** (Key Distribution Center) coincide con il **Domain Controller**.
- Il flusso Kerberos: **AS-REQ → AS-REP (TGT) → TGS-REQ → TGS-REP → AP-REQ → AP-REP**.
- Il **TGT** è cifrato con la **long-term key dell'account `KRBTGT`** — chiave alla base del **Golden Ticket**.
- Il **service ticket (TGS)** è cifrato con la long-term key dell'**account del servizio** — chiave alla base del **Silver Ticket** e del **Kerberoasting**.
- Il **PAC** (Privilege Attribute Certificate) trasporta l'identità e i gruppi dell'utente dentro il ticket.
- **NTLM** è challenge-response, mantenuto per backward compatibility, vulnerabile a **Pass-the-Hash** e privo di mutual auth.

## Spiegazione approfondita

### Definizione
L'autenticazione AD è il processo con cui utenti e computer verificano la propria identità per accedere alle risorse di rete nel dominio. È centralizzata sul DC e garantisce confidenzialità, integrità e disponibilità degli scambi di credenziali.

### Kerberos — il flusso completo
Attori coinvolti:
- **Client / user workstation** — chi vuole autenticarsi.
- **KDC** — il Domain Controller, ospita l'**Authentication Service (AS)** e il **Ticket Granting Service (TGS)**.
- **Application server / target service** — il servizio che si vuole accedere.

#### Step 1 — AS-REQ (Request TGT)
Il client invia al KDC una richiesta che contiene il **timestamp UTC corrente cifrato con la long-term key dell'utente** (derivata dalla password). Questo è il meccanismo di **preauthentication**: se l'utente fosse legittimo, il KDC è in grado di decifrare il timestamp con la chiave dell'utente memorizzata in AD.

#### Step 2 — AS-REP (Receive TGT)
Se il KDC decifra correttamente il timestamp e il tempo è entro lo skew accettato, autentica l'utente e gli restituisce un **TGT cifrato con la long-term key dell'account `KRBTGT`**. Il TGT contiene anche il **PAC** (Privilege Attribute Certificate) con identity + group membership dell'utente.

> **Nota offensive:** se la preauthentication è **disabilitata** sull'utente, il KDC manda l'AS-REP senza richiedere la prova di possesso della password → l'AS-REP è cifrato con la chiave derivata dalla password dell'utente → si può crackare offline. È l'**AS-REP Roasting** (video 010).

#### Step 3 — TGS-REQ (Present TGT, Request TGS)
Il client presenta il TGT al KDC chiedendo un **service ticket** per un servizio specifico (identificato dal suo **SPN**). La richiesta viaggia con il TGT cifrato con la chiave del `KRBTGT`.

#### Step 4 — TGS-REP (Receive TGS)
Il KDC decifra il TGT, **copia il PAC dal TGT al nuovo service ticket**, e cifra il service ticket con la **long-term key dell'account del servizio**. Lo manda al client.

> **Nota offensive:** chiunque possieda un TGT valido può richiedere un TGS per qualsiasi SPN. Il TGS è cifrato con la chiave del service account → se l'account ha password debole, si può crackare offline. È il **Kerberoasting** (video 011).

#### Step 5 — AP-REQ
Il client presenta il TGS al target service. Il service lo decifra con la propria long-term key, legge il PAC e determina il livello di autorizzazione dell'utente.

#### Step 6 — AP-REP (opzionale)
Mutual authentication: il service risponde con timestamp cifrato per provare la propria identità.

#### PAC Validation (opzionale)
Il service può richiedere al KDC di validare la firma del PAC.

### Feature di Kerberos
- **Mutual authentication** — client e server si verificano a vicenda.
- **Single Sign-On** — una volta ottenuto il TGT, si possono richiedere più TGS senza reinserire credenziali.
- **Ticket-based** — riduce esposizione delle credenziali (la password non viaggia mai in chiaro né in hash).

### NTLM / Net-NTLM
Protocollo challenge-response più vecchio, mantenuto per **backward compatibility**.

#### Flusso NTLM
1. Il client invia una **logon request** al server.
2. Il server (o DC) risponde con un **NTLM challenge** (numero random).
3. Il client **hasha** il challenge con l'hash NTLM della propria password e invia la **NTLM response**.
4. Il server confronta la response con il calcolo equivalente lato suo. Se combacia → autenticazione OK.

#### Limiti di sicurezza
- Vulnerabile a **Pass-the-Hash** — basta l'hash NTLM, non serve la password in chiaro.
- **Nessuna mutual authentication**.
- Suscettibile a **NTLM relay**.
- Hash crackabili offline (responder/SMB capture).

### Confronto rapido Kerberos vs NTLM
| Feature | Kerberos | NTLM |
|---|---|---|
| Modello | Ticket-based, KDC trusted 3rd party | Challenge-response diretto |
| Mutual auth | Sì | No |
| SSO | Sì | No |
| Backward compatibility | Da Windows 2000 in poi | Pre-Win2000 e fallback |
| Attacchi tipici | Kerberoasting, AS-REP Roasting, Pass-the-Ticket, Golden/Silver Ticket | Pass-the-Hash, NTLM Relay |

## Comandi & strumenti

N/A in questo video — è puramente teorico, niente demo pratiche.

## Esempi pratici

N/A in questo video.

## Punti d'attenzione per l'esame eCPPT

- **Memorizzare la sequenza Kerberos**: AS-REQ → AS-REP (TGT) → TGS-REQ → TGS-REP (TGS) → AP-REQ → AP-REP. Domanda quasi certa.
- **Chi cifra cosa**:
  - TGT cifrato con la chiave di **`KRBTGT`** → necessaria per **Golden Ticket**.
  - TGS cifrato con la chiave dell'**account del servizio (SPN owner)** → necessaria per **Silver Ticket** e crackabile in **Kerberoasting**.
- **KDC = DC**. L'AS e il TGS sono due ruoli logici dentro lo stesso Domain Controller.
- Il **PAC** contiene l'identità + i gruppi dell'utente; viene copiato dal TGT al TGS.
- **Preauthentication**: l'utente cifra il timestamp con la sua key per provare di conoscere la password. Se disabilitata (`DONT_REQUIRE_PREAUTH`) → AS-REP Roasting possibile.
- **Kerberos richiede sincronia temporale** — skew massimo tipico 5 minuti (il video lo accenna come "accepted skew"). Non avere clock sync = Kerberos fallisce.
- **NTLM vs Kerberos**: NTLM = challenge-response, vulnerabile a Pass-the-Hash; Kerberos = ticket-based, vulnerabile a Pass-the-Ticket.
- **Pass-the-Hash funziona con NTLM**, non con Kerberos puro (per Kerberos si usa Pass-the-Ticket o Overpass-the-Hash).
- **LDAP** è citato come terzo protocollo ma non approfondito — sappi che esiste.

## Collegamenti con altri video

- Precedente: [[03_Organizational Units (OUs)]]
- Prossimo: [[05_Trees, Forests & Trusts]]
- AS-REP Roasting (preauth disabled): [[010_AS-REP Roasting]]
- Kerberoasting (TGS crack): [[011_Kerberoasting]]
- Pass-the-Hash (NTLM): [[012_AD Lateral Movement_ Pass-the-Hash]]
- Pass-the-Ticket (Kerberos): [[013_AD Lateral Movement_ Pass-the-Ticket]]
- Golden Ticket (KRBTGT key): [[014_AD Persistence_ Golden Ticket]]
- Silver Ticket (service key): [[015_AD Persistence_ Silver Ticket]]
