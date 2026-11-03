// Короткий отчёт: только то, что требует п. 6 задания УИР 2.
// Данные и рисунки те же, что у report.typ: data.json, plots/, winmark/.
#set text(font: "Liberation Serif", size: 12pt, lang: "ru")
#set page(margin: 25mm)
#set par(justify: true, first-line-indent: 1.25cm)
#show heading: it => { v(0.6em); it; v(0.4em) }
#set heading(numbering: "1.")
#show table.cell.where(y: 0): strong
#set table(stroke: 0.5pt + rgb("555"), inset: 4pt)
#show table: set text(size: 10pt)
#show figure.caption: set text(size: 10pt)
#show figure: set block(breakable: false)
#show figure.where(kind: table): set figure.caption(position: bottom)
#show figure.where(kind: image): set figure(supplement: [Рисунок])

#let d = json("data.json")
#let s1 = d.systems.at(0)
#let s2 = d.systems.at(1)
#let m(s) = eval(s, mode: "math")

#import "title.typ": titlepage

#titlepage(
  title: [Марковские модели систем массового обслуживания\ (вариант #d.variant.code)],
  student: d.author.name,
  group: d.author.group,
  teacher: d.author.teacher,
  year: d.author.year,
)

#set page(numbering: "1")
#counter(page).update(1)

= Постановка задачи и исходные данные

Нужно построить марковские модели двух СМО, рассчитать в программе MARK их
стационарные вероятности и характеристики и выбрать лучшую систему по критерию
эффективности.

Вариант #d.variant.code: СИСТЕМА\_1 из строки #d.variant.n1 таблицы 1,
СИСТЕМА\_2 из строки #d.variant.n2, нагрузка из строки #d.variant.ng таблицы 2.

#figure(
  caption: [Исходные данные],
  table(
    columns: (1fr, auto, auto),
    align: (left, center, center),
    table.header([Параметр], [СИСТЕМА\_1], [СИСТЕМА\_2]),
    [Число приборов], [#s1.devices.len()], [#s2.devices.len(), в одном закон Эрланга 2-го порядка],
    [Ёмкости накопителей], [#s1.devices.map(x => str(x.buffer)).join("/")],
      [#s2.devices.map(x => str(x.buffer)).join("/")],
    [Интенсивность потока $lambda$, 1/с], table.cell(colspan: 2)[#d.variant.lam],
    [Средняя длительность обслуживания $b$, с], table.cell(colspan: 2)[#d.variant.b],
    [Вероятности занятия приборов], [#d.variant.probs3.join(" / ")],
      [#d.variant.probs2.join(" / ")],
  ),
)

Для двухканальной СИСТЕМЫ\_2 вероятность занятия П2 равна сумме вероятностей
П2 и П3 из таблицы 2. Сумма $N_1 + N_2 = #d.variant.sum$ #d.variant.parity,
поэтому критерий берётся по $N_2$: (#d.variant.criterion) #d.variant.criterion_text.

= Описание исследуемых систем

#figure(image("plots/scheme1.png", width: 80%),
  caption: [СИСТЕМА\_1])
#figure(image("plots/scheme2.png", width: 80%),
  caption: [СИСТЕМА\_2])

Заявка с вероятностью $q_i$ идёт к прибору П$i$. Если прибор занят, она встаёт
в его накопитель. Если накопителя нет или он полон, заявка теряется. Поток
простейший, обслуживание экспоненциальное с $mu = 1\/b = #d.variant.mu$ 1/с.

Закон Эрланга по заданию стоит в любом приборе СИСТЕМЫ\_2. Я поставил его в П2:
только у него есть накопитель, а у прибора без накопителя вероятности состояний
от закона обслуживания не зависят. Обслуживание по Эрлангу 2-го порядка разбито
на две экспоненциальные фазы по $b\/2$, то есть с интенсивностью
$2 mu = #s2.elements.find(x => x.name == "mu2").value$ 1/с. Фаза хранится
в состоянии, поэтому процесс остаётся марковским.

#figure(
  caption: [Потоки и нагрузки приборов],
  table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: center,
    table.header([Система], [Прибор], [$q_i$], [$lambda_i$, 1/с], [$y_i = lambda_i b$], [Закон]),
    ..(s1, s2).map(s => s.devices.map(x => (
      [#s.name], [П#x.index], [#x.share], [#x.lam], [#x.y], [#x.law_short],
    )).flatten()).flatten()
  ),
)

= Перечень состояний

Состояние задаётся числом заявок у каждого прибора, на обслуживании и в
накопителе. У П2 СИСТЕМЫ\_2 нижний индекс показывает фазу обслуживания:
$2_1$ значит, что у прибора две заявки и текущая на первой фазе. Получилось
#s1.states состояний у СИСТЕМЫ\_1 и #s2.states у СИСТЕМЫ\_2.

#let states-table(s) = table(
  columns: (auto, auto, 1fr),
  align: (center, center, left),
  inset: 3pt,
  table.header([№], [Код], [Содержание состояния]),
  ..s.codes.enumerate().map(((i, c)) => ([E#i], [#c], [#s.descriptions.at(i)])).flatten()
)

#figure(caption: [Состояния СИСТЕМЫ\_1], states-table(s1))
#figure(caption: [Состояния СИСТЕМЫ\_2], states-table(s2))

= Результаты

== Размеченные графы переходов

Заявка к П$i$ приходит с интенсивностью $lambda_i$, если у прибора есть место.
Обслуживание заканчивается с интенсивностью $mu$, у прибора с Эрлангом каждая
фаза с интенсивностью $2 mu$.

#page(flipped: true, margin: 15mm)[
  #figure(image("plots/graph1.png", width: 100%),
    caption: [Размеченный граф переходов СИСТЕМЫ\_1])
]
#page(flipped: true, margin: 15mm)[
  #figure(image("plots/graph2.png", width: 100%),
    caption: [Размеченный граф переходов СИСТЕМЫ\_2])
]

#let gmatrix(s, size) = {
  set text(size: size)
  table(
    columns: (auto,) + s.matrix.map(_ => 1fr),
    align: center + horizon,
    inset: 1.6pt,
    table.header([], ..range(s.states).map(j => [#j])),
    ..s.matrix.enumerate().map(((i, row)) => (
      [*#i*], ..row.enumerate().map(((j, v)) =>
        if i == j { table.cell(fill: rgb("eee"))[#v] } else [#v])
    )).flatten()
  )
}

#page(flipped: true, margin: 15mm)[
  == Матрицы интенсивностей переходов

  $g_(i j)$ равно интенсивности перехода из $E_i$ в $E_j$, на диагонали
  $g_(i i) = -sum_(j != i) g_(i j)$. Значения:
  #s1.elements.map(x => [#x.name = #x.value]).join(", ") для СИСТЕМЫ\_1,
  #s2.elements.map(x => [#x.name = #x.value]).join(", ") для СИСТЕМЫ\_2.

  #figure(caption: [Матрица интенсивностей переходов СИСТЕМЫ\_1], gmatrix(s1, 9pt))
]
#page(flipped: true, margin: 15mm)[
  #figure(caption: [Матрица интенсивностей переходов СИСТЕМЫ\_2], gmatrix(s2, 9.5pt))
]

== Стационарные вероятности

Матрицы введены в MARK, программа решила систему $P G = 0$ с нормировкой
$sum p_i = 1$.

#figure(
  caption: [Стационарные вероятности состояний, форма 1],
  table(
    columns: (auto, 1fr, auto, 1fr, auto),
    align: (center, left, right, left, right),
    inset: 3pt,
    table.header(table.cell(rowspan: 2, align: horizon)[Номер состояния],
      table.cell(colspan: 2)[СИСТЕМА\_1], table.cell(colspan: 2)[СИСТЕМА\_2],
      [Обозн.], [Вер-ть], [Обозн.], [Вер-ть]),
    ..d.form1.flatten().map(v => [#v])
  ),
)

#grid(columns: 2, gutter: 1em,
  [#figure(image("winmark/s1_probs.png", width: 100%),
    caption: [Вероятности СИСТЕМЫ\_1 в MARK])],
  [#figure(image("winmark/s2_probs.png", width: 100%),
    caption: [Вероятности СИСТЕМЫ\_2 в MARK])],
)

== Характеристики систем

Характеристики считаются через стационарные вероятности: сумма берётся по
состояниям $E$, для которых выполнено условие под знаком суммы. $n_i$ здесь
число заявок у П$i$ в состоянии $E$, $r_i$ ёмкость его накопителя, $N$ число
приборов.

Время ожидания тоже считается через вероятности, без формулы Литтла. Принятая
заявка застаёт у прибора состояние $E$ с вероятностью $p(E) \/ (1 - pi_i)$
и ждёт в среднем $tau(E) dot b$, где $tau(E) = (n_i - 1) + (k - f + 1) \/ k$.
Первое слагаемое отвечает за заявки впереди в очереди, второе за остаток
обслуживания текущей; $k$ число фаз, $f$ фаза текущей заявки.

#figure(
  caption: [Характеристики систем, форма 2],
  table(
    columns: (auto, auto, 1fr, auto, auto),
    align: (left + horizon, center + horizon, center + horizon, right + horizon, right + horizon),
    inset: 3pt,
    table.header([Хар-ка], [Прибор], [Расчётная формула], [СИСТ. 1], [СИСТ. 2]),
    ..d.form2.map(r => {
      let n = r.devices.len() + 1
      let head = (table.cell(rowspan: n)[#r.title],)
      let dev = r.devices.enumerate().map(((k, x)) => {
        let cells = ([#x.at(0)],)
        if k == 0 { cells.push(table.cell(rowspan: r.devices.len())[#m(r.formula)]) }
        cells + ([#x.at(1)], [#x.at(2)])
      }).flatten()
      head + dev + ([Сумм.], [#m(r.sum_formula)], [#r.sum.at(0)], [#r.sum.at(1)])
    }).flatten()
  ),
)

#grid(columns: 2, gutter: 1em,
  [#figure(image("winmark/s1_chars.png", width: 92%),
    caption: [Характеристики СИСТЕМЫ\_1 в MARK])],
  [#figure(image("winmark/s2_chars.png", width: 92%),
    caption: [Характеристики СИСТЕМЫ\_2 в MARK])],
)

Прочерк стоит там, где прибора в системе нет. В строке «Сумм.» загрузки
указана средняя доля занятых приборов.

Формулы Литтла в расчёте не участвовали, ими я проверил результат.

#let little = (s) => s.checks.filter(c =>
  c.name.contains("Литтл") or c.name.starts-with("ρ") or c.name.starts-with("m ="))
#figure(
  caption: [Проверка по фундаментальным зависимостям],
  table(
    columns: (1fr, auto, auto),
    align: (left, center, center),
    table.header([Зависимость], [СИСТЕМА\_1], [СИСТЕМА\_2]),
    ..little(s1).zip(little(s2)).map(((a, b)) => (
      [#a.name], [#if a.ok [выполняется] else [*нет*]], [#if b.ok [выполняется] else [*нет*]],
    )).flatten()
  ),
)

== Сравнительный анализ

Чтобы сравнить системы не только в одной точке, я менял интенсивность потока
от 0,05 до 1,2 1/с при тех же остальных параметрах. Пунктир на графиках отмечает
заданное $lambda = #d.variant.lam$ 1/с.

#figure(image("plots/sweep_criterion.png", width: 80%),
  caption: [Суммарная длина очередей в зависимости от $lambda$])

#figure(image("plots/sweep_panel.png", width: 100%),
  caption: [Характеристики систем в зависимости от $lambda$])

#d.conclusions.totals

#d.conclusions.compare

#d.conclusions.sweep

== Выбор лучшего варианта

#d.conclusions.choice

Выбор не зависит от точки: при любом $lambda$ из исследованного диапазона
очередь у СИСТЕМЫ\_1 короче. В ней заявки, не попавшие на П1, делятся между
двумя приборами, и в очередь встаёт только часть из них. В СИСТЕМЕ\_2 весь
этот поток идёт на один П2, и он перегружен.
