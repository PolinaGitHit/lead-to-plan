---
module: task3-mediaplan
category: assignments
tags:
  - direct
  - mediaplan
  - ecco
  - ecom
last_updated: 2026-08-20
version_bumped: v0.0.4-dev
---

# Часть 3 — медиаплан ECCO Kids

**Назначение:** годовой медиаплан Яндекс Директа для интернет-магазина детской обуви ECCO (раздел «мальчики»): бюджет, типы кампаний, сезонность, воронка до покупки и ДРР.

## Итоговые deliverable

| Формат | Ссылка |
|--------|--------|
| Google Таблица (ответ проверяющему) | [Sheet части 3](https://docs.google.com/spreadsheets/d/1avkiFSoxmjjAMnEqFOZ1CMU7gRuVcHpLFhmjhtzD1Ys/edit?gid=92372183#gid=92372183) |
| Общий документ задания | [Google Doc](https://docs.google.com/document/d/1GUNXwGYl72GOBB9t5hKlBvcD70D8854MhfhNs9_6Ofw/edit?tab=t.0) |

## Исходная формулировка

[`task/task3.md`](../../task/task3.md)

## Краткое содержание результата

- **Бюджет:** 1 000 000 ₽/мес. без НДС, **12 млн ₽** за год
- **ГЕО:** РФ; **посадочная:** [ecco.ru/kids/boys](https://www.ecco.ru/kids/boys/)
- **Шесть типов кампаний** (ЕПК): бренд-поиск, небренд-поиск, DSA, ретаргетинг, LAL, медийная — с обоснованием долей
- **Итог года (из снимков):** **17 838 покупок**, сводный **ДРР 15,8 %**
- Сезонность детской обуви учтена в помесячном распределении

Бенчмарки CTR, CPC, CR — обоснованные допущения с указанием источника; статистика кабинета ECCO не выдумывалась.

## Google Sheet vs snapshots в репо

При закрытии задачи Google Таблица **не была полностью заполнена** (MCP needsAuth — нет доступа к редактированию из pipeline). **Авторитетная git-копия цифр** — markdown-снимки в `snapshots/`; operator-visible слой в Google Sheet может отличаться или быть частично пустым.

## Артефакты в репозитории

Корень задачи: [`agent_work/done/002-ecco-kids-direct-mediaplan/`](../../agent_work/done/002-ecco-kids-direct-mediaplan/)

| Путь | Назначение |
|------|------------|
| [`developer/mediaplan-canons.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/developer/mediaplan-canons.md) | Канон терминов, допущений, стратегий |
| [`developer/examiner-sheet-paste.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/developer/examiner-sheet-paste.md) | Paste для проверяющего |
| [`snapshots/sheet-assumptions.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/sheet-assumptions.md) | Лист «Параметры Плана» |
| [`snapshots/sheet-instruments.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/sheet-instruments.md) | Лист «Инструменты» |
| [`snapshots/sheet-mediaplan-year.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/sheet-mediaplan-year.md) | Лист «Медиаплан год» |
| [`snapshots/sheet-summary-month.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/sheet-summary-month.md) | Лист «Сводка месяц» |
| [`snapshots/sheet-summary-year.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/snapshots/sheet-summary-year.md) | Лист «Сводка год» |
| [`ecco-kids-direct-mediaplan_record.md`](../../agent_work/done/002-ecco-kids-direct-mediaplan/ecco-kids-direct-mediaplan_record.md) | Запись о закрытии задачи |

## Теги

[`direct`](../TAG_INDEX.md#direct) [`mediaplan`](../TAG_INDEX.md#mediaplan) [`ecco`](../TAG_INDEX.md#ecco) [`ecom`](../TAG_INDEX.md#ecom)
