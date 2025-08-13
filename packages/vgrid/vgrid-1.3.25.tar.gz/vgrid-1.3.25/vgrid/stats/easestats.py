"""
This module provides functions for generating statistics for EASE-DGGS cells.
"""
import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
from vgrid.dggs.easedggs.constants import levels_specs
from vgrid.utils.constants import VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
from vgrid.generator.easegrid import easegrid
from vgrid.utils.geometry import check_crossing_geom
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm


def ease_metrics(res, unit: str = "m"):
    """
    Calculate metrics for EASE-DGGS cells at a given resolution.
    
    Args:
        res: Resolution level (0-6)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    num_cells = levels_specs[res]["n_row"] * levels_specs[res]["n_col"]
    
    # Get edge lengths in meters from constants
    edge_length_m = levels_specs[res]["x_length"]  # Assuming x_length and y_length are equal
    cell_area_m2 = edge_length_m * levels_specs[res]["y_length"]
    
    # Convert to requested unit
    if unit == "km":
        edge_length = edge_length_m / 1000.0
        cell_area = cell_area_m2 / (1000.0 ** 2)
    else:  # unit == "m"
        edge_length = edge_length_m
        cell_area = cell_area_m2
    
    return num_cells, edge_length, cell_area

def easestats(unit: str = "m"):
    """
    Generate statistics for EASE-DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing EASE-DGGS statistics with columns:
            - Resolution: Resolution level (0-6)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_{unit}: Average edge length in the given unit
            - Avg_Cell_Area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    min_res = 0
    max_res = 6
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells_at_res, edge_length, cell_area = ease_metrics(res, unit)            
        resolutions.append(res)
        num_cells_list.append(num_cells_at_res)
        avg_edge_lens.append(edge_length)
        avg_cell_areas.append(cell_area)
    
    # Create DataFrame
    # Build column labels with unit awareness
    avg_edge_len = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    avg_cell_area = f"avg_cell_area_{unit_area_label}"

    df = pd.DataFrame({
        'Resolution': resolutions,
        'Number_of_Cells': num_cells_list,
        avg_edge_len: avg_edge_lens,
        avg_cell_area: avg_cell_areas
    })
    
    return df


def easestats_cli(unit: str = "m"):
    """
    Command-line interface for generating EASE-DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default=None)
    args, _ = parser.parse_known_args()

    unit = args.unit if args.unit is not None else unit

    # Get the DataFrame
    df = easestats(unit=unit)
    
    # Display the DataFrame
    print(df.to_string(index=False))


def easeinspect(res):
    """
    Generate comprehensive inspection data for EASE-DGGS cells at a given resolution.
    
    This function creates a detailed analysis of EASE cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: EASE-DGGS resolution level (0-6)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing EASE cell inspection data with columns:
            - ease: EASE cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    ease_gpd = easegrid(res, output_format="gpd")
    ease_gpd['crossed'] = ease_gpd['geometry'].apply(check_crossing_geom)
    mean_area = ease_gpd['cell_area'].mean()
    # Calculate normalized area
    ease_gpd['norm_area'] = ease_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    ease_gpd['ipq'] = 4 * np.pi * ease_gpd['cell_area'] / (ease_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    ease_gpd['zsc'] = np.sqrt(4*np.pi*ease_gpd['cell_area'] - np.power(ease_gpd['cell_area'],2)/np.power(6378137,2))/ease_gpd['cell_perimeter']
    return ease_gpd

def ease_norm_area(ease_gpd):
    """
    Plot normalized area map for EASE cells.
    
    This function creates a visualization showing how EASE cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        ease_gpd: GeoDataFrame from easeinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = ease_gpd['norm_area'].min(), ease_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    ease_gpd = ease_gpd[~ease_gpd['crossed']] # remove cells that cross the dateline
    ease_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "EASE Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def ease_compactness(ease_gpd):
    """
    Plot IPQ compactness map for EASE cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of EASE cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.785 indicating more regular squares.
    
    Args:
        ease_gpd: GeoDataFrame from easeinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # For EASE (square cells), ideal IPQ is π/4 ≈ 0.785
    vmin, vmax, vcenter = VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    ease_gpd = ease_gpd[~ease_gpd['crossed']] # remove cells that cross the dateline
    ease_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "EASE IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def easeinspect_cli():
    """
    Command-line interface for EASE cell inspection.
    
    CLI options:
      -r, --resolution: EASE resolution level (0-6)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 0
    print(easeinspect(res))


if __name__ == "__main__":
    easestats_cli()
