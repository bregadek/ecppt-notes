# 05 — C2 Framework Terminology (Command & Control)

> **Modulo:** Command & Control (C2) · **Video:** 5/11
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [05_ C2 Framework Terminology.txt](05_ C2 Framework Terminology.txt) · [05_ C2 Framework Terminology.srt](05_ C2 Framework Terminology.srt)

> Nota: il modulo salta il video 04 (numerazione discontinua, file `.txt` non presente).

## Concetti chiave

- Video di **vocabolario condiviso** tra tutti i C2 framework. I termini ricorrono ovunque, anche se ogni framework usa nomi propri.
- Termini fondamentali: **C2 server, listener, agent, implant, beacon/beaconing, interface, payload, stager, sleep timer, jitter**.
- Distinzione chiave: **agent ≈ implant ≈ payload ≈ stager** sono spesso sinonimi parziali — riferiti tutti al "pezzo di codice che gira sul target e parla con il C2".
- Il **beaconing** è il pattern di callback periodico (no reverse shell interattiva): l'agent contatta il server ogni `sleep` secondi, riceve il task, lo esegue, restituisce il risultato al beacon successivo.
- **Sleep + Jitter** servono a rendere il traffico **meno sequenziale** → meno rilevabile dal blue team via NetFlow/IDS.

## Spiegazione approfondita

### C2 Server
Hub centrale a cui gli agenti fanno **callback**. Nel modello centralizzato è il "primary C2 server".

### Listener
Processo sul C2 server (o sul **redirector**) in ascolto su una porta/protocollo specifico per ricevere i callback degli agenti. Mentalmente: come l'**handler** Meterpreter di Metasploit.

### Agent
Pezzo di codice generato dal C2 framework, eseguito sul sistema compromesso, che si connette al listener per "essere comandato". È il **runtime** sul target.

### Implant
Sinonimo di agent / payload / stager. L'istruttore li separa concettualmente ma chiarisce che **fondamentalmente è la stessa cosa**: il codice che, eseguito sul target, stabilisce il canale C2.

### Beacon / Beaconing
È **come** un agent attivo chiama a casa periodicamente. Non c'è reverse shell diretta:
1. Configuri l'agent con `sleep = 5s`.
2. Ogni 5 s l'agent contatta il server "sono vivo, ho task?".
3. Tu invii `whoami` dal client → il server lo accoda.
4. Al beacon successivo l'agent lo riceve, esegue, e al **beacon ancora dopo** restituisce l'output.
→ Latency = sleep × (2 round-trip). Per questo l'interazione non è "real-time".

### Interface
Client che permette all'operatore di interagire col C2 server. Esempi: `msfconsole`, **PowerShell-Empire client**, **Starkiller**, **Armitage**. Possono essere locali o configurati per connessioni remote (tipico setup red team).

### Payload
Codice eseguito sul target per ottenere un obiettivo (es. stabilire una reverse shell). Spesso = implant. In Empire = **stager**.

### Stager
Piccolo eseguibile/script che funge da **dropper** per un payload più grande (lo **stage**). Modello **staged payload**:
- **stage 1 (stager)**: pochi byte, scarica/iniettà la stage 2.
- **stage 2 (stage)**: payload completo (reverse shell, beacon).
→ Vantaggio: stager piccoli passano meglio le restrizioni di delivery.

### Sleep Timer
Tempo tra due beacon consecutivi. `sleep 10` → callback ogni 10 secondi. Lo si aumenta per long-term ops (es. `sleep 3600`).

### Jitter
**Variabilità casuale** aggiunta al sleep per evitare pattern. Espresso in **ratio 0.0–1.0** (es. `0.5` = ±50%):
- Senza jitter: callback ogni esatti 10 s → su Wireshark è una riga sequenziale **sospetta**.
- Con jitter 0.5: callback in [5 s, 15 s] → traffico più "umano" e randomico.

→ Alcuni framework (es. **malleable C2** di Cobalt Strike) permettono anche di modificare i pacchetti (header, content type, host header) oltre al jitter.

## Comandi & strumenti

Video di terminologia: nessun comando, ma mappa di traduzione fra framework:

| Concetto generico | Metasploit | PowerShell-Empire | Cobalt Strike |
|---|---|---|---|
| C2 server | MSF server | Empire server | Team Server |
| Interface/Client | `msfconsole` | `powershell-empire client` / Starkiller | Cobalt Strike client |
| Listener | handler (`exploit/multi/handler`) | listener (es. `http`) | listener (`http`, `https`, `dns`, `smb`) |
| Stager | stager (`windows/x64/meterpreter/...`) | stager (`multi/launcher`, `windows/hta`...) | stager |
| Stage / Agent | meterpreter | agent | beacon |
| Beacon callback | session keepalive | beacon | beacon (con `sleep`) |
| Sleep | n/a (sessione interattiva) | `delay` option del listener | `sleep <sec> <jitter%>` |
| Jitter | n/a | `jitter` option | argomento di `sleep` |

## Esempi pratici

N/A — video teorico/vocabolario. Vedere esempi reali di sleep/jitter in [[010_Red Team Ops with Starkiller]] (dimostrazione Wireshark del beacon a 5/10 s e con jitter 0.5).

## Punti d'attenzione per l'esame eCPPT

- **Beacon ≠ reverse shell**: domanda classica. Beacon = pattern di callback periodico, latency = `sleep` × 2.
- **Sleep + Jitter** sono i due parametri **OPSEC critici** dell'agent. Saperli configurare.
- **Stager → Stage** = staged payload (Empire `multi/launcher` è uno stager PowerShell base64 one-liner).
- **Implant / Agent / Payload / Stager** vengono usati spesso come sinonimi: l'esame può chiederti di riconoscere il termine equivalente.
- **Listener** = lato server. **Agent** = lato client/target. Confondere i due è errore frequente.
- **Interface** = il client (CLI/GUI). Capacità di connettersi remotamente al server = **multi-user** ops.

## Collegamenti con altri video

- Precedente: [[03_Introduction to C2 Frameworks]]
- Prossimo: [[06_C2 Deployment & Operation]] — applichiamo terminologia all'infrastruttura.
- Uso dei termini in pratica: [[08_Introduction to PowerShell-Empire]] · [[09_ Red Team Ops with PowerShell-Empire]]
- Dimostrazione Wireshark sleep/jitter: [[010_Red Team Ops with Starkiller]]
