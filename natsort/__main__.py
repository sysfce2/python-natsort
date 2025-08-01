"""Entry-point for command-line interface."""

from __future__ import annotations

import argparse
import sys
import textwrap
from collections.abc import Iterable
from typing import TYPE_CHECKING, Callable, Union, cast

import natsort
from natsort.utils import regex_chooser

if TYPE_CHECKING:
    from re import Pattern

Num = Union[float, int]
NumIter = Iterable[Num]
NumPair = tuple[Num, Num]
NumPairIter = Iterable[NumPair]
NumConverter = Callable[[str], Num]


class TypedArgs(argparse.Namespace):
    """Typed command-line argument namespace."""

    paths: bool
    filter: list[NumPair] | None
    reverse_filter: list[NumPair] | None
    exclude: list[Num]
    reverse: bool
    number_type: str
    nosign: bool
    sign: bool
    noexp: bool
    locale: bool
    zero_terminated: bool
    entries: list[str]

    def __init__(  # noqa: PLR0913
        self,
        filter: list[NumPair] | None = None,
        reverse_filter: list[NumPair] | None = None,
        exclude: list[Num] | None = None,
        paths: bool = False,  # noqa: FBT001, FBT002
        reverse: bool = False,  # noqa: FBT001, FBT002
        zero_terminated: bool = False,  # noqa: FBT001, FBT002
        entries: list[str] | None = None,
    ) -> None:
        """Use this constructor only for running the unit tests."""
        self.filter = filter
        self.reverse_filter = reverse_filter
        self.exclude = [] if exclude is None else exclude
        self.paths = paths
        self.reverse = reverse
        self.number_type = "int"
        self.signed = False
        self.exp = True
        self.locale = False
        self.zero_terminated = zero_terminated
        if entries is None:
            entries = []
        self.entries = entries


def main(*arguments: str) -> None:
    """
    Perform a natural sort on entries given on the command-line.

    Arguments are read from sys.argv.
    """
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(cast("str", main.__doc__)),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {natsort.__version__}",
    )
    parser.add_argument(
        "-p",
        "--paths",
        default=False,
        action="store_true",
        help="Interpret the input as file paths.  This is not "
        "strictly necessary to sort all file paths, but in cases "
        'where there are OS-generated file paths like "Folder/" '
        'and "Folder (1)/", this option is needed to make the '
        'paths sorted in the order you expect ("Folder/" before '
        '"Folder (1)/").',
    )
    parser.add_argument(
        "-f",
        "--filter",
        nargs=2,
        type=float,
        metavar=("LOW", "HIGH"),
        action="append",
        help="Used for keeping only the entries that have a number "
        "falling in the given range.",
    )
    parser.add_argument(
        "-F",
        "--reverse-filter",
        nargs=2,
        type=float,
        metavar=("LOW", "HIGH"),
        action="append",
        dest="reverse_filter",
        help="Used for excluding the entries that have a number "
        "falling in the given range.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=float,
        action="append",
        help="Used to exclude an entry that contains a specific number.",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        default=False,
        help="Returns in reversed order.",
    )
    parser.add_argument(
        "-t",
        "--number-type",
        "--number_type",
        dest="number_type",
        choices=("int", "float", "real", "f", "i", "r"),
        default="int",
        help='Choose the type of number to search for. "float" will search '
        'for floating-point numbers.  "int" will only search for '
        'integers. "real" is a shortcut for "float" with --sign. '
        '"i" is a synonym for "int", "f" is a synonym for '
        '"float", and "r" is a synonym for "real".'
        "The default is %(default)s.",
    )
    parser.add_argument(
        "--nosign",
        default=False,
        action="store_false",
        dest="signed",
        help='Do not consider "+" or "-" as part of a number, i.e. do not '
        "take sign into consideration. This is the default.",
    )
    parser.add_argument(
        "-s",
        "--sign",
        default=False,
        action="store_true",
        dest="signed",
        help='Consider "+" or "-" as part of a number, i.e. '
        "take sign into consideration. The default is unsigned.",
    )
    parser.add_argument(
        "--noexp",
        default=True,
        action="store_false",
        dest="exp",
        help="Do not consider an exponential as part of a number, i.e. 1e4, "
        'would be considered as 1, "e", and 4, not as 10000.  This only '
        "effects the --number-type=float.",
    )
    parser.add_argument(
        "-l",
        "--locale",
        action="store_true",
        default=False,
        help="Causes natsort to use locale-aware sorting. You will get the "
        "best results if you install PyICU.",
    )
    parser.add_argument(
        "-z",
        "--zero-terminated",
        action="store_true",
        default=False,
        help="When reading from stdin, split entries on nulls (\\0) "
        "instead of newlines.",
    )
    parser.add_argument(
        "entries",
        nargs="*",
        help="The entries to sort. Taken from stdin if nothing is given on "
        "the command line.",
        # Note: if nothing is given on the command line, args.entries is an empty list.
    )
    args = parser.parse_args(arguments or None, namespace=TypedArgs())

    # Make sure the filter range is given properly. Does nothing if no filter
    args.filter = check_filters(args.filter)
    args.reverse_filter = check_filters(args.reverse_filter)

    # Determine which entries to sort.
    entries = get_entries(args)

    # Sort by directory then by file within directory and print.
    sort_and_print_entries(entries, args)


def range_check(low: Num, high: Num) -> NumPair:
    """
    Verify that that given range has a low lower than the high.

    Parameters
    ----------
    low : {float, int}
        Low end of the range.
    high : {float, int}
        High end of the range.

    Returns
    -------
    tuple : low, high

    Raises
    ------
    ValueError
        Low is greater than or equal to high.

    """
    if low >= high:
        msg = "low >= high"
        raise ValueError(msg)
    return low, high


def check_filters(filters: NumPairIter | None) -> list[NumPair] | None:
    """
    Execute range_check for every element of an iterable.

    Parameters
    ----------
    filters : iterable
        The collection of filters to check. Each element
        must be a two-element tuple of floats or ints.

    Returns
    -------
    The input as-is, or None if it evaluates to False.

    Raises
    ------
    ValueError
        Low is greater than or equal to high for any element.

    """
    if not filters:
        return None
    try:
        return [range_check(f[0], f[1]) for f in filters]
    except ValueError as err:
        raise ValueError("Error in --filter: " + str(err)) from None


def get_entries(args: TypedArgs) -> list[str]:
    """Determine which entries to sort."""
    # Read entries from command line or stdin?
    # If reading from stdin, are entries split on nulls or newlines?
    if len(args.entries) > 0:
        entries = args.entries
    else:
        separator = "\0" if args.zero_terminated else "\n"
        entries = sys.stdin.read().rstrip(separator).split(separator)

    # Remove trailing whitespace from all the entries
    return [e.strip() for e in entries]


def keep_entry_range(
    entry: str,
    lows: NumIter,
    highs: NumIter,
    converter: NumConverter,
    regex: Pattern[str],
) -> bool:
    """
    Check if an entry falls into a desired range.

    Every number in the entry will be extracted using *regex*,
    if any are within a given low to high range the entry will
    be kept.

    Parameters
    ----------
    entry : str
        The string to check.
    lows : iterable
        Collection of low values against which to compare the entry.
    highs : iterable
        Collection of high values against which to compare the entry.
    converter : callable
        Function to convert a string to a number.
    regex : regex object
        Regular expression to locate numbers in a string.

    Returns
    -------
    True if the entry should be kept, False otherwise.

    """
    return any(
        low <= converter(num) <= high
        for num in regex.findall(entry)
        for low, high in zip(lows, highs)
    )


def keep_entry_value(
    entry: str,
    values: NumIter,
    converter: NumConverter,
    regex: Pattern[str],
) -> bool:
    """
    Check if an entry does not match a given value.

    Every number in the entry will be extracted using *regex*,
    if any match a given value the entry will not be kept.

    Parameters
    ----------
    entry : str
        The string to check.
    values : iterable
        Collection of values against which to compare the entry.
    converter : callable
        Function to convert a string to a number.
    regex : regex object
        Regular expression to locate numbers in a string.

    Returns
    -------
    True if the entry should be kept, False otherwise.

    """
    return not any(converter(num) in values for num in regex.findall(entry))


def sort_and_print_entries(entries: list[str], args: TypedArgs) -> None:
    """Sort the entries, applying the filters first if necessary."""
    # Extract the proper number type.
    is_float = args.number_type in ("float", "real", "f", "r")
    signed = args.signed or args.number_type in ("real", "r")
    alg: int = (
        natsort.ns.FLOAT * is_float
        | natsort.ns.SIGNED * signed
        | natsort.ns.NOEXP * (not args.exp)
        | natsort.ns.PATH * args.paths
        | natsort.ns.LOCALE * args.locale
    )

    # Pre-remove entries that don't pass the filtering criteria
    # Make sure we use the same searching algorithm for filtering
    # as for sorting.
    do_filter = args.filter is not None or args.reverse_filter is not None
    if do_filter or args.exclude:
        inp_options = (
            natsort.ns.FLOAT * is_float
            | natsort.ns.SIGNED * signed
            | natsort.ns.NOEXP * (not args.exp)
        )
        regex = regex_chooser(inp_options)
        if args.filter is not None:
            lows, highs = ([f[0] for f in args.filter], [f[1] for f in args.filter])
            entries = [
                entry
                for entry in entries
                if keep_entry_range(entry, lows, highs, float, regex)
            ]
        if args.reverse_filter is not None:
            lows, highs = (
                [f[0] for f in args.reverse_filter],
                [f[1] for f in args.reverse_filter],
            )
            entries = [
                entry
                for entry in entries
                if not keep_entry_range(entry, lows, highs, float, regex)
            ]
        if args.exclude:
            exclude = set(args.exclude)
            entries = [
                entry
                for entry in entries
                if keep_entry_value(entry, exclude, float, regex)
            ]

    # Print off the sorted results
    for entry in natsort.natsorted(entries, reverse=args.reverse, alg=alg):
        print(entry)  # noqa: T201


if __name__ == "__main__":
    try:
        main()
    except ValueError as a:
        sys.exit(str(a))
    except KeyboardInterrupt:
        sys.exit(1)
