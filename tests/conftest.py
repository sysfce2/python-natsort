"""
Fixtures for pytest.
"""

from __future__ import annotations

import locale
from typing import TYPE_CHECKING

import hypothesis
import pytest

from natsort.compat.locale import dumb_sort

if TYPE_CHECKING:
    from collections.abc import Iterator

# This disables the "too slow" hypothesis heath check globally.
# For some reason it thinks that the text/binary generation is too
# slow then causes the tests to fail.
hypothesis.settings.register_profile(
    "slow-tests",
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)


def load_locale(x: str) -> None:
    """Convenience to load a locale."""
    locale.setlocale(locale.LC_ALL, str(f"{x}.UTF-8"))


@pytest.fixture
def with_locale_en_us() -> Iterator[None]:
    """Convenience to load the en_US locale - reset when complete."""
    orig = locale.getlocale()
    load_locale("en_US")
    yield
    locale.setlocale(locale.LC_ALL, orig)


@pytest.fixture
def with_locale_de_de() -> Iterator[None]:
    """
    Convenience to load the de_DE locale - reset when complete - skip if missing.
    """
    orig = locale.getlocale()
    try:
        load_locale("de_DE")
    except locale.Error:
        pytest.skip("requires de_DE locale to be installed")
    else:
        yield
    finally:
        locale.setlocale(locale.LC_ALL, orig)


@pytest.fixture
def with_locale_cs_cz() -> Iterator[None]:
    """
    Convenience to load the cs_CZ locale - reset when complete - skip if missing.
    """
    orig = locale.getlocale()
    try:
        load_locale("cs_CZ")
        if dumb_sort():
            pytest.skip("requires a functioning locale library to run")
    except locale.Error:
        pytest.skip("requires cs_CZ locale to be installed")
    else:
        yield
    finally:
        locale.setlocale(locale.LC_ALL, orig)
