# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This directory contains video lessons for the **eCPPT (eLearnSecurity Certified Professional Penetration Tester)** certification course. The goal is to use Claude to help the student study, take notes, create cheat sheets, practice commands, and prepare for the exam.

There is no code to build or test — the primary tasks are:
- Creating study notes and summaries per module
- Building command references and cheat sheets
- Answering questions about techniques covered in the videos
- Simulating exam-style questions and scenarios

## Course Modules & Video Structure

Each folder is a self-contained module. Videos are numbered (01_, 02_, ...) and follow a progression from intro to conclusion.

| Module | Key Topics |
|---|---|
| **Network Penetration Testing** | Nmap, enumeration (SMB, SNMP), SMB Relay, MSSQL RCE, NTLM hash dumping, black-box pentest lab |
| **Web Application Penetration Testing** | OWASP methodology, XSS (reflected/stored/DOM), SQLi (error-based, union-based), Burp Suite, Nikto, Amass |
| **Active Directory Penetration Testing** | AD auth, BloodHound, PowerView, Password Spraying, AS-REP Roasting, Kerberoasting, Pass-the-Hash/Ticket, Golden/Silver Tickets |
| **Privilege Escalation** | PowerUp, PrivescCheck, Windows (service perms, registry autoruns, DLL hijacking, token impersonation, Juicy Potato, UAC bypass) and Linux (SUID, SUDO, shared library injection) |
| **Lateral Movement & Pivoting** | PsExec, SMBExec, CrackMapExec, RDP, WinRM, Pass-the-Hash (Metasploit/WMIExec), SOCKS proxy, SSH tunneling, reGeorg, port forwarding |
| **Client-Side Attacks** | Social engineering, phishing (Gophish), VBA macros, MacroPack, HTA attacks, HTML smuggling, browser shells |
| **Command & Control (C2)** | C2 frameworks, PowerShell-Empire, Starkiller, C2 Matrix, red team ops |
| **PowerShell for Pentesters** | PS CLI, cmdlets, modules, scripts, objects, Empire, AV evasion with Shellter, obfuscation |
| **Exploit Development Buffer Overflows** | Stack overflows, fuzzing, SEH, Windows SEH overflow (EasyChat) |
| **System Security & x86 Assembly Fundamentals** | CPU architecture, registers, process memory, stack/stack frames, x86 assembly basics |

## How to Help the Student

When asked to study a specific module or topic:
1. Provide a concise summary of the key concepts.
2. List the most important tools and commands with usage examples.
3. Highlight what is most likely to appear on the eCPPT practical exam.
4. Generate practice questions or scenario-based exercises on request.

### eCPPT Exam Context (formato 2024)
L'esame eCPPT nel formato 2024 è composto da **45 domande a risposta multipla** su un ambiente pratico. Non è richiesta la consegna di un report. High-priority areas for exam success:
- Full Nmap scanning methodology and service enumeration
- Exploitation with Metasploit and manual techniques
- Privilege escalation (both Windows and Linux paths)
- Lateral movement and pivoting through multi-subnet networks
- Active Directory attacks (BloodHound enumeration → Kerberoasting/Pass-the-Hash → Domain Admin)

### Study Material Format
When creating notes or cheat sheets, prefer:
- Markdown files saved inside the relevant module folder
- Command tables with syntax, flags, and a one-line description
- Attack flow diagrams described in text (e.g., step-by-step attack chains)

## Pipeline di trascrizione automatica

Per ogni video `.mp4` esistono (o saranno generati) tre file fratelli nella **stessa cartella**:
- `<basename>.txt` — trascrizione piana (Whisper `large-v3`, lingua `en`)
- `<basename>.srt` — trascrizione con timestamp
- `<basename>.md` — **appunti finali** (teoria + comandi + tips esame), generati da Claude a partire dal `.txt`

Tooling in `_tools/`:
- `_tools/transcribe_all.py` — pipeline idempotente (salta se `.txt` esiste). Run: `_tools/whisper-env/Scripts/python.exe _tools/transcribe_all.py`.
  - Flag utili: `--only <substring>` (filtra per path), `--limit N`, `--force` (ritrascrivi).
- `_tools/whisper-env/` — venv Python isolato con `faster-whisper` + cuDNN/cuBLAS CUDA 12.
- `_tools/manifest.json` — inventario video↔trascrizione (durata, lingua rilevata, tempi).
- `_tools/transcribe.log` — log esecuzioni.

**Esclusione attiva:** il modulo `Web Application Penetration Testing/` è escluso (vedi `EXCLUDE_DIRS` nello script). 146 video totali in pipeline.

Quando Claude genera o aggiorna un `.md`, deve attingere **principalmente dal `.txt` corrispondente** (fedeltà al contenuto del video reale), arricchendolo con conoscenza tecnica del dominio dove serve. Niente comandi inventati che il video non menziona.
