# 02 — Introduction to Privilege Escalation (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 2/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [02_Introduction to Privilege Escalation.txt](02_Introduction to Privilege Escalation.txt) · [02_Introduction to Privilege Escalation.srt](02_Introduction to Privilege Escalation.srt)

## Concetti chiave

- **Privilege Escalation (PrivEsc)** = processo di ottenimento di **privilegi elevati** in un sistema/network, tipicamente da un low-priv user a un high-priv user o admin.
- Su **Windows**: da utente standard (es. `john`) → `Administrator` o **NT AUTHORITY\SYSTEM**.
- Su **Linux**: da utente standard → `root` o utente appartenente al gruppo `sudo`/`wheel`.
- Si ottiene **sfruttando vulnerabilità o misconfigurazioni** dell'OS che permettono di accedere a risorse/funzionalità ristrette.
- Esistono **due tipi**: **Vertical** e **Horizontal** privilege escalation.

## Spiegazione approfondita

### Perché eseguire privilege escalation
1. Eseguire **comandi amministrativi** non disponibili come standard user.
2. Pre-requisito per **persistence**, **credential access** (dumping hash da LSASS/SAM), pivoting profondo.
3. Accedere a risorse e funzionalità riservate a admin/root.

### Tipi di Privilege Escalation

#### Vertical Privilege Escalation
- L'attaccante passa da un account a **privilegi più alti**.
- Esempio Linux: da `student` a `root`.
- Esempio Windows: da `john` (user) a `Administrator` o `NT AUTHORITY\SYSTEM`.
- È il focus principale del corso.

#### Horizontal Privilege Escalation
- L'attaccante mantiene **lo stesso livello di privilegi** ma assume **l'identità di un altro utente**.
- Esempio: da user `john` a user `mary`, entrambi non admin → nessun guadagno di privilegi, ma accesso a risorse di mary.
- Può essere visto come una forma di **lateral movement** locale tra account.

### Processo generale
1. **Enumerazione locale** per identificare misconfigurazioni/vulnerabilità.
2. Selezione del vettore (service, token, SUID, sudo, ecc.).
3. Sfruttamento → ottenimento di una shell/processo con privilegi elevati.
4. Validazione (`whoami`, `whoami /priv`, `id`).

## Comandi & strumenti

Video teorico — nessun comando pratico eseguito. Comandi di base citati implicitamente per verifica privilegi:

| Comando | OS | Scopo |
|---|---|---|
| `whoami` | Windows | Utente corrente |
| `whoami /priv` | Windows | Privilegi del token corrente |
| `net localgroup administrators` | Windows | Membri del gruppo admin locale |
| `id` | Linux | UID/GID/gruppi del processo |
| `groups` | Linux | Gruppi dell'utente |

## Esempi pratici

N/A — video concettuale.

**Scenari illustrati:**
- Vertical (Linux): exploit di un applicativo → da user a `root`.
- Horizontal (Windows): pivot tra due account standard senza guadagno di privilegi.

## Punti d'attenzione per l'esame eCPPT

- Sii in grado di **definire correttamente** privilege escalation in poche righe.
- Distinguere **vertical vs horizontal**:
  | Tipo | Cambio di privilegi | Esempio |
  |---|---|---|
  | **Vertical** | Sì (verso l'alto) | user → root / NT AUTHORITY\SYSTEM |
  | **Horizontal** | No (stessi privilegi, altro utente) | john → mary (entrambi standard) |
- Su Windows ricorda che **NT AUTHORITY\SYSTEM** è il privilegio più alto (sopra Administrator).
- Su Linux il target è `root` (UID 0) — non confondere `sudo` (membership) con un cambio reale di privilegi.
- L'esame chiede spesso "quale tipo di privesc è questo scenario?" → leggi attentamente se il privilege set cambia.

## Collegamenti con altri video

- Precedente: [[01_Course Introduction]]
- Prossimo: [[03_Privilege Escalation with PowerUp]] — inizio Windows privesc.
- Sezione Linux equivalente parte da: [[014_Locally Stored Credentials]]
