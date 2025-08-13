"""
geohashcompact.py - Geohash Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding Geohash cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- geohashcompact: Compact a set of Geohash cells to their minimal covering set.
- geohashexpand: Expand (uncompact) a set of Geohash cells to a target resolution.
- geohashcompact_cli: Command-line interface for compaction.
- geohashexpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, vgrid.dggs.geohash, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from collections import defaultdict

from vgrid.conversion.dggs2geo.geohash2geo import geohash2geo
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import process_input_data_compact, convert_to_output_format
from vgrid.dggs import geohash

# --- Geohash Compaction/Expansion Logic ---
def get_geohash_resolution(geohash_id):
    """Get the resolution of a Geohash cell ID."""
    return len(geohash_id)

def geohash_compact(geohash_ids):
    """Compact a list of Geohash cell IDs to their minimal covering set."""
    geohash_ids = set(geohash_ids)  # Remove duplicates
    
    # Main loop for compaction
    while True:
        grouped_geohash_ids = defaultdict(set)
        
        # Group cells by their parent
        for geohash_id in geohash_ids:
            parent = geohash.geohash_parent(geohash_id)
            grouped_geohash_ids[parent].add(geohash_id)

        new_geohash_ids = set(geohash_ids)
        changed = False

        # Check if we can replace children with parent
        for parent, children in grouped_geohash_ids.items():
            parent_resolution = len(parent)
            # Generate the subcells for the parent at the next resolution
            childcells_at_next_res = set(
                childcell
                for childcell in geohash.geohash_children(parent, parent_resolution + 1)
            )

            # Check if the current children match the subcells at the next resolution
            if children == childcells_at_next_res:
                new_geohash_ids.difference_update(children)  # Remove children
                new_geohash_ids.add(parent)  # Add the parent
                changed = True  # A change occurred

        if not changed:
            break  # Stop if no more compaction is possible
        geohash_ids = new_geohash_ids  # Continue compacting

    return sorted(geohash_ids)  # Sorted for consistency

def geohashcompact(
    input_data,
    geohash_id=None,
    output_format=None,
):
    """Compact Geohash cells from input data."""
    if not geohash_id:
        geohash_id = "geohash"
    
    gdf = process_input_data_compact(input_data, geohash_id)
    geohash_ids = gdf[geohash_id].drop_duplicates().tolist()
    
    if not geohash_ids:
        print(f"No Geohash IDs found in <{geohash_id}> field.")
        return
    
    try:
        geohash_ids_compact = geohash_compact(geohash_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your Geohash ID field.")
    
    if not geohash_ids_compact:
        return None
    
    rows = []
    for geohash_id_compact in geohash_ids_compact:
        try:
            cell_polygon = geohash2geo(geohash_id_compact)
            cell_resolution = get_geohash_resolution(geohash_id_compact)
            row = graticule_dggs_to_geoseries(
                "geohash", geohash_id_compact, cell_resolution, cell_polygon
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    output_name = None
    if output_format in file_formats:
        ext_map = {
            "csv": ".csv",
            "geojson": ".geojson",
            "shapefile": ".shp",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "geoparquet": ".parquet",
        }
        ext = ext_map.get(output_format, "")
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_geohash_compacted{ext}"
        else:
            output_name = f"geohash_compacted{ext}"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def geohashcompact_cli():
    """Command-line interface for Geohash compaction."""
    parser = argparse.ArgumentParser(description="Geohash Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input Geohash (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="Geohash ID field")
    parser.add_argument("-f", "--output_format", type=str, default=None, help="Output format (None, csv, geojson, shapefile, gpd, geojson_dict, gpkg, geoparquet)")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format
    
    result = geohashcompact(
        input_data,
        geohash_id=cellid,
        output_format=output_format,
    )
    
    if output_format is None:
        print(result)
    elif output_format in ["csv", "geojson", "geojson_dict", "shapefile", "gpkg", "geoparquet", "parquet"]:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            ext_map = {
                "csv": ".csv",
                "geojson": ".geojson",
                "geojson_dict": ".geojson",
                "shapefile": ".shp",
                "gpkg": ".gpkg",
                "parquet": ".parquet",
                "geoparquet": ".parquet",
            }
            ext = ext_map.get(output_format, "")
            output = f"{base}_geohash_compacted{ext}"
        else:
            output = f"geohash_compacted{ext_map.get(output_format, '')}"
        print(f"Output written to {output}")
    elif output_format in ["gpd", "geopandas"]:
        print(result)
    else:
        print("Geohash compact completed.")

def geohash_expand(geohash_ids, resolution):
    """Expands a list of Geohash cells to the target resolution."""
    expand_cells = []
    for geohash_id in geohash_ids:
        cell_resolution = len(geohash_id)
        if cell_resolution >= resolution:
            expand_cells.append(geohash_id)
        else:
            expand_cells.extend(
                geohash.geohash_children(geohash_id, resolution)
            )  # Expand to the target level
    return expand_cells

def geohashexpand(
    input_data,
    resolution,
    geohash_id=None,
    output_format=None,
):
    """Expand Geohash cells to a target resolution."""
    if geohash_id is None:
        geohash_id = "geohash"
    
    gdf = process_input_data_compact(input_data, geohash_id)
    geohash_ids = gdf[geohash_id].drop_duplicates().tolist()
    
    if not geohash_ids:
        print(f"No Geohash IDs found in <{geohash_id}> field.")
        return
    
    try:
        max_res = max(len(geohash_id) for geohash_id in geohash_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        
        geohash_ids_expand = geohash_expand(geohash_ids, resolution)
    except Exception:
        raise Exception("Expand cells failed. Please check your Geohash ID field and resolution.")
    
    if not geohash_ids_expand:
        return None
    
    rows = []
    for geohash_id_expand in geohash_ids_expand:
        try:
            cell_polygon = geohash2geo(geohash_id_expand)
            cell_resolution = resolution
            row = graticule_dggs_to_geoseries(
                "geohash", geohash_id_expand, cell_resolution, cell_polygon
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    output_name = None
    if output_format in file_formats:
        ext_map = {
            "csv": ".csv",
            "geojson": ".geojson",
            "shapefile": ".shp",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "geoparquet": ".parquet",
        }
        ext = ext_map.get(output_format, "")
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_geohash_expanded{ext}"
        else:
            output_name = f"geohash_expanded{ext}"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def geohashexpand_cli():
    """Command-line interface for Geohash expansion."""
    parser = argparse.ArgumentParser(description="Geohash Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input Geohash (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target Geohash resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="Geohash ID field")
    parser.add_argument("-f", "--output_format", type=str, default=None, help="Output format (None, csv, geojson, shapefile, gpd, geojson_dict, gpkg, geoparquet)")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format
    
    result = geohashexpand(
        input_data,
        resolution,
        geohash_id=cellid,
        output_format=output_format,
    )
    
    if output_format is None:
        print(result)
    elif output_format in ["csv", "geojson", "geojson_dict", "shapefile", "gpkg", "geoparquet", "parquet"]:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            ext_map = {
                "csv": ".csv",
                "geojson": ".geojson",
                "geojson_dict": ".geojson",
                "shapefile": ".shp",
                "gpkg": ".gpkg",
                "parquet": ".parquet",
                "geoparquet": ".parquet",
            }
            ext = ext_map.get(output_format, "")
            output = f"{base}_geohash_expanded{ext}"
        else:
            output = f"geohash_expanded{ext_map.get(output_format, '')}"
        print(f"Output written to {output}")
    elif output_format in ["gpd", "geopandas"]:
        print(result)
    else:
        print("Geohash expand completed.") 