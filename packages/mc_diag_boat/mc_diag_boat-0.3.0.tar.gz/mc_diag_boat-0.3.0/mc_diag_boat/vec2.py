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


from typing import ClassVar, Generic, Self, SupportsIndex, TypeVar, overload
from dataclasses import dataclass
from math import radians, degrees, sin, cos, atan2, dist
import skimage.draw
from .angle import Angle


_T = TypeVar("_T", int, float)


@dataclass(frozen=True, slots=True)
class Vec2(Generic[_T]):
    """A 2D vector class which supports restriction to integer values
    for type hinting purposes.

    As these vectors are assumed to lie in the horizontal plane, their
    scalars are accessed via the attributes `x` and `z`.
    """
    x: _T
    z: _T

    NORTH: ClassVar["Vec2[int]"]
    WEST: ClassVar["Vec2[int]"]
    SOUTH: ClassVar["Vec2[int]"]
    EAST: ClassVar["Vec2[int]"]
    ZERO: ClassVar["Vec2[int]"]
    ZERODEG: ClassVar["Vec2[int]"]

    @classmethod
    def from_polar(cls, r: float, phi: float) -> "Vec2[float]":
        """Create a `Vec2[float]` from polar coordinate values.

        Parameters
        ----------
        `r` : `float`
            The radius, or length, of the new vector.
        `phi` : `float`
            The angle, in degrees, of the new vector, in terms of
            Minecraft horizontal facing direction.

        Returns
        -------
        `vector` : `Vec2[float]`
            A vector with the given length and angle.
        """
        return cls.ZERODEG.rotate(phi) * r

    @overload
    def __add__(self, other: "Vec2[int]") -> Self: ...
    @overload
    def __add__(self, other: "Vec2[float]") -> "Vec2[float]": ...
    def __add__(self, other: "Vec2") -> Self | "Vec2[float]":
        return Vec2(self.x + other.x, self.z + other.z)

    @overload
    def __sub__(self, other: "Vec2[int]") -> Self: ...
    @overload
    def __sub__(self, other: "Vec2[float]") -> "Vec2[float]": ...
    def __sub__(self, other: "Vec2") -> Self | "Vec2[float]":
        return Vec2(self.x - other.x, self.z - other.z)

    @overload
    def __mul__(self, scalar: SupportsIndex) -> Self: ...
    @overload
    def __mul__(self, scalar: float) -> "Vec2[float]": ...
    def __mul__(self, scalar: SupportsIndex | float) -> Self | "Vec2[float]":
        if isinstance(scalar, SupportsIndex):
            scalar = int(scalar)
            return type(self)(self.x * scalar, self.z * scalar)
        return Vec2(self.x * scalar, self.z * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vec2[float]":
        return Vec2(self.x / scalar, self.z / scalar)

    @overload
    def __floordiv__(self, scalar: SupportsIndex) -> Self: ...
    @overload
    def __floordiv__(self, scalar: float) -> "Vec2[float]": ...
    def __floordiv__(self, scalar: SupportsIndex | float) -> Self | "Vec2[float]":
        if isinstance(scalar, SupportsIndex):
            scalar = int(scalar)
            return type(self)(self.x // scalar, self.z // scalar)
        return Vec2(self.x // scalar, self.z // scalar)

    def __repr__(self) -> str:
        return f"({self.x}, {self.z})"

    def length(self) -> float:
        """The length of this vector

        Returns
        -------
        `length` : `float`
            The Euclidean length of this vector.
        """
        return dist((0, 0), (self.x, self.z))

    def angle(self) -> Angle:
        """The angle of this vector.

        Returns
        -------
        `angle` : `float`
            The angle, in degrees, of this vector in terms of
            Minecraft horizontal facing direction (0.0 == South).
        """
        return Angle(-1 * degrees(atan2(self.x, self.z)))

    def rotate(self, angle: float) -> "Vec2[float]":
        """Return a rotated version of this vector.

        Parameters
        ----------
        `angle` : `float`
            The angle, in degrees, by which this vector will be rotated.

        Returns
        -------
        `rotated` : `Vec2[float]`
            A rotated version of the original vector.
        """
        radian_angle = radians(angle)
        angle_cos = cos(radian_angle)
        angle_sin = sin(radian_angle)
        return Vec2(
            self.x * angle_cos - self.z * angle_sin,
            self.x * angle_sin + self.z * angle_cos,
        )

    def normalize(self) -> "Vec2[float]":
        """This vector's normal vector.

        Returns
        -------
        `normal` : `Vec2[float]`
            The normal vector (length = 1.0) along
            the same angle as this vector.
        """
        return self / self.length()

    @overload
    def dot(self, other: "Vec2[int]") -> _T: ...
    @overload
    def dot(self, other: "Vec2[float]") -> float: ...
    def dot(self, other: "Vec2") -> _T | float:
        """The dot product of this vector and another.

        Parameters
        ----------
        `other` : `Vec2`
            The vector to dot with this vector.

        Returns
        -------
        `dot` : `int` or `float`
            The dot product.
        """
        return self.x * other.x + self.z * other.z

    @overload
    def cross(self, other: "Vec2[int]") -> _T: ...
    @overload
    def cross(self, other: "Vec2[float]") -> float: ...
    def cross(self, other: "Vec2") -> _T | float:
        """The cross product of this vector and another.

        Parameters
        ----------
        `other` : `Vec2`
            The vector to cross with this vector.

        Returns
        -------
        `cross` : `int` or `float`
            The cross product.
        """
        return self.x * other.z - self.z * other.x

    def project(self, other: "Vec2") -> "Vec2[float]":
        """The projection of this vector onto another vector.

        Parameters
        ----------
        `other` : `Vec2`
            The vector to project this vector to.

        Returns
        -------
        `projection` : `Vec2[float]`
            The projection of this vector onto `other`.
        """
        if other == Vec2.ZERO:
            raise ValueError("`other` must be a nonzero Vec2")
        return self.dot(other) / other.dot(other) * other

    @overload
    def round(self) -> "Vec2[int]": ...
    @overload
    def round(self, ndigits: SupportsIndex) -> "Vec2[float]": ...
    def round(self, ndigits: SupportsIndex | None = None) -> "Vec2":
        """A rounded version of this vector.

        Parameters
        ----------
        `ndigits` : `int`, optional
            The number of digits to include after the decimal.
            If no value is given, a `Vec2[int]` is returned.
            If any value is given, even 0, a `Vec2[float]` is returned.

        Returns
        -------
        `rounded` : `Vec2[int]` or `Vec2[float]`
            A rounded version of the original vector.
        """
        if ndigits is None:
            return Vec2(round(self.x), round(self.z))
        return Vec2(round(self.x, ndigits), round(self.z, ndigits))

    def as_tuple(self) -> tuple[_T, _T]:
        """The tuple of the `x` and `z` values of this vector.

        Returns
        -------
        `xz_tuple` : `tuple[_T, _T]`
            A tuple containing the `x` and `z` values of the vector.
        """
        return self.x, self.z

    def dense_str(self) -> str:
        """A string representation of this vector with no spaces.

        Returns
        -------
        `dense_str` : `str`
            E.g., "(8,-5)".
        """
        return f"({self.x},{self.z})"

    def raster(self, origin: "Vec2 | None" = None, block_coords: bool = True) -> list["Vec2[int]"]:
        """The raster of this vector.

        The raster is a continuous, direct path of block locations
        from the origin (default (0, 0)) to the vector tail.

        Parameters
        ----------
        `origin` : `Vec2` or `None`, optional
            The start coordinate of the raster.
            If `None` (default), `Vec2(0, 0)` is used.
        `block_coords` : `bool`, optional
            Whether the origin and end coordinate parameters represent
            block locations or continuous coordinate values.

        Returns
        -------
        `raster` : `list` of `Vec2[int]`
            The list of block locations in the continuous, direct path.
        """
        if origin is None:
            origin = Vec2(0, 0)
        if block_coords:
            coord_adjustment = Vec2.ZERO
        else:
            coord_adjustment = Vec2(-0.5, -0.5)
        return [
            Vec2(int(x), int(z))
            for x, z in zip(*skimage.draw.line_nd(
                (origin + coord_adjustment).as_tuple(),
                (self + coord_adjustment).as_tuple(),
                endpoint=True,
            ))
        ]


Vec2.NORTH = Vec2(0, -1)
Vec2.WEST = Vec2(-1, 0)
Vec2.SOUTH = Vec2(0, 1)
Vec2.EAST = Vec2(1, 0)
Vec2.ZERO = Vec2(0, 0)
Vec2.ZERODEG = Vec2.SOUTH

