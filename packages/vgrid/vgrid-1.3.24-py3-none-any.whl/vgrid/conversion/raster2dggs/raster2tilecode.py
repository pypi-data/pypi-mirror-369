"""
Raster to Tilecode DGGS Grid Conversion Module
"""

import os
import argparse
import csv
import re
from math import cos, radians
import numpy as np
from tqdm import tqdm
import rasterio
from shapely.geometry import Polygon
from vgrid.dggs import tilecode, mercantile
from vgrid.stats.tilecodestats import tilecode_metrics
from vgrid.utils.io import validate_tilecode_resolution, convert_to_output_format

# Optional imports for additional output formats
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


def get_nearest_tilecode_resolution(raster_path):
    """
    Get the nearest Tilecode resolution for a given raster path
    """
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

    # Check resolutions from 0 to 26
    for res in range(27):
        _, _, avg_area = tilecode_metrics(res)
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


def raster2tilecode(raster_path, resolution=None, output_format=None):
    """Convert raster to tilecode output_format

    Args:
        raster_path (str): Path to input raster file
        resolution (int, optional): Tilecode resolution level [0-26]. If None, will be determined automatically
        output_format (str, optional): Output output_format, see supported formats

    Returns:
        Various formats based on output_format parameter
    """
    # Step 1: Determine the nearest tilecode resolution if none is provided
    if resolution is None:
        resolution = get_nearest_tilecode_resolution(raster_path)
        print(f"Nearest tilecode resolution determined: {resolution}")
    else:
        resolution = validate_tilecode_resolution(resolution)
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    tilecode_ids = set()

    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            tilecode_id = tilecode.latlon2tilecode(lat, lon, resolution)
            tilecode_ids.add(tilecode_id)

    # Sample the raster values at the centroids of the tilecode cells
    tilecode_data = []

    for tilecode_id in tqdm(tilecode_ids, desc="Resampling", unit=" cells"):
        # Get the centroid of the tilecode cell
        centroid_lat, centroid_lon = tilecode.tilecode2latlon(tilecode_id)

        # Sample the raster values at the centroid (lat, lon)
        col, row = ~transform * (centroid_lon, centroid_lat)

        if 0 <= col < width and 0 <= row < height:
            # Get the values for all bands at this centroid
            values = raster_data[:, int(row), int(col)]
            tilecode_data.append(
                {
                    "tilecode": tilecode_id,
                    **{
                        f"band_{i + 1}": values[i] for i in range(band_count)
                    },
                }
            )

    # Always convert to GeoDataFrame for output
    if not GEOPANDAS_AVAILABLE and (output_format is None or output_format.lower() in ["gpd", "parquet", "shapefile", "shp", "gpkg", "geopackage", "geojson"]):
        raise ImportError("geopandas is required for this output format")
    geometries = []
    properties = []
    for data in tqdm(tilecode_data, desc="Converting to GeoDataFrame", unit=" cells"):
        tilecode_id = data["tilecode"]
        match = re.match(r"z(\d+)x(\d+)y(\d+)", tilecode_id)
        if match:
            z = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            bounds = mercantile.bounds(x, y, z)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                cell_polygon = Polygon([
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ])
                geometries.append(cell_polygon)
                props = {"tilecode": tilecode_id}
                props.update({f"band_{i + 1}": data[f"band_{i + 1}"] for i in range(band_count)})
                properties.append(convert_numpy_types(props))
    gdf = gpd.GeoDataFrame(properties, geometry=geometries, crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = None
    if output_format is not None:
        ext_map = {
            "csv": f"{base_name}2tilecode.csv",
            "parquet": f"{base_name}2tilecode.parquet",
            "shapefile": f"{base_name}2tilecode.shp",
            "shp": f"{base_name}2tilecode.shp",
            "gpkg": f"{base_name}2tilecode.gpkg",
            "geopackage": f"{base_name}2tilecode.gpkg",
            "geojson": f"{base_name}2tilecode.geojson",
        }
        fmt = output_format.lower()
        output_name = ext_map.get(fmt)
    return convert_to_output_format(gdf, output_format, output_name)


def raster2tilecode_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to Tilecode DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help="Resolution [0..26]",
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

    args.resolution = validate_tilecode_resolution(args.resolution)

    result = raster2tilecode(raster, resolution, output_format)
    base_name = os.path.splitext(os.path.basename(raster))[0]

    # Handle different output formats for file saving
    if output_format.lower() == "csv":
        output_name = f"{base_name}2tilecode.csv"
        if result and len(result) > 0:
            fieldnames = list(result[0].keys())
            with open(output_name, "w", newline="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result)
        print(f"Output saved as {output_name}")
    elif output_format.lower() in ["geojson", "parquet", "shapefile", "shp", "gpkg", "geopackage"]:
        pass
    elif output_format.lower() == "geojson_dict":
        if isinstance(result, dict) and "features" in result:
            print(f"GeoJSON dict generated with {len(result['features'])} features.")
        else:
            print("GeoJSON dict generated.")

if __name__ == "__main__":
    raster2tilecode_cli()
