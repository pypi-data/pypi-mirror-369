# MC Diag Boat - A set of functions for building diagonal boat roads in Minecraft
# Copyright (C) 2024  ribqahisabsent

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from typing import Literal, Sequence
from pathlib import Path


def pretty_seqs(
    sequences: Sequence[Sequence],
    align: Literal["L", "R", "C"] | Sequence[Literal["L", "R", "C"]] = "L",
    separator: str = " ",
) -> list[str]:
    """Format the given sequences as index-aligned strings.

    This function aligns the string representations of elements of sequences
    to make them easier to read when printed as subsequent lines.

    Parameters
    ----------
    `sequences` : `Sequence[Sequence]`
        The sequences to format, ordered row-first.
        E.g., `(("a", 0), ("b", 1))` -> `["a 0", "b 1"]`
    `align` : `Literal["L", "R", "C"]` or `Sequence` thereof, default "L"
        A character or sequence of characters indicating whether column elements
        should be aligned left (L), right (R), or center (C). If a character is
        given, all columns will be aligned according to it. If a sequence is given,
        it must have the same number of elements as the second-level sequences
        provided in `sequences`.
    `separator` : `str`, default `" "`
        The string to add between each column element in the final strings.

    Returns
    -------
    `rows` : `list[str]`
        The list of strings with each element spaced according to the maximum length
        of any other element in that column, aligned according to `align`.
    """
    if len({len(sequence) for sequence in sequences}) > 1:
        raise ValueError("All sequences must be the same length")
    item_lengths = [max(len(str(item)) for item in col) for col in zip(*sequences)]
    if align == "L":
        return [
            separator.join(f"{str(item):<{item_lengths[col]}}" for col, item in enumerate(row))
            for row in sequences
        ]
    if align == "R":
        return [
            separator.join(f"{str(item):>{item_lengths[col]}}" for col, item in enumerate(row))
            for row in sequences
        ]
    if align == "C":
        return [
            separator.join(f"{str(item):^{item_lengths[col]}}" for col, item in enumerate(row))
            for row in sequences
        ]
    if isinstance(align, tuple) and len(align) != len(sequences[0]):
        raise ValueError("`align` must be the same length as each sequence")
    rows: list[str] = []
    for index, row in enumerate(sequences):
        if align[index] == "L":
            rows.append(separator.join(f"{str(item):<{item_lengths[col]}}" for col, item in enumerate(row)))
        if align[index] == "R":
            rows.append(separator.join(f"{str(item):>{item_lengths[col]}}" for col, item in enumerate(row)))
        if align[index] == "C":
            rows.append(separator.join(f"{str(item):^{item_lengths[col]}}" for col, item in enumerate(row)))
    return rows


def unique_filename(filepath: str | Path) -> Path:
    filepath = Path(filepath)
    if filepath.suffix == "":
        raise ValueError("filepath must have a suffix")
    if not filepath.exists():
        return filepath
    for n in range(1, 100):
        numbered_filepath = filepath.with_stem(f"{filepath.stem}_{n:02d}")
        if not numbered_filepath.exists():
            return numbered_filepath
    raise RuntimeError(f"Exceeded max number of attempts to generate unique filepath for {filepath}")

