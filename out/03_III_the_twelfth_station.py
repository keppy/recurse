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

    # 3. the kernel (blank / null space)
    kxx = 670
    kbox = (kxx - 32, my - 16, kxx + 32, my + 16)
    c.dots(kbox, spacing=7, color='bistre_pale', jitter=0.4, seed=c.seed + 5)
    c.poly([(kbox[0], kbox[1]), (kbox[2], kbox[1]), (kbox[2], kbox[3]), (kbox[0], kbox[3])],
           fill=None, outline='bistre_pale', width=1)
    c.label(kxx - 24, my + 30, "the kernel", size=12)

    # 4. the tally of returns
    txx = 950
    c.poly([(txx-40, my-20), (txx+40, my-20), (txx+40, my+20), (txx-40, my+20)],
           fill=None, outline='bistre_pale', width=1)
    for i in range(1, 3):
        c.line([(txx-40, my-20+i*13.3), (txx+40, my-20+i*13.3)], color='bistre_pale', width=1)
    for i in range(1, 3):
        c.line([(txx-40+i*26.6, my-20), (txx-40+i*26.6, my+20)], color='bistre_pale', width=1)
    c.label(txx-52, my+30, "the tally of returns", size=12)
    c.annotate(txx - 50, my - 40, "row 7 still struck.")

    # 5. the basket, unopened (still, before the tread acts on it)
    bxx = 1230
    basket_pts = [(bxx-38, my-8), (bxx-30, my+20), (bxx+30, my+20), (bxx+38, my-8)]
    c.textured_poly(basket_pts, fill='ochre_raw', hatch_color='umber_burnt',
                     density=0.03, extra_colors=('bistre',))
    c.curve((bxx-20, my-8), (bxx-10, my-26), (bxx+10, my-26), (bxx+20, my-8),
             color='bistre_pale', width=2)
    c.label(bxx-40, my+30, "the basket, unopened", size=12)

    # ================= heading =================
    c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"])

    # ================= flowchart header =================
    c.text(720, 296, "a: the wall  ►  b: the spiral stair  ►  c: the rock, three names  ►  d: the twelfth station",
           size=14, color='bistre_pale', anchor='ma')
    c.scale_bar(150, 330, length=110, ticks=4, label="paces", color='bistre_pale')
    c.scale_bar(320, 330, length=110, ticks=4, label="ells", color='bistre_pale')

    # ================= the dawn tread : 12 stations, one stair =================
    x_left, x_right = 250, 1000
    y0, dy = 380, 66

    names = [
        "the wall", "giornate ridge", "sinopia line", "the spiral stair",
        "second turn", "third turn", "stair foot", "courtyard",
        "rock approach", "the basket, opened", "rock of three names", "",
    ]
    drop = [1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1]

    stations = []
    cum_elev = 0
    for i in range(12):
        x = x_left if i % 2 == 0 else x_right
        y = y0 + i * dy
        cum_elev += drop[i]
        stations.append((x, y, cum_elev))

    # dotted ground field near the courtyard (station index 7)
    cx, cy, _ = stations[7]
    field_box = (cx - 90, cy - 30, cx + 90, cy + 44)
    c.dots(field_box, spacing=8, color='bistre_pale', jitter=0.5, seed=c.seed + 11)

    # path
    path_pts = [(s[0], s[1]) for s in stations]
    c.line(path_pts, color='bistre_pale', width=2)

    for i, (x, y, elev) in enumerate(stations):
        pace = i + 1
        marked = (i != 11)
        r = 9
        circ = []
        for t in range(0, 360, 24):
            ang = math.radians(t)
            circ.append((x + r * math.cos(ang), y + r * math.sin(ang)))
        if marked:
            c.poly(circ, fill='ochre_pale', outline='bistre', width=1)
        else:
            c.poly(circ, fill=None, outline='bistre_pale', width=2)

        side_right = (x == x_left)
        tx = x + 22 if side_right else x - 22
        anchor = 'la' if side_right else 'ra'

        label_txt = f"pace {pace:02d} · {names[i]}" if names[i] else f"pace {pace:02d} · (unmarked)"
        c.text(tx, y - 8, label_txt, size=13, color='bistre', anchor=anchor)
        c.text(tx, y + 8, f"-{elev} ell", size=11, color='bistre_pale', anchor=anchor)

    # ---- station 4 (index 3): the stair itself, drawn larger on the route ----
    sx, sy, _ = stations[3]
    stair_pts = []
    for t in range(0, 540, 8):
        r = 16 * (1 - t / 540)
        ang = math.radians(t * 1.6)
        stair_pts.append((sx + r * math.cos(ang), sy + r * math.sin(ang) - 30))
    c.line(stair_pts, color='umber_burnt', width=2)
    c.annotate(sx - 60, sy - 56, "it is a stair.")

    # ---- station 10 (index 9): the basket, opened ----
    kx, ky, _ = stations[9]
    open_basket = [(kx-34, ky+10), (kx-26, ky+34), (kx+26, ky+34), (kx+34, ky+10)]
    c.textured_poly(open_basket, fill='ochre_raw', hatch_color='umber_burnt', density=0.03)
    c.curve((kx-24, ky+10), (kx-34, ky-14), (kx, ky-20), (kx-8, ky+4),
             color='bistre_pale', width=2)
    c.curve((kx+24, ky+10), (kx+34, ky-14), (kx+2, ky-24), (kx+10, ky+4),
             color='bistre_pale', width=2)
    c.label(kx - 30, ky + 46, "pods 3 · turns 0 · g.leaf 1", size=11)
    c.label(kx - 20, ky + 60, "weight 0.17 g", size=11)
    c.annotate(kx + 40, ky - 20, "the basket, opened.")

    # ---- station 12 (index 11): unmarked, the kernel checked ----
    ux, uy, _ = stations[11]
    c.label(ux - 90, uy + 24, "the twelfth station, unmarked", size=12)
    kbox2 = (ux - 130, uy + 44, ux + 60, uy + 100)
    c.poly([(kbox2[0], kbox2[1]), (kbox2[2], kbox2[1]), (kbox2[2], kbox2[3]), (kbox2[0], kbox2[3])],
           fill='gold_leaf', outline='bistre', width=1)
    c.text(ux - 120, uy + 52, "ker(A) ∌ {0}", size=13, color='soot')
    c.text(ux - 120, uy + 72, "v0 = (3,0,1) · ‖v0‖ = 3.16", size=12, color='soot')
    c.annotate(ux + 70, uy + 60, "kernel: not empty.")

    # diagonal line leaving the frame
    lx, ly, _ = stations[11]
    c.arrow([(lx, ly), (lx + 300, ly + 160), (1480, 1360)], color='bistre_pale', width=2, head=12)

    # ================= legend block =================
    lgx, lgy = 1120, 400
    c.label(lgx, lgy - 20, "legend", size=13)
    r = 8
    circ1 = [(lgx + r*math.cos(math.radians(t)), lgy + r*math.sin(math.radians(t))) for t in range(0,360,30)]
    c.poly(circ1, fill='ochre_pale', outline='bistre', width=1)
    c.label(lgx + 18, lgy - 7, "station, named", size=11)

    circ2 = [(lgx + r*math.cos(math.radians(t)), lgy + 26 + r*math.sin(math.radians(t))) for t in range(0,360,30)]
    c.poly(circ2, fill=None, outline='bistre_pale', width=2)
    c.label(lgx + 18, lgy + 19, "station, unmarked", size=11)

    c.line([(lgx-8, lgy+40), (lgx+8, lgy+52), (lgx-8, lgy+64)], color='umber_burnt', width=2)
    c.label(lgx + 18, lgy + 45, "the stair", size=11)

    small_basket = [(lgx-8, lgy+80), (lgx-4, lgy+92), (lgx+8, lgy+92), (lgx+12, lgy+80)]
    c.textured_poly(small_basket, fill='ochre_raw', hatch_color='umber_burnt', density=0.03)
    c.label(lgx + 18, lgy + 78, "opened here", size=11)

    # ================= field notes, filling the lower band =================
    fny = 1180
    c.text(190, fny, "field notes:", size=13, color='bistre')
    c.text(190, fny + 22, "— pace 04, the stair: no width taken, no column recorded.", size=12, color='bistre_pale')
    c.text(190, fny + 42, "— pace 10, the basket: opened; contents entered above.", size=12, color='bistre_pale')
    c.text(190, fny + 62, "— pace 12, unmarked: omitted from the survey plate; kernel recorded regardless.", size=12, color='bistre_pale')
    c.text(190, fny + 82, "— det [pods,turns,g.leaf,basket] unchanged: 0.", size=12, color='bistre_pale')

    # ================= struck word, bottom-left =================
    c.struck(40, 1370, "EMPTY", size=15)

    # ================= verdict, bottom-right =================
    c.text(1400, 1380, "THE KERNEL IS EMPTY", size=16, color='gold_leaf', anchor='ra')
