# -*- coding: utf-8 -*-
"""Import local xlsx into an existing Google Sheet (File > Import > Replace)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

DEFAULT_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1A31rkQ9JkJ3Bet8coGxcXw22bwFhqq4Xk7_GQxtdc8c/edit"
)
XLSX = Path(__file__).with_name("ecco-kids-direct-mediaplan-formulas.xlsx")
SHOT = Path(__file__).parent
CHROME_USER_DATA = Path(
    r"C:\Users\cherv\AppData\Local\Google\Chrome\User Data"
)
PLAYWRIGHT_PROFILE = Path(__file__).parent / ".playwright-chrome-profile"
SUCCESS_TAB_MARKERS: tuple[str, ...] = (
    "Параметры плана",
    "Инструменты",
    "Медиаплан на год",
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Разбирает аргументы CLI для импорта xlsx в Google Sheet.

    Args:
        argv: Список аргументов; по умолчанию ``sys.argv[1:]``.

    Returns:
        Namespace с полем ``url`` — целевая таблица Google Sheets.
    """
    parser = argparse.ArgumentParser(description="Import xlsx into Google Sheet (replace).")
    parser.add_argument("--url", default=DEFAULT_URL, help="Target Google Spreadsheet URL")
    return parser.parse_args(argv)


def dump(page: Page, name: str) -> None:
    """Сохраняет скриншот страницы и печатает метаданные.

    Args:
        page: Активная страница Playwright.
        name: Суффикс имени файла ``import-{name}.png``.
    """
    page.screenshot(path=str(SHOT / f"import-{name}.png"), full_page=True)
    print("SCREENSHOT", name, "URL", page.url, "TITLE", page.title())


def _try_persistent_context(
    playwright: Playwright,
    user_data_dir: Path,
    label: str,
    launch_args: list[str],
) -> BrowserContext | None:
    """Пробует launch_persistent_context; при ошибке возвращает None.

    Args:
        playwright: Экземпляр Playwright.
        user_data_dir: Каталог профиля Chrome/Chromium.
        label: Метка для лога при неудаче.
        launch_args: Аргументы запуска браузера.

    Returns:
        BrowserContext или None.
    """
    user_data_dir.mkdir(parents=True, exist_ok=True)
    try:
        return playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            channel="chrome",
            headless=False,
            locale="ru-RU",
            viewport={"width": 1440, "height": 900},
            args=launch_args,
        )
    except Exception as exc:  # noqa: BLE001 — try next auth strategy
        print("WARN", label, "failed:", type(exc).__name__, str(exc).encode("ascii", "replace").decode())
        return None


def launch_context(playwright: Playwright) -> tuple[BrowserContext, str]:
    """Запускает браузер с несколькими стратегиями авторизации.

    Args:
        playwright: Экземпляр Playwright.

    Returns:
        Кортеж (context, auth_mode_label).
    """
    launch_args = ["--disable-blink-features=AutomationControlled"]
    for label, profile_dir in (
        ("persistent-chrome-user", CHROME_USER_DATA),
        ("persistent-playwright-profile", PLAYWRIGHT_PROFILE),
    ):
        if not profile_dir.is_dir() and label == "persistent-chrome-user":
            continue
        context = _try_persistent_context(playwright, profile_dir, label, launch_args)
        if context is not None:
            return context, label
    browser = playwright.chromium.launch(headless=False, args=launch_args)
    context = browser.new_context(locale="ru-RU", viewport={"width": 1440, "height": 900})
    return context, "default-chromium"


def is_login_wall(page: Page) -> bool:
    """Проверяет, видна ли кнопка входа Google (нет сессии).

    Args:
        page: Страница Google Sheets.

    Returns:
        True если обнаружена кнопка «Войти» / Sign in.
    """
    sign_in = page.get_by_role("link", name="Войти").or_(
        page.get_by_role("button", name="Войти")
    ).or_(page.get_by_role("link", name="Sign in"))
    return sign_in.count() > 0


def open_import_dialog(page: Page) -> bool:
    """Открывает меню Файл → Импортировать.

    Args:
        page: Страница Google Sheets.

    Returns:
        True если диалог импорта, похоже, открыт.
    """
    file_btn = page.locator("#docs-file-menu")
    if not file_btn.count():
        file_btn = page.get_by_role("menuitem", name="Файл").or_(
            page.get_by_role("button", name="Файл")
        )
    file_btn.first.click()
    page.wait_for_timeout(800)
    dump(page, "file-menu")
    page.keyboard.press("i")
    page.wait_for_timeout(2000)
    if page.locator('input[type="file"]').count() == 0:
        imp = page.locator(".goog-menuitem").filter(has_text="Импортировать")
        if imp.count():
            imp.first.click(force=True, timeout=8000)
            page.wait_for_timeout(1500)
    dump(page, "import-dialog")
    return page.locator('input[type="file"]').count() > 0 or page.get_by_text(
        "Импорт файла", exact=False
    ).count() > 0


def upload_xlsx(page: Page, xlsx_path: Path) -> bool:
    """Загружает xlsx через диалог импорта.

    Args:
        page: Страница с открытым диалогом импорта.
        xlsx_path: Путь к локальному xlsx.

    Returns:
        True если input[type=file] найден и файл установлен.
    """
    chooser = page.locator('input[type="file"]')
    if chooser.count() == 0:
        dialog = page.locator('[role="dialog"]').last
        upload_tab = dialog.get_by_role("tab", name="Загрузка").or_(
            dialog.get_by_role("tab", name="Upload")
        )
        if upload_tab.count():
            upload_tab.first.click(force=True)
            page.wait_for_timeout(800)
    chooser = page.locator('input[type="file"]')
    if chooser.count() == 0:
        print("FAIL no file input")
        dump(page, "no-file-input")
        return False
    chooser.first.set_input_files(str(xlsx_path))
    page.wait_for_timeout(4000)
    dump(page, "after-file")
    return True


def confirm_replace(page: Page) -> None:
    """Выбирает «Заменить электронную таблицу» и подтверждает импорт.

    Args:
        page: Страница с загруженным файлом в диалоге импорта.
    """
    for label in (
        "Заменить электронную таблицу",
        "Replace current sheet",
        "Replace spreadsheet",
        "Заменить таблицу",
    ):
        loc = page.get_by_text(label, exact=False)
        if loc.count():
            loc.first.click()
            page.wait_for_timeout(400)
            break
    for label in ("Импортировать данные", "Import data", "Импорт"):
        loc = page.get_by_role("button", name=label)
        if loc.count():
            loc.first.click()
            break
        loc = page.get_by_text(label, exact=True)
        if loc.count():
            loc.first.click()
            break
    page.wait_for_timeout(8000)
    dump(page, "after-import")


def tabs_match_success(tabs: Sequence[str]) -> bool:
    """Проверяет, что среди вкладок есть ожидаемые имена сезонного медиаплана.

    Args:
        tabs: Список имён вкладок после импорта.

    Returns:
        True если найден хотя бы один маркер из SUCCESS_TAB_MARKERS.
    """
    return any(marker in tab for tab in tabs for marker in SUCCESS_TAB_MARKERS)


def run_import(url: str) -> int:
    """Выполняет полный цикл импорта xlsx в Google Sheet.

    Args:
        url: URL целевой таблицы.

    Returns:
        Код выхода: 0 — успех, иначе код ошибки.
    """
    if not XLSX.exists():
        print("MISSING", XLSX)
        return 2
    with sync_playwright() as playwright:
        context, auth_mode = launch_context(playwright)
        print("AUTH", auth_mode)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        dump(page, "open")
        if "accounts.google.com" in page.url or is_login_wall(page):
            print("FAIL login-wall")
            dump(page, "login-wall")
            context.close()
            return 3
        page.wait_for_selector(
            ".docs-sheet-tab-name, #t-name-box, #docs-file-menu", timeout=45000
        )
        if not open_import_dialog(page):
            print("FAIL import-dialog-not-open")
            dump(page, "import-dialog-fail")
            context.close()
            return 6
        if not upload_xlsx(page, XLSX):
            context.close()
            return 4
        confirm_replace(page)
        tabs = page.locator(".docs-sheet-tab-name").all_inner_texts()
        print("TABS", tabs)
        ok = tabs_match_success(tabs)
        context.close()
        return 0 if ok else 5


def main() -> int:
    """Точка входа CLI."""
    args = parse_args()
    return run_import(args.url)


if __name__ == "__main__":
    sys.exit(main())
