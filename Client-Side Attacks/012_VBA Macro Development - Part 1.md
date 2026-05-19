# 012 — VBA Macro Development - Part 1 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 12/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_VBA Macro Development - Part 1.txt](012_VBA Macro Development - Part 1.txt) · [012_VBA Macro Development - Part 1.srt](012_VBA Macro Development - Part 1.srt)

## Concetti chiave

- Setup ambiente dev: **Windows 10 + Office 2016 (Professional Plus)** + Developer tab + Trust Center con **Trust access to VBA project object model**.
- Sintassi base VBA: `Sub <name>() ... End Sub`, `Dim x As <type>`, commenti con `'`, `MsgBox`.
- Run macro nel VBA IDE = **F5** (test prima di salvare).
- `WScript.Shell` per eseguire programmi esterni: `CreateObject("WScript.Shell").Run cmd, windowStyle, waitOnReturn`.
- **windowStyle** values: `0=hidden`, `1=normal`, `2=minimized`, `3=maximized`, `4=last position`.
- **waitOnReturn** = `False` (don't wait) / `True` (sync wait).
- Save As → **Word Macro-Enabled Document (.docm)** per persistere la macro.
- Distinzione critica: macro link a **document specifico** vs all active templates → sempre selezionare il documento attuale.

## Spiegazione approfondita

### Setup ambiente
1. Windows 10 + Office 2016 installato.
2. File → Options → Customize Ribbon → check **Developer**.
3. Trust Center Settings → Macro Settings:
   - Disable all macros with notification (default, yellow bar).
   - Trust access to VBA project object model ✓ (per testing).

### Workflow macro
1. Developer tab → Macros (o `Alt+F8`).
2. **Macros in**: selezionare il documento corrente (non "All active templates").
3. Name → Create → apre VBA IDE.

### VBA IDE
- Tools → Options → cambia font size (Consolas 14).
- Run (F5) per eseguire.
- Debug controls per breakpoint.

### Sintassi base
```vba
Sub HelloWorld()
    ' commento singola linea
    MsgBox "Hello World", vbInformation, "Demo Title"
End Sub
```
- `Sub` = subroutine.
- `MsgBox <text>, <buttons>, <title>` — VB info constant (`vbInformation`, `vbCritical`, etc.).
- Senza parentesi per chiamate semplici (stile VB classico).

### Variabili
```vba
Dim payload As String
payload = "calc.exe"

Dim ws As Worksheet
Set ws = ThisWorkbook.Sheets.Add
ws.Name = "Red Team Tracker"
```
- `Dim <name> As <type>`.
- `Set` per oggetti (Worksheet, Object).
- Type system: String, Integer, Long, Boolean, Object, Worksheet, etc.

### Bottone in Excel
1. Developer → Insert → Button.
2. Assign Macro → "Button1_Click" → New.
3. Codice eseguito al click:
```vba
Sub Button1_Click()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets.Add
    ws.Name = "Red Team Tracker"
    MsgBox "Tracker generated in new sheet"
End Sub
```

### WScript.Shell — Run method
Due varianti viste:
```vba
' Variant 1: inline create object
Sub POC()
    Dim payload As String
    payload = "calc.exe"
    CreateObject("WScript.Shell").Run payload, 0
End Sub
```
```vba
' Variant 2: object reference
Sub POC2()
    Dim WSH As Object
    Set WSH = CreateObject("WScript.Shell")
    WSH.Run "notepad.exe", 1, False
End Sub
```

### Window Style (valori run)
| Value | Comportamento |
|---|---|
| 0 | **Hidden** + activates another window |
| 1 | Normal (default) |
| 2 | Minimized |
| 3 | Maximized |
| 4 | Last position/size |

Per malware: **windowStyle=0** + **waitOnReturn=False** → exec silente.

### waitOnReturn
- `True` → macro aspetta che il processo termini.
- `False` → fire-and-forget.

### Salvataggio
- File → Save As → Browse → Desktop.
- Save as type: **Word Macro-Enabled Document (*.docm)**.
- Se salvi come `.docx` → macro scompaiono.

## Comandi & strumenti

| Elemento | Sintassi/Path |
|---|---|
| Developer tab | File → Options → Customize Ribbon |
| Trust Center | File → Options → Trust Center → Macro Settings |
| Apri VBA IDE | Alt+F11 |
| Run macro | F5 nel IDE |
| Subroutine | `Sub Name()` ... `End Sub` |
| Variabile | `Dim x As String` |
| MsgBox | `MsgBox "text", vbInformation, "title"` |
| WScript Shell | `CreateObject("WScript.Shell").Run "cmd", 0, False` |
| Save | `.docm` (Word Macro-Enabled) |

## Esempi pratici

```vba
' Hello World
Sub HelloWorld()
    MsgBox "Hello World", vbInformation, "Demo"
End Sub

' Lancia calc.exe hidden
Sub POC()
    Dim payload As String
    payload = "calc.exe"
    CreateObject("WScript.Shell").Run payload, 0, False
End Sub

' Lancia notepad maximized
Sub POC2()
    Dim WSH As Object
    Set WSH = CreateObject("WScript.Shell")
    WSH.Run "notepad.exe", 3, False
End Sub
```

## Punti d'attenzione per l'esame eCPPT

- Memorizzare **`CreateObject("WScript.Shell").Run`** + signature (cmd, windowStyle, waitOnReturn).
- **windowStyle=0** = hidden (per attacchi).
- Save come **`.docm`** obbligatorio per macro.
- **Sub HelloWorld()** dichiara una subroutine; per auto-exec usa `Document_Open()` o `AutoOpen()` (vedi video successivo).
- VBA IDE accessibile via **Alt+F11** o Developer → Visual Basic.
- "Macros in: Document1" vs "All active templates" — sempre il documento corrente.
- Possibile domanda: "Come esegui `calc.exe` da macro?" → `CreateObject("WScript.Shell").Run "calc.exe", 0, False`.

## Collegamenti con altri video

- Precedente: [[011_VBA Macro Fundamentals]]
- Prossimo: [[013_VBA Macro Development - Part 2]] — auto-exec events + payload.
- WScript usage avanzato: [[015_VBA PowerShell Dropper]] · [[016_VBA Reverse Shell Macro with Powercat]]
- ActiveX trigger alternativi: [[017_Using ActiveX Controls for Macro Execution]]
