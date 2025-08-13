"""
EASE DGGS Grid Generator Module
"""
import argparse
import json
import geopandas as gpd
from shapely.geometry import Polygon, box
from tqdm import tqdm
from vgrid.dggs.easedggs.constants import grid_spec, ease_crs, geo_crs, levels_specs
from vgrid.dggs.easedggs.dggs.grid_addressing import (
    grid_ids_to_geos,
    geo_polygon_to_grid_ids,
)
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import validate_ease_resolution, convert_to_output_format
# Initialize the geodetic model

geo_bounds = grid_spec["geo"]
min_longitude = geo_bounds["min_x"]
min_lattitude = geo_bounds["min_y"]
max_longitude = geo_bounds["max_x"]
max_latitude = geo_bounds["max_y"]


def get_ease_cells(resolution):
    """
    Generate a list of cell IDs based on the resolution, row, and column.
    """
    n_row = levels_specs[resolution]["n_row"]
    n_col = levels_specs[resolution]["n_col"]

    # Generate list of cell IDs
    cell_ids = []

    # Loop through all rows and columns at the specified resolution
    for row in range(n_row):
        for col in range(n_col):
            # Generate base ID (e.g., L0.RRRCCC for res=0)
            base_id = f"L{resolution}.{row:03d}{col:03d}"

            # Add additional ".RC" for each higher resolution
            cell_id = base_id
            for i in range(1, resolution + 1):
                cell_id += f".{row:1d}{col:1d}"  # For res=1: L0.RRRCCC.RC, res=2: L0.RRRCCC.RC.RC, etc.

            # Append the generated cell ID to the list
            cell_ids.append(cell_id)

    return cell_ids


def get_ease_cells_bbox(resolution, bbox):
    bounding_box = box(*bbox)
    bounding_box_wkt = bounding_box.wkt
    cells_bbox = geo_polygon_to_grid_ids(
        bounding_box_wkt,
        level=resolution,
        source_crs=geo_crs,
        target_crs=ease_crs,
        levels_specs=levels_specs,
        return_centroids=True,
        wkt_geom=True,
    )
    return cells_bbox


def ease_grid(resolution):
    resolution = validate_ease_resolution(resolution)
    ease_rows = []
    level_spec = levels_specs[resolution]
    n_row = level_spec["n_row"]
    n_col = level_spec["n_col"]
    cells = get_ease_cells(resolution)
    for cell in tqdm(
        cells, total=len(cells), desc="Generating EASE DGGS", unit=" cells"
    ):
        geo = grid_ids_to_geos([cell])
        center_lon, center_lat = geo["result"]["data"][0]
        cell_min_lat = center_lat - (180 / (2 * n_row))
        cell_max_lat = center_lat + (180 / (2 * n_row))
        cell_min_lon = center_lon - (360 / (2 * n_col))
        cell_max_lon = center_lon + (360 / (2 * n_col))
        cell_polygon = Polygon(
            [
                [cell_min_lon, cell_min_lat],
                [cell_max_lon, cell_min_lat],
                [cell_max_lon, cell_max_lat],
                [cell_min_lon, cell_max_lat],
                [cell_min_lon, cell_min_lat],
            ]
        )
        if cell_polygon:
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "ease", str(cell), resolution, cell_polygon, num_edges
            )
            ease_rows.append(row)
    return gpd.GeoDataFrame(ease_rows, geometry="geometry", crs="EPSG:4326")


def ease_grid_within_bbox(resolution, bbox):
    resolution = validate_ease_resolution(resolution)
    ease_rows = []
    level_spec = levels_specs[resolution]
    n_row = level_spec["n_row"]
    n_col = level_spec["n_col"]
    cells = get_ease_cells_bbox(resolution, bbox)["result"]["data"]
    if cells:
        for cell in tqdm(cells, desc="Generating EASE DGGS", unit=" cells"):
            geo = grid_ids_to_geos([cell])
            if geo:
                center_lon, center_lat = geo["result"]["data"][0]
                cell_min_lat = center_lat - (180 / (2 * n_row))
                cell_max_lat = center_lat + (180 / (2 * n_row))
                cell_min_lon = center_lon - (360 / (2 * n_col))
                cell_max_lon = center_lon + (360 / (2 * n_col))
                cell_polygon = Polygon(
                    [
                        [cell_min_lon, cell_min_lat],
                        [cell_max_lon, cell_min_lat],
                        [cell_max_lon, cell_max_lat],
                        [cell_min_lon, cell_max_lat],
                        [cell_min_lon, cell_min_lat],
                    ]
                )
                num_edges = 4
                row = geodesic_dggs_to_geoseries(
                    "ease", str(cell), resolution, cell_polygon, num_edges
                )
                ease_rows.append(row)
    return gpd.GeoDataFrame(ease_rows, geometry="geometry", crs="EPSG:4326")


def easegrid(resolution, bbox=None, output_format=None):
    if bbox is None:
        bbox = [min_longitude, min_lattitude, max_longitude, max_latitude]
        level_spec = levels_specs[resolution]
        n_row = level_spec["n_row"]
        n_col = level_spec["n_col"]
        total_cells = n_row * n_col
        if total_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = ease_grid(resolution)
    else:
        gdf = ease_grid_within_bbox(resolution, bbox)
    base_name = f"ease_grid_{resolution}"
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


def easegrid_cli():
    parser = argparse.ArgumentParser(description="Generate EASE-DGGS DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="resolution [0..6]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of EASE IDs)",
    )
    args = parser.parse_args()
    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = (
        args.bbox
        if args.bbox
        else [min_longitude, min_lattitude, max_longitude, max_latitude]
    )
    if resolution < 0 or resolution > 6:
        print("Please select a resolution in [0..6] range and try again")
        return
    try:
        result = easegrid(resolution, bbox, args.output_format)
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
    easegrid_cli()