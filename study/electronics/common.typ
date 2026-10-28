// Общее оформление отчётов по «Электронике» (преподаватель Никитина М. В.).
// Титульный лист повторяет образец из Приложения 2 методички ЛР1.

#let author = (
  name: "Данилов Тимофей",
  group: "P3331",
)

#let setup(body) = {
  set text(font: "Times New Roman", size: 12pt, lang: "ru")
  set page(paper: "a4", margin: (top: 20mm, bottom: 20mm, left: 25mm, right: 15mm))
  set par(justify: true, first-line-indent: (amount: 1.25cm, all: true), leading: 0.65em)
  set heading(numbering: none)
  show heading: it => { v(0.6em); it; v(0.4em) }
  set table(stroke: 0.5pt + rgb("555"), inset: 4pt, align: center + horizon)
  show table: set text(size: 10pt)
  show table: set par(justify: false)
  show figure.caption: set text(size: 10pt)
  show figure: set block(breakable: false)
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: image): set figure(supplement: [Рисунок])
  set math.equation(numbering: none)
  body
}

#let titlepage(title: "", variant: "", submitted: "", year: "2026") = {
  set page(numbering: none)
  set par(first-line-indent: 0pt, justify: false)
  v(30mm)
  align(center)[
    #text(size: 16pt, weight: "bold")[ЭЛЕКТРОНИКА]
    #v(25mm)
    #text(size: 18pt, weight: "bold")[ОТЧЕТ]
    #v(4mm)
    #text(size: 14pt)[по лабораторной работе]
    #v(8mm)
    #text(size: 15pt, weight: "bold")[#title]
    #v(15mm)
    #text(size: 13pt)[Группа #author.group]
    #v(3mm)
    #text(size: 13pt)[Вариант #variant]
  ]
  v(1fr)
  block(inset: (left: 70mm))[
    #set text(size: 12pt)
    Выполнил: #author.name \
    #v(4mm)
    Дата сдачи отчета: #submitted \
    #v(4mm)
    Дата защиты: \
    #v(4mm)
    Количество баллов:
  ]
  v(1fr)
  align(center)[СПб – #year]
  pagebreak()
}

// Число с округлением до тысячных и десятичной запятой (требование методички).
#let num(x, digits: 3) = {
  let r = calc.round(float(x), digits: digits)
  if calc.abs(r) < calc.pow(10.0, -digits) / 2 { r = 0.0 }
  let s = str(calc.abs(r))
  let parts = s.split(".")
  let int-part = parts.at(0)
  let frac = if parts.len() > 1 { parts.at(1) } else { "" }
  while frac.len() < digits { frac += "0" }
  let sign = if r < 0 { "−" } else { "" }
  if digits == 0 { sign + int-part } else { sign + int-part + "," + frac }
}
