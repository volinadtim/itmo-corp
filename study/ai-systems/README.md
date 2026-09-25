# Системы искусственного интеллекта (СИИ)

3 курс, 5 семестр, 2026/2027. 8 лекций, 16 практик.

## Организация

| | |
|---|---|
| Преподаватель | **Запорожцев Иван Федорович**, к.т.н., zaporozhtsev.if.work@gmail.com |
| Чат | Telegram «ИТМО СИИ 2…» (форум, 54 участника) |

Ветки чата:
- **Ветка преподавателя** — лекции, задания ЛР, доп. материалы (только Запорожцев)
- **Защиты ЛР** — запись на защиту
- **Оргвопросы** — пары на ЛР1 и датасеты (чтобы не было повторов)
- **General**

## Материалы ([materials/tg/](materials/tg/))

Из «Ветки преподавателя», выложено 13.09.2026:

| Файл | Что |
|---|---|
| [Лекция 1. Введение.pdf](materials/tg/Лекция%201.%20Введение.pdf) | ИИ/ML/DL, основные понятия, loss vs metrics, pipeline, «Норникель», EDA |
| [Лекция 2.pdf](materials/tg/Лекция%202.pdf) | Линейная регрессия (слайды в основном картинками) |
| [Lab1.ipynb](materials/tg/Lab1.ipynb) | Шаблон ЛР1 — решать в нём, текстовые ячейки не удалять |
| [sem01-pandas.ipynb](materials/tg/sem01-pandas.ipynb) | Семинар 1: pandas |
| [sem02-sklearn-linregr.ipynb](materials/tg/sem02-sklearn-linregr.ipynb) | Семинар 2: sklearn, линейная регрессия |
| [продукт/](materials/tg/продукт/) | Пример продуктивизации: модель (LogisticRegression на ирисах) → CLI `run.py` |
| babushkin_v_kravchenko_…pdf | Бабушкин, Кравченко — *ML System Design* (30 МБ, в git не коммитится) |

Не скачано:
- видео к заданию 3 ЛР1 (инновации «Норильского никеля», 3:18, 243 МБ) — есть только в чате.

Ссылки:
- [ODS Питер](https://t.me/+XDdzFxXKVAs1Mjdi) — Telegram
- [Сергей Николенко, плейлисты](https://www.youtube.com/@snikolenko/playlists) — темы «Глубокое обучение», для тех,
  кто хочет в нейросети раньше 4 курса
- Из лекции 1: [блог Дьяконова](https://alexanderdyakonov.wordpress.com/)

## Формат сдачи (все ЛР)

- Решение — в шаблоне ноутбука; можно добавлять ячейки, нельзя удалять ячейки с формулировками.
- Ответ без кода = 0 баллов. Выводы — письменно в ноутбуке (markdown/latex), без выводов не на полный балл.
- **Устная защита обязательна**: не защитил — баллов нет вовсе. Вопросы по лекциям и практике, список не публикуется.

## ЛР1. Pandas, EDA, линейная регрессия — 8 + 5 бонусных

Работа в парах (или тройках). Пару и датасет записать в «Оргвопросы».

**Задание 1 (4 б.)** — датасет для регрессии с Kaggle или UCI: **поновее**, ≥ 100 объектов.
EDA + вопросы к данным, по 0,5 б. за каждый инструмент:
groupby · resample · merge/join/concat · seaborn · plotly (интерактив) ·
распределения (гистограмма отн. частот, kde, boxplot, violin, scatter) ·
тесты на свойства распределения (нормальность) · One-Hot Encoding.

**Задание 2 (4 б.)**
1. Таргет + регрессоры, обоснование из предметной области с кодом и графиками (1 б.).
   ⚠️ Тест отделить **до** EDA — иначе data leakage.
2. Линейная регрессия без регуляризации, RMSE / MAE / R² (1 б.).
3. С регуляризацией: удаление выбросов + нормирование в `sklearn.Pipeline`, обосновать выбор методов (2 б.).

**Задание 3 (бонус 2 б.)** — по лекции 1 и видео про «Норникель»: какие задачи моделирования
и управления, какие разделы ИИ, какие физико-химические признаки; для нескольких признаков —
тип, дискретность по времени/пространству, сырой/агрегат, шум, пропуски, распределение, риск утечки.

**Задание 4 (бонус 3 б.)** — вывести, что максимум правдоподобия при нормальных невязках ⇔ минимум MSE.
2 б. за вывод, +1 б. если формулы в ячейке ноутбука, а не на бумаге.

### Мой датасет

Пара и датасет пока не записаны.

### Занятые датасеты (Оргвопросы, на 25.09.2026)

Преподаватель: старые датасеты — плохо, по ним слишком много кода в сети (так он ответил на RecGym).

| Команда | Датасет |
|---|---|
| Лукина, Антонова | [Retail Store Inventory Forecasting](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) |
| Маренников, Хабиров, Русанов | [All rockets from 1957](https://www.kaggle.com/datasets/akhilram7/allrocketsfrom1957) |
| Соловьёв, Косов, Журавлёв | [Intel & AMD Processors Full Specs](https://www.kaggle.com/datasets/alanjo/amd-processor-specifications) |
| Гулахмадзода, Рахаман, Оладое | [Bitcoin prices](https://www.kaggle.com/datasets/amineipad/bitcoin-prices-dataset) |
| Свечников, Баукин | [Aerial Bombing Operations in WWII](https://www.kaggle.com/datasets/usaf/world-war-ii/data) |
| Мохамед, Юксель | [Formula 1 World Championship 1950–2024](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) |
| Горшенин, Гребенюк | [RecGym (UCI)](https://archive.ics.uci.edu/dataset/1128/recgym:+gym+workouts+recognition+dataset+with+imu+and+capacitive+sensor-7) — преподаватель: «очень старый» |
| Корхонен, Хоменков | [London bike sharing](https://www.kaggle.com/datasets/juhyemi/london-bike-sharing-dataset) |
| Дядев, Родионов, Тенькаев | [Wine price vs blind quality](https://www.kaggle.com/datasets/sergionefedov/wine-price-vs-blind-qualitydo-you-pay-for-taste) |
| Разгоняев, Валиев, Новиков | [Basketball (NBA)](https://www.kaggle.com/datasets/wyattowalsh/basketball) |
| Сыщиков, Кириченко | [Retail sales](https://www.kaggle.com/datasets/danielsowah123/retail-sales-dataset) |
| Старченко, Ожеховский, Турыгин | [Volve production data](https://www.kaggle.com/datasets/lamyalbert/volve-production-data) |
| Хоанг, Тарнопольский | [Steam games (daily updates)](https://www.kaggle.com/datasets/hubertsidorowicz/steam-games-dataset-daily-updates) |
| Пивоваров | [BoardGameGeek games](https://www.kaggle.com/datasets/caesuric/bgggamesdata/data) |
| Бущик Гузалов | [US police shootings](https://www.kaggle.com/datasets/ahsen1330/us-police-shootings) |
| Лабин | [Student performance (UCI)](https://archive.ics.uci.edu/dataset/320/student+performance) |
