# 011 — Port Scanning with Nmap (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 11/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_Port Scanning with Nmap.txt](011_Port Scanning with Nmap.txt) · [011_Port Scanning with Nmap.srt](011_Port Scanning with Nmap.srt)

## Concetti chiave

- **Default Nmap scan** (`nmap <ip>` senza opzioni):
  - **Privileged (root)** → **SYN scan (`-sS`)**, stealth, half-open.
  - **Non-privileged** → **TCP connect scan (`-sT`)**, completa il 3-way handshake.
  - Esegue sempre **host discovery prima** del port scan (skippabile con `-Pn`).
  - Scansiona **1000 porte più comuni** se non specificate.
- **`-F`** = Fast scan, **100 porte** più comuni.
- **`-p <ports>`** = porte custom: `-p 80`, `-p 80,443,3389`, `-p 1-100`, `-p-` (tutte le 65535).
- **`-sU`** = UDP scan.
- **Stati delle porte**: `open`, `closed`, `filtered`, `open|filtered`, `unfiltered`. **filtered** = firewall.
- **SYN scan** è il preferito: più veloce, meno log (no full handshake), meno detection da IDS.
- **Trick**: porta `filtered` su Windows = Windows Firewall attivo; porta `closed` = nessun firewall.

## Spiegazione approfondita

### Default scan
```bash
nmap <target>           # senza opzioni
```
- Esegue prima host discovery → se l'host non risponde, "Host seems down". Soluzione: `-Pn`.
- Poi port scan su top 1000 porte.
- Tecnica usata: **SYN se root, Connect se non-root**.

### SYN scan (`-sS`) — Stealth / Half-open
- Nmap invia **SYN** a porta target.
- Se risposta **SYN/ACK** → porta **open**, Nmap invia **RST** (NON completa handshake).
- Se risposta **RST** → porta **closed**.
- Se **nessuna risposta** → porta **filtered** (firewall droppa).

Vantaggi:
- Stealth: non si crea connessione completa → niente log applicativi, meno alert IDS.
- Veloce: 1 step in meno del 3-way handshake.
- "SYN packets sono normali sulla rete" → poco sospetti.

Richiede privilegi root (raw socket).

### TCP Connect scan (`-sT`)
- Completa il 3-way handshake: SYN → SYN/ACK → ACK.
- Poi Nmap invia RST per chiudere.
- **Pro**: funziona senza root, leggermente più affidabile.
- **Contro**: rumoroso, genera log connessione, facilmente rilevabile da IDS/SIEM.

### UDP scan (`-sU`)
```bash
sudo nmap -sU -p 53,137,138,139 <target>
```
Più lento perché UDP non ha handshake. Stati:
- Risposta ICMP Port Unreachable → **closed**.
- Risposta UDP applicativa → **open**.
- Nessuna risposta → **open|filtered**.

### Stati delle porte (output Nmap)
| Stato | Significato |
|---|---|
| **open** | Servizio attivo che risponde |
| **closed** | Porta raggiungibile, nessun servizio |
| **filtered** | Firewall blocca → Nmap non sa |
| **open\|filtered** | Tipico di UDP/probe ambigui |
| **unfiltered** | Raggiungibile ma stato sconosciuto (es. ACK scan) |

**Trick d'esame**: `filtered` su Windows → Windows Firewall attivo. `closed` → nessun firewall stateful in mezzo.

### Output Nmap
Colonne: `PORT`, `STATE`, `SERVICE`.
Service è solo una **stima** basata su `/etc/services` — NON è service version detection (vedi video 012).

### Specifica porte (`-p`)
| Sintassi | Significato |
|---|---|
| `-p 80` | Singola porta |
| `-p 80,443,3389` | Lista |
| `-p 1-1000` | Range |
| `-p-` | Tutte le 65 535 TCP |
| `-p T:80,U:53` | Mix TCP/UDP |
| `-F` | Fast scan: top 100 porte |

### Validazione con Wireshark
- SYN scan: vedi SYN out → SYN/ACK in → RST out. Niente ACK (no handshake).
- Connect scan: SYN → SYN/ACK → ACK → ACK/RST.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap <ip>` | Default scan | SYN se root, Connect altrimenti |
| `nmap -Pn <ip>` | Skip host discovery + default port scan | Critico per Windows |
| `sudo nmap -sS <ip>` | SYN/Stealth/Half-open scan | Preferito |
| `nmap -sT <ip>` | TCP Connect scan | Default senza root |
| `sudo nmap -sU <ip>` | UDP scan | Lento |
| `nmap -F <ip>` | Fast scan (top 100 porte) | |
| `nmap -p 80,443 <ip>` | Porte custom | |
| `nmap -p- <ip>` | Tutte le 65535 TCP | Lungo |
| `nmap -p 1-100 <ip>` | Range porte | |
| `nmap -T4 -p- <ip>` | Tutte le porte, timing aggressivo | T0-T5 |

## Esempi pratici

```bash
# 1. Scan default — su Windows host fallisce per host discovery
nmap <win_target>           # "Host seems down"

# 2. Skip discovery
sudo nmap -Pn <win_target>  # default SYN scan, 1000 porte

# 3. Fast scan
sudo nmap -Pn -F <win_target>

# 4. Porte specifiche
sudo nmap -Pn -p 80,445,3389,8080 <target>
# 8080 → filtered (Windows Firewall)
# 80,445,3389 → open

# 5. Full TCP port scan (timing 4)
sudo nmap -Pn -sS -p- -T4 <target>

# 6. Explicit SYN scan + Wireshark verification
sudo wireshark -i eth1 &
sudo nmap -Pn -sS -p 445,3389 <target>
# Wireshark: SYN → SYN/ACK → RST (no ACK)

# 7. TCP Connect scan
sudo nmap -Pn -sT -F <target>
# Wireshark: SYN → SYN/ACK → ACK → RST

# 8. UDP scan
sudo nmap -Pn -sU -p 53,137,138,139,161 <target>
```

## Punti d'attenzione per l'esame eCPPT

- **Default scan**: `-sS` con root, `-sT` senza. Top 1000 porte. SEMPRE preceduto da host discovery (a meno di `-Pn`).
- **`-sS` (SYN/Stealth/Half-open)** è il flag MUST KNOW: SYN → SYN/ACK → RST. Non completa handshake.
- **`-sT` (Connect)**: completa handshake → loggable.
- **`-sU`**: lento, distingue closed (ICMP unreachable) da open|filtered (no response).
- **`-F`** = 100 porte. **`-p-`** = tutte le 65535.
- **Stati**: open / closed / filtered / open|filtered / unfiltered. **filtered = firewall**.
- **`-Pn`** è quasi obbligatorio su host Windows che bloccano discovery.
- Trick: `filtered` su una porta indica firewall stateful (es. Windows Firewall); `closed` indica nessun firewall in mezzo.
- Ricorda: **SYN packet ≠ rumoroso**, ma **TCP Connect = rumoroso** (3-way handshake completo → log).

## Collegamenti con altri video

- Precedente: [[010_Host Discovery with Nmap - Part 2]]
- Prossimo: [[012_Service Version & OS Detection]] — identificare ciò che gira sulle porte aperte.
- NSE: [[013_Nmap Scripting Engine (NSE)]]
- Evasion firewall: [[014_Firewall Detection & IDS Evasion]]
- Timing T0-T5: [[015_Optimizing Nmap Scans]]
- Output salvataggio: [[016_Nmap Output Formats]]
