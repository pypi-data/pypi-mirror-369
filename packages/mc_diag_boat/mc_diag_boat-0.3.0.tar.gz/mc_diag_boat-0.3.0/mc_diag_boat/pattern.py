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


from types import ModuleType
from typing import Iterable
from dataclasses import dataclass
from functools import cached_property
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from .vec2 import Vec2
from .optimization import pareto_indices


class Pattern(list[Vec2[int]]):
    """A child class of `list`, restricted to `Vec2[int]` elements and adding
    methods for plotting and error assessment.
    """
    MIN_PLOT_COLOR = 0.12

    def __init__(self, iterable: Iterable, target: Vec2) -> None:
        super().__init__(iterable)
        self.target = target

    def deviation(self) -> float:
        """The distance between the extension of this pattern's direction and
        the target destination.

        Returns
        -------
        `deviation` : `float`
            The deviation distance in blocks.
        """
        if len(self) <= 1:
            raise IndexError("Pattern with length <2 has no points to determine deviation")
        return (self.target - self.target.project(self[-1])).length()

    def plot(self) -> tuple[Figure, ModuleType]:
        """A plot representing the block positions in this pattern.

        Returns
        -------
        `fig` : `matplotlib.figure.Figure`
            A figure showing the block placement locations in this pattern.
            Save the figure by calling its `savefig()` method. Display the figure
            by calling the `show()` function of the returned `plt` module.
        `plt` : `ModuleType` (`matplotlib.pyplot`)
            The `matplotlib.pyplot` module. This is returned as a convenience,
            enabling the calling script to show the figure with `plt.show()`.
        """
        pattern_space = np.zeros((abs(self[-1].x) + 1, abs(self[-1].z) + 1))
        for index, point in enumerate(self[:-1]):
            pattern_space[(abs(point.x), abs(point.z))] = (len(self) - index) / len(self) + self.MIN_PLOT_COLOR
        pattern_space[(abs(self[-1].x), abs(self[-1].z))] = 1.0 + self.MIN_PLOT_COLOR
        pattern_space = np.transpose(pattern_space)
        fig, ax = plt.subplots()
        ax.imshow(pattern_space, cmap="turbo", interpolation="nearest")
        if self[-1].x < 0:
            fig.gca().invert_xaxis()
        if self[-1].z < 0:
            fig.gca().invert_yaxis()
        ax.set_title("Start at red (0, 0), follow rainbow\n(lone red is start of next iteration)")
        ax.set_xlabel("West < - > East")
        ax.set_ylabel("South < - > North")
        ax.set_xticks(
            [i for i in range(abs(self[-1].x) + 1)],
            [str(i) for i in range(abs(self[-1].x) + 1)],
            rotation=90
        )
        ax.set_yticks([i for i in range(abs(self[-1].z) + 1)])
        return fig, plt

@dataclass(frozen=True)
class PatternGenerator:
    """A class which generates all patterns (up to `max_pattern_len`) for a
    given target offset.
    """
    target: Vec2
    max_pattern_len: int = 64

    @cached_property
    def patterns(self) -> list[Pattern]:
        """`list[Pattern]` : All patterns generated for the given target.
        """
        raster = self.target.raster()
        return [
            Pattern(raster[:length], self.target)
            for length in range(2, min(len(raster), self.max_pattern_len + 1))
        ]

    @cached_property
    def pareto_front(self) -> list[Pattern]:
        """`list[Pattern]` : All patterns on the pareto front of all patterns
        generated for the given target.
        """
        paretos = pareto_indices([
            (-pattern.deviation(), -len(pattern))
            for pattern in self.patterns
        ])
        return [self.patterns[index] for index in paretos]

    def len_sorted(self, short2long: bool = True) -> list[Pattern]:
        """All generated patterns sorted by sequence length.

        Parameters
        ----------
        `short2long` : `bool`, default `True`
            Whether to sort from shortest to longest.
        """
        if short2long:
            return sorted(self.patterns, key=lambda p: len(p))
        return sorted(self.patterns, key=lambda p: -len(p))

    def deviation_sorted(self, close2far: bool = True) -> list[Pattern]:
        """All generated patterns sorted by deviation from the target.

        Parameters
        ----------
        `close2far` : `bool`, default `True`
            Whether to sort from lowest deviation to highest
        """
        if close2far:
            return sorted(self.patterns, key=lambda p: p.deviation())
        return sorted(self.patterns, key=lambda p: -p.deviation())

