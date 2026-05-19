# 015 — Optimizing Nmap Scans (Network Penetration Testing)

> **Modulo:** Network Penetration Testing · **Video:** 15/26
> **Istruttore:** Alexis Ahmed (HackerSploit / INE)
> **Fonte appunti:** [015_Optimizing Nmap Scans.txt](015_Optimizing Nmap Scans.txt) · [015_Optimizing Nmap Scans.srt](015_Optimizing Nmap Scans.srt)

## Concetti chiave

- **Timing template `-T0..-T5`**: regola velocità e parallelismo dei probe Nmap.
- Nicknames (da memorizzare!): **T0 paranoid · T1 sneaky · T2 polite · T3 normal (default) · T4 aggressive · T5 insane**.
- **T0/T1** servono a **evadere IDS** (probe distanti tra loro); **T4/T5** servono a **velocizzare** su reti veloci/affidabili.
- **`--scan-delay <time>`**: spazia manualmente i probe (es. `5s`, `15s`, `500ms`).
- **`--max-rate <N>` / `--min-rate <N>`**: cap superiore/inferiore di pacchetti al secondo.
- **`--host-timeout <time>`**: rinuncia su un host dopo X tempo (utile su grandi subnet).
- Slow down = stealth + protezione hardware vecchio; speed up = scansioni rapide su lab/network noti.

## Spiegazione approfondita

### Timing template
| Template | Nickname | Uso tipico |
|---|---|---|
| `-T0` | Paranoid | IDS evasion estremo (probe ogni ~5 minuti) |
| `-T1` | Sneaky | IDS evasion (probe ogni ~15 secondi) |
| `-T2` | Polite | Riduce carico sul target / hardware fragile |
| `-T3` | Normal | **Default** Nmap |
| `-T4` | Aggressive | Reti veloci/affidabili (standard pen test) |
| `-T5` | Insane | Massima velocità, può sacrificare accuratezza |

I template impostano in automatico una serie di parametri (parallelism, RTT timeouts, scan delay, retries). Quando si vuole un controllo fine si combinano con `--scan-delay`, `--max-rate`, `--max-retries`.

### `--scan-delay`
Forza un intervallo fisso tra ogni probe inviato. Sintassi:
- `--scan-delay 5s` (5 secondi)
- `--scan-delay 500ms` (millisecondi)
- `--scan-delay 15s` per stealth tipico

```bash
sudo nmap -Pn -sS -F --scan-delay 15s <target>
```
In Wireshark si osserva un SYN ogni 15 secondi esatti tra source e dest → look molto meno sospetto.

### `--host-timeout`
Su subnet grandi alcuni host possono richiedere troppo per rispondere (es. firewall che dropper alcuni probe e li forza in retry). Con `--host-timeout 5s` Nmap **abbandona** un host se non finisce entro 5 secondi.

```bash
sudo nmap -Pn -sS -sV -F --host-timeout 5s <subnet>/24
```
Nel lab: scan completo passa da 45.63s a 14.40s (skip degli host lenti). **Cautela**: timeout troppo bassi causano falsi negativi.

Sintassi tempi: `s` (sec), `m` (min), `h` (ore). Es. `--host-timeout 30m`.

### `--max-rate` e `--min-rate`
- `--max-rate 100` → al massimo 100 pacchetti/sec (utile contro IDS).
- `--min-rate 1000` → forza almeno 1000 pacchetti/sec (utile su scan massivi).
- Alexis preferisce non usarli e ricorre a `--scan-delay`/timing template.

### Quando usare cosa
- **Pen test interno tipico**: `-T4`.
- **Pen test stealth con IDS**: `-T1` + `--scan-delay 15s` + `-D` decoy + `-f`.
- **Scan grande Internet/CIDR**: `-T4 --host-timeout 30s`.
- **Network fragile / legacy**: `-T2` o `-T3` per non rompere switch/router vecchi.

## Comandi & strumenti

| Comando | Scopo | Note |
|---|---|---|
| `nmap -T0 <target>` | Paranoid (IDS evasion estremo) | Lentissimo |
| `nmap -T1 <target>` | Sneaky (IDS evasion) | Probe ogni ~15s |
| `nmap -T2 <target>` | Polite (riduce carico) | |
| `nmap -T3 <target>` | Normal (default) | |
| `nmap -T4 <target>` | Aggressive | Default per pen test |
| `nmap -T5 <target>` | Insane | Max velocità |
| `nmap --scan-delay <time>` | Delay fisso tra probe | `5s`, `15s`, `500ms` |
| `nmap --max-rate <N>` | Cap pacchetti/sec | |
| `nmap --min-rate <N>` | Minimo pacchetti/sec | |
| `nmap --host-timeout <time>` | Abbandona host lenti | `5s`, `30s`, `5m` |
| `nmap --max-retries <N>` | Riduce/aumenta retry | Default 10 |

## Esempi pratici

```bash
# 1. Standard pen-test interno
sudo nmap -sS -sV -A -T4 -p- <target>

# 2. Stealth massimo con timing
sudo nmap -Pn -sS -T1 -p 445,3389 <target>

# 3. Spacing custom (15s tra probe)
sudo nmap -Pn -sS -F --scan-delay 15s <target>

# 4. Scan grande subnet con host-timeout
sudo nmap -Pn -sS -sV -F --host-timeout 5s <subnet>/24

# 5. Combinazione stealth completa
sudo nmap -Pn -n -sS -T1 --scan-delay 15s -f -D <gw>,ME -g 53 <target>
```

Nota extra: combinare `-T1` + `--scan-delay` è ridondante perché T1 già include uno scan-delay implicito; `--scan-delay` esplicito override quello di T1.

## Punti d'attenzione per l'esame eCPPT

- **Memorizzare nicknames T0–T5 in ordine**: paranoid, sneaky, polite, normal, aggressive, insane.
- **Default = T3**.
- **T4 = standard** per la maggior parte degli scan in pen test.
- **`--scan-delay 5s`** sintassi con suffisso `s/ms/m/h`.
- **`--host-timeout`** evita di sprecare tempo su host che non rispondono → usare con cautela (rischio false negative).
- **`--max-rate` / `--min-rate`** = controllo pacchetti/sec.
- Slowdown serve sia per **IDS evasion** sia per **hardware fragile/legacy**.
- T0/T1 = lentissimi, possono richiedere ORE su un singolo host.
- T5 può **perdere risultati** su reti lossy o host firewallati.

## Collegamenti con altri video

- Precedente: [[014_Firewall Detection & IDS Evasion]] — timing è componente chiave dell'evasion.
- Prossimo: [[016_Nmap Output Formats]] — salvare i risultati dello scan ottimizzato.
- NSE per scan mirati veloci: [[013_Nmap Scripting Engine (NSE)]]
- OS/Service detection: [[012_Service Version & OS Detection]]
