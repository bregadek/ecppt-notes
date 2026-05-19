# 02 — Introduction to Client-Side Attacks (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 2/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Introduction to Client-Side Attacks.txt](02_Introduction to Client-Side Attacks.txt) · [02_Introduction to Client-Side Attacks.srt](02_Introduction to Client-Side Attacks.srt)

## Concetti chiave

- **Client-side attack** = tecnica che sfrutta vulnerabilità o misconfig **del software client** (browser, mail client, Office) o il comportamento umano per ottenere **initial access**.
- Target: **end-user devices** e applicazioni utilizzate dagli employee, non i server pubblici.
- **Richiedono interazione utente**: download + apertura documento + esecuzione macro / click su link.
- Più pericolosi degli attacchi server-side perché non richiedono accesso diretto al sistema target: bastano una mail e un payload.
- Vantaggi: **larga attack surface**, sfruttamento di **vulnerabilità umane** (curiosità, fiducia, ignoranza), **security control deboli sui client**, possibilità di **lateral movement**.
- Una volta dentro → standard pentest lifecycle (priv esc, lateral movement, persistence, exfiltration).
- Methodology in 7 step: Recon → Target ID → Resource Development → Payload Preparation → Delivery → Execution → Post-Exploitation.

## Spiegazione approfondita

### Perché client-side
L'eJPT copre solo server-side initial access (exploit di servizi pubblici). Ma molti asset interni non sono esposti: per arrivare alla **internal network** in un black-box pentest, bisogna passare dagli **employee computer**. Si invia una mail con un Word weaponizzato, l'employee apre il doc, la macro chiama back al listener → si bypassano firewall e perimeter security perché il traffico è **egress** (in uscita).

### Caratteristiche
- **User interaction required**: senza l'azione umana il payload non parte. Anche con la migliore macro, serve coercion via phishing.
- **Trusted delivery channels**: email, USB, siti compromessi.
- **Egress traffic**: la reverse shell esce dalla rete del target → spesso non bloccata.

### Vantaggi (perché gli attacker amano client-side)
1. **Wider attack surface** — desktop, laptop, smartphone, tablet sono ovunque.
2. **User interaction** — sfrutta debolezze umane (curiosità, trust).
3. **Less stringent security** — i client (specialmente laptop fuori dalla rete) hanno meno hardening dei server.
4. **Pivoting** — initial foothold = punto di partenza per muoversi nella rete interna.

### Client-side vs Server-side (tabella esame)

| Aspetto | Client-Side | Server-Side |
|---|---|---|
| Target | End-user device, browser, Office, employee behavior | Server, DB, web app, infrastruttura |
| Objective | Compromettere device + foothold rete | Accesso non autorizzato a server / data |
| Execution | Email, sito malevolo, doc infetto | Exploit di vulnerabilità su servizi pubblici |
| Esempi | Phishing, drive-by, social eng, malicious attachment | SQLi, XSS, RCE, brute force |
| Direzione traffico | Egress (reverse shell) | Ingress (connect to server) |

### Methodology in 7 step (esempio Acme Corp)
1. **Reconnaissance** — OSINT su sito, social, job posting; identifica employee e tech stack.
2. **Target Identification** — scelta dipartimenti più vulnerabili (HR, finance, executive).
3. **Resource Development** — sviluppo del payload (Word con macro, PDF con JS exploit).
4. **Payload Preparation** — pretext credibile, infrastruttura phishing (dominio, mail).
5. **Payload Delivery** — invio phishing con leve psicologiche (urgenza, paura, curiosità).
6. **Payload Execution** — vittima apre il doc, macro esegue, beacon C2.
7. **Post-Exploitation** — priv esc, lateral movement, exfiltration.

Mappa direttamente sulle tactic del **MITRE ATT&CK** (Recon, Resource Development, Initial Access, Execution, …).

## Comandi & strumenti

Nessun comando — video teorico. Strumenti citati:
- **Microsoft Office** (target tipico)
- **Phishing email + macro doc**
- **C2 server / listener**

## Esempi pratici

Scenario didattico: pen tester contro Acme Corp.
1. OSINT su LinkedIn → identifica dipendenti HR.
2. Recon → conferma uso di Microsoft Office.
3. Crea Word con macro che chiama back al C2.
4. Spedisce phishing "URGENT — invoice review".
5. HR apre il doc → macro lancia reverse shell.
6. Foothold sulla rete interna → lateral movement.

## Punti d'attenzione per l'esame eCPPT

- **Definizione**: client-side = exploit di software client / behavior, NON di servizi server pubblici.
- **User interaction REQUIRED** — distinguilo dagli attacchi server-side automatici.
- **Egress traffic** = reverse shell esce dal perimetro → difficile da bloccare.
- Memorizza la **7-step methodology**, ricorrente nei quesiti "what is the next step".
- I 3 vantaggi principali: **wider surface**, **human vulns**, **less hardening su client**.
- Mappa concettuale con **MITRE ATT&CK** tactics (Initial Access TA0001, Resource Development TA0042).

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_Client-Side Attack Vectors]] — dettaglio dei vettori.
- Recon: [[04_Client-Side Information Gathering]]
- Phishing tooling: [[08_Phishing with Gophish - Part 1]]
- Resource dev: [[010_Resource Development & Weaponization]]
