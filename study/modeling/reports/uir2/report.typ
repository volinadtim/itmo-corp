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
// Подпись всегда снизу, и у рисунков, и у таблиц.
#show figure.where(kind: table): set figure.caption(position: bottom)
#show figure.where(kind: image): set figure(supplement: [Рисунок])

// Числа и выводы берутся из расчёта, а не набираются руками:
//   cd ../../uir/uir2/solution && python3 -m uir2 --typst ../../../reports/uir2
#let d = json("data.json")
#let s1 = d.systems.at(0)
#let s2 = d.systems.at(1)
#let m(s) = eval(s, mode: "math")

// Скриншоты WinMark лежат в winmark/. Без них (false) вместо картинок
// стоят рамки с подсказкой, что снять.
#let winmark-ready = true
#let screenshot(what, file, width: 100%) = if winmark-ready {
  image("winmark/" + file, width: width)
} else {
  block(
    width: 100%, height: 5.5cm, stroke: (dash: "dashed", paint: rgb("888")), inset: 8pt,
    align(center + horizon, text(size: 10pt, fill: rgb("666"))[
      Скриншот WinMark: #what \ файл winmark/#file]),
  )
}

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

#outline(title: [Содержание], depth: 1)
#pagebreak()

= Цель работы

Изучить метод марковских случайных процессов и применить его к простейшим
моделям: системам массового обслуживания (СМО) с однородным потоком заявок.
В работе строятся и рассчитываются марковские модели двух многоканальных СМО,
и по заданному критерию эффективности выбирается лучшая из них.

= Постановка задачи и исходные данные

Вариант #d.variant.code. Первые два числа указывают строки таблицы 1:
#d.variant.n1 для СИСТЕМЫ\_1 и #d.variant.n2 для СИСТЕМЫ\_2. Третье число,
#d.variant.ng, это последние две цифры номера группы P3331 и строка таблицы 2
с параметрами нагрузки.

#figure(
  caption: [Исходные данные варианта],
  table(
    columns: (1fr, auto, auto),
    align: (left, center, center),
    table.header([Параметр], [СИСТЕМА\_1], [СИСТЕМА\_2]),
    [Число приборов П], [#s1.devices.len()], [#s2.devices.len() (E2)],
    [Ёмкости накопителей ЕН], [#s1.devices.map(x => str(x.buffer)).join("/")],
      [#s2.devices.map(x => str(x.buffer)).join("/")],
    [Интенсивность потока $lambda$, 1/с], table.cell(colspan: 2)[#d.variant.lam],
    [Средняя длительность обслуживания $b$, с], table.cell(colspan: 2)[#d.variant.b],
    [Вероятности занятия приборов], [#d.variant.probs3.join(" / ")],
      [#d.variant.probs2.join(" / ")],
    [Критерий эффективности], table.cell(colspan: 2)[(#d.variant.criterion) #d.variant.criterion_text],
  ),
)

В двухканальной СИСТЕМЕ\_2 вероятность занятия П2 равна сумме вероятностей
П2 и П3 из таблицы 2. Сумма N1 + N2 = #d.variant.sum #d.variant.parity, поэтому
критерий берётся по N2. В строке #d.variant.n2 он тот же, что и для N1.

Нужно построить графы переходов обеих систем, рассчитать стационарные
вероятности и характеристики, сравнить системы и выбрать лучшую по критерию.

= Описание исследуемых систем

#figure(image("plots/scheme1.png", width: 85%),
  caption: [СИСТЕМА\_1: три прибора, накопитель ёмкостью 3 только перед П2])
#figure(image("plots/scheme2.png", width: 85%),
  caption: [СИСТЕМА\_2: два прибора, накопитель ёмкостью 3 перед П2, в П2 обслуживание по закону Эрланга 2-го порядка])

Заявка с вероятностью $q_i$ идёт к прибору П$i$. Если прибор занят, она встаёт
в его накопитель, а если накопитель полон или его нет, теряется. Очередь
обслуживается в порядке поступления (FIFO).

Процесс в системе марковский при следующих предположениях:
- поток заявок простейший, $lambda = #d.variant.lam$ 1/с. Прибор выбирается
  случайно и независимо, поэтому поток к П$i$ тоже простейший,
  $lambda_i = q_i lambda$;
- обслуживание экспоненциальное с интенсивностью $mu = 1\/b = #d.variant.mu$ 1/с;
- исключение: П2 в СИСТЕМЕ\_2, где обслуживание распределено по закону Эрланга
  2-го порядка со средним $b$ ($nu = 1\/sqrt(2) approx 0,707$). Его можно
  представить как две последовательные экспоненциальные фазы по $b\/2$, то есть
  с интенсивностью $2 mu = #s2.elements.find(x => x.name == "mu2").value$ 1/с.
  Если хранить фазу в состоянии, процесс остаётся марковским.

#d.conclusions.insensitivity

#figure(
  caption: [Интенсивности потоков и нагрузки приборов],
  table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: center,
    table.header([Система], [Прибор], [$q_i$], [$lambda_i$, 1/с], [$y_i = lambda_i b$], [Закон обсл.]),
    ..(s1, s2).map(s => s.devices.map(x => (
      [#s.name], [П#x.index], [#x.share], [#x.lam], [#x.y], [#x.law_short],
    )).flatten()).flatten()
  ),
)

= Перечень состояний марковского процесса

Состояние кодируется числом заявок у каждого прибора, на обслуживании
и в накопителе вместе. В СИСТЕМЕ\_1 это $(n_1, n_2, n_3)$ с $n_1, n_3 in {0, 1}$
и $n_2 in {0, ..., 4}$, всего $2 dot 5 dot 2 = #s1.states$ состояний.

В СИСТЕМЕ\_2 это $(n_1, n_2)$, и для П2 нижний индекс показывает фазу
обслуживания текущей заявки: $2_1$ значит, что у П2 две заявки и текущая
на первой фазе. У П2 получается $1 + 4 dot 2 = 9$ состояний, у системы
$2 dot 9 = #s2.states$. Обе модели укладываются в 20 состояний, упрощать
их не пришлось.

#let states-table(s) = table(
  columns: (auto, auto, 1fr),
  align: (center, center, left),
  inset: 3pt,
  table.header([№], [Код], [Содержание состояния]),
  ..s.codes.enumerate().map(((i, c)) => ([E#i], [#c], [#s.descriptions.at(i)])).flatten()
)

#figure(caption: [Состояния СИСТЕМЫ\_1], states-table(s1))
#figure(caption: [Состояния СИСТЕМЫ\_2], states-table(s2))

= Размеченные графы переходов

Переходы бывают двух видов. Поступление заявки к П$i$ идёт с интенсивностью
$lambda_i$, если у прибора есть место. Завершение обслуживания идёт
с интенсивностью $mu$. У эрланговского прибора с интенсивностью $2 mu$
заявка переходит на вторую фазу, а со второй фазы уходит.

#figure(image("plots/graph1.png", width: 100%),
  caption: [Размеченный граф переходов СИСТЕМЫ\_1 (#s1.states состояний, #s1.transitions переходов)])

#figure(image("plots/graph2.png", width: 100%),
  caption: [Размеченный граф переходов СИСТЕМЫ\_2 (#s2.states состояний, #s2.transitions переходов)])

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
  = Матрицы интенсивностей переходов

  $g_(i j)$ – интенсивность перехода из $E_i$ в $E_j$. На диагонали
  $g_(i i) = -sum_(j != i) g_(i j)$, поэтому сумма каждой строки равна нулю.
  Значения: #s1.elements.map(x => [#x.name = #x.value]).join(", ") (СИСТЕМА\_1);
  #s2.elements.map(x => [#x.name = #x.value]).join(", ") (СИСТЕМА\_2).

  #figure(caption: [Матрица интенсивностей переходов СИСТЕМЫ\_1], gmatrix(s1, 9pt))
]
#page(flipped: true, margin: 15mm)[
  #figure(caption: [Матрица интенсивностей переходов СИСТЕМЫ\_2], gmatrix(s2, 9.5pt))
]

= Система уравнений для стационарных вероятностей

Стационарные вероятности находятся из $P G = 0$ с условием нормировки:

$ sum_(i) p_i g_(i j) = 0, quad j = 0, ..., n - 1; quad sum_i p_i = 1. $

По графу уравнение для $E_j$ записывается так: $p_j$, умноженная на сумму
интенсивностей выхода из $E_j$, равна сумме $p_i$, умноженных на интенсивности
входа из $E_i$. Например, для $E_0$ СИСТЕМЫ\_1:

$ #m(s1.equations.at(0)). $

Все уравнения приведены в приложении А. Одно из них линейно зависит
от остальных, его заменяет условие нормировки. Из любого состояния достижимо
любое другое, а состояний конечное число, поэтому процесс эргодический
и стационарное решение единственно.

= Стационарные вероятности состояний

Система решена методом Гаусса в рациональных дробях, то есть точно.
В таблице вероятности округлены до четырёх знаков.

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

= Характеристики систем

Все характеристики посчитаны через стационарные вероятности. Сумма берётся
по состояниям $E$, для которых выполнено условие под знаком суммы. Здесь $n_i$
обозначает число заявок у П$i$ в состоянии $E$, $r_i$ – ёмкость его накопителя,
$N$ – число приборов.

Время ожидания тоже считается через вероятности, без формулы Литтла.
Простейший поток видит систему в стационарном распределении. Поэтому принятая
заявка застаёт у прибора состояние $E$ с вероятностью $p(E) \/ (1 - pi_i)$
и ждёт в среднем $tau(E) dot b$, где

$ tau(E) = (n_i - 1) + (k - f + 1) / k. $

Первое слагаемое – обслуживание заявок, стоящих впереди в очереди, второе –
остаток обслуживания текущей заявки. $k$ – число фаз закона Эрланга, $f$ –
фаза текущей заявки. У экспоненциального прибора ($k = 1$) остаток равен $b$
из-за отсутствия последействия, и $tau(E) = n_i$. У эрланговского ($k = 2$)
на первой фазе остаётся $b$, на второй $b\/2$.

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

Прочерк стоит там, где прибора в системе нет. В строке «Сумм.» загрузки
указан коэффициент загрузки системы, то есть средняя доля занятых приборов.
Среднее число занятых приборов вынесено в последнюю строку.

= Проверка результатов

Результаты проверены двумя способами: фундаментальными зависимостями, как
требует указание к форме 2, и отдельным аналитическим расчётом. Поток к каждому
прибору простейший, и приборы друг на друга не влияют. Поэтому число заявок
у прибора распределено так же, как в одноканальной СМО:

- П1 и П3 без накопителя, M/M/1/0: $p_0 = 1\/(1 + y)$, $p_1 = y\/(1 + y)$;
- П2 СИСТЕМЫ\_1, M/M/1/3: $p_k = y^k (1 - y) \/ (1 - y^5)$, $k = 0, ..., 4$;
- П2 СИСТЕМЫ\_2, M/E#sub[2]/1/3: явной формулы в пособии нет. Распределение
  посчитано через вложенную цепь Маркова в моменты ухода заявок, без фаз.

Для СИСТЕМЫ\_1 ещё проверено, что вероятность каждого из 20 состояний равна
произведению вероятностей состояний трёх приборов.

#let checks-table(s) = table(
  columns: (1fr, auto, auto),
  align: (left, right, center),
  table.header([Проверка], [Расхождение], [Результат]),
  ..s.checks.map(c => ([#c.name], [#c.value], [#if c.ok [совпадает] else [*нет*]])).flatten()
)

#figure(caption: [Проверки СИСТЕМЫ\_1], checks-table(s1))
#figure(caption: [Проверки СИСТЕМЫ\_2], checks-table(s2))

Расчёт идёт в дробях, поэтому расхождения нулевые. Исключение – последняя
строка: формулы WinMark вычисляются в числах с плавающей точкой.

= Расчёт в программе WinMark

Расчёт повторён в WinMark. Элементы матрицы:
#s1.elements.map(x => [#x.name = #x.value]).join(", ") для СИСТЕМЫ\_1 и
#s2.elements.map(x => [#x.name = #x.value]).join(", ") для СИСТЕМЫ\_2;
состояния пронумерованы с 0, как в форме 1. Формулы характеристик –
в приложении Б.

#figure(screenshot([матрица интенсивностей СИСТЕМЫ\_1], "s1_matrix.png"),
  caption: [Матрица интенсивностей СИСТЕМЫ\_1 в WinMark], kind: image)
#grid(columns: 2, gutter: 1em,
  [#figure(screenshot([стационарные вероятности СИСТЕМЫ\_1], "s1_probs.png"),
    caption: [Стационарные вероятности СИСТЕМЫ\_1 в WinMark], kind: image)],
  [#figure(screenshot([характеристики СИСТЕМЫ\_1], "s1_chars.png", width: 92%),
    caption: [Характеристики СИСТЕМЫ\_1 в WinMark], kind: image)],
)
#figure(screenshot([матрица интенсивностей СИСТЕМЫ\_2], "s2_matrix.png"),
  caption: [Матрица интенсивностей СИСТЕМЫ\_2 в WinMark], kind: image)
#grid(columns: 2, gutter: 1em,
  [#figure(screenshot([стационарные вероятности СИСТЕМЫ\_2], "s2_probs.png"),
    caption: [Стационарные вероятности СИСТЕМЫ\_2 в WinMark], kind: image)],
  [#figure(screenshot([характеристики СИСТЕМЫ\_2], "s2_chars.png", width: 92%),
    caption: [Характеристики СИСТЕМЫ\_2 в WinMark], kind: image)],
)

Результаты WinMark (четыре знака после запятой) совпали с формами 1 и 2
во всех знаках: вероятности всех состояний и все характеристики обеих систем.

= Сравнительный анализ систем

Интенсивность потока менялась от 0,05 до 1,2 1/с, остальные параметры те же.
Пунктирная вертикаль на графиках отмечает исходное $lambda = #d.variant.lam$ 1/с.
WinMark варьирует параметр в пяти точках, значения в них приведены в таблице.

#figure(image("plots/sweep_criterion.png", width: 85%),
  caption: [Суммарная длина очередей (критерий эффективности) в зависимости от $lambda$])

#figure(image("plots/sweep_panel.png", width: 100%),
  caption: [Характеристики систем в зависимости от интенсивности потока])

#figure(
  caption: [Характеристики при варьировании $lambda$ (точки варьирования WinMark)],
  table(
    columns: (auto, auto) + d.winmark_points.lams.map(_ => 1fr),
    align: (left, center) + d.winmark_points.lams.map(_ => right),
    inset: 3pt,
    table.header([Хар-ка], [Сист.], ..d.winmark_points.lams.map(v => [$lambda = #v$])),
    ..d.winmark_points.rows.map(r => (
      table.cell(rowspan: 2, align: horizon)[#r.name], [1], ..r.s1.map(v => [#v]),
      [2], ..r.s2.map(v => [#v]),
    )).flatten()
  ),
)

Те же пять точек посчитаны в WinMark: начальные значения $lambda_i$ равны
шагу, пять шагов дают $lambda$ = 0,2; 0,4; …; 1,0. Значения совпали с таблицей.

#grid(columns: 2, gutter: 1em,
  [#figure(screenshot([варьирование СИСТЕМЫ\_1], "s1_vary.png"),
    caption: [Варьирование $lambda$ в WinMark, СИСТЕМА\_1], kind: image)],
  [#figure(screenshot([варьирование СИСТЕМЫ\_2], "s2_vary.png"),
    caption: [Варьирование $lambda$ в WinMark, СИСТЕМА\_2], kind: image)],
)
#figure(screenshot([график Lsum СИСТЕМЫ\_1], "s1_graph.png", width: 85%),
  caption: [Суммарная длина очередей СИСТЕМЫ\_1 по шагам варьирования (WinMark)], kind: image)
#figure(screenshot([график Lsum СИСТЕМЫ\_2], "s2_graph.png", width: 85%),
  caption: [Суммарная длина очередей СИСТЕМЫ\_2 по шагам варьирования (WinMark)], kind: image)

#d.conclusions.totals

#d.conclusions.device1

#d.conclusions.compare

#d.conclusions.erlang

#d.conclusions.sweep

= Выбор наилучшего варианта организации системы

#d.conclusions.choice

Выбор не зависит от исходной точки: при любом $lambda$ из исследованного
диапазона очередь СИСТЕМЫ\_1 короче. В СИСТЕМЕ\_1 заявки, не попавшие на П1,
делятся между двумя приборами, и в очередь встаёт только часть из них.

= Выводы

По критерию минимальной суммарной длины очередей лучше СИСТЕМА\_1.
Разницу даёт не П1, одинаковый в обеих системах, а то, как распределяется
остальной поток: в СИСТЕМЕ\_2 он весь идёт на один перегруженный прибор.

Модели получились на #s1.states и #s2.states состояний, эрланговское обслуживание
учтено методом фаз. Вероятности посчитаны точно, и с ними сходятся формулы
одноканальных СМО, формула Литтла и баланс потоков. Попутно выяснилось,
что Эрланг в приборе без накопителя ничего не меняет, а в перегруженном
приборе с накопителем снижает потери ценой чуть более длинной очереди.

#pagebreak()
#set heading(numbering: none)

= Приложение А. Уравнения для стационарных вероятностей

#set text(size: 9pt)
#set par(first-line-indent: 0pt, justify: false)

// Две колонки поровну: первая половина уравнений слева, вторая справа.
#let eqs(s) = {
  let half = calc.ceil(s.equations.len() / 2)
  let col(xs) = xs.map(e => $ #m(e) $).join()
  grid(columns: (1fr, 1fr), gutter: 4mm,
    col(s.equations.slice(0, half)), col(s.equations.slice(half)))
}

*СИСТЕМА\_1*

#eqs(s1)

*СИСТЕМА\_2*

#eqs(s2)

Условие нормировки: $p_0 + p_1 + ... + p_(n-1) = 1$.

= Приложение Б. Формулы характеристик для WinMark

Вероятность состояния с номером $N$ из формы 1 записывается как pN.
Формулы вводятся по порядку: каждая использует только элементы матрицы,
вероятности и уже введённые характеристики.

#let wm-table(s) = table(
  columns: (auto, 1fr, auto),
  align: (left, left, left),
  inset: 3pt,
  table.header([Имя], [Формула], [Смысл]),
  // После «+» пробел нулевой ширины, чтобы длинная сумма переносилась.
  ..s.winmark.map(x => ([#x.name], [#raw(x.formula.replace("+", "+\u{200b}"))], [#x.desc])).flatten()
)

#figure(caption: [Формулы WinMark для СИСТЕМЫ\_1], wm-table(s1))
#figure(caption: [Формулы WinMark для СИСТЕМЫ\_2], wm-table(s2))
