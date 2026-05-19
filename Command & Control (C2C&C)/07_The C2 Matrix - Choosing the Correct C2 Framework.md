# 07 — The C2 Matrix: Choosing the Correct C2 Framework (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 7/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [07_The C2 Matrix - Choosing the Correct C2 Framework.txt](07_The C2 Matrix - Choosing the Correct C2 Framework.txt) · [07_The C2 Matrix - Choosing the Correct C2 Framework.srt](07_The C2 Matrix - Choosing the Correct C2 Framework.srt)

## Concetti chiave

- **C2 Matrix** è un progetto aperto che aggrega in un **Google Sheet** tutti i C2 framework pubblicamente noti (>140 alla data del video), open source e commerciali.
- Fornisce anche un **questionario interattivo** che, in base ai requisiti dichiarati, suggerisce un sottoinsieme di C2 candidati.
- La scelta del C2 dipende da: **requisiti funzionali** (canali, OS supportati, capabilities), **target environment** (Windows/Linux, AV/EDR, egress), **preferenza personale**, **budget**.
- Categorie principali: **commerciali** (Cobalt Strike, Brute Ratel, Core Impact) vs **open source** (Empire, Sliver, Mythic, Covenant, Havoc).
- Criteri di valutazione nello sheet: licenza, prezzo, lingua implementazione (server+implant), UI (CLI/Web/GUI), API, payload OS, canali, capability (key exchange, domain fronting, jitter, BOF, SOCKS, pivoting, logging, ATT&CK mapping, dashboard), supporto.

## Spiegazione approfondita

### Il problema
"Quale C2 uso?" è la domanda dominante. Non c'è risposta unica: dipende da requisiti, preferenze, budget, ambiente target. La proliferazione di framework (>140) rende difficile scegliere.

### C2 Matrix — Google Sheet
Colonne principali:
- **Name, License** (GPL, BSD, Apache, Commercial in rosso), **Price**, GitHub, Site, Twitter, **Implementation language**, **Server language**, **Implant language**.
- **UI**: multi-user (yes/no), CLI, Web, GUI, dark mode, **API**.
- **Payloads**: Windows / Linux / macOS, formati, packaging.
- **C2 channels**: TCP, HTTP, HTTP/2, HTTP/3, DNS, DoH, ICMP, FTP, IMAP, MAPI, SMB, LDAP.
- **Capabilities**: key exchange, steganography, **proxy aware**, **domain fronting**, custom profiles, **jitter**, working hours, kill date, chaining, **logging**, **ATT&CK mapping**, dashboard, **SOCKS**, VPN pivoting, **BOF**.
- **Detection**, **Support** (community, docs, attivamente mantenuto).

### Esempi notevoli dalla matrice
- **Brute Ratel** (commerciale, $2,500) — Golang server, implant C/x64 ASM, solo Windows, TCP/HTTP/SMB/LDAP, GUI multi-user. Molto popolare nei red team commerciali.
- **Cobalt Strike** — leader storico commerciale, malleable C2, beacon SMB/DNS/HTTP/HTTPS.
- **PowerShell-Empire (Empire 4)** — open source, multi-user, Starkiller GUI, payload Win/Linux/macOS, solo HTTP-based ma proxy-aware, domain fronting, custom profiles, jitter, logging. Scelta dell'istruttore per Windows.
- **Covenant** — .NET, web UI.
- **Sliver, Mythic, Havoc** — alternative open source moderne.

### Questionario C2 Matrix (esempi di domande)
1. Servono multi-user / API?
2. Quali canali ti servono (HTTP, DNS, SMB...)?
3. Quali OS devono supportare gli agent?
4. Quali capability servono (proxy aware, custom profile, jitter, logging, domain fronting...)?
5. Quale interfaccia preferisci (CLI, GUI, Web)?
6. Che tipo di supporto vuoi (sito, setup guide, GitHub attivo)?

Output esempio: con requisiti "multi-user + HTTP + Windows + proxy/profile/jitter/logging/domain fronting + GUI" → suggerisce **Covenant**. Variando (no multi-user, GUI, no support specifico) → **Cobalt Strike**, **Poshc2**, **Prismatica**.

→ Il tool **non è perfetto** (non include tutti i C2 in matching), ma è utile come starting point.

## Comandi & strumenti

| Risorsa | URL | Uso |
|---|---|---|
| **C2 Matrix site** | https://www.thec2matrix.com/ | Hub progetto |
| **C2 Matrix spreadsheet** | Google Sheet linked | Confronto dettagliato feature |
| **C2 Matrix questionnaire** | https://howto.thec2matrix.com/ | Scelta guidata via Q&A |

Nessun comando da eseguire — è un workflow di selezione tramite risorse online.

## Esempi pratici

**Scenario**: red team Windows-only, vogliamo proxy-aware, custom profiles, jitter, logging, domain fronting, multi-user, GUI.
1. Apri C2 Matrix questionnaire.
2. Rispondi alle domande con i requisiti.
3. Output filtrato → Empire / Covenant / Cobalt Strike (a seconda dei dettagli).
4. Verifica dettagli sul Google Sheet (canali supportati, prezzo, manutenzione).
5. Scelta finale per il modulo del corso: **PowerShell-Empire**.

## Punti d'attenzione per l'esame eCPPT

- **Conosci la mappa C2 popolari**:
  - **Cobalt Strike** — leader commerciale Windows, beacon SMB/DNS/HTTP, malleable profiles.
  - **PowerShell-Empire** — open source Windows-centric, PowerShell native, multi-user, Starkiller GUI.
  - **Mythic** — modulare, multi-payload (Go/C#/Python), web UI.
  - **Sliver** — Bishop Fox, Golang, mTLS/WireGuard/HTTP/DNS, cross-platform, popolare alternative open source a Cobalt Strike.
  - **Havoc** — moderno open source, Windows, simil-Cobalt Strike.
  - **Covenant** — .NET, web UI.
- **Criteri di scelta da padroneggiare**: OS target, canali supportati, evasion (domain fronting, malleable), multi-user, supporto.
- L'esame può chiedere "quale C2 useresti se..." → ragiona su match feature ↔ scenario.
- **Brute Ratel** è solo Windows (implant C/ASM) e commerciale.
- **Empire** è la scelta didattica perché open source, multi-payload Windows, attivamente mantenuto da BC Security.

## Collegamenti con altri video

- Precedente: [[06_C2 Deployment & Operation]] — fattori di deployment che alimentano la scelta.
- Prossimo: [[08_Introduction to PowerShell-Empire]] — il framework scelto per il lab.
- Pratica: [[09_ Red Team Ops with PowerShell-Empire]] · [[010_Red Team Ops with Starkiller]]
- Wrap-up: [[011_ Course Conclusion]]
