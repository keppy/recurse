# recurse

A numbered visual series that remembers itself. Each run: the model reads the
motif memory, picks a document form, writes Python against a small canvas
library, the code is executed, the model looks at the rendered image and
writes the caption, alt text, and the memory update the next entry inherits.

```
pip install -r requirements.txt
cp .env.example .env                 # then put ANTHROPIC_API_KEY in .env (gitignored)
python recurse.py run                # one entry → out/NN_ROMAN_title.{png,md,py}
python recurse.py run --form plan_view
python recurse.py run --offline      # exercise the pipeline with fixtures/, no key
python recurse.py memory             # what the model reads next time
python recurse.py api                # the canvas API the model is handed
```

## Setup notes

- Config comes from `.env` next to `recurse.py` (or the environment, which wins): `ANTHROPIC_API_KEY`,
  `RECURSE_MODEL` (default `claude-sonnet-5`), `RECURSE_FONT_DIR` (only if DejaVu is somewhere unusual).
- Runs on Linux, macOS and Windows. Fonts: DejaVu Sans / Mono / Serif are searched in the standard
  system font directories; if none are found the canvas falls back to Pillow's default face rather than crashing.
- All file IO is UTF-8 regardless of locale (captions and drawing code carry → ≈ ° § №).
- `--offline` re-renders the XVII fixture as the next entry number and appends it to `memory.json`.
  Use `--memory` / `--out` to point at scratch copies if you only want to smoke-test the pipeline.

## Starting your own series

See [SEEDING.md](SEEDING.md): what each field of `memory.json` is for, what the code does with it, and how to write the story kernel, the two voices, the seed motifs, the open lines, and the palette.

## Pieces

- `memory.json` — the store. Motifs with states (open / carried / resolved), open
  lines the next entry owes an answer to, trades used, one record per entry.
  Seeded from the four observed posts (PROMOTION LEDGER, COURSE OF READING, XIV, XVI).
- `lib/canvas.py` — Pillow drawing library: vellum/black paper, ruled ledger lines,
  short-segment hatch clipped to polygons, blobs, textured bands and frames,
  struck text, cobalt annotations, a monospace `Panel` for the terminal-ledger form.
  `api_reference()` renders its own docstrings into the prompt.
- `lib/agent.py` — three model calls per cycle (plan → draw → reflect). The draw step is shown the previous entry's PNG and code. Drawing
  code that raises is sent back with the traceback, up to 3 attempts. The reflect
  step sees the PNG, so continuity is over images, not intentions.
- `fixtures/` — a hand-written stand-in cycle (XVII, a survey sheet) for `--offline`.

## Decisions

- Forms alternate; the previous entry's form is excluded.
- Every entry must draw its carried motifs first, small and labelled.
- Struck words stay struck. Banned words: love, grace, kindness, gratitude, heart, forgiveness.
- The model names its palette in the subline and the caption comes from looking at the result.
- Posting is not wired. Outputs are files; add your own publisher.
