"""
h3compact.py - H3 Cell Compaction and Expansion Utilities

This module provides functions and command-line interfaces for compacting and expanding (uncompacting) H3 cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- h3compact: Compact a set of H3 cells to their minimal covering set.
- h3expand: Expand (uncompact) H3 cells to a specified resolution.
- h3compact_cli: Command-line interface for compaction.
- h3expand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, h3, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
import h3
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import process_input_data_compact, convert_to_output_format, validate_h3_resolution
from vgrid.conversion.dggs2geo.h32geo import h32geo     

def h3compact(
    input_data,
    h3_id=None,
    output_format=None,
):
    """
    Compact H3 cells. Flexible input/output format.
    input_data: file path, URL, dict, GeoDataFrame, or list of cell IDs
    output_format: None, 'csv', 'geojson', 'shapefile', 'gpd', 'geojson_dict', 'gpkg', 'geoparquet'
    Output is always written to the current directory if file-based.
    """
    if h3_id is None:
        h3_id = "h3"
    gdf = process_input_data_compact(input_data, h3_id)
    h3_ids = gdf[h3_id].drop_duplicates().tolist()
    if not h3_ids:
        print(f"No H3 IDs found in <{h3_id}> field.")
        return
    try:
        h3_ids_compact = h3.compact_cells(h3_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your H3 ID field.")
    if not h3_ids_compact:
        return None
    # Build output GeoDataFrame
    rows = []
    for h3_id_compact in h3_ids_compact:        
        try:
            cell_polygon = h32geo(h3_id_compact)
            cell_resolution = h3.get_resolution(h3_id_compact)
            num_edges = 6
            if h3.is_pentagon(h3_id_compact):
                num_edges = 5
            row = geodesic_dggs_to_geoseries(
                "h3", h3_id_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    # If output_format is file-based, set ouput_name as just the filename in current directory
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    ouput_name = None
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
            ouput_name = f"{base}_h3_compacted{ext}"
        else:
            ouput_name = f"h3_compacted{ext}"

    return convert_to_output_format(out_gdf, output_format, ouput_name)


def h3compact_cli():
    """
    Command-line interface for h3compact with flexible input/output.
    """
    parser = argparse.ArgumentParser(description="H3 Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input H3 (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="H3 ID field")
    parser.add_argument("-f", "--output_format", type=str, default=None, help="Output format (None, csv, geojson, shapefile, gpd, geojson_dict, gpkg, geoparquet)")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format

    result = h3compact(
        input_data,
        h3_id=cellid,
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
            output = f"{base}_h3_compacted{ext}"
        else:
            output = f"h3_compacted{ext_map.get(output_format, '')}"
        print(f"Output written to {output}")
    elif output_format in ["gpd", "geopandas"]:
        print(result)
    else:
        print("H3 compact completed.")


def h3expand(
    input_data,
    resolution,
    h3_id=None,
    output_format=None,
):
    """
    Expand (uncompact) H3 cells to a target resolution. Flexible input/output format.
    input_data: file path, URL, dict, GeoDataFrame, or list of cell IDs
    resolution: target H3 resolution (int)
    output_format: None, 'csv', 'geojson', 'shapefile', 'gpd', 'geojson_dict', 'gpkg', 'parquet', 'geoparquet'
    Output is always written to the current directory if file-based.
    """
    if h3_id is None:
        h3_id = "h3"
    resolution = validate_h3_resolution(resolution)
    gdf = process_input_data_compact(input_data, h3_id)
    h3_ids = gdf[h3_id].drop_duplicates().tolist()
    if not h3_ids:
        print(f"No H3 IDs found in <{h3_id}> field.")
        return
    try:
        max_res = max(h3.get_resolution(hid) for hid in h3_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        h3_ids_expand = h3.uncompact_cells(h3_ids, resolution)
    except Exception:
        raise Exception("Expand cells failed. Please check your H3 ID field and resolution.")
    if not h3_ids_expand:
        return None
    # Build output GeoDataFrame
    rows = []
    for h3_id_expand in h3_ids_expand:
        try:
            cell_polygon = h32geo(h3_id_expand)
            cell_resolution = h3.get_resolution(h3_id_expand)
            num_edges = 6
            if h3.is_pentagon(h3_id_expand):
                num_edges = 5
            row = geodesic_dggs_to_geoseries(
                "h3", h3_id_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    # If output_format is file-based, set ouput_name as just the filename in current directory
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    ouput_name = None
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
            ouput_name = f"{base}_h3_expanded{ext}"
        else:
            ouput_name = f"h3_expanded{ext}"

    return convert_to_output_format(out_gdf, output_format, ouput_name)


def h3expand_cli():
    """
    Command-line interface for h3expand with flexible input/output.
    """
    parser = argparse.ArgumentParser(description="H3 Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input H3 (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target H3 resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="H3 ID field")
    parser.add_argument("-f", "--output_format", type=str, default=None, help="Output format (None, csv, geojson, shapefile, gpd, geojson_dict, gpkg, geoparquet)")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format

    result = h3expand(
        input_data,
        resolution,
        h3_id=cellid,
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
            output = f"{base}_h3_expanded{ext}"
        else:
            output = f"h3_expanded{ext_map.get(output_format, '')}"
        print(f"Output written to {output}")
    elif output_format in ["gpd", "geopandas"]:
        print(result)
    else:
        print("H3 expand completed.") 