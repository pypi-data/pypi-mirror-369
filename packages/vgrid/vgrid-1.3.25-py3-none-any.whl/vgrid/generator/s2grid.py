"""
S2 Grid Generator Module.
This module provides functionality to generate S2 DGGS grids.
Reference:
    https://github.com/aaliddell/s2cell,
    https://medium.com/@claude.ducharme/selecting-a-geo-representation-81afeaf3bf01
    https://github.com/sidewalklabs/s2
    https://github.com/google/s2geometry/tree/master/src/python
    https://github.com/google/s2geometry
    https://gis.stackexchange.com/questions/293716/creating-shapefile-of-s2-cells-for-given-level
    https://s2.readthedocs.io/en/latest/quickstart.html
"""

import json
import argparse
from shapely.geometry import shape
from shapely.ops import unary_union
import geopandas as gpd
from tqdm import tqdm
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.dggs import s2
from vgrid.utils.io import validate_s2_resolution, convert_to_output_format
from vgrid.utils.geometry import s2_cell_to_polygon

def s2_grid(resolution, bbox):
    """
    Generate an S2 DGGS grid for a given resolution and bounding box.
    """
    resolution = validate_s2_resolution(resolution)
    min_lng, min_lat, max_lng, max_lat = bbox
    # Define the cell level (S2 uses a level system for zoom, where level 30 is the highest resolution)
    level = resolution
    # Create a list to store the S2 cell IDs
    cell_ids = []
    # Define the cell covering
    coverer = s2.RegionCoverer()
    coverer.min_level = level
    coverer.max_level = level
    # coverer.max_cells = 1000_000  # Adjust as needed
    # coverer.max_cells = 0  # Adjust as needed

    # Define the region to cover (in this example, we'll use the entire world)
    region = s2.LatLngRect(
        s2.LatLng.from_degrees(min_lat, min_lng),
        s2.LatLng.from_degrees(max_lat, max_lng),
    )

    # Get the covering cells
    covering = coverer.get_covering(region)

    # Convert the covering cells to S2 cell IDs
    for cell_id in covering:
        cell_ids.append(cell_id)

    s2_rows = []
    num_edges = 4

    for cell_id in tqdm(cell_ids, desc="Generating S2 DGGS", unit=" cells"):
        # Generate a Shapely Polygon
        cell_polygon = s2_cell_to_polygon(cell_id)
        s2_token = cell_id.to_token()
        row = geodesic_dggs_to_geoseries(
            "s2", s2_token, resolution, cell_polygon, num_edges
        )
        s2_rows.append(row)

    return gpd.GeoDataFrame(s2_rows, geometry="geometry", crs="EPSG:4326")


def s2_grid_resample(resolution, geojson_features):
    """
    Generate an S2 DGGS grid for a given resolution and GeoJSON features.
    """
    resolution = validate_s2_resolution(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)

    # Step 2: Get bounding box from unified geometry
    min_lng, min_lat, max_lng, max_lat = unified_geom.bounds

    # Step 3: Configure the S2 coverer
    level = resolution
    coverer = s2.RegionCoverer()
    coverer.min_level = level
    coverer.max_level = level

    # Step 4: Create a LatLngRect from the bounding box
    region = s2.LatLngRect(
        s2.LatLng.from_degrees(min_lat, min_lng),
        s2.LatLng.from_degrees(max_lat, max_lng),
    )

    # Step 5: Get the covering cells
    covering = coverer.get_covering(region)

    s2_rows = []
    for cell_id in tqdm(covering, desc="Generating S2 DGGS", unit=" cells"):
        # Convert S2 cell to polygon (must define `s2_cell_to_polygon`)
        cell_polygon = s2_cell_to_polygon(cell_id)

        # Check intersection with actual geometry
        if cell_polygon.intersects(unified_geom):
            s2_token = cell_id.to_token()
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "s2", s2_token, resolution, cell_polygon, num_edges
            )
            s2_rows.append(row)

    return gpd.GeoDataFrame(s2_rows, geometry="geometry", crs="EPSG:4326")


def s2grid(resolution, bbox=None, output_format=None):
    """
    Generate S2 grid for pure Python usage.

    Args:
        resolution (int): S2 resolution [0..30]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output output_format ('geojson', 'csv', etc.). Defaults to None (list of S2 tokens).

    Returns:
        dict or list: GeoJSON FeatureCollection, list of S2 tokens, or file path depending on output_format
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        num_cells = 6 * (4 ** resolution)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
    gdf = s2_grid(resolution, bbox)
    base_name = f"s2_grid_{resolution}"
    if output_format is None:
        return gdf
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


def s2grid_cli():
    """CLI interface for generating S2 grid."""
    parser = argparse.ArgumentParser(description="Generate S2 DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..30]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of S2 IDs)",
    )
    args = parser.parse_args()
    # Ensure Python None, not string 'None'
    if args.output_format == "None":
        args.output_format = None
    try:
        result = s2grid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            # Print the entire Python list of S2 IDs at once
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
    s2grid_cli()
