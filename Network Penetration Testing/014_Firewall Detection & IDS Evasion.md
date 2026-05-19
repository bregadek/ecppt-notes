# 014 — Firewall Detection & IDS Evasion (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 14/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [014_Firewall Detection & IDS Evasion.txt](014_Firewall Detection & IDS Evasion.txt) · [014_Firewall Detection & IDS Evasion.srt](014_Firewall Detection & IDS Evasion.srt)

## Concetti chiave

- **Firewall detection** con Nmap = capire se tra noi e il target c'è un dispositivo di **filtering stateful**.
- **`-sA` (ACK scan)**: invia pacchetti con flag **ACK** → distingue **filtered** vs **unfiltered**, NON open/closed. Se la porta risponde con `unfiltered` non c'è firewall; se `filtered` → stateful firewall davanti.
- **IDS evasion** = modificare come Nmap costruisce e invia i pacchetti per non triggerare IDS/IPS o per **nascondere l'identità** dello scanner.
- Tecniche principali: **fragmentation** (`-f`), **custom MTU** (`--mtu`), **decoy** (`-D`), **source port spoof** (`-g`), **data length** (`--data-length`), **TTL** (`--ttl`), **DNS off** (`-n`).
- I pacchetti fragmentati avvengono al **livello IP (network layer)**. L'MTU deve essere multiplo di 8.
- Decoy IPs: ai log dell'analista i pacchetti sembrano provenire dalle decoy → confondono attribution.

## Spiegazione approfondita

### Firewall detection con ACK scan
Quando si lancia un SYN scan (`-sS`) classico su un host Windows con Windows Firewall attivo si vedono **porte filtered** invece di closed. Per confermare la presenza di filtering si usa:

```bash
sudo nmap -sA -p 445,3389 <target>
```

- `unfiltered` → la porta risponde all'ACK → **nessun firewall stateful** (l'ACK non appartiene a una sessione esistente quindi un firewall lo droppa, lo stack TCP risponde con RST).
- `filtered` → nessuna risposta o ICMP unreachable → stateful firewall presente.

Nel lab Alexis trova le porte `unfiltered` → conferma assenza di Windows Firewall sul target.

### Fragmentation `-f`
```bash
sudo nmap -sS -sV -f -p 80,445,3389 <target>
```
Spezza ogni probe TCP in **frammenti IP di 8 byte** (default `-f`). Doppio `-ff` = 16 byte. Un IDS basato su signature può fallire se non riassembla i frammenti.

In Wireshark si vede campo IP `fragment offset` = 0, poi 8, poi reassemble.

### `--mtu <value>`
Specifica una dimensione di MTU custom (deve essere **multiplo di 8**, minimo 8). `--mtu 32` significa "frammenta in pacchetti da 32 byte"; valori più grandi del payload nativo non producono frammentazione.

```bash
sudo nmap -sS -sV --mtu 8 -p 445 <target>
```

### Decoy `-D`
```bash
sudo nmap -sS -sV -D <decoy1>,<decoy2>,ME -p 445,3389 <target>
```
Nmap invia i probe **sia con il source IP reale sia con i decoy** in modo che un analista non possa distinguere quale sia il vero scanner. Convenzione lab: usare il **gateway** della propria subnet come decoy (es. `.1`, `.2`). `ME` indica la posizione del proprio IP nella lista.

Requisito: i decoy devono essere **raggiungibili / esistenti** sulla rete, altrimenti il target può triggerare SYN flood verso IP morti.

### Data length `--data-length`
Appende **N byte di dati random** al pacchetto. Cambia la firma e la dimensione, può evadere signature basate su packet size.

```bash
sudo nmap -sS -sV --data-length 200 <target>
```

### Source port spoof `-g` (o `--source-port`)
Maschera la sorgente come una porta "comune" e legittima (es. 53 DNS, 80, 88 Kerberos): firewall lassi possono fidarsi.

```bash
sudo nmap -sS -g 53 -p 445 <target>
```

### TTL custom `--ttl`
Modifica il TTL IP. Utile per ingannare sistemi che fingerprintano l'OS da TTL.

### Esempio combinato del lab
```bash
sudo nmap -Pn -sS -sV -p 445,3389 -f --data-length 200 -D 10.10.23.1,10.10.23.2 -g 53 <target>
```
- `-Pn` disabilita ping (host discovery)
- `-f` frammenta
- `--data-length 200` aggiunge padding
- `-D ...` decoy con IP del gateway/altri host della subnet
- `-g 53` source port = DNS

In Wireshark si osserva:
- Pacchetti SYN frammentati da 8 byte
- Source IP = decoy
- Source port = 53
- Le risposte (SYN/ACK, RST) tornano comunque all'IP reale (necessario per completare il three-way handshake)

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -sA -p <ports> <target>` | ACK scan, rileva filtering stateful | `unfiltered` vs `filtered` |
| `nmap -f <target>` | Frammenta probe in pezzi da 8 byte | `-ff` = 16 byte |
| `nmap --mtu <N> <target>` | MTU custom (multiplo di 8) | Forza frammentazione granulare |
| `nmap -D <ip1>,<ip2>,ME <target>` | Decoy IPs | Mischia probe reale con falsi |
| `nmap --data-length <N> <target>` | Appende N byte random | Modifica signature |
| `nmap -g <port>` / `--source-port <port>` | Spoof source port | Es. 53, 80, 88 |
| `nmap --ttl <N>` | Cambia IP TTL | Fingerprint evasion |
| `nmap --badsum <target>` | Pacchetti con checksum invalido | Solo IDS naive |
| `nmap -n` | Disabilita DNS resolution | Riduce noise / OPSEC |
| `nmap -Pn` | Skip host discovery | Vital su host firewallati |

## Esempi pratici

```bash
# 1. ACK scan per rilevare firewall stateful
sudo nmap -sA -p 445,3389 <target>

# 2. SYN scan con frammentazione semplice
sudo nmap -Pn -sS -sV -f -p 80,445,3389 <target>

# 3. MTU custom (8 byte)
sudo nmap -Pn -sS -sV --mtu 8 -p 445 <target>

# 4. Decoy scan: gateway + un altro host + ME
sudo nmap -Pn -sS -D 10.10.23.1,10.10.23.2,ME -p 445 <target>

# 5. Catena completa stealth (full evasion)
sudo nmap -Pn -n -sS -sV -p 445,3389 \
    -f --data-length 200 \
    -D 10.10.23.1,10.10.23.2 \
    -g 53 \
    <target>
```

Nota extra: per setup reali aggiungere anche timing template `-T1` o `-T2` (vedi 015) per ridurre rate dei probe.

## Punti d'attenzione per l'esame eCPPT

- **`-sA`**: rileva firewall, NON open/closed → output sono `unfiltered`/`filtered`. Domanda classica multi-choice.
- **`-f`** = frammenta a 8 byte; **`-ff`** = 16 byte; **`--mtu N`** = N byte (multiplo di 8).
- **`-D <ip1>,<ip2>,ME,<ip3>`**: posizione `ME` indica dove si trova il proprio IP nella lista probe inviata.
- **`-g`** o **`--source-port`**: spoof della source port (53/80/88 i più usati).
- **`--data-length N`**: payload casuale di N byte, NON cambia il flag TCP.
- **`-Pn`** è quasi sempre richiesto contro host firewallati che droppano ICMP.
- Frammentazione = livello IP (network layer), non TCP.
- Le risposte tornano sempre al **vero IP**: l'attacker deve essere on-path.
- OPSEC: combinare evasion + timing lento + `-n` per stealth massimo.

## Collegamenti con altri video

- Precedente: [[013_Nmap Scripting Engine (NSE)]]
- Prossimo: [[015_Optimizing Nmap Scans]] — timing template per ridurre rate.
- Output stealth saving: [[016_Nmap Output Formats]]
- Tecniche analoghe lato Linux man-in-the-middle: [[021_SMB_Relay_Attack.mp4]]
