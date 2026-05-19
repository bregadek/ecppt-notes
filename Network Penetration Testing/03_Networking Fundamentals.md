# 03 — Networking Fundamentals (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 3/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Networking Fundamentals.txt](03_Networking Fundamentals.txt) · [03_Networking Fundamentals.srt](03_Networking Fundamentals.srt)

## Concetti chiave

- I **network protocol** standardizzano la comunicazione tra host eterogenei (HW/SW/OS diversi).
- Le comunicazioni in rete avvengono tramite **packet** = stream di bit su mezzo fisico, strutturati in **header** (metadati: src/dst, ecc.) + **payload** (dati reali).
- L'**OSI model** è un framework **a 7 layer** sviluppato da **ISO**, usato come riferimento concettuale per progettare/comprendere lo stack di rete.
- Ogni layer **dipende** dal layer sottostante (Transport non funziona senza Network, Network non funziona senza Data Link, ecc.).
- I due layer più rilevanti per Nmap sono **Network (Layer 3)** e **Transport (Layer 4)** — coperti nei prossimi due video.

## Spiegazione approfondita

### Packet structure
Ogni packet di un protocollo standard ha la struttura:
- **Header** — struttura protocol-specific (es. IP header con src/dst IP; TCP header con src/dst port); permette al ricevente di interpretarlo correttamente.
- **Payload** — dato applicativo trasportato (porzione di file, messaggio, ecc.).

### OSI Model (7 layer, dal basso verso l'alto)

| # | Layer | Cosa fa | Esempi |
|---|---|---|---|
| 1 | **Physical** | Connessione fisica tra dispositivi; mezzi di trasmissione | USB, Ethernet, coax, fibra, hub |
| 2 | **Data Link** | Accesso al medium fisico, framing, error detection a livello locale | Ethernet frame, switch, MAC |
| 3 | **Network** | Logical addressing & routing tra reti | **IP, ICMP, IPsec** |
| 4 | **Transport** | End-to-end communication, flow control | **TCP, UDP** |
| 5 | **Session** | Gestione sessioni/connessioni tra applicazioni, sync, token | NetBIOS, RPC, API |
| 6 | **Presentation** | Traduzione, encryption, compression dei dati | SSL/TLS, SSH, JPEG, GIF, IMAP |
| 7 | **Application** | Servizi di rete agli end-user/app | HTTP, FTP, IRC, SSH, DNS |

Note di Alexis:
- "TCP/IP" indica che **TCP gira sopra IP** (TCP è L4, IP è L3) e **non** può girare su altri Network protocol.
- L'OSI non è un blueprint rigido ma un **reference model**.
- Capire l'OSI aiuta a tracciare cosa accade dal cavo Ethernet fino al browser quando si apre `google.com`.

## Comandi & strumenti

Video teorico, nessun comando.

## Esempi pratici

N/A.

## Punti d'attenzione per l'esame eCPPT

- Memorizza l'**ordine dei 7 layer** (mnemonica: *Please Do Not Throw Sausage Pizza Away* — Physical, Data Link, Network, Transport, Session, Presentation, Application).
- Sapere a **quale layer appartiene un protocollo**:
  - **IP, ICMP** → L3 Network
  - **TCP, UDP** → L4 Transport
  - **HTTP, DNS, FTP, SSH** → L7 Application
  - **TLS/SSL** → L6 Presentation (Alexis), spesso considerato L5-6 nelle implementazioni reali
  - **NetBIOS, RPC** → L5 Session
- **Ethernet frames** (L2) ≠ **IP packets** (L3) ≠ **TCP segments** (L4). Differenza ricorrente nelle domande.
- L'**header** contiene metadata, il **payload** contiene i dati. Domande tipo "dove si trovano src/dst port?" → TCP/UDP header (L4).
- Nmap opera principalmente a **L3 (ICMP, IP)** e **L4 (TCP, UDP)**; gli **NSE script** salgono a L7.

## Collegamenti con altri video

- Precedente: [[02_Active Information Gathering]]
- Prossimo: [[04_Network Layer]] (dettaglio Layer 3)
- Seguente: [[05_Transport Layer]] (dettaglio Layer 4)
- Applicazione pratica dei layer in scanning: [[09_Host Discovery with Nmap - Part 1]] · [[011_Port Scanning with Nmap]]
