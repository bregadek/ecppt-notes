# 07 — Stack Frames (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 7/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_Stack Frames.txt](07_Stack Frames.txt) · [07_Stack Frames.srt](07_Stack Frames.srt)

## Concetti chiave

- Uno **stack frame** (aka **activation record** / **call frame**) è la struttura dati che il CPU/OS usa per gestire una **singola chiamata di funzione**.
- Contiene: **parametri**, **local variables**, **return address**, **saved EBP**, eventuali registri salvati.
- Ogni funzione che parte spinge il proprio frame sullo stack; ogni `return` lo poppa.
- Due fasi cruciali per ogni funzione: **prologue** (prepara il frame) e **epilogue** (lo distrugge ripristinando lo stato).
- L'**EIP** viene salvato per consentire il ritorno al punto giusto del chiamante quando la funzione termina.

## Spiegazione approfondita

### Prologue & Epilogue (analogia bookmark)
- **Prologue** = mettere un segnalibro nel libro **prima** di leggere un capitolo (= salvare lo stato corrente).
- **Epilogue** = usare il segnalibro per **ritornare** al punto esatto da cui si era partiti (= ripristinare lo stato).

Prologue tipico in assembly x86:
```asm
push ebp           ; salva EBP del chiamante
mov  ebp, esp      ; nuovo EBP = ESP corrente (base del nuovo frame)
sub  esp, N        ; alloca spazio per variabili locali (N byte)
```

Epilogue tipico:
```asm
mov  esp, ebp      ; libera variabili locali
pop  ebp           ; ripristina EBP del chiamante
ret                ; pop dell'indirizzo di ritorno in EIP
```

### Cosa contiene uno stack frame (layout x86)
```
HIGH addresses
+---------------------------+
|       arg N               |   ← parametri pushati dal CALLER (in ordine inverso, cdecl)
|       ...                 |
|       arg 1               |
+---------------------------+
|   return address (EIP)    |   ← salvato automaticamente da `call`
+---------------------------+
|   saved EBP (caller)      |   ← salvato dal prologo
+---------------------------+ ← EBP (frame pointer della funzione corrente)
|   local var 1             |
|   local var 2             |
|   ...                     |
+---------------------------+ ← ESP (top dello stack)
LOW addresses
```
- **EBP** è il **riferimento fisso**: parametri = `[ebp+8]`, `[ebp+12]`, … · local vars = `[ebp-4]`, `[ebp-8]`, …
- **ESP** si muove ad ogni push/pop.

### Flow di esecuzione (esempio del video)
Codice C:
```c
int b() { return 0; }
int a() { b(); return 0; }
int main() { a(); return 0; }
```

#### Step 1 — Entry point: `main`
```
+--------------+
| frame main   |  ← ESP
+--------------+
```

#### Step 2 — `main` chiama `a()`
```
+--------------+
| frame main   |
+--------------+
| frame a      |  ← ESP
+--------------+
```

#### Step 3 — `a` chiama `b()`
```
+--------------+
| frame main   |
+--------------+
| frame a      |
+--------------+
| frame b      |  ← ESP
+--------------+
```

#### Step 4 — `b` ritorna (epilogue) → `a` riprende
```
+--------------+
| frame main   |
+--------------+
| frame a      |  ← ESP (frame b è stato poppato)
+--------------+
```

#### Step 5 — `a` ritorna → torna a `main`
```
+--------------+
| frame main   |  ← ESP
+--------------+
```

### Cosa fa `call` e `ret`
- `call <addr>`: **pusha l'EIP corrente** (= indirizzo dell'istruzione successiva) sullo stack come return address, poi salta a `<addr>`.
- `ret`: **poppa il valore in cima allo stack dentro EIP** → il flusso torna al chiamante.

Se l'attaccante riesce a **sovrascrivere il return address** sullo stack (via buffer overflow), `ret` salterà dove vuole l'attaccante → **redirect dell'esecuzione**.

## Comandi & strumenti

Istruzioni assembly chiave per stack frame:

| Istruzione | Ruolo |
|---|---|
| `push ebp` | Salva il frame pointer del chiamante |
| `mov ebp, esp` | Nuovo frame pointer = ESP corrente |
| `sub esp, N` | Alloca N byte per variabili locali |
| `call <fn>` | Push return address + jmp |
| `leave` | Equivalente a `mov esp, ebp; pop ebp` |
| `ret` | Pop in EIP |

## Esempi pratici

Prologue/Epilogue completo di una funzione che alloca 16 byte di locals:
```asm
my_func:
    push ebp
    mov  ebp, esp
    sub  esp, 16        ; 16 byte di local vars

    ; ... corpo funzione ...
    mov  eax, [ebp+8]   ; primo parametro
    mov  [ebp-4], eax   ; prima local var

    mov  esp, ebp       ; libera locals
    pop  ebp            ; ripristina EBP chiamante
    ret                 ; torna al caller
```

## Punti d'attenzione per l'esame eCPPT

- **Stack frame contiene 4 cose chiave**: **arguments · saved EIP (return address) · saved EBP · local variables**. Memorizza l'ordine sullo stack.
- **EBP è il frame pointer fisso**, **ESP il top mobile**. Tutti gli accessi nella funzione si fanno via `[ebp+offset]`.
- **Return address è l'EIP salvato dalla `call`** → bersaglio dei buffer overflow (es. "smashing the stack").
- **Prologue/Epilogue**: domanda concettuale ricorrente.
- Quando `ret` viene eseguita, **poppa il top dello stack in EIP**. Se hai sovrascritto quel valore con un BO, controlli EIP.
- Differenza **stack vs stack frame**:
  - Stack = la regione di memoria intera (LIFO).
  - Stack frame = un singolo "slice" relativo a UNA chiamata di funzione.
- Ricorda l'**execution flow**: main → a → b → ret (b) → ret (a) → ret (main). Domanda di tipo "in che ordine vengono distrutti i frame?"

## Collegamenti con altri video

- Precedente: [[06_Understanding the Stack]]
- Prossimo: [[08_Assemblers & Compilers]] — passaggio alla parte assembly
- Registri ESP/EBP: [[04_Registers]]
- Buffer overflow (corso successivo): collegato direttamente — la sovrascrittura del return address è qui.
