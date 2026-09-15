"""
canvas.py — the drawing library the model is handed each run.

Everything the observed series does is reachable from here: vellum or black
paper, ruled register lines, short-segment hatch textures clipped to shapes,
irregular blobs, textured bands (stems, frames), struck text, second-hand
annotations, and a monospace grid panel for the matrix form.

The model only ever calls methods on a Canvas (c) and a Panel (p).
Coordinates are pixels; the canvas is square, `c.W` on a side.
"""
from __future__ import annotations
import math, random
from PIL import Image, ImageDraw, ImageFont

import os
from pathlib import Path

# DejaVu is the series' typeface. Search the usual places; RECURSE_FONT_DIR overrides.
_FONT_DIRS = [d for d in [
    os.environ.get("RECURSE_FONT_DIR"),
    "/usr/share/fonts/truetype/dejavu",                          # Debian/Ubuntu
    "/usr/share/fonts/dejavu",                                   # Fedora/Arch
    "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts",
    "/Library/Fonts", "~/Library/Fonts",                         # macOS
    os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts"),          # Windows
    os.path.expandvars("%LOCALAPPDATA%/Microsoft/Windows/Fonts"),         # Windows per-user
] if d]
FONT_FILES = {"sans": "DejaVuSans.ttf", "mono": "DejaVuSansMono.ttf", "serif": "DejaVuSerif.ttf"}

def _find_font(name):
    for d in _FONT_DIRS:
        f = Path(os.path.expanduser(d)) / name
        if f.is_file():
            return str(f)
    return name  # let PIL try its own system lookup by basename

FONTS = {k: _find_font(v) for k, v in FONT_FILES.items()}

# Named colours. The model refers to these by name; captions may print them.
# The world is a frescoed house under assessment: plaster and soot papers, bistre ink,
# fresco earths, and the house's hand in verdigris.
PALETTE = {
    "plaster": "#e9e2d3", "plaster_dark": "#d8cfba", "soot": "#0c0b0a",
    "bistre": "#4a3b2a", "bistre_pale": "#8c7d66",
    "verdigris": "#3f8a7a", "verdigris_bright": "#5fc4ad",
    "sinopia": "#a2452e", "umber_burnt": "#6b4a2b", "ochre_raw": "#c99a4b", "ochre_pale": "#dcc48f",
    "slate": "#5b6672", "lead_white": "#f1ede2", "bone_black": "#2a2723",
    "lapis": "#2b4d8f", "gold_leaf": "#d1a83f", "gold_dim": "#7a6224",
    "cinnabar": "#c3352b", "dawn": "#e8c9b3",
}

# Names from the first series, kept only so fixtures/ still render. Not shown to the model.
LEGACY = {
    "vellum": "plaster", "paper_dark": "plaster_dark", "black": "soot", "night": "slate",
    "ink": "bistre", "ink_light": "bistre_pale", "bone": "lead_white",
    "cobalt": "verdigris", "cobalt_bright": "verdigris_bright",
    "earth_green": "sinopia", "moss": "umber_burnt", "leaf_pale": "ochre_pale",
    "seed_ochre": "ochre_raw", "ochre_dark": "umber_burnt", "umber": "ochre_raw",
    "scarlet": "cinnabar", "scarlet_dark": "sinopia", "flesh": "dawn",
    "terminal_gold": "gold_leaf", "terminal_dim": "gold_dim",
}

def col(c):
    """Resolve a palette name or pass a hex/RGB through."""
    return PALETTE.get(c) or PALETTE.get(LEGACY.get(c, ""), c)

def _rng(seed):
    return random.Random(seed)

# --------------------------------------------------------------------------- #
class Canvas:
    def __init__(self, size=1440, paper="plaster", seed=0):
        """paper: palette name or hex. seed: base seed for all textures."""
        self.W = size
        self.im = Image.new("RGB", (size, size), col(paper))
        self.d = ImageDraw.Draw(self.im)
        self.seed = seed
        self._fonts = {}

    # -- fonts ------------------------------------------------------------- #
    def font(self, size=18, family="sans"):
        key = (size, family)
        if key not in self._fonts:
            try:
                self._fonts[key] = ImageFont.truetype(FONTS[family], size)
            except OSError:
                # DejaVu not installed anywhere we looked: degrade rather than crash.
                self._fonts[key] = ImageFont.load_default(size)
        return self._fonts[key]

    # -- text -------------------------------------------------------------- #
    def text(self, x, y, s, size=18, color="bistre", family="sans", anchor="la", spacing=4):
        """Draw text. anchor uses PIL anchors: 'la' left-top, 'ra' right-top, 'ma' centred, 'ls' left-baseline."""
        self.d.multiline_text((x, y), s, font=self.font(size, family), fill=col(color), anchor=anchor, spacing=spacing)

    def text_width(self, s, size=18, family="sans"):
        return self.d.textlength(s, font=self.font(size, family))

    def struck(self, x, y, s, size=18, color="bistre_pale", strike="verdigris", family="sans"):
        """Text with a line through it (the register's cancelled entry). Returns width."""
        self.text(x, y, s, size, color, family)
        w = self.text_width(s, size, family)
        self.d.line([(x - 4, y + size * 0.55), (x + w + 4, y + size * 0.55)], fill=col(strike), width=max(1, size // 9))
        return w

    def title(self, s, sub=None, sub2=None, x=32, y=30, color="bistre"):
        """Series-style heading: 'IV / TITLE' with up to two small sublines."""
        self.text(x, y, s, 34, color)
        if sub:  self.text(x, y + 48, sub, 17, "bistre_pale")
        if sub2: self.text(x, y + 74, sub2, 13, "bistre_pale")

    def label(self, x, y, s, color="bistre", size=13):
        """Small diagram label like 'a / cut edge'."""
        self.text(x, y, s, size, color)

    def annotate(self, x, y, s, size=14, color="verdigris"):
        """The second hand: a short verdigris note, four words or fewer."""
        self.text(x, y, s, size, color)

    # -- register paper --------------------------------------------------------- #
    def ruled(self, y0, y1, step=34, color="bistre_pale", alpha=70, numbers=True, x0=None, x1=None, every=3):
        """Faint ruled lines like register paper, with '01', '04' row numbers in the margin."""
        x0 = 0 if x0 is None else x0
        x1 = self.W if x1 is None else x1
        ov = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        r, g, b = Image.new("RGB", (1, 1), col(color)).getpixel((0, 0))
        n = 1
        for y in range(y0, y1, step):
            od.line([(x0, y), (x1, y)], fill=(r, g, b, alpha), width=1)
            if numbers and (n - 1) % every == 0:
                od.text((x0 + 18, y + 4), f"{n:02d}", font=self.font(13), fill=(r, g, b, min(255, alpha + 90)))
            n += 1
        self.im.paste(Image.alpha_composite(self.im.convert("RGBA"), ov).convert("RGB"))
        self.d = ImageDraw.Draw(self.im)

    # -- shapes ----------------------------------------------------------- #
    def blob(self, cx, cy, r, n=9, irregular=0.18, seed=None):
        """Irregular rounded polygon points (a stone, a pan, a wart). Returns list of (x, y)."""
        rnd = _rng((seed if seed is not None else self.seed) + int(cx * 7 + cy * 13))
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.15, 0.15)
            rr = r * (1 + rnd.uniform(-irregular, irregular))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return pts

    def poly(self, pts, fill=None, outline=None, width=2):
        self.d.polygon(pts, fill=col(fill) if fill else None, outline=col(outline) if outline else None, width=width)

    def line(self, pts, color="bistre", width=2):
        self.d.line(pts, fill=col(color), width=width, joint="curve")

    def curve(self, p0, p1, p2, p3, color="bistre", width=3, steps=40):
        """Cubic bezier through four control points (stems, arrows)."""
        pts = []
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
            y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
            pts.append((x, y))
        self.line(pts, color, width)
        return pts

    def arrow(self, pts, color="verdigris", width=3, head=14):
        """Polyline ending in an arrowhead (a bearing, a direction of tread)."""
        self.line(pts, color, width)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        a = math.atan2(y1 - y0, x1 - x0)
        tip = (x1, y1)
        l = (x1 - head * math.cos(a - 0.4), y1 - head * math.sin(a - 0.4))
        r = (x1 - head * math.cos(a + 0.4), y1 - head * math.sin(a + 0.4))
        self.d.polygon([tip, l, r], fill=col(color))

    def star(self, cx, cy, r, color="umber_burnt", points=5):
        """Small star (a mark, a mason's sign)."""
        pts = []
        for i in range(points * 2):
            rr = r if i % 2 == 0 else r * 0.45
            a = -math.pi / 2 + i * math.pi / points
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        self.d.polygon(pts, fill=col(color))

    def dots(self, box, spacing=6, color="verdigris", jitter=0.0, seed=None):
        """Dot field inside box=(x0,y0,x1,y1) — a dotted field in a panel or a floor plan."""
        rnd = _rng(self.seed if seed is None else seed)
        x0, y0, x1, y1 = box
        for y in range(int(y0), int(y1), spacing):
            for x in range(int(x0), int(x1), spacing):
                jx, jy = rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter)
                self.d.point((x + jx, y + jy), fill=col(color))

    # -- the signature texture -------------------------------------------- #
    def hatch(self, pts, color="sinopia", density=0.012, length=(6, 18), angle=None, spread=0.35,
              width=1, seed=None, extra_colors=()):
        """
        Fill a polygon with short random line segments — the series' woven texture.
        density: segments per pixel of area (0.004 sparse … 0.03 dense).
        angle: radians; None = random per segment. spread: angular jitter.
        extra_colors: other palette names mixed in (e.g. ('ochre_raw','umber_burnt')).
        """
        rnd = _rng((seed if seed is not None else self.seed) + int(sum(x for x, _ in pts)))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
        if x1 <= x0 or y1 <= y0:
            return
        mask = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
        layer = Image.new("RGBA", mask.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        colors = [col(color)] + [col(c) for c in extra_colors]
        area = mask.size[0] * mask.size[1]
        for _ in range(int(area * density)):
            x, y = rnd.uniform(0, mask.size[0]), rnd.uniform(0, mask.size[1])
            a = rnd.uniform(0, math.pi) if angle is None else angle + rnd.uniform(-spread, spread)
            L = rnd.uniform(*length)
            c = colors[0] if rnd.random() < 0.7 else rnd.choice(colors)
            ld.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=c, width=width)
        self.im.paste(layer, (x0, y0), Image.composite(layer.split()[3], Image.new("L", mask.size, 0), mask))
        self.d = ImageDraw.Draw(self.im)

    def textured_poly(self, pts, fill, hatch_color, outline=None, **hatch_kw):
        """Fill + hatch + outline in one call (a patch of plaster, a pan, a block of stone)."""
        self.poly(pts, fill=fill)
        self.hatch(pts, hatch_color, **hatch_kw)
        if outline:
            self.poly(pts, outline=outline, width=hatch_kw.get("outline_width", 2))

    def band(self, pts, width=40, fill="sinopia", hatch_color="umber_burnt", rib="ochre_raw", ribs=True, seed=None):
        """
        A thick textured ribbon along a polyline (a route, a join between giornate, a border).
        Draws fill, hatch, a centre rib line and cross-ribs.
        """
        rnd = _rng(self.seed if seed is None else seed)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            a = math.atan2(y1 - y0, x1 - x0)
            nx, ny = -math.sin(a) * width / 2, math.cos(a) * width / 2
            quad = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
            self.poly(quad, fill=fill)
            self.hatch(quad, hatch_color, density=0.02, length=(4, 10), angle=a, spread=0.2, seed=rnd.randrange(1 << 30))
            if ribs:
                seg = math.hypot(x1 - x0, y1 - y0)
                for t in range(0, int(seg), 10):
                    px, py = x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg
                    self.d.line([(px + nx * 0.9, py + ny * 0.9), (px + nx * 0.6, py + ny * 0.6)], fill=col("lead_white"), width=2)
        self.line(pts, rib, width=1)

    def frame(self, box, thickness=40, fill="sinopia", hatch_colors=("umber_burnt", "ochre_raw", "ochre_pale"), inner_line="bistre", seed=None):
        """Textured rectangular frame (box=(x0,y0,x1,y1)) — nested frames around a plan or section."""
        x0, y0, x1, y1 = box
        t = thickness
        rings = [[(x0, y0), (x1, y0), (x1, y0 + t), (x0, y0 + t)],
                 [(x0, y1 - t), (x1, y1 - t), (x1, y1), (x0, y1)],
                 [(x0, y0), (x0 + t, y0), (x0 + t, y1), (x0, y1)],
                 [(x1 - t, y0), (x1, y0), (x1, y1), (x1 - t, y1)]]
        for i, r in enumerate(rings):
            self.poly(r, fill=fill)
            self.hatch(r, hatch_colors[0], density=0.03, length=(3, 9), angle=0 if i < 2 else math.pi / 2, spread=0.25,
                       extra_colors=hatch_colors[1:], seed=(self.seed if seed is None else seed) + i)
        self.d.rectangle(box, outline=col(inner_line), width=1)
        self.d.rectangle((x0 + t, y0 + t, x1 - t, y1 - t), outline=col(inner_line), width=1)

    def scale_bar(self, x, y, length=120, ticks=4, label="", color="bistre"):
        """Small measured scale with tick marks and a label under it."""
        self.d.line([(x, y), (x + length, y)], fill=col(color), width=2)
        for i in range(ticks + 1):
            tx = x + length * i / ticks
            self.d.line([(tx, y - 6), (tx, y + 6)], fill=col(color), width=2)
            self.text(tx, y + 12, str(i), 12, color, anchor="ma")
        if label:
            self.text(x, y + 30, label, 12, color)

    # -- matrix form -------------------------------------------- #
    def panel(self, x, y, cols, rows, cell=(12, 22), bg="soot", fg="gold_leaf"):
        """A monospace grid panel drawn onto the canvas. See Panel."""
        return Panel(self, x, y, cols, rows, cell, bg, fg)

    def save(self, path):
        self.im.save(path)
        return path


class Panel:
    """
    Character-grid panel (the PROMOTION LEDGER form). Coordinates are cells.
    p.put(col,row,text,color)   p.box(c0,r0,c1,r1)   p.rule(row,c0,c1,dotted)
    p.vrule(col,r0,r1)          p.bar(c,r,w,color)   p.hl(c,r,text)   p.strike(c,r,text)
    """
    def __init__(self, c, x, y, cols, rows, cell, bg, fg):
        self.c, self.x, self.y, self.cols, self.rows = c, x, y, cols, rows
        self.cw, self.ch = cell
        self.fg = fg
        self.size = int(self.ch * 0.62)
        c.d.rectangle((x, y, x + cols * self.cw, y + rows * self.ch), fill=col(bg))
        self._rnd = _rng(c.seed)

    def _px(self, cc, rr):
        return self.x + cc * self.cw, self.y + rr * self.ch

    def put(self, cc, rr, s, color=None):
        px, py = self._px(cc, rr)
        self.c.text(px, py + self.ch * 0.15, s, self.size, color or self.fg, "mono")

    def right(self, cc_end, rr, s, color=None):
        self.put(cc_end - len(s), rr, s, color)

    def box(self, c0, r0, c1, r1, color=None, double=False):
        x0, y0 = self._px(c0, r0); x1, y1 = self._px(c1, r1)
        self.c.d.rectangle((x0, y0, x1, y1), outline=col(color or "gold_dim"), width=1)
        if double:
            self.c.d.rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), outline=col(color or "gold_dim"), width=1)

    def rule(self, rr, c0, c1, dotted=True, color=None):
        x0, y = self._px(c0, rr); x1, _ = self._px(c1, rr)
        y += self.ch // 2
        if dotted:
            for xx in range(int(x0), int(x1), 4):
                self.c.d.point((xx, y), fill=col(color or "gold_dim"))
        else:
            self.c.d.line([(x0, y), (x1, y)], fill=col(color or "gold_dim"), width=1)

    def vrule(self, cc, r0, r1, color=None):
        x, y0 = self._px(cc, r0); _, y1 = self._px(cc, r1)
        x += self.cw // 2
        self.c.d.line([(x, y0), (x, y1)], fill=col(color or "gold_dim"), width=1)

    def bar(self, cc, rr, w, color="ochre_raw"):
        """Irregular hatched bar w cells wide: runs of checker / dots / grain / solid."""
        x, y = self._px(cc, rr); y += 3; h = self.ch - 6; end = x + w * self.cw
        tones = [col(color), col("gold_dim"), col("gold_leaf")] if color == "ochre_raw" else [col(color), col("verdigris")]
        d = self.c.d
        while x < end:
            run = min(end - x, self.cw * self._rnd.randint(1, 4)); tex = self._rnd.random(); tone = self._rnd.choice(tones)
            if tex < 0.3:
                for yy in range(0, h, 2):
                    for xx in range((yy // 2 % 2) * 2, run, 4): d.rectangle((x + xx, y + yy, x + xx + 1, y + yy + 1), fill=tone)
            elif tex < 0.5:
                for yy in range(1, h, 3):
                    for xx in range(1, run, 3): d.point((x + xx, y + yy), fill=tone)
            elif tex < 0.7:
                for yy in range(h):
                    for xx in range(run):
                        if self._rnd.random() < 0.5: d.point((x + xx, y + yy), fill=tone)
            elif tex < 0.86:
                d.rectangle((x, y, x + run, y + h), fill=tone)
            else:
                for yy in range(0, h, 3): d.line([(x, y + yy), (x + run, y + yy)], fill=tone)
            x += run

    def hl(self, cc, rr, s, bg="gold_leaf", fg="soot"):
        x, y = self._px(cc, rr)
        self.c.d.rectangle((x, y + 1, x + len(s) * self.cw, y + self.ch - 1), fill=col(bg))
        self.put(cc, rr, s, fg)

    def strike(self, cc, rr, s, color="gold_dim", strike="verdigris_bright"):
        self.put(cc, rr, s, color)
        x, y = self._px(cc, rr)
        self.c.d.line([(x, y + self.ch // 2), (x + len(s) * self.cw, y + self.ch // 2)], fill=col(strike), width=1)


def api_reference():
    """Text the model is shown: every public method with its docstring and signature."""
    import inspect
    out = ["# canvas API (call on `c`; panels via p = c.panel(...))", f"PALETTE names: {', '.join(PALETTE)}", ""]
    for cls in (Canvas, Panel):
        out.append(f"## {cls.__name__}")
        for name, fn in inspect.getmembers(cls, inspect.isfunction):
            if name.startswith("_") and name != "__init__":
                continue
            sig = str(inspect.signature(fn)).replace("(self, ", "(").replace("(self)", "()")
            doc = (inspect.getdoc(fn) or "").strip().replace("\n", " ")
            out.append(f"- {name}{sig}  — {doc}" if doc else f"- {name}{sig}")
        out.append("")
    return "\n".join(out)
