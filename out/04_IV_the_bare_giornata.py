def draw(c, P):
    import math, random
    random.seed(c.seed)

    # ================= carried motifs, small, labelled, drawn first =================
    my = 200

    # 1. gold leaf, one square
    gx = 110
    c.poly([(gx-14, my-14), (gx+14, my-14), (gx+14, my+14), (gx-14, my+14)],
           fill='gold_leaf', outline='bistre', width=1)
    c.label(gx-46, my+22, "gold leaf, one square", size=12)
    c.label(gx-30, my+38, "0.03 g · rank 1", size=11)

    # 2. the spiral stair (small spiral)
    sxx = 390
    pts = []
    for t in range(0, 720, 8):
        r = 22 * (1 - t / 720)
        ang = math.radians(t * 1.4)
        pts.append((sxx + r * math.cos(ang), my + r * math.sin(ang)))
    c.line(pts, color='bistre_pale', width=2)
    c.label(sxx - 40, my + 30, "the spiral stair", size=12)

    # 3. the kernel (blank / null space) — carried, still drawn blank here
    kxx = 670
    kbox = (kxx - 32, my - 16, kxx + 32, my + 16)
    c.dots(kbox, spacing=7, color='bistre_pale', jitter=0.4, seed=c.seed + 5)
    c.poly([(kbox[0], kbox[1]), (kbox[2], kbox[1]), (kbox[2], kbox[3]), (kbox[0], kbox[3])],
           fill=None, outline='bistre_pale', width=1)
    c.label(kxx - 24, my + 30, "the kernel", size=12)

    # ================= heading =================
    c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"])

    c.scale_bar(1080, 205, length=110, ticks=4, label="ells / giornata", color='bistre_pale')

    # ================= the wall, in giornate =================
    cols, rows = 4, 3
    x0, y0 = 170, 420
    cellw, cellh, gap = 258, 228, 16
    col_letters = "abcd"

    # column / row headers
    for cix in range(cols):
        cx = x0 + cix * (cellw + gap) + cellw / 2
        c.label(cx - 4, y0 - 26, col_letters[cix], size=13, color='bistre_pale')
    for rix in range(rows):
        ry = y0 + rix * (cellh + gap) + cellh / 2
        c.label(x0 - 30, ry - 6, str(rix + 1), size=13, color='bistre_pale')

    patches = []
    for i in range(cols * rows):
        r, col = divmod(i, cols)
        px = x0 + col * (cellw + gap)
        py = y0 + r * (cellh + gap)
        patches.append((px, py, r, col, i + 1))

    # join bands: vertical seams
    for cix in range(1, cols):
        jx = x0 + cix * (cellw + gap) - gap / 2
        c.band([(jx, y0 - 6), (jx, y0 + rows * (cellh + gap) - gap - 6)],
               width=12, fill='umber_burnt', hatch_color='bistre', rib='ochre_raw',
               seed=c.seed + cix)
    # join bands: horizontal seams
    for rix in range(1, rows):
        jy = y0 + rix * (cellh + gap) - gap / 2
        c.band([(x0 - 6, jy), (x0 + cols * (cellw + gap) - gap - 6, jy)],
               width=12, fill='umber_burnt', hatch_color='bistre', rib='ochre_raw',
               seed=c.seed + 50 + rix)

    for (px, py, r, col, n) in patches:
        box_pts = [(px, py), (px + cellw, py), (px + cellw, py + cellh), (px, py + cellh)]
        if n == 12:
            # the twelfth giornata: was bare, now painted
            c.textured_poly(box_pts, fill='plaster', hatch_color='sinopia',
                             density=0.006, seed=c.seed + 200)
            fbox = (px + 14, py + 14, px + cellw - 14, py + cellh - 14)
            c.dots(fbox, spacing=9, color='sinopia', jitter=0.5, seed=c.seed + 210)
            fcx, fcy = px + cellw / 2, py + cellh / 2 + 6
            c.poly(c.blob(fcx - 34, fcy - 20, 9, n=8, irregular=0.2, seed=c.seed + 1),
                   fill='soot', outline='bistre', width=1)
            c.poly(c.blob(fcx + 34, fcy - 20, 9, n=8, irregular=0.2, seed=c.seed + 2),
                   fill='soot', outline='bistre', width=1)
            c.curve((fcx - 40, fcy + 30), (fcx - 15, fcy + 54),
                     (fcx + 15, fcy + 54), (fcx + 40, fcy + 30),
                     color='sinopia', width=3)
            c.label(px + 12, py + 14, "giornata 12", size=13, color='bistre')
            c.label(px + 12, py + 32, "row 3 · col d — once bare", size=11, color='bistre_pale')
            c.annotate(px + cellw - 150, py - 18, "not bare. unfinished.")
            c.annotate(px + 20, py + cellh - 46, "the twelfth is here.")
            c.annotate(fcx + 46, fcy - 30, "it is a face.")
        else:
            c.textured_poly(box_pts, fill='ochre_pale', hatch_color='sinopia',
                             density=0.008, seed=c.seed + 20 + n)
            c.label(px + 12, py + 14, f"giornata {n:02d}", size=13, color='bistre')
            c.label(px + 12, py + 32, f"row {r+1} · col {col_letters[col]}", size=11, color='bistre_pale')
            if n == 7:
                c.struck(px + 12, py + 52, "row 7", size=14, color='bistre_pale')
                c.annotate(px + cellw - 130, py + cellh - 30, "still struck, row seven.")

    # ================= the arriccio scar, introduced =================
    scar_pts = []
    sx0, sy0 = x0 - 4, y0 + 30
    sx1, sy1 = x0 + cols * (cellw + gap) - gap - 30, y0 + rows * (cellh + gap) - gap - 40
    steps = 14
    for t in range(steps + 1):
        tt = t / steps
        jx = sx0 + (sx1 - sx0) * tt + random.uniform(-10, 10)
        jy = sy0 + (sy1 - sy0) * tt + random.uniform(-10, 10)
        scar_pts.append((jx, jy))
    c.band(scar_pts, width=7, fill='sinopia', hatch_color='umber_burnt',
           rib='bistre', ribs=False, seed=c.seed + 99)
    c.label(sx0 + 30, sy0 - 20, "the arriccio scar", size=12, color='bistre')

    # ================= legend =================
    lgx = 1130
    lgy = 470
    c.label(lgx, lgy - 20, "legend", size=13)
    c.poly([(lgx-10, lgy-8), (lgx+10, lgy-8), (lgx+10, lgy+8), (lgx-10, lgy+8)],
           fill='ochre_pale', outline='bistre', width=1)
    c.label(lgx + 18, lgy - 7, "day-patch, painted", size=11)

    c.poly([(lgx-10, lgy+30), (lgx+10, lgy+30), (lgx+10, lgy+46), (lgx-10, lgy+46)],
           fill='plaster', outline='bistre', width=1)
    c.label(lgx + 18, lgy + 31, "day-patch, once bare", size=11)

    c.line([(lgx-10, lgy+68), (lgx+10, lgy+68)], color='umber_burnt', width=4)
    c.label(lgx + 18, lgy + 61, "join, textured", size=11)

    c.line([(lgx-10, lgy+92), (lgx+10, lgy+92)], color='sinopia', width=3)
    c.label(lgx + 18, lgy + 85, "arriccio scar", size=11)

    # ================= field notes =================
    fny = 1180
    c.text(190, fny, "field notes:", size=13, color='bistre')
    c.text(190, fny + 22, "— giornata 12, once bare: painted this day.", size=12, color='bistre_pale')
    c.text(190, fny + 42, "— beneath the sinopia, a face surfaces.", size=12, color='bistre_pale')
    c.text(190, fny + 62, "— giornata 07: join intact, entry stands struck.", size=12, color='bistre_pale')
    c.text(190, fny + 82, "— rank of the finished wall: one.", size=12, color='bistre_pale')

    # ================= struck word, bottom-left =================
    c.struck(40, 1370, "EMPTY", size=15)

    # ================= verdict, bottom-right =================
    c.text(1400, 1380, "GIORNATA XII: RANK ONE.", size=17, color='gold_leaf', anchor='ra')
