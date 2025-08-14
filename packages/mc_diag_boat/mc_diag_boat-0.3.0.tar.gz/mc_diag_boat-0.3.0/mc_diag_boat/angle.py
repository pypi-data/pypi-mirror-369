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


from typing import ClassVar, Self, overload


class Angle(float):
    BOAT_ANGLE_STEP: ClassVar[Self]
    NORTH: ClassVar[Self]
    WEST: ClassVar[Self]
    SOUTH: ClassVar[Self]
    EAST: ClassVar[Self]
    ZERO: ClassVar[Self]
    BOAT_ANGLES: ClassVar[list[Self]]

    def __new__(cls, degrees: float) -> Self:
        return super().__new__(cls, (degrees + 180) % 360 - 180)

    def __pos__(self) -> Self:
        return type(self)(+self)

    def __neg__(self) -> Self:
        return type(self)(-self)

    def angular_dist(self, other: float) -> Self:
        """The angle from this angle to another, [-180, 180).

        Parameters
        ----------
        `other` : `float`
            The comparison angle.

        Returns
        -------
        `angle` : `Angle`
            The angle from this angle to `other`. Values are bounded [-180, 180)
            and represent what angle would add with this angle to reach `other`.
        """
        return self.__class__((other - self + 180) % 360 - 180)

    @overload
    def closest_boat_angle(self) -> Self: ...
    @overload
    def closest_boat_angle(self, n: int) -> list[Self]: ...
    def closest_boat_angle(self, n: int | None = None) -> Self | list[Self]:
        """The closest angle(s) to this angle that a boat could face.

        Parameters
        ----------
        `n` : `int`, optional
            The number of angles to return. If not given, 1 angle is returned.
            If `-1`, all 256 boat angles are returned, in ascending order of
            angular distance from this angle.

        Returns
        -------
        `angle(s)` : `Angle` or `list[Angle]`
            The valid boat angle(s) which is/are closest to this angle. If `n`
            is not given or `1`, the return type is `Angle`.
        """
        sorted_boat_angles = sorted(
            self.BOAT_ANGLES,
            key=lambda x: abs(self.angular_dist(x))
        )
        if n is None or n == 1:
            return sorted_boat_angles[0]
        if n == -1:
            n = 256
        if 0 < n <= 256:
            return sorted_boat_angles[:n]
        raise ValueError("n must be -1 or in [1, 256]")

    def boat_placement_range(self) -> tuple[Self, Self] | None:
        """The angular range within which a boat can be placed to reach
        the closest boat angle to this angle.

        Returns
        -------
        `angular_range` : `tuple[Angle, Angle]`
            The angles between which a player could face while placing a boat
            and have it face towards the closest boat angle to this angle,
            sorted in ascending order.
        """
        boat_angle = self.closest_boat_angle()
        if boat_angle == 180.0 or boat_angle == -180.0:
            return None
        if boat_angle < 0.0:
            return self.__class__(boat_angle - self.BOAT_ANGLE_STEP), self
        if boat_angle > 0.0:
            return self, self.__class__(boat_angle + self.BOAT_ANGLE_STEP)
        return -self.BOAT_ANGLE_STEP, self.BOAT_ANGLE_STEP


Angle.BOAT_ANGLE_STEP = Angle(360 / 256)
Angle.NORTH = Angle(-180.0)
Angle.WEST = Angle(90.0)
Angle.SOUTH = Angle(0.0)
Angle.EAST = Angle(-90.0)
Angle.BOAT_ANGLES = [Angle(index * Angle.BOAT_ANGLE_STEP) for index in range(-128, 128)]

