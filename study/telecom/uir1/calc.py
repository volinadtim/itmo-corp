"""УИР 1 по ТКС: кодирование сообщения и расчёт частотных характеристик.

Запуск: python3 calc.py [C_Мбит/с]  →  data.json рядом со скриптом (его читает report.typ).

Метод расчёта частот (по лекции, слайды 26–37):
сигнал делится на участки постоянного уровня. Каждый участок длительностью T считается
полупериодом гармоники f = 1/(2T) (так на слайде 36 получены fв = C/2 для NRZ, AMI, NRZI,
MLT-3 и fв = C для RZ и манчестерского кода); при T = k·tb, tb = 1/C:
f = C/(2k). Верхняя граница fв — самая короткая полуволна, нижняя fн — самая длинная,
спектр S = fв − fн, средняя частота — среднее f, взвешенное по длительности полуволн.
"""

import json
import sys
from fractions import Fraction
from pathlib import Path

CP1251 = {}
upper = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
lower = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
for i, ch in enumerate(upper):
    CP1251[ch] = 0xC0 + i
for i, ch in enumerate(lower):
    CP1251[ch] = 0xE0 + i

MESSAGE = "ДаТН"  # Да — первые две буквы фамилии (Данилов), Т, Н — инициалы (Тимофей Николаевич)

TABLE_4B5B = {
    "0000": "11110", "0001": "01001", "0010": "10100", "0011": "10101",
    "0100": "01010", "0101": "01011", "0110": "01110", "0111": "01111",
    "1000": "10010", "1001": "10011", "1010": "10110", "1011": "10111",
    "1100": "11010", "1101": "11011", "1110": "11100", "1111": "11101",
}


# --- физические коды: уровни по полубитам (2 отсчёта на битовый интервал) ---

def nrz(bits):
    return [lv for b in bits for lv in ((1, 1) if b else (-1, -1))]


def manchester(bits):
    # «1» — переход сверху вниз в середине интервала, «0» — снизу вверх (слайд 37)
    return [lv for b in bits for lv in ((1, -1) if b else (-1, 1))]


def nrzi(bits, start=-1):
    out, lv = [], start
    for b in bits:
        if b:
            lv = -lv
        out += [lv, lv]
    return out


def ami(bits):
    out, last = [], -1
    for b in bits:
        if b:
            last = -last
            out += [last, last]
        else:
            out += [0, 0]
    return out


def mlt3(bits):
    cycle = [0, 1, 0, -1]
    out, pos = [], 0
    for b in bits:
        if b:
            pos = (pos + 1) % 4
        out += [cycle[pos]] * 2
    return out


CODES = {
    "NRZ": nrz,
    "Manchester": manchester,
    "NRZI": nrzi,
    "AMI": ami,
    "MLT-3": mlt3,
}


def half_waves(levels):
    """Длительности участков постоянного уровня (полупериодов) в полубитах."""
    runs, cur = [], 1
    for a, b in zip(levels, levels[1:]):
        if a == b:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    return runs


def analyze(levels, C):
    """C в Мбит/с; частоты в МГц (точные дроби)."""
    waves = half_waves(levels)
    groups = {}
    for w in waves:
        k = Fraction(w, 2)                      # длительность в битовых интервалах
        groups.setdefault(k, 0)
        groups[k] += 1
    rows = []
    total_t = Fraction(0)
    weighted = Fraction(0)
    for k in sorted(groups):
        f = Fraction(C) / (2 * k)
        n = groups[k]
        rows.append({"k": float(k), "f": float(f), "n": n, "t": float(n * k)})
        total_t += n * k
        weighted += f * n * k
    fv = max(r["f"] for r in rows)
    fn = min(r["f"] for r in rows)
    favg = float(weighted / total_t)
    dc = sum(levels) / len(levels)
    return {
        "rows": rows, "fv": fv, "fn": fn, "S": fv - fn, "favg": favg,
        "F3": 3 * fv, "total_t": float(total_t), "dc": dc,
        "transitions": sum(1 for a, b in zip(levels, levels[1:]) if a != b),
    }


def max_run(bits, value):
    best = cur = 0
    for b in bits:
        cur = cur + 1 if b == value else 0
        best = max(best, cur)
    return best


def to_hex(bits):
    s = "".join(map(str, bits))
    s += "0" * (-len(s) % 4)
    return " ".join(format(int(s[i:i + 8].ljust(8, "0"), 2), "02X") if len(s[i:i + 8]) == 8
                    else format(int(s[i:i + 4], 2), "X")
                    for i in range(0, len(s), 8))


def scramble(bits, taps):
    out, steps = [], []
    for i, a in enumerate(bits):
        b = a
        used = []
        for t in taps:
            j = i - t
            if j >= 0:
                b ^= out[j]
                used.append((t, out[j]))
        out.append(b)
        steps.append({"i": i + 1, "a": a, "used": [{"t": t, "v": v} for t, v in used], "b": b})
    return out, steps


def descramble(bits, taps):
    return [b ^ sum(bits[i - t] for t in taps if i - t >= 0) % 2 for i, b in enumerate(bits)]


def main():
    C = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    codes = [CP1251[ch] for ch in MESSAGE]
    bits = [int(b) for c in codes for b in format(c, "08b")]

    physical = {}
    for name, fn in CODES.items():
        lv = fn(bits)
        physical[name] = {"levels": lv, **analyze(lv, C)}

    # 4B/5B + MLT-3: чтобы сохранить полезную скорость C, битовая скорость в линии 1,25·C
    nibbles = ["".join(map(str, bits[i:i + 4])) for i in range(0, len(bits), 4)]
    enc = [TABLE_4B5B[n] for n in nibbles]
    bits45 = [int(b) for s in enc for b in s]
    C45 = C * 5 / 4
    logical_code = "MLT-3"
    lv45 = CODES[logical_code](bits45)
    r45 = {"levels": lv45, **analyze(lv45, C45)}
    r45_nrzi = analyze(nrzi(bits45), C45)

    scr = {}
    for key, taps in {"3_5": (3, 5), "5_7": (5, 7)}.items():
        sb, steps = scramble(bits, taps)
        assert descramble(sb, taps) == bits
        lv = CODES[logical_code](sb)
        scr[key] = {
            "taps": list(taps), "bits": sb, "hex": to_hex(sb), "steps": steps,
            "max0": max_run(sb, 0), "max1": max_run(sb, 1), "ones": sum(sb),
            "levels": lv, **analyze(lv, C),
        }

    data = {
        "C": C,
        "message": MESSAGE,
        "chars": [{"ch": ch, "hex": format(c, "02X"), "bin": format(c, "08b")}
                  for ch, c in zip(MESSAGE, codes)],
        "bits": bits,
        "hex": to_hex(bits),
        "max0": max_run(bits, 0), "max1": max_run(bits, 1), "ones": sum(bits),
        "physical": physical,
        "b45": {
            "nibbles": nibbles, "enc": enc, "bits": bits45, "hex": to_hex(bits45),
            "C": C45, "code": logical_code, "max0": max_run(bits45, 0),
            "max1": max_run(bits45, 1), "ones": sum(bits45),
            "res": r45, "res_nrzi": r45_nrzi,
        },
        "scr": scr,
    }
    out = Path(__file__).with_name("data.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))

    # краткая сводка в консоль
    print("msg", MESSAGE, data["hex"], "".join(map(str, bits)))
    for name, r in physical.items():
        print(f"{name:11s} fв={r['fv']:.4g} fн={r['fn']:.4g} S={r['S']:.4g} fср={r['favg']:.4g} "
              f"dc={r['dc']:+.3f} rows={[(x['k'], x['n']) for x in r['rows']]}")
    print("4B/5B", data["b45"]["hex"], "".join(map(str, bits45)))
    for nm, r in (("MLT-3", r45), ("NRZI", r45_nrzi)):
        print(f"  {nm} fв={r['fv']:.4g} fн={r['fn']:.4g} S={r['S']:.4g} fср={r['favg']:.4g}")
    for key, s in scr.items():
        print(f"scr {key} {s['hex']} max0={s['max0']} max1={s['max1']} ones={s['ones']} "
              f"fв={s['fv']:.4g} fн={s['fn']:.4g} S={s['S']:.4g} fср={s['favg']:.4g} dc={s['dc']:+.3f}")


if __name__ == "__main__":
    main()
