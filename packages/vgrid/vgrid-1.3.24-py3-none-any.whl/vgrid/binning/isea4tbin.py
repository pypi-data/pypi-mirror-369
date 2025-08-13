import platform
import argparse
import os
import json
import statistics
from collections import defaultdict, Counter
from shapely.geometry import Point, Polygon
from shapely.wkt import loads
from tqdm import tqdm
import pandas as pd
import geopandas as gpd
from vgrid.binning.bin_helper import get_default_stats_structure, append_stats_value
from vgrid.utils.io import process_input_data_bin, convert_to_output_format

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.conversion.latlon2dggs import latlon2isea4t
    from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo
    isea4t_dggs = Eaggr(Model.ISEA4T)

def isea4t_bin(data, resolution, stats, category=None, numeric_field=None, lat_col="lat", lon_col="lon", **kwargs):
    if platform.system() != "Windows":
        raise RuntimeError("ISEA4T binning is only supported on Windows due to EAGGR dependency")
    
    gdf = process_input_data_bin(data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    isea4t_bins = defaultdict(lambda: defaultdict(get_default_stats_structure))
    
    for _, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Binning points"):
        geom = row.geometry
        props = row.to_dict()
        if geom is None:
            continue
        if geom.geom_type == "Point":
            isea4t_id = latlon2isea4t(geom.y, geom.x, resolution)
            append_stats_value(isea4t_bins, isea4t_id, props, stats, category, numeric_field)
        elif geom.geom_type == "MultiPoint":
            for p in geom.geoms:
                isea4t_id = latlon2isea4t(p.y, p.x, resolution)
                append_stats_value(isea4t_bins, isea4t_id, props, stats, category, numeric_field)
    
    records = []
    for isea4t_id, categories in isea4t_bins.items():
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3

        if not cell_polygon.is_valid:
            continue

        row_data = {
            "isea4t": isea4t_id,
            "geometry": cell_polygon,
            "resolution": resolution,
        }
        
        for cat, values in categories.items():
            key_prefix = "" if category is None else f"{cat}_"
            if stats == "count":
                row_data[f"{key_prefix}count"] = values["count"]
            elif stats == "sum":
                row_data[f"{key_prefix}sum"] = sum(values["sum"])
            elif stats == "min":
                row_data[f"{key_prefix}min"] = min(values["min"])
            elif stats == "max":
                row_data[f"{key_prefix}max"] = max(values["max"])
            elif stats == "mean":
                row_data[f"{key_prefix}mean"] = statistics.mean(values["mean"])
            elif stats == "median":
                row_data[f"{key_prefix}median"] = statistics.median(values["median"])
            elif stats == "std":
                row_data[f"{key_prefix}std"] = statistics.stdev(values["std"]) if len(values["std"]) > 1 else 0
            elif stats == "var":
                row_data[f"{key_prefix}var"] = statistics.variance(values["var"]) if len(values["var"]) > 1 else 0
            elif stats == "range":
                row_data[f"{key_prefix}range"] = max(values["range"]) - min(values["range"]) if values["range"] else 0
            elif stats == "minority":
                freq = Counter(values["values"])
                min_item = min(freq.items(), key=lambda x: x[1])[0] if freq else None
                row_data[f"{key_prefix}minority"] = min_item
            elif stats == "majority":
                freq = Counter(values["values"])
                max_item = max(freq.items(), key=lambda x: x[1])[0] if freq else None
                row_data[f"{key_prefix}majority"] = max_item
            elif stats == "variety":
                row_data[f"{key_prefix}variety"] = len(set(values["values"]))
        
        records.append(row_data)
    
    result_gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
    return result_gdf


def isea4tbin(
    data,
    resolution,
    stats,
    category=None,
    numeric_field=None,
    output_format=None,
    **kwargs,
):
    import platform
    if platform.system() != "Windows":
        raise RuntimeError("ISEA4T binning is only supported on Windows due to EAGGR dependency")
    if not isinstance(resolution, int):
        raise TypeError(f"Resolution must be an integer, got {type(resolution).__name__}")
    if resolution < 0 or resolution > 25:
        raise ValueError(f"Resolution must be in range [0..25], got {resolution}")
    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")
    result_gdf = isea4t_bin(data, resolution, stats, category, numeric_field, **kwargs)
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
        if isinstance(data, str):
            base = os.path.splitext(os.path.basename(data))[0]
            output_name = f"{base}_isea4tbin_{resolution}{ext}"
        else:
            output_name = f"isea4tbin_{resolution}{ext}"
    return convert_to_output_format(result_gdf, output_format, output_name)


def isea4tbin_cli():
    parser = argparse.ArgumentParser(description="Binning point data to ISEA4T DGGS")
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        default=13,
        help="Resolution of the grid [0..25]",
    )
    parser.add_argument(
        "-stats",
        "--statistics",
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
        help="Statistic option",
    )
    parser.add_argument(
        "-category",
        "--category",
        required=False,
        help="Optional category field for grouping",
    )
    parser.add_argument(
        "-field", "--field", dest="numeric_field", required=False, help="Numeric field to compute statistics (required if stats != 'count')"
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
        result = isea4tbin(
            data=args.input,
            resolution=args.resolution,
            stats=args.statistics,
            category=args.category,
            numeric_field=args.numeric_field,
            output_format=args.output_format,
            output_path=args.output,
        )
        if isinstance(result, str):
            print(f"Output saved to {result}")      
    except Exception as e:
        print(f"Error: {str(e)}")
        return


def main():
    isea4tbin_cli()


if __name__ == "__main__":
    main()
