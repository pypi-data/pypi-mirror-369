"""
Polyhedra module for vgrid.

This module provides various polyhedra implementations used in discrete global grid systems (DGGS).
"""

from .cube import Cube
from .cube_s2 import CubeS2
from .hexagon import Hexagon
from .octahedron import Octahedron
from .tetrahedron import Tetrahedron
from .fuller_icosahedron import FullerIcosahedron
from .rhombic_icosahedron import RhombicIcosahedron

__all__ = [
    'Cube', 'CubeS2', 'Hexagon', 'Octahedron', 'Tetrahedron',
    'FullerIcosahedron', 'RhombicIcosahedron'
]
