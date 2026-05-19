# 026 — Course Conclusion (Client-Side Attacks)

> **Modulo:** Client-Side Attacks · **Video:** 26/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [026_Course Conclusion.txt](026_Course Conclusion.txt) · [026_Course Conclusion.srt](026_Course Conclusion.srt)

## Concetti chiave

- Recap dei **9 learning objectives** dichiarati nel video introduttivo e verifica copertura.
- Tutto il syllabus è stato coperto: client-side attack types, fingerprinting, social engineering, pretexting, phishing con Gophish, resource development, weaponization, VBA macros, ActiveX, HTA applications.
- Argomento esplicitamente **NON** coperto a fondo: AV evasion / obfuscation (rimandato a corsi dedicati come **PowerShell for Pentesters** e **C2**).
- Il corso ha mostrato la **catena completa** initial access → post-ex → privesc → lateral, non solo l'initial access.

## Spiegazione approfondita

### Verifica learning objectives

| # | Learning Objective | Coperto in |
|---|---|---|
| 1 | Capire cosa sono i client-side attacks e i vari tipi per initial access | Video 02, 03 |
| 2 | Eseguire client-side information gathering e fingerprinting | Video 04, 05 |
| 3 | Capire social engineering, tipi di SE, ruolo del pretexting | Video 06, 07 |
| 4 | Pianificare, deployare, gestire campagne di phishing con Gophish | Video 08, 09 |
| 5 | Capire resource development e weaponization in ambito client-side | Video 010 |
| 6 | Sviluppare proprie VBA macros per initial access | Video 011-016 |
| 7 | Sfruttare ActiveX controls per controllo/facilitazione esecuzione macro | Video 017 |
| 8 | Sviluppare e customizzare propri documenti macro-enabled Office | Video 011-022 (incl. MacroPack) |
| 9 | Sfruttare HTML Applications (HTA) per initial access | Video 019, 020 |

### Cosa NON è stato coperto a fondo (e dove cercare)
- **Obfuscation profonda** dei payload (Invoke-Obfuscation, AMSI bypass moderno) → corso [[011_PowerShell-Empire]] / [[013_Obfuscating PowerShell Code]] del modulo PowerShell for Pentesters.
- **AV evasion** con tool moderni (Donut, ScareCrow, Shellter) → [[012_AV Evasion with Shellter]].
- **C2 frameworks** completi (Cobalt Strike, Mythic, Sliver, Havoc) → modulo dedicato [[Command & Control (C2C&C)]].
- **Browser exploitation** via CVE specifici (Browser AutoPwn è solo un'introduzione) — richiede studio CVE-by-CVE.

### Take-away strategici per l'esame eCPPT
1. **Pretexting batte la tecnologia**: il payload più sofisticato fallisce se l'email è poco credibile.
2. **Pipeline**: Reconnaissance → Fingerprinting → Resource Development → Weaponization → Delivery → Execution → C2.
3. **MacroPack** è il tool "industriale" per produrre documenti malevoli; tutto il flusso manuale visto nei video 011-017 viene compresso in un'unica command line.
4. **HTA + mshta.exe** è ancora un vettore valido perché LOLBin (Living-Off-the-Land Binary), spesso non bloccato.
5. **BeEF + Apache + msfvenom + multi/handler** è il setup minimo per initial access via browser.
6. La catena `phishing → meterpreter → autoroute → socks → portfwd → exploit interno → PtH → enable_rdp` (video 024) è praticamente uno **scenario d'esame standard**.

## Comandi & strumenti

| Strumento | Categoria | Modulo |
|---|---|---|
| Gophish | Phishing infrastructure | 08, 09 |
| MS Office (VBA) | Resource Development | 011-016 |
| Powercat | Reverse shell PowerShell | 016 |
| ActiveX | Macro execution control | 017 |
| mshta.exe (HTA) | Initial access LOLBin | 019, 020 |
| MacroPack | Macro weaponization automation | 021, 022 |
| HTML5 file smuggling (Blob/data URI) | Defender bypass | 023 |
| Python `smtplib` + msfvenom + multi/handler | Lab phishing simulato | 024 |
| BeEF (browser exploitation framework) | Browser hook & control | 025 |

N/A in questo video conclusivo — è solo verifica obiettivi.

## Esempi pratici

N/A — video conclusivo senza demo.

## Punti d'attenzione per l'esame eCPPT

- **Memorizza i 9 learning objectives** come "indice mentale" del modulo — molte domande mappano direttamente a un obiettivo.
- **Vettori di initial access** (importante elenco completo):
  - Macro VBA (Word/Excel)
  - HTA (`mshta.exe`)
  - Spear phishing attachment (EXE)
  - Fake Update via BeEF / browser
  - File smuggling HTML5
  - LNK / ISO smuggling (menzionati in 023 come idea)
- **Pretexting**: domande possono chiedere differenza tra pretexting, phishing, spear phishing, whaling, vishing, smishing.
- **Gophish**: profili sender, template, landing page, campaign — sai associarli ai 4 oggetti?
- **Resource Development vs Weaponization**: domanda di terminologia (Resource Development = preparare risorse, Weaponization = combinare in payload final).
- **MacroPack flags base**: `-t WORD/EXCEL/PPT`, output `-o`, `--obfuscate-form`, `-G/-W` per generazione VBA.

## Collegamenti con altri video

- Punto di partenza: [[01_Course Introduction]]
- Macro VBA: [[011_VBA Macro Fundamentals]] · [[012_VBA Macro Development - Part 1]] · [[013_VBA Macro Development - Part 2]] · [[014_Weaponizing VBA Macros with MSF]]
- HTA: [[019_HTML Applications (HTA)]] · [[020_HTA Attacks]]
- Phishing infra: [[08_Phishing with Gophish - Part 1]] · [[09_Phishing with Gophish - Part 2]]
- MacroPack: [[021_Automating Macro Development with MacroPack - Part 1]] · [[022_Automating Macro Development with MacroPack - Part 2]]
- Lab finale end-to-end: [[024_Initial Access Via Spear Phishing Attachment]] · [[025_Establishing a Shell Through the Victim's Browser]]
- Prossimi passi (AV evasion + C2): [[012_AV Evasion with Shellter]] · [[011_PowerShell-Empire]]
