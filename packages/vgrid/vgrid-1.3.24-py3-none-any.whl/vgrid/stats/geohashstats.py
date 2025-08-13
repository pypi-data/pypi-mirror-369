"""
This module provides functions for generating statistics for Geohash DGGS cells.
"""
import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
from vgrid.utils.constants import AUTHALIC_AREA, VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
from vgrid.generator.geohashgrid import geohashgrid
from vgrid.utils.geometry import check_crossing_geom
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm

def geohash_metrics(res, unit: str = "m"):
    """
    Calculate metrics for Geohash DGGS cells.
    
    Args:
        res: Resolution level (0-12)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, avg_edge_len_in_unit, avg_cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    num_cells = 32 ** res
    
    # Calculate area in km² first
    avg_cell_area_km2 = AUTHALIC_AREA / num_cells
    avg_edge_len_km = math.sqrt(avg_cell_area_km2)
    
    # Convert to requested unit
    if unit == "m":
        avg_cell_area = avg_cell_area_km2 * (10**6)  # Convert km² to m²
        avg_edge_len = avg_edge_len_km * 1000  # Convert km to m
    else:  # unit == "km"
        avg_cell_area = avg_cell_area_km2
        avg_edge_len = avg_edge_len_km
    
    return num_cells, avg_edge_len, avg_cell_area


def geohashstats(unit: str = "m"):
    """
    Generate statistics for Geohash DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing Geohash DGGS statistics with columns:
            - resolution: Resolution level (0-12)
            - number_of_cells: Number of cells at each resolution
            - avg_edge_len_{unit}: Average edge length in the given unit
            - avg_cell_area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    min_res = 1
    max_res = 12    
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_len, avg_cell_area = geohash_metrics(res, unit=unit)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lens.append(avg_edge_len)
        avg_cell_areas.append(avg_cell_area)
    
    # Create DataFrame
    # Build column labels with unit awareness (lower case)
    avg_edge_len = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    avg_cell_area = f"avg_cell_area_{unit_area_label}"

    df = pd.DataFrame({
        'resolution': resolutions,
        'number_of_cells': num_cells_list,
        avg_edge_len: avg_edge_lens,
        avg_cell_area: avg_cell_areas
    })
    
    return df


def geohashstats_cli(unit: str = "m"):
    """
    Command-line interface for generating Geohash DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default=None)
    args, _ = parser.parse_known_args()

    unit = args.unit if args.unit is not None else unit

    # Get the DataFrame
    df = geohashstats(unit=unit)
    
    # Display the DataFrame
    print(df.to_string(index=False))


def geohashinspect(res):
    """
    Generate comprehensive inspection data for Geohash DGGS cells at a given resolution.
    
    This function creates a detailed analysis of Geohash cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: Geohash resolution level (0-12)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing Geohash cell inspection data with columns:
            - geohash: Geohash cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    geohash_gpd = geohashgrid(res, output_format="gpd")
    geohash_gpd['crossed'] = geohash_gpd['geometry'].apply(check_crossing_geom)
    mean_area = geohash_gpd['cell_area'].mean()
    # Calculate normalized area
    geohash_gpd['norm_area'] = geohash_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    geohash_gpd['ipq'] = 4 * np.pi * geohash_gpd['cell_area'] / (geohash_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    geohash_gpd['zsc'] = np.sqrt(4*np.pi*geohash_gpd['cell_area'] - np.power(geohash_gpd['cell_area'],2)/np.power(6378137,2))/geohash_gpd['cell_perimeter']
    return geohash_gpd

def geohash_norm_area(geohash_gpd):
    """
    Plot normalized area map for Geohash cells.
    
    This function creates a visualization showing how Geohash cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        geohash_gpd: GeoDataFrame from geohashinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = geohash_gpd['norm_area'].min(), geohash_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    geohash_gpd = geohash_gpd[~geohash_gpd['crossed']] # remove cells that cross the dateline
    geohash_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "Geohash Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def geohash_compactness(geohash_gpd):
    """
    Plot IPQ compactness map for Geohash cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of Geohash cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.785 indicating more regular squares.
    
    Args:
        geohash_gpd: GeoDataFrame from geohashinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = geohash_gpd['ipq'].min(), geohash_gpd['ipq'].max(), np.mean([geohash_gpd['ipq'].min(), geohash_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
    geohash_gpd = geohash_gpd[~geohash_gpd['crossed']] # remove cells that cross the dateline
    geohash_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "Geohash IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def geohashinspect_cli():
    """
    Command-line interface for Geohash cell inspection.
    
    CLI options:
      -r, --resolution: Geohash resolution level (0-12)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 2
    print(geohashinspect(res))


if __name__ == "__main__":
    geohashstats_cli()
