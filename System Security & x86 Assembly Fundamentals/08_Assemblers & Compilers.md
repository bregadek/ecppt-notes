# 08 — Assemblers & Compilers (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 8/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [08_Assemblers & Compilers.txt](08_Assemblers & Compilers.txt) · [08_Assemblers & Compilers.srt](08_Assemblers & Compilers.srt)

## Concetti chiave

- Un **assembler** è un *language translator* che converte **assembly** in **machine code** eseguibile direttamente dalla CPU (in base alla ISA).
- L'output dell'assembler è un **object file** (binario, `.o` su Linux, `.obj` su Windows).
- Per ottenere un **eseguibile** occorre un **linker** che combini uno o più object file (e librerie) in un binario eseguibile (`ELF` su Linux, `.exe` su Windows).
- Un **compiler** traduce **codice high-level** (es. C/C++) in **assembly** (e poi macchina), passando per i medesimi step di assemblaggio e linking.
- I principali assembler x86:
  - **MASM** (Microsoft Macro Assembler) — Windows, sintassi Intel.
  - **GAS / GNU Assembler** — default backend di GCC, sintassi **AT&T** (di default).
  - **NASM** (Netwide Assembler) — **il più popolare su Linux**, sintassi Intel, supporta 16/32/64 bit. ★ Quello usato nel corso.
  - **FASM** (Flat Assembler) — x86 Intel-style.

## Spiegazione approfondita

### Pipeline: da assembly all'eseguibile
```
   hello.asm  ──▶  [ Assembler (NASM) ]  ──▶  hello.o (object file)
                                                  │
                                                  ▼
                                          [ Linker (ld) ] ◀── librerie/altri .o
                                                  │
                                                  ▼
                                              hello (ELF)  ──▶ esecuzione
```

### Pipeline: da C all'eseguibile (più completa, vista nel video 09)
```
   hello.c  ──▶ [ Preprocessor ] ──▶ hello.i
            ──▶ [ Compiler ]     ──▶ hello.s  (assembly)
            ──▶ [ Assembler ]    ──▶ hello.o  (object)
            ──▶ [ Linker + libs ]──▶ hello    (executable)
```

### Cosa fa un Assembler oltre la traduzione 1:1
- Mappa **istruzioni mnemonic → opcode binari**.
- **Assegna indirizzi di memoria** a variabili e istruzioni.
- **Risolve symbolic names** (labels, identifier).
- Genera l'**object file** in formato binario (con metadati per il linker: tabelle simboli, sezioni).

### Cosa fa un Linker
- Prende uno o più object file.
- Risolve riferimenti esterni (es. `printf` da `libc`).
- Combina sezioni (`.text`, `.data`, `.bss`) in un eseguibile finale.
- Aggiunge header del formato eseguibile (ELF su Linux, PE su Windows).

### Compiler vs Assembler
| | Compiler | Assembler |
|---|---|---|
| **Input** | High-level (C/C++) | Assembly mnemonic |
| **Output** | Assembly o object | Object file |
| **Mapping** | 1 statement → molte istruzioni asm | 1 istruzione asm → ~1 istruzione macchina |
| **Esempio tool** | gcc, clang | nasm, masm, gas |

### Tabella riassuntiva degli assembler

| Assembler | Sistema | Sintassi | Note |
|---|---|---|---|
| **MASM** | Windows / MS-DOS | Intel | Microsoft Macro Assembler |
| **GAS** | Linux (default GCC) | **AT&T** (può Intel con direttiva) | GNU project |
| **NASM** ★ | Linux (cross-platform) | Intel | 16/32/64-bit, **usato nel corso** |
| **FASM** | Multi | Intel | Flat Assembler |

### Intel vs AT&T syntax (concetto chiave)
Stessa istruzione, due dialetti:

| Intel (NASM/MASM) | AT&T (GAS) |
|---|---|
| `mov eax, 4` | `movl $4, %eax` |
| `mov eax, ebx` | `movl %ebx, %eax` |
| `mov eax, [ebx]` | `movl (%ebx), %eax` |

Differenze principali:
- **Ordine operandi**: Intel = `dest, src`. AT&T = `src, dest` (invertito!).
- **Prefissi**: AT&T usa `%` per registri, `$` per immediati.
- **Suffissi size**: AT&T usa `l` (long=32), `w` (word=16), `b` (byte) — es. `movl`.
- Memoria: Intel `[reg]` · AT&T `(reg)`.

## Comandi & strumenti

Comandi tipici (verranno mostrati nei video 010-011):

```bash
# Assemblaggio con NASM (Linux 32-bit ELF)
nasm -f elf32 -o hello.o hello.asm

# Linking con ld
ld -m elf_i386 -o hello hello.o

# Esecuzione
./hello
```

## Esempi pratici

Mini-confronto sintattico:

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

## Punti d'attenzione per l'esame eCPPT

- **NASM** è l'assembler di riferimento per Linux x86 — memorizzane il nome e il fatto che usa **sintassi Intel**.
- **GAS (AT&T)** è il default su Linux per GCC → quando disassembli con `objdump -d` vedrai AT&T (a meno di `-M intel`).
- **MASM** = Windows.
- Differenza **assembler ≠ compiler**: l'assembler traduce assembly, il compiler traduce C/C++.
- **Object file (.o) non è eseguibile** — serve il linker per produrre l'ELF/PE finale.
- Pipeline: **source → preprocessor → compiler → assembler → linker → executable**. Sapere l'ordine è una domanda concettuale frequente.
- **Intel vs AT&T**: ordine `dest, src` (Intel) vs `src, dest` (AT&T) — domanda ricorrente, spesso confonde.

## Collegamenti con altri video

- Precedente: [[07_Stack Frames]] (fine sezione architettura)
- Prossimo: [[09_Introduction to Assembly]] — approfondimento sul ruolo dell'assembly
- Lab setup con NASM: [[010_Setting Up Our Lab]]
- NASM in pratica: [[011_Hello World in Assembly]] · [[012_Data Types & Variables]]
