# Seeding a series

`memory.json` is the whole world. The model reads it as text every run (see `python recurse.py memory`),
draws from it, and writes back into it. To start your own series you replace the seed; the machinery
stays. This file says what each field is for, what the code does with it, and how to write it.

Reset the world with a fresh file (keep the shape below), archive `out/` (the first series lives
in `seeds/observed-series/`, memory and images together), set
`series_number` to 0, and run. Roman numerals come from `series_number + 1`.

## Shape

```json
{
 "series_number": 0,
 "story": "...",
 "voices": {"first": "...", "second": "..."},
 "motifs": [{"name": "...", "note": "...", "state": "open", "seen_in": []}],
 "open_lines": ["...", "...", "..."],
 "vocabulary": [],
 "entries": []
}
```

## story (one paragraph, under 700 characters to start)

What the model reads as "what has happened so far". Each run appends the entry's `story_beat`
and keeps only the **last 1200 characters**, so the opening erodes after four or five entries.
Write it so the sentence that matters most can survive being the only one left: a concrete
situation with objects in it, not a theme. Name the objects that will become motifs.

Bad: "A series about giving without being asked."
Good: "A ledger kept accounts of sure promotion and withheld permission to open, five times; a
leaf turned toward it and opened anyway."

## voices (two, one sentence each)

The engine of the series. The first voice makes the document; the second corrects it in the
margin. Each description should fix four things: **what kind of speaker** (an instrument, an
inspector, a clerk), **how it writes** (registers, ranks, maxims in caps), **what it refuses**
(permission without return), and **its ink** (a palette name). The second voice needs its
colour, its register (terse, plain, a little tender), and two or three sample lines the model
can imitate: `'it opened without you.'`, `'asked? no.'`. The samples matter more than the adjectives.

## motifs (six to ten to start)

Objects, not ideas. Each has a `name` the model will reuse **verbatim** as a key (keep names
short and distinctive: `the lead line`, `curd retained`, `DESERVED (struck)`), a `note` that says
what it is and where it came from, a `state`, and `seen_in`.

- `open`: a debt. The next entry owes it an appearance. Start most motifs here.
- `carried`: has appeared and must keep appearing, small and labelled, before the new entry
  does anything else.
- `resolved`: closed; may still be drawn but nothing is owed.

Motifs are never pruned by the code. If a motif should die, resolve it by hand. A good seed mixes:
two or three physical objects with a measurement attached (a weight, an angle, a count), one
struck word (a verdict the second hand has cancelled and that must stay struck), one gesture
(a head inclining, a hand turning a page), and one unanswered question in the second hand's voice.
The trade jargon that carries a double meaning belongs in the notes.

## open_lines (exactly three)

Phrases the last image left hanging: a question, a half sentence, a measurement without a verdict.
They are **replaced wholesale** every run by the reflect step, so anything you want to persist
must also be a motif. Write them as the second hand would: under eight words, lowercase, plain.

## vocabulary (start empty, or list what you have already used)

Trades already used, so the model rhymes with or avoids them. Each entry chooses one trade whose
jargon will be the document's language. Filling it in advance is a way to steer: list the trades
you do *not* want revisited.

## palette (in `lib/canvas.py`, `PALETTE`)

The model names colours from this dict in the `sub2` line of every entry, so names are part of
the poem. Rules that have worked:

- Paper first: one light paper and one dark, plus a slightly darker paper for washes
  (`vellum`, `black`, `paper_dark`).
- Ink and a faint ink for rules and struck text (`ink`, `ink_light`).
- One colour for the second hand, and a brighter variant for dark paper (`cobalt`, `cobalt_bright`).
- Two texture families of three related tones each (earths, greens), and one accent
  that appears rarely (`scarlet`).
- Names are nouns from the world of the story, never `blue` or `red`. Twelve to twenty entries.

Changing the palette does not change the drawing primitives; those are the Canvas methods, and
the model gets their docstrings as its API each run.

## forms and rules (in `lib/agent.py`)

`FORMS` is five one-line descriptions. Each run must use a form other than the previous entry's.
A form line should name the paper, the dominant structure, and two or three required parts.
The previous entry's PNG and code are also shown to the drawing step, so the strongest way to
fix a form is to hand-draw one good example and let the series inherit from it.

`STYLE` holds the standing rules (two voices, jargon with a human double meaning, quantities
required, annotations name and never interpret, banned words). Edit it when the series drifts.

## entries

Leave empty for a fresh series. To import pieces made elsewhere, add records with
`"file": "observed"`; they will count in the numbering but no image exists for the drawing step
to inherit from, so the first generated entry has only the text to go on.
