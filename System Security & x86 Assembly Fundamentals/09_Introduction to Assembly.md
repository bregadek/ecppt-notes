# 09 — Introduction to Assembly (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 9/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [09_Introduction to Assembly.txt](09_Introduction to Assembly.txt) · [09_Introduction to Assembly.srt](09_Introduction to Assembly.srt)

## Concetti chiave

- L'**assembly language** è un linguaggio di programmazione **low-level**, strettamente legato all'**ISA del CPU target**.
- Diverse CPU = diversi dialetti assembly: **x86/x64 (Intel/AMD)** vs **ARM** (mobile, embedded, Apple Silicon M1/M2).
- L'**assembly Intel** include due famiglie: **x86 (IA32)** = 32-bit e **x86_64 / Intel 64** = 64-bit.
- Nel corso si parte da **IA32 (x86) su Linux** perché:
  1. molti sistemi/processori usano ancora 32-bit e i 64-bit lo supportano;
  2. è il punto di partenza logico — passare a x64 dopo aver imparato x86 è quasi banale (solo cambio di prefisso registri E→R).
- Pipeline completa **da codice C all'esecuzione**: preprocessor → compiler → assembler → linker → loader.

## Spiegazione approfondita

### Assembly = mnemonic representation del machine code
Esempi tipici:
```asm
mov eax, ebx     ; copia EBX in EAX
add eax, ebx     ; EAX = EAX + EBX
```
Ogni mnemonic ha (quasi sempre) una corrispondenza diretta con uno o pochi opcode in machine code.

### Famiglie di CPU rilevanti
| Famiglia | Architettura | Dispositivi tipici | Assembly |
|---|---|---|---|
| **Intel / AMD** | x86 / x64 (CISC) | PC, server, laptop classici | x86 ASM / x86_64 ASM |
| **ARM** | ARM (RISC) | Mobile, embedded, MacBook M1/M2, Raspberry Pi | ARM ASM |

**Conseguenza pratica**: codice x86 NON gira nativamente su ARM (e viceversa). Per eseguire binari Intel su Apple Silicon serve **Rosetta 2** (emulazione).

### Naming convention Intel
| Nome | Significato |
|---|---|
| **x86** | 32-bit Intel/AMD |
| **x86_64 / x64 / AMD64** | 64-bit Intel/AMD |
| **IA32** | Intel Architecture 32-bit (= x86) |
| **IA-32e / Intel 64** | Intel 64-bit |

L'istruttore usa **IA32** = **x86** = 32-bit Intel assembly.

### Pipeline da C a esecuzione (diagramma)
```
   hello.c
      │
      ▼
[ Preprocessor (cpp) ]
      │
      ▼
   hello.i         (codice C pre-processato, macro espanse, #include risolti)
      │
      ▼
[ Compiler (cc1) ]
      │
      ▼
   hello.s         (assembly)
      │
      ▼
[ Assembler (as / nasm) ]
      │
      ▼
   hello.o         (object code) ──┐
                                   │
                  altri .o, libc, ─┤
                  static libs    ──┤
                                   ▼
                        [ Linker (ld) ]
                                   │
                                   ▼
                                hello       (eseguibile, es. ELF)
                                   │
                                   ▼   (loader del SO)
                            process address space (RAM)
                                   │
                                   ▼
                              esecuzione CPU
```

### Da assembly a CPU (vista dell'assembler/linker)
Il programmatore scrive `mov eax, ebx; add eax, ebx; ...` → l'**assembler + linker** trasformano questo in machine code che la CPU sa eseguire direttamente.

### Perché imparare x86 (32-bit) e non subito x64?
1. **Logical progression**: x64 è un'estensione di x86; capendo x86 si è già all'80%.
2. Molti **binari legacy** sono x86 — la maggior parte dei tutorial RE/exploit dev partono da x86.
3. Studenti che saltano direttamente a x64 si confondono perché molte risorse usano nomi `E*` (x86).
4. La differenza principale x86→x64 è il **prefisso R** sui registri (RAX vs EAX) + più registri (R8-R15) + ABI di chiamata diversa.

## Comandi & strumenti

Nessun comando eseguito (video teorico). Tool della pipeline:
- **`cpp`** — C preprocessor
- **`gcc -S`** — produce assembly da C
- **`nasm`** — assembler scelto nel corso
- **`ld`** — linker GNU
- **Loader del SO** — mappa l'eseguibile in memoria virtuale

## Esempi pratici

Visualizzazione dell'output di ogni fase con GCC:
```bash
gcc -E hello.c -o hello.i      # solo preprocessor
gcc -S hello.c -o hello.s      # fino ad assembly
gcc -c hello.c -o hello.o      # fino ad object
gcc    hello.c -o hello        # eseguibile completo
```

## Punti d'attenzione per l'esame eCPPT

- **Assembly è ISA-specifico**: x86 ≠ ARM. Domanda concettuale: "il codice x86 può girare su un Mac M1?" → **no nativamente**.
- Sinonimi da memorizzare: **x86 = IA32 = 32-bit Intel** · **x64 = x86_64 = AMD64 = Intel 64 = 64-bit Intel**.
- La **pipeline C → eseguibile** ha 5 step (preprocessor, compiler, assembler, linker, loader). Domanda ricorrente sull'ordine.
- L'**eseguibile finale** (ELF/PE) viene caricato in **process address space** (vedi video 05) dal **loader del SO**.
- Il corso e l'esame si focalizzano su **x86 (32-bit) Linux con NASM** — è il "default" per esercitazioni BO base.

## Collegamenti con altri video

- Precedente: [[08_Assemblers & Compilers]]
- Prossimo: [[010_Setting Up Our Lab]] — installiamo NASM su Ubuntu
- Memoria di processo (dove finisce l'eseguibile): [[05_Process Memory]]
- Primo programma assembly: [[011_Hello World in Assembly]]
