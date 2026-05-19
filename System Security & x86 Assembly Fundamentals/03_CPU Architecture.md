# 03 — CPU Architecture (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 3/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_CPU Architecture.txt](03_CPU Architecture.txt) · [03_CPU Architecture.srt](03_CPU Architecture.srt)

## Concetti chiave

- La **CPU** (Central Processing Unit) è il "cervello" del computer: esegue istruzioni e calcoli sul **machine code** di un programma.
- **Machine code** = set di istruzioni che il CPU processa, rappresentate in **hex**; illeggibile/scrivibile manualmente per l'uomo.
- **Assembly language (ASM)** è un linguaggio **mnemonico low-level**: traduzione 1:1 (quasi) del machine code, leggibile per l'umano.
- Ogni CPU ha la propria **Instruction Set Architecture (ISA)** — quindi anche il proprio dialetto assembly: x86/x64 per Intel/AMD, ARM per ARM-based (es. Apple Silicon M1/M2).
- **x86** = 32-bit · **x64** (aka **x86_64**, **AMD64**) = 64-bit.
- Componenti chiave della CPU: **Control Unit (CU)**, **Arithmetic Logic Unit (ALU)**, **Registers**.

## Spiegazione approfondita

### Cosa fa la CPU
1. Riceve **machine code** (istruzioni in hex).
2. Lo **decodifica** ed **esegue** (move data tra registri, operazioni aritmetiche/logiche, accesso a memoria, controllo del flusso).
3. Comunica con RAM, secondary memory, I/O devices.

### Machine code vs Assembly
| Livello | Esempio | Note |
|---|---|---|
| Machine code | `B8 04 00 00 00` | Hex, eseguibile direttamente dalla CPU |
| Assembly | `mov eax, 4` | Mnemonic, leggibile, mappato quasi 1:1 al machine code |
| C / C++ | `int x = 4;` | High-level, richiede compilazione |

### Componenti del CPU
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

- **Control Unit (CU)**: fetch-decode-execute, coordina movimento dati e flusso di controllo.
- **ALU (Arithmetic Logic Unit)**: esegue operazioni aritmetiche (`add`, `sub`, `mul`, `div`) e logiche (`and`, `or`, `not`, `xor`).
- **Registers**: piccola memoria velocissima **dentro** la CPU, temporanea (volatile).

### Tipi di registri (panoramica)
- **Program Counter (PC)** — memoria del prossimo indirizzo da fetchare.
- **Instruction Register (IR)** — istruzione attualmente in esecuzione.
- **Accumulator** — risultato di operazioni aritmetiche/logiche.
- **General Purpose Registers (GPR)** — valori intermedi e operandi (è la categoria su cui ci concentreremo: EAX, EBX, ECX, EDX, ESI, EDI, ESP, EBP).

### ISA (Instruction Set Architecture)
- Insieme di istruzioni che programmatore/compilatore deve conoscere per scrivere codice per quel CPU.
- Include: memoria addressabile, registri, istruzioni disponibili.
- L'**ISA più diffusa è x86**, derivata dall'Intel **8086**.
- Acronimi:
  - **x86** → 32-bit
  - **x64** / **x86_64** / **AMD64** → 64-bit
  - **IA32** → Intel Architecture 32-bit (= x86)
  - **IA-32e** / **Intel 64** → 64-bit Intel

### CISC vs RISC (contesto)
- **x86/x64 = CISC** (Complex Instruction Set Computing): istruzioni complesse, lunghezza variabile.
- **ARM = RISC** (Reduced Instruction Set Computing): istruzioni semplici, lunghezza fissa, più efficiente energeticamente (Apple M1/M2, mobile, embedded).

## Comandi & strumenti

Nessun comando — video puramente teorico.

## Esempi pratici

Mini-esempio di assembly mostrato dall'istruttore (non eseguito):
```asm
mov ebx, <value>   ; muove un valore nel registro EBX
```
Funziona da introduzione alla notazione mnemonic dell'assembly.

## Punti d'attenzione per l'esame eCPPT

- **Distinzione x86 vs x64** — domanda quasi garantita. Ricorda: i registri x86 iniziano con **E** (EAX), quelli x64 con **R** (RAX). Le dimensioni dei registri = "bittezza" del CPU.
- **ISA** = set di istruzioni del CPU; un binario compilato per x86 non gira nativamente su ARM.
- I **3 componenti chiave** del CPU: **CU, ALU, Registers** — memorizzali, è teoria di base ricorrente.
- I registri sono **volatile** (come RAM, perdono i dati senza alimentazione).
- **Apple Silicon (M1/M2) = ARM**, NON x86 → non si può eseguire codice x86 nativo senza emulazione (Rosetta).
- Termine **mnemonic** = parola chiave: assembly è "mnemonic code".

## Collegamenti con altri video

- Precedente: [[02_Introduction to System Security]]
- Prossimo: [[04_Registers]] — approfondimento dei registri generali.
- Memoria: [[05_Process Memory]]
- ISA / assembly correlati: [[09_Introduction to Assembly]] · [[08_Assemblers & Compilers]]
