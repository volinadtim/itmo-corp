# Отчёт по УИР 1 — typst

Оформлен по конвенции проекта, как [study/os/reports/intro-exp](../../../os/reports/intro-exp).

| Файл | Что это |
|---|---|
| `report.typ` | сам отчёт |
| `title.typ` | титульный лист (копия из os/reports с другими значениями по умолчанию) |
| `data.json` | числа и выводы — **генерируются**, вручную не править |
| `plots/` | графики — генерируются |
| `report.pdf` | результат сборки |

## Пересборка

```bash
cd ../../uir/uir1/solution && python3 -m uir1 -v 60 --typst ../../../reports/uir1
cd ../../../reports/uir1 && typst compile report.typ
```

Первая команда пересчитывает вариант и кладёт сюда `data.json` с графиками,
вторая собирает PDF. `report.typ` читает числа из `data.json` через `json()`,
поэтому текст отчёта и расчёт не могут разойтись.

Сменить вариант — поменять `-v 60`. Подпись на титульном листе берётся
из констант в `solution/uir1/__main__.py`.

## Известное

`typst compile` предупреждает `unknown font family: liberation serif` — шрифт
в системе не установлен, подставляется New Computer Modern. То же самое
происходит и в отчёте по ОС. Чтобы предупреждение ушло:

```bash
brew install --cask font-liberation
```
