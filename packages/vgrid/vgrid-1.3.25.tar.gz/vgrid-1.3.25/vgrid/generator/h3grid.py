# Reference: https://observablehq.com/@claude-ducharme/h3-map
# https://h3-snow.streamlit.app/

import json, argparse
from shapely.geometry import Polygon, box, shape
from shapely.ops import unary_union
from tqdm import tqdm
from pyproj import Geod
import geopandas as gpd
import h3
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import (
    geodesic_buffer,
    geodesic_dggs_to_geoseries,
)
from vgrid.utils.io import validate_h3_resolution, convert_to_output_format
from vgrid.conversion.dggs2geo.h32geo import h32geo 
geod = Geod(ellps="WGS84")      


def h3_grid(resolution, output_format=None):
    resolution = validate_h3_resolution(resolution)
    total_cells = h3.get_num_cells(resolution)
    if total_cells > MAX_CELLS:
        raise ValueError(
            f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
        )
    else:
        base_cells = h3.get_res0_cells()
        num_base_cells = len(base_cells)
        h3_records = []
        # Progress bar for base cells
        with tqdm(
            total=total_cells, desc="Generating H3 DGGS", unit=" cells"
        ) as pbar:
            for cell in base_cells:
                child_cells = h3.cell_to_children(cell, resolution)
                # Progress bar for child cells
                for child_cell in child_cells:
                    cell_polygon = h32geo(child_cell)
                    h3_id = str(child_cell)
                    num_edges = 6
                    if h3.is_pentagon(h3_id):
                        num_edges = 5
                    record = geodesic_dggs_to_geoseries(
                        "h3", h3_id, resolution, cell_polygon, num_edges
                    )
                    h3_records.append(record)
                    pbar.update(1)

        if output_format is None:
            # Return list of dicts with geometry as WKT
            for rec in h3_records:
                rec["geometry"] = rec["geometry"].wkt
            return h3_records
        elif output_format == "gpd":
            return gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
        else:
            gdf = gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
            base_name = f"h3_grid_{resolution}"
            if output_format == "geojson_dict":
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


def h3_grid_within_bbox(resolution, bbox, output_format=None):
    resolution = validate_h3_resolution(resolution)
    bbox_polygon = box(*bbox)  # Create a bounding box polygon
    distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
    bbox_buffer = geodesic_buffer(bbox_polygon, distance)
    bbox_buffer_cells = h3.geo_to_cells(bbox_buffer, resolution)
    total_cells = len(bbox_buffer_cells)
    if total_cells > MAX_CELLS:
        raise ValueError(
            f"Resolution {resolution} within bounding box {bbox} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
        )
    else:
        h3_records = []
        for bbox_buffer_cell in tqdm(bbox_buffer_cells, desc="Processing cells"):
            cell_polygon = h32geo(bbox_buffer_cell)
            if cell_polygon.intersects(bbox_polygon):
                h3_id = str(bbox_buffer_cell)
                num_edges = 6
                if h3.is_pentagon(h3_id):
                    num_edges = 5
                record = geodesic_dggs_to_geoseries(
                    "h3", h3_id, resolution, cell_polygon, num_edges
                )
                h3_records.append(record)

        if output_format is None:
            for rec in h3_records:
                rec["geometry"] = rec["geometry"].wkt
            return h3_records
        elif output_format == "gpd":
            return gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
        else:
            gdf = gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
            base_name = f"h3_grid_{resolution}"
            if output_format == "geojson_dict":
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


def h3_grid_resample(
    resolution, geojson_features, output_format="geojson"
):
    resolution = validate_h3_resolution(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
    buffered_geom = geodesic_buffer(unified_geom, distance)
    h3_cells = h3.geo_to_cells(buffered_geom, resolution)
    h3_records = []
    for h3_cell in tqdm(h3_cells, desc="Generating H3 DGGS", unit=" cells"):
        cell_polygon = h32geo(h3_cell)
        if cell_polygon.intersects(unified_geom):
            h3_id = str(h3_cell)
            num_edges = 6 if not h3.is_pentagon(h3_id) else 5
            record = geodesic_dggs_to_geoseries(
                "h3", h3_id, resolution, cell_polygon, num_edges
            )
            h3_records.append(record)

    if output_format is None:
        for rec in h3_records:
            rec["geometry"] = rec["geometry"].wkt
        return h3_records
    elif output_format == "gpd":
        return gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
        base_name = f"h3_grid_{resolution}"
        if output_format == "geojson_dict":
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


def h3grid(resolution, bbox=None, output_format=None):
    """
    Generate H3 grid for pure Python usage.

    Args:
        resolution (int): H3 resolution [0..15]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output output_format ('geojson' or 'csv'). Defaults to 'geojson'.

    Returns:
        dict or list: GeoJSON FeatureCollection or list of CSV rows depending on output_format
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        num_cells = h3.get_num_cells(resolution)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        return h3_grid(resolution, output_format)
    else:
        return h3_grid_within_bbox(resolution, bbox, output_format)


def h3grid_cli():
    """CLI interface for generating H3 grid."""
    parser = argparse.ArgumentParser(description="Generate H3 DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..15]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of H3 IDs)",
    )
    args = parser.parse_args()
    # Ensure Python None, not string 'None'
    if args.output_format == "None":
        args.output_format = None
    try:
        result = h3grid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            # Print the entire Python list of H3 IDs at once
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
