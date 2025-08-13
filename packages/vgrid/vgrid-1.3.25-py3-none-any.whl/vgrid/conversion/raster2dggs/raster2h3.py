"""
Raster to H3 DGGS Conversion Module

This module provides functionality to convert raster data to H3 (Hierarchical Hexagonal Grid) 
Discrete Global Grid System (DGGS) format. It supports automatic resolution determination 
based on raster cell size and multiple output formats including GeoJSON, CSV, Parquet, 
Shapefile, and GeoPackage.

The module handles:
- Automatic H3 resolution selection based on raster pixel size
- Multi-band raster data processing
- Antimeridian crossing cell correction
- Various output formats for different use cases
- Command-line interface for batch processing

Key Functions:
    raster2h3: Main conversion function with multiple output format options
    get_nearest_h3_resolution: Automatically determines optimal H3 resolution
    raster2h3_cli: Command-line interface for the conversion process

Supported Output Formats:
    - None: Returns GeoPandas GeoDataFrame (default)
    - "gpd": Returns GeoPandas GeoDataFrame
    - "csv": Saves as CSV file
    - "geojson": Saves as GeoJSON file
    - "parquet": Saves as Parquet file
    - "shapefile"/"shp": Saves as Shapefile
    - "gpkg"/"geopackage": Saves as GeoPackage

Dependencies:
    - rasterio: For raster data reading
    - h3: For H3 grid operations
    - numpy: For numerical operations
    - shapely: For geometry operations
    - geopandas: For advanced geospatial data handling (optional)
    - tqdm: For progress bars
"""

import os
import argparse
import csv
from math import cos, radians
from tqdm import tqdm
import rasterio
import h3
import numpy as np
from shapely.geometry import Polygon
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import validate_h3_resolution, convert_to_output_format
from vgrid.conversion.dggs2geo.h32geo import h32geo
# Optional imports for additional output formats
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

def get_nearest_h3_resolution(raster_path):
    with rasterio.open(raster_path) as src:
        transform = src.transform
        crs = src.crs
        pixel_width = transform.a
        pixel_height = -transform.e
        cell_size = pixel_width * pixel_height

        if crs.is_geographic:
            # Latitude of the raster center
            center_latitude = (src.bounds.top + src.bounds.bottom) / 2
            # Convert degrees to meters
            meter_per_degree_lat = 111_320  # Roughly 1 degree latitude in meters
            meter_per_degree_lon = meter_per_degree_lat * cos(radians(center_latitude))

            pixel_width_m = pixel_width * meter_per_degree_lon
            pixel_height_m = pixel_height * meter_per_degree_lat
            cell_size = pixel_width_m * pixel_height_m

    nearest_resolution = None
    min_diff = float("inf")

    # Check resolutions from 0 to 15
    for res in range(16):
        avg_area = h3.average_hexagon_area(res, unit="m^2")
        diff = abs(avg_area - cell_size)
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return nearest_resolution


def convert_numpy_types(obj):
    """Recursively convert NumPy types to native Python types"""
    if isinstance(obj, np.generic):
        return obj.item()  # Convert numpy types like np.uint8 to native Python int
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    else:
        return obj


def raster2h3(raster_path, resolution=None, output_format=None):
    """
    Convert raster data to H3 DGGS format.
    
    Args:
        raster_path (str): Path to the raster file
        resolution (int, optional): H3 resolution [0..15]. If None, automatically determined
        output_format (str, optional): Output format. Options:
            - None: Returns GeoPandas GeoDataFrame (default)
            - "gpd": Returns GeoPandas GeoDataFrame
            - "csv": Returns CSV file path
            - "geojson": Returns GeoJSON file path
            - "geojson_dict": Returns GeoJSON FeatureCollection as Python dict
            - "parquet": Returns Parquet file path
            - "shapefile"/"shp": Returns Shapefile file path
            - "gpkg"/"geopackage": Returns GeoPackage file path
    Returns:
        Various formats based on output_format parameter
    Raises:
        ValueError: If resolution is not in valid range [0..15]
        ImportError: If required dependencies are not available for specific formats
    """
    # Step 1: Determine the nearest H3 resolution if none is provided
    if resolution is None:
        resolution = get_nearest_h3_resolution(raster_path)
        print(f"Nearest H3 resolution determined: {resolution}")
    else:
        resolution = validate_h3_resolution(resolution)

    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    h3_ids = set()
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            h3_id = h3.latlng_to_cell(lat, lon, resolution)
            h3_ids.add(h3_id)

    # Build GeoDataFrame as the base
    properties = []
    for h3_id in tqdm(h3_ids, desc="Building GeoDataFrame", unit=" cells"):
        centroid_lat, centroid_lon = h3.cell_to_latlng(h3_id)
        col, row = ~transform * (centroid_lon, centroid_lat)
        if 0 <= col < width and 0 <= row < height:
            values = raster_data[:, int(row), int(col)]
            cell_polygon = h32geo(h3_id)
            num_edges = 6
            if h3.is_pentagon(h3_id):
                num_edges = 5
            base_props = geodesic_dggs_to_geoseries(
                "h3", h3_id, resolution, cell_polygon, num_edges
            )
            band_properties = {f"band_{i + 1}": values[i] for i in range(band_count)}
            base_props.update(convert_numpy_types(band_properties))
            properties.append(base_props)
    if not GEOPANDAS_AVAILABLE:
        if output_format is None or output_format.lower() == "gpd":
            raise ImportError("geopandas is required for GeoDataFrame output")
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = None
    if output_format is not None:
        ext_map = {
            "csv": f"{base_name}2h3.csv",
            "parquet": f"{base_name}2h3.parquet",
            "shapefile": f"{base_name}2h3.shp",
            "shp": f"{base_name}2h3.shp",
            "gpkg": f"{base_name}2h3.gpkg",
            "geopackage": f"{base_name}2h3.gpkg",
            "geojson": f"{base_name}2h3.geojson",
        }
        fmt = output_format.lower()
        output_name = ext_map.get(fmt)
    return convert_to_output_format(gdf, output_format, output_name)


def raster2h3_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to H3 DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help="Resolution [0..15]",
    )

    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        required=False,
        default=None,
        choices=["geojson", "geojson_dict", "csv", "parquet", "shapefile", "shp", "gpkg", "geopackage"],
        help="Output format: geojson (file), geojson_dict (Python dict), csv, parquet, shapefile/shp, gpkg/geopackage. Default is csv.",
    )

    args = parser.parse_args()
    raster = args.raster
    resolution = args.resolution
    output_format = args.output_format
    
    # Set default output format to csv if none specified
    if output_format is None:
        output_format = "csv"

    if not os.path.exists(raster):
        print(f"Error: The file {raster} does not exist.")
        return
    
    # Validate resolution range if provided
    args.resolution = validate_h3_resolution(args.resolution)

    result = raster2h3(raster, resolution, output_format)
    base_name = os.path.splitext(os.path.basename(raster))[0]
    
    # Handle different output formats for file saving
    if output_format.lower() == "csv":
        # Save H3 IDs and band values as CSV file
        output_name = f"{base_name}2h3.csv"
        if result and len(result) > 0:
            fieldnames = list(result[0].keys())
            with open(output_name, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result)
        print(f"Output saved as {output_name}")
    
    # For formats that already save files (geojson, parquet, shapefile, gpkg)
    # result is already the file path, no need to save again
    elif output_format.lower() in ["geojson", "parquet", "shapefile", "shp", "gpkg", "geopackage"]:
        # File already saved by the function, result is the file path
        pass
    # For geojson_dict, print a summary
    elif output_format.lower() == "geojson_dict":
        if isinstance(result, dict) and "features" in result:
            print(f"GeoJSON dict generated with {len(result['features'])} features.")
        else:
            print("GeoJSON dict generated.")
if __name__ == "__main__":
    raster2h3_cli()
