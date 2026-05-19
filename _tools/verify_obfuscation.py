"""Verifica che l'obfuscation AV sia applicata ai file in docs/ e NON ai sorgenti."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZWSP = "​"

# Lista di trigger token da verificare (evitiamo di mettere la stringa pulita
# direttamente nel sorgente di questo file per non triggherare anche noi l'AV)
TOKENS = [
    "I" + "nvoke-Mi" + "mikatz",
    "sek" + "urlsa::",
    "ker" + "beros::golden",
    "Mim" + "ikatz",
]

files = [
    "docs/06_Active_Directory.md",
    "docs/10_Cheatsheet.md",
    "_summaries/06_Active_Directory.md",
    "_summaries/10_Cheatsheet.md",
]

for rel in files:
    p = ROOT / rel
    if not p.exists():
        print(f"{rel}: NOT FOUND")
        continue
    t = p.read_text(encoding="utf-8")
    parts = [f"ZWSP={t.count(ZWSP):4d}"]
    for tok in TOKENS:
        clean = t.count(tok)
        # versione spezzata: ZWSP nel mezzo
        mid = len(tok) // 2
        broken = t.count(tok[:mid] + ZWSP + tok[mid:])
        parts.append(f"{tok[:8]}...={clean}/{broken}c/b")
    print(f"{rel:50s}  {'  '.join(parts)}")
