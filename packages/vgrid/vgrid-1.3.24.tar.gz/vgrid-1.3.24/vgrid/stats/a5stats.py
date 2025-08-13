"""
This module provides functions for generating statistics for A5 DGGS cells.
"""
import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
from a5.core.cell_info import get_num_cells, cell_area
from vgrid.generator.a5grid import a5grid
from vgrid.utils.geometry import check_crossing_geom
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
from vgrid.utils.constants import VMIN_PEN, VMAX_PEN, VCENTER_PEN
def a5_metrics(res, unit: str = "m"):
    """
    Calculate metrics for A5 DGGS cells at a given resolution.
    
    Args:
        res: Resolution level (0-29)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    num_cells = get_num_cells(res)
    avg_cell_area_m2 = cell_area(res)  # Assuming cell_area returns area in m²
    
    # Calculate edge length in meters
    k = math.sqrt(5*(5+2*math.sqrt(5)))
    avg_edge_len_m = round(math.sqrt(4*avg_cell_area_m2/k), 3)
    
    # Convert to requested unit
    if unit == "km":
        avg_edge_len = avg_edge_len_m / 1000.0
        avg_cell_area = avg_cell_area_m2 / (1000.0 ** 2)
    else:  # unit == "m"
        avg_edge_len = avg_edge_len_m
        avg_cell_area = avg_cell_area_m2
    
    return num_cells, avg_edge_len, avg_cell_area


def a5stats(unit: str = "m"):
    """
    Generate statistics for A5 DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing A5 DGGS statistics with columns:
            - Resolution: Resolution level (0-29)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_{unit}: Average edge length in the given unit
            - Avg_Cell_Area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    min_res = 0
    max_res = 29
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_len, avg_cell_area = a5_metrics(res, unit=unit)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lens.append(avg_edge_len)
        avg_cell_areas.append(avg_cell_area)
    
    # Create DataFrame
    # Build column labels with unit awareness
    avg_edge_len = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    avg_cell_area = f"avg_cell_area_{unit_area_label}"

    df = pd.DataFrame({
        'resolution': resolutions,
        'number_of_Cells': num_cells_list,
        avg_edge_len: avg_edge_lens,
        avg_cell_area: avg_cell_areas
    }, index=None)
    
    return df


def a5stats_cli(unit: str = "m"):
    """
    Command-line interface for generating A5 DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default=None)
    args, _ = parser.parse_known_args()

    unit = args.unit if args.unit is not None else unit

    # Get the DataFrame
    df = a5stats(unit=unit)    
    # Display the DataFrame
    print(df)


def a5inspect(res):
    """
    Generate comprehensive inspection data for A5 DGGS cells at a given resolution.
    
    This function creates a detailed analysis of A5 cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: A5 resolution level (0-29)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing A5 cell inspection data with columns:
            - a5: A5 cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    a5_gpd = a5grid(res, output_format="gpd")
    a5_gpd['crossed'] = a5_gpd['geometry'].apply(check_crossing_geom)
    mean_area = a5_gpd['cell_area'].mean()
    # Calculate normalized area
    a5_gpd['norm_area'] = a5_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    a5_gpd['ipq'] = 4 * np.pi * a5_gpd['cell_area'] / (a5_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    a5_gpd['zsc'] = np.sqrt(4*np.pi*a5_gpd['cell_area'] - np.power(a5_gpd['cell_area'],2)/np.power(6378137,2))/a5_gpd['cell_perimeter']
    return a5_gpd

def a5_norm_area(a5_gpd):
    """
    Plot normalized area map for A5 cells.
    
    This function creates a visualization showing how A5 cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        a5_gpd: GeoDataFrame from a5inspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = a5_gpd['norm_area'].min(), a5_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    a5_gpd = a5_gpd[~a5_gpd['crossed']] # remove cells that cross the dateline
    a5_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "A5 Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def a5_compactness(a5_gpd):
    """
    Plot IPQ compactness map for A5 cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of A5 cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.907 indicating more regular hexagons.
    
    Args:
        a5_gpd: GeoDataFrame from a5inspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = a5_gpd['ipq'].min(), a5_gpd['ipq'].max(),np.mean([a5_gpd['ipq'].min(), a5_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_PEN, vcenter=VCENTER_PEN, vmax=VMAX_PEN)
    a5_gpd = a5_gpd[~a5_gpd['crossed']] # remove cells that cross the dateline
    a5_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "A5 IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def a5inspect_cli():
    """
    Command-line interface for A5 cell inspection.
    
    CLI options:
      -r, --resolution: A5 resolution level (0-29)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 0
    print(a5inspect(res))

if __name__ == "__main__":
    a5stats_cli()
