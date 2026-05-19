# 019 — SNMP Enumeration (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 19/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [019_SNMP_Enumeration.mp4.txt](019_SNMP_Enumeration.mp4.txt) · [019_SNMP_Enumeration.mp4.srt](019_SNMP_Enumeration.mp4.srt)

## Concetti chiave

- **SNMP** (Simple Network Management Protocol) = application layer su **UDP**, gestione/monitoraggio device di rete (router, switch, server, stampanti).
- Componenti: **Manager** (chi interroga), **Agent** (chi risponde sul device), **MIB** (database gerarchico di **OID**).
- Porte: **UDP 161** (query), **UDP 162** (traps/notifiche).
- Versioni:
  - **SNMPv1** — community string in chiaro (default `public`, `private`).
  - **SNMPv2c** — bulk transfer + community string (ancora plain).
  - **SNMPv3** — auth + encryption (user-based).
- **Community string** = password del protocollo (v1/v2c). Default trovabili: `public`, `private`, `secret`.
- SNMP "leakoso" rivela: **OS, software installato, account utente, network interfaces, services, processes**.

## Spiegazione approfondita

### Workflow del lab

#### Step 1 — Identifica SNMP attivo (UDP scan)
```bash
sudo nmap -sU -p 161 demo.ine.local
# 161/udp open snmp
```

#### Step 2 — Verifica versione SNMP
```bash
sudo nmap -sU -sV -p 161 demo.ine.local
# Riconosce SNMPv1 (community public)
```

#### Step 3 — Brute force community string
```bash
sudo nmap -sU -p 161 --script snmp-brute demo.ine.local
# Wordlist usata: /usr/share/nmap/nselib/data/snmp-communities.lst
# Output: public, private, secret
```

Alternativa con `onesixtyone` (Nota extra: tool nativo per brute community):
```bash
onesixtyone -c /usr/share/wordlists/snmp/community.txt <target>
```

#### Step 4 — Walk MIB completo
```bash
snmpwalk -v1 -c public demo.ine.local
# Dump enorme di OID → poco leggibile
```

Per filtrare:
```bash
snmpwalk -v1 -c public <target> 1.3.6.1.2.1.25.4.2.1.2     # processi
snmpwalk -v1 -c public <target> 1.3.6.1.4.1.77.1.2.25      # utenti Windows
snmpwalk -v1 -c public <target> 1.3.6.1.2.1.25.6.3.1.2     # software installato
```

#### Step 5 — Enumerazione completa via NSE
```bash
sudo nmap -sU -p 161 --script "snmp-*" demo.ine.local -oN snmp_info
```
Script principali:
- `snmp-info`
- `snmp-sysdescr`
- `snmp-win32-software` → software installato
- `snmp-win32-services` → servizi Windows
- `snmp-win32-users` → utenti
- `snmp-netstat` → connessioni attive
- `snmp-interfaces` → interfacce di rete
- `snmp-processes`

Output rivela nel lab:
- Software: Firefox, Amazon SSM Agent, ecc.
- Network interfaces
- Community strings confermate
- Servizi Windows
- User accounts (administrator, admin)

#### Step 6 — `snmp-check` (alternativa veloce)
```bash
snmp-check -c public -v 1 <target>
```
Dump leggibile e ben formattato (system info, users, software, network).

#### Step 7 — Exploitation: brute SMB con utenti enumerati via SNMP
```bash
hydra -l administrator \
      -P /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt \
      demo.ine.local smb
# → password trovata → ps_exec → SYSTEM
```

### Object Identifier (OID)
Struttura gerarchica tipo:
- `1.3.6.1.2.1` = MIB-2 standard
- `1.3.6.1.4.1.77` = LAN Manager (Windows)
- `1.3.6.1.2.1.25` = Host Resources MIB

Conoscere alcuni OID notevoli aiuta a fare query mirate quando un walk completo è troppo rumoroso o filtrato.

## Comandi & strumenti

| Tool | Scopo | Esempio |
|---|---|---|
| `nmap -sU -p 161 <target>` | Identifica SNMP attivo | UDP! |
| `nmap -sU -sV -p 161` | Versione SNMP | |
| `nmap -sU -p 161 --script snmp-brute` | Brute community | wordlist incorporata |
| `onesixtyone -c <list> <target>` | Brute community veloce | |
| `snmpwalk -v1 -c <community> <target>` | Walk completo MIB | |
| `snmpwalk -v2c -c <community> <target> <OID>` | Walk OID specifico | |
| `snmp-check -c <community> -v 1 <target>` | Dump formattato | |
| `nmap --script "snmp-*" -sU -p 161` | Tutti gli NSE SNMP | Comodissimo |
| `snmpget -v1 -c <community> <target> <OID>` | Get singolo OID | |
| `snmpset -v1 -c <community> <target> <OID> <type> <value>` | **Write** (se `private` community) | Dangerous |

### NSE SNMP utili

| Script | Info |
|---|---|
| `snmp-info` | sysDescr, sysContact, sysName |
| `snmp-sysdescr` | OS info dettagliata |
| `snmp-win32-software` | Software installato (Windows) |
| `snmp-win32-services` | Servizi Windows |
| `snmp-win32-users` | User accounts Windows |
| `snmp-netstat` | Connessioni di rete |
| `snmp-interfaces` | Interfacce di rete |
| `snmp-processes` | Processi correnti |
| `snmp-brute` | Brute community strings |

## Esempi pratici

```bash
# Pipeline completa
sudo nmap -sU -p 161 -sV <target>
sudo nmap -sU -p 161 --script snmp-brute <target>
sudo nmap -sU -p 161 --script "snmp-*" -oN snmp_full.txt <target>

# Filtri snmpwalk
snmpwalk -v2c -c public <target> | head -50
snmpwalk -v2c -c public <target> 1.3.6.1.2.1.25.4.2.1.2   # processi
snmpwalk -v2c -c public <target> 1.3.6.1.4.1.77.1.2.25    # utenti

# snmp-check (output umano)
snmp-check -c public -v 1 <target>

# Da SNMP a RCE via SMB
# 1. enumera utenti da snmp
# 2. hydra brute SMB
# 3. impacket-psexec administrator@<target>
```

Nota extra: SNMPv3 richiede credenziali username + auth/priv keys → non si può brute con community. Identificare versione con `snmpwalk -v3 -u <user>` o `nmap --script snmp-info`.

## Punti d'attenzione per l'esame eCPPT

- **SNMP gira su UDP** (sempre `-sU` con nmap!). Porte: **161 query · 162 traps**.
- **Community string** = "password": default da provare `public`, `private`, `secret`.
- **SNMPv1/v2c** = community in chiaro; **v3** = auth user-based + encryption.
- Tool da memorizzare: **`snmpwalk`**, **`snmp-check`**, **`onesixtyone`**, NSE **`snmp-brute`** + **`snmp-*`**.
- Su Windows con SNMP si enumerano: **software installato, servizi, utenti, network interfaces, processes**.
- Username trovati via SNMP → input per **brute force SMB/RDP**.
- `snmpset` può **scrivere** OID se community `private` writable → da non sottovalutare (puoi modificare config router).
- MIB = albero di OID; conoscere `1.3.6.1.2.1.25` (Host Resources) e `1.3.6.1.4.1.77` (LAN Manager Windows).
- `nmap --script "snmp-*"` è il quickest path nel lab.

## Collegamenti con altri video

- Precedente: [[018_SMB___NetBIOS_Enumeration.mp4]]
- Prossimo: [[020_Linux_Service_Enumeration.mp4]]
- Utenti SNMP → brute SMB: [[018_SMB___NetBIOS_Enumeration.mp4]]
- Post-exploitation con creds trovate: [[025_Windows_Post-Exploitation_Lab.mp4]]
- NSE generale: [[013_Nmap Scripting Engine (NSE)]]
