"""
This module provides functions for generating statistics for ISEA4T DGGS cells.
"""
import platform
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
from vgrid.utils.constants import AUTHALIC_AREA, VMIN_TRI, VMAX_TRI, VCENTER_TRI
from vgrid.generator.isea4tgrid import isea4tgrid
from vgrid.utils.geometry import check_crossing_geom
import math

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    isea4t_dggs = Eaggr(Model.ISEA4T)


def isea4t_metrics(res, unit: str = "m"):
    """
    Calculate metrics for ISEA4T DGGS cells at a given resolution.
    
    Args:
        res: Resolution level (0-39)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    num_cells = 20 * (4**res)
    avg_cell_area_km2 = AUTHALIC_AREA / num_cells
    avg_edge_len_km = math.sqrt((4 * avg_cell_area_km2) / math.sqrt(3))
    
    # Convert to requested unit
    if unit == "m":
        avg_edge_len = avg_edge_len_km * 1000
        avg_cell_area = avg_cell_area_km2 * (10**6)
    else:  # unit == "km"
        avg_edge_len = avg_edge_len_km * 1000
        avg_cell_area = avg_cell_area_km2 * (10**6)
    
    return num_cells, avg_edge_len, avg_cell_area


def isea4tstats(unit: str = "m"):
    """
    Generate statistics for ISEA4T DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing ISEA4T DGGS statistics with columns:
            - Resolution: Resolution level (0-39)
            - Number_of_Cells: Number of cells at each resolution
            - Avg_Edge_Length_{unit}: Average edge length in the given unit
            - Avg_Cell_Area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    min_res = 0
    max_res = 39
    
    # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_len, avg_cell_area = isea4t_metrics(res, unit=unit)
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
        'number_of_cells': num_cells_list,
        avg_edge_len: avg_edge_lens,
        avg_cell_area: avg_cell_areas
    })
    
    return df


def isea4tstats_cli(unit: str = "m"):
    """
    Command-line interface for generating ISEA4T DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    if platform.system() == "Windows":
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default=None)
        args, _ = parser.parse_known_args()

        unit = args.unit if args.unit is not None else unit

        # Get the DataFrame
        df = isea4tstats(unit=unit)
        
        # Display the DataFrame
        print(df.to_string(index=False))


def isea4tinspect(res):
    """
    Generate comprehensive inspection data for ISEA4T DGGS cells at a given resolution.
    
    This function creates a detailed analysis of ISEA4T cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: ISEA4T resolution level (0-15)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing ISEA4T cell inspection data with columns:
            - isea4t: ISEA4T cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    if platform.system() != "Windows":
        raise RuntimeError("ISEA4T inspection is only supported on Windows due to EAGGR dependency")
    
    isea4t_gpd = isea4tgrid(res, output_format="gpd")
    isea4t_gpd['crossed'] = isea4t_gpd['geometry'].apply(check_crossing_geom)
    mean_area = isea4t_gpd['cell_area'].mean()
    # Calculate normalized area
    isea4t_gpd['norm_area'] = isea4t_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    isea4t_gpd['ipq'] = 4 * np.pi * isea4t_gpd['cell_area'] / (isea4t_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    isea4t_gpd['zsc'] = np.sqrt(4*np.pi*isea4t_gpd['cell_area'] - np.power(isea4t_gpd['cell_area'],2)/np.power(6378137,2))/isea4t_gpd['cell_perimeter']
    return isea4t_gpd

def isea4t_norm_area(isea4t_gpd):
    """
    Plot normalized area map for ISEA4T cells.
    
    This function creates a visualization showing how ISEA4T cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = isea4t_gpd['norm_area'].min(), isea4t_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    isea4t_gpd = isea4t_gpd[~isea4t_gpd['crossed']] # remove cells that cross the dateline
    isea4t_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "ISEA4T Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def isea4t_compactness(isea4t_gpd):
    """
    Plot IPQ compactness map for ISEA4T cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of ISEA4T cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.907 indicating more regular hexagons.
    
    Args:
        isea4t_gpd: GeoDataFrame from isea4tinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = isea4t_gpd['ipq'].min(), isea4t_gpd['ipq'].max(), np.mean([isea4t_gpd['ipq'].min(), isea4t_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_TRI, vcenter=VCENTER_TRI, vmax=VMAX_TRI)
    isea4t_gpd = isea4t_gpd[~isea4t_gpd['crossed']] # remove cells that cross the dateline
    isea4t_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "ISEA4T IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def isea4tinspect_cli():
    """
    Command-line interface for ISEA4T cell inspection.
    
    CLI options:
      -r, --resolution: ISEA4T resolution level (0-15)
    """
    if platform.system() != "Windows":
        print("ISEA4T inspection is only supported on Windows due to EAGGR dependency")
        return
        
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 0
    print(isea4tinspect(res))


if __name__ == "__main__":
    isea4tstats_cli()
