# C++ (курс Сорокина, КТ ИТМО)

Папка для обучения по курсу C++, который на КТ читает Иван Сорокин.
Курс сильно отличается от «обычного» вузовского C++ — упор на UB, RAII,
move-семантику, ручную реализацию STL-подобных контейнеров и типобезопасность.

## Теория

**Основной источник:** [cpp-kt.github.io/cpp-notes](https://cpp-kt.github.io/cpp-notes/course.html) —
конспекты лекций с ссылками на слайды и записи (33 темы).

**Официальный сайт курса** (программа, баллы, настройка окружения):
[pages.ct.itmo.ru/cpp/course](https://pages.ct.itmo.ru/cpp/course)

**Записи лекций:**
- [Twitch Сорокина](https://www.twitch.tv/sorokin_ivan) (стримы)
- [YouTube-канал курса](https://www.youtube.com/channel/UCmSlUseJEVQifMaH7PqlRoA)
- [ctlectures](https://www.youtube.com/@ctlectures) — канал с записями для разных групп КТ

На самом сайте конспектов практики нет — реальные домашки раздаются студентам
курса через GitHub Classroom (приватные репозитории), поэтому напрямую недоступны.
Ниже — обходной путь.

## Практика

Домашки курса — это классическая ITMO-задача «реализуй кусок STL с нуля под tests»:
даётся заголовочный файл-заглушка (`src/`) и набор GTest-тестов (`test/`), нужно
реализовать класс так, чтобы тесты прошли (включая UB-чувствительные assert'ы,
sanitizers, вопросы exception safety). Официальные репозитории с заданиями после
каждого потока архивируются/скрываются, но их публично форкали студенты — это
даёт доступ к тем же шаблонам и тестам:

| Тема (см. таблицу ниже) | Задание | Публичный форк с шаблоном + тестами |
|---|---|---|
| Классы, RAII, память | `socow-vector` (vector с SBO + COW) | [antkart/socow-vector-task](https://github.com/antkart/socow-vector-task) |
| Intrusive-контейнеры | `intrusive-list` | [spineight/intrusive-list-task](https://github.com/spineight/intrusive-list-task), [NH5pml30/intrusive_list_task](https://github.com/NH5pml30/intrusive_list_task) |
| Умные указатели | `shared-ptr` | [NH5pml30/shared_ptr_task](https://github.com/NH5pml30/shared_ptr_task) |
| Lambda / type erasure | `function` (свой `std::function`) | [NH5pml30/function_task](https://github.com/NH5pml30/function_task) |
| Signals | `signal` (свой boost::signals2) | [spineight/signal-task](https://github.com/spineight/signal-task), [NH5pml30/signal_task](https://github.com/NH5pml30/signal_task) |
| Optional/Variant | `optional` | [NH5pml30/optional_task](https://github.com/NH5pml30/optional_task) |
| Optional/Variant | `variant` | [spineight/variant-task](https://github.com/spineight/variant-task), [NH5pml30/variant_task](https://github.com/NH5pml30/variant_task) |

Как работать с таким репозиторием:
1. Клонировать форк (или сделать свой fork на GitHub, чтобы был свой прогресс).
2. Не смотреть чужую реализацию в `src/` до собственной попытки — стереть/переписать её самостоятельно.
3. Настроить окружение по официальной инструкции курса: [«Настройка окружения»](https://pages.ct.itmo.ru/cpp/course) (CMake + vcpkg + GTest, есть разделы под CLion/VSCode).
4. Собрать и гонять тесты (`ctest` или через IDE), пока всё не позеленеет.
5. Готовое решение — переносить в `solutions/<task-name>/` в этой папке (только код, без служебных файлов шаблона).

Официальный список заданий и баллов за них — раздел «Баллы → Практические/Домашние задания»
на [сайте курса](https://pages.ct.itmo.ru/cpp/course) — стоит свериться, не поменялся ли
состав/порядок задач в текущем потоке.

### Централизованного списка нет — вот что удалось найти

Официально задания текстом не публикуются: часть объясняют устно на отдельной
паре («практика»), часть — только через выданный студентам приватный репозиторий.
Публичного плейлиста именно «практик» (отдельно от лекций) тоже нет — на
[YouTube-канале курса](https://www.youtube.com/channel/UCmSlUseJEVQifMaH7PqlRoA)
и [ctlectures](https://www.youtube.com/@ctlectures) лежат записи лекций, семинары
отдельным списком не выкладывают.

Ниже — реальные условия задач, как они записаны в README студенческих форков
(за неимением официального текста). Для `shared-ptr` и `intrusive-list`
письменного условия в форках нет вообще — судя по всему, эти два задания
объясняли только устно на паре, интерфейс восстанавливается из `.h`-заголовка
в самом репозитории задания.

#### `socow-vector` — vector с small-object + copy-on-write оптимизациями

> Реализовать класс `socow_vector<T, SMALL_SIZE>`, аналогичный `std::vector`.
> *Small-object*: хранение небольшого числа элементов без динамической аллокации.
> *Copy-on-write*: копирование/присваивание больших векторов не копирует элементы
> сразу, а откладывает копирование до первой модифицирующей операции.
>
> Требования по сложности и exception safety:
> - конструктор копирования и `operator=` — `O(SMALL_SIZE)`, а не `O(size)`;
> - если оба вектора помещаются в small-buffer, `swap`/`operator=` дают базовую
>   гарантию, иначе — сильную;
> - неконстантные `operator[]`, `data()`, `front()`, `back()`, `pop_back()`,
>   `begin()`, `end()` — `O(size)` и сильная гарантия, если требуется COW-копирование,
>   иначе `O(1)` и `nothrow`;
> - `reserve(n)` гарантирует отсутствие переаллокаций до достижения размера `n`.

Источник: [antkart/socow-vector-task](https://github.com/antkart/socow-vector-task#readme)

#### `function` — свой `std::function`

> Полиморфная обёртка для Callable-объектов (указатель на функцию, лямбда, класс
> с `operator()`). Хранимый объект называется `target`.
>
> Идея реализации: поле `unique_ptr<concept>`, где `concept` — класс с виртуальными
> функциями (в т.ч. `operator()`), при конструировании из `F` создаётся
> `model<F>` в динамической памяти.
>
> С *small-object optimization*: раздельно хранить (1) выровненный массив байт
> под сам объект или указатель на него, (2) указатель на статически живущий
> «дескриптор» — набор функций для работы с хранилищем данного динамического типа.
> Мувающие операции должны быть `noexcept` (поэтому SOO применяется только когда
> мув самого `T` не бросает). `F* target<F>()` возвращает указатель, если
> динамический тип совпадает с `F`, иначе `nullptr`.

Источник: [spineight/function-task](https://github.com/spineight/function-task#readme)

#### `signal` — свой `boost::signals2`

> Реализовать упрощённую версию сигналов, похожих на те, что используются в Qt
> ([Signals & Slots](https://doc.qt.io/qt-5/signalsandslots.html)).

Источник: [spineight/signal-task](https://github.com/spineight/signal-task#readme)

#### `optional` — свой `std::optional`

> Написать `optional<T>`, интерфейс — в `optional.h` в репозитории задания,
> поведение соответствует `std::optional`.
>
> - Если у `T` нет какого-то из special members (например,
>   `is_copy_constructible<T> == false`), это свойство должно сохраняться и
>   для `optional<T>`.
> - Если `T` удовлетворяет `is_trivially_*`-трейту, `optional<T>` должен ему
>   удовлетворять тоже.
> - Должен работать в `constexpr`-контексте (см. тесты с `static_assert`), кроме
>   `constexpr operator=`/конструктора копирования для нетривиально
>   присваиваемых типов.

Источник: [spineight/optional-task](https://github.com/spineight/optional-task#readme)

#### `variant` — свой `std::variant`

> Интерфейс и гарантии — как у [`std::variant`](https://en.cppreference.com/w/cpp/utility/variant),
> кроме специализации `std::hash`. По аналогии с `optional`, максимально
> сохранять тривиальность special members и корректно расставлять `noexcept`.
>
> Отдельно про converting-конструктор/`operator=` — нужно повторить поведение
> из [P0608R3](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0608r3.html)
> (обработка неоднозначной конвертации к `bool`, из-за которой
> `variant<string, bool> x = "abc";` должен хранить `string`).

Источник: [spineight/variant-task](https://github.com/spineight/variant-task#readme)

### Дополнительная практика (для базовых тем, где нет готового ITMO-репозитория)

- [learncpp.com](https://www.learncpp.com/) — по каждой главе есть quiz/упражнения в конце,
  хорошо закрывает синтаксис, классы, шаблоны, память (темы 5–15 из таблицы ниже).
- [exercism.org C++ track](https://exercism.org/tracks/cpp) — короткие упражнения с менторской
  обратной связью, полезно для отработки идиом (RAII, move, шаблоны) в изоляции от большого проекта.

## Как устроена папка

```
study/cpp/
├── README.md         ← вы здесь (карта курса + практика)
├── weeks/            ← по одной заметке на тему/блок
└── solutions/         ← реализации задач из практики (код)
```

## Темы курса

Нумерация и файлы — как в [cpp-notes](https://cpp-kt.github.io/cpp-notes/course.html).
Первые темы (1–4) — это вводный блок по архитектуре/ОС, общий с АрхЭВМ, здесь не дублируется.

| № | Тема | Конспект | Практика |
|---|------|----------|----------|
| 5 | C/C++ синтаксис, типы данных | [04_syntax_types](https://cpp-kt.github.io/cpp-notes/04_syntax_types.html) | learncpp |
| 6 | Стадии компиляции | [05_compilation](https://cpp-kt.github.io/cpp-notes/05_compilation.html) | — |
| 7 | Классы, абстракция данных | [06_classes](https://cpp-kt.github.io/cpp-notes/06_classes.html) | learncpp |
| 8 | Наследование, виртуальные функции | [07_inheritance](https://cpp-kt.github.io/cpp-notes/07_inheritance.html) | learncpp |
| 9 | Исключения, exception safety, RAII | [08_exceptions](https://cpp-kt.github.io/cpp-notes/08_exceptions.html) | **socow-vector** |
| 10 | Аллокация памяти, оптимизации | [09_allocations_optimizations](https://cpp-kt.github.io/cpp-notes/09_allocations_optimizations.html) | **socow-vector** |
| 11 | Статические/динамические библиотеки | [10_libraries](https://cpp-kt.github.io/cpp-notes/10_libraries.html) | — |
| 12 | Undefined Behaviour | [11_undefined_behaviour](https://cpp-kt.github.io/cpp-notes/11_undefined_behaviour.html) | — |
| 13 | Методы валидации программ | [12_validation](https://cpp-kt.github.io/cpp-notes/12_validation.html) | — |
| 14 | Полезные инструменты | [13_tools](https://cpp-kt.github.io/cpp-notes/13_tools.html) | — |
| 15 | Шаблоны, tag-dispatching, SFINAE | [14_templates](https://cpp-kt.github.io/cpp-notes/14_templates.html) | learncpp / exercism |
| 16 | Обзор STL | [15_stl](https://cpp-kt.github.io/cpp-notes/15_stl.html) | — |
| 17 | Namespaces, using, ADL | [16_namespaces_using_adl](https://cpp-kt.github.io/cpp-notes/16_namespaces_using_adl.html) | — |
| 18 | Move-семантика, rvalue-ссылки | [17_move_rvalue](https://cpp-kt.github.io/cpp-notes/17_move_rvalue.html) | exercism |
| 19 | Intrusive-контейнеры | [18_intrusive_containers](https://cpp-kt.github.io/cpp-notes/18_intrusive_containers.html) | **intrusive-list** |
| 20 | Умные указатели | [19_smart_pointers](https://cpp-kt.github.io/cpp-notes/19_smart_pointers.html) | **shared-ptr** |
| 21 | Perfect forwarding, variadic templates | [20_perfect_forwarding](https://cpp-kt.github.io/cpp-notes/20_perfect_forwarding.html) | — |
| 22 | decltype, auto, nullptr | [21_decltype_auto_nullptr](https://cpp-kt.github.io/cpp-notes/21_decltype_auto_nullptr.html) | — |
| 23 | Лямбды, type erasure | [22_lambdas_type_erasure](https://cpp-kt.github.io/cpp-notes/22_lambdas_type_erasure.html) | **function** |
| 24 | Signals, реентерабельность, обработка ошибок | [23_signals_reetrancy_errors](https://cpp-kt.github.io/cpp-notes/23_signals_reetrancy_errors.html) | **signal** |
| 25 | optional/variant/tuple/string_view | [24_optional_variant_tuple_stringview](https://cpp-kt.github.io/cpp-notes/24_optional_variant_tuple_stringview.html) | **optional**, **variant** |
| 26 | Статическая/динамическая инициализация, constexpr | [25_constexpr](https://cpp-kt.github.io/cpp-notes/25_constexpr.html) | — |
| 27 | Многопоточность | [26_multithreading](https://cpp-kt.github.io/cpp-notes/26_multithreading.html) | — |
| 28 | Qt | [27_qt](https://cpp-kt.github.io/cpp-notes/27_qt.html) | — |
| 29 | Concepts | [28_concepts](https://cpp-kt.github.io/cpp-notes/28_concepts.html) | — |
| 30 | Ranges | [29_ranges](https://cpp-kt.github.io/cpp-notes/29_ranges.html) | — |
| 31 | Кодировки | [30_encoding](https://cpp-kt.github.io/cpp-notes/30_encoding.html) | — |
| 32 | Корутины | [31_coroutines](https://cpp-kt.github.io/cpp-notes/31_coroutines.html) | — |
| 33 | Модули | [32_modules](https://cpp-kt.github.io/cpp-notes/32_modules.html) | — |

## План обучения

- Идём по темам блоками (как в таблице), для каждого блока — конспект в `weeks/`.
- Как только в блоке появляется практика — решаем задачу, финальный код кладём в `solutions/<task-name>/`.
- Статус отмечается ниже.

## Статус

- [ ] Темы 5–8 (синтаксис, классы, наследование)
- [ ] Темы 9–10 + `socow-vector`
- [ ] Темы 11–15 (библиотеки, UB, шаблоны)
- [ ] Темы 16–18 (STL, ADL, move)
- [ ] Тема 19 + `intrusive-list`
- [ ] Тема 20 + `shared-ptr`
- [ ] Темы 21–23 + `function`
- [ ] Тема 24 + `signal`
- [ ] Тема 25 + `optional`/`variant`
- [ ] Темы 26–33 (продвинутое)
