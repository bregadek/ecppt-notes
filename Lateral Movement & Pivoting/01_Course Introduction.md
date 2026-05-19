# 01 — Course Introduction (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 1/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Il corso copre due tecniche post-exploitation distinte ma spesso confuse: **Lateral Movement** e **Pivoting**.
- Struttura del corso: Intro → Windows Lateral Movement → Linux Lateral Movement → Pivoting (Windows + Linux).
- Differenziazione esplicita **per sistema operativo** perché tool, protocolli e sintassi cambiano notevolmente.
- L'obiettivo finale è saper detect & mitigate, ma il taglio resta offensive (pentest / red team).

## Spiegazione approfondita

### Topic Overview (sezioni del corso)
1. **Introduction to Lateral Movement & Pivoting** — definizioni, differenze tra le due tecniche.
2. **Windows Lateral Movement** — tecniche e tool per spostarsi tra host Windows (SMB, WMI, WinRM, RDP).
3. **Linux Lateral Movement** — tecniche su Linux (focus su SSH).
4. **Pivoting Intro** — cos'è il pivoting, perché si usa.
5. **Windows Pivoting** — port forwarding, SOCKS proxy via Metasploit.
6. **Linux Pivoting** — SSH tunneling, reGeorg.

### Prerequisiti dichiarati
- **Networking**: IP, subnetting, routing, switch/router/firewall, TCP/UDP/HTTP/DNS.
- **OS fundamentals**: Windows e Linux, CLI, file system, processi, permessi.
- **Cybersecurity basics**: CIA triad, awareness threats (phishing, malware, brute force).
- **Pentest experience**: livello eJPT o equivalente; tool Metasploit, Nmap, Wireshark.
- **Penetration testing lifecycle** e tecniche per fase.

### Learning Objectives (i tre macro-obiettivi)
1. **Understanding Lateral Movement & Pivoting**: saperli definire, differenziare, spiegare importanza e impatto in pentest/red team.
2. **Lateral Movement**: elencare e descrivere tecniche Windows/Linux, dimostrare competenza con PsExec, WMI, SSH, RDP, ecc.
3. **Pivoting**: descrivere come funziona e perché si usa, dimostrare competenza con SSH tunneling, VPN, SOCKS proxy, implementare multi-hop pivots, saper detect/mitigate.

## Comandi & strumenti

Video introduttivo, nessun comando. Tool che verranno introdotti:

| Categoria | Tool |
|---|---|
| Windows lateral movement | PsExec (SysInternals + Impacket), SMBExec, WMIExec, CrackMapExec, Evil-WinRM, xfreerdp, Metasploit |
| Linux lateral movement | SSH, scp |
| Pivoting | Metasploit (autoroute, portfwd, socks_proxy), proxychains, SSH tunneling (-L/-R/-D), reGeorg |

## Esempi pratici

N/A — video introduttivo.

## Punti d'attenzione per l'esame eCPPT

- Una domanda classica chiede di **distinguere lateral movement da pivoting** — memorizza che lateral movement = spostarsi tra host **nella stessa rete/segmento**, pivoting = usare un host come **stepping stone verso un'altra rete/segmento** altrimenti irraggiungibile.
- Il corso è inquadrato come **post-exploitation**: prerequisito è sempre un foothold iniziale.
- Le tecniche di lateral movement coperte (PtH, credential reuse, PsExec, WMIExec, ecc.) sono **identiche a quelle del red team reale** — l'esame può proporre uno scenario "ho un hash, qual è il next step?".
- Multi-hop pivot e detection sono richiesti negli obiettivi: aspettati scenari con più di un pivot.

## Collegamenti con altri video

- Prossimo: [[02_Introduction to Lateral Movement & Pivoting]] — definizioni e differenze.
- Conclusione corso: [[016_Course Conclusion]] — verifica learning objectives.
- Corso correlato (AD): Active Directory Penetration Testing — copre Pass-the-Ticket, Golden/Silver Ticket non inclusi qui.
