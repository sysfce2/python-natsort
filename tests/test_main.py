"""\
Test the natsort command-line tool functions.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
from hypothesis import given
from hypothesis.strategies import DataObject, data, floats, integers, lists

from natsort.__main__ import (
    TypedArgs,
    check_filters,
    get_entries,
    keep_entry_range,
    keep_entry_value,
    main,
    range_check,
    sort_and_print_entries,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_main_passes_default_arguments_with_no_command_line_options(
    mocker: MockerFixture,
) -> None:
    p = mocker.patch("natsort.__main__.sort_and_print_entries")
    main("num-2", "num-6", "num-1")
    args = p.call_args[0][1]
    assert not args.paths
    assert args.filter is None
    assert args.reverse_filter is None
    assert args.exclude == []
    assert not args.reverse
    assert args.number_type == "int"
    assert not args.signed
    assert args.exp
    assert not args.locale


def test_main_passes_arguments_with_all_command_line_options(
    mocker: MockerFixture,
) -> None:
    arguments = ["--paths", "--reverse", "--locale"]
    arguments.extend(["--filter", "4", "10"])
    arguments.extend(["--reverse-filter", "100", "110"])
    arguments.extend(["--number-type", "float"])
    arguments.extend(["--noexp", "--sign"])
    arguments.extend(["--exclude", "34"])
    arguments.extend(["--exclude", "35"])
    arguments.extend(["num-2", "num-6", "num-1"])
    p = mocker.patch("natsort.__main__.sort_and_print_entries")
    main(*arguments)
    args = p.call_args[0][1]
    assert args.paths
    assert args.filter == [(4.0, 10.0)]
    assert args.reverse_filter == [(100.0, 110.0)]
    assert args.exclude == [34, 35]
    assert args.reverse
    assert args.number_type == "float"
    assert args.signed
    assert not args.exp
    assert args.locale


mock_print = "builtins.print"

entries = [
    "tmp/a57/path2",
    "tmp/a23/path1",
    "tmp/a1/path1",
    "tmp/a1 (1)/path1",
    "tmp/a130/path1",
    "tmp/a64/path1",
    "tmp/a64/path2",
]


@pytest.mark.parametrize(
    ("options", "order"),
    [
        # Defaults, all options false
        # tmp/a1 (1)/path1  # noqa: ERA001
        # tmp/a1/path1
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        # tmp/a130/path1
        ([None, None, False, False, False], [3, 2, 1, 0, 5, 6, 4]),
        # Path option True
        # tmp/a1/path1
        # tmp/a1 (1)/path1  # noqa: ERA001
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        # tmp/a130/path1
        ([None, None, False, True, False], [2, 3, 1, 0, 5, 6, 4]),
        # Filter option keeps only within range
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        ([[(20, 100)], None, False, False, False], [1, 0, 5, 6]),
        # Reverse filter, exclude in range
        # tmp/a1/path1
        # tmp/a1 (1)/path1  # noqa: ERA001
        # tmp/a130/path1
        ([None, [(20, 100)], False, True, False], [2, 3, 4]),
        # Exclude given values with exclude list
        # tmp/a1/path1
        # tmp/a1 (1)/path1  # noqa: ERA001
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        ([None, None, [23, 130], True, False], [2, 3, 0, 5, 6]),
        # Reverse order
        # tmp/a130/path1
        # tmp/a64/path2
        # tmp/a64/path1
        # tmp/a57/path2
        # tmp/a23/path1
        # tmp/a1 (1)/path1  # noqa: ERA001
        # tmp/a1/path1
        ([None, None, False, True, True], reversed([2, 3, 1, 0, 5, 6, 4])),
    ],
)
def test_sort_and_print_entries(
    options: list[Any],
    order: list[int],
    mocker: MockerFixture,
) -> None:
    p = mocker.patch(mock_print)
    sort_and_print_entries(entries, TypedArgs(*options))
    e = [mocker.call(entries[i]) for i in order]
    p.assert_has_calls(e)


@pytest.mark.parametrize(
    ("zero_terminated", "stdin_content"),
    [
        (False, "num-2\nnum-6\nnum-1"),
        (False, "num-2\nnum-6\nnum-1\n"),
        (True, "num-2\0num-6\0num-1"),
        (True, "num-2\0num-6\0num-1\0"),
    ],
)
def test_get_entries(
    zero_terminated: bool,
    stdin_content: str,
    mocker: MockerFixture,
) -> None:
    """Test that the entries are read correctly from stdin."""
    args = TypedArgs(zero_terminated=zero_terminated)
    mock_stdin = mocker.patch("sys.stdin.read", return_value=stdin_content)
    entries = get_entries(args)
    mock_stdin.assert_called_once_with()
    assert entries == ["num-2", "num-6", "num-1"]


# Each test has an "example" version for demonstrative purposes,
# and a test that uses the hypothesis module.


def test_range_check_returns_range_as_is_but_with_floats_example() -> None:
    assert range_check(10, 11) == (10.0, 11.0)
    assert range_check(6.4, 30) == (6.4, 30.0)


@given(x=floats(allow_nan=False, min_value=-1e8, max_value=1e8) | integers(), d=data())
def test_range_check_returns_range_as_is_if_first_is_less_than_second(
    x: float,
    d: DataObject,
) -> None:
    # Pull data such that the first is less than the second.
    if isinstance(x, float):
        y = d.draw(floats(min_value=x + 1.0, max_value=1e9, allow_nan=False))
    else:
        y = d.draw(integers(min_value=x + 1))
    assert range_check(x, y) == (x, y)


def test_range_check_raises_value_error_if_second_is_less_than_first_example() -> None:
    with pytest.raises(ValueError, match="low >= high"):
        range_check(7, 2)


@given(x=floats(allow_nan=False), d=data())
def test_range_check_raises_value_error_if_second_is_less_than_first(
    x: float,
    d: DataObject,
) -> None:
    # Pull data such that the first is greater than or equal to the second.
    y = d.draw(floats(max_value=x, allow_nan=False))
    with pytest.raises(ValueError, match="low >= high"):
        range_check(x, y)


def test_check_filters_returns_none_if_filter_evaluates_to_false() -> None:
    assert check_filters(()) is None


def test_check_filters_returns_input_as_is_if_filter_is_valid_example() -> None:
    assert check_filters([(6, 7)]) == [(6, 7)]
    assert check_filters([(6, 7), (2, 8)]) == [(6, 7), (2, 8)]


@given(x=lists(integers(), min_size=1), d=data())
def test_check_filters_returns_input_as_is_if_filter_is_valid(
    x: list[int],
    d: DataObject,
) -> None:
    # ensure y is element-wise greater than x
    y = [d.draw(integers(min_value=val + 1)) for val in x]
    assert check_filters(list(zip(x, y))) == list(zip(x, y))


def test_check_filters_raises_value_error_if_filter_is_invalid_example() -> None:
    with pytest.raises(ValueError, match="Error in --filter: low >= high"):
        check_filters([(7, 2)])


@given(x=lists(integers(), min_size=1), d=data())
def test_check_filters_raises_value_error_if_filter_is_invalid(
    x: list[int],
    d: DataObject,
) -> None:
    # ensure y is element-wise less than or equal to x
    y = [d.draw(integers(max_value=val)) for val in x]
    with pytest.raises(ValueError, match="Error in --filter: low >= high"):
        check_filters(list(zip(x, y)))


@pytest.mark.parametrize(
    ("lows", "highs", "truth"),
    # 1. Any portion is between the bounds => True.
    # 2. Any portion is between any bounds => True.
    # 3. No portion is between the bounds => False.
    [([0], [100], True), ([1, 88], [20, 90], True), ([1], [20], False)],
)
def test_keep_entry_range(lows: list[int], highs: list[int], truth: bool) -> None:
    assert keep_entry_range("a56b23c89", lows, highs, int, re.compile(r"\d+")) is truth


# 1. Values not in entry => True. 2. Values in entry => False.
@pytest.mark.parametrize(("values", "truth"), [([100, 45], True), ([23], False)])
def test_keep_entry_value(values: list[int], truth: bool) -> None:
    assert keep_entry_value("a56b23c89", values, int, re.compile(r"\d+")) is truth
