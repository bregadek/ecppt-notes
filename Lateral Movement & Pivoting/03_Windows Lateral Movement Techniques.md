# 03 — Windows Lateral Movement Techniques

> **Modulo:** Lateral Movement & Pivoting · **Video:** 3/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Windows Lateral Movement Techniques.txt](03_Windows Lateral Movement Techniques.txt) · [03_Windows Lateral Movement Techniques.srt](03_Windows Lateral Movement Techniques.srt)

## Concetti chiave

- Il lateral movement Windows è quasi sempre **credential-based** (clear-text password, NTLM hash, Kerberos ticket).
- Non è exploitation: usa **autenticazione legittima** → difficile da rilevare.
- Tecniche principali: **Pass-the-Hash (PTH)**, **Pass-the-Ticket (PTT)**, **Credential Reuse**, **Golden/Silver Tickets** (AD).
- Protocolli abusabili: **SMB (445)**, **RDP (3389)**, **WinRM (5985/5986)**, **WMI (RPC 135 + dynamic)**.
- Tool chiave: PsExec, SMBExec, WMIExec, Impacket, CrackMapExec, Evil-WinRM, Mimikatz.

## Spiegazione approfondita

### Credential-based Lateral Movement
Per "credenziali" si intendono:
- **Clear-text username/password**
- **NTLM hash** (Windows)
- **Kerberos ticket** (AD — trattato nel corso AD)

Una volta ottenute, NON serve exploit ulteriore: si autentica direttamente verso altri host. Difficile da detectare perché appare come login legittimo.

### Tecniche

1. **Pass-the-Hash (PTH)** — uso dell'**NTLM hash** per autenticarsi senza conoscere la password in chiaro. Possibile perché SMB su Windows accetta hash NTLM. Tool: Mimikatz (dump), Metasploit `psexec`, Impacket (`psexec.py`, `smbexec.py`, `wmiexec.py`), CrackMapExec.
2. **Pass-the-Ticket (PTT)** — uso di ticket Kerberos catturati. Tool: Mimikatz, Rubeus. **Coperto nel corso AD, non qui.**
3. **Credential Reuse** — uso di **password in chiaro** per autenticarsi su altri sistemi. Permette di usare protocolli che NON accettano hash (RDP, WinRM via basic auth).
4. **Golden/Silver Tickets** — forge di ticket Kerberos per persistence. **Coperto nel corso AD, non qui.**

### Protocolli Windows abusabili (porte fondamentali per l'esame)

| Protocollo | Porta | Auth | PTH? | Tool |
|---|---|---|---|---|
| **SMB** | 445 (139 NetBIOS) | NTLM | **Sì** | PsExec, SMBExec, WMIExec, CME |
| **RDP** | 3389 | NTLM/Kerberos | **No** (solo clear-text) | xfreerdp, rdesktop, MSF |
| **WinRM** | 5985 (HTTP) / 5986 (HTTPS) | NTLM/Basic/Kerberos | Sì (con tool ad hoc) | Evil-WinRM, CME, PS Remoting |
| **WMI** | 135 RPC + dynamic (49152-65535) | NTLM | **Sì** | wmiexec.py, MSF |

### Authenticated Remote Code Execution
Tutte le tecniche convergono in: autenticazione + esecuzione comandi/payload remoto. Tool ricorrenti:
- **PsExec** (SysInternals) / **psexec.py** (Impacket) — crea servizio temporaneo via SMB.
- **WMI** via `wmiexec.py` o moduli MSF — esecuzione via DCOM/RPC, NO servizio.
- **PowerShell Remoting** (`Invoke-Command`, `Enter-PSSession`) su WinRM.
- **Empire** C2 (PowerShell).
- **CrackMapExec** — Swiss-army knife per spray/PTH/exec su SMB/WinRM/MSSQL/SSH.

## Comandi & strumenti

| Tool | Categoria | Scopo |
|---|---|---|
| **PsExec** (SysInternals) | Windows native exe | Esecuzione remota via SMB, crea servizio |
| **Impacket psexec.py** | Python | Equivalente Linux di PsExec |
| **Impacket smbexec.py** | Python | Come psexec ma più silenzioso (no servizio classico) |
| **Impacket wmiexec.py** | Python | Esecuzione via WMI/DCOM |
| **CrackMapExec (CME)** | Multi-proto | Spray, PTH, exec, moduli |
| **Evil-WinRM** | WinRM | Shell interattiva PS via WinRM |
| **Mimikatz** | Credential dump | Estrazione hash NTLM, ticket Kerberos |
| **Metasploit `exploit/windows/smb/psexec`** | MSF | PTH via Meterpreter |

## Esempi pratici

Video teorico — esempi pratici nei video successivi (04-010).

## Punti d'attenzione per l'esame eCPPT

- **Porte da memorizzare**: SMB 445, RDP 3389, WinRM 5985/5986, WMI 135+dynamic.
- **RDP NON supporta PTH**: serve clear-text password.
- **PsExec richiede privilegi amministrativi locali** sul target (utente in local Administrators) per creare il servizio temporaneo.
- **NTLM ancora supportato** anche in ambienti Kerberos per backward compat e local accounts.
- **NTLMv1 deprecato (DES)**, NTLMv2 standard.
- **Local accounts vs domain accounts**: PsExec/SMBExec funzionano con entrambi; in AD un domain admin ha scope wider.
- **Detection**: l'auth è legittima ma il protocollo può essere anomalo per quell'utente (es. SMB exec auth dall'account dev su un DC).

## Collegamenti con altri video

- Precedente: [[02_Introduction to Lateral Movement & Pivoting]]
- Prossimi (tecniche pratiche): [[04_Lateral Movement with PsExec]] · [[05_Lateral Movement with SMBExec]] · [[06_Lateral Movement with CrackMapExec]]
- Protocolli specifici: [[07_Lateral Movement via RDP]] · [[08_Lateral Movement via WinRM]]
- Pass-the-Hash: [[09_Pass-the-Hash with Metasploit]] · [[010_Pass-the-Hash with WMIExec]]
- Linux: [[011_Linux Lateral Movement Techniques]]
