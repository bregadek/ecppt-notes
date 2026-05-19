# 09 — Host Discovery with Nmap - Part 1 (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 9/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_Host Discovery with Nmap - Part 1.txt](09_Host Discovery with Nmap - Part 1.txt) · [09_Host Discovery with Nmap - Part 1.srt](09_Host Discovery with Nmap - Part 1.srt)

## Concetti chiave

- **Nmap syntax**: `nmap <scan options> <target(s)> [port options]`. Scan options preferibilmente PRIMA del target.
- **Privilegi**: alcuni scan richiedono `sudo`/root (raw packets). Senza root, Nmap fa fallback (es. SYN scan → connect scan).
- **`-sn` (Ping Scan)**: disabilita il port scan, fa solo host discovery. NON è "solo ICMP" — invia di default un mix di probe:
  - **ICMP echo request**
  - **TCP SYN su porta 443**
  - **TCP ACK su porta 80**
  - **ICMP timestamp request**
- **Eccezione**: su rete **Ethernet locale**, Nmap usa **ARP** ignorando gli altri probe (più affidabile in LAN). Per forzare i probe IP-level: `--send-ip`.
- **Specifica target** multipli: IP separati da spazio, range tipo `10.0.0.2-240`, CIDR `10.0.0.0/24`, oppure da file con **`-iL <file>`**.

## Spiegazione approfondita

### Introduzione a Nmap
Nmap (Network Mapper) — preinstallato in Kali, Parrot, BlackArch. Su Debian/Ubuntu: `sudo apt install nmap`. Esiste anche su Windows (CLI + Zenmap GUI), ma Alexis raccomanda Linux per evitare problemi driver/Npcap.

### Syntax
```
nmap [SCAN_OPTIONS] [TARGET(S)] [PORT_OPTIONS] [SCRIPT_OPTIONS]
# es.
nmap -sn 192.168.1.0/24
nmap -sn 10.0.0.1 10.0.0.5 10.0.0.20
nmap -sn 10.0.0.2-50
nmap -sn -iL targets.txt
```

### Importanza dei privilegi
Molti scan inviano raw packets → serve root. Nmap segnala se manca il privilegio richiesto. Inoltre, lo scan effettivo cambia con i privilegi (es. `-sS` richiede root; senza root viene fatto `-sT`).

### Documentazione
- `nmap -h` → help menu sintetico, categorizzato (TARGET SPECIFICATION, HOST DISCOVERY, SCAN TECHNIQUES, ecc.).
- `man nmap` → pagina man completa con descrizione dettagliata di ogni opzione.
- Dentro `man` cercare con `/` (es. `/-sn`) e navigare con `n`.

### Il Ping Scan (`-sn`) in dettaglio
Sembrava "solo ICMP" ma in realtà combina 4 probe per massimizzare l'accuratezza:
1. ICMP echo request
2. TCP SYN → porta 443
3. TCP ACK → porta 80
4. ICMP timestamp request

Se l'host risponde a uno qualunque → vivo.

### ARP override su rete locale
Wireshark mostra che lanciando `nmap -sn 10.10.22.0/24` sulla LAN, Nmap invia **solo ARP requests** (più affidabile a L2, ignora regole firewall L3). Per forzare i probe IP/ICMP/TCP anche in LAN:
```bash
sudo nmap -sn --send-ip <target>
```
Con `--send-ip` Wireshark vede ARP + ICMP echo + TCP SYN/ACK come da documentazione.

### Verifica con Wireshark
```bash
sudo wireshark -i eth1   # poi filtro "icmp" o "tcp" o "arp"
```
Si osserva:
- ICMP type 8 in uscita; type 0 di reply dagli host vivi.
- TCP SYN verso porta 443; ACK verso 80; risposte ACK/RST identificano host vivi.

### Specificazione target avanzata
| Sintassi | Significato |
|---|---|
| `10.0.0.5` | Singolo IP |
| `10.0.0.5 10.0.0.7` | Due IP |
| `10.0.0.2-240` | Range ultimo ottetto |
| `10.0.0.0/24` | CIDR (256 IP) |
| `-iL targets.txt` | Lista da file (un IP/range per riga) |
| `--exclude <ip>` | Escludi singoli IP |
| `--excludefile <file>` | Escludi lista |

### Combinazione di probe
`-sn` può essere combinato con altri probe (es. `-PS<port>`, `-PA<port>`) per cambiare/aggiungere il tipo di probe usato durante la discovery. Le porte di default (443 per SYN, 80 per ACK) vengono **sovrascritte** quando si specificano porte custom in `-PS`/`-PA`.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -h` | Help menu categorizzato | |
| `man nmap` | Documentazione completa | `/-sn` per cercare |
| `nmap -sn <target>` | Ping scan (host discovery only) | Mix ICMP+SYN+ACK+timestamp; ARP in LAN |
| `sudo nmap -sn --send-ip <target>` | Forza probe IP-level anche in LAN | Bypassa fallback ad ARP |
| `nmap -sn 10.0.0.0/24` | Sweep CIDR | |
| `nmap -sn 10.0.0.2-240` | Sweep range | |
| `nmap -sn -iL targets.txt` | Target da file | Un IP/range per riga |
| `nmap -sn -PS<port> <target>` | TCP SYN ping su porta custom | Anticipato per Part 2 |
| `nmap -Pn <target>` | Skip host discovery | Visto in video 08 |

## Esempi pratici

```bash
# 1. Ping scan su subnet
sudo nmap -sn 10.10.22.0/24
# Output: "11 hosts up", IP attivi listati

# 2. In LAN — vediamo che usa ARP via Wireshark
sudo wireshark -i eth1
# Filtro: arp        → ARP requests
# Filtro: icmp       → vuoto (a meno di --send-ip)

# 3. Forziamo IP-level probes
sudo nmap -sn --send-ip 10.10.22.0/24
# Wireshark: ora vediamo ICMP echo + TCP SYN(443) + TCP ACK(80)

# 4. Target multipli e range
nmap -sn <target1> <target2>
nmap -sn 10.4.23.227-240

# 5. Da file
cat > targets.txt <<EOF
10.10.22.5
10.10.22.10-20
10.10.22.50
EOF
nmap -sn -iL targets.txt
```

## Punti d'attenzione per l'esame eCPPT

- **`-sn`** = Ping Scan = host discovery senza port scan. NON solo ICMP, ma 4 probe combinati.
- **Default `-sn`**: ICMP echo + TCP SYN/443 + TCP ACK/80 + ICMP timestamp.
- **In LAN, Nmap usa ARP** automaticamente (più affidabile). `--send-ip` forza i probe L3.
- **`-iL <file>`** = target da file (un'item per riga).
- **`-Pn`** = skip host discovery (forza il port scan anche su host che sembrano morti).
- Privilegi root necessari per molti scan raw → senza root, fallback meno accurato.
- Sintassi range: `1-254` per l'ultimo ottetto; CIDR `/24` per subnet.
- Differenza `-sn` vs `-Pn`: `-sn` fa SOLO discovery; `-Pn` SALTA la discovery.

## Collegamenti con altri video

- Precedente: [[08_Ping Sweeps]] — stesso lab, con `ping`/`fping`.
- Prossimo: [[010_Host Discovery with Nmap - Part 2]] — TCP SYN/ACK ping, UDP ping, esempi avanzati.
- Output da salvare: [[016_Nmap Output Formats]]
- Timing/ottimizzazione: [[015_Optimizing Nmap Scans]]
- Evasion: [[014_Firewall Detection & IDS Evasion]]
