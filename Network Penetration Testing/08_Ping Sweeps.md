# 08 — Ping Sweeps (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 8/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_Ping Sweeps.txt](08_Ping Sweeps.txt) · [08_Ping Sweeps.srt](08_Ping Sweeps.srt)

## Concetti chiave

- **Ping sweep** = scansione che invia **ICMP echo request (type 8)** a un range di IP e identifica come "vivi" quelli che rispondono con **ICMP echo reply (type 0)**.
- Strumenti nativi: `ping` (Win/Mac/Linux). Strumento batch: **`fping`** (più target in un colpo, sintassi più pulita).
- **Limite critico**: i sistemi **Windows** bloccano ICMP echo di default → ping sweep da solo **non trova host Windows** (errore tipico da junior pentester).
- Validazione con **Wireshark**: si vede ICMP type 8 in uscita, nessun type 0 in risposta → host bloccato o offline.
- Conferma "host realmente vivo" con Nmap `-Pn` (skip host discovery): se la porta scansionata risponde → l'host era vivo, era solo il ping a essere bloccato.

## Spiegazione approfondita

### Definizione
Un **ping sweep** = scansione che invia una serie di ICMP echo request a un intervallo di IP per scoprire quali host sono raggiungibili. Storicamente la prima tecnica per la network discovery.

### ICMP: type & code
Il pacchetto ping è ICMP nel suo header:
- **Echo Request** → **type = 8, code = 0**
- **Echo Reply** → **type = 0, code = 0**

Quando un host riceve un echo request e non lo blocca, risponde con un echo reply → il mittente conclude "host vivo".

### Comando `ping` nativo
- Linux/macOS: `-c N` per limitare a N pacchetti.
- Windows: `-n N` per lo stesso scopo.

Esempi dal lab:
```bash
ping <target_ip>          # ping continuo
ping -c 5 <target_ip>     # solo 5 pacchetti
```

### Sweep di un intero subnet con `ping`
Possibile in modo grezzo cambiando l'ultimo ottetto a `0` (broadcast su /24), ma rumoroso e poco affidabile. Nel lab Alexis lo fa con `ping <subnet_ip>` ma è poco pratico → si passa a `fping`.

### `fping`
Migliora `ping` permettendo di specificare **più target** o un intero range/CIDR.
```bash
fping -a -g 10.0.0.0/24             # -a = mostra solo host alive, -g = genera range
fping -a -g 10.0.0.0/24 2>/dev/null # silenzia gli "ICMP host unreachable"
fping <target_ip>                    # singolo host
```
Opzioni viste nel video:
- `-a` → mostra solo **alive** targets.
- `-A` → mostra targets per address.
- `-g` → genera la target list da un range (necessario quando non si usa `-f file`).
- `-S <source>` → spoof source IP (stealth).

### Quando il ping fallisce ma l'host è vivo
Alexis dimostra: `ping <ip>` non risponde, `fping <ip>` non risponde, ma:
```bash
nmap -Pn <ip>
# → Host is up. 993 filtered ports.
```
Il target è un sistema **Windows** che blocca ICMP via firewall ma ha porte filtrate / aperte. `-Pn` salta la fase di host discovery e procede direttamente al port scan, rivelando che l'host è vivo.

### Nmap come ping sweeper
```bash
nmap -sn <target>     # skip port scan, fa solo host discovery (ICMP + altri probe)
```
Anche `nmap -sn` può sbagliare contro Windows → lezione: **non affidarsi a una sola tecnica**.

### Validazione con Wireshark
Nel lab Alexis lancia Wireshark sull'interfaccia `eth1`, esegue ping, e osserva:
- Pacchetti ICMP Echo Request (type 8, code 0) in uscita.
- Nessun pacchetto Echo Reply in entrata → conferma blocco / host non risponde.
- Click su pacchetto → si vedono i layer OSI (Physical → Data link → Network/IP → Transport/ICMP).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `ping <ip>` | Singolo ICMP echo continuo | Builtin |
| `ping -c 5 <ip>` (Linux) | Limita a 5 pacchetti | Windows: `-n 5` |
| `fping <ip>` | Sweep singolo | Più informativo di ping |
| `fping -a -g <CIDR>` | Sweep range, solo host vivi | `-g` genera la lista |
| `fping -a -g <CIDR> 2>/dev/null` | Output pulito | Sopprime "unreachable" |
| `fping -S <ip>` | Spoof source IP | Stealth |
| `nmap -sn <target>` | Host discovery via Nmap | Combina più probe |
| `nmap -Pn <target>` | Skip host discovery, port scan diretto | Critico per Windows che bloccano ICMP |
| `sudo wireshark -i eth1` | Cattura ICMP per validare | Filtro: `icmp` |

## Esempi pratici

```bash
# 1. Ping classico — host Windows non risponde
ping -c 5 <target_ip>     # 0 reply

# 2. fping su tutto il subnet
ifconfig                  # scopri la propria interfaccia/IP
fping -a -g 10.0.0.0/24 2>/dev/null
# Output: solo gli IP che hanno risposto a ICMP

# 3. fping su singolo IP target (Windows) → ancora niente
fping <target_ip>

# 4. Conferma che l'host è invece vivo
nmap -Pn <target_ip>
# Host is up. 993 filtered ports.
```

```bash
# Verifica con Wireshark
sudo wireshark -i eth1
# In un altro terminale:
ping -c 3 <target_ip>
# In Wireshark: filter "icmp" → vedi type=8 in uscita, nessun type=0 in entrata
```

## Punti d'attenzione per l'esame eCPPT

- **ICMP type/code**: echo request = `type 8, code 0`; echo reply = `type 0, code 0`. Domanda classica.
- **Windows Firewall** blocca ICMP echo di default → un ping sweep "puro" perde gli host Windows.
- **`fping -a -g <CIDR>`** è la sintassi standard d'esame per sweep di un range.
- **`nmap -sn`** = ping scan (no port scan). **`nmap -Pn`** = skip host discovery (assume up).
- Differenza concettuale: `-sn` (scoperta soltanto) vs `-Pn` (salta la scoperta).
- Mancata risposta a ping NON implica host morto: può essere firewall, congestione, configurazione OS.
- **Lesson learned**: combina tecniche (ICMP + ARP + TCP SYN + UDP), non affidarti a una sola.

## Collegamenti con altri video

- Precedente: [[07_Host Discovery Techniques]]
- Prossimo: [[09_Host Discovery with Nmap - Part 1]] — stessa lab, ma con Nmap.
- Approfondimento opzioni Nmap discovery: [[010_Host Discovery with Nmap - Part 2]]
- Skip discovery / `-Pn`: ripreso in [[011_Port Scanning with Nmap]] e [[014_Firewall Detection & IDS Evasion]]
