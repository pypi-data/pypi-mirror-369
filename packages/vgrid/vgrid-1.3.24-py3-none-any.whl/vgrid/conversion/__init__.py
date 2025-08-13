"""
Conversion module for vgrid.

This module provides functions to convert between different coordinate systems,
geographic data formats, and discrete global grid systems (DGGS).
"""

# Latitude/Longitude to DGGS conversions
from .latlon2dggs import (
    latlon2h3, latlon2s2, latlon2a5, latlon2rhealpix, latlon2isea4t, latlon2isea3h,
    latlon2dggrid, latlon2ease, latlon2qtm, latlon2olc, latlon2geohash,
    latlon2georef, latlon2mgrs, latlon2tilecode, latlon2quadkey,
    latlon2maidenhead, latlon2gars
)

# DGGS Compact and Expand
from .dggscompact.h3compact import h3compact, h3expand
from .dggscompact.s2compact import s2compact, s2expand
from .dggscompact.a5compact import a5compact, a5expand
from .dggscompact.rhealpixcompact import rhealpixcompact, rhealpixexpand
from .dggscompact.isea4tcompact import isea4tcompact, isea4texpand
from .dggscompact.isea3hcompact import isea3hcompact, isea3hexpand
from .dggscompact.easecompact import easecompact, easeexpand
from .dggscompact.qtmcompact import qtmcompact, qtmexpand
from .dggscompact.olccompact import olccompact
from .dggscompact.geohashcompact import geohashcompact, geohashexpand
from .dggscompact.tilecodecompact import tilecodecompact, tilecodeexpand
from .dggscompact.quadkeycompact import quadkeycompact, quadkeyexpand

# Vector to DGGS conversions
from .vector2dggs.vector2h3 import vector2h3
from .vector2dggs.vector2s2 import vector2s2
from .vector2dggs.vector2a5 import vector2a5
from .vector2dggs.vector2rhealpix import vector2rhealpix
from .vector2dggs.vector2isea3h import vector2isea3h
from .vector2dggs.vector2ease import vector2ease
from .vector2dggs.vector2qtm import vector2qtm
from .vector2dggs.vector2olc import vector2olc
from .vector2dggs.vector2geohash import vector2geohash
from .vector2dggs.vector2mgrs import vector2mgrs
from .vector2dggs.vector2tilecode import vector2tilecode
from .vector2dggs.vector2quadkey import vector2quadkey

# Raster to DGGS conversions
from .raster2dggs.raster2h3 import raster2h3
from .raster2dggs.raster2s2 import raster2s2
from .raster2dggs.raster2a5 import raster2a5
from .raster2dggs.raster2rhealpix import raster2rhealpix
from .raster2dggs.raster2isea4t import raster2isea4t
from .raster2dggs.raster2qtm import raster2qtm
from .raster2dggs.raster2olc import raster2olc
from .raster2dggs.raster2geohash import raster2geohash
from .raster2dggs.raster2tilecode import raster2tilecode
from .raster2dggs.raster2quadkey import raster2quadkey

__all__ = [
    # LatLon to DGGS
    'latlon2h3', 'latlon2s2', 'latlon2a5', 'latlon2rhealpix', 'latlon2isea4t', 'latlon2isea3h',
    'latlon2dggrid', 'latlon2ease', 'latlon2qtm', 'latlon2olc', 'latlon2geohash',
    'latlon2georef', 'latlon2mgrs', 'latlon2tilecode', 'latlon2quadkey',
    'latlon2maidenhead', 'latlon2gars',
    # DGGS Compact and Expand
    'h3compact', 'h3expand', 's2compact', 's2expand', 'a5compact', 'a5expand', 'rhealpixcompact', 'rhealpixexpand',
    'isea4tcompact', 'isea4texpand', 'isea3hcompact', 'isea3hexpand', 'easecompact',
    'easeexpand', 'qtmcompact', 'qtmexpand', 'olccompact', 'geohashcompact',
    'geohashexpand', 'tilecodecompact', 'tilecodeexpand', 'quadkeycompact',
    'quadkeyexpand',
    # Vector to DGGS
    'vector2h3', 'vector2s2', 'vector2a5', 'vector2rhealpix', 'vector2isea3h',
    'vector2ease', 'vector2qtm', 'vector2olc', 'vector2geohash',
    'vector2mgrs', 'vector2tilecode', 'vector2quadkey',    # Raster to DGGS
    'raster2h3', 'raster2s2', 'raster2a5', 'raster2rhealpix', 'raster2isea4t', 'raster2qtm',
    'raster2olc', 'raster2geohash', 'raster2tilecode', 'raster2quadkey'
]
