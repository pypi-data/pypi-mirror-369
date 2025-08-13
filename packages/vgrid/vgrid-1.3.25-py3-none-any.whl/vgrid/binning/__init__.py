"""
Binning module for vgrid.

This module provides functions to bin and aggregate data using various
discrete global grid systems (DGGS), including statistical analysis
and data categorization.
"""

# Import all binning functions
from .h3bin import h3bin, h3_bin
from .s2bin import s2bin, s2_bin
from .a5bin import a5bin, a5_bin
from .rhealpixbin import rhealpixbin, rhealpix_bin
from .isea4tbin import isea4tbin, isea4t_bin
from .qtmbin import qtmbin, qtm_bin
from .olcbin import olcbin, olc_bin
from .geohashbin import geohashbin, geohash_bin
from .tilecodebin import tilecodebin, tilecode_bin
from .quadkeybin import quadkeybin, quadkey_bin
from .polygonbin import polygonbin, polygon_bin

# Import helper functions
from .bin_helper import get_default_stats_structure, append_stats_value

__all__ = [
    # Main binning functions
    'h3bin', 'h3_bin',
    's2bin', 's2_bin',
    'a5bin', 'a5_bin',
    'rhealpixbin', 'rhealpix_bin',
    'isea4tbin', 'isea4t_bin',
    'qtmbin', 'qtm_bin',
    'olcbin', 'olc_bin',
    'geohashbin', 'geohash_bin',
    'tilecodebin', 'tilecode_bin',
    'quadkeybin', 'quadkey_bin',
    'polygonbin', 'polygon_bin',
    # Helper functions
    'get_default_stats_structure', 'append_stats_value'
]
