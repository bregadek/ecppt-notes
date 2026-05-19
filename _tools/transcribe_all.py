"""
Trascrive tutti i video .mp4 del corso eCPPT usando faster-whisper su GPU.

Convenzioni:
- Output .txt e .srt accanto al video, stesso basename.
- Idempotente: salta video gia trascritti.
- Manifest JSON in _tools/manifest.json.
- Log in _tools/transcribe.log.
- Cartelle in EXCLUDE_DIRS sono saltate per intero.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

# ---- Configurazione ----------------------------------------------------------

COURSE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = COURSE_ROOT / "_tools"
MANIFEST_PATH = TOOLS_DIR / "manifest.json"
LOG_PATH = TOOLS_DIR / "transcribe.log"

# Cartelle da NON trascrivere (richiesta utente)
EXCLUDE_DIRS = {
    "Web Application Penetration Testing",
    "_tools",
}

MODEL_NAME = "large-v3"
LANGUAGE = "en"
COMPUTE_TYPE = "float16"   # RTX 3060 12GB regge senza problemi
DEVICE = "cuda"
BEAM_SIZE = 5
VAD_FILTER = True          # silenzi tagliati -> piu veloce e meno allucinazioni

# Path a ffmpeg installato via winget (Gyan.FFmpeg). Aggiunto a PATH in-process.
FFMPEG_BIN = Path(
    r"C:\Users\Mattia\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin"
)

# ---- Setup -------------------------------------------------------------------

TOOLS_DIR.mkdir(exist_ok=True)

if FFMPEG_BIN.exists():
    os.environ["PATH"] = str(FFMPEG_BIN) + os.pathsep + os.environ.get("PATH", "")

# CTranslate2 (sotto faster-whisper) cerca cuBLAS/cuDNN nel PATH di sistema.
# Le DLL CUDA sono installate dai pacchetti nvidia-cublas-cu12 e nvidia-cudnn-cu12
# dentro il venv. Le rendiamo visibili al loader DLL di Windows.
_VENV_SITE_PACKAGES = Path(sys.executable).parent.parent / "Lib" / "site-packages"
for _sub in ("cublas/bin", "cudnn/bin", "cuda_nvrtc/bin"):
    _p = _VENV_SITE_PACKAGES / "nvidia" / _sub
    if _p.exists():
        os.environ["PATH"] = str(_p) + os.pathsep + os.environ["PATH"]
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(_p))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("transcribe")


# ---- Helpers -----------------------------------------------------------------

def discover_videos(root: Path) -> list[Path]:
    """Trova tutti gli .mp4 sotto root, escludendo EXCLUDE_DIRS."""
    videos: list[Path] = []
    for p in root.rglob("*.mp4"):
        rel_parts = p.relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        videos.append(p)
    return sorted(videos)


def format_timestamp(seconds: float) -> str:
    """Formato SRT: HH:MM:SS,mmm"""
    ms = int(round(seconds * 1000))
    hh, ms = divmod(ms, 3_600_000)
    mm, ms = divmod(ms, 60_000)
    ss, ms = divmod(ms, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def write_outputs(segments: list, txt_path: Path, srt_path: Path) -> str:
    """Scrive il file .txt (testo piano) e .srt (con timestamp). Ritorna il testo piano."""
    text_lines: list[str] = []
    srt_lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        text = seg.text.strip()
        if not text:
            continue
        text_lines.append(text)
        srt_lines.append(str(i))
        srt_lines.append(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}")
        srt_lines.append(text)
        srt_lines.append("")
    full_text = "\n".join(text_lines)
    txt_path.write_text(full_text + "\n", encoding="utf-8")
    srt_path.write_text("\n".join(srt_lines) + "\n", encoding="utf-8")
    return full_text


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.warning("Manifest corrotto, lo ricreo da zero")
    return {"version": 1, "entries": {}}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---- Core --------------------------------------------------------------------

def transcribe_one(model, video: Path) -> dict:
    """Trascrive un singolo video. Ritorna metadati per il manifest."""
    txt_path = video.with_suffix(".txt")
    srt_path = video.with_suffix(".srt")
    t0 = time.time()

    segments_iter, info = model.transcribe(
        str(video),
        language=LANGUAGE,
        beam_size=BEAM_SIZE,
        vad_filter=VAD_FILTER,
        condition_on_previous_text=False,  # riduce allucinazioni a catena
    )
    # Materializza il generator (whisper streamma)
    segments = list(segments_iter)
    text = write_outputs(segments, txt_path, srt_path)

    elapsed = time.time() - t0
    duration = info.duration if info and info.duration else 0.0
    rtf = elapsed / duration if duration else 0.0
    log.info(
        "OK %s | dur=%.1fs | elapsed=%.1fs | rtf=%.2fx | chars=%d",
        video.relative_to(COURSE_ROOT),
        duration,
        elapsed,
        rtf,
        len(text),
    )
    return {
        "txt": str(txt_path.relative_to(COURSE_ROOT)),
        "srt": str(srt_path.relative_to(COURSE_ROOT)),
        "duration_sec": duration,
        "elapsed_sec": elapsed,
        "language": info.language if info else LANGUAGE,
        "lang_prob": info.language_probability if info else None,
        "chars": len(text),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Trascrive solo il file il cui path relativo contiene questa stringa")
    parser.add_argument("--limit", type=int, default=0, help="Numero massimo di video da trascrivere (0 = tutti)")
    parser.add_argument("--force", action="store_true", help="Ritrascrive anche se .txt esiste gia")
    args = parser.parse_args()

    log.info("Course root: %s", COURSE_ROOT)
    log.info("Modello: %s | device=%s | compute=%s | lang=%s", MODEL_NAME, DEVICE, COMPUTE_TYPE, LANGUAGE)
    log.info("Esclusioni: %s", ", ".join(sorted(EXCLUDE_DIRS)))

    videos = discover_videos(COURSE_ROOT)
    if args.only:
        needle = args.only.lower().replace("\\", "/")
        videos = [v for v in videos if needle in v.as_posix().lower()]
    log.info("Video totali da considerare: %d", len(videos))

    manifest = load_manifest()

    # Filtra i gia fatti (a meno di --force)
    to_do: list[Path] = []
    for v in videos:
        rel = str(v.relative_to(COURSE_ROOT))
        txt_exists = v.with_suffix(".txt").exists()
        if not args.force and txt_exists:
            log.debug("SKIP gia trascritto: %s", rel)
            continue
        to_do.append(v)

    if args.limit:
        to_do = to_do[: args.limit]

    log.info("Video da trascrivere in questo run: %d", len(to_do))
    if not to_do:
        log.info("Nulla da fare.")
        return 0

    # Caricamento modello solo se serve
    log.info("Caricamento modello %s...", MODEL_NAME)
    from faster_whisper import WhisperModel
    model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
    log.info("Modello pronto.")

    failures: list[tuple[Path, str]] = []
    for i, video in enumerate(to_do, start=1):
        rel = str(video.relative_to(COURSE_ROOT))
        log.info("[%d/%d] %s", i, len(to_do), rel)
        try:
            meta = transcribe_one(model, video)
            manifest["entries"][rel] = meta
            save_manifest(manifest)
        except Exception as e:
            log.exception("FAIL %s: %s", rel, e)
            failures.append((video, str(e)))

    log.info("Done. Successi=%d  Fallimenti=%d", len(to_do) - len(failures), len(failures))
    for v, err in failures:
        log.error("  - %s : %s", v.relative_to(COURSE_ROOT), err)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
