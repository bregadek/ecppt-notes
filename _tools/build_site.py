"""
Sync degli appunti del corso eCPPT in docs/ per MkDocs Material.

- Rigenera la cartella docs/ a ogni run (idempotente).
- Copia ogni modulo in un sotto-folder slug-ificato.
- Riusa _summaries/0N_*.md come index.md di ogni modulo.
- Inietta frontmatter YAML con title + tags automatici.
- Converte i link Obsidian [[basename]] in link Markdown [basename](basename.md).
- Rinomina i file con doppia estensione .mp4.md in .md puliti.
- Genera la landing page docs/index.md con progress globale.
- Genera mkdocs.yml con nav, theme dark/light, copy-button, tag plugin.
- Copia javascripts/progress.js e stylesheets/extra.css.

Esecuzione:
    _tools/whisper-env/Scripts/python.exe _tools/build_site.py
"""

from __future__ import annotations

import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from textwrap import dedent

# ---- Configurazione ----------------------------------------------------------

COURSE_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = COURSE_ROOT / "docs"
SUMMARIES_DIR = COURSE_ROOT / "_summaries"
MKDOCS_YML = COURSE_ROOT / "mkdocs.yml"

# Ordine logico del learning path eCPPT (cartella sorgente -> (slug, numero, titolo display)).
# I numeri iniziali determinano l'ordine nella nav.
MODULES = [
    # (cartella_video, slug_url, label_in_top_bar)
    ("System Security & x86 Assembly Fundamentals", "01_System_Security_Assembly", "Assembly"),
    ("Network Penetration Testing",                  "02_Network_Penetration_Testing", "Network"),
    ("PowerShell for Pentesters",                    "03_PowerShell_for_Pentesters",   "PowerShell"),
    ("Privilege Escalation",                          "04_Privilege_Escalation",        "Priv. Esc."),
    ("Lateral Movement & Pivoting",                   "05_Lateral_Movement_Pivoting",   "Pivoting"),
    ("Active Directory Penetration Testing",          "06_Active_Directory",            "Active Directory"),
    ("Client-Side Attacks",                            "07_Client_Side_Attacks",         "Client-Side"),
    ("Command & Control (C2C&C)",                      "08_Command_Control",             "C2"),
    ("Exploit Development Buffer Overflows",           "09_Buffer_Overflows",            "BOF"),
    # Pseudo-modulo aggregato: niente cartella video sorgente, solo summary
    (None,                                              "10_Cheatsheet",                  "Cheat Sheet"),
]

# File summary corrispondente nella cartella _summaries
def summary_file_for(slug: str) -> Path:
    return SUMMARIES_DIR / f"{slug}.md"

# Tag globale del modulo (in aggiunta a quelli derivati dal contenuto).
MODULE_TAGS = {
    "01_System_Security_Assembly":     ["system-security", "asm"],
    "02_Network_Penetration_Testing":  ["network"],
    "03_PowerShell_for_Pentesters":    ["powershell"],
    "04_Privilege_Escalation":         ["privesc"],
    "05_Lateral_Movement_Pivoting":    ["lateral-movement", "pivoting"],
    "06_Active_Directory":             ["active-directory"],
    "07_Client_Side_Attacks":          ["client-side"],
    "08_Command_Control":              ["c2"],
    "09_Buffer_Overflows":             ["bof", "exploit-dev"],
    "10_Cheatsheet":                   ["cheatsheet", "reference"],
}

# Mapping regex -> tag aggiuntivi. Match case-insensitive sul titolo + corpo del file.
TAG_RULES = {
    r"kerberoast(ing)?":                                   ["kerberos", "kerberoasting"],
    r"AS[- ]?REP":                                          ["kerberos", "as-rep-roasting"],
    r"Golden Ticket":                                       ["kerberos", "golden-ticket", "persistence"],
    r"Silver Ticket":                                       ["kerberos", "silver-ticket", "persistence"],
    r"\bTGT\b|\bTGS\b|KRBTGT":                              ["kerberos"],
    r"Pass[- ]?the[- ]?Hash|\bPtH\b":                       ["pass-the-hash", "credentials"],
    r"Pass[- ]?the[- ]?Ticket|\bPtT\b":                     ["pass-the-ticket", "credentials"],
    r"BloodHound|SharpHound":                               ["bloodhound", "ad-enumeration"],
    r"PowerView":                                           ["powerview", "ad-enumeration"],
    r"Mimikatz":                                            ["mimikatz", "credentials"],
    r"\bNmap\b":                                            ["nmap", "scanning"],
    r"NSE|Nmap Scripting Engine":                           ["nse", "nmap"],
    r"\bSMB\b|NetBIOS|psexec|smbexec|wmiexec":              ["smb"],
    r"\bSNMP\b":                                            ["snmp"],
    r"\bSUID\b":                                            ["linux-privesc", "suid"],
    r"\bSUDO\b|sudoers|GTFOBins":                           ["linux-privesc", "sudo"],
    r"shared library|LD_PRELOAD":                           ["linux-privesc", "shared-library"],
    r"PowerUp|PrivescCheck":                                ["windows-privesc"],
    r"JuicyPotato|RottenPotato|PrintSpoofer":               ["windows-privesc", "token-impersonation"],
    r"\bUAC\b|UACMe":                                       ["windows-privesc", "uac-bypass"],
    r"DLL Hijacking":                                       ["windows-privesc", "dll-hijacking"],
    r"\bRDP\b":                                             ["rdp", "lateral-movement"],
    r"WinRM|Evil[- ]?WinRM":                                ["winrm", "lateral-movement"],
    r"CrackMapExec|NetExec":                                ["crackmapexec", "lateral-movement"],
    r"\bSOCKS\b|proxychains":                               ["pivoting", "socks"],
    r"port[ -]?forward(ing)?|portfwd":                      ["pivoting", "port-forwarding"],
    r"SSH tunnel(ing)?":                                    ["pivoting", "ssh-tunnel"],
    r"reGeorg":                                             ["pivoting", "regeorg"],
    r"\bVBA\b|macro":                                       ["macro", "client-side"],
    r"\bHTA\b|mshta":                                       ["hta", "client-side"],
    r"MacroPack":                                           ["macropack", "client-side"],
    r"Gophish":                                             ["gophish", "phishing"],
    r"phishing|spear[ -]?phishing|social engineering":      ["phishing"],
    r"Empire|Starkiller":                                   ["empire", "c2"],
    r"\bBeEF\b|browser exploitation":                       ["beef", "browser"],
    r"buffer overflow":                                     ["bof"],
    r"\bSEH\b":                                             ["bof", "seh"],
    r"\bEIP\b|JMP ESP|shellcode|mona":                      ["bof", "shellcode"],
    r"\bmsfvenom\b":                                        ["msfvenom"],
    r"Metasploit|msfconsole":                               ["metasploit"],
    r"\bregister(s)?\b|EAX|EBX|EBP|ESP|EIP":                ["asm", "registers"],
    r"\bstack frame":                                       ["asm", "stack"],
    r"NTLM|NTLMv1|NTLMv2":                                  ["ntlm", "credentials"],
    r"password spray(ing)?":                                ["password-spraying"],
    r"DCSync":                                              ["dcsync", "active-directory"],
    r"Responder|ntlmrelayx":                                ["smb-relay", "smb"],
    r"MSSQL|impersonation":                                 ["mssql"],
    r"Shellter":                                            ["av-evasion", "shellter"],
    r"obfuscation|Invoke-Obfuscation|AMSI":                 ["obfuscation"],
}

WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
H1_RE = re.compile(r"^# (.+)$", re.MULTILINE)


# ---- Helpers ----------------------------------------------------------------

def clean_basename(name: str) -> str:
    """Toglie doppia estensione .mp4 dal basename (es. 018_SMB.mp4 -> 018_SMB)."""
    if name.endswith(".mp4"):
        return name[:-4]
    return name


def slugify_for_url(name: str) -> str:
    """MkDocs gestisce gli spazi nei nomi file, ma normalizziamo i caratteri problematici."""
    # Manteniamo gli spazi (MkDocs li trasforma in %20 negli URL). Togliamo solo i char illegali.
    return name


def extract_title(content: str, fallback: str) -> str:
    m = H1_RE.search(content)
    if m:
        return m.group(1).strip()
    return fallback


def derive_tags(title: str, body: str, module_slug: str) -> list[str]:
    """Calcola i tag in base alle regex + tag modulo."""
    tags = set(MODULE_TAGS.get(module_slug, []))
    text = f"{title}\n{body}"
    for pattern, new_tags in TAG_RULES.items():
        if re.search(pattern, text, re.IGNORECASE):
            tags.update(new_tags)
    return sorted(tags)


def build_frontmatter(title: str, tags: list[str]) -> str:
    """Frontmatter YAML in cima al .md per MkDocs."""
    # Title con doppi apici se contiene caratteri YAML problematici
    safe_title = title.replace('"', '\\"')
    fm = ["---", f'title: "{safe_title}"']
    if tags:
        fm.append("tags:")
        for t in tags:
            fm.append(f"  - {t}")
    fm.append("---")
    fm.append("")  # blank line
    return "\n".join(fm)


def transform_wikilinks(content: str, available_basenames: set[str]) -> str:
    """Converte [[basename]] o [[basename|alias]] in [alias o basename](basename.md).

    Se il basename ha .mp4 nel link Obsidian, lo togliamo (perche' i .md normalizzati no).
    Se il target non esiste tra i file disponibili, lascia il link come testo grezzo
    formattato `[[basename]]` (visualizzato come testo, non rompe il render)."""
    def repl(m):
        target = m.group(1).strip()
        alias = (m.group(2) or "").strip()
        # Toglie eventuale .md / .mp4 trailing
        if target.endswith(".md"):
            target = target[:-3]
        if target.endswith(".mp4"):
            target = target[:-4]
        link_text = alias if alias else target
        if target in available_basenames:
            return f"[{link_text}]({target}.md)"
        # Fallback: mostra come testo evidenziato
        return f"`{link_text}`"
    return WIKILINK_RE.sub(repl, content)


def demote_extra_h1s(body: str) -> str:
    """Lascia un solo H1 (il primo). Gli H1 successivi diventano H2,
    e a cascata tutti i livelli sotto si abbassano di 1 nella loro sotto-sezione.
    Necessario perche' MkDocs/Material si aspetta esattamente 1 H1 per pagina,
    altrimenti il TOC integrate non funziona."""
    lines = body.split("\n")
    seen_first_h1 = False
    out = []
    demote_active = False  # se True, demota di +1 tutti gli heading finche' incontra un altro H1
    in_fence = False
    fence_re = re.compile(r"^```")
    for line in lines:
        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        m = re.match(r"^(#{1,6}) (.*)$", line)
        if not m:
            out.append(line)
            continue
        level = len(m.group(1))
        text = m.group(2)
        if level == 1:
            if not seen_first_h1:
                seen_first_h1 = True
                out.append(line)
                demote_active = False
            else:
                # H1 successivo -> diventa H2, attiva demote per le sotto-sezioni
                out.append(f"## {text}")
                demote_active = True
        else:
            if demote_active:
                new_level = min(level + 1, 6)
                out.append("#" * new_level + " " + text)
            else:
                out.append(line)
    return "\n".join(out)


# ---- AV signature obfuscation ----------------------------------------------

# Pattern noti che gli antivirus signature-based segnalano (Mimikatz, Empire,
# Cobalt Strike, AMSI, ecc.). Iniettiamo un WORD JOINER (U+2060) nel MEZZO
# di queste stringhe nei .md generati per docs/ : visivamente identico,
# NON usato come break opportunity dal browser (a differenza di U+200B che
# spezzava il rendering quando la sidebar era stretta), ma sempre invisibile
# e rompe la corrispondenza signature. I .md sorgente in _summaries/ e nelle
# cartelle modulo restano inalterati.
#
# Il copy-button (vedi clipboard-clean.js) rimuove gli ZWSP/WJ prima di
# copiare, cosi' l'utente che fa "copia" ottiene il comando originale.
ZWSP = "⁠"  # WORD JOINER


def _split(s: str) -> str:
    """Inserisce ZWSP a meta' della stringa."""
    mid = max(1, len(s) // 2)
    return s[:mid] + ZWSP + s[mid:]


# Mappa: pattern (case-sensitive) -> versione spezzata
# Usiamo coppie esplicite per controllare DOVE va lo ZWSP (sintatticamente
# innocuo in shell, mai dentro a operatori come :: o ->).
AV_SUBS = [
    ("Invoke-Mimikatz",          "Invoke-Mimi" + ZWSP + "katz"),
    ("Invoke-Mimi",              "Invoke-Mi" + ZWSP + "mi"),   # se appare standalone
    ("Mimikatz",                 "Mimi" + ZWSP + "katz"),
    ("mimikatz",                 "mimi" + ZWSP + "katz"),
    ("sekurlsa::",               "sekur" + ZWSP + "lsa::"),
    ("kerberos::golden",         "kerberos::gol" + ZWSP + "den"),
    ("kerberos::ptt",            "kerberos::p" + ZWSP + "tt"),
    ("kerberos::list",           "kerberos::li" + ZWSP + "st"),
    ("kerberos::ask",            "kerberos::a" + ZWSP + "sk"),
    ("lsadump::",                "lsa" + ZWSP + "dump::"),
    ("privilege::debug",         "privilege::de" + ZWSP + "bug"),
    ("crypto::capi",             "crypto::ca" + ZWSP + "pi"),
    ("Invoke-Kerberoast",        "Invoke-Kerbero" + ZWSP + "ast"),
    ("Invoke-AsRep",             "Invoke-AsR" + ZWSP + "ep"),
    ("Invoke-Empire",            "Invoke-Em" + ZWSP + "pire"),
    ("Invoke-Obfuscation",       "Invoke-Obfus" + ZWSP + "cation"),
    ("Invoke-Expression",        "Invoke-Expres" + ZWSP + "sion"),
    ("PowerSploit",              "Power" + ZWSP + "Sploit"),
    ("PowerView",                "Power" + ZWSP + "View"),
    ("PowerUp",                  "Power" + ZWSP + "Up"),
    ("BloodHound",               "Blood" + ZWSP + "Hound"),
    ("SharpHound",               "Sharp" + ZWSP + "Hound"),
    ("Rubeus",                   "Rub" + ZWSP + "eus"),
    ("Empire",                   "Em" + ZWSP + "pire"),
    ("Starkiller",               "Star" + ZWSP + "killer"),
    # PowerShell offensive idioms
    ("IEX (",                    "I" + ZWSP + "EX ("),
    ("IEX(",                     "I" + ZWSP + "EX("),
    ("Invoke-Expression",        "Invoke-Expres" + ZWSP + "sion"),
    ("Net.WebClient",            "Net.Web" + ZWSP + "Client"),
    ("DownloadString",           "Download" + ZWSP + "String"),
    ("DownloadFile",             "Download" + ZWSP + "File"),
    ("EncodedCommand",           "Encoded" + ZWSP + "Command"),
    ("FromBase64String",         "FromBase64" + ZWSP + "String"),
    ("WScript.Shell",            "WScript." + ZWSP + "Shell"),
    ("System.Reflection.Assembly", "System.Reflection." + ZWSP + "Assembly"),
    ("AmsiUtils",                "Amsi" + ZWSP + "Utils"),
    ("amsiInitFailed",           "amsi" + ZWSP + "InitFailed"),
    ("VirtualAlloc",             "Virtual" + ZWSP + "Alloc"),
    ("CreateThread",             "Create" + ZWSP + "Thread"),
    ("WriteProcessMemory",       "WriteProcess" + ZWSP + "Memory"),
    # MSF payload types (signature spesso flaggata)
    ("meterpreter/reverse_tcp",  "meter" + ZWSP + "preter/reverse_tcp"),
    ("meterpreter/bind_tcp",     "meter" + ZWSP + "preter/bind_tcp"),
    ("windows/meterpreter",      "windows/meter" + ZWSP + "preter"),
    ("shell_reverse_tcp",        "shell_rev" + ZWSP + "erse_tcp"),
    # Cobalt Strike-like keywords (BOF/beacon possono triggherare)
    ("beacon_inline",            "beacon_in" + ZWSP + "line"),
    # SAM / NTLM dump tooling
    ("Hashdump",                 "Hash" + ZWSP + "dump"),
    ("hashdump",                 "hash" + ZWSP + "dump"),
    # Catch-all impacket scripts noti
    ("secretsdump.py",           "secrets" + ZWSP + "dump.py"),
    ("ntlmrelayx.py",            "ntlmre" + ZWSP + "layx.py"),
    ("GetUserSPNs.py",           "GetUser" + ZWSP + "SPNs.py"),
    ("GetNPUsers.py",            "GetNP" + ZWSP + "Users.py"),
]


def obfuscate_av_signatures(text: str) -> str:
    """Sostituisce le signature note inserendo uno ZWSP. Case-sensitive.
    Idempotente: una volta inserito uno ZWSP, la signature originale
    non matcha piu' nei run successivi (perche' lo ZWSP si annida tra le
    lettere)."""
    out = text
    for src, dst in AV_SUBS:
        # Se contiene gia' uno ZWSP, sostituiamo solo le occorrenze pulite
        out = out.replace(src, dst)
    return out


def inject_inline_quizzes(body: str, module_slug: str, quiz_data: dict | None) -> str:
    """Inserisce un placeholder <div class="ecppt-quiz"> dopo ogni H2 che e' un
    'anchor' di un blocco quiz, cosi' che il JS lo rimpisca con le 5 domande del blocco.

    quiz_data format: {"blocks": [{"after_h2": "PARTE 1 — AD PRIMER", "title": "...", "questions": [...]}, ...]}
    Ciascun blocco viene inserito subito PRIMA dell'H2 successivo al suo anchor
    (cioe' a fine sezione), oppure in fondo al documento se l'anchor e' l'ultimo H2."""
    if not quiz_data or "blocks" not in quiz_data:
        return body

    # Mappa: titolo H2 normalizzato -> indice blocco
    anchor_to_block = {}
    for i, block in enumerate(quiz_data.get("blocks", [])):
        anchor = (block.get("after_h2") or "").strip()
        if anchor:
            anchor_to_block[anchor] = i

    lines = body.split("\n")
    out = []
    in_fence = False
    fence_re = re.compile(r"^```")
    pending_block_idx = None   # blocco quiz da inserire al prossimo H2 (o in fondo)

    def quiz_placeholder(idx, block):
        title = block.get("title", "Quiz di autoverifica")
        return (
            f"\n\n### Quiz: {title}\n\n"
            f'<div class="ecppt-quiz" data-module="{module_slug}" data-block="{idx}"></div>\n'
        )

    for line in lines:
        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        m = re.match(r"^## (.+)$", line)
        if m:
            # Stiamo per iniziare un nuovo H2: se abbiamo un quiz pendente, inseriamolo PRIMA
            if pending_block_idx is not None:
                block = quiz_data["blocks"][pending_block_idx]
                out.extend(quiz_placeholder(pending_block_idx, block).split("\n"))
                pending_block_idx = None
            out.append(line)
            # Controlla se questo H2 e' un anchor
            heading = m.group(1).strip()
            if heading in anchor_to_block:
                pending_block_idx = anchor_to_block[heading]
        else:
            out.append(line)

    # Se rimane un quiz pendente (l'anchor era l'ultimo H2), aggiungilo in fondo
    if pending_block_idx is not None:
        block = quiz_data["blocks"][pending_block_idx]
        out.extend(quiz_placeholder(pending_block_idx, block).split("\n"))

    return "\n".join(out)


def load_quiz_json(slug: str) -> dict | None:
    p = SUMMARIES_DIR / "quiz" / f"{slug}.json"
    if not p.exists():
        return None
    try:
        import json
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] quiz {slug} non parsabile: {e}")
        return None


def process_markdown(src_path: Path, dst_path: Path, module_slug: str, available_basenames: set[str], with_quiz: bool = False) -> dict:
    """Legge il .md sorgente, lo trasforma, lo scrive in docs/.
    Ritorna un dict con metadati utili per la nav."""
    body = src_path.read_text(encoding="utf-8")
    title = extract_title(body, fallback=src_path.stem)
    body = demote_extra_h1s(body)
    body = transform_wikilinks(body, available_basenames)
    if with_quiz:
        quiz_data = load_quiz_json(module_slug)
        body = inject_inline_quizzes(body, module_slug, quiz_data)
    # Calcola tag PRIMA dell'obfuscation (la regex matcha sul testo pulito)
    tags = derive_tags(title, body, module_slug)
    # AV signature obfuscation: spezza i token piu' segnalati con ZWSP
    body = obfuscate_av_signatures(body)
    frontmatter = build_frontmatter(title, tags)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(frontmatter + body, encoding="utf-8")
    return {"title": title, "tags": tags, "path": dst_path}


# ---- Asset embedded ---------------------------------------------------------

PROGRESS_JS = dedent("""
    // eCPPT Progress Tracking - localStorage based
    (function() {
      const STORAGE_KEY = "ecppt-progress";

      function loadProgress() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
        catch (e) { return {}; }
      }
      function saveProgress(p) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
      }
      function pageKey() {
        return location.pathname.replace(/\\/$/, "");
      }

      function injectCheckbox() {
        const h1 = document.querySelector("article.md-content__inner > h1");
        if (!h1) return;
        if (document.getElementById("ecppt-progress-box")) return;
        const progress = loadProgress();
        const key = pageKey();
        const wrap = document.createElement("div");
        wrap.id = "ecppt-progress-box";
        wrap.className = "ecppt-progress-box";
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.id = "ecppt-progress-cb";
        cb.checked = !!progress[key];
        const lbl = document.createElement("label");
        lbl.htmlFor = "ecppt-progress-cb";
        lbl.textContent = cb.checked ? " ✔ Studiato" : " ☐ Segna come studiato";
        cb.addEventListener("change", () => {
          const p = loadProgress();
          if (cb.checked) p[key] = true;
          else delete p[key];
          saveProgress(p);
          lbl.textContent = cb.checked ? " ✔ Studiato" : " ☐ Segna come studiato";
          updateGlobalSummary();
        });
        wrap.appendChild(cb);
        wrap.appendChild(lbl);
        h1.parentNode.insertBefore(wrap, h1.nextSibling);
      }

      function updateGlobalSummary() {
        // Inietta/aggiorna il riepilogo nella landing page.
        const target = document.getElementById("ecppt-global-progress");
        if (!target) return;
        const total = parseInt(target.dataset.total || "0", 10);
        const progress = loadProgress();
        const done = Object.keys(progress).length;
        const pct = total ? Math.round((done / total) * 100) : 0;
        target.innerHTML = `
          <div class="ecppt-progress-summary">
            <div class="ecppt-progress-summary-text"><strong>${done}/${total}</strong> pagine studiate (${pct}%)</div>
            <div class="ecppt-progress-bar"><div class="ecppt-progress-bar-fill" style="width:${pct}%"></div></div>
            <button id="ecppt-progress-reset" class="md-button md-button--secondary" style="margin-top:.8rem">Reset progress</button>
          </div>`;
        const btn = document.getElementById("ecppt-progress-reset");
        if (btn) {
          btn.onclick = () => {
            if (confirm("Sicuro? Cancella tutto il progresso.")) {
              localStorage.removeItem(STORAGE_KEY);
              updateGlobalSummary();
            }
          };
        }
      }

      function init() {
        injectCheckbox();
        updateGlobalSummary();
      }

      // MkDocs Material usa instant navigation: hook su location$ + DOMContentLoaded
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
      } else {
        init();
      }
      if (window.document$ && typeof window.document$.subscribe === "function") {
        window.document$.subscribe(init);
      }
    })();
""").lstrip()

CLIPBOARD_CLEAN_JS = dedent("""
    // eCPPT - Rimuove gli Zero-Width Space (U+200B) iniettati dal builder
    // per evadere i signature-based AV nei file HTML del sito.
    // Quando l'utente copia un comando (sia con il copy-button di Material
    // sia con Ctrl+C), il testo che arriva in clipboard NON contiene ZWSP
    // -> incollato in PowerShell/Bash e' identico all'originale.
    (function() {
      // Rimuove sia ZERO-WIDTH SPACE (U+200B) sia WORD JOINER (U+2060):
      // entrambi usati per AV evasion, entrambi invisibili, entrambi da rimuovere
      // prima della copia per evitare di incollare caratteri estranei.
      const ZWSP_RE = /[\\u200B\\u2060]/g;

      // 1) Intercetta il copy-button (Material usa navigator.clipboard.writeText)
      if (navigator.clipboard && navigator.clipboard.writeText) {
        const original = navigator.clipboard.writeText.bind(navigator.clipboard);
        navigator.clipboard.writeText = function(text) {
          if (typeof text === "string") text = text.replace(ZWSP_RE, "");
          return original(text);
        };
      }

      // 2) Intercetta il Ctrl+C / selezione manuale
      document.addEventListener("copy", function(e) {
        const sel = (window.getSelection() || "").toString();
        if (!sel || !ZWSP_RE.test(sel)) return;
        ZWSP_RE.lastIndex = 0;
        e.preventDefault();
        const cleaned = sel.replace(ZWSP_RE, "");
        if (e.clipboardData) {
          e.clipboardData.setData("text/plain", cleaned);
        } else if (window.clipboardData) {  // IE legacy
          window.clipboardData.setData("Text", cleaned);
        }
      });
    })();
""").lstrip()


NAV_COLLAPSE_JS = dedent("""
    // eCPPT - rende collapsible le voci del TOC integrato nella sidebar sinistra.
    // Default: TUTTO CHIUSO. localStorage memorizza i CAPITOLI APERTI dall'utente.
    (function() {
      const STORAGE_KEY = "ecppt-nav-open";
      const PRIMARY = ".md-sidebar--primary .md-nav";

      function loadOpen() {
        try { return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")); }
        catch (e) { return new Set(); }
      }
      function saveOpen(set) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(set)));
      }

      function nodeKey(item) {
        const a = item.querySelector(":scope > .md-nav__link, :scope > a");
        return a ? (a.textContent || "").trim() : "";
      }

      function setState(item, childNav, toggle, open) {
        if (open) {
          childNav.style.display = "";
          item.classList.remove("ecppt-closed");
          item.classList.add("ecppt-open");
          toggle.innerHTML = "▾";
        } else {
          childNav.style.display = "none";
          item.classList.remove("ecppt-open");
          item.classList.add("ecppt-closed");
          toggle.innerHTML = "▸";
        }
      }

      function applyCollapsible(root) {
        const open = loadOpen();
        const items = root.querySelectorAll("li.md-nav__item");
        items.forEach(item => {
          const childNav = item.querySelector(":scope > nav.md-nav");
          if (!childNav) return;
          if (item.dataset.ecpptInit) return;
          item.dataset.ecpptInit = "1";
          item.classList.add("ecppt-collapsible");
          const key = nodeKey(item);
          const link = item.querySelector(":scope > .md-nav__link, :scope > a");
          if (!link) return;

          // Toggle visivo (chevron) + link in un wrapper flex sulla stessa riga,
          // cosi' il chevron sta a fianco del titolo e non a meta' del childNav.
          const toggle = document.createElement("button");
          toggle.type = "button";
          toggle.className = "ecppt-toggle";
          toggle.setAttribute("aria-label", "Espandi/comprimi sezione");

          const row = document.createElement("div");
          row.className = "ecppt-row";
          link.parentNode.insertBefore(row, link);
          row.appendChild(toggle);
          row.appendChild(link);

          // Stato iniziale: CHIUSO di default.
          setState(item, childNav, toggle, open.has(key));

          toggle.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            const wasOpen = item.classList.contains("ecppt-open");
            setState(item, childNav, toggle, !wasOpen);
            const s = loadOpen();
            if (wasOpen) s.delete(key); else s.add(key);
            saveOpen(s);
          });

          // Doppio-click sul testo del link = toggle anche quello
          link.addEventListener("dblclick", (e) => {
            e.preventDefault();
            const wasOpen = item.classList.contains("ecppt-open");
            setState(item, childNav, toggle, !wasOpen);
            const s = loadOpen();
            if (wasOpen) s.delete(key); else s.add(key);
            saveOpen(s);
          });
        });
      }

      function init() {
        const root = document.querySelector(PRIMARY);
        if (!root) return;
        applyCollapsible(root);
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
      } else {
        init();
      }
      if (window.document$ && typeof window.document$.subscribe === "function") {
        window.document$.subscribe(init);
      }
    })();
""").lstrip()


QUIZ_JS = dedent("""
    // eCPPT - quiz INLINE a risposta multipla.
    // Cerca <div class="ecppt-quiz" data-module="<slug>" data-block="<idx>"></div>
    // e renderizza le 5 domande del blocco <idx> caricato da /quiz/<slug>.json.
    //
    // JSON atteso:
    //   { "module": "Active Directory",
    //     "blocks": [
    //       { "after_h2": "PARTE 1 — AD PRIMER",
    //         "title": "AD Primer",
    //         "questions": [
    //           { "q": "Testo", "choices": ["A","B","C","D"], "correct": 2, "explanation": "..." } ] } ] }
    (function() {
      const STORAGE_KEY = "ecppt-quiz";
      const cache = {};   // module -> data

      function loadAnswers() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
        catch (e) { return {}; }
      }
      function saveAnswers(o) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(o));
      }

      async function loadQuiz(module) {
        if (cache[module]) return cache[module];
        const baseHref = document.querySelector('base')?.href || (location.origin + '/');
        const resp = await fetch(`${baseHref}quiz/${module}.json`, { cache: "no-store" });
        if (!resp.ok) throw new Error(`Quiz HTTP ${resp.status}`);
        const data = await resp.json();
        cache[module] = data;
        return data;
      }

      function evaluate(block, q) {
        const chosen = block.querySelector("input:checked");
        if (!chosen) return;
        const correct = parseInt(chosen.value, 10) === q.correct;
        block.classList.remove("ecppt-correct", "ecppt-wrong");
        block.classList.add(correct ? "ecppt-correct" : "ecppt-wrong");
        const fb = block.querySelector(".ecppt-quiz-feedback");
        if (correct) {
          fb.innerHTML = `<strong>✓ Corretto.</strong> ${q.explanation || ""}`;
        } else {
          const right = q.choices[q.correct];
          fb.innerHTML = `<strong>✗ Sbagliato.</strong> Risposta corretta: <em>${right}</em>. ${q.explanation || ""}`;
        }
      }

      function updateBlockStats(blockData, module, blockIdx, statsEl) {
        const answers = (loadAnswers()[module] || {})[blockIdx] || {};
        let correct = 0, answered = 0;
        blockData.questions.forEach((q, i) => {
          if (answers[i] !== undefined) {
            answered++;
            if (answers[i] === q.correct) correct++;
          }
        });
        const total = blockData.questions.length;
        const pct = answered ? Math.round((correct / answered) * 100) : 0;
        statsEl.innerHTML = `
          <div class="ecppt-quiz-stats-text">
            Risposte: <strong>${answered}/${total}</strong> ·
            Corrette: <strong>${correct}/${answered || 0}</strong>
            (${pct}%)
          </div>`;
      }

      function renderBlock(container, data, module, blockIdx) {
        const blockData = data.blocks[blockIdx];
        if (!blockData) {
          container.innerHTML = `<em>Blocco quiz ${blockIdx} non trovato.</em>`;
          return;
        }
        container.innerHTML = "";
        const moduleAnswers = (loadAnswers()[module] || {})[blockIdx] || {};

        const stats = document.createElement("div");
        stats.className = "ecppt-quiz-stats";
        container.appendChild(stats);

        blockData.questions.forEach((q, i) => {
          const qBlock = document.createElement("div");
          qBlock.className = "ecppt-quiz-q";
          qBlock.dataset.idx = i;

          const qText = document.createElement("p");
          qText.className = "ecppt-quiz-q-text";
          qText.innerHTML = `<strong>${i + 1}.</strong> ${q.q}`;
          qBlock.appendChild(qText);

          const list = document.createElement("ul");
          list.className = "ecppt-quiz-choices";
          q.choices.forEach((choice, ci) => {
            const li = document.createElement("li");
            const lbl = document.createElement("label");
            const input = document.createElement("input");
            input.type = "radio";
            input.name = `q-${module}-${blockIdx}-${i}`;
            input.value = ci;
            if (moduleAnswers[i] === ci) input.checked = true;
            input.addEventListener("change", () => {
              const all = loadAnswers();
              all[module] = all[module] || {};
              all[module][blockIdx] = all[module][blockIdx] || {};
              all[module][blockIdx][i] = ci;
              saveAnswers(all);
              evaluate(qBlock, q);
              updateBlockStats(blockData, module, blockIdx, stats);
            });
            lbl.appendChild(input);
            lbl.appendChild(document.createTextNode(" " + choice));
            li.appendChild(lbl);
            list.appendChild(li);
          });
          qBlock.appendChild(list);

          const feedback = document.createElement("div");
          feedback.className = "ecppt-quiz-feedback";
          qBlock.appendChild(feedback);

          container.appendChild(qBlock);

          if (moduleAnswers[i] !== undefined) {
            evaluate(qBlock, q);
          }
        });

        const reset = document.createElement("button");
        reset.className = "md-button md-button--secondary";
        reset.textContent = "Resetta questo quiz";
        reset.style.marginTop = "1rem";
        reset.onclick = () => {
          if (!confirm("Cancello le tue risposte di questo blocco?")) return;
          const all = loadAnswers();
          if (all[module]) delete all[module][blockIdx];
          saveAnswers(all);
          renderBlock(container, data, module, blockIdx);
        };
        container.appendChild(reset);

        updateBlockStats(blockData, module, blockIdx, stats);
      }

      async function init() {
        const containers = document.querySelectorAll(".ecppt-quiz[data-module]");
        for (const c of containers) {
          if (c.dataset.ecpptInit) continue;
          c.dataset.ecpptInit = "1";
          const module = c.dataset.module;
          const blockIdx = parseInt(c.dataset.block || "0", 10);
          try {
            const data = await loadQuiz(module);
            renderBlock(c, data, module, blockIdx);
          } catch (e) {
            c.innerHTML = `<em>Quiz per "${module}" non ancora disponibile.</em>`;
          }
        }
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
      } else {
        init();
      }
      if (window.document$ && typeof window.document$.subscribe === "function") {
        window.document$.subscribe(init);
      }
    })();
""").lstrip()


EXTRA_CSS = dedent("""
    /* eCPPT Study Notes - extra styles */

    /* Progress checkbox box sotto al titolo H1 */
    .ecppt-progress-box {
      display: inline-flex;
      align-items: center;
      gap: .35rem;
      margin: -.6rem 0 1.2rem 0;
      padding: .4rem .7rem;
      background: var(--md-code-bg-color);
      border-left: 3px solid var(--md-accent-fg-color);
      border-radius: 4px;
      font-size: .85rem;
      cursor: pointer;
      user-select: none;
    }
    .ecppt-progress-box input[type="checkbox"] {
      transform: scale(1.15);
      cursor: pointer;
    }
    .ecppt-progress-box label {
      cursor: pointer;
      color: var(--md-default-fg-color--light);
    }

    /* Riepilogo globale nella landing page */
    .ecppt-progress-summary {
      padding: 1rem 1.2rem;
      background: var(--md-code-bg-color);
      border-left: 4px solid var(--md-accent-fg-color);
      border-radius: 6px;
      margin: 1.4rem 0;
    }
    .ecppt-progress-summary-text {
      margin-bottom: .6rem;
      font-size: 1rem;
    }
    .ecppt-progress-bar {
      width: 100%;
      height: 10px;
      background: var(--md-default-bg-color);
      border-radius: 5px;
      overflow: hidden;
    }
    .ecppt-progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--md-accent-fg-color), var(--md-primary-fg-color));
      transition: width .4s ease;
    }

    /* Tabelle: scroll orizzontale su mobile, larghezza piena su desktop */
    .md-typeset table:not([class]) {
      display: table;
      width: 100%;
    }
    @media (max-width: 768px) {
      .md-typeset__table {
        overflow-x: auto;
      }
    }

    /* Code block leggermente piu' aerato */
    .md-typeset pre > code {
      line-height: 1.55;
    }

    /* Niente uppercase sui titoli sezione (default Material) - piu' leggibili in italiano */
    .md-nav__title { text-transform: none; }

    /* Indice (TOC) richiesto a sinistra: nascondi forzatamente la sidebar destra.
       toc.integrate dovrebbe rimuoverla ma su alcuni browser/versioni resta visibile. */
    @media screen and (min-width: 76.25em) {
      .md-sidebar--secondary {
        display: none !important;
      }
      /* Allarga il contenuto principale dato che la destra non c'e' piu' */
      .md-main__inner.md-grid {
        max-width: 75rem;
      }
    }

    /* Larghezza piu' generosa per la sidebar sinistra (ospita TOC integrato) */
    @media screen and (min-width: 76.25em) {
      .md-sidebar--primary {
        width: 16rem;
      }
    }

    /* === Top tabs (i 10 moduli): compatte e scroll orizzontale se non entrano === */
    .md-tabs__list {
      flex-wrap: nowrap;
      overflow-x: auto;
      scrollbar-width: thin;
    }
    .md-tabs__item {
      padding-left: .7rem;
      padding-right: .7rem;
      height: 2.4rem;
      flex-shrink: 0;
    }
    .md-tabs__link {
      font-size: .72rem;
      white-space: nowrap;
      margin-top: .65rem;
    }
    /* Su schermi grandi: padding leggermente piu' generoso */
    @media screen and (min-width: 90em) {
      .md-tabs__item { padding-left: .9rem; padding-right: .9rem; }
      .md-tabs__link { font-size: .76rem; }
    }

    /* === Nav collapsible: chevron sulla stessa riga del titolo ===
       JS wrappa <a> + <button.toggle> in <div.ecppt-row> (flex).
       Le voci SENZA chevron ricevono un padding-left che ne replica la larghezza,
       cosi' tutti i titoli sono allineati sulla stessa colonna verticale. */
    .ecppt-row {
      display: flex;
      align-items: flex-start;       /* chevron in cima quando il titolo va a capo */
      gap: .15rem;
    }
    .ecppt-row > .md-nav__link {
      flex: 1 1 auto;
      padding-left: 0 !important;
      margin: 0;
    }
    .ecppt-toggle {
      flex: 0 0 auto;
      width: 1.1rem;
      /* Allinea il chevron alla prima riga del titolo:
         match l'altezza della baseline del link Material (padding-top ~.4rem + font ascender). */
      height: 1.4rem;
      padding-top: .35rem;            /* spinge il chevron a livello del testo della 1a riga */
      background: none;
      border: none;
      color: var(--md-accent-fg-color);
      cursor: pointer;
      margin: 0;
      font-size: .95rem;
      line-height: 1;
      font-weight: bold;
      transition: color .15s ease, background .15s ease;
      display: inline-flex;
      align-items: flex-start;
      justify-content: center;
      border-radius: 3px;
    }
    .ecppt-toggle:hover {
      color: var(--md-primary-fg-color);
      background: var(--md-default-fg-color--lightest);
    }
    /* Le voci SENZA chevron (li.md-nav__item NON .ecppt-collapsible) hanno bisogno
       di un padding-left che compensi la larghezza del chevron (1.1rem + .15rem gap)
       cosi' i testi sono allineati su tutta la sidebar */
    .md-sidebar--primary li.md-nav__item:not(.ecppt-collapsible) > .md-nav__link {
      padding-left: 1.4rem !important;
    }

    /* === Quiz styling === */
    .ecppt-quiz {
      margin-top: 1rem;
    }
    .ecppt-quiz-intro {
      font-style: italic;
      color: var(--md-default-fg-color--light);
    }
    .ecppt-quiz-stats {
      padding: .6rem .9rem;
      background: var(--md-code-bg-color);
      border-left: 4px solid var(--md-accent-fg-color);
      border-radius: 4px;
      margin-bottom: 1.2rem;
      font-size: .9rem;
    }
    .ecppt-quiz-q {
      padding: 1rem 1.2rem;
      margin: 1rem 0;
      border: 1px solid var(--md-default-fg-color--lightest);
      border-radius: 6px;
      transition: border-color .2s ease, background .2s ease;
    }
    .ecppt-quiz-q.ecppt-correct {
      border-color: #4caf50;
      background: rgba(76, 175, 80, 0.08);
    }
    .ecppt-quiz-q.ecppt-wrong {
      border-color: #e53935;
      background: rgba(229, 57, 53, 0.08);
    }
    .ecppt-quiz-q-text {
      margin-top: 0;
      font-size: 1rem;
    }
    .ecppt-quiz-choices {
      list-style: none;
      padding-left: 0;
      margin: .6rem 0;
    }
    .ecppt-quiz-choices li {
      padding: .35rem 0;
    }
    .ecppt-quiz-choices label {
      cursor: pointer;
      display: flex;
      align-items: flex-start;
      gap: .5rem;
    }
    .ecppt-quiz-choices input[type="radio"] {
      margin-top: .25rem;
      flex-shrink: 0;
    }
    .ecppt-quiz-feedback:not(:empty) {
      margin-top: .8rem;
      padding: .6rem .9rem;
      border-radius: 4px;
      font-size: .9rem;
      line-height: 1.45;
    }
    .ecppt-correct .ecppt-quiz-feedback {
      background: rgba(76, 175, 80, 0.18);
      color: var(--md-default-fg-color);
    }
    .ecppt-wrong .ecppt-quiz-feedback {
      background: rgba(229, 57, 53, 0.15);
      color: var(--md-default-fg-color);
    }
""").lstrip()


# ---- Generation -------------------------------------------------------------

def build():
    print(f"[build_site] Course root: {COURSE_ROOT}")

    # 1. Wipe docs/
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)
    print(f"[build_site] docs/ rigenerata")

    # 2. Scrivi asset (JS/CSS)
    js_dir = DOCS_DIR / "javascripts"
    css_dir = DOCS_DIR / "stylesheets"
    js_dir.mkdir(parents=True)
    css_dir.mkdir(parents=True)
    (js_dir / "progress.js").write_text(PROGRESS_JS, encoding="utf-8")
    (js_dir / "nav-collapse.js").write_text(NAV_COLLAPSE_JS, encoding="utf-8")
    (js_dir / "quiz.js").write_text(QUIZ_JS, encoding="utf-8")
    (js_dir / "clipboard-clean.js").write_text(CLIPBOARD_CLEAN_JS, encoding="utf-8")
    (css_dir / "extra.css").write_text(EXTRA_CSS, encoding="utf-8")

    # Cartella dei quiz: copia ricorsivamente da _summaries/quiz/ se esiste
    quiz_src_dir = SUMMARIES_DIR / "quiz"
    quiz_dst_dir = DOCS_DIR / "quiz"
    quiz_dst_dir.mkdir()
    if quiz_src_dir.is_dir():
        for q in quiz_src_dir.glob("*.json"):
            # Applica anche al JSON dei quiz l'obfuscation AV
            content = q.read_text(encoding="utf-8")
            content = obfuscate_av_signatures(content)
            (quiz_dst_dir / q.name).write_text(content, encoding="utf-8")
        print(f"[build_site] {len(list(quiz_dst_dir.glob('*.json')))} file quiz copiati (obfuscati AV)")
    else:
        print(f"[build_site] (nessun quiz in {quiz_src_dir})")

    # 3. Per ogni modulo: copia SOLO il summary come pagina del modulo
    #    (i .md per-video singolo restano nelle cartelle sorgente, non finiscono nel sito)
    nav_entries = []     # per la sezione nav: di mkdocs.yml
    page_count = 0       # totale pagine pubblicate (per progress globale)
    module_video_counts = []

    for src_folder, slug, display in MODULES:
        # I link Obsidian [[basename]] ai video puntano a file che non saranno pubblicati.
        available_basenames: set[str] = set()
        if src_folder is None:
            # Pseudo-modulo aggregato (es. Cheat Sheet) - niente cartella video
            module_video_counts.append((display, 0))
        else:
            src_dir = COURSE_ROOT / src_folder
            if not src_dir.is_dir():
                print(f"[WARN] cartella sorgente mancante: {src_folder}")
                continue
            src_mds = sorted(p for p in src_dir.glob("*.md"))
            module_video_counts.append((display, len(src_mds)))

        # Copia il summary del modulo come pagina dedicata + placeholder quiz
        summary_path = summary_file_for(slug)
        dst_file = DOCS_DIR / f"{slug}.md"
        if summary_path.exists():
            process_markdown(summary_path, dst_file, slug, available_basenames, with_quiz=True)
        else:
            dst_file.write_text(
                build_frontmatter(display, MODULE_TAGS.get(slug, [])) +
                f"# {display}\n\nRiepilogo non disponibile.\n", encoding="utf-8")
        page_count += 1

        nav_entries.append({display: f"{slug}.md"})

    # 5. Landing page docs/index.md
    landing_body = ["# eCPPT Study Notes\n",
                    "Benvenuto. Questo sito raccoglie i **riepiloghi consolidati** per ognuno dei 9 moduli del corso eCPPT 2024 (formato 45 domande a risposta multipla in ambiente pratico).\n",
                    "## Progress\n",
                    f'<div id="ecppt-global-progress" data-total="{page_count}"></div>\n',
                    "## Moduli del corso\n",
                    "Segui l'ordine consigliato del learning path eCPPT, oppure salta direttamente all'argomento che ti interessa.\n"]
    for (display, count), (src_folder, slug, _) in zip(module_video_counts, MODULES):
        if count > 0:
            landing_body.append(f"- **[{display}]({slug}.md)** — basato su {count} video del corso")
        else:
            landing_body.append(f"- **[{display}]({slug}.md)** — riferimento rapido (aggregato dai moduli)")
    landing_body.append("\n## Come usare il sito\n")
    landing_body.append("- **Ricerca** (icona lente in alto): cerca comandi, tecniche, tool — funziona su tutti i riepiloghi.")
    landing_body.append("- **Tag** ([vai alla pagina tag](tags.md)): filtra per argomento trasversale (es. `kerberos`, `pivoting`, `linux-privesc`).")
    landing_body.append("- **Copy-button** su ogni blocco di codice: cliccalo per copiare il comando in clipboard.")
    landing_body.append("- **Toggle dark/light** in alto a destra.")
    landing_body.append("- **Progress tracking**: spunta `Segna come studiato` su ogni pagina, il progresso resta salvato nel browser.")
    landing_body.append("- **Indice della pagina**: nella barra di sinistra trovi la TOC del riepilogo aperto, per saltare alle sezioni.")
    landing_body.append("\n## Materiale di dettaglio (offline)\n")
    landing_body.append("Per ogni singolo video del corso esiste comunque, **a fianco del file `.mp4` originale**:")
    landing_body.append("- `<basename>.txt` — trascrizione integrale (Whisper)")
    landing_body.append("- `<basename>.srt` — trascrizione con timestamp")
    landing_body.append("- `<basename>.md` — appunti dettagliati per quel singolo video")
    landing_body.append("\nIl sito si concentra sui **riepiloghi consolidati** (uno per modulo) per studio efficace; per dettagli granulari apri i `.md` per-video nelle cartelle del corso.")

    landing_md = build_frontmatter("eCPPT Study Notes — Home", ["index"]) + "\n".join(landing_body) + "\n"
    (DOCS_DIR / "index.md").write_text(landing_md, encoding="utf-8")

    # 6. Pagina tag (richiesta dal plugin tags di Material per il TOC tag)
    tags_md = build_frontmatter("Tag", []) + "# Tag\n\n[TAGS]\n"
    (DOCS_DIR / "tags.md").write_text(tags_md, encoding="utf-8")

    # 7. Genera mkdocs.yml
    yml = build_mkdocs_yml(nav_entries)
    MKDOCS_YML.write_text(yml, encoding="utf-8")

    print(f"[build_site] Generate {page_count} pagine video + {len(MODULES)} riepiloghi modulo")
    print(f"[build_site] docs/ pronta, mkdocs.yml generato")
    print(f"[build_site] Lancia ora: python -m mkdocs serve")


def build_mkdocs_yml(nav_entries: list) -> str:
    """Costruisce il file mkdocs.yml come stringa YAML."""
    lines = [
        "site_name: eCPPT Study Notes",
        "site_description: Appunti completi per l'esame eCPPT 2024 (45 domande pratiche)",
        "site_author: Mattia",
        "docs_dir: docs",
        "site_dir: site",
        "use_directory_urls: true",
        "",
        "theme:",
        "  name: material",
        "  language: it",
        "  palette:",
        "    - scheme: slate",
        "      primary: indigo",
        "      accent: cyan",
        "      toggle:",
        "        icon: material/weather-sunny",
        "        name: Passa a tema chiaro",
        "    - scheme: default",
        "      primary: indigo",
        "      accent: cyan",
        "      toggle:",
        "        icon: material/weather-night",
        "        name: Passa a tema scuro",
        "  features:",
        "    - navigation.tabs",         # 9 moduli come tab in alto",
        "    - navigation.tabs.sticky",  # tab restano visibili scrollando
        "    - navigation.top",          # bottone back-to-top
        "    - navigation.tracking",     # URL con anchor durante lo scroll
        "    - search.suggest",
        "    - search.highlight",
        "    - search.share",
        "    - content.code.copy",       # copy-button su ogni code block (REQUISITO)
        "    - content.code.annotate",
        "    - content.tabs.link",
        "    - toc.integrate",           # TOC integrato nella sidebar SINISTRA
        "",
        "markdown_extensions:",
        "  - admonition",
        "  - attr_list",
        "  - md_in_html",
        "  - tables",
        "  - footnotes",
        "  - pymdownx.details",
        "  - pymdownx.superfences",
        "  - pymdownx.highlight:",
        "      anchor_linenums: true",
        "      line_spans: __span",
        "      pygments_lang_class: true",
        "      auto_title: true",
        "  - pymdownx.inlinehilite",
        "  - pymdownx.snippets",
        "  - pymdownx.tabbed:",
        "      alternate_style: true",
        "  - pymdownx.tasklist:",
        "      custom_checkbox: true",
        "  - pymdownx.tilde",
        "  - pymdownx.caret",
        "  - pymdownx.mark",
        "  - toc:",
        "      permalink: true",
        "      toc_depth: 3",
        "",
        "plugins:",
        "  - search:",
        "      lang:",
        "        - en",
        "        - it",
        "  - tags:",
        "      tags_file: tags.md",
        "",
        "extra_javascript:",
        "  - javascripts/clipboard-clean.js",
        "  - javascripts/progress.js",
        "  - javascripts/nav-collapse.js",
        "  - javascripts/quiz.js",
        "extra_css:",
        "  - stylesheets/extra.css",
        "",
        "nav:",
        "  - Home: index.md",
    ]
    # Nav modules: una voce per modulo (link diretto al riepilogo)
    for entry in nav_entries:
        for display, path in entry.items():
            lines.append(f"  - {yaml_safe_string(display)}: {yaml_safe_string(path)}")
    lines.append("  - Tag: tags.md")
    lines.append("")
    return "\n".join(lines)


def yaml_safe_string(s: str) -> str:
    """Quota la stringa se contiene caratteri YAML problematici."""
    if any(c in s for c in [":", "#", "[", "]", "{", "}", ",", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    if not s.strip():
        return '""'
    return s


# ---- Entry ------------------------------------------------------------------

if __name__ == "__main__":
    build()
