# 08 — Phishing with Gophish - Part 1 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 8/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_Phishing with Gophish - Part 1.txt](08_Phishing with Gophish - Part 1.txt) · [08_Phishing with Gophish - Part 1.srt](08_Phishing with Gophish - Part 1.srt)

## Concetti chiave

- **Gophish** = framework open source per phishing simulation, pensato per pen tester e security pro.
- Vantaggi su SET: **WYSIWYG email editor**, **campaign management**, **target segmentation**, **landing page builder**, **tracking real-time**, **report generation**, **scheduling/automation** ricorrente.
- Architettura: **admin server** (default :3333, HTTPS) + **phishing server** (default :80) + DB SQLite.
- Deploy reale: VPS (AWS/Linode/DigitalOcean) + dominio + mail server (es. **AWS SES**).
- Lab INE = ambiente Windows pre-configurato (Gophish + Thunderbird + CSV targets + email template).
- Setup iniziale lab: rimuovi reference esterne nei template HTML (fonts/CSS via CDN) per non bloccare load.
- `config.json` controlla URL, porta, TLS admin/phish server.

## Spiegazione approfondita

### Cos'è Gophish
Open-source phishing framework completo:
- Email template editor.
- Target list + segmentation (per dept, role, geo).
- Landing page editor (clone di portali login).
- Tracking: opened, clicked, submitted, reported.
- Report generation per CISO/board.
- **Scheduling/automation** (campagne ricorrenti annuali).

### Perché Gophish vs alternative
- **SET (Social Engineering Toolkit)**: ottimo per test, manca management/tracking.
- **Gophish**: production-ready, multi-campaign, multi-target, reportistica → ideale per real pentest.

### Features chiave
| Feature | Descrizione |
|---|---|
| Campaign Creation | Multi-campaign per stessa org, sortable |
| Email Template Editor | WYSIWYG, pre-text loadable |
| Target Management | CSV import, segmentation per dept |
| Landing Pages | Clone portali (Office365, etc.), credential capture |
| Tracking & Reporting | Open/click/submit in real-time, share con cliente |
| Scheduling | Lancio a data/ora, **recurring** annuale |

### Deploy in produzione
1. VPS (AWS/Linode/DO).
2. Dominio resolved a IP server.
3. Mail relay: **AWS SES** o Mailgun.
4. Configurare SPF/DKIM/DMARC del dominio attaccante (no spoof se target ha policy strict).

### Lab INE — tour
- Windows VM con Guacamole.
- Folder Gophish desktop con `gophish.exe`.
- Thunderbird configurato con mailbox `victim@demo.ine.local`.
- Email template pretexting: **password reset**.
- CSV targets: CEO, CFO, CMO, Intern (`victim@demo.ine.local`).

### Fix template per lab offline
Lab non ha internet → modifica `templates/base.html` e `login.html`:
- Rimuovi `<link rel="stylesheet">` a Google Fonts.
- Rimuovi JS CDN esterni.
- CSS locali (`static/css/gophish.css`) restano.

### config.json
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
Nel lab: settare `use_tls: false` su admin per evitare warning cert.

### Avvio
- Doppio click su `gophish.exe` (Windows) o `./gophish` (Linux).
- Console mostra credenziali admin random alla prima esecuzione (logfile).
- Firefox → `http://127.0.0.1:3333` → login.

## Comandi & strumenti

| Comando / Path | Scopo |
|---|---|
| `gophish.exe` / `./gophish` | Avvia admin + phish server |
| `config.json` | Configurazione TLS/porte |
| `templates/base.html`, `login.html` | Template UI da pulire |
| `static/css/gophish.css` | CSS locale |
| `gophish.db` | SQLite DB campagne |
| Default admin URL | `https://127.0.0.1:3333` |
| Default phish URL | `http://0.0.0.0:80` |

## Esempi pratici

```bash
# Linux production setup
wget https://github.com/gophish/gophish/releases/...
unzip gophish-v*.zip && cd gophish
chmod +x gophish
# Edit config.json: admin listen_url 0.0.0.0:3333
./gophish
# stdout: admin user=admin pwd=<random>
# Apri https://<vps-ip>:3333
```

```text
# CSV targets (esempio del lab)
First Name,Last Name,Email,Position
John,Smith,ceo@demo.ine.local,CEO
Jane,Doe,cfo@demo.ine.local,CFO
Mark,Roe,cmo@demo.ine.local,CMO
Sam,Intern,victim@demo.ine.local,Intern
```

## Punti d'attenzione per l'esame eCPPT

- **Gophish** è IL framework di phishing menzionato dal corso (preferito su SET per pentest reali).
- Saper distinguere **admin server (3333)** vs **phish server (80)**.
- Componenti di una campagna: **Sending Profile, Email Template, Landing Page, Users & Groups, Campaign**.
- Per produzione: **VPS + dominio + SPF/DKIM/DMARC + mail relay** (SES).
- Possibile domanda: "Quale tool useresti per phishing campaign con tracking real-time?" → **Gophish**.
- **Scheduling/recurring** = feature distintiva per assessment annuali.

## Collegamenti con altri video

- Precedente: [[07_Pretexting]]
- Prossimo: [[09_Phishing with Gophish - Part 2]] — setup campagna completa.
- Pretexting templates usati: [[07_Pretexting]] (L4bF0x repo)
- Spear phishing attachment: [[024_Initial Access Via Spear Phishing Attachment]]
