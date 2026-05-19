# 06 — Understanding the Stack (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 6/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_Understanding the Stack.txt](06_Understanding the Stack.txt) · [06_Understanding the Stack.srt](06_Understanding the Stack.srt)

## Concetti chiave

- Lo **stack** è una struttura dati **LIFO** (Last In, First Out) — analogia: pila di libri, l'ultimo messo è il primo tolto.
- È un'area di memoria che contiene **function call frames, parametri di funzione, variabili locali, return addresses**.
- È gestito dal registro **ESP (Stack Pointer)**, che punta sempre al **top dello stack**.
- Due operazioni fondamentali: **PUSH** (aggiunge in cima) e **POP** (rimuove dalla cima).
- **Lo stack cresce verso indirizzi BASSI di memoria** (controintuitivo!):
  - `PUSH` → ESP -= 4 (su x86) o -= 8 (su x64) → poi scrive il valore.
  - `POP`  → legge il valore puntato da ESP → poi ESP += 4 (x86) o += 8 (x64).
- Lo stack è cruciale per i **buffer overflow** (stack overflow).

## Spiegazione approfondita

### LIFO — Last In, First Out
Pila di libri: l'ultimo libro messo in cima è il primo che togli. Lo stesso vale per la memoria: l'ultimo valore "pushato" è il primo "poppato".

### ESP — Stack Pointer
- **ESP** (x86) / **RSP** (x64) punta **al top dello stack** = all'ultimo elemento inserito.
- Ogni `PUSH` e `POP` aggiorna ESP automaticamente.

### Perché lo stack cresce verso il basso
Motivi storici: nei vecchi PC la memoria era limitata e divisa tra heap e stack. Per massimizzare l'uso si decise:
- **Heap**: parte da indirizzi bassi, cresce verso l'**alto**.
- **Stack**: parte da indirizzi alti, cresce verso il **basso**.
Così entrambi convivono nello stesso spazio senza collisioni immediate.

### Operazioni PUSH e POP — meccanica

#### PUSH `<valore>`
1. **Decrementa ESP** di 4 (x86) o 8 (x64).
2. **Scrive** il valore all'indirizzo di memoria puntato da ESP.

```
Prima di PUSH 1:                Dopo PUSH 1:
ESP → 0x0028FF14 [data ]        ESP → 0x0028FF10 [  1   ]   ← nuovo top
       0x0028FF18 [ ... ]              0x0028FF14 [data  ]
                                       0x0028FF18 [ ... ]
```
ESP è passato da `0x0028FF14` a `0x0028FF10` (–4 byte → indirizzo più basso).

#### POP `<reg>`
1. **Legge** il valore all'indirizzo puntato da ESP e lo copia nel registro.
2. **Incrementa ESP** di 4 (x86) o 8 (x64).

```
Prima di POP EAX:               Dopo POP EAX:
ESP → 0x0028FF10 [  1   ]        ESP → 0x0028FF14 [data ]   ← nuovo top
       0x0028FF14 [data ]              0x0028FF18 [ ... ]
       0x0028FF18 [ ... ]
EAX = ?                          EAX = 1
```

### Esempio numerico (dal video)
- ESP inizialmente punta a `0x0028FF14` = **2'686'848** in decimale.
- Si esegue `PUSH 1`.
- ESP diventa `0x0028FF10` = **2'686'844** (= 2'686'848 − 4). Su x64 sarebbe −8.
- Al top dello stack ora c'è il valore `1`.

### Visualizzazione: stack con ABCDE
```
HIGH addresses
  ┌─────────┐
  │    D    │  0x... (più basso a salire)
  │    C    │
  │    B    │
  │    A    │
  ├─────────┤  ← ESP iniziale (top)
  │         │
  ↓ cresce verso il basso

Dopo PUSH E:
  ┌─────────┐
  │    D    │
  │    C    │
  │    B    │
  │    A    │
  │    E    │  ← nuovo top, ESP = (ESP_prec − 4)
  └─────────┘
```

### Casi d'uso reali dello stack
- **Function calls**: parametri pushati prima della `call`, return address salvato automaticamente.
- **Local variables**: allocate sullo stack frame della funzione.
- **Salvataggio registri** (callee/caller saved).
- **Context switching** (a basso livello dal kernel).

## Comandi & strumenti

Istruzioni assembly trattate (le useremo in NASM nei video 011-012):

| Istruzione | Effetto su ESP | Esempio |
|---|---|---|
| `push <op>` | `ESP -= 4` poi `[ESP] = op` | `push eax`, `push 0x42` |
| `pop  <reg>` | `reg = [ESP]` poi `ESP += 4` | `pop ebx` |
| `call <addr>` | Pusha return address poi salta | `call func` |
| `ret` | Poppa l'indirizzo in EIP | (epilogue di funzione) |

## Esempi pratici

```asm
; Esempio concettuale di push/pop
mov  eax, 0x41        ; EAX = 0x41
push eax              ; stack: [0x41]    ESP -= 4
push 0x42             ; stack: [0x42][0x41]  ESP -= 4

pop  ebx              ; EBX = 0x42       ESP += 4
pop  ecx              ; ECX = 0x41       ESP += 4
```

## Punti d'attenzione per l'esame eCPPT

- **LIFO** = parola chiave: l'ultimo inserito è il primo estratto.
- **PUSH decrementa ESP**, **POP incrementa ESP** — domanda frequente e controintuitiva (lo stack "sale" verso indirizzi più bassi).
- Su **x86 push/pop muovono ESP di 4 byte**, su **x64 di 8 byte**.
- ESP punta sempre al **top dello stack** = ultimo elemento inserito = indirizzo **più basso** dello stack popolato.
- Stack contiene: **return address, parametri, variabili locali, saved registers** → è esattamente ciò che un BO può corrompere.
- Una **stack overflow** scrive oltre il buffer locale, sovrascrive il **saved EBP** e il **return address (saved EIP)** → controllo del flusso.
- Differenza con la **heap**: heap cresce **verso l'alto**, allocato dinamicamente via `malloc`.

## Collegamenti con altri video

- Precedente: [[05_Process Memory]] (dove si colloca lo stack nel layout)
- Prossimo: [[07_Stack Frames]] — come le funzioni usano lo stack
- Registri rilevanti: [[04_Registers]] (ESP, EBP)
- Push/pop in azione: [[011_Hello World in Assembly]] · [[012_Data Types & Variables]]
