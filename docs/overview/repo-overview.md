---
module: repo-overview
category: overview
tags:
  - direct
  - repo
last_updated: 2026-08-20
version_bumped: v0.0.5-dev
---

# Обзор репозитория для проверяющего

**Назначение:** как устроен репозиторий **От лида до медиаплана** (`lead-to-plan`) и где искать ответы по трём частям портфолио по Яндекс Директ.

## Что это за репозиторий

Приватное портфолио работ по контекстной рекламе (Яндекс Директ): B2B-кейс, аудит эффективности e-com, годовой медиаплан. Продуктового backend или веб-приложения здесь нет — только задания, расчёты, снимки таблиц и ссылки на Google Docs/Sheets.

Материалы подготовлены в рамках отбора специалиста по Яндекс Директ.

## Рекомендуемый маршрут проверки

1. Открыть **[README.md](../../README.md)** — таблица «часть → deliverable → артефакты»
2. Перейти по ссылке на **Google Doc или Sheet** нужной части
3. При необходимости сверить цифры с **`agent_work/done/`** (части 2–3) или **`task/`** (часть 1)

Подробная карта папок — в **[index.md](../../index.md)**.

## Зоны репозитория

| Зона | Роль |
|------|------|
| `task/` | Исходные формулировки заказчика — не переписывались при сдаче |
| `agent_work/done/` | Закрытые задачи: расчёты, paste, persona, markdown-снимки листов |
| `agent_work/tasks/`, `inbox/` | Процесс работы (TZ, qa, промпты) — для прозрачности, не обязательны для проверки |
| `docs/` | Навигация: INDEX, TAG_INDEX, страницы по частям |
| `tests/` | Регрессионные pytest-проверки согласованности медиаплана (часть 3) |
| `.cursor/` | Конфигурация IDE и agent pipeline — не часть ответа на задание |

## Три части — одна строка каждая

| Часть | Deliverable | Git-артефакты |
|-------|-------------|---------------|
| Кейс B2B | [Google Doc](https://docs.google.com/document/d/15305Tsn8MqypVOmnAHCASRaxYbydpezJVsMm4jCJf8U/edit?tab=t.0) | `task/task1.md` |
| 2 Эффективность | [Google Sheet](https://docs.google.com/spreadsheets/d/1H0179SIX8_3z46P9edR7zxJvy057jZl1Eu6NEBoqZv0/edit?usp=sharing) | `agent_work/done/001-direct-test-part2-efficiency/` |
| 3 Медиаплан ECCO | [Google Sheet](https://docs.google.com/spreadsheets/d/1A31rkQ9JkJ3Bet8coGxcXw22bwFhqq4Xk7_GQxtdc8c/edit?gid=0#gid=0) | `agent_work/done/002-ecco-kids-direct-mediaplan/` |

## Важные оговорки

- **Кейс B2B:** итог только во внешнем Google Doc; в репо — текст кейса.
- **Часть 2:** ячейки B3/B6 в Google Sheet могли обновляться оператором вне git; paste в репо — эталон формулировок.
- **Часть 3:** Google Sheet может быть частично не заполнен; **snapshots/** в репо — авторитетная копия цифр.

## Теги

[`direct`](../TAG_INDEX.md#direct) [`repo`](../TAG_INDEX.md#repo)
