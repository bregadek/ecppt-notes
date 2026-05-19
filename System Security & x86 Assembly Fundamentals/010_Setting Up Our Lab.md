# 010 — Setting Up Our Lab (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 10/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [010_Setting Up Our Lab.txt](010_Setting Up Our Lab.txt) · [010_Setting Up Our Lab.srt](010_Setting Up Our Lab.srt)

## Concetti chiave

- Lab consigliato per IA32 assembly su Linux: **Ubuntu 16.04.7 LTS Desktop 32-bit** in VirtualBox.
- Motivo della scelta del 32-bit: evitare problemi di compatibilità con NASM quando si scrive **x86 / IA32 assembly puro**.
- Tool da installare: **`nasm`** (assembler) + **`build-essential`** (toolchain di compilazione Ubuntu).
- Limite RAM per OS 32-bit: max **4 GB** addressabili.
- Editor a scelta: **vim** (consigliato dall'istruttore, con line numbers + syntax highlighting), `nano`, o `gedit`.

## Spiegazione approfondita

### Perché Ubuntu 16.04 32-bit
- **LTS** (Long Term Support) → stabile.
- L'istruttore lo usa da anni per insegnare assembly senza problemi noti.
- Le versioni 64-bit recenti richiedono il **compat layer** per NASM 32-bit e possono dare errori.
- È un environment "predicibile" per gli esercizi del corso.

### Step di setup

1. **VirtualBox + Ubuntu 16.04 32-bit Desktop** (~1 GB ISO).
2. Installazione standard come VM.
3. RAM ≤ 4 GB (limite OS 32-bit).
4. Installare **VirtualBox Guest Additions** per:
   - Auto-scaling risoluzione,
   - Drag & drop,
   - Shared clipboard.
5. Aggiornare i pacchetti e installare il toolchain.

### Tool da installare
- **`nasm`** — Netwide Assembler (l'assembler che useremo).
- **`build-essential`** — meta-pacchetto Ubuntu con `gcc`, `make`, header C, ecc. Utile in generale.

### Configurazione vim consigliata
File `~/.vimrc`:
```vim
set number       " mostra numeri di riga
syntax on        " syntax highlighting
```
I numeri di riga sono utili soprattutto seguendo gli esercizi assembly riga per riga.

### Verifica dell'architettura
Output di `lscpu` (esempio dell'istruttore):
- `Architecture: i686` ← 32-bit
- `CPU op-mode(s): 32-bit`
- 2 CPU virtuali, ~2 GB RAM allocati.

## Comandi & strumenti

```bash
# Aggiornamento pacchetti
sudo apt-get update

# Installazione NASM + build essentials
sudo apt-get install nasm build-essential

# Verifica installazione
nasm --version
man nasm

# Verifica architettura del sistema
lscpu
```

Editor:
```bash
# vim consigliato
vim ~/.vimrc
# aggiungere: set number / syntax on

# alternative
nano hello.asm
gedit hello.asm   # GUI default su Ubuntu
```

## Esempi pratici

Verifica end-to-end che il lab è pronto:
```bash
# 1. NASM presente
which nasm
nasm -v

# 2. ld (linker) presente
which ld

# 3. Architettura 32-bit
uname -m              # atteso: i686 o i386
```

## Punti d'attenzione per l'esame eCPPT

- **Ambiente di riferimento**: Ubuntu 32-bit + NASM + ld. Domande pratiche sull'esame possono basarsi su questo setup.
- **`build-essential`** = pacchetto da ricordare per Ubuntu (analogo a `Development Tools` group su Red Hat).
- **OS 32-bit max 4 GB RAM** = limite hardware/teorico noto.
- Su una distribuzione **64-bit** è comunque possibile assemblare codice 32-bit con `nasm -f elf32` + `ld -m elf_i386`, ma servono librerie multilib (`gcc-multilib`).
- Verificare l'architettura con **`lscpu`** o **`uname -m`** è una skill base.

## Collegamenti con altri video

- Precedente: [[09_Introduction to Assembly]]
- Prossimo: [[011_Hello World in Assembly]] — primo programma sul lab appena configurato
- Strumenti del lab: [[08_Assemblers & Compilers]] (NASM, ld)
- Uso completo del lab: [[012_Data Types & Variables]]
