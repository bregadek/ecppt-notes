# 04 — Network Layer (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 4/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Network Layer.txt](04_Network Layer.txt) · [04_Network Layer.srt](04_Network Layer.srt)

## Concetti chiave

- Il **Network Layer (L3)** gestisce **logical addressing, routing e forwarding** dei pacchetti tra reti diverse.
- Protocolli chiave: **IPv4 (32-bit), IPv6 (128-bit), ICMP, DHCP**.
- L'**IPv4 header** contiene campi cruciali per la pentest analysis: version, IHL, total length, identification, flags (DF, MF), TTL, **protocol** (6=TCP, 17=UDP, 1=ICMP), source/destination IP.
- L'**encapsulation** è il principio per cui ogni layer trasporta il pacchetto del layer superiore (Ethernet ⊃ IP ⊃ TCP ⊃ HTTP).
- **Wireshark** mostra graficamente l'incapsulamento OSI e permette di leggere ogni campo dell'header IP/TCP.

## Spiegazione approfondita

### Ruolo del Network Layer
- Calcola il **percorso ottimale** sorgente → destinazione anche tra reti separate (è il layer che abilita "internet").
- Astrae la rete fisica sottostante per offrire un internetwork coerente.

### Protocolli L3

| Protocollo | Funzione |
|---|---|
| **IPv4** | Logical addressing 32-bit, routing, fragmentation |
| **IPv6** | Address space 128-bit (esadecimale) |
| **ICMP** | Error reporting & diagnostics (ping echo request/reply, traceroute) |
| **DHCP** | Assegnazione dinamica IP (lavora insieme a IP) |

### IPv4 — funzionalità
- **Logical addressing**: IP univoco per interfaccia; gerarchia tramite classi/subnet/CIDR.
- **Packet structure**: header + payload.
- **Fragmentation & reassembly**: pacchetti grandi spezzati in fragment in base alla **MTU** del path; riassemblati a destinazione.
- **Address types**:
  - **Unicast** = 1-to-1
  - **Broadcast** = 1-to-all (within subnet)
  - **Multicast** = 1-to-many (gruppo selezionato)
- **Subnetting**: divisione di una rete grande in sotto-reti (es. `/24`). Esempio organizzativo: **DMZ** (esposta a Internet, host web/servizi pubblici) vs **Internal network** (workstation, non raggiungibile dall'esterno).

### IPv4 reserved addresses (citati)
- `0.0.0.0/0` → "this network"
- `127.0.0.1` → loopback / localhost
- `192.168.0.0/16` → private networks
- Riferimento completo: **RFC 5735**

### Struttura dell'IPv4 header (campi principali)
| Campo | Bit | Note |
|---|---|---|
| **Version** | 4 | `4` per IPv4, `6` per IPv6 |
| **IHL** (Header Length) | 4 | In 32-bit words. Min 5 (20 byte), max 15 (60 byte) |
| **Type of Service (ToS)** | 8 | Priorità / QoS |
| **Total Length** | 16 | Header + payload (max 65 535 byte) |
| **Identification** | 16 | Per riassemblare fragment |
| **Flags** | 3 | bit0 reserved=0; bit1 **DF** (Don't Fragment); bit2 **MF** (More Fragments) |
| **TTL** | 8 | Numero massimo hop; decrementato di 1 ad ogni router |
| **Protocol** | 8 | **1=ICMP, 6=TCP, 17=UDP** |
| **Source Address** | 32 | IP sorgente |
| **Destination Address** | 32 | IP destinazione |

### Encapsulation (visto in Wireshark)
Sequenza per una richiesta HTTP a `google.com`:
1. **Frame (L1/L2)** — Ethernet, 66 byte, src/dst MAC.
2. **L3 IPv4** — Version=4, IHL=20 byte, DF set, Protocol=TCP, src=`192.168.2.134`, dst=IP del web server.
3. **L4 TCP** — src/dst port, flags, options.
4. **L7 HTTP** — payload applicativo.

## Comandi & strumenti

| Comando/Tool | Scopo | Note |
|---|---|---|
| **Wireshark** | Cattura e analisi pacchetti | Mostra OSI completo per ogni packet |
| `ping <ip>` | Test raggiungibilità via ICMP echo | Layer 3 |
| `traceroute <ip>` | Mappa hop intermedi | Sfrutta TTL |
| `ip a` (Linux) | Mostra interfacce/IP | |

## Esempi pratici

```bash
# Cattura traffico su Ethernet0 con Wireshark
# 1. Avviare Wireshark, selezionare interfaccia eth0
# 2. Aprire firefox -> google.com per generare traffico
# 3. Filtrare per tcp; ispezionare un pacchetto

# Equivalente CLI con tcpdump
sudo tcpdump -i eth0 -nn -v 'tcp and host google.com'
```

Lettura di un IPv4 header da Wireshark (esempio del video):
- Version: 4
- Header length: 20 bytes
- Flags: DF=1, MF=0 (no fragmentation)
- Protocol: TCP (6)
- Source: `192.168.2.134`
- Destination: IP del web server Google

## Punti d'attenzione per l'esame eCPPT

- Memorizza i **valori del campo Protocol IPv4**: **1=ICMP, 6=TCP, 17=UDP**.
- IPv4 = **32 bit** (4 octet); IPv6 = **128 bit** (esadecimale).
- **TTL** decrementa di 1 ad ogni hop → usato anche per **OS fingerprinting** (TTL=64 Linux, 128 Windows, 255 alcuni networking device).
- **DF / MF flags** sono rilevanti per **IDS evasion via fragmentation** (`-f`, `--mtu` in Nmap, vedi [[014_Firewall Detection & IDS Evasion]]).
- **MTU** standard Ethernet = 1500 byte; pacchetti più grandi → fragmentation.
- ICMP non è "ping" — ping usa ICMP echo request (type 8) / echo reply (type 0). Esistono altri tipi (3 destination unreachable, 11 time exceeded usato da traceroute).
- **CIDR** = Classless Inter-Domain Routing (definizione esatta utile per domande di subnetting).
- L'**encapsulation** spiega perché un Nmap TCP scan ha bisogno di IP routing funzionante; se non c'è L3 reachability nessun L4 scan funziona.

## Collegamenti con altri video

- Precedente: [[03_Networking Fundamentals]]
- Prossimo: [[05_Transport Layer]] — TCP/UDP, porte
- ICMP/ARP in host discovery: [[07_Host Discovery Techniques]] · [[08_Ping Sweeps]] · [[09_Host Discovery with Nmap - Part 1]]
- Fragmentation per evasion: [[014_Firewall Detection & IDS Evasion]]
