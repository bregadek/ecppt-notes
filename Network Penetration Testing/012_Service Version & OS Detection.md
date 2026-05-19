# 012 — Service Version & OS Detection (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 12/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_Service Version & OS Detection.txt](012_Service Version & OS Detection.txt) · [012_Service Version & OS Detection.srt](012_Service Version & OS Detection.srt)

## Concetti chiave

- **`-sV`** = Service Version detection. Trasforma la colonna `SERVICE` da "guess" (basato su `/etc/services`) a **versione esatta** del software.
- **`-O`** = OS detection via TCP/IP fingerprinting.
- **`-A`** = Aggressive scan = `-sV -O -sC --traceroute` combinati.
- **`--osscan-guess`** (o `--fuzzy`) = forza Nmap a tentare guess aggressivi quando non c'è match certo → lista di "aggressive OS guesses" con percentuali.
- **`--version-intensity <0-9>`** = livello di intensità di `-sV`. 0 = veloce, 9 = massima accuratezza (default 7). Più alto = più probe = più lento.
- **`--version-light`** = intensity 2. **`--version-all`** = intensity 9.
- I servizi su porte **non-standard** (es. MongoDB su 6421 invece di 27017) richiedono `-sV` per identificarli.

## Spiegazione approfondita

### Workflow del lab
Nuovo lab: **nessun target IP fornito**. Il pentester deve:
1. `ifconfig` / `ip a` → determina propria interfaccia/subnet.
2. `nmap -sn 192.x.x.0/24` → trova host vivi.
3. Identificati: gateway + `target1` + Kali.
4. `nmap -sS <target>` → tutte le 1000 porte default = closed (!).
5. `nmap -sS -p- -T4 <target>` → trova porte aperte su numeri alti.
6. Aggiunge `-sV` → identifica servizi/versioni.
7. Aggiunge `-O` → tenta OS detection.

### Service Version Detection (`-sV`)
Dopo aver trovato porte aperte con SYN scan, Nmap si connette al servizio e legge i banner, esegue probe specifici, confronta con `nmap-service-probes` DB. Restituisce nome **e** versione esatta.

Esempio reale dal lab:
- Porta **6421/tcp** → MongoDB **2.6.10**
- Porta **41288/tcp** → Memcached
- Porta **55413/tcp** → vsftpd **3.0.3**
- Service Info: `OS: Unix` → indizio per OS detection

### OS Detection (`-O`)
Invia una serie di probe TCP/IP/ICMP carefully crafted e analizza:
- TCP options
- Window size / TTL iniziale
- Risposte a probe malformati
- ICMP timestamp

Confronta il "fingerprint" con `nmap-os-db`. Se match → OS specifico. Altrimenti mostra il fingerprint raw + "No exact OS match".

Su Windows: spesso identifica anche **build** (es. Windows Server 2012 R2). Su Linux: tipicamente solo **kernel version** (es. 2.6.32).

### Quando OS detection fallisce
Se solo poche porte aperte/chiuse, il fingerprint è insufficiente. Soluzioni:
```bash
sudo nmap -O --osscan-guess <target>
# Output: "Aggressive OS guesses: Linux 2.6.32 (96%), Linux 3.2-4.9 (90%), ..."
```
`--osscan-guess` forza Nmap a tirare a indovinare con percentuali di confidence.

### Version intensity
```bash
sudo nmap -sV --version-intensity 8 <target>
```
- `0` = solo probe più probabili.
- `7` = default (bilanciato).
- `9` = tutti i probe (più accurato, molto più lento).
- `--version-light` = `--version-intensity 2`.
- `--version-all` = `--version-intensity 9`.

### `-A` (Aggressive)
Shorthand per `-sV -O -sC --traceroute` in un colpo solo. Molto utile per un overview rapido ma molto rumoroso.

### Perché serve
- Vuln assessment: serve la **versione esatta** per cercare CVE.
- Threat modeling: OS detection guida la scelta di payload/exploit (Windows vs Linux vs BSD).
- Servizi su **porte non-standard** sono altrimenti invisibili (vedi MongoDB su 6421).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -sV <target>` | Service Version detection | Banner + probe DB |
| `nmap -O <target>` | OS detection (TCP/IP fingerprint) | Richiede root |
| `nmap -sV -O <target>` | Combinato | |
| `nmap -A <target>` | `-sV -O -sC --traceroute` | One-shot aggressive |
| `nmap -O --osscan-guess <target>` | Forza guess OS aggressivo | Mostra percentuali |
| `nmap -O --osscan-limit <target>` | OS scan solo se almeno 1 open + 1 closed | |
| `nmap -sV --version-intensity 9 <target>` | Max intensity service detection | |
| `nmap -sV --version-light <target>` | Intensity 2, veloce | |
| `nmap -sV --version-all <target>` | Intensity 9 | |
| `nmap -sS -p- -T4 <target>` | Full port scan prerequisito | Trovare le porte high-number |

## Esempi pratici

```bash
# Workflow completo del lab
# 1. Discovery dell'ambiente
ifconfig                                # determina subnet
sudo nmap -sn 192.31.2.0/24             # → trova target1

# 2. Default port scan — vuoto
sudo nmap -sS 192.31.2.143
# All 1000 scanned ports are closed!

# 3. Full TCP port scan con timing aggressivo
sudo nmap -sS -p- -T4 192.31.2.143
# Trova porte: 6421, 41288, 55413

# 4. Service version detection
sudo nmap -sS -sV -p 6421,41288,55413 192.31.2.143
# 6421/tcp  mongodb     MongoDB 2.6.10
# 41288/tcp memcached
# 55413/tcp ftp         vsftpd 3.0.3
# Service Info: OS: Unix

# 5. OS detection
sudo nmap -sS -sV -O -p 6421,41288,55413 192.31.2.143
# Nmap dice "No exact OS match" → forziamo guess

# 6. Aggressive OS guess
sudo nmap -O --osscan-guess 192.31.2.143
# Aggressive OS guesses: Linux 2.6.32 (96%), Linux 3.2-4.9 (90%)...

# 7. Massima accuratezza
sudo nmap -sV --version-intensity 8 -O --osscan-guess 192.31.2.143

# 8. Shortcut "aggressive"
sudo nmap -A 192.31.2.143
```

## Punti d'attenzione per l'esame eCPPT

- **`-sV`** è il flag base per service VERSION (non solo nome). Senza `-sV` la colonna SERVICE è solo una guess da `/etc/services`.
- **`-O`** = OS detection, richiede **root** e idealmente **almeno 1 porta open + 1 closed** per buona accuratezza.
- **`-A`** = `-sV -O -sC --traceroute` combinati. Molto comodo, ma rumoroso.
- **`--osscan-guess`** quando Nmap dice "No exact OS match".
- **`--version-intensity 0-9`** (default 7), `--version-light` = 2, `--version-all` = 9.
- Su Windows OS detection può scendere fino a build (Win Server 2012 R2). Su Linux di solito solo kernel.
- **Servizi su porte non-standard**: necessario `-p-` + `-sV` per trovare e identificare.
- **Service Info: OS: Unix** è un indizio gratuito dal banner di servizi (es. vsftpd).
- Versione esatta = chiave per CVE lookup (searchsploit, nvd).

## Collegamenti con altri video

- Precedente: [[011_Port Scanning with Nmap]]
- Prossimo: [[013_Nmap Scripting Engine (NSE)]] — estende la detection con script.
- Enumerazione approfondita: [[017_Introduction to Enumeration]]
- Timing T4 prerequisito: [[015_Optimizing Nmap Scans]]
- Output: [[016_Nmap Output Formats]]
