# 09 — Phishing with Gophish - Part 2 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 9/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_Phishing with Gophish - Part 2.txt](09_Phishing with Gophish - Part 2.txt) · [09_Phishing with Gophish - Part 2.srt](09_Phishing with Gophish - Part 2.srt)

## Concetti chiave

- Login lab: `admin / phishingpassword` (`P-A-S-S-W-D`).
- I 5 building block di una campagna Gophish: **Sending Profile → Landing Page → Email Template → Users & Groups → Campaign**.
- **Sending Profile** = SMTP server, sender address; nel lab `localhost:25` con user `red@demo.ine.local`.
- **Landing Page** = clone portale (es. login INE su `localhost:8080`) con **Capture Submitted Data** e **Capture Passwords**.
- **Email Template** = importabile da raw email/HTML; supporta **attachments** (es. macro doc).
- **Users & Groups** = CSV `First Name, Last Name, Email, Position`.
- **Campaign** = associa template + landing page + URL phish server + profile + group; supporta **scheduling**.
- Risultati live: emails sent, opened, clicked, submitted, reported → export CSV per il cliente.

## Spiegazione approfondita

### Sending Profile
- Name: es. "Red Team".
- Interface Type: SMTP.
- From: `Info & Support <info@demo.ine.local>` (spoof se il dominio target non ha SPF/DKIM strict).
- Host: `localhost:25`.
- Username/Password: account su mail server (`red@demo.ine.local` / `penetrationtesting`).
- Ignore Certificate Errors: true (lab).
- **Send Test Email** prima del deploy.

### Landing Page
- Name: "INE Password".
- **Import Site**: scarica HTML del portale target (es. `http://localhost:8080`).
- Toggle **Capture Submitted Data** + **Capture Passwords**.
- **Redirect to**: URL legittimo per non insospettire la vittima dopo submit (es. `https://ine.com/login`).

### Email Template
- Name: descrittivo (es. "INE Password Reset").
- Subject: "Password Reset Instructions".
- **Import Email**: incolla raw email/HTML (pretext da L4bF0x).
- **Add Tracking Image**: pixel di tracking.
- **Add Files**: allegati malevoli (`.docm`, `.hta`, archivio).

### Users & Groups
- **Bulk Import** via CSV.
- Crea gruppi per dipartimento (HR, Accounting, IT) per segmentation.

### Campaign
- Name: "INE Password Reset".
- Email Template, Landing Page, URL (`http://<phish-server>`), Sending Profile, Groups.
- **Launch Date** + opzionalmente **Send Emails By** (campagna distribuita nel tempo).
- Risultati real-time:
  - **Email Sent**
  - **Email Opened**
  - **Clicked Link**
  - **Submitted Data**
  - **Email Reported**
- **Export** raw events / results CSV.

### Demo lab — problema esterno
La landing page tira CSS/JS da CDN esterne → in lab senza internet rende lenta/rotta. Fix: scaricare risorse locally o editare `Inetpub/wwwroot/index` rimuovendo `<link>`/`<script>` esterni.

## Comandi & strumenti

| Step | Path Gophish UI |
|---|---|
| Sending Profile | Sending Profiles → New |
| Landing Page | Landing Pages → New → Import Site |
| Email Template | Email Templates → New → Import Email |
| Group | Users & Groups → New → Bulk Import (CSV) |
| Campaign | Campaigns → New → fill all fields → Launch |
| Risultati | Campaigns → View Results |

## Esempi pratici

```text
# Sending Profile JSON-like
Name: Red Team
From: Info & Support <info@demo.ine.local>
Host: localhost:25
Username: red@demo.ine.local
Password: penetrationtesting

# Group CSV
First Name,Last Name,Email,Position
Vic,Tim,victim@demo.ine.local,Intern

# Landing Page
Import Site URL: http://localhost:8080
Capture Submitted Data: ON
Capture Passwords: ON
Redirect to: http://localhost:8080  (in prod: https://target.com/login)

# Campaign
URL: http://localhost   (in prod: http://phish.attacker.com)
Launch Date: now or scheduled
```

## Punti d'attenzione per l'esame eCPPT

- I **5 building block** di una campagna Gophish sono materia d'esame: **Sending Profile, Email Template, Landing Page, Users & Groups, Campaign**.
- **Capture Passwords** è opzionale (e disattivata di default per ragioni etico/legali).
- **Redirect post-submit** verso URL legittimo = tecnica di evasion (no insospettire l'utente).
- **Tracking pixel** = come Gophish misura "opened".
- **Send Test Email** prima del deploy.
- Sapere che il phish server ascolta su porta 80 (default) e l'admin su 3333.
- In production: **dominio + SPF/DKIM/DMARC + mail relay**.

## Collegamenti con altri video

- Precedente: [[08_Phishing with Gophish - Part 1]]
- Prossimo: [[010_Resource Development & Weaponization]]
- Allegati malevoli da inserire: [[011_VBA Macro Fundamentals]] e successivi.
- Spear phishing finale: [[024_Initial Access Via Spear Phishing Attachment]]
