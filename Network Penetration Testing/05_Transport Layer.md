# 05 — Transport Layer (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 5/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_Transport Layer.txt](05_Transport Layer.txt) · [05_Transport Layer.srt](05_Transport Layer.srt)

## Concetti chiave

- Il **Transport Layer (L4)** garantisce comunicazione end-to-end, error detection, flow control, segmentation.
- Due protocolli principali: **TCP** (connection-oriented, reliable, ordered) e **UDP** (connectionless, unreliable, fast).
- TCP usa il **three-way handshake** (SYN → SYN/ACK → ACK) per stabilire la connessione.
- **Flag TCP** chiave: **SYN, ACK, FIN, RST, PSH, URG** — fondamentali per capire i vari Nmap scan type.
- **Port range**: 0-1023 well-known (IANA), 1024-49151 registered, 49152-65535 dynamic/ephemeral.

## Spiegazione approfondita

### TCP — caratteristiche
- **Connection-oriented**: handshake prima di scambiare dati ("virtual circuit").
- **Reliable**: ACK + retransmission dei segment persi/corrotti.
- **Ordered**: i segment vengono riordinati prima di passare al layer superiore.
- Usato da: **HTTP, HTTPS, FTP, SSH, SMTP, Telnet** — tutto ciò che richiede ordine/integrità.

### Three-way handshake
| Step | Mittente | Flag | Note |
|---|---|---|---|
| 1 | Client → Server | **SYN** | Initial Sequence Number (ISN) random |
| 2 | Server → Client | **SYN + ACK** | ACK = ISN_client + 1; genera proprio ISN |
| 3 | Client → Server | **ACK** | ACK = ISN_server + 1; connessione stabilita |

Da questo punto in poi i dati possono fluire bidirezionalmente. La chiusura usa **FIN** (o **RST** per abort).

### TCP header — campi rilevanti
- **Source port** (16 bit) / **Destination port** (16 bit)
- **Sequence Number** / **Acknowledgement Number**
- **Control flags**: URG, ACK, PSH, RST, SYN, FIN
- Window size, checksum, urgent pointer, options

### UDP — caratteristiche
- **Connectionless**: nessun handshake, ogni datagram è indipendente.
- **Unreliable, stateless**: nessuna garanzia di consegna, no retransmission.
- **Header più piccolo** → minore overhead → più veloce.
- Usato da: **DNS, DHCP, SNMP, VoIP/SIP, video streaming, online gaming**.

### Comparativa TCP vs UDP

| Aspetto | TCP | UDP |
|---|---|---|
| Connessione | Three-way handshake | Connectionless |
| Affidabilità | Reliable, retransmission | Unreliable |
| Ordine | Ordered | Out-of-order possibile |
| Header | Grande | Piccolo |
| Latency | Maggiore | Minore |
| Applicazioni | Web, email, file transfer | Real-time, streaming, gaming, VoIP |

### Port ranges
| Range | Tipo | Esempi |
|---|---|---|
| 0–1023 | **Well-known** (IANA standardized) | 21 FTP, 22 SSH, 23 Telnet, 25 SMTP, 53 DNS, 80 HTTP, 110 POP3, 443 HTTPS |
| 1024–49151 | **Registered** | 3306 MySQL, 3389 RDP, 8080 HTTP-alt, 27017 MongoDB |
| 49152–65535 | **Dynamic / ephemeral** | Source port lato client |

Totale: max **65 535** porte.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `netstat -antp` | Lista connessioni TCP attive con PID/programma (Linux) | `-a` all, `-n` numeric, `-t` tcp, `-p` process |
| `netstat -ano` | Equivalente Windows | |
| `ss -tnp` | Alternativa moderna a `netstat` su Linux | |
| **Wireshark** | Visualizza handshake e flag TCP | Filtro `tcp` |

## Esempi pratici

```bash
# Visualizza connessioni TCP attive prima/dopo aprire un browser
netstat -antp

# Apri firefox e raggiungi https://google.com
# Rilancia netstat: vedrai stato ESTABLISHED verso :443

# Cattura il three-way handshake con Wireshark
# Filtro: tcp.flags.syn == 1
# Sequenza attesa:
#   1) client -> server : [SYN]    seq=0
#   2) server -> client : [SYN,ACK] seq=0 ack=1
#   3) client -> server : [ACK]    seq=1 ack=1
# Subito dopo, traffico TLS (L6) per HTTPS.
```

## Punti d'attenzione per l'esame eCPPT

- **Three-way handshake**: ricorda l'esatta sequenza **SYN → SYN/ACK → ACK**. Domanda ricorrente.
- **Flag TCP** mappa con scan Nmap (vedi [[011_Port Scanning with Nmap]]):
  - **`-sS`** SYN scan (half-open): invia SYN, riceve SYN/ACK → porta aperta; RST → chiusa.
  - **`-sT`** Connect scan: completa handshake (rumoroso, niente raw socket).
  - **`-sF`** FIN scan: solo FIN.
  - **`-sX`** Xmas scan: FIN+PSH+URG.
  - **`-sN`** Null scan: nessun flag.
  - **`-sA`** ACK scan: solo ACK (firewall detection).
- **Porte well-known da sapere a memoria**: 21 FTP, 22 SSH, 23 Telnet, 25 SMTP, 53 DNS, 80 HTTP, 110 POP3, 111 RPCbind, 135 MS-RPC, 139 NetBIOS-SSN, 143 IMAP, 161 SNMP (UDP), 443 HTTPS, 445 SMB, 389 LDAP, 3306 MySQL, 3389 RDP, 5985/5986 WinRM.
- **UDP scan** (`-sU`) è più lento e ambiguo (no handshake) — esame può chiedere perché.
- **Stato `TIME_WAIT`** appare dopo terminazione → indica connessione chiusa di recente.
- **Source port lato client** è quasi sempre random (>49152). Può essere falsificato con `--source-port` per evasion.

## Collegamenti con altri video

- Precedente: [[04_Network Layer]]
- Prossimo: [[06_Network Mapping]] — inizia la parte pratica
- TCP scan types: [[011_Port Scanning with Nmap]]
- UDP scan: [[011_Port Scanning with Nmap]] e [[019_SNMP_Enumeration.mp4]]
- Source port spoofing per evasion: [[014_Firewall Detection & IDS Evasion]]
