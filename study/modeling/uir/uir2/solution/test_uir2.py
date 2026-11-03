"""Проверка модели по аналитическим решениям и фундаментальным зависимостям."""

import pytest

from uir2.model import Device, solve
from uir2.systems import devices
from uir2.variants import TABLE1, TABLE2, load


def test_tables_complete():
    assert sorted(TABLE1) == list(range(1, 81))
    assert TABLE1[60] == (3, "0/3/0", 2, "E2", "0/3", "д")
    assert TABLE2[31] == (0.6, 10, (0.75, 0.15, 0.1))


def test_mm1r_matches_closed_form():
    # M/M/1/r: p_k = ρ^k (1 − ρ) / (1 − ρ^(r+2))
    rho, r = 0.9, 3
    _, p, _ = solve((Device("П", 1.0, r),), lam=0.09, b=10)
    exact = [rho**k * (1 - rho) / (1 - rho ** (r + 2)) for k in range(r + 2)]
    assert p == pytest.approx(exact, abs=1e-12)


def test_erlang_loss_insensitive_to_law():
    # M/G/1/0: вероятность потери y/(1+y) не зависит от закона обслуживания.
    _, _, st = solve((Device("П", 1.0, 0, phases=2),), lam=0.45, b=10)
    assert st.devices[0].loss == pytest.approx(4.5 / 5.5)


@pytest.mark.parametrize("which", ["system1", "system2"])
def test_variant_60_little(which):
    v = load(60, 60, 31)
    devs = devices(getattr(v, which), v)
    chain, p, st = solve(devs, v.lam, v.b)
    assert chain.n <= 20
    assert sum(p) == pytest.approx(1.0)
    assert min(p) > 0
    for s in st.devices:
        assert s.util == pytest.approx(s.throughput * v.b)
        assert s.count == pytest.approx(s.queue + s.util)
    assert st.total.loss == pytest.approx(
        sum(d.p * s.loss for d, s in zip(devs, st.devices)))


def test_criterion_rule():
    # Чётная сумма N1+N2 — критерий по N2, нечётная — по N1.
    assert load(60, 60, 31).criterion == "д"
    assert load(1, 2, 31).criterion == TABLE1[1][5]
    assert load(2, 4, 31).criterion == TABLE1[4][5]


def test_erlang_goes_to_buffered_device():
    v = load(60, 60, 31)
    devs = devices(v.system2, v)
    assert [d.phases for d in devs] == [1, 2]
    assert [d.p for d in devs] == pytest.approx([0.75, 0.25])
