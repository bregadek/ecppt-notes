# 01 — Course Introduction (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 1/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Il corso **System Security & x86 Assembly Fundamentals** è il **prerequisito diretto** del successivo corso **Exploit Development** (buffer overflow, fuzzing, shellcoding) nel learning path eCPPT.
- Obiettivo: fornire le fondamenta di **architettura CPU**, **registri**, **memoria di processo**, **stack/stack frame**, **assemblers/compilers** e **assembly x86 (IA32) su Linux**.
- Approccio dal basso (machine code → assembly → C) per capire **da dove nascono le memory-based vulnerabilities** e come si possano sfruttare al livello più basso.
- Focus pratico su **32-bit / x86 / Linux** con assembler **NASM**.
- Prerequisiti dichiarati: nozioni base di computer architecture, basi di C/C++, dimestichezza con Linux/CLI. **Nessuna esperienza pregressa di assembly richiesta.**

## Spiegazione approfondita

### Topic overview del corso
1. **Architecture Fundamentals** — CPU architecture, componenti del CPU, CPU registers (general purpose).
2. **Process Memory & Stack** — come i programmi vengono caricati in memoria, come funziona lo stack, come i registri interagiscono con esso (push/pop), stack frames.
3. **Assembly (IA32 / x86 su Linux)** — introduzione all'assembly, relazione con i linguaggi high level (C/C++), processo di compilazione/assemblaggio/linking.
4. **x86 Assembly Programming** — primi programmi in NASM (Hello World, data types & variables) per consolidare l'interazione tra registri e memoria.

### Perché è importante per il pentester
Anche per un pentester "classico" (network, AD) capire l'assembly:
- Apre la porta a **reverse engineering**, **binary exploitation**, **malware analysis**.
- È **indispensabile** per capire i **buffer overflow** (oggetto del corso Exploit Development).
- Mostra **perché** nascono certe vulnerabilità (es. corruzione dello stack) e **come** sfruttarle a livello più basso.

### Prerequisiti
- Nozioni di **computer architecture** (CPU, RAM, …).
- **C/C++** base (funzioni, OOP, scrivere un programma semplice).
- **Linux**: terminale, file manipulation, processi.
- Assembly: **non richiesto** (si parte da zero).

### Learning objectives (verificati nel video 013)
1. **Computer architecture fundamentals** — CPU, registri, memoria.
2. **IA32 / x86 CPU architecture** — registri, instruction set, execution pipeline.
3. **Memory organization & process memory** — code, data, BSS, heap, stack.
4. **Stack & stack frames** — ruolo nelle function call e nelle local variable.
5. **Introduzione all'assembly IA32** — distinzione high-level vs low-level, flusso di compilazione.
6. **IA32 assembly basics** — istruzioni di data movement, aritmetica/logica, addressing modes.

## Comandi & strumenti

Video introduttivo, **nessun comando**. Strumenti che verranno usati:

| Strumento | Categoria | Scopo |
|---|---|---|
| **NASM** (Netwide Assembler) | Assembler | Scrivere/assemblare codice x86 su Linux |
| **ld** | Linker | Linkare l'object file e creare l'ELF eseguibile |
| **gcc / build-essential** | Toolchain C | Compilare C e supporto generale |
| **Ubuntu 16.04 LTS 32-bit** | Lab OS | Ambiente didattico consigliato dal corso |
| **GDB** | Debugger | Ispezionare registri/memoria a runtime |

## Esempi pratici

N/A — video introduttivo. I primi esempi pratici partono dal video **011 — Hello World in Assembly**.

## Punti d'attenzione per l'esame eCPPT

- L'esame eCPPT (45 domande, ambiente pratico) non chiede di **scrivere** assembly avanzato, ma chiede di **riconoscere** strutture base (registri, prologue/epilogue, segmenti di memoria, push/pop) — fondamentale per BO/RE.
- Memorizza la **catena prerequisiti**: System Security → Exploit Development → BO.
- Sapere distinguere **x86 (32-bit) vs x64 (64-bit)** e relativi nomi dei registri (`E*` vs `R*`) è una domanda ricorrente.
- Il focus didattico del corso è **IA32 / x86 su Linux con NASM** — è questo l'ambiente da padroneggiare per l'esame.

## Collegamenti con altri video

- Prossimo: [[02_Introduction to System Security]]
- CPU & registers: [[03_CPU Architecture]] · [[04_Registers]]
- Memoria & stack: [[05_Process Memory]] · [[06_Understanding the Stack]] · [[07_Stack Frames]]
- Assembly: [[08_Assemblers & Compilers]] · [[09_Introduction to Assembly]]
- Lab & programmazione: [[010_Setting Up Our Lab]] · [[011_Hello World in Assembly]] · [[012_Data Types & Variables]]
- Conclusione (verifica learning objectives): [[013_Course Conclusion]]
