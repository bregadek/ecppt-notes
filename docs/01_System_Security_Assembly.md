---
title: "System Security & x86 Assembly Fundamentals — Studio Completo"
tags:
  - asm
  - bof
  - client-side
  - linux-privesc
  - macro
  - nmap
  - nse
  - registers
  - seh
  - shellcode
  - stack
  - sudo
  - system-security
---
# System Security & x86 Assembly Fundamentals — Studio Completo

> Riepilogo organico dei 13 video del modulo eCPPT **System Security & x86 Assembly Fundamentals** (istruttore: Alexis Ahmed — HackerSploit / INE).
> Fonte: i singoli `.md` accanto ai video in `../System Security & x86 Assembly Fundamentals/`.
> Focus: **IA32 / x86 (32-bit) su Linux con NASM**, prerequisito diretto del corso **Exploit Development** (buffer overflow, fuzzing, shellcoding).

---

## Indice (TOC)

1. [Obiettivi del modulo e posizionamento](#1-obiettivi-del-modulo-e-posizionamento)
2. [CPU Architecture](#2-cpu-architecture)
3. [Registri x86 (e mapping x64)](#3-registri-x86-e-mapping-x64)
4. [Process Memory Layout](#4-process-memory-layout)
5. [Stack: struttura e meccanica LIFO](#5-stack-struttura-e-meccanica-lifo)
6. [Stack Frames, Prologue/Epilogue, Calling Convention](#6-stack-frames-prologueepilogue-calling-convention)
7. [Assemblers, Compilers, Linkers e Pipeline di Build](#7-assemblers-compilers-linkers-e-pipeline-di-build)
8. [Sintassi Intel vs AT&T](#8-sintassi-intel-vs-att)
9. [Lab Setup (Ubuntu 16.04 32-bit + NASM)](#9-lab-setup-ubuntu-1604-32-bit--nasm)
10. [Hello World in Assembly + Syscall Linux](#10-hello-world-in-assembly--syscall-linux)
11. [Data Types & Variables (.data / .bss) + GDB](#11-data-types--variables-data--bss--gdb)
12. [Idiomi assembly ricorrenti & quick reference istruzioni](#12-idiomi-assembly-ricorrenti--quick-reference-istruzioni)
13. [Collegamento ai Buffer Overflow](#13-collegamento-ai-buffer-overflow)
14. [Punti chiave per l'esame eCPPT](#14-punti-chiave-per-lesame-ecppt)
15. [Cheat-sheet finale a 1 pagina](#15-cheat-sheet-finale-a-1-pagina)

---

## 1. Obiettivi del modulo e posizionamento

Il corso fornisce le **fondamenta low-level** indispensabili per affrontare lo studio dei buffer overflow, della reverse engineering e dello shellcoding. L'istruttore afferma esplicitamente che **questo corso è più importante dell'Exploit Development**, perché senza le basi non si capiscono i BO. Lo si vede sia nell'introduzione ([01_Course Introduction.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/01_Course%20Introduction.md)) che nella conclusione ([013_Course Conclusion.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/013_Course%20Conclusion.md)).

### Learning objectives ufficiali
1. **Computer architecture fundamentals** — CPU, registri, memoria.
2. **IA32 / x86 CPU architecture** — registri, ISA, execution pipeline.
3. **Memory organization & process memory** — text, data, BSS, heap, stack.
4. **Stack & stack frames** — ruolo nelle function call e nelle variabili locali.
5. **Introduction to IA32 assembly language** — high-level vs low-level, pipeline di compilazione.
6. **IA32 assembly basics** — istruzioni di data movement, aritmetica/logica, addressing modes.

### Posizionamento nel learning path eCPPT
```
... → System Security & x86 Assembly  (QUESTO CORSO)
                  ↓ (prerequisito diretto)
       Exploit Development            (buffer overflow, fuzzing, shellcoding)
                  ↓
       Esame eCPPT (45 MCQ in ambiente pratico)
```

### Domini abilitati dalla conoscenza dell'assembly
- **Fuzzing**
- **Exploit development**
- **Buffer overflow** (smashing the stack)
- **Debugging** a basso livello
- **Reverse engineering & malware analysis**

### Prerequisiti
- Computer architecture base (CPU, RAM).
- **C/C++** base.
- **Linux CLI**.
- Assembly: **non richiesto**.

### Scelta didattica: x86 (IA32) prima di x64
1. **Logical progression** — x64 è un'estensione di x86: il salto è quasi solo prefisso `E → R`.
2. Tanti binari legacy / risorse RE / tutorial BO partono da x86.
3. Saltare direttamente a x64 confonde perché molte risorse usano nomi `E*`.

---

## 2. CPU Architecture

La **CPU** è il "cervello" del computer: riceve **machine code** (istruzioni in hex), le decodifica ed esegue, comunicando con RAM, I/O e secondary memory. Vedi [03_CPU Architecture.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/03_CPU%20Architecture.md).

### Componenti chiave
```
+-------------------- CPU --------------------+
|  +---------+   +--------+   +-----------+   |
|  | Control |   |  ALU   |   | Registers |   |
|  |  Unit   |   |        |   |           |   |
|  +---------+   +--------+   +-----------+   |
+---------------------------------------------+
        |              |                |
       RAM        Input/Output     Secondary
                                   Memory
```

- **Control Unit (CU)** — orchestrazione del fetch-decode-execute, movimento dei dati e flusso di controllo.
- **Arithmetic Logic Unit (ALU)** — operazioni aritmetiche (`add`, `sub`, `mul`, `div`) e logiche (`and`, `or`, `not`, `xor`).
- **Registers** — piccola memoria velocissima **dentro** la CPU, volatile.

### Tipologie di registri (concetto)
- **Program Counter (PC)** — indirizzo della prossima istruzione (in x86 è **EIP**).
- **Instruction Register (IR)** — istruzione attualmente in esecuzione.
- **Accumulator** — risultato di operazioni aritmetiche/logiche (EAX in x86).
- **General Purpose Registers (GPR)** — operandi e valori intermedi.

### Machine code vs Assembly vs C
| Livello | Esempio | Note |
|---|---|---|
| Machine code | `B8 04 00 00 00` | Hex, eseguibile direttamente dalla CPU |
| Assembly (mnemonic) | `mov eax, 4` | Leggibile, mappato quasi 1:1 al machine code |
| C / C++ | `int x = 4;` | High-level, richiede compilazione |

### ISA (Instruction Set Architecture) e famiglie di CPU
- **ISA** = il "vocabolario" di istruzioni esposto dalla CPU; chi scrive codice low-level deve rispettarla.
- **x86/x64 = CISC** (Complex Instruction Set Computing) — istruzioni complesse, lunghezza variabile.
- **ARM = RISC** (Reduced Instruction Set Computing) — istruzioni semplici, lunghezza fissa, efficienza energetica. Usata in mobile, embedded, Apple Silicon M1/M2, Raspberry Pi.
- Conseguenza pratica: **codice x86 NON gira nativamente su ARM** e viceversa (serve emulazione, es. Rosetta 2 su Apple Silicon).

### Naming convention Intel (sinonimi importanti)
| Nome | Significato |
|---|---|
| **x86** | 32-bit Intel/AMD |
| **x86_64 / x64 / AMD64** | 64-bit Intel/AMD |
| **IA32** | Intel Architecture 32-bit (= x86) |
| **IA-32e / Intel 64** | 64-bit Intel |

L'istruttore usa **IA32 = x86 = 32-bit Intel assembly**.

---



### Quiz: CPU, ISA e fondamenta architetturali

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="0"></div>

## 3. Registri x86 (e mapping x64)

Approfondimento in [04_Registers.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/04_Registers.md).

I **registri** sono locazioni di memoria interne alla CPU, volatili e ad altissima velocità. **L'architettura (32 vs 64 bit) determina la larghezza dei registri.**

### Tabella dei General Purpose Registers x86

| Reg. | Nome esteso | Scopo principale |
|---|---|---|
| **EAX** | Accumulator | Operazioni aritmetiche, **valore di ritorno** delle funzioni, **numero della syscall** in `int 0x80` |
| **EBX** | Base | Puntatore a dati / base address, primo arg syscall |
| **ECX** | Counter | Contatore in loop, shift/rotate, secondo arg syscall |
| **EDX** | Data | Aritmetica (assieme a EAX), I/O, terzo arg syscall |
| **ESI** | Source Index | Puntatore alla **sorgente** in string ops (`movsb`) |
| **EDI** | Destination Index | Puntatore alla **destinazione** in string ops |
| **ESP** | Stack Pointer | Punta al **top dello stack** (indirizzo più basso popolato) |
| **EBP** | Base Pointer | Punta alla **base dello stack frame** corrente (fisso durante la funzione) |

Più, separato dai GPR:

| Reg. | Ruolo |
|---|---|
| **EIP** | **Instruction Pointer** — indirizzo della prossima istruzione. **Target #1 dei buffer overflow.** |
| **EFLAGS** | Flag di stato della CPU (zero, carry, sign, overflow, ...). |

### Naming convention completa per dimensione

| 64-bit | 32-bit | 16-bit | 8-bit High | 8-bit Low |
|---|---|---|---|---|
| RAX | EAX | AX | AH | AL |
| RBX | EBX | BX | BH | BL |
| RCX | ECX | CX | CH | CL |
| RDX | EDX | DX | DH | DL |
| RSP | ESP | SP | — | SPL |
| RBP | EBP | BP | — | BPL |
| RSI | ESI | SI | — | SIL |
| RDI | EDI | DI | — | DIL |

Mnemonica:
- Prefisso **R** = 64-bit (RAX).
- Prefisso **E** = 32-bit Extended (EAX).
- Senza prefisso = 16-bit (AX).
- Suffisso **H/L** = byte High/Low di AX (AH/AL).

```
        RAX  (64 bit)
        ├──────────────────────────────────────┐
                       EAX  (32 bit)
                       ├──────────────────────┐
                                  AX  (16 bit)
                                  ├──────────┬──────────┐
                                       AH         AL
                                     (8 hi)     (8 lo)
```

Imparando bene x86 si è già al ~80-90% di x64.

### EIP — perché conta per gli exploit
- Contiene l'indirizzo della prossima istruzione machine code.
- Non si scrive con `mov`: è aggiornato da `jmp`, `call`, `ret`.
- Se un attaccante riesce a **sovrascrivere EIP** (es. via stack overflow), redireziona l'esecuzione verso shellcode o gadget. È la base concettuale del buffer overflow.

### ESP vs EBP — la coppia dello stack frame
- **ESP** = **top mobile** dello stack; cambia con ogni `push`/`pop`/`call`/`ret`.
- **EBP** = **base fissa** dello stack frame corrente; usato come riferimento per accedere a parametri e variabili locali (`[ebp+8]`, `[ebp-4]`, ...).

---



### Quiz: Registri x86, mapping x64 e ruolo nei BO

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="1"></div>

## 4. Process Memory Layout

Vedi [05_Process Memory.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/05_Process%20Memory.md).

Gli OS moderni usano **virtual memory**: ogni processo vede uno spazio di indirizzi virtuale contiguo, da `0x00000000` al massimo addressabile (≈ 4 GB su x86). L'OS+MMU mappa virtuale → fisica trasparentemente.

### Diagramma del layout (x86 Linux)
```
HIGH addresses (es. 0xFFFFFFFF)
+----------------------------+
|   env vars / args (argv)   |
+----------------------------+
|         STACK              |  ← cresce verso il BASSO
|           ↓                |     PUSH: ESP -= 4
+----------------------------+
|         (free / gap)       |
+----------------------------+
|           ↑                |
|         HEAP               |  ← cresce verso l'ALTO (malloc/sbrk)
+----------------------------+
|         BSS                |  uninit. globals/statics → zero-filled al load
+----------------------------+
|         DATA               |  init. globals/statics
+----------------------------+
|       TEXT / CODE          |  read-only, istruzioni macchina
+----------------------------+
LOW addresses (0x00000000)
```

### Tabella dei segmenti

| Segmento | Contenuto | Permessi | Note |
|---|---|---|---|
| **Text / Code** | Istruzioni macchina | **R-X** | Read-only: protegge dal patching a runtime |
| **Data** | Globali/statiche **inizializzate** (`int g = 5;`) | **RW-** | Modificabili, occupano spazio nel binario |
| **BSS** | Globali/statiche **non inizializzate** (`static int t;`) | **RW-** | Azzerate al load time. "Block Started by Symbol" |
| **Heap** | Allocazioni dinamiche (`malloc`, `realloc`, `free`) | **RW-** | Cresce **verso l'alto** via `brk`/`sbrk` |
| **Stack** | Frame di funzioni, parametri, local vars, return address | **RW-** | Cresce **verso il basso**. Regione cruciale per i BO. |

### Direzioni di crescita (chiave per i BO!)
- **Heap**: low → high.
- **Stack**: **high → low** (controintuitivo).
- Storicamente potevano "collidere" nel mezzo (oggi mitigato da ASLR e guard pages).

### Perché esiste questa suddivisione
- **Permessi diversi**: text R-X impedisce di scrivere shellcode nel codice senza bypass.
- Separazione dati statici/dinamici/runtime per gestione efficiente.
- Permette al **loader** di mappare velocemente le sezioni del binario ELF/PE.

### Esempio C — dove finiscono le variabili
```c
int   g_init = 42;        // → DATA  (initialized global)
int   g_uninit;           // → BSS   (uninitialized global)
static int s_local = 7;   // → DATA
int main(void) {
    int local = 5;        // → STACK (variabile locale del frame di main)
    int *p = malloc(16);  // p è su STACK, ma punta a memoria sull'HEAP
    return 0;
}
```

### Strumenti per ispezionare il layout
- **`/proc/<pid>/maps`** — layout reale di un processo in esecuzione.
- **`readelf -S <binary>`** — sezioni di un ELF.
- **`gdb`** — `info proc mappings`, `maintenance info sections`.

---



### Quiz: Process memory layout e meccanica dello stack

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="2"></div>

## 5. Stack: struttura e meccanica LIFO

Vedi [06_Understanding the Stack.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/06_Understanding%20the%20Stack.md).

Lo **stack** è una struttura dati **LIFO** (Last In, First Out) — analogia: pila di libri, l'ultimo messo è il primo tolto. È l'area di memoria che contiene **function call frames, parametri, variabili locali, return address, saved registers**.

### Le due operazioni fondamentali

#### PUSH `<valore>` (x86 → 4 byte; x64 → 8 byte)
1. **Decrementa ESP** di 4.
2. **Scrive** il valore all'indirizzo puntato da ESP.

```
Prima di PUSH 1:                Dopo PUSH 1:
ESP → 0x0028FF14 [ data ]       ESP → 0x0028FF10 [   1   ]  ← nuovo top
       0x0028FF18 [ ... ]              0x0028FF14 [ data  ]
                                       0x0028FF18 [ ... ]
```

#### POP `<reg>`
1. **Legge** il valore puntato da ESP nel registro.
2. **Incrementa ESP** di 4.

```
Prima di POP EAX:               Dopo POP EAX:
ESP → 0x0028FF10 [   1   ]      ESP → 0x0028FF14 [ data ]  ← nuovo top
       0x0028FF14 [ data  ]            0x0028FF18 [ ... ]
EAX = ?                          EAX = 1
```

### Perché lo stack cresce verso il basso
Ragione storica: nei vecchi PC la RAM era limitata e divisa tra heap e stack. Stack dall'alto verso il basso, heap dal basso verso l'alto → massimo uso dello spazio condiviso.

### Esempio numerico (dal video)
- ESP iniziale = `0x0028FF14` = 2'686'848 in decimale.
- `PUSH 1` → ESP diventa `0x0028FF10` = 2'686'844 (−4 byte).
- Al top dello stack ora c'è il valore `1`.

### Visualizzazione "pila di valori"
```
HIGH addresses
  ┌─────────┐
  │    D    │   (più basso a salire)
  │    C    │
  │    B    │
  │    A    │
  ├─────────┤  ← ESP iniziale (top)
  │         │
  ↓ cresce verso il basso

Dopo PUSH E:
  ┌─────────┐
  │    D    │
  │    C    │
  │    B    │
  │    A    │
  │    E    │  ← nuovo top, ESP = ESP_prec − 4
  └─────────┘
```

### Mini-esempio NASM
```asm
mov  eax, 0x41        ; EAX = 0x41
push eax              ; stack: [0x41]               ESP -= 4
push 0x42             ; stack: [0x42][0x41]         ESP -= 4

pop  ebx              ; EBX = 0x42                  ESP += 4
pop  ecx              ; ECX = 0x41                  ESP += 4
```

### Istruzioni rilevanti

| Istruzione | Effetto su ESP | Esempio |
|---|---|---|
| `push <op>` | `ESP -= 4` poi `[ESP] = op` | `push eax`, `push 0x42` |
| `pop  <reg>` | `reg = [ESP]` poi `ESP += 4` | `pop ebx` |
| `call <addr>` | Pusha return address (EIP+1) poi salta | `call func` |
| `ret` | Poppa l'indirizzo dal top in EIP | (epilogue) |

### Casi d'uso dello stack
- **Function calls** — parametri, return address.
- **Local variables** — allocate nel frame.
- **Salvataggio registri** (callee/caller saved).
- **Context switching** (a livello kernel).

---

## 6. Stack Frames, Prologue/Epilogue, Calling Convention

Vedi [07_Stack Frames.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/07_Stack%20Frames.md).

Uno **stack frame** (aka **activation record** / **call frame**) è la struttura che il CPU/OS usa per gestire **una singola chiamata di funzione**. Contiene:
- **Parametri (arguments)**
- **Return address** (EIP salvato dalla `call`)
- **Saved EBP** del chiamante
- **Local variables**
- (opzionale) registri salvati

### Layout di uno stack frame x86 (cdecl)
```
HIGH addresses
+---------------------------+
|       arg N               |   ← parametri pushati dal CALLER in ordine inverso (cdecl)
|       ...                 |
|       arg 1               |
+---------------------------+
|   return address (EIP)    |   ← salvato AUTOMATICAMENTE da `call`
+---------------------------+
|   saved EBP (caller)      |   ← salvato dal prologue
+---------------------------+ ← EBP corrente (frame pointer della funzione)
|   local var 1             |
|   local var 2             |
|   ...                     |
+---------------------------+ ← ESP (top dello stack)
LOW addresses
```

Accessi tipici via EBP fisso:
- **Parametri**: `[ebp+8]`, `[ebp+12]`, `[ebp+16]`, ... (saltando saved EBP e ret address)
- **Local vars**: `[ebp-4]`, `[ebp-8]`, `[ebp-12]`, ...

### Prologue (analogia: "metti il segnalibro")
```asm
push ebp           ; salva EBP del chiamante
mov  ebp, esp      ; nuovo EBP = base del nuovo frame
sub  esp, N        ; alloca N byte per variabili locali
```

### Epilogue (analogia: "riprendi dal segnalibro")
```asm
mov  esp, ebp      ; libera locals
pop  ebp           ; ripristina EBP del chiamante
ret                ; pop del return address in EIP
```
oppure più compatto:
```asm
leave              ; = mov esp, ebp ; pop ebp
ret
```

### Esempio completo di funzione
```asm
my_func:
    push ebp
    mov  ebp, esp
    sub  esp, 16        ; 16 byte di local vars

    ; ... corpo funzione ...
    mov  eax, [ebp+8]   ; primo parametro
    mov  [ebp-4], eax   ; prima local var

    mov  esp, ebp       ; libera locals
    pop  ebp            ; ripristina saved EBP
    ret                 ; ret → caller
```

### Execution flow — esempio main → a → b
```c
int b() { return 0; }
int a() { b(); return 0; }
int main() { a(); return 0; }
```

```
Step 1: main             Step 2: main→a         Step 3: a→b
+--------------+         +--------------+        +--------------+
| frame main   |         | frame main   |        | frame main   |
| ← ESP        |         +--------------+        +--------------+
+--------------+         | frame a      |        | frame a      |
                         | ← ESP        |        +--------------+
                         +--------------+        | frame b      |
                                                 | ← ESP        |
                                                 +--------------+

Step 4: b ret → a        Step 5: a ret → main
+--------------+         +--------------+
| frame main   |         | frame main   |
+--------------+         | ← ESP        |
| frame a      |         +--------------+
| ← ESP        |
+--------------+
```

### `call` e `ret` in dettaglio
- **`call <addr>`** = push EIP corrente (= indirizzo della prossima istruzione del caller) + jmp `<addr>`.
- **`ret`** = pop del top dello stack in EIP → il flusso torna al chiamante.

Se l'attaccante sovrascrive il return address con un BO, `ret` salterà dove vuole → **controllo del flusso**.

### Stack vs Stack Frame
- **Stack** = intera regione di memoria LIFO.
- **Stack frame** = una singola "fetta" relativa a UNA chiamata di funzione.

---



### Quiz: Stack frames, prologue/epilogue e calling convention

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="3"></div>

## 7. Assemblers, Compilers, Linkers e Pipeline di Build

Vedi [08_Assemblers & Compilers.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/08_Assemblers%20%26%20Compilers.md) e [09_Introduction to Assembly.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/09_Introduction%20to%20Assembly.md).

### Definizioni
- **Compiler** — traduce **codice high-level** (C/C++) → assembly → object → ... 1 statement = molte istruzioni asm.
- **Assembler** — traduce **assembly** (mnemonic) → **machine code** (object file). 1 istruzione asm ≈ 1 istruzione macchina.
- **Linker** — combina uno o più `.o` (+ librerie) in un **eseguibile** (ELF su Linux, PE su Windows). Risolve simboli esterni (es. `printf` da libc).
- **Loader** (parte del SO) — mappa l'eseguibile in **process address space** e avvia l'esecuzione.

### Pipeline completa: da C all'esecuzione
```
   hello.c
      │
      ▼
[ Preprocessor (cpp) ]
      │
      ▼  hello.i         (macro espanse, #include risolti)
[ Compiler (cc1) ]
      │
      ▼  hello.s         (assembly)
[ Assembler (as / nasm) ]
      │
      ▼  hello.o         (object code) ──┐
                                          │
                  altri .o, libc, libs ───┤
                                          ▼
                                [ Linker (ld) ]
                                          │
                                          ▼  hello (ELF eseguibile)
                                          │
                                          ▼  (loader del SO)
                                process address space (RAM)
                                          │
                                          ▼
                                    esecuzione sulla CPU
```

### Verifica delle fasi con GCC
```bash
gcc -E hello.c -o hello.i      # solo preprocessor
gcc -S hello.c -o hello.s      # fino ad assembly
gcc -c hello.c -o hello.o      # fino ad object
gcc    hello.c -o hello        # eseguibile completo
```

### Pipeline assembly-only (NASM)
```
   hello.asm  ──▶ [ NASM ] ──▶ hello.o ──▶ [ ld ] ──▶ hello (ELF)
```

### Cosa fa l'assembler oltre la traduzione 1:1
- Mappa istruzioni mnemonic → opcode binari.
- Assegna **indirizzi di memoria** a variabili e istruzioni.
- Risolve **symbolic names** (label, identifier).
- Genera l'**object file** con tabelle simboli, sezioni, metadati per il linker.

### Cosa fa il linker
- Combina più object file.
- Risolve riferimenti esterni (es. `printf`).
- Combina le sezioni (`.text`, `.data`, `.bss`).
- Aggiunge header del formato eseguibile (ELF / PE).

### Tabella dei principali assembler x86

| Assembler | Sistema | Sintassi | Note |
|---|---|---|---|
| **MASM** (Microsoft Macro Assembler) | Windows / MS-DOS | Intel | Microsoft toolchain |
| **GAS** (GNU Assembler) | Linux (default GCC) | **AT&T** (Intel via direttiva) | GNU project |
| **NASM** (Netwide Assembler) ★ | Linux / cross-platform | Intel | 16/32/64-bit. **Usato nel corso.** |
| **FASM** (Flat Assembler) | Multi | Intel | |

---

## 8. Sintassi Intel vs AT&T

Stessa istruzione, due dialetti — domanda quasi garantita all'esame.

| Intel (NASM/MASM) | AT&T (GAS) |
|---|---|
| `mov eax, 4` | `movl $4, %eax` |
| `mov eax, ebx` | `movl %ebx, %eax` |
| `mov eax, [ebx]` | `movl (%ebx), %eax` |

### Differenze chiave
- **Ordine operandi**: Intel = `dest, src`. AT&T = `src, dest` (**invertito**).
- **Prefissi AT&T**: `%` per registri, `$` per immediati.
- **Suffissi size** (AT&T): `l` (long=32), `w` (word=16), `b` (byte) — es. `movl`.
- **Memoria**: Intel `[reg]` · AT&T `(reg)`.

Esempio confronto Hello World:
```asm
; --- NASM (Intel) ---
section .text
global _start
_start:
    mov eax, 1     ; sys_exit
    mov ebx, 0     ; exit code
    int 0x80
```

```asm
# --- GAS (AT&T) ---
.section .text
.globl _start
_start:
    movl $1, %eax     # sys_exit
    movl $0, %ebx     # exit code
    int  $0x80
```

**Default di GDB** su Linux = AT&T. Per passare a Intel:
```
(gdb) set disassembly-flavor intel
```

---



### Quiz: Toolchain di build, Intel vs AT&T

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="4"></div>

## 9. Lab Setup (Ubuntu 16.04 32-bit + NASM)

Vedi [010_Setting Up Our Lab.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/010_Setting%20Up%20Our%20Lab.md).

### Ambiente consigliato dal corso
- **Ubuntu 16.04.7 LTS Desktop 32-bit** in VirtualBox.
- Motivo: ambiente "predicibile" senza problemi di compatibilità con NASM 32-bit puro.
- Limite RAM per OS 32-bit: **4 GB** addressabili.

### Step di installazione
1. Scaricare la ISO Ubuntu 16.04 32-bit (~1 GB).
2. Installazione standard come VM in VirtualBox.
3. RAM ≤ 4 GB.
4. Installare **VirtualBox Guest Additions** (scaling, drag&drop, clipboard).
5. Aggiornare i pacchetti e installare il toolchain.

### Comandi
```bash
# Aggiornamento pacchetti
sudo apt-get update

# Installazione NASM + build essentials
sudo apt-get install nasm build-essential

# Verifica installazione
nasm --version
man nasm

# Verifica architettura del sistema
lscpu
uname -m              # atteso: i686 o i386

# Linker presente
which ld
```

### Editor (vim consigliato)
```vim
" ~/.vimrc
set number       " mostra numeri di riga
syntax on        " syntax highlighting
```
Alternativi: `nano`, `gedit`.

### Su una distro 64-bit
È possibile assemblare codice 32-bit con:
```bash
sudo apt-get install gcc-multilib
nasm -f elf32 -o hello.o hello.asm
ld   -m elf_i386 -o hello hello.o
```

---

## 10. Hello World in Assembly + Syscall Linux

Vedi [011_Hello World in Assembly.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/011_Hello%20World%20in%20Assembly.md).

### Struttura di un sorgente NASM
```asm
section .data        ; variabili globali inizializzate
    ; ... db / dw / dd / dq ...

section .bss         ; variabili non inizializzate (riservate)
    ; ... resb / resw / resd / resq ...

section .text        ; codice eseguibile
global _start        ; entry point per ld
_start:
    ; istruzioni
```

- **Commenti**: iniziano con `;`.
- **`global _start`** = entry point Linux per `ld` (analogo concettuale di `main()` in C).

### Convenzione syscall Linux x86 (`int 0x80`)
| Registro | Ruolo |
|---|---|
| **EAX** | numero della syscall |
| **EBX** | arg1 (es. file descriptor) |
| **ECX** | arg2 (es. puntatore al buffer) |
| **EDX** | arg3 (es. count) |

### Syscall di base
| `EAX` | Syscall | EBX | ECX | EDX |
|---|---|---|---|---|
| **1** | `sys_exit` | exit status | — | — |
| **3** | `sys_read` | fd | *buf | count |
| **4** | `sys_write` | fd | *buf | count |

File descriptor standard: `0`=stdin, `1`=stdout, `2`=stderr.

> Su **Linux x64** invece di `int 0x80` si usa l'istruzione **`syscall`**, la tabella dei numeri cambia e gli argomenti vanno in **RDI/RSI/RDX/R10/R8/R9** (ABI System V AMD64).

### Sorgente completo `helloworld.asm`
```asm
; ============================================
;  Hello World in x86 Assembly (Linux, NASM)
; ============================================

section .data
    hello db "Hello World", 0xA   ; stringa + newline (\n in hex)

section .text
global _start

_start:
    ; --- sys_write(stdout, hello, 13) ---
    mov eax, 0x4         ; syscall # = sys_write
    mov ebx, 0x1         ; fd = 1 (stdout)
    mov ecx, hello       ; pointer alla stringa
    mov edx, 13          ; lunghezza
    int 0x80             ; invoca il kernel

    ; --- sys_exit(0) ---
    mov eax, 0x1         ; syscall # = sys_exit
    xor ebx, ebx         ; return status = 0 (xor reg, reg = azzera)
    int 0x80
```

### Build & run
```bash
nasm -f elf32 -o helloworld.o helloworld.asm
ld   -m elf_i386 -o helloworld   helloworld.o
./helloworld
# Output: Hello World
```

### Direttive "Define" (variabili inizializzate)
| Direttiva | Dimensione | Esempio |
|---|---|---|
| **`db`** | 1 byte | `msg db "A", 0` |
| **`dw`** | 2 byte (word) | `n   dw 0x1234` |
| **`dd`** | 4 byte (dword) | `cnt dd 100` |
| **`dq`** | 8 byte (qword) | `big dq 0xFFFFFFFFFFFFFFFF` |

---



### Quiz: NASM, syscall Linux x86 e direttive data/bss

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="5"></div>

## 11. Data Types & Variables (.data / .bss) + GDB

Vedi [012_Data Types & Variables.md](../System%20Security%20%26%20x86%20Assembly%20Fundamentals/012_Data%20Types%20%26%20Variables.md).

### Direttive "Reserve" (variabili non inizializzate, BSS)
| Direttiva | Dimensione | Esempio |
|---|---|---|
| **`resb`** | 1 byte/elem | `val resb 1` |
| **`resw`** | 2 byte/elem | `arr resw 10` (20 byte) |
| **`resd`** | 4 byte/elem | `buf resd 64` (256 byte) |
| **`resq`** | 8 byte/elem | `big resq 4` (32 byte) |

### Differenza `.data` vs `.bss`
|  | `.data` | `.bss` |
|---|---|---|
| Stato iniziale | **Inizializzato** dal programmatore | **Zero-filled** dall'OS al load |
| Direttive | `db, dw, dd, dq` | `resb, resw, resd, resq` |
| Occupa spazio nel binario | **Sì** (i valori sono nel file) | **No** (solo metadati: "riserva N byte") |
| Tipico contenuto | Costanti, stringhe note, LUT | Buffer, array di scratch |

### Esempio `variables.asm`
```asm
section .text
global _start

_start:
    xor eax, eax              ; EAX = 0
    mov eax, 0x41             ; EAX = 'A' (0x41 = 65)
    mov [val], eax            ; salva EAX nella memoria di `val`
                              ;  → solo il byte basso (AL) finisce in val (resb 1)

    ; --- exit ---
    xor ebx, ebx              ; return status 0
    mov eax, 0x1              ; sys_exit
    int 0x80

section .bss
    val resb 1                ; 1 byte non inizializzato
```

**`[val]` vs `val`**:
- `[val]` (con parentesi quadre) = **valore alla locazione di `val`**.
- `val` (senza) = **indirizzo** di `val`.

### Build & ispezione con GDB (il programma non stampa nulla)
```bash
nasm -f elf32 -o variables.o variables.asm
ld   -m elf_i386 -o variables variables.o
./variables          # nessun output

gdb -q ./variables
(gdb) set disassembly-flavor intel
(gdb) set pagination off
(gdb) info functions
(gdb) disassemble _start
(gdb) break *_start+14         ; subito dopo mov [val], eax
(gdb) run
(gdb) x /s &val                ; → "A"
(gdb) info registers
```

### Reference comandi GDB utili
| Comando | Scopo |
|---|---|
| `set disassembly-flavor intel` | Disassembly Intel (default è AT&T) |
| `info functions` | Lista funzioni |
| `disassemble <fn>` | Disassembla una funzione |
| `break *_start+N` | Breakpoint a offset N |
| `run` / `r` | Avvia |
| `x /s <addr>` | Esamina come stringa |
| `x /x <addr>` | Esamina come hex |
| `info registers` | Stato di tutti i registri |

---

## 12. Idiomi assembly ricorrenti & quick reference istruzioni

### Idiomi da riconoscere SEMPRE
- **`xor reg, reg`** → azzera il registro. Più corto/veloce di `mov reg, 0`, e soprattutto **non contiene byte `0x00`** → fondamentale negli **shellcode** (i byte null rompono le stringhe terminate da null).
- **`push 0 / pop reg`** → idem per azzerare.
- **`mov [var], reg`** vs **`mov reg, [var]`** → scrittura vs lettura in memoria.
- **`lea reg, [var]`** → carica un **indirizzo** (non il valore puntato). Anche usato per aritmetica veloce.

### Data movement
| Istruzione | Effetto |
|---|---|
| `mov dst, src` | Copia un valore (registro, immediato, memoria) |
| `push op` | `ESP -= 4; [ESP] = op` |
| `pop  reg` | `reg = [ESP]; ESP += 4` |
| `lea reg, [expr]` | Load Effective Address (carica l'indirizzo, non il valore) |

### Aritmetica/logica (ALU)
| Istruzione | Effetto |
|---|---|
| `add dst, src` | `dst = dst + src` |
| `sub dst, src` | `dst = dst - src` |
| `mul / imul` | Moltiplicazione (unsigned / signed) |
| `div / idiv` | Divisione |
| `and, or, xor, not` | Operazioni logiche |
| `shl, shr` | Shift sinistro/destro |
| `inc, dec` | Incrementa/decrementa |

### Control flow
| Istruzione | Effetto |
|---|---|
| `jmp label` | Salto incondizionato |
| `je / jne / jg / jl / jz / jnz / ...` | Salti condizionati (basati su EFLAGS) |
| `cmp a, b` | Setta EFLAGS in base ad `a - b` |
| `call addr` | Push del return address + jmp |
| `ret` | Pop in EIP |
| `int 0x80` | Software interrupt (syscall Linux x86) |

### String ops (rilevanti per shellcoding/RE)
- `movsb` / `rep movsb` — copia byte da `[ESI]` a `[EDI]`, ECX volte.
- `stosb` / `lodsb` — store/load tramite ESI/EDI.

---



### Quiz: Idiomi assembly, GDB e collegamento ai buffer overflow

<div class="ecppt-quiz" data-module="01_System_Security_Assembly" data-block="6"></div>

## 13. Collegamento ai Buffer Overflow

Anche se i BO sono coperti nel corso successivo (**Exploit Development**), questo modulo dà tutti i mattoni concettuali. La meccanica:

1. La funzione vulnerabile alloca un **buffer locale** sullo stack (sotto EBP, in `[ebp-N]`).
2. Una funzione di copy **senza bound check** (es. `gets`, `strcpy`, `sprintf`) scrive **oltre** la dimensione del buffer.
3. La scrittura "sale" lungo lo stack (verso indirizzi più alti) e sovrascrive in ordine:
   - **saved EBP**
   - **return address (saved EIP)**
   - parametri / frame del caller
4. Quando la funzione fa `ret`, esegue **pop del return address corrotto in EIP** → l'attaccante controlla il flusso.
5. Si redireziona EIP verso **shellcode** (spesso piazzato sullo stack stesso, in mancanza di DEP/NX) o verso una gadget chain (ROP) se le mitigations sono attive.

```
ATTACCO: scrittura di un buffer locale OLTRE i limiti

      EBP-N  [ buffer ]   ← scrittura inizia qui
      ...    [ ...    ]   ← supera la dimensione
   EBP    →  [ saved EBP ]   ← sovrascritto
   EBP+4  →  [ ret addr  ]   ← sovrascritto con l'indirizzo dello shellcode
                ↑
            controllato dall'attaccante → CFI compromessa
```

Pre-requisiti concettuali (tutti coperti qui):
- Direzione di crescita dello stack (high → low).
- Layout dello stack frame (param / ret / saved EBP / locals).
- Ruolo di EIP e meccanica di `ret`.
- Convenzione di chiamata cdecl.
- Idioma `xor reg, reg` (per evitare null byte negli shellcode).
- Syscall `int 0x80` con EAX/EBX/ECX/EDX (per scrivere shellcode `execve`).

---

## 14. Punti chiave per l'esame eCPPT

L'esame eCPPT 2024 è composto da **45 domande a risposta multipla** in ambiente pratico. Non si scrive assembly avanzato, ma si deve **riconoscere** strutture e rispondere a domande concettuali. Aspettarsi tipicamente:

### Concettuali (alta probabilità)
- **Distinzione x86 vs x64**: registri `E*` vs `R*`. Esempio: "il valore di ritorno di una funzione su x86 sta in?" → **EAX**.
- **8 GPR x86** + EIP: nomi e scopo (Accumulator, Base, Counter, Data, Source Index, Destination Index, Stack Pointer, Base Pointer).
- **EIP è il target #1 del buffer overflow.**
- **ESP vs EBP**: ESP top mobile, EBP base fissa del frame.
- **Stack cresce verso indirizzi BASSI** (controintuitivo!). `push` ↓ ESP, `pop` ↑ ESP. Su x86 di 4 byte, su x64 di 8.
- **Heap cresce verso indirizzi ALTI**.
- **Layout process memory** top→bottom: STACK ↓ … HEAP ↑ BSS DATA TEXT.
- **Text/Code = read-only**.
- **DATA = init / BSS = uninit (zero-filled al load)**.
- **LIFO** = struttura dello stack.
- **Stack frame** contiene: **args · saved EIP (return address) · saved EBP · local vars**.
- **Prologue/Epilogue**: `push ebp; mov ebp, esp; sub esp, N` / `mov esp, ebp; pop ebp; ret` (oppure `leave; ret`).
- **`call`** = push EIP + jmp; **`ret`** = pop in EIP.
- **`int 0x80`** = syscall Linux x86; EAX = syscall #, EBX/ECX/EDX = args. Memorizza `sys_exit = 1`, `sys_write = 4`.
- **Pipeline C → eseguibile**: preprocessor → compiler → assembler → linker → loader.
- **NASM = Intel syntax**, **GAS = AT&T syntax di default**. Intel `dest, src`, AT&T `src, dest`.
- **Object file (.o) non è eseguibile** — serve il linker.
- **ISA** specifica per CPU: codice x86 NON gira nativamente su ARM (Apple M1/M2 = ARM, serve Rosetta 2).
- **CISC = x86/x64**, **RISC = ARM**.
- **xor reg, reg** = idioma di azzeramento (anche in shellcode per evitare null byte).

### Pratiche / riconoscimento
- Distinguere un prologue da un epilogue in un disassembly.
- Identificare `int 0x80` come syscall x86.
- Capire che `[var]` = valore, `var` = indirizzo.
- Riconoscere le direttive NASM `db/dw/dd/dq` e `resb/resw/resd/resq`.
- Comandi base di GDB: `disassemble`, `break`, `x /s`, `x /x`, `info registers`, `set disassembly-flavor intel`.
- Lab: `nasm -f elf32 -o file.o file.asm` → `ld -m elf_i386 -o exe file.o`.

### Sinonimi da non confondere
- **x86 = IA32 = 32-bit Intel** · **x64 = x86_64 = AMD64 = Intel 64 = 64-bit Intel**.

---

## 15. Cheat-sheet finale a 1 pagina

> 📋 La cheat sheet originalmente qui presente è stata spostata nel modulo dedicato: vedi [Cheat Sheet — sezione Assembly & System Internals](../10_Cheatsheet.md#assembly-system-internals).

---

> **Prossimo modulo del learning path**: *Exploit Development Buffer Overflows* — fuzzing, stack smashing, SEH overflow, shellcoding. Tutte le basi sono in questo documento.
