#set text(font: "Liberation Serif", size: 12pt, lang: "ru")
#set page(margin: 25mm)
#set par(justify: true, first-line-indent: 1.25cm)
#show heading: it => { v(0.6em); it; v(0.4em) }

#import "title.typ": titlepage

#titlepage(
  title: [Introductory Experiment: обход графа как модель\ паттернов доступа к памяти и диску],
  student: "Данилов Тимофей Николаевич",
  group: "P3331",
  teacher: "Тюрин Иван",
)

#set page(numbering: "1")
#counter(page).update(1)

#outline(title: [Содержание], depth: 2)
#pagebreak()

= Ход работы

Pull Request: #link("TODO")[TODO: ссылка на PR]

== Цель и постановка эксперимента

TODO

== Паспорт системы

TODO: таблица из lscpu / free / smartctl

== Настройка окружения

TODO: governor, turbo, taskset, методология кэша

== Гипотезы

TODO

== План эксперимента

TODO: метрика, N, порядок запусков, прогрев

= Этап 1. read() / lseek()

TODO

= Этап 2. mmap()

TODO

= Этап 3. Итоговое сравнение

TODO

= Выводы

TODO

= Приложение А. Использование LLM

TODO: промпты и что именно генерировалось
