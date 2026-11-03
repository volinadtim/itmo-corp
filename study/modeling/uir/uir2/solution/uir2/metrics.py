"""Характеристики СМО через стационарные вероятности (форма 2).

Указание к форме 2: характеристики считаются через вероятности состояний,
без формул Литтла; фундаментальные зависимости – только для проверки.
Поэтому и время ожидания здесь считается напрямую, по вероятностям того,
что поступившая заявка застаёт прибор в том или ином состоянии
(простейший поток видит систему в стационарном распределении – свойство
PASTA), а w = l/λ' остаётся проверкой.

Время ожидания заявки, заставшей у прибора n заявок (n < r+1, заявка принята):
  (n − 1)·b + остаток обслуживания текущей заявки;
  остаток при экспоненте – b (отсутствие последействия),
  при Эрланге k-го порядка на фазе f – (k − f + 1)·b/k.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from .model import Model
from .variant import Device


@dataclass(frozen=True)
class DeviceMetrics:
    device: Device
    lam: F        # λ_i – интенсивность потока к прибору
    y: F          # нагрузка
    rho: F        # загрузка
    l: F          # средняя длина очереди
    m: F          # среднее число заявок
    w: F          # среднее время ожидания (через вероятности)
    u: F          # среднее время пребывания
    loss: F       # вероятность потери
    lam_acc: F    # производительность λ'
    # Проверки фундаментальными зависимостями
    w_little: F   # l / λ'
    u_little: F   # m / λ'
    rho_flow: F   # λ'·b


@dataclass(frozen=True)
class SystemMetrics:
    devices: tuple[DeviceMetrics, ...]
    lam: F
    y: F          # суммарная нагрузка Σ y_i
    busy: F       # среднее число занятых приборов Σ ρ_i
    rho: F        # загрузка системы Σ ρ_i / N
    l: F
    m: F
    w: F
    u: F
    loss: F
    lam_acc: F


def _wait_weight(device: Device, n: int, f: int) -> F:
    """Ожидание в единицах b для заявки, заставшей у прибора n заявок (фаза f)."""
    if n == 0:
        return F(0)
    k = device.phases
    return F(n - 1) + F(k - f + 1, k)


def device_metrics(model: Model, pos: int) -> DeviceMetrics:
    spec = model.spec
    d = spec.devices[pos]
    b = spec.b
    lam = spec.lam_i(d)

    def local(st):
        return st[pos]

    rho = model.prob(model.where(lambda st: local(st)[0] > 0))
    l = sum((max(local(st)[0] - 1, 0) * model.p[i] for i, st in enumerate(model.states)), F(0))
    m = sum((local(st)[0] * model.p[i] for i, st in enumerate(model.states)), F(0))
    loss = model.prob(model.where(lambda st: local(st)[0] == d.capacity))
    lam_acc = lam * (1 - loss)
    wait_sum = sum(
        (_wait_weight(d, *local(st)) * model.p[i]
         for i, st in enumerate(model.states) if local(st)[0] < d.capacity),
        F(0),
    )
    w = b * wait_sum / (1 - loss)
    return DeviceMetrics(
        device=d, lam=lam, y=lam * b, rho=rho, l=l, m=m, w=w, u=w + b,
        loss=loss, lam_acc=lam_acc,
        w_little=l / lam_acc, u_little=m / lam_acc, rho_flow=lam_acc * b,
    )


def system_metrics(model: Model) -> SystemMetrics:
    devs = tuple(device_metrics(model, i) for i in range(len(model.spec.devices)))
    lam = model.spec.lam
    lam_acc = sum((d.lam_acc for d in devs), F(0))
    busy = sum((d.rho for d in devs), F(0))
    return SystemMetrics(
        devices=devs,
        lam=lam,
        y=sum((d.y for d in devs), F(0)),
        busy=busy,
        rho=busy / len(devs),
        l=sum((d.l for d in devs), F(0)),
        m=sum((d.m for d in devs), F(0)),
        w=sum((d.lam_acc * d.w for d in devs), F(0)) / lam_acc,
        u=sum((d.lam_acc * d.u for d in devs), F(0)) / lam_acc,
        loss=1 - lam_acc / lam,
        lam_acc=lam_acc,
    )


# ---------------------------------------------------------------- WinMark

def _psum(indices: list[int], weights: list[F] | None = None) -> str:
    """Сумма вероятностей в синтаксисе WinMark: p3+p4+2*p7."""
    if not indices:
        return "0"
    terms = []
    for k, i in enumerate(indices):
        wgt = F(1) if weights is None else weights[k]
        if wgt == 0:
            continue
        coef = "" if wgt == 1 else f"{_num(wgt)}*"
        terms.append(f"{coef}p{i}")
    return "+".join(terms) if terms else "0"


def _num(x: F) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{float(x):.4f}".rstrip("0")


def winmark_formulas(model: Model) -> list[tuple[str, str, str]]:
    """Формулы характеристик для окна «Ввод формул» WinMark.

    Возвращает (имя, формула, пояснение) в порядке ввода: каждая формула
    ссылается только на элементы матрицы, вероятности pN и ранее введённые
    характеристики. Имена не начинаются с p/P, чтобы не путаться с pN.
    """
    spec = model.spec
    out: list[tuple[str, str, str]] = []
    nd = len(spec.devices)
    for pos, d in enumerate(spec.devices):
        i = d.index
        st = list(enumerate(model.states))
        busy = [s for s, x in st if x[pos][0] > 0]
        queue = [s for s, x in st if x[pos][0] > 1]
        full = [s for s, x in st if x[pos][0] == d.capacity]
        accepted_busy = [s for s, x in st if 0 < x[pos][0] < d.capacity]
        out += [
            (f"y{i}", f"la{i}/mu", f"нагрузка П{i}"),
            (f"rho{i}", _psum(busy), f"загрузка П{i}"),
            (f"l{i}", _psum(queue, [F(model.states[s][pos][0] - 1) for s in queue]),
             f"длина очереди П{i}"),
            (f"m{i}", _psum(busy, [F(model.states[s][pos][0]) for s in busy]),
             f"число заявок у П{i}"),
            (f"loss{i}", _psum(full), f"вероятность потери П{i}"),
            (f"lp{i}", f"la{i}*(1-loss{i})", f"производительность П{i}"),
        ]
        if accepted_busy:
            weights = [_wait_weight(d, *model.states[s][pos]) for s in accepted_busy]
            w = f"({_psum(accepted_busy, weights)})/mu/(1-loss{i})"
        else:
            w = "0"
        out += [
            (f"w{i}", w, f"время ожидания П{i}"),
            (f"u{i}", f"w{i}+1/mu", f"время пребывания П{i}"),
        ]
    ids = [d.index for d in spec.devices]
    plus = lambda fmt: "+".join(fmt.format(i) for i in ids)  # noqa: E731
    out += [
        ("Ysum", plus("y{}"), "суммарная нагрузка"),
        ("Ksum", plus("rho{}"), "среднее число занятых приборов"),
        ("Rsys", f"Ksum/{nd}", "загрузка системы"),
        ("Lsum", plus("l{}"), "суммарная длина очередей"),
        ("Msum", plus("m{}"), "суммарное число заявок"),
        ("LPsum", plus("lp{}"), "производительность системы"),
        ("lossS", f"1-LPsum/({plus('la{}')})", "вероятность потери"),
        ("Wsum", f"({plus('lp{0}*w{0}')})/LPsum", "время ожидания"),
        ("Usum", f"({plus('lp{0}*u{0}')})/LPsum", "время пребывания"),
    ]
    return out


def eval_winmark(formulas, model: Model) -> dict[str, float]:
    """Вычислить формулы WinMark так, как это сделала бы программа.

    Нужен для проверки: формулы, которые студент вводит в WinMark, дают
    те же значения, что и расчёт выше.
    """
    import ast
    import operator as op
    import re

    env: dict[str, float] = {f"p{i}": float(v) for i, v in enumerate(model.p)}
    env.update({k: float(v) for k, v in model.elements().items()})
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
           ast.Pow: op.pow, ast.USub: op.neg}

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return env[node.id]
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](ev(node.operand))
        raise ValueError(f"недопустимая конструкция: {ast.dump(node)}")

    for name, formula, _ in formulas:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
            raise ValueError(f"имя {name!r} недопустимо в WinMark")
        env[name] = ev(ast.parse(formula.replace("^", "**"), mode="eval"))
    return {name: env[name] for name, _, _ in formulas}
