# 01 — Course Introduction (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 1/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Il corso copre **Network Penetration Testing** end-to-end: host discovery, port scanning, service enumeration, MITM/network attacks, Windows/Linux exploitation & post-exploitation.
- Approccio "tool-first": non si spiegano i fondamentali di TCP/IP in profondità, si entra subito in tecniche e tool.
- Strumenti core anticipati: **Nmap, NSE, smbmap, Wireshark, arpspoof, dnsspoof, Responder, Metasploit**.
- Forte focus su **SMB relaying** e attacchi network-based per ottenere RCE su Windows.
- Prerequisiti chiave (raccomandati): networking di base + esperienza pratica di exploitation/post-exploitation Windows/Linux (livello eJPT).

## Spiegazione approfondita

### Topic Overview
1. **Host Discovery & Port Scanning** — tecniche di scoperta host su LAN, port scanning TCP/UDP, fondamentali di networking richiamati al volo per capire i protocolli.
2. **Service Enumeration** — enumerazione avanzata di servizi tramite **NSE** (Nmap Scripting Engine) e tool protocollo-specifici (smbmap, snmpwalk, ecc.).
3. **Man-in-the-Middle & Network-based Attacks** — ARP spoofing, DNS spoofing, NBT-NS / LLMNR poisoning, SMB relay; uso di **arpspoof, dnsspoof, Responder**.
4. **Windows & Linux Exploitation + Post-Exploitation** — labs realistici che simulano un piccolo pentest end-to-end.

### Prerequisiti dichiarati
- **Networking**: IP, subnetting, routing, network devices; protocolli TCP, UDP, HTTP, DNS.
- **OS**: uso pratico di Windows e Linux, CLI/terminal, file system, processi, permessi.
- **Pentest hands-on** (il più importante): exploitation/post-exploitation su Windows e Linux, targeting di SMB, RDP, WinRM per initial access; uso di Metasploit.
- **Tool**: Metasploit, Nmap, Wireshark; conoscenza della pentest methodology e lifecycle.

Alexis sottolinea che, dei prerequisiti, i due **primari** sono **networking fundamentals** ed **esperienza di exploitation** — il corso non rifà la teoria di TCP, va dritto agli use-case di network pentest.

### Learning Objectives
- **Host discovery & port scanning**: identificare host attivi con diverse tecniche; usare port scanner per trovare servizi su Windows e Linux.
- **Service enumeration**: estrarre informazioni utili da servizi via **NSE script** e tool protocollo-specifici (SMB, NetBIOS, SMTP, FTP, ecc.).
- **MITM & network attacks**: eseguire **ARP spoofing, DNS spoofing, ARP poisoning, NBT-NS poisoning**; usare **arpspoof, dnsspoof, Responder**.
- **Exploitation/Post-Exploitation**: sfruttare protocolli/servizi Windows e Linux per initial access; eseguire **SMB relaying**; condurre attività di post-exploitation su entrambi gli OS.

## Comandi & strumenti

Video introduttivo, nessun comando eseguito. Tool che verranno usati nel modulo:

| Strumento | Categoria | Scopo |
|---|---|---|
| **Nmap + NSE** | Discovery, scanning, enum | Backbone del modulo, intero blocco di 8+ video |
| **smbmap** | SMB enumeration | Enum share, permessi |
| **Wireshark** | Traffic analysis | Verifica MITM, packet inspection |
| **arpspoof / dnsspoof** (dsniff) | MITM | ARP/DNS spoofing |
| **Responder** | LLMNR/NBT-NS poisoning | Cattura NTLM hash, base per SMB relay |
| **Metasploit** | Exploitation framework | `smb_relay`, post-exploitation modules |
| **Impacket suite** | Network attacks | `ntlmrelayx.py`, `psexec.py`, `secretsdump.py` |
| **Hashcat / John** | Cracking | NTLM, NTLMv2 |

## Esempi pratici

N/A — video introduttivo. La prima sezione pratica inizia da **02 — Active Information Gathering**.

## Punti d'attenzione per l'esame eCPPT

- L'esame (formato 2024) è **45 domande a risposta multipla in ambiente pratico**: la maggior parte dei task del modulo Network richiede di **eseguire scan/enum reali** e leggere l'output.
- Memorizza la **mappa del corso** in 4 blocchi (Discovery/Scan → Enum → MITM → Exploit/Post-Exploit): le domande tipicamente seguono la **kill chain di rete**.
- I tool dichiarati nelle learning objectives sono quelli **attesi all'esame**: Nmap, NSE, smbmap, Responder, arpspoof, dnsspoof, Metasploit.
- Differenze concettuali da memorizzare già da ora:
  - **ARP spoofing** (Layer 2) vs **DNS spoofing** (Layer 7).
  - **LLMNR poisoning** vs **NBT-NS poisoning** (entrambi usati da Responder).
  - **SMB relay** richiede **SMB signing disabilitato** sul target.

## Collegamenti con altri video

- Prossimo: [[02_Active Information Gathering]]
- Blocco Discovery/Scan: [[06_Network Mapping]] · [[07_Host Discovery Techniques]] · [[09_Host Discovery with Nmap - Part 1]]
- Blocco Enumeration: [[017_Introduction to Enumeration]]
- Blocco MITM/Network attacks: [[021_SMB_Relay_Attack.mp4]]
- Blocco Exploit/Post-Exploit lab: [[022_MSSQL_DB_User_Impersonation_to_RCE.mp4]] · [[023_Linux_Black-Box_Penetration_Test.mp4]] · [[025_Windows_Post-Exploitation_Lab.mp4]]
- Wrap-up: [[026_Course Conclusion_1717745829269]]
