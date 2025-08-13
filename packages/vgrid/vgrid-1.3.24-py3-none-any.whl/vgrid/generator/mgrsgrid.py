
"""
MGRS Grid Generator Module.

This module provides functionality to generate Military Grid Reference System (MGRS)
Discrete Global Grid System (DGGS) grids. MGRS is a geocoordinate standard used
by NATO militaries for locating points on Earth.

The module supports:
- Generation of MGRS grids for specific Grid Zone Designators (GZD)
- Multiple output formats (GeoJSON, CSV, Shapefile, GeoPackage, Parquet)
- Resolution levels from 0 to 5
- UTM coordinate system transformations

Key Functions:
- mgrs_grid(): Creates MGRS grid cells for a given GZD and resolution
- convert_mgrsgrid_output_format(): Converts grid data to various output formats
- mgrsgrid_cli(): Command-line interface for grid generation
"""

import argparse
import json
import re
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import shape, Polygon
from shapely.ops import transform
from pyproj import CRS, Transformer
from tqdm import tqdm
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import validate_mgrs_resolution, convert_to_output_format
from vgrid.dggs import mgrs


def is_valid_gzd(gzd):
    """Check if a Grid Zone Designator (GZD) is valid."""
    pattern = r"^(?:0[1-9]|[1-5][0-9]|60)[C-HJ-NP-X]$"
    return bool(re.match(pattern, gzd))


def mgrs_grid(gzd, resolution): 
    resolution = validate_mgrs_resolution(resolution)   
    # Reference: https://www.maptools.com/tutorials/utm/details
    cell_size = 100_000 // (10**resolution)
    north_bands = "NPQRSTUVWX"
    south_bands = "MLKJHGFEDC"
    band_distance = 111_132 * 8
    gzd_band = gzd[2]

    if gzd_band >= "N":  # North Hemesphere
        epsg_code = int("326" + gzd[:2])
        min_x, min_y, max_x, max_y = 100000, 0, 900000, 9500000  # for the North
        north_band_idx = north_bands.index(gzd_band)
        max_y = band_distance * (north_band_idx + 1)
        if gzd_band == "X":
            max_y += band_distance  # band X = 12 deggrees instead of 8 degrees

    else:  # South Hemesphere
        epsg_code = int("327" + gzd[:2])
        min_x, min_y, max_x, max_y = 100000, 0, 900000, 10000000  # for the South
        south_band_idx = south_bands.index(gzd_band)
        max_y = band_distance * (south_band_idx + 1)

    utm_crs = CRS.from_epsg(epsg_code)
    wgs84_crs = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True).transform

    gzd_json_path = os.path.join(os.path.dirname(__file__), "gzd.geojson")
    with open(gzd_json_path, encoding="utf-8") as f:
        gzd_data = json.load(f)

    gzd_features = gzd_data["features"]
    gzd_feature = [
        feature for feature in gzd_features if feature["properties"].get("gzd") == gzd
    ][0]
    gzd_geom = shape(gzd_feature["geometry"])

    # Create grid polygons
    mgrs_records = []
    x_coords = np.arange(min_x, max_x, cell_size)
    y_coords = np.arange(min_y, max_y, cell_size)
    num_cells = len(x_coords) * len(y_coords)
    with tqdm(total=num_cells, desc="Generating MGRS DGGS", unit=" cells") as pbar:
        for x in x_coords:
            for y in y_coords:
                cell_polygon_utm = Polygon(
                    [
                        (x, y),
                        (x + cell_size, y),
                        (x + cell_size, y + cell_size),
                        (x, y + cell_size),
                        (x, y),  # Close the polygon
                    ]
                )
                cell_polygon = transform(transformer, cell_polygon_utm)

                if cell_polygon.intersects(gzd_geom):
                    centroid_lat, centroid_lon = (
                        cell_polygon.centroid.y,
                        cell_polygon.centroid.x,
                    )
                    mgrs_id = mgrs.toMgrs(centroid_lat, centroid_lon, resolution)
                    mgrs_record = graticule_dggs_to_geoseries(
                        "mgrs", mgrs_id, resolution, cell_polygon
                    )
                    # clip inside GZD:
                    if not gzd_geom.contains(cell_polygon):
                        intersected_polygon = cell_polygon.intersection(gzd_geom)
                        if intersected_polygon:
                            intersected_centroid_lat, intersected_centroid_lon = (
                                intersected_polygon.centroid.y,
                                intersected_polygon.centroid.x,
                            )
                            interescted_mgrs_id = mgrs.toMgrs(
                                intersected_centroid_lat,
                                intersected_centroid_lon,
                                resolution,
                            )
                            mgrs_record = graticule_dggs_to_geoseries(
                                "mgrs",
                                interescted_mgrs_id,
                                resolution,
                                intersected_polygon,
                            )
                    mgrs_records.append(mgrs_record)
                pbar.update(1)
    return gpd.GeoDataFrame(mgrs_records, geometry="geometry", crs="EPSG:4326")


def mgrsgrid(gzd, resolution, output_format=None):
    """
    Generate MGRS grid for pure Python usage.

    Args:
        gzd (str): Grid Zone Designator, e.g. '48P'.
        resolution (int): MGRS resolution [0..5].
        output_format (str, optional): Output format ('geojson', 'csv', 'geo', 'gpd', 'shapefile', 'gpkg', 'parquet', or None for list of MGRS IDs). Defaults to None.

    Returns:
        Depends on output_format: list, GeoDataFrame, file path, or GeoJSON FeatureCollection.
    """
    if not is_valid_gzd(gzd):
        raise ValueError("Invalid GZD. Please input a valid GZD.")
    gdf = mgrs_grid(gzd, resolution)
   
    base_name = f"mgrs_grid_{resolution}"
    if output_format is None:
        return gdf.to_dict(orient="records")
    elif output_format in ["gpd", "geo"]:
        return gdf
    elif output_format == "geojson_dict":
        return gdf.__geo_interface__
    elif output_format == "geojson":
        output_name = base_name + ".geojson"
        geojson = gdf.__geo_interface__
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)

        return output_name
    elif output_format == "csv":
        output_name = base_name + ".csv"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "shapefile":
        output_name = base_name + ".shp"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "gpkg":
        output_name = base_name + ".gpkg"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format in ["geoparquet", "parquet"]:
        output_name = base_name + ".parquet"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    else:
        return convert_to_output_format(gdf, output_format)


def mgrsgrid_cli():
    parser = argparse.ArgumentParser(description="Generate MGRS DGGS.")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        default=0,
        required=True,
        help="Resolution [0..5]",
    )
    parser.add_argument(
        "-gzd",
        type=str,
        default="48P",
        required=True,
        help="GZD - Grid Zone Designator, e.g. 48P",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of MGRS IDs)",
    )
    args = parser.parse_args()
   
    gzd = args.gzd
    if not is_valid_gzd(gzd):
        print("Invalid GZD. Please input a valid GZD and try again.")
        return
    resolution = args.resolution
    if args.output_format == "None":
        args.output_format = None   
   
    try:
        result = mgrsgrid(gzd, resolution, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            print(result)
        elif args.output_format in ["geo", "gpd"]:
            print(result)
        elif args.output_format in [
            "csv",
            "parquet",
            "gpkg",
            "shapefile",
            "geojson",
        ] and isinstance(result, str):
            print(f"Output saved as {result}")
        elif args.output_format == "geojson" and isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"Output saved in current directory.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    mgrsgrid_cli()
