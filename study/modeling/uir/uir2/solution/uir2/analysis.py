"""Полный прогон: обе системы, проверки, варьирование λ, выбор по критерию."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from . import analytic, ctmc
from .metrics import SystemMetrics, eval_winmark, system_metrics, winmark_formulas
from .model import Model, build
from .variant import (
    CRITERIA,
    LAMBDA,
    N1,
    N2,
    NG,
    criterion_letter,
    system1,
    system2,
)

# Варьирование λ для графиков: 0,05…1,2 с шагом 0,05.
SWEEP = [F(k, 20) for k in range(1, 25)]
# Пять точек варьирования WinMark: λ = 0,2; 0,4; …; 1,0 (номинал 0,6 – третья).
WINMARK_POINTS = [F(k, 5) for k in range(1, 6)]

# Критерий → (атрибут SystemMetrics, лучше – меньше?)
CRITERION_KEY = {
    "а": ("lam_acc", False),
    "б": ("loss", True),
    "в": ("rho", False),
    "г": ("u", True),
    "д": ("l", True),
}


@dataclass
class Check:
    name: str
    value: float  # максимальное абсолютное расхождение
    exact: bool   # совпадение в точной арифметике


@dataclass
class Result:
    models: dict[str, Model]
    metrics: dict[str, SystemMetrics]
    checks: dict[str, list[Check]]
    winmark: dict[str, list[tuple[str, str, str]]]
    sweep: dict[str, list[dict]]
    winmark_points: dict[str, list[dict]]
    alternative: SystemMetrics      # СИСТЕМА_2 с Эрлангом на П1
    alternative_states: int
    exponential: SystemMetrics      # СИСТЕМА_2 без Эрланга, для сравнения
    criterion: str
    best: str


def _row(sm: SystemMetrics, lam: F) -> dict:
    return {
        "lam": float(lam),
        "l": float(sm.l), "loss": float(sm.loss), "lam_acc": float(sm.lam_acc),
        "rho": float(sm.rho), "busy": float(sm.busy), "u": float(sm.u),
        "w": float(sm.w), "m": float(sm.m),
    }


def checks_for(model: Model, sm: SystemMetrics) -> list[Check]:
    out = [Check("Σ p = 1", float(abs(sum(model.p) - 1)), sum(model.p) == 1),
           Check("P·G = 0 (невязка СЛАУ)", float(ctmc.residual(model.g, model.p)),
                 ctmc.residual(model.g, model.p) == 0)]

    # Аналитика: произведение распределений приборов.
    spec = model.spec
    dists = [analytic.device_distribution(spec.lam_i(d), spec.b, d.buffer, d.phases)
             for d in spec.devices]
    worst = F(0)
    for pos, d in enumerate(spec.devices):
        for n, pa in enumerate(dists[pos]):
            pn = model.prob(model.where(lambda st, pos=pos, n=n: st[pos][0] == n))
            worst = max(worst, abs(pn - pa))
    out.append(Check("распределения приборов = формулы Алиева / M/G/1/K", float(worst),
                     worst == 0))
    if all(d.phases == 1 for d in spec.devices):
        prod = F(0)
        for s, st in enumerate(model.states):
            v = F(1)
            for pos in range(len(spec.devices)):
                v *= dists[pos][st[pos][0]]
            prod = max(prod, abs(model.p[s] - v))
        out.append(Check("p(n1,n2,n3) = p1(n1)·p2(n2)·p3(n3)", float(prod), prod == 0))

    little_w = max(abs(d.w - d.w_little) for d in sm.devices)
    little_u = max(abs(d.u - d.u_little) for d in sm.devices)
    flow = max(abs(d.rho - d.rho_flow) for d in sm.devices)
    ml = max(abs(d.m - d.l - d.rho) for d in sm.devices)
    out += [
        Check("w = l/λ' (формула Литтла)", float(little_w), little_w == 0),
        Check("u = m/λ' (формула Литтла)", float(little_u), little_u == 0),
        Check("ρ = λ'·b (баланс потока)", float(flow), flow == 0),
        Check("m = l + ρ", float(ml), ml == 0),
    ]
    wm = eval_winmark(winmark_formulas(model), model)
    ref = {"Lsum": sm.l, "lossS": sm.loss, "LPsum": sm.lam_acc, "Rsys": sm.rho,
           "Wsum": sm.w, "Usum": sm.u, "Msum": sm.m}
    diff = max(abs(wm[k] - float(v)) for k, v in ref.items())
    out.append(Check("формулы для WinMark дают те же значения", diff, diff < 1e-12))
    return out


def analyse() -> Result:
    specs = {"СИСТЕМА_1": system1, "СИСТЕМА_2": system2}
    models = {name: build(make()) for name, make in specs.items()}
    metrics = {name: system_metrics(m) for name, m in models.items()}
    checks = {name: checks_for(models[name], metrics[name]) for name in models}
    winmark = {name: winmark_formulas(m) for name, m in models.items()}

    sweep = {name: [_row(system_metrics(build(make(lam))), lam) for lam in SWEEP]
             for name, make in specs.items()}
    points = {name: [_row(system_metrics(build(make(lam))), lam) for lam in WINMARK_POINTS]
              for name, make in specs.items()}

    alt_model = build(system2(erlang_device=1))
    alternative = system_metrics(alt_model)

    letter = criterion_letter()
    key, smaller = CRITERION_KEY[letter]
    values = {name: getattr(sm, key) for name, sm in metrics.items()}
    best = (min if smaller else max)(values, key=values.get)
    exponential = system_metrics(build(system2(erlang_device=0)))
    return Result(models, metrics, checks, winmark, sweep, points, alternative,
                  alt_model.n, exponential, letter, best)


# ---------------------------------------------------------------- выводы

def _f(x, d=4) -> str:
    return f"{float(x):.{d}f}".replace(".", ",")


def _pct(x) -> str:
    return f"{float(x) * 100:.1f}".replace(".", ",") + " %"


GEN = {"СИСТЕМА_1": "СИСТЕМЫ_1", "СИСТЕМА_2": "СИСТЕМЫ_2"}


def conclusions(r: Result) -> dict[str, str]:
    s1, s2 = r.metrics["СИСТЕМА_1"], r.metrics["СИСТЕМА_2"]
    d11, d12, d13 = s1.devices
    d21, d22 = s2.devices
    ex2 = r.exponential.devices[1]
    key, smaller = CRITERION_KEY[r.criterion]
    other = "СИСТЕМА_2" if r.best == "СИСТЕМА_1" else "СИСТЕМА_1"
    v_best = getattr(r.metrics[r.best], key)
    v_other = getattr(r.metrics[other], key)

    sw1, sw2 = r.sweep["СИСТЕМА_1"], r.sweep["СИСТЕМА_2"]
    always = all((a[key] < b[key]) if smaller else (a[key] > b[key])
                 for a, b in zip(sw1, sw2))

    out = {}
    out["device1"] = (
        f"Почти все потери обеих систем даёт П1. К нему идёт {_pct(d11.device.share)} "
        f"заявок, накопителя нет, нагрузка y₁ = {_f(d11.y, 2)}. Прибор занят с вероятностью "
        f"{_f(d11.rho)}, и с той же вероятностью заявка к нему теряется. В обеих системах "
        f"П1 одинаков, поэтому на выбор он не влияет."
    )
    out["compare"] = (
        f"Системы отличаются тем, куда идёт оставшаяся четверть потока. В СИСТЕМЕ_1 она "
        f"делится: {_pct(d12.device.share)} на П2 с накопителем (y₂ = {_f(d12.y, 2)}) и "
        f"{_pct(d13.device.share)} на П3 без накопителя. В СИСТЕМЕ_2 все "
        f"{_pct(d22.device.share)} идут на П2, и он перегружен: y₂ = {_f(d22.y, 2)}. "
        f"Отсюда у П2 больше потерь ({_f(d22.loss)} против {_f(d12.loss)}), длиннее очередь "
        f"({_f(d22.l)} против {_f(d12.l)}) и дольше ожидание ({_f(d22.w, 2)} с против "
        f"{_f(d12.w, 2)} с)."
    )
    out["erlang"] = (
        f"Эрланговское обслуживание очередь в П2 не сократило, а немного удлинило: "
        f"{_f(d22.l)} против {_f(ex2.l)} при экспоненциальном. Меньшая вариация "
        f"(ν = 1/√2) снижает потери П2 с {_f(ex2.loss)} до {_f(d22.loss)}, принятых заявок "
        f"становится больше, и при перегрузке они тоже ждут. Короче очередь от Эрланга "
        f"становится только без перегрузки, при y₂ < 1."
    )
    out["totals"] = (
        f"В исходной точке СИСТЕМА_1 лучше по всем показателям, кроме загрузки: очередь "
        f"{_f(s1.l)} против {_f(s2.l)}, потери {_f(s1.loss)} против {_f(s2.loss)}, "
        f"производительность {_f(s1.lam_acc)} против {_f(s2.lam_acc)} 1/с, время пребывания "
        f"{_f(s1.u, 2)} с против {_f(s2.u, 2)} с. Загрузка у СИСТЕМЫ_2 выше ({_f(s2.rho)} "
        f"против {_f(s1.rho)}) только потому, что приборов меньше при той же нагрузке."
    )
    out["sweep"] = (
        ("По критерию СИСТЕМА_1 лучше на всём диапазоне "
         if always else "По критерию СИСТЕМА_1 лучше не на всём диапазоне ")
        + f"λ от {_f(SWEEP[0], 2)} до {_f(SWEEP[-1], 2)} 1/с. Очередь СИСТЕМЫ_2 растёт быстрее: "
        "весь остаток потока приходится на один прибор с накопителем. При большом λ обе "
        "кривые выходят на насыщение, потому что очередь не может быть больше 3 заявок."
    )
    loss_s2_better = [p1["lam"] for p1, p2 in zip(sw1, sw2) if p2["loss"] < p1["loss"]]
    if loss_s2_better:
        out["sweep"] += (
            f" С потерями иначе: при λ ≤ {_f(max(loss_s2_better), 2)} 1/с СИСТЕМА_2 теряет "
            "чуть меньше. При слабом потоке её накопитель на П2 ещё принимает заявки, "
            "которые в СИСТЕМЕ_1 идут на П3 без накопителя и теряются, если он занят."
        )
    out["choice"] = (
        f"Лучший вариант – {r.best}. Критерий ({r.criterion}), {CRITERIA[r.criterion]}: "
        f"{_f(v_best)} у {GEN[r.best]} против {_f(v_other)} у {GEN[other]}, в "
        f"{_f(v_other / v_best, 2)} раза {'меньше' if smaller else 'больше'}."
    )
    alt = r.alternative
    out["insensitivity"] = (
        f"Эрланговское обслуживание поставлено в П2, потому что в П1 оно ничего бы "
        f"не изменило. Задание разрешает любой прибор, но в системе с отказами вероятности "
        f"состояний зависят только от среднего времени обслуживания. Проверено расчётом: "
        f"с Эрлангом в П1 граф имеет {r.alternative_states} состояний, а загрузка П1 "
        f"та же, {_f(alt.devices[0].rho)}."
    )
    return out
