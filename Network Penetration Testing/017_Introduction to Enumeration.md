# 017 — Introduction to Enumeration (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 17/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [017_Introduction to Enumeration.txt](017_Introduction to Enumeration.txt) · [017_Introduction to Enumeration.srt](017_Introduction to Enumeration.srt)

## Concetti chiave

- **Enumeration** = fase successiva a host discovery + port scanning. Obiettivo: raccogliere informazioni **aggiuntive e specifiche** sui servizi e gli host identificati.
- È **active information gathering**: si interagisce direttamente con il target (genera traffico/log).
- Si lavora **protocol-specific**: per ogni servizio (SMB, SNMP, SMTP, FTP, ...) esistono tool e tecniche dedicati.
- Tipologie di info cercate: **account names, shares, misconfigurations, versioni software, domain info, user permissions**.
- L'output di enumeration alimenta direttamente la fase di **exploitation**.

## Spiegazione approfondita

### Posizionamento nella metodologia
La methodology eCPPT/PTES segue:
1. **Information Gathering** (passive + active)
2. **Host Discovery**
3. **Port Scanning**
4. **Service Detection / OS Detection**
5. **Enumeration** ← (questo video)
6. **Vulnerability Assessment**
7. **Exploitation**
8. **Post-Exploitation**
9. **Reporting**

L'enumeration parte **dopo** che si sa quali host esistono e quali porte/servizi sono aperti. Non si limita più a "porta 445 aperta = SMB" ma scava: "SMB v1 attivo? null session? quali utenti? quali share? signing disabled?".

### Perché è critica
- Spesso le vulnerabilità reali nascono da **misconfigurazioni** dei servizi (default creds, anonymous access, weak community strings), non da CVE.
- Permette di costruire un **inventario preciso**: utenti, gruppi, share, banner, versioni → input per scelta dell'exploit.
- Più info raccolte = exploit mirato = meno noise = più successo.

### Cosa enumerare per protocollo (preview dei prossimi video)
| Protocollo | Porte | Cosa enumerare |
|---|---|---|
| **NetBIOS** | UDP 137, 138 / TCP 139 | Hostname, workgroup, domain |
| **SMB** | TCP 445 (139 backwards) | Share, users, groups, SMB version, security mode |
| **SNMP** | UDP 161 | Community string, sysDescr, users, services, OID tree |
| **SMTP** | TCP 25 | User enum (VRFY/EXPN), open relay |
| **FTP** | TCP 21 | Anonymous login, banner, versione vulnerabile |
| **Finger** | TCP 79 | User enumeration su Linux |
| **MSSQL** | TCP 1433 | Versione, login, ruoli (sysadmin), impersonation |
| **HTTP/HTTPS** | TCP 80/443 | Tech stack, dir, vhosts (vedi modulo Web App) |
| **MySQL** | TCP 3306 | Versione, default creds |
| **RDP** | TCP 3389 | NLA, certificate, user enum (limited) |

### Active vs Passive
- **Passive**: WHOIS, DNS pubblico, OSINT, Shodan — nessun pacchetto al target.
- **Active**: nmap, enum4linux, smbclient, snmpwalk — pacchetti diretti → log sul target.

Enumeration è **sempre active**. Implicazioni OPSEC:
- Genera log sul target.
- Può triggerare IDS/IPS.
- Combinare con timing lento + `-Pn` se l'engagement è stealth.

### Obiettivo finale
"Trovare anomalie o misconfig sfruttabili" → il deliverable di questa fase è una **lista di candidate vulnerability** (es. SMB v1 con null session → user enum → brute force; SNMP `public` community → estrai utenti → spray; FTP anonymous → cerca file con creds).

## Comandi & strumenti

Questo video è teorico — i comandi specifici arrivano nei video 018–020. Anteprima:

| Tool | Protocollo | Note |
|---|---|---|
| `enum4linux` | SMB/NetBIOS | One-stop SMB enum su Linux |
| `smbclient` / `smbmap` | SMB | Liste share, navigazione |
| `rpcclient` | MSRPC | Query domain/user/group |
| `nbtscan` / `nmblookup` | NetBIOS | Name service |
| `snmpwalk` / `snmp-check` / `onesixtyone` | SNMP | Walk MIB, brute community |
| `smtp-user-enum` | SMTP | User enum via VRFY/EXPN |
| `finger` / `finger-user-enum.pl` | Finger | User enum Linux |
| `nmap --script <proto>-*` | Tutti | NSE protocol-specific |

## Esempi pratici

Esempi indicativi (dettagli nei video successivi):

```bash
# SMB
enum4linux -a <target>
smbmap -H <target>
smbclient -L //<target>/ -N

# SNMP
snmpwalk -v1 -c public <target>
onesixtyone -c communities.txt <target>

# SMTP
smtp-user-enum -M VRFY -U users.txt -t <target>

# NSE per protocollo specifico
nmap -p 445 --script "smb-enum-*" <target>
nmap -sU -p 161 --script "snmp-*" <target>
```

Nota extra: tenere sempre traccia dei risultati di enumeration in un file di note (es. CherryTree, Obsidian, KeepNote) organizzato per host/porta. Sull'esame eCPPT 2024 il tempo è limitato → la documentazione strutturata fa la differenza.

## Punti d'attenzione per l'esame eCPPT

- **Enumeration = active**, sempre. Differenza vs passive information gathering è una domanda ricorrente.
- Si esegue **dopo** host discovery e port scanning, **prima** di exploitation.
- Approccio **protocol-specific**: non un singolo tool, ma uno per ogni servizio.
- Obiettivo = trovare **users, shares, misconfig, versioni vulnerabili**.
- Spesso porta a credenziali (anonymous SMB, default SNMP) → input per fasi successive.
- Tool da conoscere ASSOLUTAMENTE: `enum4linux`, `smbclient`, `smbmap`, `rpcclient`, `snmpwalk`, `smtp-user-enum`, `nmap NSE`.
- Concetto chiave: **null session SMB** = anonymous → user enumeration → brute force.
- SNMP **community string** = "password" del protocollo: default `public`/`private`/`secret`.

## Collegamenti con altri video

- Precedente: [[016_Nmap Output Formats]] — l'enumeration parte dai dati salvati.
- Prossimo: [[018_SMB___NetBIOS_Enumeration.mp4]] — primo protocollo enumerato in pratica.
- Approfondimento Windows: [[018_SMB___NetBIOS_Enumeration.mp4]], [[019_SNMP_Enumeration.mp4]]
- Approfondimento Linux: [[020_Linux_Service_Enumeration.mp4]]
- Output → exploitation: [[021_SMB_Relay_Attack.mp4]], [[022_MSSQL_DB_User_Impersonation_to_RCE.mp4]]
