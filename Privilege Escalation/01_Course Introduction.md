# 01 — Course Introduction (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 1/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Il corso copre **Privilege Escalation** su **Windows** e **Linux** in modo separato (sezioni distinte) perché i due OS sono **molto diversi** in termini di vettori sfruttabili.
- Le tecniche sono **handpicked** in base ad applicabilità nel mondo reale: ciò che effettivamente si trova durante un pentest.
- Il corso parte da **uso di script automatici di privesc** (PowerUp) e arriva a **tecniche avanzate** (DLL Hijacking, UAC Bypass, Shared Library Injection).
- Si assume di **partire da post-exploitation**: il corso NON copre initial access né local enumeration manuale → focus puro sull'elevazione.

## Spiegazione approfondita

### Topic Overview
1. **Introduzione formale a Privilege Escalation** — concetti generali, tipi.
2. **Windows Privilege Escalation** (la sezione più lunga):
   - Script di privesc: **PowerUp** (PowerSploit), **PrivescCheck**.
   - **Locally stored credentials**: Unattended files, Credential Manager, PowerShell history.
   - **Insecure service permissions** (service binary replacement).
   - **Registry AutoRuns** insicuri.
   - **Access Token Impersonation** (Incognito).
   - **Juicy Potato** (token impersonation via DCOM).
   - **UAC Bypass** con UACMe.
   - **DLL Hijacking** (tecnica avanzata).
3. **Linux Privilege Escalation**:
   - Locally stored credentials (riuso password).
   - **Misconfigured file permissions** (es. /etc/shadow scrivibile).
   - **SUID binaries**.
   - **Misconfigured SUDO privileges** (GTFOBins).
   - **Shared Library Injection** (LD_PRELOAD, equivalente Linux del DLL Hijacking).

### Prerequisiti
- **Networking di base**: TCP/UDP/HTTP/DNS, IP, subnetting, routing.
- **OS fundamentals**: navigazione CLI, file system, processi, permessi (Windows e Linux).
- **Exploitation & Post-Exploitation** (livello eJPT o equivalente) — molto importante. Il corso parte da "siamo già dentro".
- **Tool**: Metasploit, Nmap.
- Conoscenza del **pentest lifecycle** (dove cade privesc).

### Learning Objectives
1. Comprendere e definire privilege escalation.
2. Identificare vulnerabilità comuni → riconoscere attack vector tipici su Windows/Linux.
3. Eseguire **system enumeration** in funzione di privesc.
4. Applicare tecniche di privesc su **Windows**: insecure services, token impersonation, ecc., usando Metasploit / PowerShell / PowerUp.
5. Applicare tecniche su **Linux**: SUID, sudo, ecc.
6. Leverage **tecniche avanzate**: DLL hijacking, UAC bypass, Shared Object injection.

## Comandi & strumenti

Video introduttivo — nessun comando eseguito. Strumenti citati che verranno usati:

| Strumento | OS | Uso |
|---|---|---|
| **PowerUp** (PowerSploit) | Windows | Privesc automation script |
| **PrivescCheck** | Windows | Alternativa a PowerUp |
| **Mimikatz / Incognito** | Windows | Token impersonation, credential dump |
| **Juicy Potato** | Windows | Privesc via DCOM |
| **UACMe (akagi64)** | Windows | UAC bypass (60+ tecniche) |
| **Metasploit** | Both | Exploit framework |
| **GTFOBins** | Linux | Catalogo abuso binari SUID/SUDO |

## Esempi pratici

N/A — video introduttivo.

## Punti d'attenzione per l'esame eCPPT

- L'esame eCPPT include **scenari pratici di privesc** sia Windows sia Linux: devi sapere distinguere immediatamente i due ecosistemi.
- **Mindset**: si è già dentro → la domanda d'esame è "come elevo?", non "come entro?".
- Memorizza la **mappa di attacco**:
  - Windows → script automatici, credential reuse, service misconf, token, UAC, DLL hijack.
  - Linux → credential reuse, file perms, SUID, SUDO, LD_PRELOAD.
- I prerequisiti dichiarati corrispondono al **baseline eCPPT** (eJPT-level).

## Collegamenti con altri video

- Prossimo: [[02_Introduction to Privilege Escalation]] — definizioni formali, vertical vs horizontal.
- Sezione Windows: [[03_Privilege Escalation with PowerUp]] → [[013_DLL Hijacking]].
- Sezione Linux: [[014_Locally Stored Credentials]] → [[018_ Shared Library Injection]].
- Recap finale: [[019_Course Conclusion]].
