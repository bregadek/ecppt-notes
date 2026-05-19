# 011 — Hello World in Assembly (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 11/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [011_Hello World in Assembly.txt](011_Hello World in Assembly.txt) · [011_Hello World in Assembly.srt](011_Hello World in Assembly.srt)

## Concetti chiave

- Primo programma assembly x86/IA32 su Linux con **NASM**: stampa "Hello World" usando **syscall** Linux.
- Sezioni fondamentali di un sorgente NASM: **`section .data`** (variabili globali inizializzate), **`section .text`** (codice), **`global _start`** (entry point per il linker).
- I **commenti** in NASM iniziano con `;`.
- Per stampare su schermo si usa la **syscall `sys_write`** (numero **4** in x86 Linux) e per uscire **`sys_exit`** (numero **1**), invocate via `int 0x80`.
- Le convenzioni dei registri per `int 0x80` (Linux x86):
  - **EAX** = numero della syscall
  - **EBX** = primo argomento (es. file descriptor)
  - **ECX** = secondo argomento (es. puntatore al buffer)
  - **EDX** = terzo argomento (es. lunghezza)
- Pipeline: **`hello.asm` → `nasm -f elf32` → `hello.o` → `ld -m elf_i386` → `hello` (ELF eseguibile)**.

## Spiegazione approfondita

### Struttura di un programma NASM
```asm
section .data        ; variabili globali inizializzate
    hello db "Hello World", 0xA   ; stringa + newline (\n in hex)

section .text        ; codice eseguibile
global _start        ; entry point per il linker
_start:
    ; istruzioni qui
```

### Direttiva `db` e altre size directive
- **`db`** = define byte (1 byte/valore).
- **`dw`** = define word (2 byte).
- **`dd`** = define double word (4 byte).
- **`dq`** = define quad word (8 byte).
- I caratteri sono espressi tra `"`/`'`, valori speciali (es. newline) in hex: `0xA` = `\n`.

### Linux syscalls x86 (panoramica)
La syscall si invoca settando i registri e chiamando `int 0x80`. Tabelle complete (es. su syscalls.w3challs.com):

| #EAX | Syscall | EBX | ECX | EDX |
|---|---|---|---|---|
| **1** | `sys_exit` | exit status | — | — |
| **4** | `sys_write` | fd | *buf | count |
| **3** | `sys_read` | fd | *buf | count |

File descriptor standard:
- `0` = stdin
- `1` = stdout
- `2` = stderr

### Sorgente completo `helloworld.asm`
```asm
; ============================================
;  Hello World in x86 Assembly (Linux, NASM)
;  Author: ...
; ============================================

section .data
    hello db "Hello World", 0xA      ; stringa null-terminated con newline

section .text
global _start

_start:
    ; --- sys_write(stdout, hello, 13) ---
    mov eax, 0x4         ; syscall number = sys_write
    mov ebx, 0x1         ; fd = 1 (stdout)
    mov ecx, hello       ; pointer alla stringa
    mov edx, 13          ; lunghezza ("Hello World" = 11 + newline = 12; istr. usa 13)
    int 0x80             ; invoca il kernel

    ; --- sys_exit(0) — gracefully exit ---
    mov eax, 0x1         ; syscall number = sys_exit
    xor ebx, ebx         ; return status = 0 (XOR di un reg con sé stesso = 0)
    int 0x80
```

### Note sulle istruzioni
- **`mov dest, src`** — Intel syntax: destinazione PRIMA, sorgente DOPO.
- **`xor ebx, ebx`** — idioma comune per azzerare un registro (più corto e veloce di `mov ebx, 0`).
- **`int 0x80`** — interrupt software che attiva la syscall del kernel Linux (x86 32-bit).

### Compilazione e linking
```bash
# 1. Assemblaggio (genera l'object file)
nasm -f elf32 -o helloworld.o helloworld.asm

# 2. Linking (genera l'eseguibile ELF)
ld -m elf_i386 -o helloworld helloworld.o

# 3. Esecuzione
./helloworld
# Output: Hello World
```

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `nasm -f elf32 -o file.o file.asm` | Assembla in object file ELF 32-bit |
| `ld -m elf_i386 -o exe file.o` | Linka in eseguibile ELF i386 |
| `./exe` | Esegue il binario |

## Esempi pratici

Vedi sorgente completo sopra. Sintesi degli **opcode di data movement** menzionati:
- `mov` — sposta valore tra registri/memoria/immediati.
- `push` — pusha sullo stack.
- `pop` — poppa dallo stack.
- `lea` (Load Effective Address) — carica un indirizzo (non il valore puntato).

## Punti d'attenzione per l'esame eCPPT

- **3 sezioni standard NASM**: `.data` (initialized), `.bss` (uninitialized — vedi video 012), `.text` (codice).
- **`global _start`** = entry point Linux per `ld`. (Equivalente concettuale di `main()` in C.)
- **Convenzione syscall Linux x86 con `int 0x80`**:
  - EAX = syscall #, EBX/ECX/EDX = arg1/arg2/arg3.
  - Memorizza almeno `sys_exit = 1` e `sys_write = 4`.
- **Sintassi Intel**: `mov dest, src` (NASM/MASM). NON confondere con AT&T (GAS).
- **`xor reg, reg`** = idioma per azzerare un registro.
- Su Linux x86 sì `int 0x80`; su Linux x64 invece si usa **`syscall`** con tabella diversa e registri RDI/RSI/RDX (ABI System V).
- Questo programma è la **base degli shellcode Linux x86** — gli stessi concetti, ma con byte machine code direttamente.

## Collegamenti con altri video

- Precedente: [[010_Setting Up Our Lab]]
- Prossimo: [[012_Data Types & Variables]] — sezione `.bss`, `RES*`, debug con GDB
- Registri usati: [[04_Registers]] (EAX, EBX, ECX, EDX)
- Pipeline assemble→link: [[08_Assemblers & Compilers]]
- Pertinente a shellcoding e BO nel corso successivo Exploit Development.
