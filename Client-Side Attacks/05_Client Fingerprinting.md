# 05 — Client Fingerprinting (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 5/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_Client Fingerprinting.txt](05_Client Fingerprinting.txt) · [05_Client Fingerprinting.srt](05_Client Fingerprinting.srt)

## Concetti chiave

- **Client Fingerprinting** = tecnica active per identificare **browser, versione, plugin, OS, architettura** del target.
- Subset principale: **Browser Fingerprinting** via **JavaScript** eseguito sul browser della vittima.
- Workflow: il pen tester ospita una pagina web con script di fingerprint; convince via social engineering la vittima a visitarla; la pagina logga le info su file.
- Libreria standard: **FingerprintJS2** (open source, raccoglie UA, plugin, fonts, screen, language, AdBlock, WebGL, …).
- Setup demo del video: Kali + Apache + Fingerprint.js2 + script `fingerprint.php` per salvare i dati.
- Tool per parsare il **User-Agent**: `explore.whatismybrowser.com` → restituisce browser+versione+OS.
- Limitazione: browser come **Brave** o estensioni come **uBlock Origin** possono bloccare JS → tecnica non foolproof.

## Spiegazione approfondita

### Obiettivi
Identificare:
1. **Browser** (Firefox, Chrome, Edge, Brave).
2. **Versione browser** → CVE noti possibili.
3. **Plugin/Extensions** → vettori di exploit.
4. **OS + versione** (Windows 10/11, macOS Catalina, Linux).
5. **Architettura** (x86/x64, Intel/Apple Silicon).
6. **Language locale** → utile per scrivere phishing nella lingua giusta.

### Perché JavaScript
JS gira **lato client** → quando la vittima visita la pagina, lo script raccoglie info dal browser e le invia (es. via `XMLHttpRequest` POST) ad uno script server-side che le salva.

### Workflow lab
1. Setup **Apache2** su Kali: `sudo apt install apache2 && sudo systemctl start apache2`.
2. `cd /var/www/html && sudo git clone https://github.com/Valve/fingerprintjs2`.
3. Modifica `index.html` del demo Fingerprint.js2:
   - Cambia titolo (es. "Construction Tips") per pretexting.
   - Cambia label bottone ("Get Construction Tips").
   - Sostituisce `<br>` con `\n` in output per salvataggio testo.
   - Aggiunge codice `XMLHttpRequest` POST a `fp.php`.
4. Crea `fp.php` che salva i dati in `fingerprint.txt`:
   ```php
   <?php
   $data = "Client IP: " . $_SERVER['REMOTE_ADDR'] . "\n"
         . file_get_contents("php://input") . "\n\n";
   file_put_contents("/var/www/html/fingerprintjs2/fingerprint.txt",
                     $data, FILE_APPEND);
   ?>
   ```
5. `sudo chown -R www-data:www-data /var/www/html/fingerprintjs2`.
6. Restart Apache, visita pagina, click bottone → `fingerprint.txt` popolato.
7. Copia UA → parse su `https://explore.whatismybrowser.com/useragents/parse/`.

### Tipo info estratte
- `User-Agent` (browser + OS).
- Language (`en-US`, `de-DE`).
- Screen resolution, color depth.
- Plugins, MIME types.
- Fonts, WebGL info.
- AdBlock detected (true/false).
- Touch support.
- Timezone.

### Parsing del User-Agent
Esempi visti nel video:
- `Mozilla/5.0 (Macintosh; Intel Mac OS X ...) ... Chrome/...` → **Chrome on macOS Catalina (Intel Mac)**.
- `Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/123` → Chrome 123 on Windows 10 (in realtà Win 11, NT 10.0 è kernel).
- Linux dà info meno conclusive (es. "Firefox 115 on Linux").

## Comandi & strumenti

| Comando / Tool | Scopo |
|---|---|
| `sudo apt install apache2` | Web server |
| `sudo systemctl start apache2` | Start |
| `git clone https://github.com/Valve/fingerprintjs2` | Lib JS |
| `XMLHttpRequest()` + `.open("POST", "fp.php")` | Invio dati |
| `file_put_contents(..., FILE_APPEND)` | Salva su disco |
| `https://explore.whatismybrowser.com/useragents/parse/` | Parse UA online |
| **FingerprintJS2** | Lib principale (anche v3/Pro) |
| **BeEF** | Alternativa più aggressiva (hooking completo) |

## Esempi pratici

```bash
# Setup completo Kali
sudo apt install apache2 -y
sudo systemctl start apache2
cd /var/www/html
sudo git clone https://github.com/Valve/fingerprintjs2
sudo chown -R www-data:www-data fingerprintjs2

# Edit index.html: pretext + XHR POST
# Crea fp.php (vedi sopra)

# Esegui campagna phishing -> link a http://attacker.com/fingerprintjs2/
# Output:
cat /var/www/html/fingerprintjs2/fingerprint.txt
# Client IP: 10.0.0.45
# user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/123
# language = en-US
# ...
```

## Punti d'attenzione per l'esame eCPPT

- **Client Fingerprinting** è una tecnica **active recon** (interagisce con browser via link).
- Richiede **interazione utente** (click sul link inviato via phishing).
- **JavaScript-dependent**: browser privacy-focused (Brave) o estensioni (NoScript, uBlock) possono bloccarla.
- Lo scopo è ottenere info per **payload tailor-made** (es. macro per Office 2019 vs 365).
- **FingerprintJS2** = libreria standard menzionata.
- **whatismybrowser.com/useragents/parse** = tool per UA parsing.
- L'OS detection è più affidabile su Windows/macOS che Linux.

## Collegamenti con altri video

- Precedente: [[04_Client-Side Information Gathering]]
- Prossimo: [[06_Introduction to Social Engineering_1717706352952]]
- Browser hooking avanzato: [[025_Establishing a Shell Through the Victim's Browser]] (BeEF)
- Uso del fingerprint per scegliere payload: [[010_Resource Development & Weaponization]]
