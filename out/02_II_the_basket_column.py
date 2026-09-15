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

    # 2. the cardamom game
    cxx = 390
    c.poly([(cxx-64, my-16), (cxx+64, my-16), (cxx+64, my+16), (cxx-64, my+16)],
           fill='ochre_pale', outline='umber_burnt', width=1)
    for i in range(5):
        px = cxx - 50 + i * 25
        pts = c.blob(px, my, 7, n=7, irregular=0.32, seed=c.seed + i)
        c.poly(pts, fill='verdigris', outline='umber_burnt', width=1)
    c.label(cxx-58, my+30, "the cardamom game", size=12)

    # 3. the balance of norms
    bxx = 670
    c.line([(bxx-40, my), (bxx+40, my)], color='bistre_pale', width=3)
    c.line([(bxx, my-26), (bxx, my+4)], color='bistre_pale', width=2)
    lp = c.blob(bxx-40, my+18, 12, n=8, irregular=0.25, seed=c.seed+40)
    rp = c.blob(bxx+40, my+18, 12, n=8, irregular=0.25, seed=c.seed+41)
    c.textured_poly(lp, fill='plaster_dark', hatch_color='umber_burnt', density=0.02)
    c.textured_poly(rp, fill='plaster_dark', hatch_color='umber_burnt', density=0.02)
    c.label(bxx-56, my+40, "the balance of norms", size=12)

    # 4. the tally of returns (small ledger icon)
    txx = 950
    c.poly([(txx-40, my-20), (txx+40, my-20), (txx+40, my+20), (txx-40, my+20)],
           fill=None, outline='bistre_pale', width=1)
    for i in range(1, 3):
        c.line([(txx-40, my-20+i*13.3), (txx+40, my-20+i*13.3)], color='bistre_pale', width=1)
    for i in range(1, 3):
        c.line([(txx-40+i*26.6, my-20), (txx-40+i*26.6, my+20)], color='bistre_pale', width=1)
    c.label(txx-52, my+30, "the tally of returns", size=12)

    # 5. NEW: the basket, unopened
    kxx = 1230
    basket_pts = [(kxx-38, my-8), (kxx-30, my+20), (kxx+30, my+20), (kxx+38, my-8)]
    c.textured_poly(basket_pts, fill='ochre_raw', hatch_color='umber_burnt',
                     density=0.03, extra_colors=('bistre',))
    c.curve((kxx-20, my-8), (kxx-10, my-26), (kxx+10, my-26), (kxx+20, my-8),
             color='bistre_pale', width=2)
    c.label(kxx-40, my+30, "the basket, unopened", size=12)
    c.annotate(kxx-30, my-46, "it is a basket.")

    # ================= heading =================
    c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"])

    # ================= the assessment matrix =================
    mx, myy = 190, 380
    cw, ch = 14, 25
    cols, rows = 56, 10
    p = c.panel(mx, myy, cols, rows, cell=(cw, ch), bg='bistre', fg='gold_leaf')

    col_name, col_date, col_pods, col_turns, col_gold, col_basket, col_norm = 0, 13, 20, 26, 32, 39, 48

    p.put(col_name, 0, "hand", color='ochre_pale')
    p.put(col_date, 0, "day", color='ochre_pale')
    p.put(col_pods, 0, "pods", color='ochre_pale')
    p.put(col_turns, 0, "turns", color='ochre_pale')
    p.put(col_gold, 0, "g.leaf", color='ochre_pale')
    p.put(col_basket, 0, "basket", color='verdigris_bright')
    p.put(col_norm, 0, "‖v‖", color='verdigris_bright')

    names = ["first hand", "second hand", "third hand", "fourth hand",
             "fifth hand", "sixth hand", "seventh hand"]
    days = [3, 5, 7, 9, 11, 13, 15]
    pods = [12, 9, 15, 7, 11, 10, 14]
    turns = [21, 18, 27, 15, 20, 19, 25]
    gold = [0, 0, 1, 0, 0, 0, 0]

    for i, nm in enumerate(names):
        rr = i + 1
        norm = math.sqrt(pods[i]**2 + turns[i]**2 + gold[i]**2)
        if i < 6:
            p.put(col_name, rr, nm, color='gold_leaf')
            p.put(col_date, rr, f"d{days[i]:02d}")
            p.put(col_pods, rr, f"{pods[i]}")
            p.put(col_turns, rr, f"{turns[i]}")
            p.put(col_gold, rr, f"{gold[i]}")
            p.bar(col_basket, rr, 4, color='bistre_pale')
            p.put(col_norm, rr, f"{norm:.2f}", color='verdigris_bright')
        else:
            p.strike(col_name, rr, nm)
            p.strike(col_date, rr, f"d{days[i]:02d}")
            p.strike(col_pods, rr, f"{pods[i]}")
            p.strike(col_turns, rr, f"{turns[i]}")
            p.strike(col_gold, rr, f"{gold[i]}")
            p.strike(col_basket, rr, "----")
            p.strike(col_norm, rr, f"{norm:.2f}")

    # blank row 8, determinant row 9
    p.rule(8, 0, cols - 1, dotted=True, color='bistre_pale')
    p.put(col_name, 9, "det [pods,turns,g.leaf,basket]", color='ochre_pale')
    p.hl(col_norm, 9, "0", bg='gold_leaf', fg='soot')

    # frame + column separators
    p.box(0, 0, cols - 1, rows - 1, color='bistre_pale')
    p.vrule(col_basket - 1, 0, rows - 1, color='verdigris_bright')
    p.vrule(col_norm - 1, 0, rows - 1, color='verdigris_bright')

    # ================= second-hand notes on the matrix =================
    px_basket = mx + col_basket * cw
    py_header = myy - 6
    c.annotate(px_basket - 6, py_header, "unopened, not zero.")

    px_norm = mx + col_norm * cw
    c.annotate(px_norm - 10, py_header, "six pans, six norms.")

    px_row7 = mx + (col_norm + 8) * cw
    py_row7 = myy + 7 * ch + 6
    c.annotate(px_row7, py_row7, "row 7 stays struck.")

    # ================= struck word, bottom-left =================
    c.struck(40, 1370, "RANK ZERO", size=15)

    # ================= verdict, bottom-right =================
    c.text(1400, 1380, "THE KERNEL IS EMPTY", size=16, color='gold_leaf', anchor='ra')
