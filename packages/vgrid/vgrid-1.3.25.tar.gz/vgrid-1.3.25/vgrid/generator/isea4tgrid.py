"""
ISEA4T DGGS Grid Generator Module

This module provides functionality for generating ISEA4T DGGS at various resolutions.

Key Features:
- Generate complete global ISEA4T grids at specified resolutions (0-39)
- Generate ISEA4T grids within specified bounding boxes
- Generate ISEA4T grids that intersect with provided geometries (resampling)
- Export grids in multiple formats (GeoJSON, CSV, Shapefile, GeoPackage, Parquet)
- Handle antimeridian crossing cells appropriately
- Support for Windows platform using EAGGR library
"""

import argparse
import json
from shapely.ops import unary_union
from tqdm import tqdm
from shapely.geometry import box, shape
import geopandas as gpd
import platform
if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.utils.constants import ISEA4T_RES_ACCURACY_DICT
    isea4t_dggs = Eaggr(Model.ISEA4T)
    from vgrid.utils.constants import MAX_CELLS, ISEA4T_BASE_CELLS

from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo
from vgrid.utils.geometry import  geodesic_dggs_to_geoseries, isea4t_cell_to_polygon
from vgrid.utils.io import validate_isea4t_resolution, convert_to_output_format

def get_isea4t_children_cells(base_cells, target_resolution):
    """
    Recursively generate DGGS cells for the desired resolution.
    """
    current_cells = base_cells
    for res in range(target_resolution):
        next_cells = []
        for cell in current_cells:
            children = isea4t_dggs.get_dggs_cell_children(DggsCell(cell))
            next_cells.extend([child._cell_id for child in children])
        current_cells = next_cells
    return current_cells


def get_isea4t_children_cells_within_bbox(
    bounding_cell, bbox, target_resolution
):
    current_cells = [
        bounding_cell
    ]  # Start with a list containing the single bounding cell
    bounding_resolution = len(bounding_cell) - 2

    for res in range(bounding_resolution, target_resolution):
        next_cells = []
        for cell in current_cells:
            # Get the child cells for the current cell
            children = isea4t_dggs.get_dggs_cell_children(DggsCell(cell))
            for child in children:
                # Convert child cell to geometry
                child_shape = isea4t_cell_to_polygon(child)
                if child_shape.intersects(bbox):
                    # Add the child cell ID to the next_cells list
                    next_cells.append(child._cell_id)
        if not next_cells:  # Break early if no cells remain
            break
        current_cells = (
            next_cells  # Update current_cells to process the next level of children
        )

    return current_cells


def isea4t_grid(resolution):
    resolution = validate_isea4t_resolution(resolution)
    children = get_isea4t_children_cells(ISEA4T_BASE_CELLS, resolution)
    isea4t_rows = []
    for child in tqdm(children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)        
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4t_grid_within_bbox(resolution, bbox):
    resolution = validate_isea4t_resolution(resolution)
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    bounding_box = box(*bbox)
    bounding_box_wkt = bounding_box.wkt  # Create a bounding box polygon
    isea4t_shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
        bounding_box_wkt, ShapeStringFormat.WKT, accuracy
    )
    isea4t_shape = isea4t_shapes[0]
    bbox_cells = isea4t_shape.get_shape().get_outer_ring().get_cells()
    bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
    bounding_children = get_isea4t_children_cells_within_bbox(
        bounding_cell.get_cell_id(), bounding_box, resolution
    )
    isea4t_rows = []
    for child in tqdm(bounding_children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4t_grid_resample(resolution, geojson_features):
    resolution = validate_isea4t_resolution(resolution)
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    unified_geom_wkt = unified_geom.wkt
    isea4t_shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
        unified_geom_wkt, ShapeStringFormat.WKT, accuracy
    )
    isea4t_shape = isea4t_shapes[0]
    bbox_cells = isea4t_shape.get_shape().get_outer_ring().get_cells()
    bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
    bounding_children = get_isea4t_children_cells_within_bbox(
        bounding_cell.get_cell_id(), unified_geom, resolution
    )
    isea4t_rows = []
    for child in tqdm(bounding_children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        if not cell_polygon.intersects(unified_geom):
            continue
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4tgrid(resolution, bbox=None, output_format=None):
    if platform.system() != "Windows":
        raise RuntimeError("ISEA4T grid generation is only supported on Windows due to EAGGR dependency")
    
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        total_cells = 20 * (4 ** resolution)
        if total_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = isea4t_grid(resolution)
    else:
        gdf = isea4t_grid_within_bbox(resolution, bbox)
    base_name = f"isea4t_grid_{resolution}"
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


def isea4tgrid_cli():
    parser = argparse.ArgumentParser(description="Generate Open-Eaggr ISEA4T DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..39]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of ISEA4T IDs)",
    )
    args = parser.parse_args()
    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180, -90, 180, 90]
    
    try:
        result = isea4tgrid(resolution, bbox, args.output_format)
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
    isea4tgrid_cli()
