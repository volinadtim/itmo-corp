"""Проверки расчётной части: python3 -m unittest test_uir2 -v"""

from __future__ import annotations

import unittest
from fractions import Fraction as F

from uir2 import analytic, ctmc
from uir2.analysis import analyse
from uir2.metrics import eval_winmark, system_metrics, winmark_formulas
from uir2.model import build
from uir2.variant import (
    LAMBDA,
    B,
    Device,
    SystemSpec,
    criterion_letter,
    routing,
    system1,
    system2,
)


class TestVariant(unittest.TestCase):
    def test_parameters_of_variant_60_31(self):
        self.assertEqual(LAMBDA, F(3, 5))
        self.assertEqual(B, 10)
        self.assertEqual(routing(3), (F(3, 4), F(3, 20), F(1, 10)))
        # Двухканальная СМО: q2 = P2 + P3 из таблицы 2.
        self.assertEqual(routing(2), (F(3, 4), F(1, 4)))
        self.assertEqual(routing(1), (F(1),))

    def test_criterion_by_parity(self):
        # 60 + 60 чётно → критерий варианта N2.
        self.assertEqual(criterion_letter(60, 60), "д")

    def test_structure(self):
        s1, s2 = system1(), system2()
        self.assertEqual([d.buffer for d in s1.devices], [0, 3, 0])
        self.assertEqual([d.phases for d in s1.devices], [1, 1, 1])
        self.assertEqual([d.buffer for d in s2.devices], [0, 3])
        self.assertEqual([d.phases for d in s2.devices], [1, 2])


class TestSolver(unittest.TestCase):
    def test_birth_death_two_states(self):
        g = ctmc.generator(2, {(0, 1): F(1), (1, 0): F(3)})
        self.assertEqual(ctmc.stationary(g), [F(3, 4), F(1, 4)])

    def test_rows_sum_to_zero(self):
        for spec in (system1(), system2()):
            m = build(spec)
            for row in m.g:
                self.assertEqual(sum(row), 0)

    def test_state_counts_fit_form1(self):
        # Форма 1 рассчитана на 20 состояний; укрупнять модель не нужно.
        self.assertEqual(build(system1()).n, 20)
        self.assertEqual(build(system2()).n, 18)

    def test_exact_solution(self):
        for spec in (system1(), system2()):
            m = build(spec)
            self.assertEqual(sum(m.p), 1)
            self.assertEqual(ctmc.residual(m.g, m.p), 0)
            self.assertTrue(all(x > 0 for x in m.p))


class TestAnalytic(unittest.TestCase):
    def test_system1_is_product_of_mm1r(self):
        m = build(system1())
        p1 = analytic.mm10(F(9, 2))
        p2 = analytic.mm1r(F(9, 10), 3)
        p3 = analytic.mm10(F(3, 5))
        for s, st in enumerate(m.states):
            self.assertEqual(m.p[s], p1[st[0][0]] * p2[st[1][0]] * p3[st[2][0]])

    def test_mm1r_known_values(self):
        # Алиев: M/M/1/r при y = 1 – равномерное распределение.
        self.assertEqual(analytic.mm1r(F(1), 3), [F(1, 5)] * 5)
        self.assertEqual(analytic.mm10(F(9, 2))[1], F(9, 11))

    def test_erlang_device_matches_embedded_chain(self):
        m = build(system2())
        exact = analytic.mek1(F(3, 20), B, 2, 4)
        for n in range(5):
            self.assertEqual(m.prob(m.where(lambda st, n=n: st[1][0] == n)), exact[n])

    def test_embedded_chain_reduces_to_mm1r(self):
        # При k = 1 вложенная цепь M/G/1/K обязана дать формулу M/M/1/r.
        for y in (F(1, 2), F(9, 10), F(3, 2)):
            self.assertEqual(analytic.mek1(y / B, B, 1, 4), analytic.mm1r(y, 3))

    def test_loss_system_insensitive_to_service_law(self):
        exp = system_metrics(build(system2(erlang_device=0)))
        erl = system_metrics(build(system2(erlang_device=1)))
        self.assertEqual(erl.devices[0].rho, exp.devices[0].rho)
        self.assertEqual(erl.devices[0].loss, exp.devices[0].loss)


class TestMetrics(unittest.TestCase):
    def test_little_and_flow_balance_exact(self):
        for spec in (system1(), system2()):
            sm = system_metrics(build(spec))
            for d in sm.devices:
                self.assertEqual(d.w, d.w_little)
                self.assertEqual(d.u, d.u_little)
                self.assertEqual(d.rho, d.rho_flow)
                self.assertEqual(d.m, d.l + d.rho)
            self.assertEqual(sm.lam * (1 - sm.loss), sm.lam_acc)

    def test_reference_values(self):
        s1 = system_metrics(build(system1()))
        s2 = system_metrics(build(system2()))
        self.assertAlmostEqual(float(s1.l), 1.0345, places=4)
        self.assertAlmostEqual(float(s2.l), 1.8937, places=4)
        self.assertAlmostEqual(float(s1.loss), 0.6752, places=4)
        self.assertAlmostEqual(float(s2.loss), 0.7050, places=4)
        self.assertEqual(s1.devices[0].rho, F(9, 11))

    def test_erlang_vs_exponential(self):
        """Меньшая вариация: без перегрузки очередь короче, при перегрузке
        (y₂ = 1,5 в варианте) – меньше потерь, но очередь длиннее."""
        light = F(3, 10)  # y₂ = 0,75
        erl = system_metrics(build(system2(light))).devices[1]
        exp = system_metrics(build(system2(light, erlang_device=0))).devices[1]
        self.assertLess(erl.l, exp.l)
        erl = system_metrics(build(system2())).devices[1]
        exp = system_metrics(build(system2(erlang_device=0))).devices[1]
        self.assertLess(erl.loss, exp.loss)
        self.assertGreater(erl.l, exp.l)

    def test_winmark_formulas_reproduce_metrics(self):
        for spec in (system1(), system2(), system2(erlang_device=1)):
            m = build(spec)
            sm = system_metrics(m)
            wm = eval_winmark(winmark_formulas(m), m)
            for pos, d in enumerate(sm.devices):
                i = d.device.index
                for name, attr in (("rho", "rho"), ("l", "l"), ("m", "m"),
                                   ("loss", "loss"), ("lp", "lam_acc"),
                                   ("w", "w"), ("u", "u"), ("y", "y")):
                    self.assertAlmostEqual(wm[f"{name}{i}"], float(getattr(d, attr)), 12)
            self.assertAlmostEqual(wm["Lsum"], float(sm.l), 12)
            self.assertAlmostEqual(wm["Wsum"], float(sm.w), 12)

    def test_winmark_elements_have_four_decimals(self):
        # WinMark хранит значения элементов с точностью до 4 знаков.
        for spec in (system1(), system2()):
            for v in build(spec).elements().values():
                self.assertEqual(v * 10000, int(v * 10000))

    def test_single_mm1_no_buffer_textbook(self):
        spec = SystemSpec("M/M/1/0", (Device(1, 0, 1, F(1)),), F(1, 10), F(10))
        sm = system_metrics(build(spec))
        self.assertEqual(sm.loss, F(1, 2))
        self.assertEqual(sm.u, 10)


class TestAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = analyse()

    def test_all_checks_pass(self):
        for name, checks in self.r.checks.items():
            for c in checks:
                self.assertTrue(c.exact, f"{name}: {c.name}")

    def test_choice(self):
        self.assertEqual(self.r.criterion, "д")
        self.assertEqual(self.r.best, "СИСТЕМА_1")

    def test_choice_stable_over_sweep(self):
        for a, b in zip(self.r.sweep["СИСТЕМА_1"], self.r.sweep["СИСТЕМА_2"]):
            self.assertLess(a["l"], b["l"])

    def test_winmark_points_include_nominal(self):
        lams = [p["lam"] for p in self.r.winmark_points["СИСТЕМА_1"]]
        self.assertIn(float(LAMBDA), lams)
        self.assertEqual(len(lams), 5)


if __name__ == "__main__":
    unittest.main()
