# 016 — Nmap Output Formats (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 16/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [016_Nmap Output Formats.txt](016_Nmap Output Formats.txt) · [016_Nmap Output Formats.srt](016_Nmap Output Formats.srt)

## Concetti chiave

- **Salvare sempre i risultati**: accountability, evita scan ripetuti, base per il report.
- Formati: **`-oN`** normal (txt human readable), **`-oX`** XML (import Metasploit), **`-oG`** grepable, **`-oS`** ScriptKiddie (raramente usato), **`-oA <base>`** tutti e tre insieme.
- **XML → Metasploit DB**: `db_import file.xml` popola `hosts`/`services` nel workspace corrente.
- **Workspaces** Metasploit: isolano dati per ciascun engagement (`workspace -a pentest1`).
- **`db_nmap`** = lancia Nmap dall'msfconsole e salva direttamente nel DB.
- **Verbosity** `-v`/`-vv` e **`--reason`** = info aggiuntive sul terminale (non sui file di output).

## Spiegazione approfondita

### Formati di output

| Flag | Formato | Quando usarlo |
|---|---|---|
| `-oN <file>` | Normal (text) | Reporting, leggibile a occhio |
| `-oX <file>` | XML | Import in Metasploit / parsing con script |
| `-oG <file>` | Grepable | Pipeline con `grep`, `awk`, `cut`, `sed` |
| `-oS <file>` | Script Kiddie | Solo "estetico", `c00l h4x0r` style |
| `-oA <base>` | All formats | Genera `<base>.nmap`, `<base>.xml`, `<base>.gnmap` |

Convenzione tipica:
- `-oN scan.txt`
- `-oX scan.xml`
- `-oG scan.grep`
- `-oA scan_basename`

### Esempio base
```bash
sudo nmap -Pn -sS -F -T4 <target> -oN nmap_normal.txt
sudo nmap -Pn -sS -F -T4 <target> -oX nmap_xml.xml
sudo nmap -Pn -sS -F -T4 <target> -oG nmap_grep.grep
sudo nmap -Pn -sS -F -T4 <target> -oA fullscan
```

Indipendentemente dal formato, l'output viene mostrato **anche a terminale**.

### Workflow import in Metasploit
```bash
# 1. Avvia PostgreSQL (richiesto)
sudo service postgresql start

# 2. Apri msfconsole
msfconsole

# 3. Crea/seleziona workspace
msf6 > workspace -a pentest1
msf6 > workspace pentest1

# 4. Verifica connessione DB
msf6 > db_status
[*] Connected to msf. Connection type: postgresql.

# 5. Importa scan
msf6 > db_import /root/nmap_xml.xml

# 6. Query
msf6 > hosts
msf6 > services
msf6 > services -p 445
```

`db_nmap` esegue nmap direttamente da msf e salva i risultati nel workspace corrente:
```
msf6 > db_nmap -Pn -sS -sV -O -p 445 <target>
```
Aggiorna i campi `os_name`, `info`, ecc. nei record `hosts/services`.

### Grepable format — utilità reale
Per pipeline custom. Esempio: estrarre `host\tports_open` dal `.grep`:
```bash
egrep -v "^#" nmap_grep.grep | \
  cut -d ' ' -f 2,4 | \
  sed 's/Ports://'
```
O usare `awk` per riformattare. Utile per ingest in script di follow-up (es. lanciare brute-force solo su host con porta 22 aperta).

### Report finale
- Nel report ufficiale del pen test → **sempre formato normal (`.txt`)**: leggibile da clienti/manager.
- Mai mettere output grepable o XML grezzo nel report.

### Verbosity / reason (extra)
- `-v` / `-vv`: più dettaglio a terminale (non nei file).
- `--reason`: spiega perché una porta è open/closed/filtered (es. `syn-ack`, `no-response`).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -oN <file> <target>` | Normal output | `.txt` |
| `nmap -oX <file> <target>` | XML output | per Metasploit / parsing |
| `nmap -oG <file> <target>` | Grepable output | pipeline shell |
| `nmap -oS <file> <target>` | ScriptKiddie output | raramente utile |
| `nmap -oA <basename> <target>` | Tutti i 3 formati | `.nmap/.xml/.gnmap` |
| `service postgresql start` | Avvia DB Metasploit | richiesto prima di msfconsole |
| `msf > workspace -a <name>` | Crea workspace | isolamento per engagement |
| `msf > db_import <file.xml>` | Importa scan XML | popola hosts/services |
| `msf > db_nmap <args>` | Lancia nmap salvando in DB | wrapper integrato |
| `msf > hosts` / `services` / `creds` / `loot` | Query DB | view post-import |
| `nmap -v` / `-vv` | Verbosity | terminale |
| `nmap --reason` | Mostra perché stato porta | |

## Esempi pratici

```bash
# 1. Salva nei 3 formati con un solo flag
sudo nmap -Pn -sS -sV -F -T4 <target> -oA fullscan

# 2. Import XML in workspace dedicato Metasploit
sudo service postgresql start
msfconsole -q
msf6 > workspace -a clientX
msf6 > db_import /root/fullscan.xml
msf6 > hosts
msf6 > services -p 445,3389

# 3. db_nmap direttamente da msf
msf6 > db_nmap -Pn -sS -sV -O -p 445 <target>

# 4. Grepable + parsing per host con porta 22 aperta
sudo nmap -Pn -p 22 <subnet>/24 -oG ssh.grep
egrep "22/open" ssh.grep | cut -d ' ' -f 2

# 5. Verbose con reason a video
sudo nmap -v --reason -p 445 <target>
```

## Punti d'attenzione per l'esame eCPPT

- **`-oN`** = normal/text (human readable).
- **`-oX`** = XML (per Metasploit `db_import`).
- **`-oG`** = grepable (pipeline shell).
- **`-oS`** = ScriptKiddie.
- **`-oA <base>`** = tutti e tre i principali (`.nmap`, `.xml`, `.gnmap`).
- **`db_import file.xml`** in msfconsole popola `hosts` e `services` del workspace corrente.
- **PostgreSQL** deve essere avviato prima di msfconsole per persistere dati.
- **Workspaces**: `workspace -a <name>`, `workspace <name>`, `workspace -d <name>`.
- **`db_nmap`** = nmap nativo dentro msf, salva su DB automaticamente.
- I dati sono **persistenti**: chiudere msfconsole non li cancella.
- Per il report finale → sempre formato **normal**.

## Collegamenti con altri video

- Precedente: [[015_Optimizing Nmap Scans]]
- Prossimo: [[017_Introduction to Enumeration]]
- Workflow Metasploit usato in: [[018_SMB___NetBIOS_Enumeration.mp4]], [[021_SMB_Relay_Attack.mp4]], [[025_Windows_Post-Exploitation_Lab.mp4]]
- Output di scan grandi: [[009_Host Discovery with Nmap - Part 1]]
