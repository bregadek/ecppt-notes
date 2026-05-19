# 07 — Host Discovery Techniques (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 7/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_Host Discovery Techniques.txt](07_Host Discovery Techniques.txt) · [07_Host Discovery Techniques.srt](07_Host Discovery Techniques.srt)

## Concetti chiave

- **Host discovery** = fase di network mapping in cui si identificano gli **host vivi** prima di passare a port scanning e vuln assessment.
- La scelta della tecnica dipende da: **caratteristiche della rete**, **requisiti di stealth**, **obiettivi del pentest**. Nessuna tecnica è "one-size-fits-all".
- Tecniche principali viste nel video:
  1. **ICMP echo / Ping sweep** — classico, ma bloccato dal **Windows Firewall** di default.
  2. **ARP scanning** — solo sulla **stessa LAN / broadcast domain**, ma estremamente affidabile.
  3. **TCP SYN ping** (alias *half-open* / *stealth*) — invia SYN, alla risposta SYN/ACK risponde con RST.
  4. **UDP ping** — utile per host che non rispondono a ICMP o TCP.
  5. **TCP ACK ping** e **SYN/ACK ping** — varianti che sfruttano il fatto che un RST implica host vivo.
- L'idea fondamentale di Nmap: **sfruttare il comportamento standard di TCP/ICMP/ARP** per inferire la presenza di un host.

## Spiegazione approfondita

### Cos'è la host discovery in pentest
Identificare quali IP di un range/subnet sono **online** prima di sprecare tempo a fare port scan su 65k indirizzi morti. È il primo step attivo del network mapping.

### Perché non basta una sola tecnica
- **ICMP**: spesso bloccato (Windows Firewall default DROP per ICMP echo request inbound). Affidarsi solo al ping sweep significa **perdere host Windows**.
- **TCP SYN ping**: se la porta probata è chiusa, nessuna risposta → host classificato come morto (falso negativo). Conviene probare **più porte** comuni.
- **ARP**: funziona solo se sei sulla stessa LAN del target (stesso broadcast domain).
- **UDP**: utile per servizi UDP-only (DNS, SNMP, NTP) o per bypassare regole che permettono solo UDP.

### ICMP Echo / Ping sweep
Invia ICMP echo request a ogni IP del range. Se l'host risponde con echo reply → vivo.
- **Pro**: rapido, ampiamente supportato.
- **Contro**: Windows Firewall blocca ICMP echo di default; gli IDS rilevano facilmente ping sweep massivi.

### ARP scanning
Sfrutta ARP request a livello L2 sul broadcast domain. Se un IP risponde con il proprio MAC → vivo. **Bypassa qualsiasi firewall host** perché ARP è necessario per la comunicazione L2.
- **Pro**: estremamente affidabile in LAN.
- **Contro**: limitato al segmento di rete corrente.

### TCP SYN ping (half-open / stealth)
Invia TCP SYN su una porta (default 80). Se risposta SYN/ACK → host vivo, e Nmap invia subito **RST** per non completare il 3-way handshake (più veloce + meno log lato target).
- **Pro**: stealthier dell'ICMP, può bypassare firewall che permettono traffico outbound.
- **Contro**: se la porta probata è chiusa/filtrata → falso negativo. Mitigare specificando più porte.

### UDP ping
Invia un pacchetto UDP a una porta specifica. Se la porta è chiusa l'host risponde con ICMP *Port Unreachable* → host vivo. Utile per device che rispondono solo a UDP.

### TCP ACK ping
Invia TCP ACK senza connessione precedente. Per lo standard TCP, l'host risponde con RST (perché non c'è sessione). Il **RST = host vivo**.

### TCP SYN/ACK ping
Analogo: invia un SYN/ACK fuori contesto, attende un RST.

### Considerazioni di scelta
| Tecnica | Quando usarla |
|---|---|
| ICMP (`-PE`) | Reti senza filtraggio, primo tentativo veloce |
| ARP (`-PR`) | Sei sulla LAN target — sempre preferita |
| TCP SYN (`-PS`) | Attraversare firewall che bloccano ICMP |
| TCP ACK (`-PA`) | Firewall stateless che lasciano passare ACK |
| UDP (`-PU`) | Host che rispondono solo a UDP / DNS-SNMP-NTP |

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `ping <ip>` | ICMP echo singolo | Builtin Win/Mac/Linux |
| **Nmap** `-PE` | ICMP echo ping | Sarà dettagliato nei video 09-010 |
| **Nmap** `-PR` | ARP ping (default in LAN) | |
| **Nmap** `-PS<ports>` | TCP SYN ping | Specifica porte multiple per ridurre falsi negativi |
| **Nmap** `-PA<ports>` | TCP ACK ping | |
| **Nmap** `-PU<ports>` | UDP ping | |
| **Nmap** `-sn` | Disable port scan (solo host discovery) | Anticipato per i prossimi video |

> Nota extra: i flag specifici (`-PE/-PR/-PS/-PA/-PU/-sn/-Pn`) saranno mostrati in azione nei video 09-010. Qui sono solo presentati a livello concettuale.

## Esempi pratici

Video teorico — nessun comando eseguito. Anteprima dell'utilizzo:

```bash
# Concetti che verranno applicati nei prossimi video
nmap -sn -PE 192.168.1.0/24      # ICMP echo sweep
nmap -sn -PR 192.168.1.0/24      # ARP sweep (LAN)
nmap -sn -PS22,80,443 10.0.0.0/24  # TCP SYN ping su più porte
nmap -sn -PU53,161 10.0.0.0/24     # UDP ping su DNS/SNMP
```

## Punti d'attenzione per l'esame eCPPT

- **Windows Firewall blocca ICMP echo di default** → ping sweep solo ICMP = host Windows mancanti = domanda classica d'esame.
- **ARP scan = più affidabile in LAN**: nessun firewall host può bloccarlo (serve per la comunicazione L2).
- **Half-open / SYN scan**: invia SYN → riceve SYN/ACK → risponde con **RST** (non completa handshake). Stealthier e più veloce.
- **TCP ACK ping**: l'host risponde con RST perché non c'è sessione → RST significa host vivo.
- **UDP**: la mancata risposta NON significa host morto (potrebbe essere porta aperta filtrata). Solo *ICMP unreachable* o reply applicativo = certezza.
- Per ridurre falsi negativi con SYN ping → specificare **più porte** comuni (`-PS22,80,443,3389`).
- Le tecniche di host discovery saranno mappate ai flag Nmap `-P*` nei video 09 e 010.

## Collegamenti con altri video

- Precedente: [[06_Network Mapping]]
- Prossimo: [[08_Ping Sweeps]] — ICMP sweep tradizionale e suoi limiti
- Implementazione in Nmap: [[09_Host Discovery with Nmap - Part 1]], [[010_Host Discovery with Nmap - Part 2]]
- Differenza con il port scan: [[011_Port Scanning with Nmap]]
- Evasione di firewall/IDS: [[014_Firewall Detection & IDS Evasion]]
