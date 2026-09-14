"""
agent.py — one cycle of the series.

  plan     : read memory → choose a form, decide which motifs to carry, resolve, introduce
  draw     : write `draw(c, P)` against the canvas API → exec → retry on traceback
  reflect  : look at the rendered PNG → final caption, alt text, memory update

Each stage is a separate model call so the model sees its own output the way a
reader would (the recursion is over images, not over intentions).
"""
from __future__ import annotations
import base64, json, os, re, textwrap, traceback, types
from pathlib import Path

import anthropic

from . import canvas as canvaslib
from .memory import Memory

MODEL = os.environ.get("RECURSE_MODEL", "claude-sonnet-5")
ROOT = Path(__file__).resolve().parent.parent

STYLE = """
You are the drawing hand of a numbered visual series. Read the memory carefully: it is
the only continuity the series has. Rules the series has kept so far:

- Two voices. The first voice is an instrument: it keeps accounts, ranks, prescribes,
  permits nothing without guaranteed return. It writes in the paper's ink (or umber on
  black). The second hand annotates in cobalt: short, plain, sometimes a question,
  always correcting the first voice or naming what it left out.
- Every image is a document from one trade (bookbinding, intaglio, cartography,
  botany plates, bell-founding...) whose jargon carries a human double meaning. The
  reader decodes the story from the accounting; the theme is never stated.
- Motifs recur literally: an object from an earlier piece appears again, small and
  labelled, before the new piece does anything else. Struck-through words stay struck.
- Forms alternate. Do not use the form used by the previous entry.
- Typography: DejaVu Sans, sentence case labels 'a / cut edge', a heading
  'XVII / TITLE IN CAPS', small sublines, ruled ledger paper or textured frames.
  Textures are short random line segments, never gradients.
- The drawing is the document; text is subordinate to it. Labels are 12-14 px,
  annotations 13-14 px, the verdict at most 18 px, the struck word at most 16 px.
  Nothing else is large except the heading. No boxes or highlights behind text
  outside a terminal Panel.
- Every document counts something. It carries real quantities with units, scales,
  numbered stations, sections a/ b/ c/, weights, degrees, dates, folios: the
  accounting is where the story hides. A bar or a column that measures nothing is
  a flaw.
- The second hand names things; it never interprets them. 'wet.' 'asked? no.'
  '0.4 g still listed.' are right. 'the wet was never water, it was tone' is wrong:
  it explains the metaphor, and the metaphor is never explained. Keep each note
  to four words or fewer and place it on the thing it comments on.
- Never repeat a line. The verdict appears once; each second-hand note once.
- Never write the words love, grace, kindness, gratitude, heart, or forgiveness.
""".strip()

FORMS = {
    "terminal_ledger": "black paper, one large monospace Panel with three columns, hatched bars, a highlighted verdict, a cobalt margin column",
    "route_diagram": "black or vellum paper, nested boxes with a flowchart header (a ► b ► c), a legend block, dotted fields, one diagonal line leaving the frame",
    "plan_view": "vellum paper, nested textured frames (c.frame) around a receiving surface holding many textured blobs, section labels a/ b/ c/, a scale bar",
    "botanical_plate": "vellum paper with faint ruled lines, a thick textured band crossing the page, many large textured blobs on stems, one enlarged detail, struck word bottom-left, verdict bottom-right",
    "map_sheet": "vellum, a coastline or route drawn as a textured band, hatched land, a compass rose, numbered stations, cobalt bearings",
}


def _client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Export it, or run with --offline to use the fixture cycle.")
    return anthropic.Anthropic()


def _text(r) -> str:
    """Join the text blocks of a response. Current models return a thinking block first, so never index content[0]."""
    if r.stop_reason == "refusal":
        raise RuntimeError(f"model refused: {getattr(r.stop_details, 'explanation', None)}")
    text = "".join(b.text for b in r.content if b.type == "text").strip()
    if not text:
        raise RuntimeError(f"no text in response (stop_reason={r.stop_reason}); if max_tokens, raise it")
    return text


def _json_from(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    return json.loads(text[text.index("{"): text.rindex("}") + 1])


def _code_from(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


# --------------------------------------------------------------------------- #
def plan(mem: Memory, client=None, form=None) -> dict:
    client = client or _client()
    last_form = mem.entries[-1]["form"] if mem.entries else None
    prompt = f"""{STYLE}

MEMORY
{mem.as_text()}

Choose the next entry. Available forms (avoid '{last_form}'):
{json.dumps(FORMS, indent=1)}
{f"The operator asks for form: {form}." if form else ""}

Return ONLY JSON:
{{
 "roman": "{mem.next_roman()}",
 "title": "SHORT TITLE IN CAPS",
 "sub": "three / short / glosses in the trade's jargon",
 "sub2": "palette names separated by slashes, from the canvas PALETTE",
 "form": "one key from the forms above",
 "trade": "the trade whose vocabulary this document uses",
 "carry": ["motif names from memory that must appear, 2-4"],
 "resolve": ["motif names (or open lines) this piece answers, 0-2"],
 "introduce": ["one new object or word the series will have to carry from now on"],
 "struck": "one word or phrase to draw struck-through, or null",
 "verdict": "the first voice's line for the bottom-right, ≤ 5 words",
 "second_hand": ["2-4 short cobalt annotations, ≤ 4 words each"],
 "story_beat": "one sentence, for memory only: what happens in the story here"
}}"""
    r = client.messages.create(model=MODEL, max_tokens=8000, messages=[{"role": "user", "content": prompt}])
    return _json_from(_text(r))


# --------------------------------------------------------------------------- #
def render(code: str, plan_: dict, out_png: Path, seed: int) -> None:
    """Exec model-written code defining draw(c, P) and save the canvas."""
    ns = {"math": __import__("math"), "random": __import__("random"), "canvas": canvaslib, "PALETTE": canvaslib.PALETTE}
    exec(compile(code, "<draw>", "exec"), ns)
    if "draw" not in ns:
        raise RuntimeError("code must define draw(c, P)")
    paper = "black" if plan_.get("form") in ("terminal_ledger",) else "vellum"
    if plan_.get("form") == "route_diagram" and plan_.get("paper") == "black":
        paper = "black"
    c = canvaslib.Canvas(1440, paper=plan_.get("paper", paper), seed=seed)
    ns["draw"](c, plan_)
    c.save(out_png)


def previous_entry(mem: Memory, out_dir: Path):
    """The last rendered entry as (png_path, code) — the image and the hand that drew it.
    Observed (imported) entries have no files; returns (None, None) then."""
    for e in reversed(mem.entries):
        png = out_dir / e.get("file", "")
        if e.get("file") and e["file"] != "observed" and png.is_file():
            py = png.with_suffix(".py")
            return png, (py.read_text(encoding="utf-8") if py.is_file() else None)
    return None, None


def draw(mem: Memory, plan_: dict, out_png: Path, client=None, seed=None, attempts=3, prev=(None, None)) -> str:
    client = client or _client()
    seed = seed if seed is not None else mem.next_number() * 7919
    prev_png, prev_code = prev
    prompt = f"""{STYLE}

PLAN FOR THIS ENTRY
{json.dumps(plan_, indent=1)}

FORM: {FORMS[plan_["form"]]}

MEMORY (for the exact wording of carried motifs)
{mem.as_text()}

{canvaslib.api_reference()}
"""
    if prev_png is not None:
        prompt += f"""
PREVIOUS ENTRY
The image above is the previous entry, {mem.entries[-1]['roman']}. Match its density, its
text sizes, and the way its labels sit on the things they name. Its form is used up; the
new entry takes a different form but belongs to the same hand and the same paper.
"""
        if prev_code:
            prompt += f"The code that drew it, for the idiom and the sizes it used:\n```python\n{prev_code}\n```\n"
    prompt += """
Write Python defining `def draw(c, P):` where c is a Canvas (1440×1440, paper already set)
and P is the plan dict. Use only the API above plus math and random (seed random with c.seed).
Fill the page with the document itself, not with text. Draw the carried motifs first, small
and labelled with c.label. Put the heading with c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"]).
Draw the struck word with c.struck near the bottom-left (size ≤ 16), the verdict bottom-right
in caps with c.text (size ≤ 18, no box behind it), and each second-hand note once with
c.annotate, placed on the thing it comments on. Keep all text inside the page.
Return ONLY a python code block."""
    content = [{"type": "text", "text": prompt}]
    if prev_png is not None:
        b64 = base64.b64encode(prev_png.read_bytes()).decode()
        content.insert(0, {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}})
    messages = [{"role": "user", "content": content}]
    code = ""
    for attempt in range(attempts):
        r = client.messages.create(model=MODEL, max_tokens=16000, messages=messages)
        code = _code_from(_text(r))
        try:
            render(code, plan_, out_png, seed)
            return code
        except Exception:
            tb = traceback.format_exc(limit=4)
            messages += [{"role": "assistant", "content": r.content},  # echo the full blocks (thinking included)
                         {"role": "user", "content": f"That raised:\n{tb}\nFix it and return the full corrected code block only."}]
    raise RuntimeError(f"drawing code failed after {attempts} attempts; last error above")


# --------------------------------------------------------------------------- #
def reflect(mem: Memory, plan_: dict, png: Path, client=None) -> dict:
    client = client or _client()
    b64 = base64.b64encode(png.read_bytes()).decode()
    prompt = f"""{STYLE}

This is the rendered entry {plan_['roman']}. Plan: {json.dumps(plan_)}
Look at what was actually drawn (labels may have been clipped or shifted; describe what is there, not what was intended).

Return ONLY JSON:
{{
 "caption": "the post text: 2 sentences, 45-70 words, first person, lists what the document records and what it has no column for, ends with what the margin says",
 "alt": "plain alt text for a screen reader, 1-2 sentences, literal",
 "motifs_seen": ["motif names actually visible in the image"],
 "new_motifs": [{{"name": "short name", "note": "what it is and where it came from"}}],
 "resolved": ["motif names or open lines this image closes"],
 "open_lines": ["1-3 phrases from this image the next entry will have to answer"],
 "flaws": ["anything drawn badly the next hand should avoid; empty list if none"]
}}"""
    r = client.messages.create(model=MODEL, max_tokens=8000, messages=[{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
        {"type": "text", "text": prompt}]}])
    return _json_from(_text(r))


# --------------------------------------------------------------------------- #
def run_cycle(mem: Memory, out_dir: Path, offline=False, form=None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    n = mem.next_number()
    if offline:
        plan_ = json.loads((ROOT / "fixtures" / "plan.json").read_text(encoding="utf-8"))
        plan_["roman"] = mem.next_roman()
        code = (ROOT / "fixtures" / "draw.py").read_text(encoding="utf-8")
        slug = re.sub(r"[^a-z0-9]+", "_", plan_["title"].lower()).strip("_")
        png = out_dir / f"{n:02d}_{plan_['roman']}_{slug}.png"
        render(code, plan_, png, seed=n * 7919)
        reflection = json.loads((ROOT / "fixtures" / "reflect.json").read_text(encoding="utf-8"))
    else:
        client = _client()
        plan_ = plan(mem, client, form)
        slug = re.sub(r"[^a-z0-9]+", "_", plan_["title"].lower()).strip("_")
        png = out_dir / f"{n:02d}_{plan_['roman']}_{slug}.png"
        code = draw(mem, plan_, png, client, prev=previous_entry(mem, out_dir))
        reflection = reflect(mem, plan_, png, client)

    (png.with_suffix(".py")).write_text(code.rstrip() + "\n", encoding="utf-8", newline="\n")
    (png.with_suffix(".md")).write_text(
        f"# {plan_['roman']} / {plan_['title']}\n\n{reflection['caption']}\n\n**alt:** {reflection['alt']}\n\n"
        f"form: {plan_['form']} · trade: {plan_.get('trade','')}\n", encoding="utf-8")
    mem.record(plan_, reflection, png.name)
    return {"png": str(png), "caption": reflection["caption"], "alt": reflection["alt"], "plan": plan_}
