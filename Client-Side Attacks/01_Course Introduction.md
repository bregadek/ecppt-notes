# 01 — Course Introduction (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 1/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [01_Course Introduction.txt](01_Course Introduction.txt) · [01_Course Introduction.srt](01_Course Introduction.srt)

## Concetti chiave

- Il corso è una **introduzione completa al client-side attack** come tecnica di **initial access** in operazioni di pentest/red team.
- Roadmap: Intro → Client-side recon & fingerprinting → Social Engineering & Pretexting → Phishing con **Gophish** → Resource Development & Weaponization → **VBA macros** (dropper, reverse shell, ActiveX) → **HTA** → **MacroPack** → **HTML Smuggling** → Spear Phishing → Browser shells (**BeEF**).
- Focus operativo: **Microsoft Office** come vettore principale (macro abilitate), **mshta.exe** per HTA, **PowerShell** come dropper, **BeEF** per attacchi via browser.
- Prerequisiti: penetration testing lifecycle (livello eJPT), familiarità Windows/Linux, basi di Metasploit.
- Filosofia: il client (employee + suo PC) è "the weakest link" → recon mirata e payload **tailor-made**.

## Spiegazione approfondita

### Topic Overview (blocchi del corso)
1. **Introduction to client-side attacks** — definizione, motivazioni, vantaggi rispetto agli attacchi server-side.
2. **Client-side information gathering & fingerprinting** — identificare browser, OS, software installato sul target.
3. **Social Engineering & Pretexting** — manipolazione + creazione di contesto credibile per la consegna del payload.
4. **Phishing con Gophish** — planning, deploy, tracking di campagne phishing.
5. **Resource Development & Weaponization** — costruire payload e Office docs weaponizzati.
6. **VBA Macros** — fondamenti, sviluppo, integrazione PowerShell, ActiveX per controllare l'esecuzione.
7. **HTA (HTML Applications)** — uso di `mshta.exe` come vettore di esecuzione, anche embedded in macro.
8. **HTML Smuggling** — payload nascosto in pagine HTML+JS (Blob API).
9. **Browser-based attacks** — abuso di pop-up, notifiche e finti update via **BeEF**.

### Prerequisiti
- **Penetration testing lifecycle**: chi arriva da eJPT è la baseline.
- **Windows + Linux**: capacità di operare da CLI, conoscere processi/servizi.
- **Metasploit Framework**: uso base (msfvenom, multi/handler).

### Learning Objectives (alla fine del corso)
- Capire **cosa sono i client-side attacks** e quali vettori esistono per initial access.
- Eseguire **client-side information gathering + fingerprinting** (browser, OS, software).
- Padroneggiare **Social Engineering**, ruolo del **pretexting** in una campagna riuscita.
- Pianificare, deployare e gestire campagne phishing con **Gophish**.
- Capire **Resource Development & Weaponization** in chiave client-side.
- Sviluppare **VBA macro** custom per initial access (dropper, reverse shell, ActiveX trigger).
- Generare e personalizzare **documenti Office malevoli**.
- Sfruttare **HTA** sia in stand-alone (via `mshta.exe`) sia integrate in macro.

## Comandi & strumenti

Video introduttivo, nessun comando. Strumenti citati che vedremo:

| Strumento | Categoria | Scopo |
|---|---|---|
| **Gophish** | Phishing platform | Campagne phishing complete con tracking |
| **VBA / Office** | Macro malware | Document_Open / Auto_Open / Workbook_Open |
| **PowerShell** | Dropper / payload | IEX, download cradle |
| **mshta.exe** | LOLBIN | Esecuzione HTA |
| **MacroPack** | Macro generator | Automazione e obfuscation macro |
| **BeEF** | Browser exploitation | Hook su browser, pop-up, fake updates |

## Esempi pratici

N/A — video introduttivo. Le demo iniziano nei moduli successivi.

## Punti d'attenzione per l'esame eCPPT

- L'esame eCPPT (2024) include scenari di **initial access** che richiedono di scegliere il giusto vettore client-side data una recon (es. ufficio HR con Office installato → Word macro).
- Memorizza la **catena**: Recon → Target ID → Pretext → Payload Dev → Delivery → Execution → Post-exploitation.
- Sapere distinguere **client-side vs server-side** (target, esecuzione, contromisure).
- Sapere che **macro + HTA + HTML smuggling** sono i 3 vettori coperti in profondità.

## Collegamenti con altri video

- Prossimo: [[02_Introduction to Client-Side Attacks]]
- Recon: [[04_Client-Side Information Gathering]] · [[05_Client Fingerprinting]]
- Phishing: [[08_Phishing with Gophish - Part 1]]
- Macro: [[011_VBA Macro Fundamentals]] · [[014_Weaponizing VBA Macros with MSF]]
- HTA: [[019_HTML Applications (HTA)]]
- Smuggling: [[023_File Smuggling with HTML & JavaScript]]
- Browser shells: [[025_Establishing a Shell Through the Victim's Browser]]
- Conclusione: [[026_Course Conclusion]]
