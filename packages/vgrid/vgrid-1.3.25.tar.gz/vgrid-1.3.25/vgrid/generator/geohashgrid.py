"""
GEOHASH DGGS Grid Generator Module
Reference: https://geohash.softeng.co/uekkn, https://github.com/vinsci/geohash, https://www.movable-type.co.uk/scripts/geohash.html?geohash=dp3

"""

import argparse
import json
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
from tqdm import tqdm
from vgrid.utils.constants import MAX_CELLS, INITIAL_GEOHASHES
from vgrid.utils.geometry import graticule_dggs_to_geoseries
import geopandas as gpd
from vgrid.conversion.dggs2geo.geohash2geo import geohash2geo
from vgrid.utils.io import validate_geohash_resolution, convert_to_output_format

def expand_geohash(gh, target_length, geohashes):
    if len(gh) == target_length:
        geohashes.add(gh)
        return
    for char in "0123456789bcdefghjkmnpqrstuvwxyz":
        expand_geohash(gh + char, target_length, geohashes)


def geohash_grid(resolution):
    """Generate GeoJSON for the entire world at the given geohash resolution."""
    resolution = validate_geohash_resolution(resolution)
    geohashes = set()
    for gh in INITIAL_GEOHASHES:
        expand_geohash(gh, resolution, geohashes)

    geohash_records = []
    for gh in tqdm(geohashes, desc="Generating Geohash DGGS", unit=" cells"):
        cell_polygon = geohash2geo(gh)
        geohash_record = graticule_dggs_to_geoseries(
            "geohash", gh, resolution, cell_polygon
        )
        geohash_records.append(geohash_record)
    return gpd.GeoDataFrame(geohash_records, geometry="geometry", crs="EPSG:4326")


def expand_geohash_bbox(gh, target_length, geohashes, bbox_polygon):
    """Expand geohash only if it intersects the bounding box."""
    polygon = geohash2geo(gh)
    if not polygon.intersects(bbox_polygon):
        return

    if len(gh) == target_length:
        geohashes.add(gh)  # Add to the set if it reaches the target resolution
        return

    for char in "0123456789bcdefghjkmnpqrstuvwxyz":
        expand_geohash_bbox(gh + char, target_length, geohashes, bbox_polygon)


def geohash_grid_within_bbox(resolution, bbox):
    """Generate GeoJSON for geohashes within a bounding box at the given resolution."""
    resolution = validate_geohash_resolution(resolution)
    geohash_records = []
    bbox_polygon = Polygon.from_bounds(*bbox)
    intersected_geohashes = {
        gh
        for gh in INITIAL_GEOHASHES
        if geohash2geo(gh).intersects(bbox_polygon)
    }
    geohashes_bbox = set()
    for gh in intersected_geohashes:
        expand_geohash_bbox(gh, resolution, geohashes_bbox, bbox_polygon)
    for gh in tqdm(geohashes_bbox, desc="Generating Geohash DGGS", unit=" cells"):
        geohash_record = graticule_dggs_to_geoseries("geohash", gh, resolution, geohash2geo(gh))
        geohash_records.append(geohash_record)
    return gpd.GeoDataFrame(geohash_records, geometry="geometry", crs="EPSG:4326")


def geohash_grid_resample(resolution, geojson_features):
    """Generate GeoJSON for geohashes within a GeoJSON feature collection at the given resolution."""
    resolution = validate_geohash_resolution(resolution)
    geohash_records = []
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    intersected_geohashes = {
        gh
        for gh in INITIAL_GEOHASHES
        if geohash2geo(gh).intersects(unified_geom)
    }
    geohashes_geom = set()
    for gh in intersected_geohashes:
        expand_geohash_bbox(gh, resolution, geohashes_geom, unified_geom)
    for gh in tqdm(geohashes_geom, desc="Generating Geohash DGGS", unit="cells"):
        geohash_record = graticule_dggs_to_geoseries("geohash", gh, resolution, geohash2geo(gh))
        geohash_records.append(geohash_record)
    return gpd.GeoDataFrame(geohash_records, geometry="geometry", crs="EPSG:4326")


def geohashgrid(resolution, bbox=None, output_format=None):
    """
    Generate Geohash grid for pure Python usage.

    Args:
        resolution (int): Geohash resolution [1..10]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', 'geo', 'gpd', 'shapefile', 'gpkg', 'parquet', or None for list of Geohash IDs).

    Returns:
        dict, list, or str: Output in the requested format or file path.
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        total_cells = 32 ** resolution
        if total_cells > MAX_CELLS:
            raise ValueError(f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}")
        gdf = geohash_grid(resolution)
    else:
        gdf = geohash_grid_within_bbox(resolution, bbox)
    base_name = f"geohash_grid_{resolution}"
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


def geohashgrid_cli():
    parser = argparse.ArgumentParser(description="Generate Geohash DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [1..10]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of Geohash IDs)",
    )
    args = parser.parse_args()
    if args.output_format == "None":
        args.output_format = None
    try:
        result = geohashgrid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            print(result)
        elif args.output_format in ["geo", "gpd"]:
            print(result)
        elif args.output_format in ["csv", "parquet", "gpkg", "shapefile", "geojson"] and isinstance(result, str):
            print(f"Output saved as {result}")
        elif args.output_format == "geojson" and isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"Output saved in current directory.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    geohashgrid_cli()
