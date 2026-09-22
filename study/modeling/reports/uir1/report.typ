#set text(font: "Liberation Serif", size: 12pt, lang: "ru")
#set page(margin: 25mm)
#set par(justify: true, first-line-indent: 1.25cm)
#show heading: it => { v(0.6em); it; v(0.4em) }
#show table.cell.where(y: 0): strong
#set table(stroke: 0.5pt + rgb("555"), inset: 4pt)
// Широкие формы 1 и 2 не помещаются в 12pt — таблицы набираются мельче.
#show table: set text(size: 10pt)
#show figure.caption: set text(size: 10pt)
#show figure: set block(breakable: false)
// Подпись всегда снизу — и у рисунков, и у таблиц.
#show figure.where(kind: table): set figure.caption(position: bottom)
// Единое слово для всех изображений: «Рисунок», а не «Рис.».
#show figure.where(kind: image): set figure(supplement: [Рисунок])

// Числа и выводы берутся из расчёта, а не набираются руками:
//   cd ../../uir/uir1/solution && python3 -m uir1 -v 60 --typst ../../../reports/uir1
#let d = json("data.json")

#import "title.typ": titlepage

#titlepage(
  title: [Статистический анализ числовой последовательности\ (вариант #d.variant)],
  student: d.author.name,
  group: d.author.group,
  teacher: d.author.teacher,
  year: d.author.year,
)

#set page(numbering: "1")
#counter(page).update(1)

#outline(title: [Содержание], depth: 2)
#pagebreak()

= Цель работы

Изучение методов обработки и статистического анализа результатов измерений
на примере заданной числовой последовательности: оценка числовых моментов,
выявление свойств последовательности на основе корреляционного анализа,
аппроксимация закона распределения по двум числовым моментам случайной
величины и сравнение сгенерированной по этому закону последовательности
с заданной.

= Исходные данные

Задана числовая последовательность (ЧП) варианта #d.variant объёмом #d.n
значений. Обработка выполнена для выборок из первых
#d.sizes.map(str).join(", ") значений.

Расчёты выполнены программно на языке Python; генератор псевдослучайных
величин инициализирован фиксированным значением (seed #d.seed), поэтому
результаты воспроизводимы.

= Числовые моменты заданной ЧП

Оценка математического ожидания — среднее арифметическое; оценка дисперсии
рассчитана по несмещённой формуле с делителем $n - 1$:

$ tilde(m) = 1/n sum_(i=1)^n X_i, quad
  tilde(D) = (sum_(i=1)^n (X_i - tilde(m))^2) / (n - 1), quad
  tilde(sigma) = sqrt(tilde(D)), quad
  nu = tilde(sigma) / tilde(m) $

Доверительный интервал для математического ожидания определяется через
среднеквадратическое отклонение самой оценки:

$ tilde(sigma)_m = sqrt(tilde(D) \/ n), quad Delta_p = t_p tilde(sigma)_m, quad
  m_"н" = tilde(m) - Delta_p, quad m_"в" = tilde(m) + Delta_p $

где $t_p$ — коэффициент нормального распределения, принимающий значения
1,643 при доверительной вероятности 0,9; 1,960 при 0,95 и 2,576 при 0,99.

#figure(
  caption: [Характеристики заданной ЧП, форма 1 (вариант #d.variant)],
  table(
    columns: (3.1cm, 1.3cm) + d.sizes.map(_ => 1fr),
    align: (left, center) + d.sizes.map(_ => right),
    table.header([Характеристика], [], ..d.sizes.map(n => [#n])),
    ..d.form1.map(r => (
      table.cell(rowspan: 2, align: horizon)[#r.label],
      [Знач.], ..r.values.map(v => [#v]),
      [\%], ..r.percents.map(v => [#v]),
    )).flatten()
  ),
)

В графы «Дов. инт.» занесена длина полуинтервала. Строка «\%» — относительное
отклонение рассчитанных значений от значений, полученных для наиболее
представительной выборки из #d.n величин.

*Выводы.* #d.conclusions.moments

= Характер числовой последовательности

#figure(
  image("plots/plot1_series.png", width: 100%),
  caption: [Значения заданной числовой последовательности],
)

*Вывод.* #d.conclusions.series

= Автокорреляционный анализ

Коэффициент автокорреляции со сдвигом $k$ при $n >> k$:

$ r_k approx (sum_i (x_i - tilde(m)) (x_(i+k) - tilde(m)))
              / (sum_i (x_i - tilde(m))^2) $

Границей значимости принято значение $plus.minus t_p \/ sqrt(n)$, равное
#d.autocorr.threshold при доверительной вероятности 0,95: для случайной
последовательности коэффициенты автокорреляции колеблются около нуля
в этих пределах.

#figure(
  caption: [Коэффициенты автокорреляции, форма 3],
  table(
    columns: (3.6cm,) + d.lags.map(_ => 1fr),
    align: (left,) + d.lags.map(_ => right),
    inset: 3.5pt,
    table.header([Сдвиг ЧП], ..d.lags.map(k => [#k])),
    [К-т АК для задан. ЧП], ..d.autocorr.given.map(v => [#v]),
    [К-т АК для сгенерир. ЧП], ..d.autocorr.generated.map(v => [#v]),
    [\%], ..d.autocorr.percents.map(v => [#v]),
  ),
)

#figure(
  image("plots/plot_autocorr.png", width: 80%),
  caption: [Коэффициенты автокорреляции и граница значимости],
)

*Вывод.* #d.conclusions.randomness

= Гистограмма распределения частот

Число интервалов принято равным #d.histogram.bins.

#figure(
  image("plots/plot2_histogram.png", width: 80%),
  caption: [Гистограмма распределения частот заданной ЧП],
)

#figure(
  caption: [Распределение частот по интервалам],
  table(
    columns: 3,
    align: (center, right, right),
    table.header([Интервал], [Частота], [Отн. частота]),
    ..d.histogram.rows.flatten().map(v => [#v])
  ),
)

= Аппроксимирующий закон распределения

Коэффициент вариации заданной ЧП составляет $nu = #d.law.cv$;
#d.law.rationale. Выбран *#d.law.name* закон.

#figure(
  caption: [Параметры аппроксимирующего закона],
  table(
    columns: 2,
    align: (left, right),
    table.header([Параметр], [Значение]),
    ..d.law.params.flatten().map(v => [#v])
  ),
)

#figure(
  caption: [Проверка аппроксимации по двум моментам],
  table(
    columns: 4,
    align: (left, right, right, right),
    table.header([Момент], [Заданная ЧП], [Закон], [Расхождение]),
    ..d.law.fit.flatten().map(v => [#v])
  ),
)

#if d.law.notes.len() > 0 [
  *Замечание.*
  #list(..d.law.notes.map(n => [#n]))
]

= Генератор случайных величин

Генерация выполнена методом обратной функции: если $U$ равномерно
распределена на интервале $(0; 1)$, то величина $X = F^(-1)(U)$ распределена
по закону $F$.

#d.generator.description

$ #eval(d.generator.formula, mode: "math") $

Значения параметров приведены выше, в таблице параметров аппроксимирующего
закона. #d.generator.note

= Характеристики сгенерированной ЧП

#figure(
  caption: [Характеристики сгенерированной случайной ЧП, форма 2],
  table(
    columns: (3.1cm, 1.3cm) + d.sizes.map(_ => 1fr),
    align: (left, center) + d.sizes.map(_ => right),
    table.header([Характеристика], [], ..d.sizes.map(n => [#n])),
    ..d.form2.map(r => (
      table.cell(rowspan: 2, align: horizon)[#r.label],
      [Знач.], ..r.values.map(v => [#v]),
      [\%], ..r.percents.map(v => [#v]),
    )).flatten()
  ),
)

Строка «\%» — отклонение характеристик сгенерированной случайной
последовательности от одноимённых значений заданной ЧП.

*Выводы.* #d.conclusions.generated

= Сравнение распределений

#figure(
  image("plots/plot3_fit.png", width: 80%),
  caption: [
    Гистограмма заданной ЧП, гистограмма сгенерированной ЧП
    и плотность аппроксимирующего закона
  ],
)

Гистограмма нормирована на $n dot Delta x$, поэтому её площадь равна единице
и сопоставима с плотностью распределения $f(x)$.

= Корреляционный анализ заданной и сгенерированной ЧП

$ r_(X Y) = "cov"_(X Y) / (sigma_X sigma_Y)
  = (sum_i (x_i - M[X]) (y_i - M[Y]))
    / sqrt(sum_i (x_i - M[X])^2 dot sum_i (y_i - M[Y])^2) $

Расчётное значение: $r = #d.cross_correlation$.

*Вывод.* #d.conclusions.correlation

= Выводы

#d.conclusions.final
