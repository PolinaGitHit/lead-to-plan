# От лида до медиаплана

Портфолио работ по контекстной рекламе (Яндекс Директ): B2B-кейс, аудит эффективности e-com, годовой медиаплан. Здесь собраны исходные формулировки заданий, расчёты и снимки таблиц в git, а также ссылки на итоговые Google Docs и Google Sheets для проверяющего.

## Три части портфолио

| Часть | Тема | Итоговый deliverable | Артефакты в репозитории |
|-------|------|----------------------|-------------------------|
| **1** | Кейс B2B (котельные, дымовые трубы) | [Отчёт в Google Doc](https://docs.google.com/document/d/15305Tsn8MqypVOmnAHCASRaxYbydpezJVsMm4jCJf8U/edit?tab=t.0) | [`task/task1.md`](task/task1.md) — текст кейса |
| **2** | Эффективность рекламных кампаний (e-com) | [Google Таблица части 2](https://docs.google.com/spreadsheets/d/1H0179SIX8_3z46P9edR7zxJvy057jZl1Eu6NEBoqZv0/edit?usp=sharing) | [`agent_work/done/001-direct-test-part2-efficiency/`](agent_work/done/001-direct-test-part2-efficiency/) — расчёты, paste, письмо |
| **3** | Медиаплан ECCO Kids на 12 месяцев | [Google Таблица части 3](https://docs.google.com/spreadsheets/d/1A31rkQ9JkJ3Bet8coGxcXw22bwFhqq4Xk7_GQxtdc8c/edit?gid=0#gid=0) | [`agent_work/done/002-ecco-kids-direct-mediaplan/`](agent_work/done/002-ecco-kids-direct-mediaplan/) — канон, снимки листов |

Общий документ с формулировками частей 2–3: [Google Doc](https://docs.google.com/document/d/1GUNXwGYl72GOBB9t5hKlBvcD70D8854MhfhNs9_6Ofw/edit?tab=t.0).

## Быстрая навигация

- **[Карта проекта](index.md)** — дерево папок и поток «задание → артефакты → внешний deliverable»
- **[Документация](docs/README.md)** — указатели по категориям и тегам, страницы по каждой части
- **[История изменений](AGENT_CHANGELOG.md)** — версия и журнал правок

## Кратко по результатам

**Кейс B2B.** Реструктуризация пяти B2B-кабинетов: стабильный поток лидов через 1,5 месяца; за 2 месяца после запуска — 210 лидов/мес. (160 квалиф.), CPQL с 12 500 до 6 000 ₽. Подробности — в отчёте и [`task/task1.md`](task/task1.md).

**Часть 2.** Слабое условие — «Новая аудитория» в медийной кампании на сетях; одно действие — снижение ставки за 1000 показов. Расчёты и сравнительные таблицы — в [`snapshots/`](agent_work/done/001-direct-test-part2-efficiency/snapshots/).

**Часть 3.** Годовой медиаплан ECCO Kids: 12 млн ₽ без НДС, шесть типов кампаний, сезонность детской обуви. Авторитетная git-копия цифр — в [`snapshots/`](agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/); Google Sheet может быть заполнен частично.

## Структура репозитория (кратко)

```
task/              — исходные формулировки заданий (task1.md … task3.md)
agent_work/done/   — закрытые задачи: расчёты, paste, снимки таблиц
agent_work/        — процесс работы (tasks, inbox)
docs/              — документация для проверяющего
tests/             — регрессионные проверки медиаплана (pytest)
```

Папка `agent_work/` сохранена целиком — виден процесс подготовки ответов; для проверки достаточно README, `docs/` и ссылок на Google.

Материалы подготовлены в рамках отбора специалиста по Яндекс Директ.
