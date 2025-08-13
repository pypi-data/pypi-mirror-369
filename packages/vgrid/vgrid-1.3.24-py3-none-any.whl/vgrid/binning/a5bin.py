import argparse
import statistics
from collections import defaultdict, Counter
from tqdm import tqdm
import geopandas as gpd
from vgrid.binning.bin_helper import get_default_stats_structure, append_stats_value
from vgrid.conversion.latlon2dggs import latlon2a5
from vgrid.conversion.dggs2geo.a52geo import a52geo
from vgrid.utils.io import process_input_data_bin, convert_to_output_format


def a5_bin(data, resolution, stats, category=None, numeric_field=None, lat_col="lat", lon_col="lon", **kwargs):
    """
    Bin point data into A5 grid cells and compute statistics.
    Args:
        data: Input data in various formats (DataFrame, GeoDataFrame, file path, etc.)
        resolution (int): A5 resolution level [0..29]
        stats (str): Statistic to compute
        category (str, optional): Category field for grouping
        numeric_field (str, optional): Numeric field to compute statistics (required if stats != 'count')
        lat_col (str): Name of latitude column for CSV/DataFrame (default 'lat')
        lon_col (str): Name of longitude column for CSV/DataFrame (default 'lon')
        **kwargs: Additional arguments for pandas/geopandas read functions
    Returns:
        pd.DataFrame: DataFrame with A5 cell stats and geometry
    """
    # Process input data to GeoDataFrame
    gdf = process_input_data_bin(data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    a5_bins = defaultdict(lambda: defaultdict(get_default_stats_structure))

    for _, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Binning points"):
        geom = row.geometry
        props = row.to_dict()
        if geom is None:
            continue
        if geom.geom_type == "Point":
            a5_hex = latlon2a5(geom.y, geom.x, resolution)
            append_stats_value(a5_bins, a5_hex, props, stats, category, numeric_field)
        elif geom.geom_type == "MultiPoint":
            for p in geom.geoms:
                a5_hex = latlon2a5(p.y, p.x, resolution)
                append_stats_value(a5_bins, a5_hex, props, stats, category, numeric_field)

    records = []
    for a5_hex, categories in a5_bins.items():
        try:
            # Convert hex string to bigint for A5 operations
            cell_polygon = a52geo(a5_hex)            
            if not cell_polygon.is_valid:
                continue
                
            row_data = {
                "a5": a5_hex,
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
        except Exception as e:
            # Skip cells that can't be processed
            continue
            
    result_gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
    return result_gdf

def a5bin(
    data,
    resolution,
    stats,
    category=None,
    numeric_field=None,
    output_format=None,
    **kwargs,
):
    """
    Bin point data into A5 grid cells and compute statistics from various input formats.

    This is the main function that handles binning of point data to A5 grid cells.
    It supports multiple input formats including file paths, URLs, DataFrames, GeoDataFrames,
    GeoJSON dictionaries, and lists of features.

    Args:
        data: Input data in one of the following formats:
            - File path (str): Path to vector file (shapefile, GeoJSON, etc.)
            - URL (str): URL to vector data
            - pandas.DataFrame: DataFrame with geometry column
            - geopandas.GeoDataFrame: GeoDataFrame
            - dict: GeoJSON dictionary
            - list: List of GeoJSON feature dictionaries
        resolution (int): A5 resolution level [0..29] (0=coarsest, 29=finest)
        stats (str): Statistic to compute:      
            - 'count': Count of points in each cell
            - 'sum': Sum of field values
            - 'min': Minimum field value
            - 'max': Maximum field value
            - 'mean': Mean field value
            - 'median': Median field value
            - 'std': Standard deviation of field values
            - 'var': Variance of field values
            - 'range': Range of field values
            - 'minority': Least frequent value
            - 'majority': Most frequent value
            - 'variety': Number of unique values
        category (str, optional): Category field for grouping statistics
        numeric_field (str, optional): Numeric field to compute statistics (required if stats != 'count')
        output_format (str, optional): Output output_format ('geojson', 'gpkg', 'parquet', 'csv', 'shapefile')
        output_path (str, optional): Output file path. If None, uses default naming
        **kwargs: Additional arguments passed to geopandas read functions

    Returns:
        dict or str: Output in the specified output_format. Returns file path if output_path is specified,
        otherwise returns the data directly.

    Raises:
        ValueError: If input data type is not supported or conversion fails
        TypeError: If resolution is not an integer

    Example:
        >>> # Bin from file
        >>> result = a5bin("cities.shp", 10, "count")
        
        >>> # Bin from GeoDataFrame
        >>> import geopandas as gpd
        >>> gdf = gpd.read_file("cities.shp")
        >>> result = a5bin(gdf, 10, "mean", numeric_field="population")
        
        >>> # Bin from GeoJSON dict
        >>> geojson = {"type": "FeatureCollection", "features": [...]}
        >>> result = a5bin(geojson, 10, "sum", numeric_field="value")
    """
    if not isinstance(resolution, int):
        raise TypeError(f"Resolution must be an integer, got {type(resolution).__name__}")

    if resolution < 0 or resolution > 29:
        raise ValueError(f"Resolution must be in range [0..29], got {resolution}")

    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")

    # Process input data and bin
    result_gdf = a5_bin(data, resolution, stats, category, numeric_field, **kwargs)
    
    # Convert to output output_format if specified
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
            output_name = f"{base}_a5bin_{resolution}{ext}"
        else:
            output_name = f"a5bin_{resolution}{ext}"
    return convert_to_output_format(result_gdf, output_format, output_name)


def a5bin_cli():
    """
    Command-line interface for a5bin conversion.

    This function provides a command-line interface for binning point data to A5 grid cells.
    It parses command-line arguments and calls the main a5bin function.

    Usage:
        python a5bin.py -i input.shp -r 10 -stats count -f geojson -o output.geojson

    Arguments:
        -i, --input: Input file path, URL, or other vector file formats
        -r, --resolution: A5 resolution [0..29]
        -stats, --statistics: Statistic to compute (count, min, max, sum, mean, median, std, var, range, minority, majority, variety)
        -category, --category: Optional category field for grouping
        -field, --field: Numeric field to compute statistics (required if stats != 'count')
        -o, --output: Output file path (optional, will auto-generate if not provided)
        -f, --output_format: Output output_format (geojson, gpkg, parquet, csv, shapefile)

    Example:
        >>> # Bin shapefile to A5 cells at resolution 10 with count statistics
        >>> # python a5bin.py -i cities.shp -r 10 -stats count -f geojson
    """
    parser = argparse.ArgumentParser(description="Binning point data to A5 DGGS")
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
        help="Resolution of the grid [0..29]",
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
        # Use the a5bin function
        result = a5bin(
            data=args.input,
            resolution=args.resolution,
            stats=args.statistics,
            category=args.category,
            numeric_field=args.numeric_field,
            output_format=args.output_format,
            output_path=args.output,
        )
        # Print notification is now handled in convert_to_output_format
    except Exception as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    a5bin_cli() 