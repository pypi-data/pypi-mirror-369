"""
VGrid - A comprehensive library for discrete global grid systems (DGGS).

This package provides tools for working with various discrete global grid systems
including H3, S2, RHEALPix, ISEA4T, ISEA3H, EASE, QTM, OLC, Geohash, GEOREF,
MGRS, Tilecode, Quadkey, Maidenhead, and GARS.

Main modules:
- binning: Data binning and aggregation functions
- conversion: Coordinate and format conversion utilities
- correction: Data correction and fixing tools
- dggs: Core DGGS implementations
- generator: Grid generation functions
- stats: Statistical analysis tools
- utils: Utility functions and helpers
"""

# Version information
__version__ = "0.1.0"

# Import main modules
from . import binning
from . import conversion
from . import generator
from . import stats

# Import key functions from each module for easy access
from .conversion import (
    latlon2h3, latlon2s2, latlon2a5, latlon2rhealpix, latlon2isea4t, latlon2isea3h,
    latlon2dggrid, latlon2ease, latlon2qtm, latlon2olc, latlon2geohash,
    latlon2georef, latlon2mgrs, latlon2tilecode, latlon2quadkey,
    latlon2maidenhead, latlon2gars,
    # Compact functions
    h3compact, h3expand, s2compact, s2expand, a5compact, a5expand, rhealpixcompact, rhealpixexpand,
    isea4tcompact, isea4texpand, isea3hcompact, isea3hexpand, easecompact,
    easeexpand, qtmcompact, qtmexpand, olccompact, geohashcompact,
    geohashexpand, tilecodecompact, tilecodeexpand, quadkeycompact,
    quadkeyexpand,
    # Vector conversions
    vector2h3, vector2s2, vector2a5, vector2rhealpix, vector2isea3h,
    vector2ease, vector2qtm, vector2olc, vector2geohash,
    vector2mgrs, vector2tilecode, vector2quadkey,
    # Raster conversions
    raster2h3, raster2s2, raster2a5, raster2rhealpix, raster2isea4t, raster2qtm,
    raster2olc, raster2geohash, raster2tilecode, raster2quadkey
)

from .binning import (
    h3bin, s2bin, a5bin, rhealpixbin, isea4tbin, qtmbin, olcbin, geohashbin,
    tilecodebin, quadkeybin, polygonbin
)


from .generator import (
    h3grid, s2grid, a5grid, rhealpixgrid, easegrid, qtmgrid, olcgrid, geohashgrid,
    georefgrid, mgrsgrid, tilecodegrid, quadkeygrid, maidenheadgrid, garsgrid
)

from .stats import (
    h3stats, s2_metrics, s2stats, a5_metrics, a5stats, rhealpix_metrics, rhealpixstats,
    easestats, qtm_metrics, qtmstats, olc_metrics, olcstats,
    geohash_metrics, geohashstats, georef_metrics, georefstats,
    mgrs_metrics, mgrsstats, tilecode_metrics, tilecodestats,
    quadkey_metrics, quadkeystats, maidenhead_metrics, maidenheadstats,
    gars_metrics, garsstats, dggridstats
)

__all__ = [
    # Version
    '__version__',
    # Main modules
    'binning', 'conversion', 'correction', 'dggs', 'generator', 'stats', 'utils',
    # Binning functions
    'h3bin', 's2bin', 'a5bin', 'rhealpixbin', 'isea4tbin', 'qtmbin', 'olcbin', 'geohashbin',
    'tilecodebin', 'quadkeybin', 'polygonbin',
    # Conversion functions
    'latlon2h3', 'latlon2s2', 'latlon2a5', 'latlon2rhealpix', 'latlon2isea4t', 'latlon2isea3h',
    'latlon2dggrid', 'latlon2ease', 'latlon2qtm', 'latlon2olc', 'latlon2geohash',
    'latlon2georef', 'latlon2mgrs', 'latlon2tilecode', 'latlon2quadkey',
    'latlon2maidenhead', 'latlon2gars',
    'h3compact', 'h3expand', 's2compact', 's2expand', 'a5compact', 'a5expand', 'rhealpixcompact', 'rhealpixexpand',
    'isea4tcompact', 'isea4texpand', 'isea3hcompact', 'isea3hexpand', 'easecompact',
    'easeexpand', 'qtmcompact', 'qtmexpand', 'olccompact', 'geohashcompact',
    'geohashexpand', 'tilecodecompact', 'tilecodeexpand', 'quadkeycompact',
    'quadkeyexpand',
    'vector2h3', 'vector2s2', 'vector2a5', 'vector2rhealpix', 'vector2isea3h',
    'vector2ease', 'vector2qtm', 'vector2olc', 'vector2geohash',
    'vector2mgrs', 'vector2tilecode', 'vector2quadkey', 
    'raster2h3', 'raster2s2', 'raster2a5', 'raster2rhealpix', 'raster2isea4t', 'raster2qtm',
    'raster2olc', 'raster2geohash', 'raster2tilecode', 'raster2quadkey',
    # Generator functions
    'h3grid', 's2grid', 'a5grid', 'rhealpixgrid', 'easegrid', 'qtmgrid', 'olcgrid', 'geohashgrid',
    'georefgrid', 'mgrsgrid', 'tilecodegrid', 'quadkeygrid', 'maidenheadgrid', 'garsgrid',
    # Stats functions
    'h3stats', 's2_metrics', 's2stats', 'a5_metrics', 'a5stats', 'rhealpix_metrics', 'rhealpixstats',
    'easestats', 'qtm_metrics', 'qtmstats', 'olc_metrics', 'olcstats',
    'geohash_metrics', 'geohashstats', 'georef_metrics', 'georefstats',
    'mgrs_metrics', 'mgrsstats', 'tilecode_metrics', 'tilecodestats',
    'quadkey_metrics', 'quadkeystats', 'maidenhead_metrics', 'maidenheadstats',
    'gars_metrics', 'garsstats', 'dggridstats',
    ]
