def draw(c, P):
    import random, math
    random.seed(c.seed)

    # ---------- carried motifs, drawn first, small and labelled ----------

    # 1. gold leaf, one square
    gx, gy = 110, 200
    c.poly([(gx-14, gy-14), (gx+14, gy-14), (gx+14, gy+14), (gx-14, gy+14)],
           fill='gold_leaf', outline='bistre', width=1)
    c.label(gx-46, gy+22, "gold leaf, one square", size=12)
    c.label(gx-30, gy+38, "0.03 g · rank 1", size=11)

    # 2. the cardamom game (cloth + pods)
    cxx, cyy = 520, 200
    c.poly([(cxx-70, cyy-18), (cxx+70, cyy-18), (cxx+70, cyy+18), (cxx-70, cyy+18)],
           fill='ochre_pale', outline='umber_burnt', width=1)
    for i in range(5):
        px = cxx - 54 + i * 27
        pts = c.blob(px, cyy, 8, n=7, irregular=0.32, seed=c.seed + i)
        c.poly(pts, fill='verdigris', outline='umber_burnt', width=1)
    c.label(cxx-58, cyy+30, "the cardamom game", size=12)
    c.annotate(cxx-40, cyy-42, "we left the cloth.")

    # 3. the rock, three names
    rxx, ryy = 950, 200
    rpts = c.blob(rxx, ryy, 32, n=11, irregular=0.35, seed=c.seed + 9)
    c.textured_poly(rpts, fill='slate', hatch_color='bone_black', density=0.02)
    c.label(rxx-52, ryy+40, "the rock, three names", size=12)

    # ---------- heading ----------
    c.title(P["roman"] + " / " + P["title"], P["sub"], P["sub2"])

    # ---------- section a / pods entered by weight ----------
    ax0, ay0 = 780, 300
    c.text(ax0, ay0, "a/ pods entered by weight", size=14, color='bistre')
    c.ruled(ay0 + 20, ay0 + 20 + 14*26 + 10, step=26, numbers=False,
            x0=ax0-10, x1=1380)

    ry = ay0 + 36
    total_w = 0.0
    for i in range(1, 15):
        seeds = 14
        w = round(seeds * 0.1, 1)
        total_w += w
        val = round(w * 0.6, 2)
        icon = c.blob(ax0+10, ry+6, 6, n=6, irregular=0.4, seed=c.seed + 100 + i)
        c.poly(icon, fill='verdigris', outline='umber_burnt', width=1)
        c.text(ax0+30, ry, f"pod {i:02d}", size=12, color='bistre')
        c.text(ax0+160, ry, f"{seeds} seeds", size=12, color='bistre')
        c.text(ax0+300, ry, f"{w:.1f} g", size=12, color='bistre')
        c.text(ax0+420, ry, f"{val:.2f} sc.", size=12, color='bistre')
        ry += 26

    ry += 10
    c.text(ax0, ry, f"subtotal — {total_w:.1f} g", size=13, color='bistre')
    c.annotate(ax0+270, ry, "basket left untouched.")

    # ---------- section b / the tally of returns ----------
    bx0, by0 = 90, 800
    c.text(bx0, by0, "b/ the tally of returns", size=14, color='bistre')
    c.label(bx0, by0+22, "hand", size=11)
    c.label(bx0+160, by0+22, "pods", size=11)
    c.label(bx0+280, by0+22, "weight", size=11)
    c.label(bx0+400, by0+22, "turns", size=11)
    c.label(bx0+520, by0+22, "status", size=11)

    hands = ["first hand", "second hand", "third hand", "fourth hand",
             "fifth hand", "sixth hand", "seventh hand"]
    pods_captured = [12, 9, 15, 7, 11, 10, 14]
    turns_taken = [21, 18, 27, 15, 20, 19, 25]

    ryb = by0 + 48
    for i, (nm, pc, tn) in enumerate(zip(hands, pods_captured, turns_taken)):
        w = round(pc * 0.1, 1)
        icon = c.blob(bx0-14, ryb+6, 7, n=7, irregular=0.3, seed=c.seed + 200 + i)
        c.poly(icon, fill='ochre_raw', outline='bistre', width=1)
        c.text(bx0, ryb, nm, size=12, color='bistre')
        c.text(bx0+160, ryb, f"{pc}", size=12, color='bistre')
        c.text(bx0+280, ryb, f"{w:.1f} g", size=12, color='bistre')
        c.text(bx0+400, ryb, f"{tn}", size=12, color='bistre')
        if i == 6:
            c.struck(bx0+520, ryb, "returned", size=13)
            c.annotate(bx0+520, ryb+22, "six came down.")
        else:
            c.text(bx0+520, ryb, "returned", size=12, color='bistre')
        ryb += 32

    # ---------- balance, drawn once ----------
    bxx, byy = 1180, 1150
    c.line([(bxx-70, byy), (bxx+70, byy)], color='bistre', width=3)
    c.line([(bxx, byy-46), (bxx, byy+6)], color='bistre', width=2)
    lp = c.blob(bxx-70, byy+26, 18, n=8, irregular=0.25, seed=c.seed+300)
    rp = c.blob(bxx+70, byy+26, 18, n=8, irregular=0.25, seed=c.seed+301)
    c.line([(bxx-70, byy), (bxx-70, byy+10)], color='bistre', width=2)
    c.line([(bxx+70, byy), (bxx+70, byy+10)], color='bistre', width=2)
    c.textured_poly(lp, fill='plaster_dark', hatch_color='umber_burnt', density=0.015)
    c.textured_poly(rp, fill='plaster_dark', hatch_color='umber_burnt', density=0.015)
    c.label(bxx-56, byy+56, "the balance of norms", size=11)
    c.annotate(bxx-20, byy-70, "no wart here.")

    # ---------- struck word, bottom-left ----------
    c.struck(40, 1370, "returned", size=15)

    # ---------- verdict, bottom-right ----------
    c.text(1400, 1380, "ALL HOLDINGS ACCOUNTED FOR", size=16, color='bistre', anchor='ra')
