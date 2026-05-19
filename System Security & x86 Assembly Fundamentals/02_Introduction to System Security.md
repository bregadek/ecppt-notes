# 02 — Introduction to System Security (System Security & x86 Assembly)

> **Modulo:** System Security & x86 Assembly Fundamentals · **Video:** 2/13
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Introduction to System Security.txt](02_Introduction to System Security.txt) · [02_Introduction to System Security.srt](02_Introduction to System Security.srt)

## Concetti chiave

- Il corso **System Security** è la **base teorica** per pentester e red teamer: computer architecture + assembly language + meccanismi di sicurezza dei computer system.
- Serve come **prerequisito al corso Exploit Development**, che parte direttamente con i **buffer overflow** senza ripassare le basi.
- L'instructor afferma esplicitamente che **questo corso è più importante dell'Exploit Development**, perché senza le fondamenta non si capiscono i BO.
- Le competenze fornite abilitano: **fuzzing, exploit development, buffer overflow, debugging, reverse engineering, malware analysis**.
- Focus: **x86 (IA32) instruction set** su **Linux**, con accenni a x64.
- L'assembly è la **gateway** verso exploitation, reverse engineering e shellcoding.

## Spiegazione approfondita

### Cosa imparerai (in sintesi)
- **CPU architecture** e gestione della memoria.
- Intricacies di **x86 e x64 instruction set** (focus su x86).
- **32-bit assembly language** per Intel architecture (IA32) su Linux.
- Come applicare queste conoscenze in **infosec / cybersecurity** offensiva.

### Perché studiare assembly come pentester?
Anche per chi fa **network/AD pentesting** la conoscenza dell'assembly:
- Permette di **sfruttare manualmente buffer overflow**.
- Apre la strada al **reverse engineering** (capire come gira un binario).
- È la base per **binary exploitation** moderna.
- Aumenta le opzioni di carriera (resource development, red team operator avanzato).

### Posizionamento nel learning path eCPPT
```
... → System Security & x86 Assembly  (questo corso)
                  ↓ (prerequisito)
       Exploit Development            (buffer overflow, fuzzing, shellcoding)
```

### Tono del corso
Volutamente **introduttivo** e accessibile a chi non ha mai programmato. L'istruttore ribadisce di **non spaventarsi** dalla complessità apparente: le slide vanno riviste più volte, i concetti si consolidano con la pratica.

## Comandi & strumenti

Nessun comando in questo video (panoramica narrativa).

## Esempi pratici

N/A — vedi videos 011, 012 per i primi esempi pratici in NASM.

## Punti d'attenzione per l'esame eCPPT

- L'esame eCPPT include scenari di **buffer overflow** elementari: senza le basi di questo corso è impossibile risolverli.
- Memorizza i **5 ambiti** sbloccati dall'assembly: **fuzzing · exploit development · buffer overflow · debugging · RE/malware analysis**.
- La scelta didattica del corso è **x86 (32-bit) Linux**: gli stessi concetti applicati all'esame.
- Sapere **perché** l'assembly conta è spesso una domanda concettuale ("why do you need to understand low level to exploit X?").

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_CPU Architecture]] (inizio della sezione tecnica)
- Conclusione e verifica obiettivi: [[013_Course Conclusion]]
