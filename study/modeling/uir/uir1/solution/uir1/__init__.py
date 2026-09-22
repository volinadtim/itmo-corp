"""УИР 1 «Статистический анализ результатов измерений» — расчётная часть."""

from .analysis import analyse, build_report, render
from .variants import load_variant, load_variants

__all__ = ["analyse", "build_report", "render", "load_variant", "load_variants"]
