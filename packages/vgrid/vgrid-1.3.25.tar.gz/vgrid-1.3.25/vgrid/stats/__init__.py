"""
Statistics module for vgrid.

This module provides functions to calculate and display statistics for various
discrete global grid systems (DGGS), including cell counts, areas, and edge lengths.
"""

# DGGS statistics functions
import platform

from .h3stats import h3stats
from .s2stats import s2_metrics, s2stats
from .a5stats import a5_metrics, a5stats
from .rhealpixstats import rhealpix_metrics, rhealpixstats
# if platform.system() == "Windows":
    # from .isea4tstats import isea4t_metrics, isea4tstats
    # from .isea3hstats import isea3h_metrics, isea3hstats
from .easestats import easestats
from .qtmstats import qtm_metrics, qtmstats
from .olcstats import olc_metrics, olcstats
from .geohashstats import geohash_metrics, geohashstats
from .georefstats import georef_metrics, georefstats
from .mgrsstats import mgrs_metrics, mgrsstats
from .tilecodestats import tilecode_metrics, tilecodestats
from .quadkeystats import quadkey_metrics, quadkeystats
from .maidenheadstats import maidenhead_metrics, maidenheadstats
from .garsstats import gars_metrics, garsstats

# DGGRID statistics
from .dggridstats import dggridstats

__all__ = [
    # H3 statistics
    'h3stats',
    # S2 statistics
    's2_metrics', 's2stats',
    # A5 statistics
    'a5_metrics', 'a5stats',
    # RHEALPix statistics
    'rhealpix_metrics', 'rhealpixstats',
    # ISEA4T statistics 
    # ISEA3H statistics
    # 'isea3h_metrics', 'isea3hstats',
    # EASE statistics
    'easestats',
    # QTM statistics
    'qtm_metrics', 'qtmstats',
    # OLC statistics
    'olc_metrics', 'olcstats',
    # Geohash statistics
    'geohash_metrics', 'geohashstats',
    # GEOREF statistics
    'georef_metrics', 'georefstats',
    # MGRS statistics
    'mgrs_metrics', 'mgrsstats',
    # Tilecode statistics
    'tilecode_metrics', 'tilecodestats',
    # Quadkey statistics
    'quadkey_metrics', 'quadkeystats',
    # Maidenhead statistics
    'maidenhead_metrics', 'maidenheadstats',
    # GARS statistics
    'gars_metrics', 'garsstats',
    # DGGRID statistics
    'dggridstats'
]
