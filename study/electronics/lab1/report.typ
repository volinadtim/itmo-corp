#import "../common.typ": setup, titlepage, num
#import "@preview/cetz:0.4.2": canvas, draw
#import "@preview/cetz-plot:0.1.3": plot

#show: setup

#titlepage(
  title: [Исследование характеристик источника электрической \ энергии постоянного тока],
  variant: "052",
  submitted: "27.10.2026",
)

#set page(numbering: "1")
#counter(page).update(2)

#outline(title: [СОДЕРЖАНИЕ], depth: 1)
#pagebreak()

// ---------------------------------------------------------------------------
// Исходные данные варианта 052 (Приложение 1 методички)
#let E = 18.0      // ЭДС, В
#let r = 375.0     // внутреннее сопротивление, Ом
#let Rn = (none, 3375, 1500, 875, 563, 375, 250, 161, 94, 42, 0) // none = ∞

// Результаты моделирования в LTspice (.meas, файл lab1.log; шаг = 11 - k):
// ток In, мА; напряжение Un, В.
#let In = (0.0, 4.80000022799, 9.60000045598, 14.3999997526, 19.1897656769,
  24.0000002086, 28.7999995053, 33.5820913315, 38.3795313537, 43.1654676795,
  48.0000004172)
#let Un = (18.0, 16.2000007629, 14.3999996185, 12.6000003815, 10.8038377762,
  9.0, 7.19999980927, 5.40671634674, 3.60767579079, 1.81294965744, 0.0)
#let Pn = range(11).map(k => Un.at(k) * In.at(k)) // мВт (В · мА)

// rk = (Unk − Unk+1) / (Ink+1 − Ink), k = 1…9; ток переводим в амперы
#let rk = range(1, 10).map(k =>
  (Un.at(k) - Un.at(k + 1)) / ((In.at(k + 1) - In.at(k)) / 1000))
#let rp = calc.sqrt(rk.map(x => x * x).sum() / rk.len())
#let Ep = Un.at(0)
#let Jp = Ep / rp * 1000 // мА

// Расчётные значения по схеме замещения
#let Inp = Rn.map(R => if R == none { 0.0 } else { Ep / (R + rp) * 1000 })
#let Unp = Inp.map(i => Ep - rp * i / 1000)
#let Pnp = range(11).map(k => Unp.at(k) * Inp.at(k))
#let ef = Rn.map(R => if R == none { 1.0 } else { 1 - rp / (rp + R) })

#let ex = 4 // строка для примера расчёта
// ---------------------------------------------------------------------------

= Цель работы

Исследование режимов работы и экспериментальное определение параметров
схемы замещения источника электрической энергии.

= Исходные данные для выполнения лабораторной работы

#figure(
  table(
    columns: 14,
    table.header(
      table.cell(rowspan: 2)[Вар.],
      table.cell(colspan: 2)[Параметры источника],
      table.cell(colspan: 11)[Параметры нагрузки, Ом],
      [$E$, В], [$r$, Ом],
      ..range(11).map(k => [$R_#k$]),
    ),
    [052], [#E], [#r],
    ..Rn.map(R => if R == none [$infinity$] else [#R]),
  ),
  numbering: none,
  caption: [Исходные данные варианта 052],
)

= Схема эксперимента

Источник V1 задан последовательной схемой замещения: ЭДС
$E = #num(E, digits: 0)$ В и внутреннее сопротивление $r = #num(r, digits: 0)$ Ом
(параметр Rser). R1 это нагрузка $R_n$. Её сопротивление я перебираю директивой
`.step param Rn list …`. Значение `10t` ($10^13$ Ом) задаёт холостой ход
($R_n = infinity$), `10f` ($10^(-14)$ Ом) задаёт короткое замыкание ($R_n = 0$).
Ток, напряжение и мощность нагрузки измеряю директивами `.meas`.

#figure(
  image("img/scheme.png", width: 90%),
  caption: [Схема эксперимента в LTspice],
) <fig-scheme>

= Таблица экспериментальных и расчётных данных

#figure(
  table(
    columns: 10,
    table.header(
      table.cell(rowspan: 4)[$k$],
      table.cell(colspan: 5)[Измерения],
      table.cell(colspan: 4)[Расчёт],
      table.cell(colspan: 9)[
        $r_р = #num(rp)$ Ом; #h(1em) $E_р = #num(Ep)$ В; #h(1em) $J_р = #num(Jp)$ мА
      ],
      [$R_(n k)$], [$I_(n k)$], [$U_(n k)$], [$P_(n k)$], [$r_k$],
      [$I_(n р k)$], [$U_(n р k)$], [$P_(n р k)$], [$eta_k$],
      [Ом], [мА], [В], [мВт], [Ом], [мА], [В], [мВт], [–],
    ),
    ..range(11).map(k => (
      [#k],
      if Rn.at(k) == none [$infinity$] else [#Rn.at(k)],
      [#num(In.at(k))], [#num(Un.at(k))], [#num(Pn.at(k))],
      if k >= 1 and k <= 9 [#num(rk.at(k - 1))] else [],
      [#num(Inp.at(k))], [#num(Unp.at(k))], [#num(Pnp.at(k))], [#num(ef.at(k))],
    )).flatten(),
  ),
  supplement: [Таблица],
  numbering: _ => "1.1",
  caption: [Экспериментальные и расчётные данные],
)

= Расчёт параметров схемы замещения

- ЭДС источника: $E_р = U_(n 0) = #num(Ep)$ В.
- Внутреннее сопротивление по парам соседних измерений:
  $ r_k = (U_(n k) - U_(n, k+1)) / (I_(n, k+1) - I_(n k)), quad k = 1 dots 9; $
  все девять значений равны $#num(rk.at(0))$ Ом. Оценка в виде среднего
  квадратического:
  $ r_р = sqrt(1/9 sum_(k=1)^9 r_k^2) = #num(rp) " Ом". $
- Ток короткого замыкания:
  $J_р = E_р / r_р = #num(Ep) / #num(rp) = #num(Jp)$ мА.

= Пример измерений и расчёта для опыта $k = #ex$

== Пример измерений

Результаты `.meas` LTspice пишет в журнал моделирования (View, SPICE Output
Log). Шаги `.step` он выполняет по возрастанию $R_n$, поэтому номер шага в
журнале и номер опыта связаны так: $k = 11 - "step"$. Опыт $k = #ex$
($R_(n #ex) = #Rn.at(ex)$ Ом) в журнале идёт шагом #(11 - ex). В нём
$U_(n #ex) = #num(Un.at(ex))$ В, $I_(n #ex) = #num(In.at(ex))$ мА,
$P_(n #ex) = #num(Pn.at(ex))$ мВт.

#figure(
  image("img/meas-log.png", width: 75%),
  caption: [Журнал измерений `.meas` (напряжение, ток и мощность нагрузки
    по шагам перебора $R_n$)],
)

== Пример расчёта

Данные для расчёта: $R_(n #ex) = #Rn.at(ex)$ Ом,
$I_(n #ex) = #num(In.at(ex))$ мА, $U_(n #ex) = #num(Un.at(ex))$ В,
$I_(n #(ex + 1)) = #num(In.at(ex + 1))$ мА, $U_(n #(ex + 1)) = #num(Un.at(ex + 1))$ В,
$E_р = #num(Ep)$ В, $r_р = #num(rp)$ Ом.

$ r_#ex = (U_(n #ex) - U_(n #(ex + 1))) / (I_(n #(ex + 1)) - I_(n #ex))
  = (#num(Un.at(ex)) - #num(Un.at(ex + 1))) / (#num(In.at(ex + 1) / 1000, digits: 6) - #num(In.at(ex) / 1000, digits: 6))
  = #num(rk.at(ex - 1)) " Ом" $

$ I_(n р #ex) = E_р / (R_(n #ex) + r_р) = #num(Ep) / (#Rn.at(ex) + #num(rp))
  = #num(Inp.at(ex)) " мА" $

$ U_(n р #ex) = E_р - r_р I_(n р #ex) = #num(Ep) - #num(rp) dot #num(Inp.at(ex) / 1000, digits: 6)
  = #num(Unp.at(ex)) " В" $

$ P_(n р #ex) = U_(n р #ex) I_(n р #ex) = #num(Unp.at(ex)) dot #num(Inp.at(ex))
  = #num(Pnp.at(ex)) " мВт" $

$ eta_#ex = 1 - r_р / (r_р + R_(n #ex)) = 1 - #num(rp) / (#num(rp) + #Rn.at(ex))
  = #num(ef.at(ex)) $

= Расчётная внешняя характеристика источника

Расчётную характеристику $U_n (I_n)$ провёл через точки
$[0; U_(n 0)] = [0; #num(Ep)]$ и $[I_(n 10); 0] = [#(num(In.at(10))); 0]$.
Маркеры это точки эксперимента из таблицы 1.1.

#figure(
  canvas({
    plot.plot(
      size: (13, 7),
      x-label: [$I_n$, мА], y-label: [$U_n$, В],
      x-min: 0, x-max: 50, x-tick-step: 5, x-grid: true,
      y-min: 0, y-max: 20, y-tick-step: 2, y-grid: true,
      legend: "inner-north-east",
      {
        plot.add(((0, Ep), (In.at(10), 0)), label: [расчёт])
        plot.add(range(11).map(k => (In.at(k), Un.at(k))),
          mark: "o", mark-size: 0.15, style: (stroke: none), label: [эксперимент])
      },
    )
  }),
  caption: [Внешняя характеристика источника $U_n (I_n)$],
)

= Рабочие характеристики $P_n (I_n)$ и $eta (I_n)$

#figure(
  canvas({
    plot.plot(
      size: (13, 7),
      axis-style: "scientific",
      x-label: [$I_n$, мА], y-label: [$P_n$, мВт], y2-label: [$eta$],
      x-min: 0, x-max: 50, x-tick-step: 5, x-grid: true,
      y-min: 0, y-max: 240, y-tick-step: 20, y-grid: true,
      y2-min: 0, y2-max: 1.2, y2-tick-step: 0.1,
      legend: "north",
      {
        plot.add(range(11).map(k => (Inp.at(k), Pnp.at(k))),
          mark: "o", mark-size: 0.12, line: "spline", label: [$P_n (I_n)$])
        plot.add(range(11).map(k => (Inp.at(k), ef.at(k))), axes: ("x", "y2"),
          mark: "square", mark-size: 0.12, label: [$eta (I_n)$])
      },
    )
  }),
  caption: [Зависимости мощности нагрузки и КПД от тока нагрузки],
)

= Выводы по работе

+ Внешняя характеристика источника получилась линейной. С ростом тока
  напряжение на нагрузке падает на $r I_n$, то есть на величину падения на
  внутреннем сопротивлении. Все точки эксперимента легли на расчётную прямую.
+ По данным эксперимента нашёл параметры схемы замещения:
  $E_р = #num(Ep)$ В, $r_р = #num(rp)$ Ом, $J_р = #num(Jp)$ мА. Они совпали с
  заданными $E = #num(E, digits: 0)$ В и $r = #num(r, digits: 0)$ Ом. Так и должно
  быть: модель источника в LTspice линейная, а приборы в ней без погрешности.
+ Мощность в нагрузке максимальна в согласованном режиме $R_n = r_р$ ($k = 5$):
  $P_(max) = #num(Pnp.at(5))$ мВт $= E^2 / (4 r)$ при токе
  $I_n = J_р / 2 = #num(Inp.at(5))$ мА. КПД при этом всего $#num(ef.at(5))$.
+ КПД падает с ростом тока линейно: от 1 на холостом ходу до 0 при коротком
  замыкании. Поэтому получить от источника одновременно максимум мощности и
  высокий КПД нельзя.
