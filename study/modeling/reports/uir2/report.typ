#set text(font: "Liberation Serif", size: 12pt, lang: "ru")
#set page(margin: 25mm)
#set par(justify: true, first-line-indent: 1.25cm)
#show heading: it => { v(0.6em); it; v(0.4em) }
#show table.cell.where(y: 0): strong
#set table(stroke: 0.5pt + rgb("555"), inset: 4pt)
#show table: set text(size: 10pt)
#show figure.caption: set text(size: 10pt)
#show figure: set block(breakable: false)
#show figure.where(kind: table): set figure.caption(position: bottom)
#show figure.where(kind: image): set figure(supplement: [Рисунок])

// Числа и выводы берутся из расчёта:
//   cd ../../uir/uir2/solution && python3 -m uir2 -v 60/60/31 --typst ../../../reports/uir2
#let d = json("data.json")
#let m(s) = eval(s, mode: "math")
#let s1 = d.systems.at(0)
#let s2 = d.systems.at(1)

#import "title.typ": titlepage

#titlepage(
  title: [Марковские модели систем массового обслуживания\ (вариант #d.variant)],
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

Изучить метод марковских случайных процессов на простых моделях: построить
и рассчитать марковские модели двух многоканальных СМО с однородным потоком
заявок и выбрать из них лучшую по заданному критерию эффективности.

= Постановка задачи и исходные данные

Вариант #d.variant. СИСТЕМА_1 взята из варианта #d.n1 таблицы 1, СИСТЕМА_2 из
варианта #d.n2 той же таблицы, параметры нагрузки из строки #d.ng таблицы 2.

#figure(
  caption: [Параметры нагрузки],
  table(
    columns: 5,
    align: center,
    table.header([$lambda$, 1/с], [$b$, с], [$p_1$], [$p_2$], [$p_3$]),
    [#d.lam], [#d.b], ..d.probs.map(x => [#x]),
  ),
)

Заявка с вероятностью $p_i$ идёт к прибору П#sub[$i$]. Если прибор занят,
она встаёт в его накопитель. Если накопителя нет или он полон, заявка
теряется. В двухканальной СИСТЕМЕ_2 к П2 идут заявки с вероятностью $p_2 + p_3$.

Сумма $N_1 + N_2 = #(d.n1 + d.n2)$ #d.criterion_rule, поэтому критерий берётся
по варианту #d.criterion_from: (#d.criterion_letter) #d.criterion.

= Описание исследуемых систем

#let devtable(s, cap) = figure(
  caption: cap,
  table(
    columns: 4,
    align: (center, center, center, left),
    table.header([Прибор], [Вер. занятия], [Ёмкость накопителя], [Закон обслуживания]),
    ..s.devices.flatten().map(x => [#x]),
  ),
)

#devtable(s1, [Структура СИСТЕМЫ_1])
#devtable(s2, [Структура СИСТЕМЫ_2])

Средняя длительность обслуживания во всех приборах $b = #d.b$ с, интенсивность
обслуживания $mu = 1 \/ b = #d.mu$ 1/с.

Закон Эрланга 2-го порядка по заданию стоит в одном любом приборе СИСТЕМЫ_2.
Я поставил его в П2: только перед ним есть накопитель, значит, только там закон
обслуживания влияет на очередь, а по очереди считается критерий.

Обслуживание по Эрлангу 2-го порядка разбито на две экспоненциальные фазы
со средним $b\/2$ каждая, то есть с интенсивностью $2 mu$. Моменты окончания
фаз образуют цепь Маркова (Алиев, разд. 5.5.3).

*Предположения.* Входящий поток простейший. Длительности обслуживания и фаз
распределены экспоненциально. Буферизация с потерями, обслуживание в порядке
поступления.

= Состояния марковских процессов

Каждая заявка сразу уходит к своему прибору, поэтому приборы работают
независимо. Состояние системы задаю числом заявок у каждого прибора, на
обслуживании и в накопителе: $(k_1, k_2, k_3)$ для СИСТЕМЫ_1 и $(k_1, k_2)$
для СИСТЕМЫ_2. У прибора с законом Эрланга нижний индекс показывает фазу
обслуживания. Например, $3_2$ значит, что у прибора три заявки и та, что
на обслуживании, находится на второй фазе.

У СИСТЕМЫ_1 получается $2 dot 5 dot 2 = #s1.n$ состояний, у СИСТЕМЫ_2
$2 dot (1 + 4 dot 2) = #s2.n$. В ограничение задания (не больше 20) обе укладываются.

Интенсивности потоков к приборам:

#figure(
  caption: [Интенсивности потоков заявок к приборам],
  table(
    columns: 4,
    align: (center, center, right, right),
    table.header([Обозн.], [Формула], [СИСТЕМА_1, 1/с], [СИСТЕМА_2, 1/с]),
    m("lambda_1"), m("lambda p_1"), [#s1.rates.at(0).at(2)], [#s2.rates.at(0).at(2)],
    m("lambda_2"), [$lambda p_2$ / $lambda (p_2 + p_3)$], [#s1.rates.at(1).at(2)], [#s2.rates.at(1).at(2)],
    m("lambda_3"), m("lambda p_3"), [#s1.rates.at(2).at(2)], [–],
  ),
)

= Размеченные графы переходов

Заявка, пришедшая к П#sub[$i$], увеличивает $k_i$ на единицу с интенсивностью
$lambda_i$, если накопитель не полон. Конец обслуживания уменьшает $k_i$
с интенсивностью $mu$. У прибора с законом Эрланга конец первой фазы переводит
заявку на вторую, а конец второй завершает обслуживание. Оба перехода идут
с интенсивностью $2 mu$.

#page(flipped: true)[
  #figure(
    image("plots/graph1.png", width: 100%),
    caption: [Размеченный граф переходов СИСТЕМЫ_1],
  )
]

#page(flipped: true)[
  #figure(
    image("plots/graph2.png", width: 100%),
    caption: [Размеченный граф переходов СИСТЕМЫ_2],
  )
]

= Матрицы интенсивностей переходов

Элемент $g_(i j)$ равен интенсивности перехода из $E_i$ в $E_j$ в 1/с.
На диагонали $g_(i i) = -sum_(j != i) g_(i j)$. Пустая клетка означает ноль.

#let gmatrix(s, cap) = {
  let n = s.n
  figure(
    caption: cap,
    {
      set text(size: 8pt)
      table(
        columns: (auto,) + range(n).map(_ => 1fr),
        inset: 2.5pt,
        align: center + horizon,
        table.header([], ..range(n).map(j => [$E_#(j + 1)$])),
        ..range(n).map(i => ([$E_#(i + 1)$], ..s.matrix.at(i).map(x => [#x]))).flatten(),
      )
    },
  )
}

#page(flipped: true)[
  #gmatrix(s1, [Матрица интенсивностей переходов СИСТЕМЫ_1])
]
#page(flipped: true)[
  #gmatrix(s2, [Матрица интенсивностей переходов СИСТЕМЫ_2])
]

= Стационарные вероятности

Стационарные вероятности находятся из системы $P G = 0$ с условием
нормировки $sum_i p_i = 1$. Одно уравнение баланса лишнее, его я заменил
нормировкой и решил систему методом Гаусса.

#figure(
  caption: [Стационарные вероятности состояний, форма 1],
  table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr),
    align: (center, center, right, center, right),
    table.header(
      table.cell(rowspan: 2)[№],
      table.cell(colspan: 2)[СИСТЕМА_1],
      table.cell(colspan: 2)[СИСТЕМА_2],
      [Обозн.], [Вер-ть], [Обозн.], [Вер-ть],
    ),
    ..range(d.form1_rows).map(i => (
      [#(i + 1)],
      if i < s1.n { m(s1.states.at(i)) } else { [] },
      if i < s1.n { [#s1.probs.at(i)] } else { [] },
      if i < s2.n { m(s2.states.at(i)) } else { [] },
      if i < s2.n { [#s2.probs.at(i)] } else { [] },
    )).flatten(),
    [$sum$], [], [#s1.psum], [], [#s2.psum],
  ),
)

= Характеристики систем

Все характеристики считаю через стационарные вероятности. Для прибора
П#sub[$i$] суммирую по состояниям $E_j$ с нужным значением $k_i$. Поток
пуассоновский, поэтому вероятность потери равна вероятности того, что прибор
занят и накопитель полон ($k_i = r_i + 1$). Загрузку системы беру как среднюю
загрузку $K$ приборов.

#let formtable(s, cap) = figure(
  caption: cap,
  table(
    columns: (auto, 1fr),
    align: (center, left),
    table.header([Прибор], [Формулы]),
    ..s.formulas.map(f => ([#f.device], [#f.items.map(x => m(x)).join(linebreak())])).flatten(),
  ),
)

#formtable(s1, [Расчётные формулы СИСТЕМЫ_1 через вероятности состояний])
#formtable(s2, [Расчётные формулы СИСТЕМЫ_2 через вероятности состояний])

#figure(
  caption: [Характеристики систем, форма 2],
  table(
    columns: (auto, auto, auto, 1fr, 1fr),
    align: (left, center, left, right, right),
    table.header([Хар-ка], [Прибор], [Расчётная формула], [СИСТ. 1], [СИСТ. 2]),
    ..d.form2.map(c => (
      table.cell(rowspan: c.rows.len(), align: horizon)[#c.label],
      ..c.rows.map(r => ([#r.device], m(r.formula), ..r.values.map(v => [#v]))).flatten(),
    )).flatten(),
  ),
)

*Проверка.* Формулы Литтла в расчёте не участвовали, поэтому ими можно
проверить результат: $rho_i = lambda'_i b$, $m_i = l_i + rho_i$, $u_i = w_i + b$.

#let checktable(s, cap) = figure(
  caption: cap,
  table(
    columns: 7,
    align: (center,) + range(6).map(_ => right),
    table.header([Прибор], [$rho_i$], [$lambda'_i b$], [$m_i$], [$l_i + rho_i$], [$u_i$], [$w_i + b$]),
    ..s.checks.flatten().map(x => [#x]),
  ),
)

#checktable(s1, [Проверка характеристик СИСТЕМЫ_1])
#checktable(s2, [Проверка характеристик СИСТЕМЫ_2])

Все пары сошлись.

= Сравнительный анализ

#d.conclusions.common

#d.conclusions.queue

#d.conclusions.law

Чтобы сравнить системы не только в одной точке, я пересчитал их при разной
интенсивности потока $lambda$, остальные параметры не менял. Пунктиром
на графиках отмечено заданное $lambda = #d.lam$ 1/с.

#figure(
  image("plots/compare.png", width: 100%),
  caption: [Характеристики систем в зависимости от интенсивности потока],
)

#figure(
  caption: [Характеристики систем при разной интенсивности потока],
  table(
    columns: 7,
    align: right,
    table.header(
      table.cell(rowspan: 2)[$lambda$, 1/с],
      table.cell(colspan: 2)[$L$],
      table.cell(colspan: 2)[$pi$],
      table.cell(colspan: 2)[$u$, с],
      [СИСТ. 1], [СИСТ. 2], [СИСТ. 1], [СИСТ. 2], [СИСТ. 1], [СИСТ. 2],
    ),
    ..d.sweep.flatten().map(x => [#x]),
  ),
)

#d.conclusions.sweep

= Выбор варианта организации системы

#d.conclusions.choice

= Выводы

Построил марковские модели двух СМО с раздельными накопителями: на #s1.n
состояний для трёхканальной СИСТЕМЫ_1 и на #s2.n для двухканальной СИСТЕМЫ_2
с обслуживанием по Эрлангу в П2. Проверка по формулам Литтла сошлась.

По критерию «#d.criterion» лучше #d.conclusions.winner. Дело в том, как
поток делится между приборами: в СИСТЕМЕ_1 часть заявок забирает П3, и на
единственный прибор с очередью приходит меньше. Большие потери в обеих
системах даёт П1 без накопителя. Выбор между системами их не уменьшит,
для этого нужно менять сам П1.
