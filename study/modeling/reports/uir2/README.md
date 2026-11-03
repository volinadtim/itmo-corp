# Отчёт по УИР 2 в typst

Собирается так же, как [отчёт по УИР 1](../uir1/). Числа и тексты выводов генерирует расчёт,
руками в `report.typ` правится только связный текст.

| Файл | Что это |
|---|---|
| `report.typ` | сам отчёт |
| `title.typ` | титульный лист, копия из uir1 с «работе № 2» |
| `data.json` | числа и выводы, генерируются, вручную не править |
| `plots/` | схемы, графы переходов и графики, тоже генерируются |
| `winmark/` | скриншоты WinMark и файлы моделей `uir2_s1.mrk`, `uir2_s2.mrk` |
| `report.pdf` | собранный отчёт |
| `report-short.typ`, `report-short.pdf` | короткий отчёт: только пункты 6.1–6.4 задания, расчёт в MARK |

## Пересборка

```bash
cd ../../uir/uir2/solution && python3 -m uir2 --typst ../../../reports/uir2
cd ../../../reports/uir2 && typst compile report.typ
```

Если CLI `typst` не стоит, подойдёт pip-пакет `typst`:
`python3 -c "import typst; typst.compile('report.typ', output='report.pdf')"`.

## Скриншоты WinMark

Сняты 03.11.2026 в WinMark на Windows, в `winmark/`: матрица, вероятности и характеристики
каждой системы (`s1_*`, `s2_*`), результаты варьирования λ (`*_vary.png`) и график
Lsum по шагам варьирования (`*_graph.png`). Все числа совпали с расчётом. Что вводилось,
описано в [walkthrough.md, шаг 7](../../uir/uir2/walkthrough.md#шаг-7-winmark).
`#let winmark-ready = false` в `report.typ` вернёт пунктирные рамки вместо картинок.

Со всех скриншотов обрезана чёрная рамка окна Windows (3–10 px слева, справа и снизу).

Если в системе нет Liberation Serif, typst подставит запасной шрифт, как и в УИР 1.
