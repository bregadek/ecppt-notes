# 02 — Active Information Gathering (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 2/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Active Information Gathering.txt](02_Active Information Gathering.txt) · [02_Active Information Gathering.srt](02_Active Information Gathering.srt)

## Concetti chiave

- **Active Information Gathering** = il pentester **interagisce direttamente** con il target (probing, scanning) per raccogliere dati e individuare vulnerabilità.
- Si contrappone al **Passive Information Gathering** (OSINT senza interazione: WHOIS, DNS passivo, social media, search engine dorking).
- È la fase che **alimenta tutto il resto del pentest**: enumeration, vuln analysis, exploitation, post-exploitation derivano dai dati raccolti qui.
- Sotto-attività: **network mapping, host discovery, port scanning, service detection, OS fingerprinting**.
- Tool centrale del corso = **Nmap**; il modulo è strutturato per imparare a usarlo in modo efficiente, non solo lanciarlo.

## Spiegazione approfondita

### Penetration testing methodology (richiamo)
1. **Information Gathering** (passive → active)
2. **Enumeration** (separabile, corso a parte)
3. **Vulnerability Analysis & Threat Modeling** — ricerca lowest hanging fruit.
4. **Exploitation**
5. **Post-Exploitation**: local enum, privilege escalation, credential access, persistence, evasion, lateral movement / pivoting.
6. **Reporting & Cleanup**

Il processo è **ciclico**: dopo lateral movement si ricomincia da local enumeration sul nuovo host.

### Active vs Passive
| | Passive IG | Active IG |
|---|---|---|
| Interazione col target | No | Sì |
| Rumore in rete | Nullo | Alto/medio (logs, IDS) |
| Esempi | WHOIS, DNS recon, social, Google dorking | Network mapping, port scan, service detection, OS detection |
| Output | Domini, IP owner, persone, leak | Host attivi, porte aperte, servizi, versioni, OS |

### Cosa copre il corso (sotto active IG)
- **Network mapping** — topologia, host attivi, subnet.
- **Host discovery** — chi è up sulla rete (ARP, ICMP, TCP/UDP probes).
- **Port scanning** — quali porte sono aperte.
- **Service detection** — quale servizio gira (banner, probe).
- **OS fingerprinting** — quale OS gira.

Tutto contestualizzato in **Nmap** + accenni a tool complementari per protocolli specifici (visti nel modulo Enumeration).

## Comandi & strumenti

Video teorico, nessun comando eseguito. Tool annunciati: **Nmap** come backbone.

## Esempi pratici

N/A — la pratica parte da [[06_Network Mapping]] / [[07_Host Discovery Techniques]].

## Punti d'attenzione per l'esame eCPPT

- Domanda tipo: "Quale fase è X?" — `nmap -sS` → **Active Information Gathering**, `whois example.com` → **Passive**.
- Sequenza standard da memorizzare: **Info Gathering → Enumeration → Vuln Analysis → Exploitation → Post-Exploitation → Reporting**.
- L'**enumeration** è considerata fase a sé nel corso, anche se concettualmente fa parte dell'info gathering attivo.
- Il **post-exploitation cycle** (local enum → privesc → creds → persistence → lateral movement) è la base degli scenari pratici dei lab 022/023/025.

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_Networking Fundamentals]]
- Network mapping pratico: [[06_Network Mapping]]
- Host discovery: [[07_Host Discovery Techniques]] · [[09_Host Discovery with Nmap - Part 1]]
- Enumeration: [[017_Introduction to Enumeration]]
