# 07 — Pretexting (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 7/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_Pretexting.txt](07_Pretexting.txt) · [07_Pretexting.srt](07_Pretexting.srt)

## Concetti chiave

- **Pretexting** = creazione di un **falso scenario/narrativa** per guadagnare fiducia ed estrarre info o azioni.
- Differenza da deception pura: il pretext costruisce un **narrativa coerente**, non solo bugie singole.
- 5 caratteristiche: **False Pretense**, **Establishing Trust**, **Manipulating Emotion**, **Information Gathering**, **Maintaining Consistency**.
- Esempi classici: **Tech Support Scam**, **Job Interview Scam**, **Emergency Situation** (security breach, LastPass reset).
- Sfrutta **fear, urgency, curiosity, sympathy**.
- Risorsa chiave: **GitHub Phishing-Pretexts** (di **L4bF0x**) — libreria template HTML pronti per offensive engagement.
- Template tipico: "Corporate IT Department Upgrade" (es. Office 365 migration → credential harvest).

## Spiegazione approfondita

### Definizione
Pretexting = mettere l'employee in una **situazione familiare** per estrarre info. La chiave è la **narrativa coerente** che sembra plausible nel daily flow del lavoro.

### 5 caratteristiche del pretexting
1. **False Pretense** — storia fittizia (mail professionale, impersonazione autorevole).
2. **Establishing Trust** — rapporto via tono, linguaggio, professionalità (no "Nigerian Prince" obvious scam).
3. **Manipulating Emotion** — leve: curiosità, paura, urgenza, simpatia.
4. **Information Gathering** — dopo trust, richiesta "naturale".
5. **Maintaining Consistency** — narrativa coerente per tutta l'interazione.

### Pretexting examples
- **Tech Support Scam**: finto rappresentante "il tuo PC è infetto", chiede remote access. Sfrutta **fear/urgency**.
- **Job Interview Scam**: finto recruiter LinkedIn, chiede resume/info personali/payment. Sfrutta **desire for approval**.
- **Emergency Situation**: finto security vendor "data breach, resetta password" → link a portale fake → credential harvest. Esempio LastPass.
- **VPN issues**: "stiamo riscontrando problemi VPN, verifica accesso al portale temporaneo" → credential harvest.
- **Shipping invoice**: per accounting → review documento allegato → macro execution.
- **Office 365 / Webmail upgrade**: IT department impersonation → click link per "aggiornare account" → credential harvest.

### Template "Corporate IT Department Upgrade"
- Subject: "New Webmail Office 365 Rollout".
- Body: "In an effort to bring you the best technology, {Organization} has implemented the newest version of Microsoft Office Webmail. Your existing emails, contacts and calendar events will be seamlessly transferred. Please visit {link} and log in with your current credentials to confirm your upgraded account."
- Leve: **urgency** (avoid service disruption) + **fear** (lose email).

### Importance & Impact
- Bypassa controlli tecnici.
- Causa **data breaches**, **financial loss**, **reputational damage**, **regulatory penalties**.
- Mitigazione: training, policy, **phishing simulations** ricorrenti.

### Workflow tipico pen test
1. Recon target organization.
2. Scegli template appropriato (IT upgrade, VPN issues, invoice).
3. Personalizza con variabili (org name, sender name, link).
4. Spoof domain (se DKIM/SPF non strict).
5. Imposta mailbox replies.
6. Invia campagna.
7. Misura risultati.

## Comandi & strumenti

| Risorsa | URL/Path | Scopo |
|---|---|---|
| **L4bF0x Phishing-Pretexts** | `github.com/L4bF0x/PhishingPretexts` | Libreria template HTML pronti |
| **Gophish** | (video 08-09) | Delivery |
| Template variabili | `{Organization}`, `{Link}`, `{Sender}` | Sostituzione per target |

## Esempi pratici

```html
<!-- Esempio pretext IT Upgrade -->
Subject: New Webmail Office 365 Rollout

Dear Colleagues,

In an effort to continue to bring you the best available technology,
{{ORG_NAME}} has implemented the newest version of Microsoft Office Webmail.
Your existing emails, contacts and calendar events will be
seamlessly transferred to your new account.

Please visit {{PHISHING_URL}} and log in with your current
username and password to confirm your upgraded account.

If you have any additional questions, please contact the help desk.

Thank you,
IT Department
```

## Punti d'attenzione per l'esame eCPPT

- **Pretexting ≠ Phishing**: pretexting è il contesto narrativo; phishing è il canale di consegna.
- **5 caratteristiche** da memorizzare (False Pretense → Maintaining Consistency).
- I 3 example principali da conoscere: **Tech Support**, **Job Interview**, **Emergency**.
- Pretext per il pentest dev'essere **plausibile nel daily workflow** (IT upgrade, invoice, VPN, password reset).
- Risorsa **L4bF0x/PhishingPretexts** su GitHub è la libreria standard.
- Leve psicologiche tipiche: **fear + urgency** > greed/sympathy in contesti corporate.
- Esame può chiedere: dato uno scenario, quale pretext useresti? → match con dipartimento target (HR → CV / job; Accounting → invoice; All → IT upgrade).

## Collegamenti con altri video

- Precedente: [[06_Introduction to Social Engineering_1717706352952]]
- Prossimo: [[08_Phishing with Gophish - Part 1]] — delivery pratica.
- Recon attiva via pretext: [[04_Client-Side Information Gathering]]
- Pretexting su doc malevoli: [[018_Pretexting Phishing Documents]]
- Spear phishing applicato: [[024_Initial Access Via Spear Phishing Attachment]]
