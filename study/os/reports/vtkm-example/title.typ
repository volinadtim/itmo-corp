// Титульный лист в стиле отчётов ИТМО.
#let titlepage(
  ministry: "Министерство науки и высшего образования Российской Федерации",
  university: "Федеральное государственное автономное образовательное учреждение\nвысшего образования «Национальный исследовательский университет ИТМО»",
  faculty: "Факультет программной инженерии и компьютерной техники",
  discipline: "Операционные системы",
  work-kind: "Отчёт по лабораторной работе № 1",
  title: "",
  student: "",
  group: "",
  teacher: "",
  city: "Санкт-Петербург",
  year: "2026",
) = {
  set page(numbering: none, margin: (top: 20mm, bottom: 20mm, left: 30mm, right: 15mm))
  set par(justify: false, first-line-indent: 0pt, leading: 0.65em)

  align(center)[
    #text(size: 11pt)[#ministry]
    #v(2mm)
    #text(size: 11pt)[#university]
    #v(4mm)
    #line(length: 100%, stroke: 0.5pt)
    #v(2mm)
    #text(size: 12pt)[#faculty]
  ]

  v(1fr)

  align(center)[
    #text(size: 14pt)[#work-kind] \
    #v(3mm)
    #text(size: 12pt)[по дисциплине «#discipline»]
    #v(10mm)
    #text(size: 15pt, weight: "bold")[#title]
  ]

  v(1fr)

  align(right)[
    #block(width: 85mm)[
      #set align(left)
      *Выполнил:* \
      студент группы #group \
      #student
      #v(6mm)
      *Преподаватель практики:* \
      #teacher
    ]
  ]

  v(1fr)

  align(center)[#city, #year]
  pagebreak()
}
