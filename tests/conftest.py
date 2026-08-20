"""Общие pytest-фикстуры для монорепозитория Polina."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Корень git-репозитория (родитель каталога ``tests/``).

    Returns:
        Абсолютный путь к корню репозитория.
    """
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def tests_root(repo_root: Path) -> Path:
    """Корень каталога ``tests/``.

    Args:
        repo_root: Корень репозитория.

    Returns:
        Абсолютный путь к ``tests/``.
    """
    return repo_root / "tests"
