# 02 — Introduction to Lateral Movement & Pivoting

> **Modulo:** Lateral Movement & Pivoting · **Video:** 2/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Introduction to Lateral Movement & Pivoting.txt](02_Introduction to Lateral Movement & Pivoting.txt) · [02_Introduction to Lateral Movement & Pivoting.srt](02_Introduction to Lateral Movement & Pivoting.srt)

## Concetti chiave

- **Lateral Movement** = processo di muoversi **da un host compromesso ad altri host** della **stessa rete**, tipicamente riusando credenziali/hash.
- **Pivoting** = uso di un host compromesso come **stepping stone (pivot)** per accedere a **un'altra rete/segmento** altrimenti non raggiungibile dall'attaccante.
- I due termini sono spesso usati interscambiabilmente ma **non sono sinonimi**.
- Lateral movement abusa di **protocolli di autenticazione remota**: SMB, RDP, WinRM, WMI, SSH.
- Pivoting usa **routing/forwarding**: port forwarding, SSH tunneling, VPN, SOCKS proxy.

## Spiegazione approfondita

### Lateral Movement
- Scenario tipico: pentest interno, gain di una sola macchina, dump di credenziali/hash, riuso per autenticarsi su altri host.
- Obiettivo: **escalate access & privileges**, raggiungere high-value target / sensitive data.
- Mezzi: vulnerabilità in servizi di rete, credential dumping, shared resources, remote access (RDP/SSH/WMI).
- Su Windows si possono usare **hash** (Pass-the-Hash via SMB) oltre alle clear-text; su Linux **solo clear-text** o **chiavi SSH** — questa è la ragione della divisione in due sezioni del corso.

### Pivoting
- Scenario tipico: si compromette un server publicly-exposed (DMZ) che ha **due interfacce di rete** — una verso Internet e una verso una rete interna inaccessibile.
- Si usa quel host come **proxy/hop** per raggiungere i sistemi della rete interna.
- Tecniche: port forwarding, SSH tunneling, VPN, SOCKS proxy.

### Diagramma topologia (pivoting tipico)

```
   Attacker                  Pivot/Compromised             Target
 (192.168.1.2)              Victim 1                     Victim 2
       │              ┌──────────────────────┐                │
       │   eth0       │ eth0  192.168.1.X    │                │
       │──────────────│                      │                │
       │ 192.168.1.0/24                      │                │
                      │ eth1  10.10.10.X     │  10.10.10.0/24 │
                      │──────────────────────│────────────────│
                                                              │
   L'attacker NON vede direttamente 10.10.10.0/24 — passa attraverso Victim 1
```

### Le 3 differenze chiave (tabella fondamentale)

| Aspetto | Lateral Movement | Pivoting |
|---|---|---|
| **Scope** | Stessa rete / segmento | Da una rete a un'altra rete/segmento |
| **Approach** | Exploit vuln, credential reuse, hash | Routing complesso, tunnel, proxy |
| **Objective** | Privilege escalation, estendere accesso | Bypassare network boundaries, raggiungere segmenti isolati |

## Comandi & strumenti

Video teorico — nessun comando. Tool richiamati:
- Lateral movement: PsExec, WMI, SSH, RDP.
- Pivoting: SSH tunnels, VPN, SOCKS proxy, bastion server.

## Esempi pratici

- **Lateral movement**: compromesso Windows → dump hash NTLM → riuso hash via SMB con PsExec su altri host della stessa LAN.
- **Pivoting**: compromesso web server DMZ (192.168.1.X / 10.10.10.X) → port forwarding/SSH tunnel attraverso esso → scan e exploit di host nella 10.10.10.0/24.

## Punti d'attenzione per l'esame eCPPT

- **Questa è LA domanda d'esame ricorrente**: dato uno scenario, è lateral movement o pivoting?
  - "Stesso /24, riuso hash su altro host" → **lateral movement**.
  - "Subnet diversa raggiungibile solo via host compromesso" → **pivoting**.
- Le due tecniche **si combinano**: spesso si fa pivoting su una rete interna e poi lateral movement al suo interno.
- Su Linux **non esiste Pass-the-Hash** (a meno di SSH agent forwarding); il principale vettore di lateral movement è SSH (chiavi/password riutilizzate).
- Pivoting richiede che il pivot abbia **due interfacce** o comunque routing verso la rete target.

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_Windows Lateral Movement Techniques]] — inizio sezione Windows.
- Pivoting pratico: [[012_Pivoting & Port Forwarding with Metasploit]]
- Linux lateral movement: [[011_Linux Lateral Movement Techniques]]
