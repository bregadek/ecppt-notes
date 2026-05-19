# 06 — Introduction to Social Engineering (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 6/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_Introduction to Social Engineering_1717706352952.txt](06_Introduction to Social Engineering_1717706352952.txt) · [06_Introduction to Social Engineering_1717706352952.srt](06_Introduction to Social Engineering_1717706352952.srt)

## Concetti chiave

- **Social Engineering** = manipolazione di individui per ottenere accesso non autorizzato sfruttando **vulnerabilità della psicologia umana** (the weakest link).
- Bypassa i controlli tecnici colpendo direttamente l'employee.
- Archetipi psicologici sfruttati: **desire to be helpful**, **tendency to trust**, **desire for approval**, **fear of getting in trouble**, **avoiding conflict**.
- Termine coniato dall'industriale olandese **J.C. Van Marken (1894)**.
- Le agenzie d'intelligence (CIA, Mossad) chiamano questa pratica **target development**.
- **Tipi**: Phishing, **Spear Phishing**, Vishing (voce), Smishing (SMS), Pretexting, Baiting, Tailgating.
- Spear phishing = phishing **mirato** su individuo/gruppo specifico con info personalizzate.

## Spiegazione approfondita

### Definizione
Social engineering = tecnica per **manipolare individui** dentro un'organizzazione → ottenere unauthorized access a info, sistemi o facility. Sfrutta **trust** e **comunicazione** stabilita.

### Due categorie di azione
1. **Information disclosure** — far rivelare info ("quale versione di Word usate?").
2. **Performing actions** — far cliccare un link, scaricare allegato, fornire credenziali.

### I 5 archetipi psicologici (memorizzare per esame)
1. **Desire to be helpful** — la gente vuole sentirsi utile.
2. **Tendency to trust** — specialmente in società occidentali ben organizzate.
3. **Desire for approval** — bisogno di apprezzamento.
4. **Fear of getting in trouble** — efficace con junior, meno con executive.
5. **Avoiding conflict/arguments** — evitano scontro a tutti i costi.

### Perché funziona
Bypassa il perimetro tecnico. Non serve essere skilled hacker se si trova un employee giusto. Esempio menzionato: **breach Rockstar Games** da un giovane con social engineering.

### Social Media nella SE
- Facebook/Instagram → interessi personali.
- LinkedIn → ruoli, dipartimenti, colleghi.
- Twitter/X → opinioni, eventi.
- Profili spesso vecchi 5+ anni con info accumulate. Anche **eventi pubblicizzati** sono leva (stress, distrazione).

### Storia
- **1894 — J.C. Van Marken** conia "social engineering" (gestire relazioni sociali come sistemi meccanici).
- **Intelligence community**: target development (long-game per estrarre info).
- Solo **recentemente** è diventato parte del pentest (prima era solo red team).

### Phishing — i 5 step
1. **Planning & Reconnaissance** — recon employee, comm channels.
2. **Message Crafting** — mail credibile con urgency/fear.
3. **Delivery** — invio mass o targeted, bypass spam.
4. **Deception & Manipulation** — link/attachment malevolo.
5. **Exploitation** — payload eseguito → accesso.

### Spear Phishing — cosa cambia
Solo le **prime 3 fasi** differiscono:
1. **Target Selection & Research** — recon estensiva su singolo target (ruolo, relazioni, interessi).
2. **Message Tailoring** — riferimenti a eventi/progetti/colleghi reali (es. "Mark mi ha mandato questa invoice").
3. **Delivery** — via mail, social, IM, eventualmente account spoofed/compromessi.

### Tipi di Social Engineering

| Tipo | Canale | Note |
|---|---|---|
| **Phishing** | Email mass | Wide net |
| **Spear Phishing** | Email targeted | Personalizzato |
| **Whaling** | Email su executive | Sottocaso spear |
| **Vishing** | Telefono/voce | Impersona entità legittime |
| **Smishing** | SMS | Es. Pegasus (NSO) |
| **Pretexting** | Trasversale | Crea narrativa credibile |
| **Baiting** | Incentivi | Free software, job offer |
| **Tailgating** | Fisico | Seguire dentro area restricted |

### Phishing simulations
Aziende ingaggiano pen tester per campagne phishing **ricorrenti** (es. 6/anno) per misurare l'efficacia del training.

## Comandi & strumenti

Nessun comando — video teorico. Tool citati:
- **Social Engineering Toolkit (SET)**
- **Gophish** (vedremo nei video 08-09)
- **BeEF** (visto nel video 025)

## Esempi pratici

Pegasus / NSO Group esempio: SMS con link di fingerprinting → identifica device del giornalista → payload mirato.

Recruiter scam LinkedIn fine 2023: account falsi su Fortune 500 → "JD.docm" → macro malware.

## Punti d'attenzione per l'esame eCPPT

- Conoscere **5 archetipi psicologici** sfruttati.
- Distinzione netta **Phishing vs Spear Phishing vs Whaling** (mass / targeted / executive).
- **Vishing** (voce) vs **Smishing** (SMS) — domande terminologiche tipiche.
- **Pretexting** è trasversale: non è un tipo separato ma una pratica che alimenta gli altri.
- **Spear phishing methodology**: cambiano solo i primi 3 step.
- Sapere che **client-side attack methodology** = phishing methodology + payload execution.
- Esame può chiedere: "Quale tecnica usi se vuoi targetare CFO con info da LinkedIn?" → **Whaling / Spear Phishing**.

## Collegamenti con altri video

- Precedente: [[05_Client Fingerprinting]]
- Prossimo: [[07_Pretexting]] — deep dive su pretexting.
- Phishing pratico: [[08_Phishing with Gophish - Part 1]] · [[09_Phishing with Gophish - Part 2]]
- Spear phishing applicato: [[024_Initial Access Via Spear Phishing Attachment]]
