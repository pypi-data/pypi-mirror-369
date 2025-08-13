import os
import argparse
import csv
from tqdm import tqdm
import rasterio
import a5
import numpy as np
import math
from shapely.geometry import Polygon
from a5.core.cell_info import cell_area
from vgrid.utils.antimeridian import fix_polygon
from vgrid.utils.geometry import geodesic_dggs_metrics
from math import cos, radians
from vgrid.utils.io import validate_a5_resolution, convert_to_output_format

# Optional imports for additional output formats
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


def get_nearest_a5_resolution(raster_path):
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

    # Check resolutions from 0 to 29
    for res in range(30):
        avg_area = cell_area(res)
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


def raster2a5(raster_path, resolution=None, output_format=None):
    # Step 1: Determine the nearest a5 resolution if none is provided
    if resolution is None:
        resolution = get_nearest_a5_resolution(raster_path)
        print(f"Nearest a5 resolution determined: {resolution}")
    else:
        resolution = validate_a5_resolution(resolution)
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    a5_tokens = set()
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            a5_id = a5.lonlat_to_cell((lon, lat), resolution)
            a5_token = a5.bigint_to_hex(a5_id)
            a5_tokens.add(a5_token)

    # Build GeoDataFrame as the base
    properties = []
    for a5_token in tqdm(a5_tokens, desc="Building GeoDataFrame", unit=" cells"):
        try:
            a5_id = a5.hex_to_bigint(a5_token)
            cell_boundary = a5.cell_to_boundary(a5_id)
            cell_polygon = fix_polygon(Polygon(cell_boundary))
            num_edges = 5
            centroid_lat, centroid_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(cell_polygon, num_edges)
            col, row = ~transform * (centroid_lon, centroid_lat)
            if 0 <= col < width and 0 <= row < height:
                values = raster_data[:, int(row), int(col)]
                base_props = {
                    "a5": a5_token,
                    "resolution": resolution,
                    "center_lat": centroid_lat,
                    "center_lon": centroid_lon,
                    "avg_edge_len": avg_edge_len,
                    "cell_area": cell_area,
                    "cell_perimeter": cell_perimeter,
                    "geometry": cell_polygon,
                }
                band_properties = {f"band_{i + 1}": values[i] for i in range(band_count)}
                base_props.update(convert_numpy_types(band_properties))
                properties.append(base_props)
        except Exception as e:
            # Skip cells that can't be processed
            continue

    if not GEOPANDAS_AVAILABLE:
        if output_format is None or output_format.lower() == "gpd":
            raise ImportError("geopandas is required for GeoDataFrame output")
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = None
    if output_format is not None:
        ext_map = {
            "csv": f"{base_name}2a5.csv",
            "parquet": f"{base_name}2a5.parquet",
            "shapefile": f"{base_name}2a5.shp",
            "shp": f"{base_name}2a5.shp",
            "gpkg": f"{base_name}2a5.gpkg",
            "geopackage": f"{base_name}2a5.gpkg",
            "geojson": f"{base_name}2a5.geojson",
        }
        fmt = output_format.lower()
        output_name = ext_map.get(fmt)
    return convert_to_output_format(gdf, output_format, output_name)


def raster2a5_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to A5 DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help="Resolution [0..29]",
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

    args.resolution = validate_a5_resolution(args.resolution)

    result = raster2a5(raster, resolution, output_format)
    base_name = os.path.splitext(os.path.basename(raster))[0]

    # Handle different output formats for file saving
    if output_format.lower() == "csv":
        output_name = f"{base_name}2a5.csv"
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
    raster2a5_cli() 