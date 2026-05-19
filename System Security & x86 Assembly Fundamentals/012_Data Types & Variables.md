# 012 — Data Types & Variables (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 12/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [012_Data Types & Variables.txt](012_Data Types & Variables.txt) · [012_Data Types & Variables.srt](012_Data Types & Variables.srt)

## Concetti chiave

- In NASM le **variabili inizializzate** si dichiarano in `section .data` con le direttive **`db / dw / dd / dq`** (byte/word/dword/qword).
- Le **variabili non inizializzate** (riservate) vanno in `section .bss` con **`resb / resw / resd / resq`** (reserve byte/word/dword/qword).
- Il segmento **BSS** è azzerato automaticamente al load del programma.
- L'idioma **`xor eax, eax`** azzera un registro (usato sia per init sia per `sys_exit` return = 0).
- Si può ispezionare il valore di una variabile BSS a runtime con **GDB** (`break`, `run`, `x /s <var>`).

## Spiegazione approfondita

### Direttive di dichiarazione

#### Variabili inizializzate (`.data`) — Define
| Direttiva | Dimensione | Esempio |
|---|---|---|
| **`db`** | 1 byte | `msg db "A", 0` |
| **`dw`** | 2 byte (word) | `n   dw 0x1234` |
| **`dd`** | 4 byte (dword) | `cnt dd 100` |
| **`dq`** | 8 byte (qword) | `big dq 0xFFFFFFFFFFFFFFFF` |

#### Variabili riservate (`.bss`) — Reserve
| Direttiva | Dimensione | Esempio |
|---|---|---|
| **`resb`** | 1 byte/elem | `val resb 1` |
| **`resw`** | 2 byte/elem | `arr resw 10` (20 byte) |
| **`resd`** | 4 byte/elem | `buf resd 64` (256 byte) |
| **`resq`** | 8 byte/elem | `big resq 4` (32 byte) |

### Esempio del video — `variables.asm`
```asm
section .text
global _start

_start:
    xor eax, eax              ; EAX = 0
    mov eax, 0x41             ; EAX = 'A' (0x41 = 65 = lettera A)
    mov [val], eax            ; salva il valore di EAX nella variabile `val`

    ; --- gracefully exit ---
    xor ebx, ebx              ; return status 0
    mov eax, 0x1              ; sys_exit
    int 0x80

section .bss
    val resb 1                ; riserva 1 byte non inizializzato
```

Note:
- `[val]` (con parentesi quadre) = **valore alla locazione di `val`**; senza parentesi = **indirizzo** di `val`.
- `resb 1` riserva 1 byte: lo aggiorneremo con il primo byte di EAX (cioè AL = `0x41`).

### Compilazione e link
```bash
nasm -f elf32 -o variables.o variables.asm
ld   -m elf_i386 -o variables variables.o
./variables          # non stampa nulla — la verifica si fa con GDB
```

### Verifica con GDB
Dato che il programma non stampa, si usa GDB per ispezionare la BSS:
```bash
gdb -q ./variables
(gdb) set disassembly-flavor intel
(gdb) set pagination off
(gdb) info functions
(gdb) disassemble _start
(gdb) break *_start+14         ; breakpoint subito dopo l'assegnazione di val
(gdb) run
(gdb) x /s &val                ; esamina come stringa il contenuto di val
        →  0x...: "A"          ; conferma: val è stato aggiornato a 'A'
```

### Differenza `.data` vs `.bss`
| | `.data` | `.bss` |
|---|---|---|
| Stato iniziale | **Inizializzato** dal programmatore | **Zero-filled** dall'OS al load |
| Direttive | `db, dw, dd, dq` | `resb, resw, resd, resq` |
| Occupa spazio nel binario? | **Sì** (i valori sono nel file) | **No** (solo metadati: "riserva N byte") |
| Tipico contenuto | Costanti, stringhe note, lookup table | Buffer, array di lavoro, variabili di scratch |

### Idioma `xor reg, reg`
- `xor eax, eax` → EAX = 0 (qualsiasi valore XOR con sé stesso = 0).
- Più efficiente di `mov eax, 0` (opcode più corto, dipendenza meno problematica nella pipeline).
- Comunissimo in shellcode (anche perché `0x00` nei byte di un `mov` può rompere stringhe terminate da null).

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `nasm -f elf32 -o file.o file.asm` | Assembla |
| `ld -m elf_i386 -o exe file.o` | Linka |
| `gdb -q ./exe` | Avvia GDB silenziosamente |
| `set disassembly-flavor intel` | Mostra disassembly in sintassi Intel (default è AT&T) |
| `info functions` | Lista le funzioni |
| `disassemble <fn>` | Disassembla |
| `break *_start+N` | Breakpoint a offset N dall'inizio di `_start` |
| `run` / `r` | Avvia l'esecuzione |
| `x /s <addr>` | Esamina memoria come stringa |
| `x /x <addr>` | Esamina come hex |
| `info registers` | Stato di tutti i registri |

## Esempi pratici

Variante con allocazione più grande (es. buffer 64 byte):
```asm
section .bss
    buffer resb 64        ; 64 byte non inizializzati

section .data
    msg    db  "Hello", 0xA, 0
    n      dd  42         ; integer 32-bit
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza le 4 direttive `D*` per .data e le 4 `RES*` per .bss** — è il pattern minimo per qualsiasi programma NASM.
- **`.bss` è azzerato al load** — utile sapere per shellcoding (puoi assumere zero-initialized).
- **`[var]` vs `var`**: con parentesi = valore, senza = indirizzo. Errore comune.
- **`xor reg, reg`** = idioma da riconoscere SEMPRE nel disassembly: significa azzeramento.
- **GDB**:
  - `set disassembly-flavor intel` (default Linux è AT&T — confusione frequente).
  - `x /s`, `x /x`, `info registers`: comandi base per RE.
- **AL (8-bit low di EAX)** contiene il byte basso → assegnare 0x41 a EAX e salvare il primo byte in `resb 1` significa che `val` conterrà 'A'.
- Differenza tra **dimensioni**: byte (8) · word (16) · dword (32) · qword (64). Memorizza.

## Collegamenti con altri video

- Precedente: [[011_Hello World in Assembly]] — sezione `.data` e `.text`
- Prossimo: [[013_Course Conclusion]]
- Memoria di processo (dove vive .bss): [[05_Process Memory]]
- Registri usati: [[04_Registers]] (EAX/EBX, AL come byte basso)
- GDB e debugging sono propedeutici al corso Exploit Development.
