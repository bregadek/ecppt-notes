# 04 — Registers (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 4/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [04_Registers.txt](04_Registers.txt) · [04_Registers.srt](04_Registers.srt)

## Concetti chiave

- **Registers** = piccole locazioni di memoria ad alta velocità **dentro la CPU**, temporanee (volatile), usate per dati in elaborazione.
- L'**architettura del CPU (32/64 bit)** indica la **larghezza dei registri** (32 bit → EAX 32 bit, 64 bit → RAX 64 bit).
- I **General Purpose Registers (GPR)** sono il focus del corso: **EAX, EBX, ECX, EDX, ESI, EDI, ESP, EBP**.
- Naming convention per dimensione: **8-bit (AL/AH)** · **16-bit (AX)** · **32-bit (EAX)** · **64-bit (RAX)**.
- **EIP** = **Instruction Pointer** — punta all'indirizzo della prossima istruzione da eseguire. **Bersaglio numero 1 di un buffer overflow.**

## Spiegazione approfondita

### Tabella riassuntiva dei General Purpose Registers (x86)

| x86 | Nome esteso | Scopo principale |
|---|---|---|
| **EAX** | Accumulator | Operazioni aritmetiche, **valore di ritorno** delle funzioni |
| **EBX** | Base | Puntatore a dati / base address |
| **ECX** | Counter | Contatore in loop e shift/rotate |
| **EDX** | Data | Aritmetica (assieme a EAX), I/O |
| **ESI** | Source Index | Puntatore alla **sorgente** in string ops |
| **EDI** | Destination Index | Puntatore alla **destinazione** in string ops |
| **ESP** | Stack Pointer | Punta al **top dello stack** |
| **EBP** | Base Pointer | Punta alla **base dello stack frame** corrente |

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

**Regola mnemonica**:
- Prefisso **R** = 64-bit (RAX).
- Prefisso **E** = 32-bit Extended (EAX).
- Senza prefisso = 16-bit (AX).
- Suffisso **H/L** = byte High/Low del 16-bit (AH/AL, sub-parti di AX).

Il "salto" da 32 a 64 bit è solo prefisso `E → R`: imparando bene x86 si è già al 80-90% di x64.

### EIP — Instruction Pointer (separato dai GPR)
- Contiene **l'indirizzo della prossima istruzione** in machine code che la CPU eseguirà.
- La CPU **non scrive arbitrariamente** in EIP — viene aggiornato dalle istruzioni di control flow (`jmp`, `call`, `ret`).
- **Importanza per gli exploit**: se un attaccante riesce a sovrascrivere EIP (es. via stack overflow), può **deviare il flusso di esecuzione** verso shellcode o gadget. È la base concettuale dei buffer overflow.

### Categorie dei registri (focus del corso)
- **General purpose** → EAX/EBX/ECX/EDX (data manipulation, arithmetic).
- **Index** → ESI/EDI (string ops).
- **Stack-related** → **ESP** (top stack), **EBP** (base frame).
- **Instruction** → **EIP** (next instruction).
- **EFLAGS** (citato implicitamente): flag di stato della CPU (zero, carry, sign, overflow, ecc.).

## Comandi & strumenti

Nessun comando — solo teoria. I registri li manipoleremo via assembly nei video 011-012.

## Esempi pratici

Esempi di uso "tipico" (concettuali):
```asm
mov eax, 4          ; assegna 4 a EAX (numero syscall sys_write su Linux x86)
mov ecx, msg        ; ECX = puntatore alla stringa (source)
push ebx            ; salva EBX sullo stack (modifica ESP)
pop  ebx            ; ripristina EBX dallo stack
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza tutti gli 8 GPR x86** e il loro scopo. Domanda classica: "Quale registro contiene il valore di ritorno di una funzione?" → **EAX**.
- **ESP vs EBP**:
  - **ESP** = top dello stack, cambia con ogni push/pop.
  - **EBP** = base dello stack frame corrente, **fisso** durante l'esecuzione della funzione → usato come riferimento per accedere a parametri e variabili locali.
- **EIP è il target principale dei buffer overflow** — sovrascriverlo permette di redirezionare l'esecuzione.
- **Prefisso E (32-bit) vs R (64-bit)** — domanda ricorrente. AL/AH sono i byte basso/alto di AX (16-bit), che è la metà bassa di EAX (32-bit), che è la metà bassa di RAX (64-bit).
- **ESI source / EDI destination** in string ops: collegato a istruzioni come `movsb`, `rep movsb` (utili in shellcoding).
- **ECX = counter** → usato in `loop` e con `rep` prefix.

## Collegamenti con altri video

- Precedente: [[03_CPU Architecture]]
- Prossimo: [[05_Process Memory]] — vediamo dove vivono i dati che i registri puntano.
- Stack & ESP/EBP in azione: [[06_Understanding the Stack]] · [[07_Stack Frames]]
- Registri usati negli esempi: [[011_Hello World in Assembly]] · [[012_Data Types & Variables]]
