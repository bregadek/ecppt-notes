# 016 — Course Conclusion (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 16/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [016_Course Conclusion.txt](016_Course Conclusion.txt) · [016_Course Conclusion.srt](016_Course Conclusion.srt)

## Concetti chiave

- Video di **chiusura del modulo** — Alexis ripercorre i **learning objectives** dichiarati in introduzione e li valida uno per uno.
- Tre macro-aree coperte:
  1. **Understanding** — differenza concettuale tra Lateral Movement e Pivoting.
  2. **Lateral Movement** — tecniche/strumenti per Windows e Linux (PsExec, WMI, SMBExec, CrackMapExec, RDP, WinRM, SSH, Pass-the-Hash).
  3. **Pivoting** — multi-hop, SOCKS proxy, SSH tunneling, port forwarding, reGeorg.
- Unica lacuna dichiarata: **VPN pivoting** (non coperto per difficoltà di replica in lab; previsto in futuri update).
- Tutti i video — eccetto pochissimi puramente teorici — hanno **lab pratico associato**: Alexis raccomanda di **ripeterli**.

## Spiegazione approfondita

### Recap dei learning objectives

#### 1. Understanding Lateral Movement & Pivoting
- **Definire e distinguere** Lateral Movement (movimento tra host **dentro** un perimetro a cui hai già accesso) e Pivoting (uso di un host compromesso come **ponte** verso reti che altrimenti non raggiungeresti).
- **Impatto** in pentest / red team: misurato in termini di OS coperti (Win/Linux), livelli di accesso ottenuti e facilità di RCE.

#### 2. Lateral Movement
- **Windows**: SMB (PsExec, SMBExec, CrackMapExec), RDP, WinRM, Pass-the-Hash (Metasploit `psexec_psh`, WMIExec).
- **Linux**: principalmente **SSH** (creds, key reuse, agent hijacking).
- Competenza pratica dimostrata via lab dedicati a ciascuna tecnica.

#### 3. Pivoting
- **SSH tunneling** (`-L`, `-R`, `-D`).
- **SOCKS proxy** via Metasploit (`autoroute` + `auxiliary/server/socks_proxy` + `proxychains`).
- **Port forwarding** Metasploit (`portfwd`).
- **reGeorg** per pivot HTTP-only / web shell senza privilegi.
- **Multi-hop**: estensione a topologie complesse (più reti, più pivot in cascata).
- **Defense side**: capire come funzionano queste tecniche aiuta anche a **rilevarle e mitigarle**.

### Non coperto
- **VPN pivoting** (es. tunnel SSL/SSH-based VPN, OpenVPN over compromised host): omesso per complessità lab. Sarà aggiunto in futuro.

### Mappa mentale finale del modulo
```
LATERAL MOVEMENT & PIVOTING (modulo eCPPT)
│
├── Concetti (01_Introduction, 02_What is...)
│
├── LATERAL MOVEMENT
│   ├── Windows
│   │   ├── PsExec (03)
│   │   ├── SMBExec (04)
│   │   ├── CrackMapExec (05)
│   │   ├── RDP (06)
│   │   └── WinRM (07)
│   ├── Pass-the-Hash
│   │   ├── PtH via Metasploit (08, 09)
│   │   └── WMIExec (10)
│   └── (Linux LM → SSH, coperto trasversalmente)
│
└── PIVOTING
    ├── Concetti (11)
    ├── Port Forwarding via MSF (12)
    ├── SOCKS Proxy via MSF (13)
    ├── SSH Tunneling -L/-R/-D (14)
    └── reGeorg HTTP tunnel (15)
```

### Messaggio finale di Alexis
- Grazie a chi ha completato il corso.
- Raccomanda di **rifare i lab** una seconda volta per consolidare.
- Annuncia possibili **update futuri** al corso (nuovi video e lab, incluso VPN).
- Conclude rimandando al successivo corso del percorso eCPPT.

## Comandi & strumenti

Nessun comando nuovo in questo video. Sintesi rapida dei tool **trasversali** del modulo da padroneggiare per l'esame:

| Categoria | Tool / Comando chiave |
|---|---|
| Lateral movement Win | `psexec.py`, `smbexec.py`, `wmiexec.py`, `crackmapexec smb`, `evil-winrm`, `xfreerdp` |
| Pass-the-Hash | `crackmapexec smb <ip> -u <u> -H <NTLM>`, `psexec.py -hashes :<NTLM> <u>@<ip>` |
| Lateral movement Linux | `ssh`, key reuse, `ssh-agent` hijack |
| Pivoting MSF | `run autoroute -s <subnet>`, `auxiliary/server/socks_proxy`, `portfwd add` |
| Pivoting OS-native | `ssh -L`, `ssh -R`, `ssh -D 9050 -N -f` |
| Pivoting senza privilegi | `reGeorgSocksProxy.py -p 9050 -u <url>` |
| Proxy wrapper | `proxychains <cmd>` (sempre `-sT -Pn` per nmap) |

## Esempi pratici

Nessun lab in questo video. Per ripasso pratico → riprendere i lab dei video 12–15:

```bash
# Cheat-sheet pivoting unificato (1-pager)

# --- Metasploit SOCKS ---
msf6 > sessions -i 1
meterpreter > run autoroute -s 192.168.69.0/24
meterpreter > background
msf6 > use auxiliary/server/socks_proxy
msf6 > set SRVPORT 9050
msf6 > set VERSION 4a
msf6 > run -j

# --- SSH dynamic ---
ssh -D 9050 -N -f user@pivot

# --- reGeorg ---
# (upload tunnel.<ext> sul web server)
python reGeorgSocksProxy.py -p 9050 -u http://pivot/path/tunnel.php

# --- Uso unificato ---
proxychains nmap -sT -Pn <internal_target>
proxychains ssh root@<internal_target>
proxychains curl http://<internal_target>/
```

## Punti d'attenzione per l'esame eCPPT

- **Distinzione Lateral Movement vs Pivoting** — domanda concettuale ricorrente:
  - **Lateral Movement** = ti muovi da host a host **dentro** una rete a cui hai già accesso (es. da WS01 a WS02 via SMB/PsExec).
  - **Pivoting** = usi un host compromesso come **proxy/gateway** verso una rete a cui non hai accesso diretto (es. DMZ → LAN interna).
- **Albero decisionale pivoting** (chiave per le domande pratiche dell'esame):
  - Hai Meterpreter privilegiato? → **`autoroute` + `socks_proxy`**.
  - Hai SSH + creds sul pivot? → **`ssh -D 9050`**.
  - Hai SOLO web shell / utente non privilegiato? → **reGeorg**.
  - Ti serve UNA porta specifica? → `portfwd` o `ssh -L`.
- **Proxychains golden rules** (ricorrenti):
  - Porta default **9050**.
  - **TCP-only** → `nmap -sT -Pn` (mai `-sS`, mai `-sn`).
  - Niente UDP, niente ICMP.
- **Pass-the-Hash** funziona contro **NTLM**, non contro Kerberos puro (per quello → Overpass-the-Hash / Pass-the-Ticket, vedi modulo AD).
- **CrackMapExec / NetExec** = swiss army knife per LM Windows — memorizza `cme smb <range> -u u -H NTLM --shares / --sessions / -x cmd`.
- **OPSEC**: PsExec/SMBExec creano servizi e file su ADMIN$ → loggati; preferire WMIExec/WinRM dove possibile.
- **VPN pivoting**: non coperto qui, ma se appare → pensa a SoftEther / sshuttle / Chisel come riferimenti.
- **Pratica > teoria**: l'esame è 45 domande multiple su ambiente pratico — la familiarità con l'output reale dei comandi (errori inclusi) fa la differenza.

## Collegamenti con altri video

- Inizio modulo: [[01_Introduction]] — gli obiettivi appena riassunti.
- Tecniche LM Windows: [[03_PsExec]], [[04_SMBExec]], [[05_CrackMapExec]], [[06_RDP]], [[07_WinRM]].
- Pass-the-Hash: [[08_Pass-the-Hash with Metasploit]], [[09_Pass-the-Hash with Metasploit]], [[10_WMIExec]].
- Pivoting: [[12_Pivoting & Port Forwarding with Metasploit]], [[013_Pivoting with SOCKS Proxy]], [[014_Pivoting via SSH Tunneling]], [[015_Pivoting with reGeorg]].
- Connessione cross-modulo: l'output di questo modulo (SOCKS + proxychains) alimenta gli attacchi del modulo **Active Directory Penetration Testing** quando il DC è in rete interna.
