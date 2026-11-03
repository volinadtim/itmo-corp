# Отчёт по УИР 2: typst

Устроен так же, как [../uir1](../uir1/README.md): `report.typ` читает числа и выводы
из `data.json`, а графы и графики лежат в `plots/`. Всё это генерируется расчётом,
вручную не править.

## Пересборка

```bash
cd ../../uir/uir2/solution && uv run --no-project --with matplotlib python -m uir2 -v 60/60/31 --typst ../../../reports/uir2
cd ../../../reports/uir2 && typst compile report.typ
```

Графы переходов и матрицы интенсивностей свёрстаны на альбомных страницах.
