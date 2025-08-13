"""
ISEA3H DGGS Grid Generator Module
"""

import argparse
import json
import platform
import geopandas as gpd
from shapely.geometry import box
from tqdm import tqdm

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    isea3h_dggs = Eaggr(Model.ISEA3H)

from vgrid.utils.geometry import isea3h_cell_to_polygon, geodesic_dggs_to_geoseries
from vgrid.utils.io import validate_isea3h_resolution, convert_to_output_format

from vgrid.utils.constants import (
    ISEA3H_ACCURACY_RES_DICT,
    ISEA3H_RES_ACCURACY_DICT,
    MAX_CELLS,
    ISEA3H_BASE_CELLS,
)

from pyproj import Geod

geod = Geod(ellps="WGS84")


def get_isea3h_children_cells(base_cells, target_resolution):
    """
    Recursively generate DGGS cells for the desired resolution, returning only the cells at the target resolution.
    """
    current_cells = base_cells
    for res in range(target_resolution):
        next_cells = []
        seen_cells = set()
        for cell in current_cells:
            children = isea3h_dggs.get_dggs_cell_children(DggsCell(cell))
            for child in children:
                if child._cell_id not in seen_cells:
                    seen_cells.add(child._cell_id)
                    next_cells.append(child._cell_id)
        current_cells = next_cells
    return current_cells


def get_isea3h_children_cells_within_bbox(
    bounding_cell, bbox, target_resolution
):
    """
    Recursively generate DGGS cells within a bounding box, returning only the cells at the target resolution.
    """
    current_cells = [bounding_cell]  # Start with a list containing the single bounding cell
    bounding_cell2point = isea3h_dggs.convert_dggs_cell_to_point(
        DggsCell(bounding_cell)
    )
    accuracy = bounding_cell2point._accuracy
    bounding_resolution = ISEA3H_ACCURACY_RES_DICT.get(accuracy)

    if bounding_resolution <= target_resolution:
        for res in range(bounding_resolution, target_resolution):
            next_cells = []
            seen_cells = set()
            for cell in current_cells:
                # Get the child cells for the current cell
                children = isea3h_dggs.get_dggs_cell_children(DggsCell(cell))
                for child in children:
                    if child._cell_id not in seen_cells:
                        child_shape = isea3h_cell_to_polygon(child)
                        if child_shape.intersects(bbox):
                            seen_cells.add(child._cell_id)
                            next_cells.append(child._cell_id)
            if not next_cells:  # Break early if no cells remain
                break
            current_cells = next_cells  # Update current_cells to process the next level of children

        return current_cells
    else:
        # print('Bounding box area is < 0.028 square meters. Please select a bigger bounding box')
        return None


def isea3h_grid(resolution):
    """
    Generate DGGS cells and convert them to GeoJSON features.
    """
    if platform.system() == "Windows":
        resolution = validate_isea3h_resolution(resolution)
        children = get_isea3h_children_cells(ISEA3H_BASE_CELLS, resolution)
        records = []
        for child in tqdm(children, desc="Generating ISEA3H DGGS", unit=" cells"):
            try:
                isea3h_cell = DggsCell(child)
                cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
                isea3h_id = isea3h_cell.get_cell_id()
                num_edges = 6 if resolution > 0 else 3
                record = geodesic_dggs_to_geoseries(
                    "isea3h", isea3h_id, resolution, cell_polygon, num_edges
                )
                records.append(record)
            except Exception as e:
                print(f"Error generating ISEA3H DGGS cell {child}: {e}")
                continue
        return gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")


def isea3h_grid_within_bbox(resolution, bbox):
    if platform.system() == "Windows":
        resolution = validate_isea3h_resolution(resolution)
        accuracy = ISEA3H_RES_ACCURACY_DICT.get(resolution)
        bounding_box = box(*bbox)
        bounding_box_wkt = bounding_box.wkt
        shapes = isea3h_dggs.convert_shape_string_to_dggs_shapes(
            bounding_box_wkt, ShapeStringFormat.WKT, accuracy
        )
        shape = shapes[0]
        bbox_cells = shape.get_shape().get_outer_ring().get_cells()
        bounding_cell = isea3h_dggs.get_bounding_dggs_cell(bbox_cells)
        bounding_children_cells = get_isea3h_children_cells_within_bbox(
            bounding_cell.get_cell_id(), bounding_box, resolution
        )
        if bounding_children_cells:
            records = []
            for child in bounding_children_cells:
                isea3h_cell = DggsCell(child)
                cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
                isea3h_id = isea3h_cell.get_cell_id()
                num_edges = 6 if resolution > 0 else 3
                record = geodesic_dggs_to_geoseries(
                    "isea3h", isea3h_id, resolution, cell_polygon, num_edges
                )
                records.append(record)
            return gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")


def isea3hgrid(resolution, bbox=None, output_format=None):
    """
    Generate ISEA3H grid for pure Python usage.

    Args:
        resolution (int): ISEA3H resolution [0..40]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output output_format ('geojson', 'csv', etc). Defaults to None (list of IDs).

    Returns:
        dict or list: GeoJSON FeatureCollection, file path, or list of IDs depending on output_format
    """
    if platform.system() != "Windows":
        raise RuntimeError("ISEA3H grid generation is only supported on Windows due to EAGGR dependency")

    if bbox is None:
        bbox = [-180, -90, 180, 90]
        total_cells = 20 * (7 ** resolution)
        if total_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = isea3h_grid(resolution)
    else:
        gdf = isea3h_grid_within_bbox(resolution, bbox)
    
    base_name = f"isea3h_grid_{resolution}"
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

def isea3hgrid_cli():
    parser = argparse.ArgumentParser(description="Generate Open-Eaggr ISEA3H DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..40]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of ISEA3H IDs)",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file path (optional)", default=None
    )
    args = parser.parse_args()
    
    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180, -90, 180, 90]
    
    if bbox == [-180, -90, 180, 90]:
        total_cells = 20 * (7**resolution)
        print(f"Resolution {resolution} within bounding box {bbox} will generate {total_cells} cells ")
        if total_cells > MAX_CELLS:
            print(f"which exceeds the limit of {MAX_CELLS}. ")
            print("Please select a smaller resolution and try again.")
            return
        isea3h_features = isea3h_grid(resolution)
    else:
        isea3h_features = isea3h_grid_within_bbox(resolution, bbox)
    try:
        result = convert_to_output_format(isea3h_features["features"], args.output_format, args.output)
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
    isea3hgrid_cli()
