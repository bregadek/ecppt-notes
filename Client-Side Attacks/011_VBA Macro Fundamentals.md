# 011 — VBA Macro Fundamentals (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 11/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_VBA Macro Fundamentals.txt](011_VBA Macro Fundamentals.txt) · [011_VBA Macro Fundamentals.srt](011_VBA Macro Fundamentals.srt)

## Concetti chiave

- **VBA = Visual Basic for Applications** — linguaggio di scripting Microsoft per automazione Office (Word, Excel, PowerPoint, Access, Outlook).
- VBA può chiamare **Windows API** + **WScript** (shell, run, env vars) → potere quasi nativo.
- **Macro** = blocco di codice VBA embedded in documento Office che automatizza task.
- Storia: pre-2003 macro **auto-eseguite**; da Office 2003 prompt; da Office 2007 **nuovi formati** (`docx` no-macro vs `docm` macro-enabled).
- Formati Office: **docx, dotx (no macro)** vs **docm, dotm (macro)**.
- Validazione file: **wwlib.dll** controlla struttura Open Office XML — non l'estensione.
- Trick: `.docm` rinominato `.rtf` mantiene esecuzione macro (con caveat, non stabile su Office 2016).
- **WScript.Shell** in VBA → esecuzione comandi esterni (PowerShell, cmd, payload). Vettore preferito per initial access.

## Spiegazione approfondita

### VBA in dettaglio
- Tightly integrated in Office.
- IDE built-in in ogni Office app (Developer tab → Visual Basic).
- Sintassi simile a Visual Basic / BASIC: keywords, operators, variables, control structures.
- Oggetti: Worksheet, Cell, Range, Document, Application.
- Eventi: **Document_Open**, **Auto_Open**, **Workbook_Open** — eseguono macro automaticamente all'apertura del doc.

### Macro = arma
- Già nel 1990s erano vettore primario di virus (es. Melissa).
- Pre-2003 auto-exec. Post-2003 prompt utente. Post-2007 estensioni separate.
- Oggi: utente deve **Enable Content** → social engineering critico.

### Formati Office (memorizza per esame)

| Estensione | Macro? | Tipo |
|---|---|---|
| `.docx` | NO | Document standard |
| `.docm` | **SI** | Document macro-enabled |
| `.dotx` | NO | Template standard |
| `.dotm` | **SI** | Template macro-enabled |
| `.xlsx` / `.xlsm` | NO / SI | Excel doc |
| `.pptx` / `.pptm` | NO / SI | PowerPoint |
| `.doc` (97-2003) | SI | Legacy, può contenere macro |
| `.rtf` | NO by design | Ma `.docm` rinominato `.rtf` può eseguire (instabile su Office 2016) |

### Validazione file
- `wwlib.dll` valida la struttura Open Office XML.
- L'estensione **non determina** apertura/esecuzione.
- Quindi rinominare `.docm` → `.docx` NON funziona (validazione fallisce per file macro-enabled).

### WScript object
- **WScript** = Windows Script Host object model.
- VBA può chiamare `CreateObject("WScript.Shell")` per:
  - Run external programs.
  - Manipulate files/folders.
  - Read env variables.
  - Execute shell commands.
- È il **vettore #1** per VBA malware: chiamare PowerShell, cmd, payload.

### Macro nei client-side attack
- **Delivery mechanism**: doc è il wrapper, payload è la macro.
- **Social engineering**: nome file invitante (`Salaries.docm`, `Invoice.docm`, `Resume.docm`).
- **Vulnerability exploitation**: macro + ActiveX + embedded objects.
- **Payload delivery**: macro come **dropper** (scarica payload da remote) o reverse shell **inline**.

### Eventi auto-execute
| Evento | App | Quando |
|---|---|---|
| `Document_Open()` | Word | All'apertura doc |
| `AutoOpen()` | Word | Legacy, retro-compat |
| `Workbook_Open()` | Excel | All'apertura workbook |
| `Auto_Open()` | Excel | Legacy |
| `Document_Close()` / `AutoClose()` | Word | Alla chiusura |

## Comandi & strumenti

| Step | Path |
|---|---|
| Abilita Developer tab | File → Options → Customize Ribbon → Developer ✓ |
| Apri VBA IDE | Developer → Visual Basic (Alt+F11) |
| Trust Center | File → Options → Trust Center → Macro Settings |
| Crea macro | Developer → Macros → name → Create |
| `CreateObject("WScript.Shell")` | Accesso a shell run |
| Salva come docm | Save As → Word Macro-Enabled Document (*.docm) |

## Esempi pratici

```vba
' Esempio macro Document_Open in Word
Sub Document_Open()
    Dim payload As String
    payload = "calc.exe"
    CreateObject("WScript.Shell").Run payload, 0, False
End Sub
```

```vba
' Excel auto-exec via Workbook_Open
Private Sub Workbook_Open()
    Dim WSH As Object
    Set WSH = CreateObject("WScript.Shell")
    WSH.Run "powershell.exe -NoP -W Hidden -Enc <BASE64>", 0, False
End Sub
```

## Punti d'attenzione per l'esame eCPPT

- **Solo `.docm`, `.dotm`, `.xlsm`, `.pptm`, `.doc` (97-2003)** supportano macro. **NON** `.docx`.
- **Document_Open**, **Auto_Open**, **Workbook_Open** = eventi auto-execute critici da memorizzare.
- **WScript.Shell.Run(cmd, windowStyle, waitOnReturn)** — `windowStyle=0` nasconde la finestra.
- Pre-2007: macro auto-eseguite. Post-2007: serve **Enable Content**.
- Office 2016: bypass `.docm`→`.rtf` non stabile.
- `wwlib.dll` valida struttura, non estensione.
- **Trust Center** controlla policy macro (disable all, prompt, enable all).
- Possibile domanda: "Quale estensione usi per consegnare una macro?" → **.docm** (Word) o **.xlsm** (Excel).

## Collegamenti con altri video

- Precedente: [[010_Resource Development & Weaponization]]
- Prossimo: [[012_VBA Macro Development - Part 1]] — primi macro pratici.
- Weaponization MSF: [[014_Weaponizing VBA Macros with MSF]]
- Dropper PS: [[015_VBA PowerShell Dropper]]
- Reverse shell Powercat: [[016_VBA Reverse Shell Macro with Powercat]]
- ActiveX trigger: [[017_Using ActiveX Controls for Macro Execution]]
