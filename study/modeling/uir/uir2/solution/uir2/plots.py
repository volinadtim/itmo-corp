"""Рисунки: схемы систем, размеченные графы переходов, зависимости от λ."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

from .model import Model  # noqa: E402

# Категориальные цвета (фиксированный порядок): СИСТЕМА_1, СИСТЕМА_2, П3.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#222222", "#666666", "#dddddd"
SYSTEM_STYLE = {
    "СИСТЕМА_1": {"color": BLUE, "marker": "o", "linestyle": "-"},
    "СИСТЕМА_2": {"color": ORANGE, "marker": "s", "linestyle": "--"},
}
DEVICE_COLOR = {1: BLUE, 2: ORANGE, 3: AQUA}

plt.rcParams.update({
    "font.size": 10,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
    "savefig.dpi": 200,
})


# ------------------------------------------------------------ граф переходов

def _layout(model: Model) -> dict[int, tuple[float, float]]:
    """Координаты вершин.

    По горизонтали – состояние прибора с накопителем (число заявок, фаза),
    по вертикали – комбинации состояний остальных приборов. Ряды сдвинуты
    по x так, чтобы длинные вертикальные рёбра не проходили через вершины.
    """
    devs = model.spec.devices
    main = max(range(len(devs)), key=lambda i: devs[i].capacity * devs[i].phases)
    others = [i for i in range(len(devs)) if i != main]
    dx = 2.6
    row_h = 2.4 if devs[main].phases == 1 else 2.9
    k = devs[main].phases

    combos = sorted({tuple(st[i][0] for i in others) for st in model.states})
    pos = {}
    for s, st in enumerate(model.states):
        n, f = st[main]
        combo = tuple(st[i][0] for i in others)
        row = combos.index(combo)
        x = n * dx
        y = -row * row_h
        if k > 1 and n > 0:
            x += (f - 1) * dx / k
            y += (f - 1) * 1.0
        # Последний «малый» прибор занят → ряд сдвигается вправо.
        if others and combo[-1] > 0 and k == 1:
            x += dx * 0.38
        pos[s] = (x, y)
    return pos


def _edge(ax, p, q, r, offset, color, label, label_side):
    vx, vy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(vx, vy)
    ux, uy = vx / d, vy / d
    nx, ny = -uy, ux
    a = (p[0] + ux * r + nx * offset, p[1] + uy * r + ny * offset)
    b = (q[0] - ux * r + nx * offset, q[1] - uy * r + ny * offset)
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=7,
                                 color=color, lw=0.8, shrinkA=0, shrinkB=0))
    # Подпись – не в середине ребра: там его пересекают вертикальные рёбра
    # соседних рядов; у длинных вертикальных – между рядами вершин.
    if abs(uy) < 0.2:
        t = 0.3
    elif abs(ux) < 0.2 and d > 3:
        t = 0.75
    else:
        t = 0.5
    mx = a[0] + (b[0] - a[0]) * t + nx * label_side
    my = a[1] + (b[1] - a[1]) * t + ny * label_side
    ax.text(mx, my, label, fontsize=6.5, color=INK, ha="center", va="center",
            bbox={"boxstyle": "round,pad=0.08", "fc": "white", "ec": "none", "alpha": 0.85})


def state_graph(model: Model, path: Path) -> Path:
    pos = _layout(model)
    r = 0.5
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    w = max(xs) - min(xs) + 2
    h = max(ys) - min(ys) + 2
    fig, ax = plt.subplots(figsize=(w * 0.8, h * 0.8))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(min(xs) - 1, max(xs) + 1)
    ax.set_ylim(min(ys) - 1, max(ys) + 1)

    pairs = {(t.src, t.dst) for t in model.transitions}
    for t in model.transitions:
        two_way = (t.dst, t.src) in pairs
        off = 0.09 if two_way else 0.0
        side = 0.2 if two_way else -0.2
        _edge(ax, pos[t.src], pos[t.dst], r, off, DEVICE_COLOR[t.device], t.label, side)

    for s, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=0.9, zorder=3))
        ax.text(x, y + 0.11, model.code(s)[1:-1].replace(", ", ","), fontsize=7.5,
                ha="center", va="center", zorder=4, color=INK)
        ax.text(x, y - 0.22, f"E{s}", fontsize=6.5, ha="center", va="center",
                zorder=4, color=MUTED)

    handles = [plt.Line2D([], [], color=DEVICE_COLOR[d.index], lw=1.2,
                          label=f"переходы П{d.index}") for d in model.spec.devices]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.0),
              ncol=len(handles), fontsize=8)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


# ------------------------------------------------------------ схема системы

def scheme(model: Model, path: Path) -> Path:
    spec = model.spec
    nd = len(spec.devices)
    fig, ax = plt.subplots(figsize=(7, 0.9 + 1.0 * nd))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, nd + 0.2)
    ys = [nd - 0.5 - i for i in range(nd)]
    cy = sum(ys) / nd
    ax.annotate("", xy=(2.0, cy), xytext=(0.3, cy),
                arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 1})
    ax.text(1.1, cy + 0.15, f"λ = {float(spec.lam):g}".replace(".", ","), ha="center",
            va="bottom", fontsize=9)
    ax.add_patch(Circle((2.15, cy), 0.12, fc=INK))
    for d, y in zip(spec.devices, ys):
        lam_i = float(spec.lam_i(d))
        # Без накопителя заявка идёт сразу к прибору: стрелка до прибора.
        tip = (4.45, y) if d.buffer else (6.35, y)
        ax.annotate("", xy=tip, xytext=(2.25, cy),
                    arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 0.8,
                                "shrinkA": 0, "shrinkB": 0})
        ax.text(3.2, (y + cy) / 2 + 0.12, f"q{d.index}={float(d.share):g}".replace(".", ","),
                fontsize=8, ha="center", va="bottom", color=MUTED)
        if d.buffer:
            for c in range(d.buffer):
                ax.add_patch(Rectangle((4.45 + c * 0.35, y - 0.2), 0.35, 0.4,
                                       fc="white", ec=INK, lw=0.8))
            bx = 4.45 + d.buffer * 0.35
            ax.text(4.45 + d.buffer * 0.175, y - 0.28, f"r{d.index} = {d.buffer}",
                    fontsize=8, ha="center", va="top", color=MUTED)
            ax.annotate("", xy=(6.35, y), xytext=(bx, y),
                        arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 0.8,
                                    "shrinkA": 0, "shrinkB": 0})
        else:
            ax.text(5.6, y - 0.2, "r = 0", fontsize=8, ha="center", va="top",
                    color=MUTED)
        ax.add_patch(Circle((6.75, y), 0.38, fc="white", ec=DEVICE_COLOR[d.index], lw=1.4))
        ax.text(6.75, y, f"П{d.index}", ha="center", va="center", fontsize=9)
        law = "exp" if d.phases == 1 else f"E{d.phases}"
        ax.text(7.25, y + 0.05, f"b = {float(spec.b):g} с, {law}".replace(".", ","),
                fontsize=8, va="bottom")
        ax.text(7.25, y - 0.05, f"λ{d.index} = {lam_i:g}".replace(".", ","),
                fontsize=8, va="top", color=MUTED)
        ax.annotate("", xy=(9.8, y), xytext=(9.0, y),
                    arrowprops={"arrowstyle": "-|>", "color": INK, "lw": 0.8})
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


# ------------------------------------------------------------ зависимости от λ

def _series(ax, sweep, key, nominal):
    for name, pts in sweep.items():
        st = SYSTEM_STYLE[name]
        xs = [p["lam"] for p in pts]
        ys = [p[key] for p in pts]
        ax.plot(xs, ys, color=st["color"], linestyle=st["linestyle"], lw=2,
                marker=st["marker"], markersize=4, markevery=4,
                label=name.replace("_", " ").capitalize())
    ax.axvline(nominal, color=MUTED, lw=0.8, linestyle=":")
    comma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    ax.xaxis.set_major_formatter(comma)
    ax.yaxis.set_major_formatter(comma)
    ax.set_xlabel("Интенсивность потока λ, 1/с")


def sweep_criterion(sweep, nominal: float, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    _series(ax, sweep, "l", nominal)
    ax.set_ylabel("Суммарная длина очередей l")
    ax.legend(loc="upper left")
    ax.text(nominal, ax.get_ylim()[1], f" λ = {nominal:g}".replace(".", ","),
            fontsize=8, color=MUTED, va="top")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


PANEL = [
    ("loss", "Вероятность потери π"),
    ("lam_acc", "Производительность λ', 1/с"),
    ("rho", "Загрузка системы ρ"),
    ("u", "Время пребывания u, с"),
    ("w", "Время ожидания w, с"),
    ("m", "Число заявок в системе m"),
]


def sweep_panel(sweep, nominal: float, path: Path) -> Path:
    fig, axes = plt.subplots(3, 2, figsize=(7.2, 8.4))
    for ax, (key, title) in zip(axes.flat, PANEL):
        _series(ax, sweep, key, nominal)
        ax.set_title(title, fontsize=10, loc="left")
        ax.set_xlabel("λ, 1/с")
    axes.flat[0].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
