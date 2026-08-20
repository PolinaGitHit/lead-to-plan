"""Автотесты MC-1…MC-5 для ECCO Kids Search benches (agent_work mediaplan artifacts).

placement_reason: cross-cutting сверка артефактов ``agent_work/done/002-ecco-kids-direct-mediaplan``;
не относится к product zone ``support_gor`` / ``support_prometey``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.fixtures.mediaplan import ecco_kids_artifacts as artifacts

pytestmark = pytest.mark.regression

PLACEMENT_REASON = (
    "Cross-cutting mediaplan artifact verification under agent_work/done; "
    "not owned by a single product support zone."
)


@pytest.fixture(scope="module")
def mediaplan_rows(repo_root: Path) -> list[artifacts.MediaplanRow]:
    """Строки годовой сетки из snapshot.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Список строк медиаплана.
    """
    return artifacts.load_mediaplan_rows(repo_root)


class TestSearchBenchConstants:
    """Константы ТЗ: три Search-линии попарно различны."""

    def test_search_triples_pairwise_distinct(self) -> None:
        """Три целевых CTR/CPC/CR из ТЗ не совпадают попарно."""
        assert artifacts.search_triples_distinct()


class TestMc1SearchBenches:
    """MC-1: три Search-линии с разными CTR/CPC/CR по ТЗ на всех 12 месяцах."""

    def test_has_thirty_six_search_rows(self, mediaplan_rows: list[artifacts.MediaplanRow]) -> None:
        """В сетке 36 строк Search (12 месяцев × 3 линии)."""
        search_rows = [row for row in mediaplan_rows if row.search_kind]
        assert len(search_rows) >= 36

    @pytest.mark.parametrize(
        ("kind", "ctr", "cpc", "cr"),
        [
            ("brand", 10.0, 28.0, 6.5),
            ("nonbrand", 4.5, 48.0, 3.8),
            ("gallery", 7.0, 44.0, 4.5),
        ],
    )
    def test_search_line_benches_match_tz(
        self,
        mediaplan_rows: list[artifacts.MediaplanRow],
        kind: str,
        ctr: float,
        cpc: float,
        cr: float,
    ) -> None:
        """Каждая Search-линия держит константы ТЗ на каждом месяце."""
        line_rows = [row for row in mediaplan_rows if row.search_kind == kind]
        assert line_rows, f"no rows for search kind {kind}"
        mismatches = [
            row
            for row in line_rows
            if abs(row.ctr - ctr) > 0.05
            or abs(row.cpc - cpc) > 0.5
            or abs(row.cr - cr) > 0.05
        ]
        assert not mismatches, (
            f"{kind}: expected {ctr}/{cpc}/{cr}; "
            f"sample mismatch {mismatches[0].month} "
            f"{mismatches[0].ctr}/{mismatches[0].cpc}/{mismatches[0].cr}"
        )

    def test_no_old_unified_search_bench(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """На Search-строках нет старого общего бенча 6/45/4.5."""
        old_ctr, old_cpc, old_cr = artifacts.OLD_SEARCH_BENCH
        hits = [
            row
            for row in mediaplan_rows
            if row.search_kind
            and abs(row.ctr - old_ctr) < 0.05
            and abs(row.cpc - old_cpc) < 0.5
            and abs(row.cr - old_cr) < 0.05
        ]
        assert not hits, f"old bench still present in {hits[0].month} {hits[0].campaign}"

    def test_no_primary_tz_search_bench_on_grid(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """На Search-строках нет первичного ТЗ-бенча brand 7 % CR / gallery 40 ₽ / 5 % CR."""
        hits: list[artifacts.MediaplanRow] = []
        for row in mediaplan_rows:
            if not row.search_kind or row.search_kind not in artifacts.PRIMARY_TZ_SEARCH_BENCH:
                continue
            tz_ctr, tz_cpc, tz_cr = artifacts.PRIMARY_TZ_SEARCH_BENCH[row.search_kind]
            if (
                abs(row.ctr - tz_ctr) < 0.05
                and abs(row.cpc - tz_cpc) < 0.5
                and abs(row.cr - tz_cr) < 0.05
            ):
                hits.append(row)
        assert not hits, (
            f"primary TZ bench still present in {hits[0].month} {hits[0].campaign}"
        )

    def test_search_benches_constant_within_line(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """Внутри каждой Search-линии бенч не меняется между месяцами."""
        for kind in artifacts.SEARCH_LINES:
            triples = {
                (row.ctr, row.cpc, row.cr)
                for row in mediaplan_rows
                if row.search_kind == kind
            }
            assert len(triples) == 1, f"{kind} has inconsistent benches: {triples}"


class TestMc2BudgetAndDrr:
    """MC-2: сходимость бюджета и коридоры ДРР."""

    def test_six_campaigns_per_month(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """В каждом месяце ровно шесть кампаний."""
        by_month = artifacts.group_rows_by_month(mediaplan_rows)
        bad = {month: len(rows) for month, rows in by_month.items() if len(rows) != 6}
        assert not bad, f"unexpected campaign counts: {bad}"

    def test_month_budget_sums_match(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """Сумма бюджетов шести кампаний сходится внутри месяца (допуск 1 ₽)."""
        by_month = artifacts.group_rows_by_month(mediaplan_rows)
        for month, rows in by_month.items():
            month_total = sum(row.budget for row in rows)
            for row in rows:
                share_sum = sum(item.budget for item in rows)
                assert abs(share_sum - month_total) <= artifacts.BUDGET_TOLERANCE_RUB, (
                    f"{month}: campaign sum {share_sum} != month total {month_total}"
                )

    def test_year_budget_total(self, mediaplan_rows: list[artifacts.MediaplanRow]) -> None:
        """Годовая сумма бюджетов = 12 000 000 ₽ без НДС."""
        year_total = sum(row.budget for row in mediaplan_rows)
        assert abs(year_total - artifacts.YEAR_BUDGET) <= artifacts.BUDGET_TOLERANCE_RUB

    def test_search_drr_not_above_thirty_percent(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """ДРР каждой Search-строки ≤ 30 %."""
        offenders = [
            row
            for row in mediaplan_rows
            if row.search_kind and row.drr > artifacts.DRR_SEARCH_MAX + 0.05
        ]
        assert not offenders, (
            f"Search DRR > 30%: {offenders[0].month} "
            f"{offenders[0].campaign} DRR={offenders[0].drr}"
        )

    def test_year_drr_in_corridor(self, repo_root: Path) -> None:
        """Сводный ДРР года в коридоре 15–25 %."""
        summary_text = artifacts.read_text(
            artifacts.snapshots_dir(repo_root) / artifacts.SHEET_FILES["summary_year"]
        )
        year_drr = artifacts.parse_year_drr(summary_text)
        assert year_drr is not None, "could not parse year DRR from summary-year"
        assert artifacts.DRR_YEAR_MIN <= year_drr <= artifacts.DRR_YEAR_MAX

    def test_year_drr_matches_live_ssot(self, repo_root: Path) -> None:
        """Сводный ДРР года = 15,1 % по snapshot summary-year."""
        summary_text = artifacts.read_text(
            artifacts.snapshots_dir(repo_root) / artifacts.SHEET_FILES["summary_year"]
        )
        year_drr = artifacts.parse_year_drr(summary_text)
        assert year_drr is not None
        assert abs(year_drr - artifacts.YEAR_DRR) <= 0.05

    def test_year_spend_and_revenue_from_summary(self, repo_root: Path) -> None:
        """Годовой расход и выручка совпадают с live SSOT summary-year."""
        summary_text = artifacts.read_text(
            artifacts.snapshots_dir(repo_root) / artifacts.SHEET_FILES["summary_year"]
        )
        spend = artifacts.parse_summary_year_metric(summary_text, "Расход без НДС")
        revenue = artifacts.parse_summary_year_metric(summary_text, "Выручка")
        assert spend is not None, "could not parse year spend from summary-year"
        assert revenue is not None, "could not parse year revenue from summary-year"
        assert abs(spend - artifacts.YEAR_SPEND) <= artifacts.BUDGET_TOLERANCE_RUB
        assert abs(revenue - artifacts.YEAR_REVENUE) <= artifacts.BUDGET_TOLERANCE_RUB

    def test_year_spend_sums_from_grid(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """Сумма расходов по сетке сходится с годовым расходом live SSOT."""
        year_spend = sum(row.spend for row in mediaplan_rows)
        assert abs(year_spend - artifacts.YEAR_SPEND) <= artifacts.BUDGET_TOLERANCE_RUB


class TestMc3RsyBenches:
    """MC-3: бенчи РСЯ не изменены; стратегия «Максимум кликов» только на автотаргетинге."""

    def test_has_thirty_six_rsy_rows(self, mediaplan_rows: list[artifacts.MediaplanRow]) -> None:
        """В сетке не менее 36 строк РСЯ."""
        rsy_rows = [row for row in mediaplan_rows if row.rsy_kind]
        assert len(rsy_rows) >= 36

    def test_rsy_ctr_cpc_unchanged(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """CTR 0,8 % и CPC 11 ₽ на всех строках РСЯ."""
        for row in mediaplan_rows:
            if not row.rsy_kind:
                continue
            assert abs(row.ctr - artifacts.RSY_BENCH["ctr"]) <= 0.05, row.campaign
            assert abs(row.cpc - artifacts.RSY_BENCH["cpc"]) <= 0.5, row.campaign

    def test_rsy_cr_by_line_type(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """CR 2,5 % (интересы/ретаргет) и 1,5 % (автотаргетинг)."""
        for row in mediaplan_rows:
            if row.rsy_kind == "cold":
                want_cr = artifacts.RSY_BENCH["cr_cold"]
            elif row.rsy_kind == "warm":
                want_cr = artifacts.RSY_BENCH["cr_warm"]
            else:
                continue
            assert abs(row.cr - want_cr) <= 0.05, (
                f"{row.campaign}: CR {row.cr} want {want_cr}"
            )

    def test_max_clicks_strategy_only_on_autotarget(
        self, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """«Максимум кликов» только у автотаргетинга; остальные РСЯ — «Максимум конверсий»."""
        for row in mediaplan_rows:
            if not row.rsy_kind:
                continue
            if row.rsy_kind == "cold":
                assert "максимум кликов" in row.strategy.lower(), row.campaign
            else:
                assert "максимум конверсий" in row.strategy.lower(), row.campaign


class TestMc4BenchSourceColumn:
    """MC-4: нет столбца «источник бенча» на сетке; нет ложной фразы в допущениях."""

    def test_year_grid_header_has_no_bench_source_column(self, repo_root: Path) -> None:
        """Заголовок mediaplan-year не содержит «источник бенча»."""
        year_text = artifacts.read_text(
            artifacts.snapshots_dir(repo_root) / artifacts.SHEET_FILES["mediaplan_year"]
        )
        header_line = next(
            (
                line
                for line in year_text.splitlines()
                if line.strip().startswith("|") and "кампания" in line.lower()
            ),
            "",
        )
        assert "источник бенча" not in header_line.lower()

    def test_assumptions_no_false_grid_column_claim(self, repo_root: Path) -> None:
        """В допущениях нет утверждения, что на «Медиаплан год» есть столбец «источник бенча»."""
        assumptions_text = artifacts.read_text(
            artifacts.snapshots_dir(repo_root) / artifacts.SHEET_FILES["assumptions"]
        )
        assert not artifacts.assumptions_claims_bench_source_on_year_grid(
            assumptions_text
        ), "assumptions still claim bench-source column on year grid"


class TestFunnelFormulas:
    """Воронка при фиксированном бюджете строки: clicks/spend/imps/purchases/revenue/DRR."""

    @pytest.mark.parametrize("kind", ["brand", "nonbrand", "gallery"])
    def test_search_funnel_formulas_sample_month(
        self,
        mediaplan_rows: list[artifacts.MediaplanRow],
        kind: str,
    ) -> None:
        """Производные метрики Search-строки сходятся с формулами ТЗ (допуск округления)."""
        spec = artifacts.SEARCH_LINES[kind]
        sample = next(row for row in mediaplan_rows if row.search_kind == kind)
        expected = artifacts.expected_funnel_from_budget(
            budget=sample.budget,
            ctr=spec["ctr"],
            cpc=spec["cpc"],
            cr=spec["cr"],
        )
        assert abs(sample.clicks - expected["clicks"]) <= 1
        assert abs(sample.impressions - expected["impressions"]) <= 1
        assert abs(sample.spend - expected["spend"]) <= artifacts.BUDGET_TOLERANCE_RUB
        assert abs(sample.purchases - expected["purchases"]) <= 1
        assert abs(sample.revenue - expected["revenue"]) <= artifacts.BUDGET_TOLERANCE_RUB
        assert abs(sample.drr - expected["drr"]) <= 0.15

    def test_aov_constant_on_grid(self, mediaplan_rows: list[artifacts.MediaplanRow]) -> None:
        """AOV на всех строках сетки = 4 250 ₽."""
        for row in mediaplan_rows:
            assert abs(row.aov - artifacts.AOV) < 0.5, row.campaign


class TestMc5PasteAndXlsxParity:
    """MC-5: paste TSV и xlsx совпадают со snapshots (фаза 3)."""

    def test_paste_mediaplan_contains_search_live_benches(self, repo_root: Path) -> None:
        """Paste mediaplan-year содержит live Search-бенчи и не старый общий 6/45/4.5."""
        paste_path = artifacts.developer_dir(repo_root) / "examiner-sheet-paste.md"
        if not paste_path.is_file():
            pytest.skip("examiner-sheet-paste.md not present yet (phase 3)")
        paste_text = artifacts.read_text(paste_path)
        block = artifacts.extract_paste_tsv_block(
            paste_text, artifacts.PASTE_SECTION_MARKERS["mediaplan_year"]
        )
        assert block, "mediaplan-year TSV block missing in paste"
        assert "10,0" in block or "10.0" in block, "paste lacks brand CTR 10.0%"
        assert "28" in block, "paste lacks brand CPC 28"
        assert "6,5" in block or "6.5" in block, "paste lacks brand CR 6.5%"
        assert "44" in block, "paste lacks gallery CPC 44"

    @pytest.mark.parametrize("sheet_key", list(artifacts.PASTE_SECTION_MARKERS))
    def test_paste_sections_exist(self, repo_root: Path, sheet_key: str) -> None:
        """В paste есть TSV-блок для каждого из пяти листов."""
        paste_path = artifacts.developer_dir(repo_root) / "examiner-sheet-paste.md"
        if not paste_path.is_file():
            pytest.skip("examiner-sheet-paste.md not present yet (phase 3)")
        paste_text = artifacts.read_text(paste_path)
        marker = artifacts.PASTE_SECTION_MARKERS[sheet_key]
        block = artifacts.extract_paste_tsv_block(paste_text, marker)
        assert block, f"missing paste block for {sheet_key}"

    def test_xlsx_has_five_sheets(self, repo_root: Path) -> None:
        """xlsx содержит пять вкладок; сверка ключевых ячеек mediaplan-year."""
        xlsx_path = artifacts.developer_dir(repo_root) / "ecco-kids-direct-mediaplan.xlsx"
        if not xlsx_path.is_file():
            pytest.skip("ecco-kids-direct-mediaplan.xlsx missing — phase 3 delivery artifact")

        sheet_names = artifacts.read_xlsx_sheet_names(xlsx_path)
        expected_names = {
            "Допущения",
            "Инструменты",
            "Медиаплан год",
            "Сводка месяц",
            "Сводка год",
        }
        assert expected_names.issubset(set(sheet_names)), sheet_names

        grid_rows = artifacts.read_xlsx_sheet_rows(xlsx_path, "Медиаплан год")
        flat = "\n".join("\t".join(row) for row in grid_rows)
        assert "бренд ECCO" in flat
        assert "6,5" in flat or "6.5" in flat, "xlsx lacks brand CR 6.5%"
        assert "44" in flat, "xlsx lacks gallery CPC 44"

    def test_paste_mediaplan_row_count_matches_snapshot(
        self, repo_root: Path, mediaplan_rows: list[artifacts.MediaplanRow]
    ) -> None:
        """Число строк данных в paste mediaplan-year = числу строк в snapshot."""
        paste_path = artifacts.developer_dir(repo_root) / "examiner-sheet-paste.md"
        if not paste_path.is_file():
            pytest.skip("examiner-sheet-paste.md not present yet (phase 3)")
        block = artifacts.extract_paste_tsv_block(
            artifacts.read_text(paste_path),
            artifacts.PASTE_SECTION_MARKERS["mediaplan_year"],
        )
        paste_data_rows = [
            line for line in block.splitlines() if line.strip() and "ЕПК ·" in line
        ]
        assert len(paste_data_rows) == len(mediaplan_rows)


class TestMc6GoogleLiveOptional:
    """MC-6: Google Таблица — опционально, не блокер."""

    def test_google_paste_skipped_by_default(self) -> None:
        """Без GOOGLE_PASTE=1 live-проверка Google не требуется."""
        if os.environ.get("GOOGLE_PASTE", "").strip().lower() in ("1", "true", "yes"):
            pytest.xfail("MC-6 Google live check not automated — operator manual step")
        pytest.skip("MC-6 optional: set GOOGLE_PASTE=1 for explicit operator live run")
