#!/usr/bin/env python3
"""
recurse — a numbered visual series that remembers itself.

  python recurse.py run              one cycle: plan → draw → render → reflect → remember
  python recurse.py run --offline    same pipeline, model calls replaced by fixtures/ (no API key needed)
  python recurse.py run --form map_sheet
  python recurse.py memory           print what the model will read next time
  python recurse.py api              print the canvas API the model is handed

Env: ANTHROPIC_API_KEY (required for real runs), RECURSE_MODEL (default claude-sonnet-5),
     RECURSE_FONT_DIR (optional: directory holding the DejaVu .ttf files).
     A `.env` file next to this script is loaded first; see .env.example.
Posting is deliberately not wired: outputs land in out/ as .png + .md (caption, alt) + .py (the code that drew it).
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def load_env(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE lines, # comments, optional quotes. Never overrides a variable already set."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().removeprefix("export ").strip(); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in (chr(34), chr(39)):
            v = v[1:-1]
        if k and k not in os.environ:
            os.environ[k] = v


load_env(ROOT / ".env")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # captions carry → ≈ ° №; Windows consoles default to cp1252

from lib.memory import Memory
from lib import agent, canvas

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--offline", action="store_true"); r.add_argument("--form", choices=list(agent.FORMS))
    r.add_argument("--memory", default=str(ROOT / "memory.json")); r.add_argument("--out", default=str(ROOT / "out"))
    m = sub.add_parser("memory"); m.add_argument("--memory", default=str(ROOT / "memory.json"))
    sub.add_parser("api")
    a = ap.parse_args()

    if a.cmd == "api":
        print(canvas.api_reference()); return
    mem = Memory(a.memory)
    if a.cmd == "memory":
        print(mem.as_text()); return
    result = agent.run_cycle(mem, Path(a.out), offline=a.offline, form=a.form)
    print(f"\n{result['plan']['roman']} / {result['plan']['title']}\n\n{result['caption']}\n\nalt: {result['alt']}\n\n→ {result['png']}")

if __name__ == "__main__":
    main()
