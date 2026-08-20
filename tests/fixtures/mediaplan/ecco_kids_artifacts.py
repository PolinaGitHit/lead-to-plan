"""Парсинг и константы артефактов ECCO Kids mediaplan для автотестов MC-1…MC-5."""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

SEARCH_LINES: dict[str, dict[str, Any]] = {
    "brand": {
        "label": "бренд ECCO",
        "ctr": 10.0,
        "cpc": 28,
        "cr": 6.5,
    },
    "nonbrand": {
        "label": "небренд (фразы)",
        "ctr": 4.5,
        "cpc": 48,
        "cr": 3.8,
    },
    "gallery": {
        "label": "товарная галерея",
        "ctr": 7.0,
        "cpc": 44,
        "cr": 4.5,
    },
}

RSY_BENCH: dict[str, float] = {
    "ctr": 0.8,
    "cpc": 11.0,
    "cr_warm": 2.5,
    "cr_cold": 1.5,
}

OLD_SEARCH_BENCH: tuple[float, float, float] = (6.0, 45.0, 4.5)
PRIMARY_TZ_SEARCH_BENCH: dict[str, tuple[float, float, float]] = {
    "brand": (10.0, 28.0, 7.0),
    "gallery": (7.0, 40.0, 5.0),
}
AOV: int = 4250
YEAR_BUDGET: int = 12_000_000
YEAR_SPEND: int = 11_999_968
YEAR_REVENUE: int = 79_538_750
YEAR_DRR: float = 15.1
DRR_YEAR_MIN: float = 15.0
DRR_YEAR_MAX: float = 25.0
DRR_SEARCH_MAX: float = 30.0
BUDGET_TOLERANCE_RUB: float = 1.0

SHEET_FILES: dict[str, str] = {
    "assumptions": "sheet-assumptions.md",
    "instruments": "sheet-instruments.md",
    "mediaplan_year": "sheet-mediaplan-year.md",
    "summary_month": "sheet-summary-month.md",
    "summary_year": "sheet-summary-year.md",
}

PASTE_SECTION_MARKERS: dict[str, str] = {
    "assumptions": '## Лист «Допущения»',
    "instruments": '## Лист «Инструменты»',
    "mediaplan_year": '## Лист «Медиаплан год»',
    "summary_month": '## Лист «Сводка месяц»',
    "summary_year": '## Лист «Сводка год»',
}


@dataclass(frozen=True)
class MediaplanRow:
    """Одна строка годовой сетки медиаплана."""

    month: str
    campaign: str
    strategy: str
    budget: float
    impressions: int
    ctr: float
    clicks: int
    cpc: float
    spend: float
    cr: float
    purchases: int
    aov: float
    revenue: float
    cpa: float
    drr: float
    search_kind: str | None
    rsy_kind: str | None


def mediaplan_root(repo_root: Path) -> Path:
    """Путь к каталогу done-задачи ECCO Kids mediaplan.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Путь к ``agent_work/done/002-ecco-kids-direct-mediaplan``.
    """
    return repo_root / "agent_work/done/002-ecco-kids-direct-mediaplan"


def snapshots_dir(repo_root: Path) -> Path:
    """Каталог snapshot-файлов медиаплана.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Путь к ``snapshots/`` внутри mediaplan-задачи.
    """
    return mediaplan_root(repo_root) / "snapshots"


def developer_dir(repo_root: Path) -> Path:
    """Каталог developer-артефактов медиаплана.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Путь к ``developer/`` внутри mediaplan-задачи.
    """
    return mediaplan_root(repo_root) / "developer"


def read_text(path: Path) -> str:
    """Прочитать UTF-8 текст из файла.

    Args:
        path: Путь к файлу.

    Returns:
        Содержимое файла.

    Raises:
        FileNotFoundError: Если файл отсутствует.
    """
    return path.read_text(encoding="utf-8")


def parse_ru_number(value: str) -> float:
    """Разобрать число в русском формате (пробелы, запятая).

    Args:
        value: Строковое представление числа.

    Returns:
        Числовое значение.
    """
    cleaned = value.strip().replace("\u00a0", " ").replace(" ", "").replace(",", ".")
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)
    if not cleaned or cleaned == "-":
        return 0.0
    return float(cleaned)


def parse_markdown_table_rows(text: str) -> list[list[str]]:
    """Извлечь строки markdown-таблицы.

    Args:
        text: Markdown-текст.

    Returns:
        Список строк таблицы (каждая — список ячеек).
    """
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\|\s*[-:]+", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def classify_search_line(campaign: str) -> str | None:
    """Классифицировать поисковую линию по названию кампании.

    Args:
        campaign: Название кампании.

    Returns:
        Ключ ``brand`` / ``nonbrand`` / ``gallery`` или ``None``.
    """
    lowered = campaign.lower()
    if "бренд ecco" in lowered:
        return "brand"
    if "небренд" in lowered and "фраз" in lowered:
        return "nonbrand"
    if "товарная галерея" in lowered or "галерея" in lowered:
        return "gallery"
    return None


def classify_rsy_line(campaign: str) -> str | None:
    """Классифицировать линию РСЯ по названию кампании.

    Args:
        campaign: Название кампании.

    Returns:
        ``warm``, ``cold`` или ``None``.
    """
    lowered = campaign.lower()
    if "рся" not in lowered:
        return None
    if "автотаргетинг" in lowered:
        return "cold"
    return "warm"


def load_mediaplan_rows(repo_root: Path) -> list[MediaplanRow]:
    """Загрузить строки годовой сетки из snapshot markdown.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Список строк медиаплана.
    """
    path = snapshots_dir(repo_root) / SHEET_FILES["mediaplan_year"]
    text = read_text(path)
    table_rows = parse_markdown_table_rows(text)
    if not table_rows:
        return []

    header = [cell.lower() for cell in table_rows[0]]
    index = {name: header.index(name) for name in header}

    def col(row: list[str], key: str) -> str:
        position = index.get(key)
        if position is None or position >= len(row):
            return ""
        return row[position]

    records: list[MediaplanRow] = []
    current_month = ""
    for row in table_rows[1:]:
        month_cell = col(row, "месяц")
        if month_cell:
            current_month = month_cell
        campaign = col(row, "кампания")
        if not campaign:
            continue
        records.append(
            MediaplanRow(
                month=current_month,
                campaign=campaign,
                strategy=col(row, "стратегия"),
                budget=parse_ru_number(col(row, "бюджет, ₽")),
                impressions=int(round(parse_ru_number(col(row, "показы")))),
                ctr=parse_ru_number(col(row, "ctr, %")),
                clicks=int(round(parse_ru_number(col(row, "клики")))),
                cpc=parse_ru_number(col(row, "cpc, ₽")),
                spend=parse_ru_number(col(row, "расход, ₽")),
                cr=parse_ru_number(col(row, "cr покупка, %")),
                purchases=int(round(parse_ru_number(col(row, "покупки")))),
                aov=parse_ru_number(col(row, "aov, ₽")),
                revenue=parse_ru_number(col(row, "выручка, ₽")),
                cpa=parse_ru_number(col(row, "cpa, ₽")),
                drr=parse_ru_number(col(row, "дрр, %")),
                search_kind=classify_search_line(campaign),
                rsy_kind=classify_rsy_line(campaign),
            )
        )
    return records


def group_rows_by_month(rows: list[MediaplanRow]) -> dict[str, list[MediaplanRow]]:
    """Сгруппировать строки медиаплана по месяцу.

    Args:
        rows: Строки сетки.

    Returns:
        Словарь месяц → строки.
    """
    grouped: dict[str, list[MediaplanRow]] = {}
    for row in rows:
        grouped.setdefault(row.month, []).append(row)
    return grouped


def expected_funnel_from_budget(
    budget: float,
    ctr: float,
    cpc: float,
    cr: float,
    aov: float = float(AOV),
) -> dict[str, float | int]:
    """Рассчитать ожидаемую воронку при фиксированном бюджете строки.

    Args:
        budget: Бюджет строки без НДС.
        ctr: CTR в процентах.
        cpc: CPC в рублях.
        cr: CR в процентах.
        aov: Средний чек.

    Returns:
        Словарь производных метрик с округлением как в snapshots.
    """
    clicks = int(round(budget / cpc))
    impressions = int(round(clicks / (ctr / 100.0))) if ctr else 0
    spend = round(clicks * cpc)
    purchases = int(round(clicks * (cr / 100.0)))
    revenue = round(purchases * aov)
    drr = round((spend / revenue) * 100.0, 1) if revenue else 0.0
    return {
        "clicks": clicks,
        "impressions": impressions,
        "spend": spend,
        "purchases": purchases,
        "revenue": revenue,
        "drr": drr,
    }


def search_triples_distinct() -> bool:
    """Проверить, что три целевых Search-бенча попарно различны.

    Returns:
        ``True``, если все три тройки CTR/CPC/CR различаются.
    """
    triples = {
        (spec["ctr"], spec["cpc"], spec["cr"]) for spec in SEARCH_LINES.values()
    }
    return len(triples) == 3


def extract_paste_tsv_block(paste_text: str, section_marker: str) -> str:
    """Извлечь TSV-блок из paste markdown по заголовку секции.

    Args:
        paste_text: Содержимое ``examiner-sheet-paste.md``.
        section_marker: Заголовок секции (например ``## Лист «Допущения»``).

    Returns:
        TSV-текст без обрамляющих ``` или пустая строка.
    """
    start = paste_text.find(section_marker)
    if start < 0:
        return ""
    fence_start = paste_text.find("```", start)
    if fence_start < 0:
        return ""
    content_start = paste_text.find("\n", fence_start) + 1
    fence_end = paste_text.find("```", content_start)
    if fence_end < 0:
        return ""
    return paste_text[content_start:fence_end].strip("\n")


def _xlsx_col_to_index(cell_ref: str) -> int:
    """Преобразовать ссылку на ячейку Excel в индекс столбца (0-based).

    Args:
        cell_ref: Ссылка вида ``AB12``.

    Returns:
        Индекс столбца.
    """
    letters = "".join(char for char in cell_ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index - 1


def _xlsx_row_number(cell_ref: str) -> int:
    """Извлечь номер строки из ссылки на ячейку.

    Args:
        cell_ref: Ссылка вида ``AB12``.

    Returns:
        Номер строки (1-based).
    """
    digits = "".join(char for char in cell_ref if char.isdigit())
    return int(digits) if digits else 0


def read_xlsx_sheet_names(xlsx_path: Path) -> list[str]:
    """Прочитать имена вкладок из ``xl/workbook.xml`` без внешних зависимостей.

    Args:
        xlsx_path: Путь к ``.xlsx``.

    Returns:
        Список имён листов в порядке workbook.

    Raises:
        FileNotFoundError: Если файл отсутствует.
    """
    if not xlsx_path.is_file():
        raise FileNotFoundError(xlsx_path)

    with zipfile.ZipFile(xlsx_path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets_elem = workbook.find("m:sheets", NS)
        if sheets_elem is None:
            return []
        return [
            sheet.attrib.get("name", "")
            for sheet in sheets_elem.findall("m:sheet", NS)
        ]


def assumptions_claims_bench_source_on_year_grid(assumptions_text: str) -> bool:
    """Проверить, что допущения ложно утверждают столбец «источник бенча» на сетке года.

    Исправительные формулировки («не выводится», «нет столбца») не считаются ложным
    утверждением. Проверка ограничена одной строкой — без DOTALL-склейки через файл.

    Args:
        assumptions_text: Текст ``sheet-assumptions.md``.

    Returns:
        ``True``, если найдено положительное утверждение о столбце на «Медиаплан год».
    """
    negation = re.compile(
        r"нет\s+столбца|не\s+(?:выводится|показывается|отображается)|отсутствует",
        re.IGNORECASE,
    )

    for line in assumptions_text.splitlines():
        lowered = line.lower()
        if (
            "медиаплан" in lowered
            and "год" in lowered
            and "столбец" in lowered
            and "источник бенча" in lowered
        ):
            if negation.search(lowered):
                continue
            return True
    return False


def read_xlsx_sheet_rows(xlsx_path: Path, sheet_name: str) -> list[list[str]]:
    """Прочитать лист xlsx без внешних зависимостей (stdlib zip+xml).

    Args:
        xlsx_path: Путь к ``.xlsx``.
        sheet_name: Имя вкладки.

    Returns:
        Строки листа как списки строковых значений ячеек.

    Raises:
        FileNotFoundError: Если файл отсутствует.
        ValueError: Если лист не найден.
    """
    if not xlsx_path.is_file():
        raise FileNotFoundError(xlsx_path)

    with zipfile.ZipFile(xlsx_path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find("m:sheets", NS)
        if sheets is None:
            raise ValueError("workbook has no sheets")

        target_rid = ""
        for sheet in sheets.findall("m:sheet", NS):
            if sheet.attrib.get("name") == sheet_name:
                target_rid = sheet.attrib[
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                ]
                break
        if not target_rid:
            raise ValueError(f"sheet not found: {sheet_name}")

        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target_path = ""
        for rel in rels:
            if rel.attrib.get("Id") == target_rid:
                target_path = "xl/" + rel.attrib["Target"].lstrip("/")
                break
        if not target_path:
            raise ValueError(f"relationship not found for sheet: {sheet_name}")

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            sst = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in sst.findall("m:si", NS):
                text_parts = [node.text or "" for node in item.findall(".//m:t", NS)]
                shared_strings.append("".join(text_parts))

        sheet_xml = ET.fromstring(archive.read(target_path))
        row_map: dict[int, dict[int, str]] = {}
        max_col = 0
        for row in sheet_xml.findall("m:sheetData/m:row", NS):
            row_number = int(row.attrib.get("r", "0"))
            row_map[row_number] = {}
            for cell in row.findall("m:c", NS):
                ref = cell.attrib.get("r", "")
                col_index = _xlsx_col_to_index(ref)
                max_col = max(max_col, col_index)
                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", NS)
                inline = cell.find("m:is/m:t", NS)
                if cell_type == "s" and value_node is not None:
                    value = shared_strings[int(value_node.text)]
                elif inline is not None:
                    value = inline.text or ""
                elif value_node is not None:
                    value = value_node.text or ""
                else:
                    value = ""
                row_map[row_number][col_index] = value

        if not row_map:
            return []

        result: list[list[str]] = []
        for row_number in sorted(row_map):
            row_cells = row_map[row_number]
            result.append(
                [row_cells.get(col_index, "") for col_index in range(max_col + 1)]
            )
        return result


def parse_year_drr(summary_year_text: str) -> float | None:
    """Извлечь сводный ДРР года из snapshot summary-year.

    Args:
        summary_year_text: Текст ``sheet-summary-year.md``.

    Returns:
        Значение ДРР в процентах или ``None``.
    """
    lowered = summary_year_text.lower()
    match = re.search(
        r"сводный\s+дрр[^\d]*(\d+[,.]\d+)",
        lowered,
    ) or re.search(r"дрр[^\d]*(\d+[,.]\d+)\s*%", lowered)
    if not match:
        return None
    return parse_ru_number(match.group(1))


def parse_summary_year_metric(summary_year_text: str, label: str) -> float | None:
    """Извлечь числовую метрику из блока «Общий итог» summary-year.

    Args:
        summary_year_text: Текст ``sheet-summary-year.md``.
        label: Подпись строки (например ``расход без ндс`` или ``выручка``).

    Returns:
        Числовое значение или ``None``.
    """
    pattern = re.compile(
        rf"\|\s*\*?\*?{re.escape(label)}\*?\*?\s*\|\s*([\d\s]+)",
        re.IGNORECASE,
    )
    match = pattern.search(summary_year_text)
    if not match:
        return None
    return parse_ru_number(match.group(1))
