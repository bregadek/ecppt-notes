# 06 — Network Mapping (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 6/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_Network Mapping.txt](06_Network Mapping.txt) · [06_Network Mapping.srt](06_Network Mapping.srt)

## Concetti chiave

- **Network mapping** = processo di scoperta/identificazione di device, host e infrastruttura entro la rete target; **contiene** host discovery, port scanning, service detection, OS fingerprinting.
- Tool centrale: **Nmap** (Network Mapper) — open source, standard de facto per scanning.
- Obiettivi: live host discovery, open ports/services, network topology, OS fingerprinting, service version detection, identificazione di **firewall/IDS/IPS**.
- Esempio di scope: blocco IP `200.200.0.0/16` → **65 536** IP possibili, va capito quali sono attivi.
- Tecniche di host discovery che Nmap supporta: **ICMP echo request, ARP request, TCP/UDP probe**.

## Spiegazione approfondita

### Cos'è Network Mapping (in pentest)
Dopo la fase passiva, il pentester entra in attiva: deve mappare il target. Tipicamente parte da un range IP (in scope) senza sapere quali sistemi siano accesi, quale OS girino, se è una rete Active Directory, una DMZ, ecc.

Output atteso a fine fase:
- Numero di sistemi attivi e relativi IP.
- Porte aperte per ciascun host.
- Servizi e versioni dietro ogni porta.
- OS di ogni host.
- Eventuale topologia (router, switch, firewall).
- Difese rilevate (firewall, IPS).

### Scenario tipico
Cliente fornisce **CIDR** in scope (es. `200.200.0.0/16` = 65 536 IP da `200.200.0.0` a `200.200.255.255`). Spesso si arriva via **VPN**. In **black-box** non hai info: devi mappare prima di tutto.

### Obiettivi del network mapping
1. **Live host discovery** — quali IP sono attivi.
2. **Open ports & services** — attack surface.
3. **Network topology mapping** — router/switch/firewall, layout.
4. **OS fingerprinting** — adatta gli attacchi (es. AD attacks vs Linux misconfig).
5. **Service version detection** — input per la vuln analysis.
6. **Filtering & security measures** — firewall, IDS/IPS → si decide se rallentare gli scan, fragmentare, ecc.

### Perché Nmap
- Open source, multipiattaforma.
- Supporta **discovery, port scan, service detection, OS detection** in un unico tool.
- Estensibile via **NSE** (Nmap Scripting Engine).
- Riconosce un host Windows da SMB/NetBIOS aperti, poi raffina con OS fingerprinting più profondo.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| **Nmap** | Network mapping all-in-one | Cuore del modulo |

Tecniche di host discovery supportate da Nmap (anticipate):
- **ICMP echo** (`-PE`)
- **ARP request** (`-PR`, default in LAN)
- **TCP probe** (`-PS`, `-PA`)
- **UDP probe** (`-PU`)

## Esempi pratici

Video teorico, nessun comando eseguito. Esempi pratici partono da [[09_Host Discovery with Nmap - Part 1]].

## Punti d'attenzione per l'esame eCPPT

- **Network mapping** è il termine "contenitore" che include host discovery + port scan + OS/service detection. Domanda tipo: "Quale tool è lo standard per network mapping?" → **Nmap**.
- **CIDR**: `/16` = 65 536 host, `/24` = 256, `/8` = ~16M. Esercitati a convertire.
- In una **LAN** la tecnica di host discovery più affidabile è **ARP** (`-PR`): bypassa firewall che bloccano ICMP.
- Identificare **firewall/IDS** è parte del network mapping: se rilevati, cambia strategia (slower timing, fragmentation).
- Black-box vs white-box: il network mapping è molto più ampio in black-box.

## Collegamenti con altri video

- Precedente: [[05_Transport Layer]]
- Prossimo: [[07_Host Discovery Techniques]]
- Tutti i video successivi del modulo Nmap (07-016) sono sotto-fasi del network mapping.
- Identificazione firewall/IDS: [[014_Firewall Detection & IDS Evasion]]
