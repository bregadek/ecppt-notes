# 04 — Client-Side Information Gathering (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 4/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Client-Side Information Gathering.txt](04_Client-Side Information Gathering.txt) · [04_Client-Side Information Gathering.srt](04_Client-Side Information Gathering.srt)

## Concetti chiave

- Il successo del client-side attack dipende dalla **qualità del recon** sul client (OS, browser, Office version, plugin).
- Due categorie: **Passive** (OSINT, search engine, social) e **Active** (interazione con employee per estrarre info).
- Passive: già coperto in eJPT (Google Dorks, Maltego, theHarvester, Shodan).
- Active: **Client Fingerprinting** (browser fingerprinting) + **Social Engineering** + **Banner Grabbing client**.
- Esempio canonico: macro che genera errore "documento corrotto" come **canary** per confermare presenza di Office sul target.
- L'info su versione di Office determina quali macro / bypass funzionano.

## Spiegazione approfondita

### Perché serve recon client-side
Senza sapere se l'employee usa Windows + Office, oppure Mac + Pages, oppure ChromeOS, sviluppi payload a vuoto. Identifica:
- Browser + versione.
- OS + architettura (x86/x64).
- Software installato (Office, Adobe Reader, mail client, AV).

### Passive Client Information Gathering
- **OSINT**: LinkedIn, Twitter, GitHub, public forum.
- **Search Engine Recon**: Google Dorks, Shodan, Censys.
- **Email harvesting**: `theHarvester`.
- **Tool**: Maltego per link analysis.
- *Out of scope del corso* (visto in eJPT).

### Active Client Information Gathering
Interazione indiretta con l'employee per estrarre info:
1. **Client Fingerprinting** — pagina web che raccoglie User-Agent, plugin, screen, fonts → identifica browser/OS (video 05).
2. **Social Engineering** — chiedere info via mail/telefono "per compatibilità".
3. **Banner Grabbing** — analoga ai server, ma sulle risposte del client.

### Scenario didattico — Alice contro Acme Corp
1. **Research**: Alice trova job opening con resume upload.
2. **Initiating Contact**: crea persona "Sarah Johnson", invia resume `.docm` con macro che **genera errore** (non malevola, solo crash).
3. **Response**: HR prova ad aprire → errore → contatta Sarah dicendo "il doc non si apre".
   - **Conferma implicita: hanno Office installato.**
4. **Follow-up**: Sarah chiede "potresti dirmi la versione di Word per assicurare compatibilità?".
5. **Information Gathering**: HR risponde con versione Office.
6. **Analysis & Resource Dev**: Alice ora sa versione esatta → costruisce macro mirata (bypass security feature di quella versione).

### Tabella tecniche active

| Tecnica | Cosa estrae | Tooling |
|---|---|---|
| Client Fingerprinting | UA, plugin, OS, screen, fonts | Pagina HTML+JS custom, BeEF |
| Social Engineering | Versione software, abitudini | Email, telefono |
| Banner Grabbing | Header risposte client | Custom server log |

## Comandi & strumenti

Nessun comando concreto in questo video. Tool citati (passive):
- `theHarvester -d acme.com -b all`
- Maltego
- Google Dorks
- Shodan

## Esempi pratici

```text
# Pretexting con "documento corrotto"
1. Crea Word .docm con macro:
   Sub Document_Open()
       Err.Raise 5  ' simula corruzione
   End Sub
2. Invia come "Sarah Johnson CV" all'HR.
3. Attendi risposta "non si apre".
4. Rispondi: "Quale versione di Word usate? voglio assicurare compatibilità."
5. HR risponde -> hai Office version + conferma OS Windows.
```

## Punti d'attenzione per l'esame eCPPT

- **Passive vs Active recon client-side**: la passive non tocca il target, l'active interagisce (anche solo via mail).
- **Client Fingerprinting** è il principale tool active per **browser/OS**, vedi video 05.
- L'esempio "macro che genera errore" è un classico — **pretexting per recon**, non per exploit immediato.
- Conoscere **versione esatta** di Office è critico per scegliere il bypass (es. Protected View, AMSI, MOTW).
- Il flusso è: **Recon → Target ID → Pretext per recon attivo → Resource Dev → Delivery**.

## Collegamenti con altri video

- Precedente: [[03_Client-Side Attack Vectors]]
- Prossimo: [[05_Client Fingerprinting]] — demo pratica.
- Social engineering: [[06_Introduction to Social Engineering_1717706352952]]
- Pretexting: [[07_Pretexting]]
- Recon iniziale per phishing: [[018_Pretexting Phishing Documents]]
