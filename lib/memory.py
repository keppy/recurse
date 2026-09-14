"""
memory.py — the motif store. This is the part the series is actually made of.

memory.json holds:
  voices      : the two speakers and how they write
  motifs      : named objects/phrases with a state — open | carried | resolved — and
                the entries they appeared in. Open motifs are debts the next entry owes.
  open_lines  : phrases the last image left hanging (questions, unfinished sentences)
  vocabulary  : trades already used, so the next piece can rhyme or avoid them
  entries     : one record per published image
"""
from __future__ import annotations
import json
from pathlib import Path

ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def roman(n):
    s = ""
    for v, r in ROMAN:
        while n >= v:
            s += r; n -= v
    return s


class Memory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    # -- accessors -------------------------------------------------------- #
    @property
    def entries(self): return self.data["entries"]
    @property
    def motifs(self): return self.data["motifs"]

    def next_number(self): return self.data["series_number"] + 1
    def next_roman(self): return roman(self.next_number())

    # -- text the model reads -------------------------------------------- #
    def as_text(self):
        d = self.data
        lines = [f"Series so far: {d['series_number']} entries. Story: {d['story']}", "",
                 "Voices:", f"  first voice — {d['voices']['first']}", f"  second hand — {d['voices']['second']}", "",
                 "Motifs (state · name — note · seen in):"]
        for m in d["motifs"]:
            lines.append(f"  [{m['state']:8}] {m['name']} — {m['note']} · {', '.join(m['seen_in']) or '—'}")
        lines += ["", "Open lines the next entry owes an answer to:"] + [f"  · {l}" for l in d["open_lines"]]
        lines += ["", f"Trades already used: {', '.join(d['vocabulary'])}", "", "Recent entries:"]
        for e in d["entries"][-4:]:
            lines.append(f"  {e['roman']} {e['title']} ({e['form']}) — {e['beat']}")
            if e.get("flaws"):
                lines.append(f"     flaws to avoid: {'; '.join(e['flaws'])}")
        return "\n".join(lines)

    # -- update after a cycle ---------------------------------------------- #
    def record(self, plan_, reflection, filename):
        n = self.next_number(); r = plan_["roman"]
        byname = {m["name"]: m for m in self.motifs}
        for name in reflection.get("motifs_seen", []) + plan_.get("carry", []):
            if name in byname:
                m = byname[name]; m["state"] = "carried" if m["state"] != "resolved" else m["state"]
                if r not in m["seen_in"]: m["seen_in"].append(r)
        for name in reflection.get("resolved", []) + plan_.get("resolve", []):
            if name in byname: byname[name]["state"] = "resolved"
        for nm in reflection.get("new_motifs", []):
            if nm["name"] not in byname:
                self.motifs.append({"name": nm["name"], "note": nm["note"], "state": "open", "seen_in": [r]})
        for name in plan_.get("introduce", []):
            if name not in {m["name"] for m in self.motifs}:
                self.motifs.append({"name": name, "note": "introduced in " + r, "state": "open", "seen_in": [r]})
        self.data["open_lines"] = reflection.get("open_lines", [])[:3]
        if plan_.get("trade") and plan_["trade"] not in self.data["vocabulary"]:
            self.data["vocabulary"].append(plan_["trade"])
        self.data["story"] = (self.data["story"] + " " + plan_.get("story_beat", "")).strip()[-1200:]
        self.entries.append({"n": n, "roman": r, "title": plan_["title"], "form": plan_["form"], "file": filename,
                             "caption": reflection["caption"], "beat": plan_.get("story_beat", ""), "flaws": reflection.get("flaws", [])})
        self.data["series_number"] = n
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
