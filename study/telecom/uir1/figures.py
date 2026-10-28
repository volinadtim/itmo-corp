"""Рисунки для defense-theory.typ: python3 figures.py  (SVG в fig/, без сторонних библиотек)."""
import math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family='Helvetica, Arial, sans-serif'"
BLUE, RED, GREY, GREEN, ORANGE = "#1f5fa8", "#c0392b", "#888", "#2e8b57", "#d98200"

def bits(h): return [int(c) for b in bytes.fromhex(h) for c in f"{b:08b}"]
A = bits("C4E0D2CD")
f45 = {'0':'11110','1':'01001','2':'10100','3':'10101','4':'01010','5':'01011','6':'01110','7':'01111',
       '8':'10010','9':'10011','A':'10110','B':'10111','C':'11010','D':'11011','E':'11100','F':'11101'}
E = [int(c) for ch in "C4E0D2CD" for c in f45[ch]]
def scr(a, j, k, init=0):
    B = []
    for i in range(len(a)):
        g = lambda d: B[i-d] if i-d >= 0 else init
        B.append(a[i] ^ g(j) ^ g(k))
    return B

# уровни по полубитам: список (уровень первой половины, уровень второй)
def nrz(b): return [(1 if x else -1,)*2 for x in b]
def rz(b): return [((1 if x else -1), 0) for x in b]
def ami(b):
    out, s = [], 1
    for x in b:
        if x: out.append((s, s)); s = -s
        else: out.append((0, 0))
    return out
def mlt3(b):
    lv, s, out = [0, 1, 0, -1], 0, []
    for x in b:
        if x: s = (s+1) % 4
        out.append((lv[s],)*2)
    return out
def manch(b): return [((1, -1) if x else (-1, 1)) for x in b]

def svg_open(w, h): return [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}'>",
                           f"<rect width='{w}' height='{h}' fill='white'/>"]
def text(x, y, s, size=11, anchor="start", fill="#222", weight="normal"):
    return f"<text x='{x}' y='{y}' {FONT} font-size='{size}' text-anchor='{anchor}' fill='{fill}' font-weight='{weight}'>{s}</text>"
def line(x1, y1, x2, y2, c="#222", w=1, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{c}' stroke-width='{w}'{d}/>"
def rect(x, y, w, h, fill="none", stroke="#222", sw=1, rx=0):
    return f"<rect x='{x:.1f}' y='{y:.1f}' width='{w:.1f}' height='{h:.1f}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}' rx='{rx}'/>"

def wave_path(halves, x0, bw, ymid, amp, color):
    pts, prev = [], None
    for i, (a, b) in enumerate(halves):
        for k, lvl in enumerate((a, b)):
            x = x0 + (i + k*0.5)*bw
            y = ymid - lvl*amp
            if prev is not None and prev != y: pts.append((x, prev))
            if prev is None or prev != y: pts.append((x, y))
            prev = y
    pts.append((x0 + len(halves)*bw, prev))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f"<path d='{d}' fill='none' stroke='{color}' stroke-width='2' stroke-linejoin='round'/>"

def row(parts, label, halves, x0, bw, ymid, amp, color, levels3=False, nbits=None):
    n = len(halves)
    parts.append(text(x0-8, ymid+4, label, 12, "end", weight="bold"))
    parts.append(line(x0, ymid, x0+n*bw, ymid, "#bbb", 0.7, "3,3"))
    if levels3:
        for lv, t in ((1, "+"), (-1, "−")):
            parts.append(line(x0, ymid-lv*amp, x0+n*bw, ymid-lv*amp, "#ddd", 0.6, "2,3"))
    parts.append(wave_path(halves, x0, bw, ymid, amp, color))

def grid(parts, x0, bw, n, top, bottom, group=8):
    for i in range(n+1):
        heavy = (i % group == 0)
        parts.append(line(x0+i*bw, top, x0+i*bw, bottom, "#444" if heavy else "#e4e4e4", 1 if heavy else 0.6))

def bitrow(parts, bs, x0, bw, y, group=8, names=None):
    for i, b in enumerate(bs):
        parts.append(text(x0+(i+0.5)*bw, y, str(b), 12, "middle", weight="bold"))
    if names:
        for g, nm in enumerate(names):
            parts.append(text(x0+(g*group+group/2)*bw, y-16, nm, 11, "middle", "#555"))

def save(name, parts, w=None):
    parts.append("</svg>")
    open(os.path.join(OUT, name), "w").write("\n".join(parts))

# ---------- 1. гармоники ----------
def fig_harmonics():
    W, H = 760, 300; x0, x1 = 50, 730; ym = 150; amp = 90
    p = svg_open(W, H)
    p.append(text(W/2, 20, "Прямоугольный сигнал и его разложение в ряд Фурье", 13, "middle", weight="bold"))
    N = 600
    def sq(t): return 1 if math.sin(2*math.pi*t) >= 0 else -1
    def approx(t, ks): return 4/math.pi*sum(math.sin(2*math.pi*k*t)/k for k in ks)
    T = 2.0
    def path(f, color, w=1.6, dash=None):
        pts = []
        for i in range(N+1):
            t = T*i/N; pts.append(f"{x0+(x1-x0)*i/N:.1f},{ym-amp*f(t):.1f}")
        d = f" stroke-dasharray='{dash}'" if dash else ""
        return f"<path d='M{' L'.join(pts)}' fill='none' stroke='{color}' stroke-width='{w}'{d}/>"
    p.append(line(x0, ym, x1, ym, "#bbb", 0.8))
    p.append(path(sq, "#bbb", 3))
    p.append(path(lambda t: approx(t, [1]), BLUE, 1.8))
    p.append(path(lambda t: approx(t, [1, 3]), GREEN, 1.8))
    p.append(path(lambda t: approx(t, [1, 3, 5, 7]), RED, 1.8))
    lx = 60
    for c, s in ((("#bbb"), "идеальный меандр"), (BLUE, "только f₀"), (GREEN, "f₀ + 3f₀ (амплитуда 1/3)"), (RED, "f₀ + 3f₀ + 5f₀ + 7f₀")):
        p.append(line(lx, 270, lx+22, 270, c, 3)); p.append(text(lx+28, 274, s, 11)); lx += 28 + 7*len(s) + 14
    p.append(text(W/2, 292, "Чем больше гармоник пропускает канал, тем точнее форма. Основная гармоника: f₀ = C/2 для 1010… в NRZ", 11, "middle", "#555"))
    save("harmonics.svg", p)

# ---------- 2. все коды на сообщении ----------
def fig_codes():
    n = 32; x0, bw = 80, 20.5; W = x0 + n*bw + 15
    rows = [("NRZ", nrz(A), BLUE, False), ("RZ", rz(A), RED, True), ("AMI", ami(A), GREEN, True),
            ("MLT-3", mlt3(A), ORANGE, True), ("Манчестер", manch(A), "#7b3fa0", False)]
    rh = 62; top = 74; H = top + rh*len(rows) + 30
    p = svg_open(W, H)
    p.append(text(W/2, 16, "Сообщение C4 E0 D2 CD в пяти физических кодах (C = 10 Мбит/с)", 13, "middle", weight="bold"))
    grid(p, x0, bw, n, top-10, top+rh*len(rows)-10)
    # серия из 5 нулей: биты 12..16 (индексы 11..15)
    p.append(rect(x0+11*bw, top-10, 5*bw, rh*len(rows), "#fff0f0", "none"))
    p.append(f"<g opacity='0.9'>{rect(x0+11*bw, top-10, 5*bw, rh*len(rows), 'none', RED, 1.2)}</g>")
    p.append(text(x0+13.5*bw, top+rh*len(rows)+10, "5 нулей подряд", 11, "middle", RED, "bold"))
    bitrow(p, A, x0, bw, top-16, names=["C4", "E0", "D2", "CD"])
    for i, (nm, h, c, l3) in enumerate(rows):
        row(p, nm, h, x0, bw, top+rh*i+rh/2-10, 17, c, l3)
    save("codes.svg", p)

# ---------- 3. полуволны NRZ ----------
def fig_halfwave():
    n = 32; x0, bw = 30, 21.3; W = x0 + n*bw + 20; H = 240
    p = svg_open(W, H)
    p.append(text(W/2, 16, "NRZ: участки постоянного уровня = полуволны, f = C/(2L)", 13, "middle", weight="bold"))
    grid(p, x0, bw, n, 60, 140)
    bitrow(p, A, x0, bw, 54, names=["C4", "E0", "D2", "CD"])
    p.append(wave_path(nrz(A), x0, bw, 96, 28, BLUE))
    # участки
    runs, i = [], 0
    while i < n:
        j = i
        while j < n and A[j] == A[i]: j += 1
        runs.append((i, j-i)); i = j
    col = {1: GREEN, 2: ORANGE, 3: "#7b3fa0", 5: RED}
    for k, (s, L) in enumerate(runs):
        c = col[L]; xa, xb = x0+s*bw+2, x0+(s+L)*bw-2; y = 150 + (k % 2)*0
        p.append(line(xa, y, xb, y, c, 3))
        p.append(line(xa, y-4, xa, y+4, c, 1.5)); p.append(line(xb, y-4, xb, y+4, c, 1.5))
        p.append(text((xa+xb)/2, y+16, f"L={L}", 10, "middle", c, "bold"))
    lx = 30
    for L, c in col.items():
        f = 10/(2*L)
        s = f"L = {L}τ → f = {round(f, 2):g} МГц".replace(".", ",")
        p.append(line(lx, 205, lx+16, 205, c, 3)); p.append(text(lx+22, 209, s, 11)); lx += 170
    p.append(text(W/2, 226, "fв = 5 МГц (самый короткий, L=1), fн = 1 МГц (самый длинный, L=5), S = 4 МГц", 11, "middle", "#555"))
    save("halfwave.svg", p)

# ---------- 4. MLT-3: автомат + полуволны с краями ----------
def mlt_runs(b):
    out = [v[0] for v in mlt3(b)]
    r = []
    for v in out:
        if r and r[-1][0] == v: r[-1][1] += 1
        else: r.append([v, 1])
    return r
def fig_mlt3():
    n = 32; x0, bw = 60, 20.5; W = x0 + n*bw + 20; H = 380
    p = svg_open(W, H)
    p.append(text(W/2, 16, "MLT-3: цикл уровней и полуволны на сообщении C4 E0 D2 CD", 13, "middle", weight="bold"))
    # автомат
    cx = [150, 270, 390, 510]; lab = ["0", "+", "0", "−"]
    for i, x in enumerate(cx):
        p.append(f"<circle cx='{x}' cy='62' r='18' fill='#fff7e6' stroke='{ORANGE}' stroke-width='1.6'/>")
        p.append(text(x, 67, lab[i], 15, "middle", weight="bold"))
        nx = cx[(i+1) % 4] if i < 3 else None
        if nx: p.append(line(x+18, 62, nx-18, 62, "#444", 1.4)); p.append(text((x+nx)/2, 55, "1", 11, "middle", RED, "bold"))
    p.append(f"<path d='M510,80 Q330,118 150,80' fill='none' stroke='#444' stroke-width='1.4'/>")
    p.append(text(330, 108, "1", 11, "middle", RED, "bold"))
    p.append(text(600, 66, "на 1: следующий уровень", 11, "start"))
    p.append(text(600, 82, "на 0: уровень сохраняется", 11, "start"))
    top = 165
    grid(p, x0, bw, n, top-6, top+110)
    bitrow(p, A, x0, bw, top-12, names=["C4", "E0", "D2", "CD"])
    ym, amp = top+50, 34
    p.append(line(x0, ym, x0+n*bw, ym, "#bbb", 0.7, "3,3"))
    p.append(wave_path(mlt3(A), x0, bw, ym, amp, ORANGE))
    p.append(text(x0-8, ym-amp+4, "+", 12, "end")); p.append(text(x0-8, ym+4, "0", 12, "end")); p.append(text(x0-8, ym+amp+4, "−", 12, "end"))
    # полуволны
    r = mlt_runs(A); pos = 0; pulses = []
    for k, (v, L) in enumerate(r):
        if v != 0:
            gb = r[k-1][1] if k > 0 else 0
            ga = r[k+1][1] if k < len(r)-1 else 0
            pulses.append((pos, L, gb, ga, k == 0 or k == len(r)-1, k == 0))
        pos += L
    for idx, (s, L, gb, ga, edge, first) in enumerate(pulses):
        full = L + (gb if gb else 0)*(0.5) + (ga if ga else 0)*0.5
        rep = L + (gb/2 if not (edge and not first) else gb) + (ga/2 if not (edge and first) else ga)
        # отчёт: у первого — весь gap после, у последнего — весь gap до
        y = top+122 + (idx % 2)*28
        xa = x0 + (s - gb/2)*bw if gb else x0 + s*bw
        xb = x0 + (s + L + ga/2)*bw if ga else x0 + (s+L)*bw
        c = RED if edge else BLUE
        p.append(line(xa+1, y, xb-1, y, c, 3))
        lbl = f"{full:g}" if not edge else f"{full:g} / {rep:g}"
        p.append(text((xa+xb)/2, y+14, lbl.replace('.', ','), 10, "middle", c, "bold"))
    p.append(text(W/2, H-22, "Синее: полуволна = импульс + половины соседних нулевых участков (в τ).", 11, "middle", "#333"))
    p.append(text(W/2, H-6, "Красное — краевые импульсы: «пополам / как в отчёте» (там нулевой участок со стороны сообщения берётся целиком).", 11, "middle", RED))
    save("mlt3.svg", p)

# ---------- 5. 4B/5B + MLT-3 ----------
def fig_4b5b():
    n = 40; x0, bw = 50, 16.7; W = x0 + n*bw + 15; H = 260
    p = svg_open(W, H)
    p.append(text(W/2, 16, "4B/5B + MLT-3 для C4 E0 D2 CD: 32 бита → 40 бит, линия 12,5 Мбит/с", 13, "middle", weight="bold"))
    src = ["C", "4", "E", "0", "D", "2", "C", "D"]
    nib = [f"{int(c,16):04b}" for c in "C4E0D2CD"]
    for g in range(8):
        xs = x0+g*5*bw
        p.append(rect(xs+1, 28, 5*bw-2, 18, "#eef4fb", BLUE, 0.8, 3))
        p.append(text(xs+2.5*bw, 41, f"{src[g]} = {nib[g]}", 10, "middle", BLUE, "bold"))
        p.append(f"<path d='M{xs+2.5*bw},47 L{xs+2.5*bw},57' stroke='#555' stroke-width='1' marker-end='url(#a)'/>")
    p.insert(2, "<defs><marker id='a' markerWidth='6' markerHeight='6' refX='3' refY='5' orient='auto'><path d='M0,0 L3,6 L6,0z' fill='#555'/></marker></defs>")
    for g in range(8):
        xs = x0+g*5*bw
        p.append(rect(xs+1, 58, 5*bw-2, 18, "#fff7e6", ORANGE, 0.8, 3))
    grid(p, x0, bw, n, 58, 200, group=5)
    bitrow(p, E, x0, bw, 71, group=5)
    ym = 150
    p.append(line(x0, ym, x0+n*bw, ym, "#bbb", 0.7, "3,3"))
    p.append(wave_path(mlt3(E), x0, bw, ym, 34, ORANGE))
    p.append(text(x0-6, ym-30, "+", 12, "end")); p.append(text(x0-6, ym+4, "0", 12, "end")); p.append(text(x0-6, ym+38, "−", 12, "end"))
    p.append(text(W/2, 220, "Серии: не больше 2 нулей и 4 единиц подряд; 4B/5B гарантирует ≤ 3 нулей для любых данных.", 11, "middle"))
    p.append(text(W/2, 238, "Hex: D2 B9 ED D3 5B. Избыточность (40−32)/32 = 25 %. Частоты считаются для τ' = 0,08 мкс.", 11, "middle", "#555"))
    save("4b5b.svg", p)

# ---------- 6. схема скремблера ----------
def fig_scrambler():
    W, H = 760, 270; p = svg_open(W, H)
    p.insert(2, "<defs><marker id='a' markerWidth='7' markerHeight='7' refX='6' refY='3.5' orient='auto'><path d='M0,0 L7,3.5 L0,7z' fill='#444'/></marker></defs>")
    p.append(text(W/2, 18, "Скремблер Bᵢ = Aᵢ ⊕ Bᵢ₋₅ ⊕ Bᵢ₋₇ (регистр сдвига на 7 разрядов)", 13, "middle", weight="bold"))
    bx0, by, bwid = 120, 150, 52
    for k in range(7):
        x = bx0 + k*(bwid+10)
        fill = "#fff0f0" if k+1 in (5, 7) else "#f4f4f4"
        p.append(rect(x, by, bwid, 34, fill, RED if k+1 in (5, 7) else "#444", 1.4, 3))
        p.append(text(x+bwid/2, by+21, f"Bᵢ₋{k+1}", 12, "middle", weight="bold"))
        if k < 6: p.append(line(x+bwid, by+17, x+bwid+10, by+17, "#444", 1.2))
    # вход A и сумматоры
    ax = 60; ay = 60
    p.append(text(ax-20, ay+4, "Aᵢ", 13, "end", weight="bold"))
    xor1, xor2 = 250, 480
    def xor(x, y):
        return f"<circle cx='{x}' cy='{y}' r='11' fill='white' stroke='#222' stroke-width='1.4'/>" + line(x-7, y, x+7, y, "#222", 1.4) + line(x, y-7, x, y+7, "#222", 1.4)
    p.append(line(ax-14, ay, xor1-11, ay, "#444", 1.4)); p.append(xor(xor1, ay))
    p.append(line(xor1+11, ay, xor2-11, ay, "#444", 1.4)); p.append(xor(xor2, ay))
    p.append(line(xor2+11, ay, 690, ay, "#444", 1.4)); p.append(text(700, ay+4, "Bᵢ", 13, weight="bold"))
    # отводы
    def tap(k, xr):
        x = bx0 + (k-1)*(bwid+10) + bwid/2
        p.append(line(x, by, x, ay+20, RED, 1.4)); p.append(line(x, ay+20, xr, ay+20, RED, 1.4))
        p.append(line(xr, ay+20, xr, ay+11, RED, 1.4))
    tap(5, xor1); tap(7, xor2)
    # обратная связь Bᵢ → первый разряд
    p.append(line(640, ay, 640, 215, "#444", 1.4)); p.append(line(640, 215, bx0-30, 215, "#444", 1.4))
    p.append(line(bx0-30, 215, bx0-30, by+17, "#444", 1.4)); p.append(line(bx0-30, by+17, bx0-1, by+17, "#444", 1.4))
    p.append(text(370, 232, "новый бит Bᵢ записывается в регистр, остальные сдвигаются вправо", 11, "middle", "#555"))
    p.append(text(W/2, 258, "Дескремблер: Cᵢ = Bᵢ ⊕ Bᵢ₋₅ ⊕ Bᵢ₋₇ = Aᵢ, но регистр хранит принятые B (поэтому 1 ошибка портит биты i, i+5, i+7)", 11, "middle", "#333"))
    save("scrambler.svg", p)

# ---------- 7. полосы ----------
def fig_bands():
    items = [("NRZ", 1, 5, BLUE), ("RZ", 5, 10, RED), ("AMI", 1.43, 5, GREEN), ("MLT-3", 0.91, 1.67, ORANGE),
             ("Манчестер", 5, 10, "#7b3fa0"), ("4B/5B + MLT-3", 1.25, 3.13, "#2a2a2a"), ("Скрембл. 5/7 + MLT-3", 0.83, 2.5, "#117a8b"),
             ("Инверсия + MLT-3", 1.0, 2.5, "#8a6d3b")]
    W = 760; x0, x1 = 190, 730; top = 44; rh = 30; H = top + rh*len(items) + 50
    p = svg_open(W, H)
    p.append(text(W/2, 18, "Полоса, которую должен пропускать канал: от fн до fв (по отчёту)", 13, "middle", weight="bold"))
    sx = lambda f: x0 + (x1-x0)*f/10
    for f in range(0, 11):
        p.append(line(sx(f), top-10, sx(f), top+rh*len(items), "#e4e4e4", 0.7)); p.append(text(sx(f), top+rh*len(items)+14, str(f), 11, "middle", "#555"))
    p.append(text(x1, top+rh*len(items)+32, "МГц", 11, "end", "#555"))
    for i, (nm, a, b, c) in enumerate(items):
        y = top+i*rh
        p.append(text(x0-8, y+15, nm, 12, "end"))
        p.append(rect(sx(a), y+4, sx(b)-sx(a), 18, c, "none", 0, 2))
        lbl = f"{a:g}…{b:g}  (S={b-a:.2f})".replace(".", ",")
        if b >= 9: p.append(text(sx(a)-6, y+17, lbl, 10, "end", "#333"))
        else: p.append(text(sx(b)+6, y+17, lbl, 10, "start", "#333"))
    save("bands.svg", p)

if __name__ == "__main__":
    for f in (fig_harmonics, fig_codes, fig_halfwave, fig_mlt3, fig_4b5b, fig_scrambler, fig_bands): f()
    print(sorted(os.listdir(OUT)))
