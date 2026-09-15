import math, random

def draw(c, P):
    rnd = random.Random(c.seed)
    c.ruled(150, 1300, step=34, every=3)
    c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"])

    # carried relic: curd retained
    hexa = [(150 + 36*math.cos(a), 220 + 30*math.sin(a)) for a in [i*math.pi/3 + 0.2 for i in range(6)]]
    c.textured_poly(hexa, "bone", "seed_ochre", outline="ochre_dark", density=0.02, length=(3, 7))
    c.label(112, 262, "curd retained")

    # the coast: hatched land above a textured band
    coast = [(0, 640), (140, 610), (300, 650), (470, 600), (640, 630), (800, 580), (960, 610), (1120, 560), (1300, 590), (1440, 550)]
    land = coast + [(1440, 330), (0, 330)]
    c.poly(land, fill="paper_dark")
    c.hatch(land, "earth_green", density=0.006, length=(8, 22), angle=0.15, spread=0.3, extra_colors=("leaf_pale", "seed_ochre"))
    c.band(coast, width=26, fill="earth_green", hatch_color="moss", rib="seed_ochre")

    # sea: dotted, denser with depth
    for k, sp in enumerate((12, 9, 7, 5)):
        c.dots((0, 700 + k*120, 1440, 700 + (k+1)*120), spacing=sp, color="cobalt", jitter=1.5, seed=c.seed + k)

    # the Hag's course as stations along the coast
    for tag, name, x in [("§1", "Euclid", 250), ("§2", "Newton", 560), ("§3", "Fluxions", 880), ("§4", "Conics", 1190)]:
        y = 560
        c.d.ellipse((x-6, y-6, x+6, y+6), fill="#5a5138")
        c.label(x - 10, y - 46, tag + " / " + name, size=14)
        c.line([(x, y), (x, y + 28)], "ink", 1)
    c.annotate(1090, 480, "the route ran downhill past him", 13)

    # soundings: dashed lead lines dropped into the sea
    depths = []
    for i in range(11):
        x = 90 + i * 125 + rnd.randint(-15, 15)
        y0 = 660 + rnd.randint(0, 20)
        y1 = 780 + rnd.randint(40, 380)
        for y in range(int(y0), int(y1), 12):
            c.line([(x, y), (x, y + 6)], "ink", 1)
        c.d.ellipse((x-5, y1-5, x+5, y1+5), fill="#5a5138")
        c.label(x + 8, y1 - 8, "–", size=13)
        depths.append((x, y1))
    c.label(90, 690, "soundings, unrequested", size=13)
    c.annotate(depths[3][0] + 12, depths[3][1] + 14, "the lead came back wet")
    c.annotate(depths[7][0] + 12, depths[7][1] + 14, "he asked nothing")

    # compass rose with the inclining bearing
    cx, cy, r = 1250, 250, 70
    for a in range(0, 360, 45):
        ax = math.radians(a)
        c.line([(cx, cy), (cx + r*math.cos(ax), cy + r*math.sin(ax))], "ink_light", 1)
    c.d.ellipse((cx-r, cy-r, cx+r, cy+r), outline="#5a5138", width=1)
    c.text(cx, cy - r - 22, "N", 16, "ink", anchor="ma")
    a = math.radians(90 + 12)
    c.arrow([(cx, cy), (cx + (r+40)*math.cos(a), cy + (r+40)*math.sin(a))], "cobalt", 3)
    c.annotate(cx + 60, cy + r + 30, "head: 12° down")
    c.label(cx - 70, cy + r + 52, "bearing taken without asking", size=12)

    # legend, scale, the crumb listed above everything
    lx, ly = 90, 1330
    c.line([(lx, ly), (lx + 40, ly)], "earth_green", 8); c.label(lx + 50, ly - 8, "prescribed coast")
    c.line([(lx + 230, ly), (lx + 270, ly)], "ink", 1); c.label(lx + 280, ly - 8, "lead line")
    c.dots((lx + 400, ly - 6, lx + 440, ly + 6), 5, "cobalt"); c.label(lx + 450, ly - 8, "no bottom")
    c.scale_bar(1130, 1330, 160, 4, "cables")
    c.text(560, 1240, "one crumb ≈ 0.4 g · listed above everything", 17, "ink")
    c.annotate(560, 1266, "0.4 g still listed")

    # struck word, verdict
    c.struck(90, 1395, P["struck"], 16)
    c.text(1350, 1392, P["verdict"], 18, "ink", anchor="ra")
