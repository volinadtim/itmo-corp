"""Проверки расчётной части: python3 -m unittest test_uir1 -v"""

from __future__ import annotations

import math
import random
import statistics
import unittest
from pathlib import Path

from uir1 import approx
from uir1.analysis import analyse
from uir1.estimates import (
    T_TABLE,
    autocorrelation,
    correlation,
    histogram,
    moments,
    sturges_bins,
    t_value,
)
from uir1.variants import load_variants

XLSX = Path(__file__).resolve().parents[3] / "materials" / "lms" / "!_УИР1_Варианты_с.xlsx"


class TestEstimates(unittest.TestCase):
    def test_variance_uses_bessel_correction(self):
        sample = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        m = moments(sample)
        self.assertAlmostEqual(m.mean, 5.0)
        # Делитель n−1 даёт 32/7, делитель n дал бы 4.0.
        self.assertAlmostEqual(m.variance, 32 / 7)
        self.assertAlmostEqual(m.variance, statistics.variance(sample))

    def test_variance_is_unbiased_on_average(self):
        """M[D̃] = D: усреднение по многим выборкам сходится к истинной дисперсии."""
        rng = random.Random(1)
        true_variance = 4.0
        biased, unbiased, trials, n = [], [], 4000, 5
        for _ in range(trials):
            s = [rng.gauss(10.0, math.sqrt(true_variance)) for _ in range(n)]
            mean = sum(s) / n
            squares = sum((x - mean) ** 2 for x in s)
            unbiased.append(squares / (n - 1))
            biased.append(squares / n)
        self.assertAlmostEqual(statistics.mean(unbiased), true_variance, delta=0.15)
        # Смещённая занижает примерно в (n−1)/n = 0,8 раза.
        self.assertLess(statistics.mean(biased), true_variance * 0.9)

    def test_std_of_mean_falls_as_sqrt_n(self):
        rng = random.Random(2)
        sample = [rng.expovariate(0.1) for _ in range(1000)]
        m100 = moments(sample[:100])
        m400 = moments(sample[:400])
        # σ_m ~ 1/√n: при четырёхкратном росте n падает примерно вдвое.
        ratio = m100.std_of_mean / m400.std_of_mean
        self.assertAlmostEqual(ratio, 2.0, delta=0.4)

    def test_t_table_matches_normal_quantiles(self):
        """Табличные t_p — квантили нормального распределения Φ⁻¹((1+p)/2)."""
        from statistics import NormalDist

        for p, expected in T_TABLE.items():
            exact = NormalDist().inv_cdf((1 + p) / 2)
            # 0,90 в методичке округлено до 1,643 (точное 1,645) — допуск 0,003.
            self.assertAlmostEqual(expected, exact, delta=0.003, msg=f"p={p}")

    def test_t_value_rejects_unknown_probability(self):
        with self.assertRaises(KeyError):
            t_value(0.975)

    def test_autocorrelation_of_constant_trend(self):
        """Монотонный ряд даёт высокую положительную автокорреляцию."""
        ramp = [float(i) for i in range(300)]
        self.assertGreater(autocorrelation(ramp, 1), 0.9)

    def test_autocorrelation_of_white_noise_is_near_zero(self):
        rng = random.Random(3)
        noise = [rng.random() for _ in range(5000)]
        for lag in (1, 2, 5, 10):
            self.assertLess(abs(autocorrelation(noise, lag)), 0.05)

    def test_correlation_of_identical_series_is_one(self):
        rng = random.Random(4)
        s = [rng.random() for _ in range(200)]
        self.assertAlmostEqual(correlation(s, s), 1.0)

    def test_histogram_density_integrates_to_one(self):
        rng = random.Random(5)
        s = [rng.expovariate(0.05) for _ in range(1000)]
        h = histogram(s)
        area = sum(d * h.width for d in h.density)
        self.assertAlmostEqual(area, 1.0, places=9)
        self.assertEqual(sum(h.counts), len(s))

    def test_sturges(self):
        self.assertEqual(sturges_bins(300), 9)


class TestDistributions(unittest.TestCase):
    """Генератор каждого закона должен воспроизводить заданные m и ν."""

    CASES = [
        ("uniform", 100.0, 0.4),
        ("exponential", 100.0, 1.0),
        ("erlang", 100.0, 0.5),
        ("hypoexponential", 100.0, 0.8),
        ("hypoexponential", 300.0, 0.6274),
        ("hyperexponential", 100.0, 2.0),
    ]

    def test_generators_reproduce_moments(self):
        for name, mean, cv in self.CASES:
            with self.subTest(law=name):
                law = approx.LAWS[name](mean, cv)
                rng = random.Random(42)
                sample = law.generate(200_000, rng)
                got = moments(sample)
                self.assertAlmostEqual(got.mean / mean, 1.0, delta=0.02)
                self.assertAlmostEqual(got.cv / law.theoretical_cv, 1.0, delta=0.03)

    def test_theoretical_moments_match_request(self):
        """Законы, подгоняющие оба момента точно, должны это делать."""
        for name, mean, cv in self.CASES:
            if name in ("erlang", "uniform"):
                continue  # Эрланг ограничен целым k; равномерный проверяем ниже
            with self.subTest(law=name):
                law = approx.LAWS[name](mean, cv)
                self.assertAlmostEqual(law.theoretical_mean, mean, places=6)
                self.assertAlmostEqual(law.theoretical_cv, cv, places=6)

    def test_uniform_bounds(self):
        law = approx.Uniform(100.0, 0.2)
        self.assertAlmostEqual(law.theoretical_mean, 100.0)
        self.assertAlmostEqual(law.theoretical_cv, 0.2)

    def test_erlang_k_from_cv(self):
        for k in (1, 2, 3, 4, 9, 16):
            law = approx.NormalizedErlang(50.0, 1 / math.sqrt(k))
            self.assertEqual(law.k, k)

    def test_erlang_pdf_integrates_to_one(self):
        law = approx.NormalizedErlang(50.0, 0.25)  # k = 16, большие факториалы
        step, total = 0.05, 0.0
        x = 0.0
        while x < 300:
            total += law.pdf(x) * step
            x += step
        self.assertAlmostEqual(total, 1.0, delta=0.01)

    def test_hyperexponential_rejects_q_above_limit(self):
        cv = 2.0
        q_max = 2 / (1 + cv**2)
        with self.assertRaises(ValueError):
            approx.Hyperexponential(100.0, cv, q=q_max * 1.01)

    def test_hyperexponential_default_q_keeps_t2_positive(self):
        for cv in (1.1, 1.5, 2.0, 3.0, 5.0):
            law = approx.Hyperexponential(100.0, cv)
            self.assertGreater(law.t2, 0, msg=f"ν={cv}")
            self.assertLess(law.q, law.q_max)

    def test_hypoexponential_rejects_cv_outside_zero_one(self):
        for cv in (0.0, 1.0, 1.5):
            with self.subTest(cv=cv), self.assertRaises(ValueError):
                approx.Hypoexponential(100.0, cv)

    def test_hypoexponential_picks_minimal_phase_count(self):
        """k = ⌈1/ν²⌉ — минимальное, при котором закон существует."""
        for cv, expected_k in [(0.9, 2), (0.75, 2), (0.6274, 3), (0.45, 5), (0.3, 12)]:
            with self.subTest(cv=cv):
                law = approx.Hypoexponential(100.0, cv)
                self.assertEqual(law.k, expected_k)
                self.assertGreaterEqual(cv, 1 / math.sqrt(law.k) - 1e-12)

    def test_hypoexponential_fits_both_moments_exactly(self):
        for cv in (0.3, 0.45, 0.6, 0.6274, 0.75, 0.9, 0.95):
            with self.subTest(cv=cv):
                law = approx.Hypoexponential(250.0, cv)
                self.assertAlmostEqual(law.theoretical_mean, 250.0, places=8)
                self.assertAlmostEqual(law.theoretical_cv, cv, places=8)

    def test_hypoexponential_pdf_integrates_to_one(self):
        for cv in (0.35, 0.6274, 0.85):
            with self.subTest(cv=cv):
                law = approx.Hypoexponential(100.0, cv)
                step, total, x = 0.2, 0.0, 0.0
                while x < 1500:
                    total += law.pdf(x) * step
                    x += step
                self.assertAlmostEqual(total, 1.0, delta=0.005)

    def test_choose_picks_expected_law(self):
        self.assertIsInstance(approx.choose(100.0, 0.25), approx.NormalizedErlang)
        self.assertIsInstance(approx.choose(100.0, 1.0), approx.Exponential)
        self.assertIsInstance(approx.choose(100.0, 2.0), approx.Hyperexponential)
        # ν=0,9: округление k исказило бы второй момент → точная гипоэкспонента
        self.assertIsInstance(approx.choose(100.0, 0.9), approx.Hypoexponential)


@unittest.skipUnless(XLSX.exists(), "файл вариантов недоступен")
class TestAllVariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.variants = load_variants(XLSX)

    def test_all_360_variants_present(self):
        self.assertEqual(len(self.variants), 360)
        self.assertEqual(min(self.variants), 1)
        self.assertEqual(max(self.variants), 360)
        for number, data in self.variants.items():
            self.assertEqual(len(data), 300, msg=f"вариант {number}")

    def test_every_variant_analyses_without_error(self):
        for number, data in self.variants.items():
            with self.subTest(variant=number):
                result = analyse(data, number)
                self.assertEqual(len(result.generated), 300)
                # Мат. ожидание закон обязан воспроизводить точно всегда.
                self.assertAlmostEqual(
                    result.law.theoretical_mean, result.full.mean, places=6
                )

    def test_reproducible_with_same_seed(self):
        a = analyse(self.variants[49], 49, seed=123)
        b = analyse(self.variants[49], 49, seed=123)
        self.assertEqual(a.generated, b.generated)

    def test_cross_correlation_is_near_zero(self):
        """Заданная и сгенерированная ЧП независимы — r должен быть около нуля."""
        for number in (26, 49, 141, 200, 360):
            with self.subTest(variant=number):
                result = analyse(self.variants[number], number)
                self.assertLess(abs(result.cross_correlation), 0.2)



class TestReportRendering(unittest.TestCase):
    """Отчёт должен собираться для каждого закона.

    Раньше эти тесты отсутствовали, и смена сигнатуры гипоэкспоненты
    уронила генерацию отчёта, хотя все расчётные тесты проходили.
    """

    LAWS = ["uniform", "exponential", "erlang", "hypoexponential", "hyperexponential"]

    def _sample(self, law_name: str) -> list[float]:
        cv = {"uniform": 0.4, "exponential": 1.0, "erlang": 0.5,
              "hypoexponential": 0.6274, "hyperexponential": 2.0}[law_name]
        law = approx.LAWS[law_name](200.0, cv)
        return law.generate(300, random.Random(9))

    def test_report_builds_for_every_law(self):
        import tempfile

        from uir1.analysis import render

        for name in self.LAWS:
            with self.subTest(law=name), tempfile.TemporaryDirectory() as tmp:
                result = analyse(self._sample(name), 1, law_name=name)
                path = render(result, Path(tmp))
                text = path.read_text(encoding="utf-8")
                self.assertIn("## 6. Генератор случайных величин", text)
                self.assertIn(result.law.name, text)
                # В формулах генератора не должно остаться незаполненных полей.
                self.assertNotIn("{", text)
                for plot in ("plot1_series", "plot2_histogram", "plot3_fit"):
                    self.assertTrue((Path(tmp) / "plots" / f"{plot}.png").exists())

if __name__ == "__main__":
    unittest.main()
