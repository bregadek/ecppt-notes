# 013 — Course Conclusion (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 13/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [013_Course Conclusion.txt](013_Course Conclusion.txt) · [013_Course Conclusion.srt](013_Course Conclusion.srt)

## Concetti chiave

- Video conclusivo: ripasso e **verifica dei learning objectives** dichiarati nel video 01.
- Tutti i 6 obiettivi del corso sono stati coperti: **architettura · registri · process memory · stack/stack frames · assembly basics · assembly programming**.
- Il corso era pensato come **prerequisito** del corso **Exploit Development** (buffer overflow), e l'obiettivo è dare le basi per identificare e sfruttare vulnerabilità memory-based.

## Spiegazione approfondita

### Verifica dei 6 learning objectives

#### 1. Computer architecture fundamentals
- **Coperto** in: [[03_CPU Architecture]], [[04_Registers]], [[05_Process Memory]].
- Si è spiegato cos'è una CPU, i suoi componenti (CU, ALU, Registers), il ruolo della memoria.

#### 2. IA32 / x86 CPU architecture
- **Coperto** in: [[03_CPU Architecture]], [[04_Registers]].
- Si sono visti registri x86 (E*), naming convention 8/16/32/64-bit, ISA, EIP, execution pipeline (anche via process memory).

#### 3. Memory organization & process memory
- **Coperto** in: [[05_Process Memory]], [[06_Understanding the Stack]], [[07_Stack Frames]].
- Si sono esplorati i segmenti **text, data, BSS, heap, stack** e il loro ruolo nell'esecuzione.

#### 4. Understanding stack and stack frames
- **Coperto** in: [[06_Understanding the Stack]] (LIFO, push/pop, direzione di crescita) e [[07_Stack Frames]] (frame, prologue/epilogue, return address).

#### 5. Introduction to IA32 assembly language
- **Coperto** in: [[08_Assemblers & Compilers]], [[09_Introduction to Assembly]].
- Differenza high-level vs low-level, pipeline di compilazione, assembler vs linker, sintassi Intel vs AT&T.

#### 6. IA32 assembly basics (data movement, arithmetic, addressing)
- **Coperto** in: [[010_Setting Up Our Lab]], [[011_Hello World in Assembly]], [[012_Data Types & Variables]].
- Hello World con syscall Linux, sezioni `.data`/`.bss`/`.text`, direttive `db/dw/dd/dq` e `resb/resw/resd/resq`, idioma `xor reg, reg`, debug con GDB.

### Cosa segue
Il corso successivo nel learning path eCPPT è **Exploit Development**, che parte direttamente con i **buffer overflow** assumendo come prerequisiti tutti gli argomenti di questo corso.

## Comandi & strumenti

Nessun comando — video di chiusura.

## Esempi pratici

N/A.

## Punti d'attenzione per l'esame eCPPT

- Usa questo video come **checklist di ripasso** prima dell'esame: per ogni learning objective verifica di saper rispondere a una domanda concettuale e identificare la struttura in un disassembly elementare.
- Concetti **must-know** per la sezione System Security dell'esame:
  - Distinzione **x86 vs x64**, naming registri.
  - **8 GPR x86** e relativo scopo (EAX, EBX, ECX, EDX, ESI, EDI, ESP, EBP) + **EIP**.
  - **Layout process memory**: text/data/BSS/heap/stack con direzioni di crescita.
  - **LIFO**, push/pop, ESP/EBP, prologue/epilogue.
  - **Return address sullo stack** → bersaglio del buffer overflow.
  - Pipeline **C → executable** (preprocessor → compiler → assembler → linker → loader).
  - Syscall Linux x86 base: `sys_write (4)`, `sys_exit (1)`, `int 0x80`.
- Le competenze qui coperte sono la base per la successiva valutazione su **Exploit Development / BO** durante l'esame.

## Collegamenti con altri video

- Inizio corso: [[01_Course Introduction]] · [[02_Introduction to System Security]]
- Sezione architettura: [[03_CPU Architecture]] · [[04_Registers]]
- Memoria: [[05_Process Memory]] · [[06_Understanding the Stack]] · [[07_Stack Frames]]
- Assembly: [[08_Assemblers & Compilers]] · [[09_Introduction to Assembly]]
- Pratica: [[010_Setting Up Our Lab]] · [[011_Hello World in Assembly]] · [[012_Data Types & Variables]]
- **Prossimo modulo del learning path**: Exploit Development (buffer overflow, fuzzing, shellcoding).
