# 013 — Nmap Scripting Engine (NSE) (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 13/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_Nmap Scripting Engine (NSE).txt](013_Nmap Scripting Engine (NSE).txt) · [013_Nmap Scripting Engine (NSE).srt](013_Nmap Scripting Engine (NSE).srt)

## Concetti chiave

- **NSE** = Nmap Scripting Engine. Permette di automatizzare port scan, vuln detect, enumeration, brute force, exploitation tramite script in **Lua** (`.nse`).
- Script preinstallati in: **`/usr/share/nmap/scripts/`** (Linux).
- **`-sC`** = esegue script della **categoria `default`** (safe, non intrusivi, informativi).
- **`-A`** = `-sV -O -sC --traceroute` combinati (aggressive scan).
- **`--script=<name>`** = esegue script specifico (estensione `.nse` opzionale).
- **`--script=<cat1,cat2>`** o **`--script=ftp-*`** = categorie / wildcard.
- **`--script-help=<name>`** = mostra descrizione + categorie del script.
- Categorie principali: `auth`, `broadcast`, `brute`, **`default`**, **`discovery`**, `dos`, **`exploit`**, `external`, `fuzzer`, `intrusive`, `malware`, **`safe`**, **`version`**, **`vuln`**.
- **Trick d'oro del lab**: lo script `mongodb-databases` ha rivelato distro (Ubuntu 14.04) e kernel version del target dove `-O` aveva fallito.

## Spiegazione approfondita

### Cos'è NSE
Framework di scripting in Lua integrato in Nmap. Una libreria di **>600 script** ufficiali coperti dalla community + script personali. Permette di trasformare Nmap da semplice port scanner a **tool di enumeration e vuln assessment**.

### Dove sono gli script
```bash
ls /usr/share/nmap/scripts/
ls /usr/share/nmap/scripts/ | grep http
ls /usr/share/nmap/scripts/ | grep mongodb
```

### Categorie NSE
| Categoria | Significato |
|---|---|
| `auth` | Bypass / test meccanismi di autenticazione |
| `broadcast` | Scoperta host via broadcast/multicast |
| `brute` | Brute force credenziali |
| **`default`** | Script informativi, sicuri, non intrusivi (invocati con `-sC`) |
| `discovery` | Enumera info sulla rete/host |
| `dos` | Denial of service (pericolosi!) |
| `exploit` | Sfruttano vulnerabilità (pericolosi!) |
| `external` | Si appoggiano a servizi terzi (es. whois online) |
| `fuzzer` | Test di robustezza |
| `intrusive` | Possono crashare o saturare il target |
| `malware` | Rilevano backdoor/malware |
| `safe` | Garantiti sicuri |
| `version` | Aiutano `-sV` |
| `vuln` | Verificano vulnerabilità note (CVE) |

### `-sC` Default scan
```bash
sudo nmap -sS -sV -sC -p- -T4 <target>
```
Esegue automaticamente gli script `default` applicabili ai servizi trovati. Niente brute, niente exploit, solo info-gathering "safe".

### Caso lab — la magia di NSE
Nel lab del video 12, `-O` non riusciva a identificare l'OS. Aggiungendo `-sC`:
- Lo script `mongodb-databases` viene eseguito automaticamente su porta 6421.
- Output rivela: **System Info** con `host: victim1`, `os: ubuntu 14.04`, `kernel: ...`, `process uptime`, ecc.
- Database enumerate: `local` (non vuoto), `admin` (vuoto).

Risultato: OS detection riuscita **via banner del servizio** dove TCP/IP fingerprinting aveva fallito.

### Eseguire script specifici
```bash
# Singolo script (estensione .nse opzionale)
sudo nmap --script=mongodb-info -p 6421 <target>
sudo nmap --script mongodb-info -p 6421 <target>     # senza =

# Multipli, separati da virgola
sudo nmap --script=memcached-info,ftp-anon -p- <target>

# Wildcard
sudo nmap --script="ftp-*" -p 21 <target>          # tutti gli FTP scripts
sudo nmap --script="http-*" -p 80,443 <target>

# Per categoria
sudo nmap --script=vuln <target>
sudo nmap --script=discovery,safe <target>

# Esclusione
sudo nmap --script="not intrusive" <target>
```

### Help di uno script
```bash
nmap --script-help=mongodb-databases
nmap --script-help=ftp-anon
# Output: categorie, descrizione, esempi
```

### Esempi di script utili visti nel video
- **`mongodb-databases`** (default/discovery/safe) → enumera DB MongoDB e rivela sys info.
- **`mongodb-info`** (default/discovery/safe) → build info, server status.
- **`memcached-info`** (safe, NOT default) → arch, PID, server time, conn count, auth status.
- **`ftp-anon`** → verifica login anonimo FTP.
- **`http-enum`** → enumeration dir/title/banner web.

### `-A` Aggressive
`-A` = `-sV -O -sC --traceroute`. Comodo per overview rapida. Da `man nmap`:
> "This option enables additional advanced and aggressive option. Presently, this enables OS detection (-O), version scanning (-sV), script scanning (-sC) and traceroute (--traceroute)."

Nota: `-A` non abilita timing template — devi specificarlo separatamente (`-T4`).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `ls /usr/share/nmap/scripts/` | Lista script disponibili | `| grep <keyword>` per filtrare |
| `nmap -sC <target>` | Default script scan | Equivalente a `--script=default` |
| `nmap --script=<name>` | Script specifico | `.nse` opzionale |
| `nmap --script=<s1>,<s2>` | Multipli | |
| `nmap --script="ftp-*"` | Wildcard | |
| `nmap --script=<categoria>` | Per categoria | `vuln`, `discovery`, ecc. |
| `nmap --script-help=<name>` | Help script | |
| `nmap --script-args=<k>=<v>` | Passa argomenti allo script | Es. `userdb=users.txt` |
| `nmap -A <target>` | `-sV -O -sC --traceroute` | Manca timing |
| `nmap --script-updatedb` | Aggiorna DB script | |

## Esempi pratici

```bash
# 1. Default script scan completo
sudo nmap -sS -sV -sC -p- -T4 <target>
# Output: include mongodb-databases che rivela OS = Ubuntu 14.04

# 2. Cerca script per servizio
ls /usr/share/nmap/scripts/ | grep mongodb
# mongodb-brute, mongodb-databases, mongodb-info

# 3. Verifica categoria di uno script
nmap --script-help=mongodb-databases
# Categories: default, discovery, safe

# 4. Esegui script specifico
sudo nmap --script=mongodb-info -p 6421 <target>

# 5. Combina più script
sudo nmap --script=memcached-info,ftp-anon -p- <target>

# 6. Tutti gli script FTP via wildcard
sudo nmap --script="ftp-*" -p 21 <target>

# 7. Vulnerability scan (categoria vuln)
sudo nmap --script=vuln <target>

# 8. Aggressive scan
sudo nmap -A -p- -T4 <target>
```

## Punti d'attenzione per l'esame eCPPT

- **`-sC`** = esegue solo script categoria `default` (= safe + informativi). Non intrusivo.
- **`-A`** = `-sV` + `-O` + `-sC` + `--traceroute`. NON include timing.
- **Categorie chiave**: `default`, `safe`, `discovery`, `vuln`, `brute`, `exploit`, `intrusive`. Distinguere "safe" da "intrusive".
- **`--script=<name>`**: estensione `.nse` opzionale, multipli separati da virgola, wildcard `*`.
- **`--script-help=<name>`** per scoprire categorie e descrizione PRIMA di lanciare.
- Path: **`/usr/share/nmap/scripts/`**.
- Script `.nse` scritti in **Lua**.
- Trick: servizi misconfig possono rivelare l'OS dove `-O` fallisce (banner via NSE = OS detection alternativa).
- NSE per **vuln scanning**: `--script=vuln` esegue tutti i check vulnerabilità (basato su CVE).
- Brute force: `--script=<protocol>-brute` (es. `ssh-brute`, `ftp-brute`) — categoria `brute`, NON in `default`.

## Collegamenti con altri video

- Precedente: [[012_Service Version & OS Detection]] — NSE compensa quando `-O` fallisce.
- Prossimo: [[014_Firewall Detection & IDS Evasion]]
- Enumeration con script protocol-specific: [[018_SMB___NetBIOS_Enumeration.mp4]], [[019_SNMP_Enumeration.mp4]]
- Brute force NSE: [[021_SMB_Relay_Attack.mp4]]
- Timing: [[015_Optimizing Nmap Scans]]
