== Интрузивность инструментов

`graph_traverse` и `graph_traverse_mmap`, 1 МиБ, по 3 запуска на инструмент
(`scripts/characterize_variant.sh`), медиана wall:

#table(
  columns: (auto, auto, auto),
  align: (left, right, right),
  table.header([*Инструмент*], [*graph_traverse, с*], [*graph_traverse_mmap, с*]),
  [без инструмента], [11,24], [0,0143],
  [`/usr/bin/time -v`], [13,46], [0,0176],
  [`strace -c`], [25,34], [0,0283],
)

`strace` увеличивает время обеих программ примерно в 2 раза и в серии не
использовался. У `/usr/bin/time -v` добавка ≈ 3 мс на запуск видна у
`graph_traverse_mmap`; она одинакова для всех запусков серии. Для
`graph_traverse` разница меньше разброса между запусками.
