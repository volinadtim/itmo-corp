"""УИР 1 «Кодирование данных в телекоммуникационных системах»: все расчёты и диаграммы.

Запуск: python uir1.py  →  results.json + fig/*.png (отчёт собирает report.py).

Модель сигнала: каждый битовый интервал t_b = 1/C делится на два полуинтервала,
сигнал задаётся уровнем на каждом полуинтервале (-1, 0, +1). Частоты считаются
по участкам постоянного уровня (см. freq_segments).
"""

import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
FIG = HERE / "fig"

# --- Этап 1. Сообщение ------------------------------------------------------

FIO = "Данилов Тимофей Николаевич"
MESSAGE = "ДаТН"  # Фа + И + О
C = 10  # Мбит/с: номер в списке группы чётный (см. README)

# Кодировочная таблица из описания УИР 1 (совпадает с cp1251 для кириллицы).
TABLE = {ch: 0xC0 + i for i, ch in enumerate("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")}
TABLE |= {ch: 0xE0 + i for i, ch in enumerate("абвгдежзийклмнопрстуфхцчшщъыьэюя")}

# 4B/5B (FDDI / 100BASE-X)
B4B5 = {
    "0000": "11110", "0001": "01001", "0010": "10100", "0011": "10101",
    "0100": "01010", "0101": "01011", "0110": "01110", "0111": "01111",
    "1000": "10010", "1001": "10011", "1010": "10110", "1011": "10111",
    "1100": "11010", "1101": "11011", "1110": "11100", "1111": "11101",
}


def to_bits(text):
    codes = [TABLE[ch] for ch in text]
    return codes, "".join(f"{c:08b}" for c in codes)


def bits_to_hex(bits):
    pad = bits + "0" * (-len(bits) % 4)
    return " ".join(f"{int(pad[i:i + 8], 2):02X}" if len(pad[i:i + 8]) == 8 else f"{int(pad[i:i + 4], 2):X}"
                    for i in range(0, len(pad), 8))


def group(bits, n=4):
    return " ".join(bits[i:i + n] for i in range(0, len(bits), n))


# --- Этап 2. Физическое кодирование (уровни по полуинтервалам) --------------

def nrz(bits):
    return [lv for b in bits for lv in ([1, 1] if b == "1" else [-1, -1])]


def rz(bits):
    return [lv for b in bits for lv in ([1, 0] if b == "1" else [-1, 0])]


def ami(bits):
    out, last = [], -1
    for b in bits:
        if b == "1":
            last = -last
            out += [last, last]
        else:
            out += [0, 0]
    return out


def nrzi(bits, start=-1):
    out, lv = [], start
    for b in bits:
        if b == "1":
            lv = -lv
        out += [lv, lv]
    return out


def mlt3(bits):
    cycle, k, out = [0, 1, 0, -1], 0, []
    for b in bits:
        if b == "1":
            k = (k + 1) % 4
        out += [cycle[k]] * 2
    return out


def manchester(bits):
    # IEEE 802.3 / конспект: «1» — переход сверху вниз, «0» — снизу вверх.
    return [lv for b in bits for lv in ([1, -1] if b == "1" else [-1, 1])]


METHODS = {
    "NRZ": nrz,
    "RZ": rz,
    "AMI": ami,
    "NRZI": nrzi,
    "MLT-3": mlt3,
    "Манчестерский": manchester,
}


def runs(seq):
    """[(значение, длина)] участков постоянного значения."""
    out = []
    for x in seq:
        if out and out[-1][0] == x:
            out[-1][1] += 1
        else:
            out.append([x, 1])
    return [tuple(r) for r in out]


def freq_segments(method, bits, levels, c):
    """Разбить сигнал на участки и приписать каждому частоту, МГц.

    Возвращает [(частота, длительность в битовых интервалах)].

    - NRZ, NRZI, AMI, Манчестер: участок постоянного уровня длиной m полуинтервалов —
      это полупериод, T = 2·m·t_b/2 = m·t_b  →  f = C/m.
      Для потенциальных кодов m = 2k (k бит подряд): f = C/(2k).
    - MLT-3: за период уровень проходит четыре ступени 0 → + → 0 → − → 0, поэтому участок
      постоянного уровня — четверть периода: f = C/(2m)  (k бит → C/(4k)).
    - RZ: импульс возвращается к нулю в каждом бите, период задают соседние импульсы:
      одинаковые биты подряд (++ или −−) → T = t_b, f = C; одиночный бит между
      противоположными → T = 2·t_b, f = C/2.
    """
    c = Fraction(c)
    if method == "RZ":
        segs = []
        for bit, k in runs(bits):
            segs.append((c if k > 1 else c / 2, Fraction(k)))
        return segs
    quarter = method == "MLT-3"
    segs = []
    for _, m in runs(levels):
        f = c / (2 * m) if quarter else c / m
        segs.append((f, Fraction(m, 2)))
    return segs


def spectrum(method, bits, levels, c):
    segs = freq_segments(method, bits, levels, c)
    total = sum(d for _, d in segs)
    by_f = {}
    for f, d in segs:
        n, dur = by_f.get(f, (0, Fraction(0)))
        by_f[f] = (n + 1, dur + d)
    f_hi, f_lo = max(by_f), min(by_f)
    f_avg = sum(f * d for f, d in segs) / total
    return {
        "table": [
            {"f": float(f), "f_frac": frac_str(f / c), "segments": n, "bits": float(dur)}
            for f, (n, dur) in sorted(by_f.items(), reverse=True)
        ],
        "f_hi": float(f_hi),
        "f_lo": float(f_lo),
        "S": float(f_hi - f_lo),
        "f_avg": float(f_avg),
        "f_avg_expr": " + ".join(f"{float(f):g}·{float(dur):g}" for f, (n, dur) in sorted(by_f.items(), reverse=True))
        + f") / {float(total):g}",
        "F_q": float(3 * f_hi - f_lo),
        "total_bits": float(total),
    }


def frac_str(x):
    """Доля от C в виде C, C/2, C/6 и т.п."""
    if x == 1:
        return "C"
    if x.numerator == 1:
        return f"C/{x.denominator}"
    return f"{x.numerator}C/{x.denominator}"


def properties(method, bits, levels):
    """Объективные свойства для сравнительной таблицы."""
    level_runs = runs(levels)
    max_run_bits = max(m for _, m in level_runs) / 2
    dc = sum(levels) / len(levels)
    return {
        "levels": len(set(levels) | ({-1, 1} if method in ("NRZ", "NRZI", "Манчестерский") else {-1, 0, 1})),
        "max_const_bits": max_run_bits,
        "dc": round(dc, 3),
        "transitions": sum(1 for a, b in zip(levels, levels[1:]) if a != b),
    }


# --- Этап 4. Скремблирование ------------------------------------------------

def scramble(bits, taps):
    a = [int(b) for b in bits]
    b, steps = [], []
    for i, ai in enumerate(a):
        val, terms = ai, [f"A{i + 1}={ai}"]
        for t in taps:
            if i - t >= 0:
                val ^= b[i - t]
                terms.append(f"B{i + 1 - t}={b[i - t]}")
        b.append(val)
        steps.append(f"B{i + 1} = " + " ⊕ ".join(terms) + f" = {val}")
    return "".join(map(str, b)), steps


def descramble(bits, taps):
    b = [int(x) for x in bits]
    return "".join(str(b[i] ^ (sum(b[i - t] for t in taps if i - t >= 0) % 2)) for i in range(len(b)))


def max_run(bits, ch):
    return max((k for x, k in runs(bits) if x == ch), default=0)


# --- Диаграммы ---------------------------------------------------------------

def plot(levels, bits, title, path, bit_groups=8, three=False):
    n = len(bits)
    fig, ax = plt.subplots(figsize=(max(10, n * 0.36), 2.3))
    xs, ys = [], []
    for i, lv in enumerate(levels):
        xs += [i / 2, (i + 1) / 2]
        ys += [lv, lv]
    ax.plot(xs, ys, color="#1f4e9c", lw=2, drawstyle="default")
    for i in range(n + 1):
        ax.axvline(i, color="#bbbbbb", lw=0.6, ls=":" if i % bit_groups else "-", zorder=0)
    ax.axhline(0, color="#888888", lw=0.6)
    for i, b in enumerate(bits):
        ax.text(i + 0.5, 1.35, b, ha="center", va="bottom", fontsize=9, family="DejaVu Sans Mono")
    ax.set_xlim(0, n)
    ax.set_ylim(-1.5, 1.8)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["−U", "0", "+U"])
    ax.set_xticks(range(0, n + 1, bit_groups))
    ax.set_xticklabels([f"{i}" for i in range(0, n + 1, bit_groups)], fontsize=8)
    ax.set_xlabel("время, битовые интервалы t_b", fontsize=8)
    ax.set_title(title, fontsize=10, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


# --- Сборка -------------------------------------------------------------------

def main():
    FIG.mkdir(exist_ok=True)
    codes, bits = to_bits(MESSAGE)
    res = {
        "fio": FIO,
        "message": MESSAGE,
        "C": C,
        "hex": " ".join(f"{c:02X}" for c in codes),
        "bin": group(bits),
        "bits": bits,
        "len_bytes": len(codes),
        "len_bits": len(bits),
        "stats": {"ones": bits.count("1"), "zeros": bits.count("0"),
                  "max_ones": max_run(bits, "1"), "max_zeros": max_run(bits, "0")},
        "physical": {},
    }

    for i, (name, fn) in enumerate(METHODS.items(), 1):
        lv = fn(bits)
        sp = spectrum(name, bits, lv, C)
        res["physical"][name] = {"spectrum": sp, "props": properties(name, bits, lv), "fig": f"fig/phys_{i}.png"}
        plot(lv, bits, f"{name}: «{MESSAGE}» = {res['hex']}", HERE / f"fig/phys_{i}.png")

    # Этап 3. 4B/5B поверх MLT-3 и NRZI (линейная скорость 12,5 Мбит/с)
    c5 = Fraction(C) * Fraction(5, 4)
    nibbles = [bits[i:i + 4] for i in range(0, len(bits), 4)]
    b5 = "".join(B4B5[n] for n in nibbles)
    res["b4b5"] = {
        "mapping": [[n, B4B5[n]] for n in nibbles],
        "bin": group(b5, 5),
        "bin4": group(b5),
        "hex": bits_to_hex(b5),
        "len_bits": len(b5),
        "len_bytes": len(b5) / 8,
        "redundancy": (len(b5) - len(bits)) / len(bits),
        "C_line": float(c5),
        "max_ones": max_run(b5, "1"),
        "max_zeros": max_run(b5, "0"),
        "coded": {},
    }
    for name in ("MLT-3", "NRZI"):
        lv = METHODS[name](b5)
        tag = name.replace("-", "").lower()
        res["b4b5"]["coded"][name] = {"spectrum": spectrum(name, b5, lv, c5), "props": properties(name, b5, lv),
                                       "fig": f"fig/b4b5_{tag}.png"}
        plot(lv, b5, f"4B/5B + {name}: {res['b4b5']['hex']}  (C' = {float(c5):g} Мбит/с)",
             HERE / f"fig/b4b5_{tag}.png", bit_groups=5)

    # Этап 4. Скремблирование: оба полинома из задания
    res["scramble"] = {}
    for key, taps in (("3,5", (3, 5)), ("5,7", (5, 7))):
        sb, steps = scramble(bits, taps)
        assert descramble(sb, taps) == bits
        entry = {"taps": list(taps), "bin": group(sb), "bits": sb, "hex": bits_to_hex(sb), "steps": steps,
                 "max_ones": max_run(sb, "1"), "max_zeros": max_run(sb, "0"), "ones": sb.count("1"), "coded": {}}
        for name in ("MLT-3", "NRZI"):
            lv = METHODS[name](sb)
            entry["coded"][name] = {"spectrum": spectrum(name, sb, lv, C), "props": properties(name, sb, lv)}
        res["scramble"][key] = entry
    best = res["scramble"]["3,5"]
    for name in ("MLT-3", "NRZI"):
        tag = name.replace("-", "").lower()
        best["coded"][name]["fig"] = f"fig/scr_{tag}.png"
        plot(METHODS[name](best["bits"]), best["bits"], f"Скремблирование Bi = Ai ⊕ Bi−3 ⊕ Bi−5 + {name}: {best['hex']}",
             HERE / f"fig/scr_{tag}.png")
    alt = res["scramble"]["5,7"]
    plot(METHODS["MLT-3"](alt["bits"]), alt["bits"], f"Скремблирование Bi = Ai ⊕ Bi−5 ⊕ Bi−7 + MLT-3: {alt['hex']}",
         HERE / "fig/scr57_mlt3.png")

    (HERE / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    # краткий вывод
    print(MESSAGE, res["hex"], res["bin"], res["stats"])
    for name, r in res["physical"].items():
        s = r["spectrum"]
        print(f"{name:14} fв={s['f_hi']:<6g} fн={s['f_lo']:<8.4g} S={s['S']:<8.4g} fср={s['f_avg']:.3f}  {r['props']}")
    print("4B/5B", res["b4b5"]["bin"], res["b4b5"]["hex"], res["b4b5"]["max_ones"], res["b4b5"]["max_zeros"])
    for name, r in res["b4b5"]["coded"].items():
        s = r["spectrum"]
        print(f"  4B5B+{name:6} fв={s['f_hi']:<6g} fн={s['f_lo']:<8.4g} S={s['S']:<8.4g} fср={s['f_avg']:.3f} {r['props']}")
    for key, e in res["scramble"].items():
        print("scr", key, e["bin"], e["hex"], "max1", e["max_ones"], "max0", e["max_zeros"])
        for name, r in e["coded"].items():
            s = r["spectrum"]
            print(f"  {name:6} fв={s['f_hi']:<6g} fн={s['f_lo']:<8.4g} S={s['S']:<8.4g} fср={s['f_avg']:.3f} {r['props']}")


if __name__ == "__main__":
    main()
