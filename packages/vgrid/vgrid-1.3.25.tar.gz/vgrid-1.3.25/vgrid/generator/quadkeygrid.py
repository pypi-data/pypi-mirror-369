"""
Quadkey DGGS Grid Generator Module
"""

import argparse
import geopandas as gpd
import json
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
from tqdm import tqdm
from vgrid.dggs import mercantile
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import validate_quadkey_resolution, convert_to_output_format
from pyproj import Geod
geod = Geod(ellps="WGS84")


def quadkey_grid(resolution, bbox):
    resolution = validate_quadkey_resolution(resolution)
    quadkey_records = []
    min_lon, min_lat, max_lon, max_lat = bbox
    tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
    for tile in tqdm(tiles, desc="Generating Quadkey DGGS", unit=" cells"):
        z, x, y = tile.z, tile.x, tile.y
        bounds = mercantile.bounds(x, y, z)
        if bounds:
            min_lat, min_lon = bounds.south, bounds.west
            max_lat, max_lon = bounds.north, bounds.east
            quadkey_id = mercantile.quadkey(tile)
            cell_polygon = Polygon(
                [
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ]
            )
            quadkey_record = graticule_dggs_to_geoseries(
                "quadkey", quadkey_id, resolution, cell_polygon
            )
            quadkey_records.append(quadkey_record)
    return gpd.GeoDataFrame(quadkey_records, geometry="geometry", crs="EPSG:4326")


def quadkey_grid_resample(resolution, geojson_features):
    resolution = validate_quadkey_resolution(resolution)
    quadkey_records = []

    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)

    min_lon, min_lat, max_lon, max_lat = unified_geom.bounds

    tiles = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
    num_cells = len(tiles)
    for tile in tqdm(tiles, total=num_cells, desc="Generating Quadkey DGGS", unit=" cells"):
        z, x, y = tile.z, tile.x, tile.y
        bounds = mercantile.bounds(x, y, z)

        # Construct tile polygon
        tile_polygon = Polygon(
            [
                [bounds.west, bounds.south],
                [bounds.east, bounds.south],
                [bounds.east, bounds.north],
                [bounds.west, bounds.north],
                [bounds.west, bounds.south],
            ]
        )

        if tile_polygon.intersects(unified_geom):
            quadkey_id = mercantile.quadkey(tile)
            quadkey_record = graticule_dggs_to_geoseries(
                "quadkey", quadkey_id, resolution, tile_polygon
            )
            quadkey_records.append(quadkey_record)
    import geopandas as gpd
    return gpd.GeoDataFrame(quadkey_records, geometry="geometry", crs="EPSG:4326")


def quadkeygrid(resolution, bbox=None, output_format=None, output_path=None):
    """
    Generate Quadkey grid for pure Python usage.

    Args:
        resolution (int): Quadkey resolution [0..26]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', etc.). Defaults to None (list of Quadkey IDs).
        output_path (str, optional): Output file path. Defaults to None.

    Returns:
        dict, list, or str: Output depending on output_format
    """
    if bbox is None:
        bbox = [-180.0, -85.05112878, 180.0, 85.05112878]
        num_cells = 4 ** resolution
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = quadkey_grid(resolution, bbox)
    else:
        gdf = quadkey_grid(resolution, bbox)

    return convert_to_output_format(gdf, output_format, output_path)


def quadkeygrid_cli():
    parser = argparse.ArgumentParser(description="Generate Quadkey DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="resolution [0..26]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the output_format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of Quadkey IDs)",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file path (optional)", default=None
    )
    args = parser.parse_args()
    
    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180.0, -85.05112878, 180.0, 85.05112878]

    if bbox == [-180.0, -85.05112878, 180.0, 85.05112878]:
        num_cells = 4**resolution
        if num_cells > MAX_CELLS:
            print(f"Resolution {resolution} will generate {num_cells} cells "
                  f"which exceeds the limit of {MAX_CELLS}.")
            print("Please select a smaller resolution and try again.")
            return
    gdf = quadkey_grid(resolution, bbox)
    try:
        result = convert_to_output_format(gdf, args.output_format, args.output)
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
            print(f"Output saved as {args.output}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    quadkeygrid_cli()
