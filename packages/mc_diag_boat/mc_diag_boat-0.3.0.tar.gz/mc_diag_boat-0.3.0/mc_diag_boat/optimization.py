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


from typing import Sequence
import numpy as np


def pareto_indices(points: Sequence[Sequence] | np.ndarray) -> np.ndarray:
    """The index of each sequence on the pareto front of all passed sequences.

    This function aims for maximization, so measures which are intended to be
    minimized should be negated prior to being passed.

    Parameters
    ----------
    `points` : `Sequence[Sequence]` or `numpy.ndarray`
        A sequence of sequences or 2D numpy array with values that support
        comparison. Each inner sequence should contain the relevant measures for
        an object which can be used to determine whether it lies on the pareto
        front of all objects in the top-level sequence.

    Returns
    -------
    `indices` : `numpy.ndarray`
        An array of the index of each sequence that lies on the pareto front.
    """
    points = np.array(points)
    return np.where(np.apply_along_axis(
            lambda p: ~np.any(np.all(points >= p, axis=1) & np.any(points > p, axis=1)),
            axis=1,
            arr=points,
    ))[0]

