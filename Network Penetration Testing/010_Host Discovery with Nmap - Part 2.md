# 010 — Host Discovery with Nmap - Part 2 (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 10/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_Host Discovery with Nmap - Part 2.txt](010_Host Discovery with Nmap - Part 2.txt) · [010_Host Discovery with Nmap - Part 2.srt](010_Host Discovery with Nmap - Part 2.srt)

> Nota: la trascrizione `.txt` fornita per il video 010 risulta essere un duplicato di `08_Ping Sweeps.txt`. Gli appunti seguenti coprono i temi attesi per la "Part 2" della host discovery con Nmap (TCP SYN/ACK ping, UDP ping, ICMP variants, opzioni avanzate), tutti già parzialmente anticipati in [[07_Host Discovery Techniques]] e [[09_Host Discovery with Nmap - Part 1]], che restano la base di studio per i flag mostrati.

## Concetti chiave

- **`-PS<ports>`** = **TCP SYN ping**. Invia SYN → si aspetta SYN/ACK o RST come "alive". Default port 80 se non specificata.
- **`-PA<ports>`** = **TCP ACK ping**. Invia ACK fuori sessione → si aspetta un RST = host vivo. Bypassa firewall stateless.
- **`-PU<ports>`** = **UDP ping**. Invia UDP a porte tipicamente chiuse → risposta ICMP *Port Unreachable* = host vivo. Default port 40125.
- **`-PE`** = ICMP echo ping (type 8). **`-PP`** = ICMP timestamp (type 13). **`-PM`** = ICMP address mask (type 17).
- **`-PR`** = ARP ping. Default in LAN, override altri probe.
- **`-PO<proto>`** = IP protocol ping (es. `-PO1` ICMP, `-PO2` IGMP).
- **`-Pn`** = NO host discovery, considera tutti gli host come "up" e passa al port scan.
- **`-n`** = no DNS resolution. **`-R`** = DNS resolution sempre. **`--dns-servers`** = DNS custom.
- **`--reason`** = mostra perché Nmap ha classificato un host/porta in un certo stato (es. `echo-reply`, `syn-ack`).
- **`--traceroute`** = path tracing combinato con la discovery.

## Spiegazione approfondita

### TCP SYN ping (`-PS`)
```bash
sudo nmap -sn -PS22,80,443,3389 10.0.0.0/24
```
Per ogni IP Nmap manda un TCP SYN sulle porte specificate. Se riceve **SYN/ACK** (porta aperta) o **RST** (porta chiusa) → host vivo. Specificare **più porte comuni** riduce i falsi negativi (un solo porta probata può essere filtrata).

### TCP ACK ping (`-PA`)
```bash
sudo nmap -sn -PA80,443 10.0.0.0/24
```
Invia un ACK senza alcuna sessione TCP in corso. Per RFC l'host deve rispondere con **RST**. Il RST = host vivo. Utile contro firewall **stateless** che bloccano SYN nuovi ma lasciano passare ACK (assumendoli traffico legittimo di una sessione esistente).

### UDP ping (`-PU`)
```bash
sudo nmap -sn -PU53,161,123 10.0.0.0/24
```
Invia UDP a una porta. Se porta chiusa → ICMP Port Unreachable → host vivo. Se porta aperta → solitamente nessuna risposta o risposta applicativa (DNS, SNMP, NTP). Utile su device che rispondono solo a UDP.

### Varianti ICMP
- **`-PE`** ICMP Echo (type 8) — il classico ping.
- **`-PP`** ICMP Timestamp (type 13) — alcuni host bloccano echo ma rispondono a timestamp.
- **`-PM`** ICMP Address Mask (type 17) — vecchia tecnica, raramente utile oggi.

### ARP ping (`-PR`)
Default su LAN. Per disabilitarlo: `--send-ip` (forza probe a livello IP).

### IP Protocol ping (`-PO`)
Invia pacchetti IP con protocol number specifico (1=ICMP, 2=IGMP, 4=IPv4 in IPv4, 41=IPv6, ecc.). Utile per fingerprinting/evasion.

### Combinazione di probe
Tutti i `-P*` possono essere combinati nello stesso comando:
```bash
sudo nmap -sn -PE -PP -PS22,80,443 -PA80 -PU161 10.0.0.0/24
```
Nmap considera l'host vivo se **qualsiasi** dei probe ottiene una risposta valida.

### Skip discovery — `-Pn`
```bash
sudo nmap -Pn -sS -p- 10.0.0.5
```
Non fa discovery, tratta tutti i target come up → forza il port scan. Essenziale per host che bloccano TUTTI i probe (firewall hardening).

### DNS handling
- `-n` salta resolution (più veloce, meno log DNS).
- `-R` forza resolution anche per host non risponditori.
- `--dns-servers 8.8.8.8,1.1.1.1` per DNS custom.

### `--reason`
Estremamente utile: aggiunge la colonna "REASON" mostrando il pacchetto che ha portato Nmap a una decisione (`syn-ack`, `reset`, `echo-reply`, `no-response`, `host-unreach`).

## Comandi & strumenti

| Comando | Scopo | Default |
|---|---|---|
| `-PE` | ICMP echo ping | type 8 |
| `-PP` | ICMP timestamp | type 13 |
| `-PM` | ICMP address mask | type 17 |
| `-PS<ports>` | TCP SYN ping | port 80 |
| `-PA<ports>` | TCP ACK ping | port 80 |
| `-PU<ports>` | UDP ping | port 40125 |
| `-PR` | ARP ping | default LAN |
| `-PO<proto>` | IP protocol ping | 1,2,4 |
| `-Pn` | Skip host discovery | — |
| `-n` / `-R` | No DNS / Force DNS | -n consigliato in pen test |
| `--dns-servers` | DNS custom | — |
| `--reason` | Mostra causa decisione | — |
| `--traceroute` | Path tracing | — |
| `--send-ip` | Forza probe L3 anche in LAN | — |

## Esempi pratici

```bash
# 1. SYN ping su porte comuni — utile contro firewall che bloccano ICMP
sudo nmap -sn -PS22,80,443,3389,8080 10.0.0.0/24 --reason

# 2. ACK ping — bypass firewall stateless
sudo nmap -sn -PA80,443 10.0.0.0/24

# 3. UDP ping su servizi UDP tipici
sudo nmap -sn -PU53,123,161 10.0.0.0/24

# 4. Combinato — massima copertura
sudo nmap -sn -PE -PP -PS21,22,80,443,3389 -PA80 -PU53,161 10.0.0.0/24 --reason

# 5. Skip discovery (host Windows che blocca tutto)
sudo nmap -Pn -sS -p- 10.0.0.5

# 6. Traceroute durante discovery
sudo nmap -sn -PE --traceroute 10.0.0.0/24
```

## Punti d'attenzione per l'esame eCPPT

- **`-PS<ports>`** vs **`-PA<ports>`**: SYN richiede risposta SYN/ACK/RST; ACK richiede RST. ACK passa firewall stateless.
- **`-PU`** richiede una porta dove il `Port Unreachable` ICMP sia leggibile.
- **`-Pn` è essenziale** quando un host blocca ogni probe (es. Windows con firewall hardened): forza il port scan.
- **`--reason`** è la chiave per debugging: mostra `syn-ack`, `reset`, `echo-reply`, `no-response`.
- ICMP non è solo echo: **`-PP` (timestamp)** è spesso accettato anche quando `-PE` è bloccato.
- ARP ping in LAN (`-PR`) è il più affidabile, non passabile via firewall host.
- Specificare **più porte** in `-PS/-PA` riduce falsi negativi.
- `-n` (no DNS) accelera notevolmente e riduce footprint nei DNS log del target.

## Collegamenti con altri video

- Precedente: [[09_Host Discovery with Nmap - Part 1]] — Ping Scan e ARP override.
- Prossimo: [[011_Port Scanning with Nmap]] — finita la discovery, si scansionano le porte.
- Teoria delle tecniche: [[07_Host Discovery Techniques]]
- Bypass firewall avanzato: [[014_Firewall Detection & IDS Evasion]]
- Output: [[016_Nmap Output Formats]]
