# 06 — C2 Deployment & Operation (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 6/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_C2 Deployment & Operation.txt](06_C2 Deployment & Operation.txt) · [06_C2 Deployment & Operation.srt](06_C2 Deployment & Operation.srt)

## Concetti chiave

- Fattori da considerare PRIMA di deployare un'infrastruttura C2: **payload delivery**, **client-side protection** (AV/EDR/XDR), **network-based protection** (egress filter, IDS/IPS, packet filter).
- La scelta del **C2 framework** e del **canale di comunicazione** dipende dal target e dalle protezioni rilevate.
- I C2 framework entrano in gioco di solito **dopo l'initial access** (post-exploitation), non come vettore di initial access (raro).
- Best practice canale C2: porte standard (**443 > 80 > 8080**), domini (non IP raw), encryption, jitter, sleep adeguato.
- **Domain fronting**: tecnica per nascondere la vera destinazione del traffico C2 dietro un dominio fidato (es. Cloudflare).

## Spiegazione approfondita

### Fattori di deployment infrastruttura
1. **Payload delivery** — come si consegna lo stager? Email phishing, web delivery, exploit. Il C2 framework deve supportare formati compatibili col vettore di delivery.
2. **Client-side protection** — AV, EDR, XDR sui target. Determina se servono **encoding/obfuscation** dello stager (PE encoding, shellcode injection, PowerShell obfuscation con Invoke-Obfuscation/ConfuserEx, PowerSploit).
3. **Network-based protection** — egress filtering (quali porte sono aperte in uscita?), IDS/IPS, deep packet inspection. Influenza scelta protocollo C2.

### Initial access vs Post-exploitation
- L'initial access è **raramente** ottenuto tramite C2 stager. Più tipico: exploit pubblico, supply chain, phishing, valid accounts.
- Lo stager Empire/Cobalt Strike viene **droppato dopo l'initial access** per ottenere il canale C2 stabile.

### Selezione del C2 in base al target OS
- Target Windows → preferire framework con supporto ricco per stager Windows: **PowerShell-Empire** (PowerShell native, EXE, DLL, VBA, VBS, HTA, macro, shellcode).
- Empire esegue moduli PowerShell **in memory** (no scrittura su disco) → ottima evasion.
- Sconsigliato: framework con implant solo Python non compilato per target Windows.

### Evasion client-side (Windows)
Tecniche tipiche per evadere AV signature-based:
- **PE encoding & obfuscation**
- **Shellcode injection** (in memoria)
- **PowerShell encoding & obfuscation** (base64, Invoke-Obfuscation)
- **PowerSploit** (shellcode injection in memory)

### Best practice canale di comunicazione
- Usa **porte standard** (443/80/8080) — meno sospetto, blende-in.
- Le porte standard sono **heavily monitored** → usa **domini, non IP raw**.
- Usa **HTTPS** per encryption.
- Configura **sleep + jitter** per random.
- Considera protocolli alternativi (DNS/53 UDP, ICMP, SMB) se HTTPS è filtrato.

### Domain Fronting (con Cloudflare)
Tecnica per **nascondere la vera destinazione** del traffico egress sfruttando CDN come Cloudflare.

**Setup tipico**:
1. Operatore registra un dominio e lo configura sui name server Cloudflare.
2. Cloudflare fa proxy di tutte le richieste → l'A record risolve a IP Cloudflare.
3. L'agent sul target è configurato per chiamare il dominio C2.
4. Il traffico esce verso un **IP Cloudflare** (fidato, comune); Cloudflare ispeziona l'`Host` header e inoltra al vero C2 server.
5. Risposta torna proxata da Cloudflare.

**Risultato**: dal perimetro target sembra traffico HTTPS legittimo verso Cloudflare. Difficile da bloccare senza bloccare Cloudflare intero. Tecnica MITRE **T1090.004 - Domain Fronting**.

### Modelli di deployment
- **Centralizzato** (un C2 server, N agent) — semplice, single point of failure.
- **Peer-to-peer** (agent comunicano tra loro, es. via SMB) — più resiliente, modello tipico Cobalt Strike con SMB beacons per host segmentati.

## Comandi & strumenti

| Concetto | Note operative |
|---|---|
| Porta C2 raccomandata | **443/TCP (HTTPS)** |
| Protocollo alternativo se filtered | **DNS (53/UDP)** o **ICMP** |
| Encoding stager PowerShell | `-EncodedCommand` base64 + Invoke-Obfuscation |
| Tool obfuscation | **Invoke-Obfuscation**, **ConfuserEx 2**, **PowerSploit** |
| Domain fronting service | **Cloudflare** (storicamente anche Fastly, Akamai) |
| MITRE ATT&CK | **T1090.004** Domain Fronting, **T1071** App Layer Protocol |

## Esempi pratici

**Setup domain fronting (concettuale, dal video)**:
1. Acquista `legit-domain.com` e configura Cloudflare name server.
2. Avvia Empire server su VPS, esponi su HTTPS:443.
3. Configura listener HTTP Empire con `Host = legit-domain.com`.
4. Genera stager → eseguilo su target.
5. L'agent contatta `legit-domain.com` → Cloudflare proxy → Empire server.
6. Operatore + collega red team si collegano via PowerShell-Empire client remoto al server.

## Punti d'attenzione per l'esame eCPPT

- **C2 in initial access è raro** — di solito si usa post-exploitation.
- **Match framework ↔ target OS**: Windows → Empire/Cobalt Strike; Linux/cross-platform → Sliver, Mythic.
- **Porte standard + domini**: mai IP raw. **443/TCP** è il default sensato.
- **Domain fronting** = MITRE **T1090.004**, classico con Cloudflare. Conosci il flusso: agent → CDN → vero C2.
- **In-memory execution PowerShell** = pilastro evasion Windows (Empire lo fa nativamente per i moduli).
- **Egress filtering**: se solo 80/443 sono aperti, scegli HTTP/HTTPS C2; se neanche quelli, prova DNS tunneling.

## Collegamenti con altri video

- Precedente: [[05_ C2 Framework Terminology]]
- Prossimo: [[07_The C2 Matrix - Choosing the Correct C2 Framework]] — scegliamo concretamente.
- Pratica: [[08_Introduction to PowerShell-Empire]] · [[09_ Red Team Ops with PowerShell-Empire]]
- Evasion in memory PowerShell: [[09_ Red Team Ops with PowerShell-Empire]]
