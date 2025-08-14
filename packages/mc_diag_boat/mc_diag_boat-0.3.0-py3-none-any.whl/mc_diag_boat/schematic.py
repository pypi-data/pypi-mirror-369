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
import litemapy as lm
from .vec2 import Vec2


SXN_SIZE = 16


def _add_gaps(raster: Sequence[Vec2[int]], gap_size: int) -> list[Vec2[int]]:
    """Add gaps to the raster, effectively removing all indices except every
    `gap_size` + 1 index.

    Parameters
    ----------
    `raster` : `Sequence[Vec2[int]]`
        The raster to modify.
    `gap_size` : `int`
        The number of indices to skip between each included index.
        Should be non-negative.

    Returns
    -------
    `raster_with_gaps` : `list[Vec2[int]]`
        The raster, with only every `gap_size` + 1 block included.
    """
    return [
        coord
        for index, coord in enumerate(raster)
        if index % (gap_size + 1) == 0 or index == len(raster) - 1
    ]


def _cut_regions(raster: Sequence[Vec2[int]]) -> list[Sequence[Vec2[int]]]:
    """Section the raster into, at biggest, chunk-sized regions.

    Parameters
    ----------
    `raster` : `Sequence[Vec2[int]]`
        The raster to modify.

    Returns
    -------
    `regions` : `list[Sequence[Vec2[int]]]`
        The list of regions, each region spanning at most 16 blocks square.
    """
    regions: list[Sequence[Vec2]] = []
    region_start_index = 0
    for index in range(len(raster)):
        diff = (raster[index] - raster[region_start_index])
        if abs(diff.x) >= SXN_SIZE or abs(diff.z) >= SXN_SIZE:
            regions.append(raster[region_start_index:index])
            region_start_index = index
    if region_start_index < len(raster) - 1:
        regions.append(raster[region_start_index:len(raster) - 1])
    return regions


def _make_region(raster: Sequence[Vec2[int]], blocks: Sequence[lm.BlockState]) -> lm.Region:
    """Create a region object for inclusion in a schematic object.

    Parameters
    ----------
    `raster` : `Sequence[Vec2[int]]`
        The raster of positions at which to insert blocks.
    `blocks` : `Sequence[litemapy.BlockState]`
        A sequence of blocks to place at each location specified by `raster`.
        Blocks are placed on top of one another, in the order they were provided.
        I.e., the first block is placed on the bottom.
    """
    if len(blocks) == 0:
        raise ValueError("Must be at least one BlockState provided.")
    region_span = Vec2(
        raster[-1].x - raster[0].x + (1 if raster[-1].x >= 0 else -1),
        raster[-1].z - raster[0].z + (1 if raster[-1].z >= 0 else -1)
    )
    region = lm.Region(
        x=raster[0].x,
        y=0,
        z=raster[0].z,
        width=int(region_span.x),
        height=len(blocks),
        length=int(region_span.z),
    )
    for coords in raster:
        for block_index, block_state in enumerate(blocks):
            region[coords.x - raster[0].x, block_index, coords.z - raster[0].z] = block_state
    return region


def generate_schematic(
    offset: Vec2,
    gap_size: int = 0,
    blocks: lm.BlockState | Sequence[lm.BlockState] = lm.BlockState("minecraft:blue_ice"),
    name: str | None = None
) -> lm.Schematic:
    """Create a schematic for the path to the given offset.

    Parameters
    ----------
    `offset` : `Vec2`
        The position of the endpoint of the path (beginning is assumed to be at
        block (0, 0)). This should represent the block position of the endpoint,
        i.e., the start is assumed to be at continuous coordinates (0.5, 0.5),
        which is the center of block (0, 0); specify the endpoint relative to
        the center of a whole block. E.g., providing (10.1, -5.8) will place
        the endpoint at the center of (10, -5) + (0.1, -0.8), or continuous
        coordinates (10.5, -4.5) + (0.1, -0.8) = (10.6, -5.3).
    `gap_size` : `int`, default `0`
        The number of blocks to skip between each included block. `0` or `1`
        are recommended for boat roads. Should be non-negative.
    `name` : `str`, optional
        The name of the schematic, shown in the Litematica UI.

    Returns
    -------
    `schematic` : `litemapy.Schematic`
        The schematic object representing the path from block (0, 0) to block
        `offset`, with gaps added.
    """
    raster = offset.raster()
    gapped_raster = _add_gaps(raster, gap_size)
    regioned_raster = _cut_regions(gapped_raster)
    if name is None:
        name = lm.info.DEFAULT_NAME
    schem = lm.Schematic(name=name, author="mc_diag_boat")
    if isinstance(blocks, lm.BlockState):
        blocks = [blocks]
    for index, region in enumerate(regioned_raster):
        schem.regions[str(index)] = _make_region(region, blocks)
    return schem

