import argparse
import os
import json
from shapely.geometry import shape, Point
from collections import defaultdict, Counter
import statistics
from tqdm import tqdm
from vgrid.binning.bin_helper import get_default_stats_structure, append_stats_value
import pandas as pd
import geopandas as gpd
from vgrid.utils.io import process_input_data_bin, convert_to_output_format

def polygon_bin(polygon_data, point_data, stat, category=None, field_name=None, lat_col="lat", lon_col="lon", **kwargs):
    """
    Bins points into arbitrary polygon features and computes statistics.

    :param polygon_data: polygon data in various formats (file, DataFrame, GeoDataFrame, GeoJSON)
    :param point_data: point data in various formats (file, DataFrame, GeoDataFrame, GeoJSON)
    :param stat: statistic type (count, sum, mean, etc.)
    :param category: optional grouping field in properties
    :param field_name: field to use for statistical calculation (except for count)
    :return: GeoDataFrame with polygon features and stats
    """
    # Process input data
    polygon_gdf = process_input_data_bin(polygon_data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    point_gdf = process_input_data_bin(point_data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    
    # Preprocess polygons
    polygons = []
    for idx, row in polygon_gdf.iterrows():
        poly = row.geometry
        if not poly.is_valid:
            continue
        polygons.append((idx, row, poly))

    # Initialize stat structure per polygon ID
    polygon_bins = defaultdict(lambda: defaultdict(get_default_stats_structure))

    for _, point_row in tqdm(point_gdf.iterrows(), total=len(point_gdf), desc="Binning points into polygons"):
        point_geom = point_row.geometry
        props = point_row.to_dict()

        if not isinstance(point_geom, Point):
            continue

        for poly_idx, poly_row, poly_shape in polygons:
            if poly_shape.contains(point_geom):
                append_stats_value(
                    polygon_bins, poly_idx, props, stat, category, field_name
                )
                break  # one point belongs to only one polygon

    # Attach stats to polygon properties
    result_records = []
    for poly_idx, poly_row, poly_shape in polygons:
        categories = polygon_bins.get(poly_idx, {})
        row_data = poly_row.to_dict()
        row_data["geometry"] = poly_shape

        for cat, values in categories.items():
            key_prefix = "" if category is None else f"{cat}_"

            if stat == "count":
                row_data[f"{key_prefix}count"] = values["count"]
            elif stat == "sum":
                row_data[f"{key_prefix}sum"] = sum(values["sum"])
            elif stat == "min":
                row_data[f"{key_prefix}min"] = min(values["min"])
            elif stat == "max":
                row_data[f"{key_prefix}max"] = max(values["max"])
            elif stat == "mean":
                row_data[f"{key_prefix}mean"] = statistics.mean(values["mean"])
            elif stat == "median":
                row_data[f"{key_prefix}median"] = statistics.median(values["median"])
            elif stat == "std":
                row_data[f"{key_prefix}std"] = statistics.stdev(values["std"]) if len(values["std"]) > 1 else 0
            elif stat == "var":
                row_data[f"{key_prefix}var"] = statistics.variance(values["var"]) if len(values["var"]) > 1 else 0
            elif stat == "range":
                row_data[f"{key_prefix}range"] = max(values["range"]) - min(values["range"]) if values["range"] else 0
            elif stat == "minority":
                freq = Counter(values["values"])
                min_item = min(freq.items(), key=lambda x: x[1])[0] if freq else None
                row_data[f"{key_prefix}minority"] = min_item
            elif stat == "majority":
                freq = Counter(values["values"])
                max_item = max(freq.items(), key=lambda x: x[1])[0] if freq else None
                row_data[f"{key_prefix}majority"] = max_item
            elif stat == "variety":
                row_data[f"{key_prefix}variety"] = len(set(values["values"]))

        result_records.append(row_data)

    result_gdf = gpd.GeoDataFrame(result_records, geometry="geometry", crs="EPSG:4326")
    return result_gdf

def polygonbin(
    polygon_data,
    point_data,
    stat,
    category=None,
    field_name=None,
    output_format=None,
    **kwargs,
):
    if stat not in ["count", "min", "max", "sum", "mean", "median", "std", "var", "range", "minority", "majority", "variety"]:
        raise ValueError(f"Unsupported statistic: {stat}")
    if stat != "count" and not field_name:
        raise ValueError("A field_name is required for statistics other than 'count'")
    result_gdf = polygon_bin(polygon_data, point_data, stat, category, field_name, **kwargs)
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet"]
    output_name = None
    if output_format in file_formats:
        import os
        ext_map = {
            "csv": ".csv",
            "geojson": ".geojson",
            "shapefile": ".shp",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
        }
        ext = ext_map.get(output_format, "")
        if isinstance(point_data, str):
            base = os.path.splitext(os.path.basename(point_data))[0]
            output_name = f"{base}_polygonbin_{stat}{ext}"
        else:
            output_name = f"polygonbin_{stat}{ext}"
    return convert_to_output_format(result_gdf, output_format, output_name)

def polygonbin_cli():
    parser = argparse.ArgumentParser(description="Bin points into polygons and compute statistics")
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input point data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-p", "--polygon",
        type=str,
        required=True,
        help="Input polygon data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-stats",
        "--statistic",
        choices=[
            "count",
            "min",
            "max",
            "sum",
            "mean",
            "median",
            "std",
            "var",
            "range",
            "minority",
            "majority",
            "variety",
        ],
        required=True,
        help="Statistic option: choose from count, min, max, sum, mean, median, std, var, range, minority, majority, variety",
    )
    parser.add_argument(
        "-category",
        "--category",
        required=False,
        help="Optional category field for grouping",
    )
    parser.add_argument(
        "-field", "--field", dest="field_name", required=False, help="Field name for numeric values (required if stats != 'count')"
    )
    parser.add_argument(
        "-o", "--output", 
        required=False, 
        help="Output file path (optional, will auto-generate if not provided)"
    )
    parser.add_argument(
        "-f", "--output_format",
        required=False,
        default=None,
        choices=["geojson", "gpkg", "parquet", "csv", "shapefile"],
        help="Output output_format (default: None, returns GeoDataFrame)",
    )
    args = parser.parse_args()
    try:
        result = polygonbin(
            polygon_data=args.polygon,
            point_data=args.input,
            stat=args.statistic,
            category=args.category,
            field_name=args.field_name,
            output_format=args.output_format,
            output_path=args.output,
        )
        if isinstance(result, str):
            print(f"Output saved to {result}")      
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    polygonbin_cli()
