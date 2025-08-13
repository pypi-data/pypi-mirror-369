"""
Raster to rHEALPix DGGS Conversion Module

This module provides functionality to convert raster data to rHEALPix (Rectified Hierarchical
Equal Area isoLatitude Pixelization) Discrete Global Grid System (DGGS) output_format.

The module supports:
- Automatic resolution determination based on raster cell size
- Multi-band raster processing
- Output in both GeoJSON and CSV formats
- Command-line interface for batch processing

Key Functions:
- raster2rhealpix: Main conversion function
- get_nearest_rhealpix_resolution: Determines optimal rHEALPix resolution
- raster2rhealpix_cli: Command-line interface

The rHEALPix DGGS provides equal-area hierarchical tessellations of the sphere,
making it suitable for global raster data analysis and visualization.

"""

import os
import argparse
from tqdm import tqdm
import rasterio
import numpy as np
import csv
from vgrid.stats.rhealpixstats import rhealpix_metrics
from vgrid.utils.geometry import geodesic_dggs_metrics, rhealpix_cell_to_polygon
from vgrid.utils.io import validate_rhealpix_resolution, convert_to_output_format
from math import cos, radians
from vgrid.dggs.rhealpixdggs.dggs import RHEALPixDGGS
from vgrid.dggs.rhealpixdggs.ellipsoids import WGS84_ELLIPSOID
E = WGS84_ELLIPSOID
rhealpix_dggs = RHEALPixDGGS(ellipsoid=E, north_square=1, south_square=3, N_side=3)

# Optional imports for additional output formats
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

def get_nearest_rhealpix_resolution(raster_path):
    """
    Determine the nearest rHEALPix resolution based on the raster cell size.
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

    # Check resolutions from 0 to 15
    for res in range(16):
        _, _, avg_area = rhealpix_metrics(res)
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


def raster2rhealpix(raster_path, resolution=None, output_format=None):
    """
    Convert raster data to rHEALPix DGGS.
    """
    # Step 1: Determine the nearest rhealpix resolution if none is provided
    if resolution is None:
        resolution = get_nearest_rhealpix_resolution(raster_path)
        print(f"Nearest rhealpix resolution determined: {resolution}")
    else:
        resolution = validate_rhealpix_resolution(resolution)
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    rhealpix_ids = set()
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            point = (lon, lat)
            rhealpix_cell = rhealpix_dggs.cell_from_point(
                resolution, point, plane=False
            )
            rhealpix_ids.add(str(rhealpix_cell))

    # Build GeoDataFrame as the base
    properties = []
    for rhealpix_id in tqdm(rhealpix_ids, desc="Building GeoDataFrame", unit=" cells"):
        rhealpix_uids = (rhealpix_id[0],) + tuple(map(int, rhealpix_id[1:]))
        rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
        cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
        num_edges = 4
        if rhealpix_cell.ellipsoidal_shape() == "dart":
            num_edges = 3
        centroid_lat, centroid_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(
            cell_polygon, num_edges
        )
        col, row = ~transform * (centroid_lon, centroid_lat)
        if 0 <= col < width and 0 <= row < height:
            values = raster_data[:, int(row), int(col)]
            base_props = {
                "rhealpix": rhealpix_id,
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
    if not GEOPANDAS_AVAILABLE:
        if output_format is None or output_format.lower() == "gpd":
            raise ImportError("geopandas is required for GeoDataFrame output")
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = None
    if output_format is not None:
        ext_map = {
            "csv": f"{base_name}2rhealpix.csv",
            "parquet": f"{base_name}2rhealpix.parquet",
            "shapefile": f"{base_name}2rhealpix.shp",
            "shp": f"{base_name}2rhealpix.shp",
            "gpkg": f"{base_name}2rhealpix.gpkg",
            "geopackage": f"{base_name}2rhealpix.gpkg",
            "geojson": f"{base_name}2rhealpix.geojson",
        }
        fmt = output_format.lower()
        output_name = ext_map.get(fmt)
    return convert_to_output_format(gdf, output_format, output_name)


def raster2rhealpix_cli():
    """Command line interface for raster2rhealpix"""
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to rHEALPix DGGS"
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


    # Set default output format to csv if none specified
    output_format = args.output_format
    if output_format is None:
        output_format = "csv"

    if not os.path.exists(args.raster):
        raise FileNotFoundError(f"The file {args.raster} does not exist.")

    args.resolution = validate_rhealpix_resolution(args.resolution)

    result = raster2rhealpix(args.raster, args.resolution, output_format)
    base_name = os.path.splitext(os.path.basename(args.raster))[0]

    # Handle different output formats for file saving
    if output_format.lower() == "csv":
        output_name = f"{base_name}2rhealpix.csv"
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
    raster2rhealpix_cli()
