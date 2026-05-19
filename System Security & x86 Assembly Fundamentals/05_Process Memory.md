# 05 — Process Memory (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 5/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_Process Memory.txt](05_Process Memory.txt) · [05_Process Memory.srt](05_Process Memory.srt)

## Concetti chiave

- I moderni OS usano la **virtual memory**: ogni processo vede un proprio spazio di indirizzi virtuale **contiguo**, da `0x00000000` fino al limite max addressable.
- La memoria di processo è suddivisa in **segmenti** ben definiti: **text/code, data, BSS, heap, stack**.
- **Text/code** = istruzioni del programma, **read-only**.
- **Data** = variabili globali/statiche **inizializzate**.
- **BSS** = variabili globali/statiche **non inizializzate** (azzerate al runtime).
- **Heap** = memoria allocata dinamicamente (`malloc`, `realloc`, `free`); **cresce verso l'alto** (verso indirizzi maggiori).
- **Stack** = function frames, parametri, variabili locali, return addresses; **cresce verso il basso** (verso indirizzi minori).

## Spiegazione approfondita

### Memoria virtuale (concetto)
Ogni processo "crede" di avere a disposizione tutta la RAM, partendo da indirizzo 0 fino all'indirizzo massimo addressabile (su x86: ~4 GB virtuali). L'OS+MMU si occupano della mappatura virtuale→fisica trasparentemente.

### Layout di una process memory (x86 Linux)

```
HIGH addresses (es. 0xFFFFFFFF)
+--------------------------+
|         STACK            |  ← cresce verso il BASSO
|           ↓              |     (push fa decrescere ESP)
+--------------------------+
|         (free)           |
+--------------------------+
|           ↑              |
|         HEAP             |  ← cresce verso l'ALTO
+--------------------------+     (malloc/sbrk)
|         BSS              |     (uninitialized data, zeroed)
+--------------------------+
|         DATA             |     (initialized data: globals/statics)
+--------------------------+
|       TEXT / CODE        |     (read-only, instructions)
+--------------------------+
LOW addresses (0x00000000)
```

### Dettaglio dei segmenti

| Segmento | Contenuto | Permessi tipici | Note |
|---|---|---|---|
| **Text / Code** | Istruzioni macchina del programma | **R-X** (read+execute) | Read-only: non deve cambiare durante l'esecuzione |
| **Data** | Variabili globali/statiche **inizializzate** (es. `int g = 5;`) | **RW-** | Modificabile |
| **BSS** | Variabili globali/statiche **non inizializzate** (es. `static int t;`) | **RW-** | Azzerate al load time. Nome storico = "Block Started by Symbol" |
| **Heap** | Allocazioni dinamiche | **RW-** | Cresce verso indirizzi **alti** via `brk`/`sbrk` (`malloc`, `realloc`, `free`) |
| **Stack** | Stack frames di funzioni, parametri, variabili locali, return address | **RW-** | Cresce verso indirizzi **bassi**. È **la regione cruciale per i buffer overflow** |

### Direzione di crescita (chiave per i BO)
- **Heap**: low → high.
- **Stack**: **high → low**. È contro-intuitivo e cruciale.
- Heap e stack possono potenzialmente "collidere" nel mezzo (storicamente significativo, oggi mitigato da ASLR e guard pages).

### Perché esiste questa suddivisione
Motivi storici + ottimizzazione:
- Permette permessi diversi (text read-only impedisce code injection nelle aree dati senza bypass).
- Separa dati statici/dinamici/runtime per gestione memoria efficiente.
- Consente al loader/OS di mappare velocemente le sezioni del binario ELF/PE.

## Comandi & strumenti

Nessun comando in questo video. Strumenti utili per ispezionare segmenti:
- **`/proc/<pid>/maps`** su Linux — mostra il layout reale di un processo.
- **`readelf -S <binary>`** — sezioni di un ELF.
- **`gdb`** — `info proc mappings`, `maintenance info sections`.

## Esempi pratici

```c
// Esempio C per visualizzare dove vanno le variabili
int   g_init = 42;        // → DATA  (initialized global)
int   g_uninit;           // → BSS   (uninitialized global)
static int s_local = 7;   // → DATA
int main(void) {
    int local = 5;        // → STACK (variabile locale del frame di main)
    int *p = malloc(16);  // p è su STACK, ma punta a memoria sull'HEAP
    return 0;
}
```

## Punti d'attenzione per l'esame eCPPT

- **Memorizza il diagramma di layout** — l'ordine top-to-bottom: **STACK ↓ … HEAP ↑ BSS DATA TEXT**.
- **Stack cresce verso indirizzi BASSI** — domanda classica, controintuitiva. `push` → ESP diminuisce. `pop` → ESP aumenta.
- **Heap cresce verso indirizzi ALTI**.
- **Text/Code è read-only** → spiega perché certe exploit techniques richiedono di scrivere shellcode su stack/heap (sezioni RW).
- **DATA vs BSS**: differenza basata su initialized vs uninitialized (BSS azzerato al load).
- Il segmento da **conoscere a fondo per l'esame** è lo **stack** (vedi video 06-07).
- La **virtual memory** è ciò che permette ogni processo di avere indirizzi che partono da 0 — niente conflitti tra processi.

## Collegamenti con altri video

- Precedente: [[04_Registers]] (ESP/EBP gestiscono lo stack)
- Prossimo: [[06_Understanding the Stack]] — deep dive nello stack
- Stack frames di funzione: [[07_Stack Frames]]
- BSS in pratica: [[012_Data Types & Variables]] (direttiva `RES*` in NASM)
