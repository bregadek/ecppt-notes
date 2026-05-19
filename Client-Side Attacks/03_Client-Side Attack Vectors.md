# 03 — Client-Side Attack Vectors (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 3/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [03_Client-Side Attack Vectors.txt](03_Client-Side Attack Vectors.txt) · [03_Client-Side Attack Vectors.srt](03_Client-Side Attack Vectors.srt)

## Concetti chiave

- **Attack vector** = percorso/metodo usato per exploit di vulnerabilità o weakness in un sistema.
- I client-side attack vectors principali: **Social Engineering** (phishing, social media), **Pretexting / Baiting / Tailgating**, **Malicious Documents**, **Drive-by Downloads**, **Watering Hole**, **USB-based**, **Exploit Kits**, **Browser Exploitation**.
- **Phishing email** + **malicious document** = combo più usata e più efficace.
- **BeEF** è citato come exploit kit / framework per browser exploitation.
- **Watering Hole** = compromesso di un sito frequentato dal target, raro ma potente.

## Spiegazione approfondita

### Social Engineering
- **Phishing emails** — mail ingannevoli con allegato (doc, zip) o link malevolo.
- **Social media engineering** — fake profile (es. LinkedIn) per costruire fiducia, poi consegnare il payload.
- **Pretexting** — costruire un contesto credibile (es. fingersi recruiter, IT support) per legittimare la richiesta.
- **Baiting** — sfrutta offerte/curiosità ("compensation package in this Excel").
- **Tailgating** — fisico: seguire un employee dentro l'ufficio per accesso alla rete interna.

### Malicious Documents
Office (Word/Excel), PDF con embedded macro o exploit. Veicolo principale del corso: VBA macros in `.docm`/`.xlsm`.

### Drive-by Downloads
Hosting di payload / exploit kit / script su sito compromesso o malevolo. Quando l'utente visita → download automatico o prompt per "update".

### Watering Hole
Identifichi via recon un sito **non social** frequentato dal target (es. portale di settore). Lo compromettidi e inietti codice malevolo che colpisce solo i visitatori target. Complesso ma molto efficace per APT.

### USB-based attacks
Distribuzione di USB infette o Rubber Ducky. Cadute fuori dall'ufficio nella speranza che un employee le inserisca. Quando inserita esegue automaticamente payload/script.

### Exploit Kits
Suite automatizzate per colpire vuln in browser, plugin (Flash, Java), client software. Esempio menzionato: **BeEF (Browser Exploitation Framework)**.

### Browser Exploitation diretta
Exploit manuale di vuln in browser/plugin/estensioni per RCE. Differisce da exploit kit per il livello di automazione.

### Tabella riassuntiva vettori

| Vettore | Frequenza | Skill | Note |
|---|---|---|---|
| Phishing email + macro doc | Altissima | Bassa-media | Standard del corso |
| Social media engineering | Alta | Media | Fake profile, long-game |
| Pretexting | Trasversale | Media-alta | Abilita tutti gli altri |
| Drive-by download | Media | Media | Sito + landing malevola |
| Watering hole | Bassa | Alta | Tipico di APT |
| USB / Rubber Ducky | Media | Bassa | Richiede vicinanza fisica |
| Exploit kit (BeEF) | Media | Media | Browser hooking automatico |
| Browser exploitation | Bassa | Alta | Manuale, RCE su browser |

## Comandi & strumenti

Video teorico, nessun comando. Tool menzionati:
- **BeEF** (esplorato nel modulo 025).
- **Office macro tooling** (modulo VBA Macros).

## Esempi pratici

Combinazioni realistiche:
- Phishing email + Word con macro → la più comune.
- Social media (LinkedIn) "recruiter Sarah" → invia "JD.docm" → execute.
- Watering hole → forum di settore compromesso → inject JS che fa drive-by con HTA.

## Punti d'attenzione per l'esame eCPPT

- **Distinguere chiaramente**: Pretexting (creare contesto) ≠ Phishing (invio mail) ≠ Baiting (offerta/incentivo) ≠ Tailgating (fisico).
- **Spear Phishing** vs phishing generico (vedi video 024).
- **Watering hole**: target organizzazione tramite un sito di terzi compromesso.
- **BeEF** = exploit kit citato; sarà usato nel video 025.
- **USB-based** rientra nei client-side anche se fisico.
- Possibile domanda: "Quale vettore usi se l'employee non clicca link ma usa l'ufficio fisico?" → tailgating + USB drop.

## Collegamenti con altri video

- Precedente: [[02_Introduction to Client-Side Attacks]]
- Prossimo: [[04_Client-Side Information Gathering]]
- Pretexting: [[07_Pretexting]] · [[018_Pretexting Phishing Documents]]
- Phishing pratico: [[08_Phishing with Gophish - Part 1]]
- Malicious docs: [[011_VBA Macro Fundamentals]]
- HTA / drive-by: [[019_HTML Applications (HTA)]] · [[020_HTA Attacks]]
- Browser exploitation / BeEF: [[025_Establishing a Shell Through the Victim's Browser]]
