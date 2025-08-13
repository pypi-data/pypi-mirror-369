import sys
import os
import argparse
import platform
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import box
from vgrid.utils.geometry import check_predicate, shortest_point_distance, shortest_polyline_distance, shortest_polygon_distance
from vgrid.utils.io import validate_isea4t_resolution, process_input_data_vector, convert_to_output_format
def is_windows():
    return platform.system() == "Windows"

if is_windows():
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.dggs.eaggr.shapes.lat_long_point import LatLongPoint
    from vgrid.generator.isea4tgrid import get_isea4t_children_cells_within_bbox
    from vgrid.utils.constants import ISEA4T_RES_ACCURACY_DICT
    from vgrid.utils.geometry import geodesic_dggs_to_geoseries
    from vgrid.conversion.dggscompact.isea4tcompact import isea4t_compact
    from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo
    from vgrid.stats.isea4tstats import isea4t_metrics
    isea4t_dggs = Eaggr(Model.ISEA4T)


def point2isea4t(
    resolution,
    point,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,
):
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        if shortest_distance > 0:
            for res in range(26):
                _, avg_edge_length, _ = isea4t_metrics(res)
                cell_diameter = avg_edge_length * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 25
    isea4t_rows = []
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    lat_long_point = LatLongPoint(point.y, point.x, accuracy)
    isea4t_cell = isea4t_dggs.convert_point_to_dggs_cell(lat_long_point)
    isea4t_id = isea4t_cell.get_cell_id()
    cell_polygon = isea4t2geo(isea4t_id)
    num_edges = 3
    row = geodesic_dggs_to_geoseries(
        "isea4t", isea4t_id, resolution, cell_polygon, num_edges
    )
    if include_properties and feature_properties:
        row.update(feature_properties)
    isea4t_rows.append(row)
    return isea4t_rows


def polyline2isea4t(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,
):
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        if shortest_distance > 0:
            # Import locally to avoid circular import
            from vgrid.stats.isea4tstats import isea4t_metrics
            for res in range(26):
                _, avg_edge_length, _ = isea4t_metrics(res)
                cell_diameter = avg_edge_length * 4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 25
    isea4t_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
        bounding_box = box(*polyline.bounds)
        bounding_box_wkt = bounding_box.wkt
        shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
            bounding_box_wkt, ShapeStringFormat.WKT, accuracy
        )
        shape = shapes[0]
        bbox_cells = shape.get_shape().get_outer_ring().get_cells()
        bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
        bounding_child_cells = get_isea4t_children_cells_within_bbox(
            bounding_cell.get_cell_id(), bounding_box, resolution
        )        
        for child in bounding_child_cells:
            isea4t_id = child
            cell_polygon = isea4t2geo(isea4t_id)
            if cell_polygon.intersects(polyline):
                num_edges = 3
                cell_resolution = len(isea4t_id) - 2
                row = geodesic_dggs_to_geoseries(
                    "isea4t", isea4t_id, cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                isea4t_rows.append(row)
    return isea4t_rows


def polygon2isea4t(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,
):
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        if shortest_distance > 0:
            # Import locally to avoid circular import
            from vgrid.stats.isea4tstats import isea4t_metrics
            for res in range(26):
                _, avg_edge_length, _ = isea4t_metrics(res)
                cell_diameter = avg_edge_length * 4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 25
    isea4t_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
        bounding_box = box(*polygon.bounds)
        bounding_box_wkt = bounding_box.wkt
        shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
            bounding_box_wkt, ShapeStringFormat.WKT, accuracy
        )
        shape = shapes[0]
        bbox_cells = shape.get_shape().get_outer_ring().get_cells()
        bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
        bounding_child_cells = get_isea4t_children_cells_within_bbox(
            bounding_cell.get_cell_id(), bounding_box, resolution
        )
        if compact:
            bounding_child_cells = isea4t_compact(bounding_child_cells)
        for child in bounding_child_cells:
            isea4t_id = child
            cell_polygon = isea4t2geo(isea4t_id)
            if check_predicate(cell_polygon, polygon, predicate):
                num_edges = 3
                cell_resolution = len(isea4t_id) - 2
                row = geodesic_dggs_to_geoseries(
                    "isea4t", isea4t_id, cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                isea4t_rows.append(row)
    return isea4t_rows


def geometry2isea4t(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    if not is_windows():
        raise NotImplementedError("ISEA4T DGGS conversion is only supported on Windows")

    resolution = validate_isea4t_resolution(resolution)
    # Handle single geometry or list of geometries
    if not isinstance(geometries, list):
        geometries = [geometries]

    # Handle properties
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    isea4t_rows = []
    # Collect all points, polylines, and polygons for topology preservation if needed
    all_points = None
    all_polylines = None
    all_polygons = None
    if topology:
        from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
        points_list = []
        polylines_list = []
        polygons_list = []
        for i, geom in enumerate(geometries):
            if geom is None:
                continue
            if geom.geom_type == "Point":
                points_list.append(geom)
            elif geom.geom_type == "MultiPoint":
                points_list.extend(list(geom.geoms))
            elif geom.geom_type == "LineString":
                polylines_list.append(geom)
            elif geom.geom_type == "MultiLineString":
                polylines_list.extend(list(geom.geoms))
            elif geom.geom_type == "Polygon":
                polygons_list.append(geom)
            elif geom.geom_type == "MultiPolygon":
                polygons_list.extend(list(geom.geoms))
        if points_list:
            all_points = MultiPoint(points_list)
        if polylines_list:
            all_polylines = MultiLineString(polylines_list)
        if polygons_list:
            all_polygons = MultiPolygon(polygons_list)
    for idx, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue
        props = (
            properties_list[idx]
            if properties_list and idx < len(properties_list)
            else {}
        )
        if not include_properties:
            props = {}
        if geom.geom_type == "Point":
            isea4t_rows.extend(
                point2isea4t(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_points,
                )
            )
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                isea4t_rows.extend(
                    point2isea4t(
                        resolution,
                        pt,
                        props,
                        predicate,
                        compact,
                        topology,
                        include_properties,
                        all_points,
                    )
                )
        elif geom.geom_type in ("LineString", "MultiLineString"):
            isea4t_rows.extend(
                polyline2isea4t(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polylines,
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            isea4t_rows.extend(
                polygon2isea4t(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polygons,
                )
            )
    if isea4t_rows:
        gdf = gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    return gdf


def dataframe2isea4t(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    geometries = []
    properties_list = []
    for idx, row in df.iterrows():
        geom = row.geometry if "geometry" in row else row["geometry"]
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)
    return geometry2isea4t(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2isea4t(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    geometries = []
    properties_list = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)
    return geometry2isea4t(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2isea4t(
    data,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    output_format=None,
    include_properties=True,
    **kwargs,
):
    """
    Convert vector data to ISEA4T grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    if not is_windows():
        raise NotImplementedError("ISEA4T DGGS conversion is only supported on Windows")
    resolution = validate_isea4t_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2isea4t(
        gdf, resolution, predicate, compact, topology, include_properties
    )
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    output_name = None
    if output_format in file_formats:
        ext_map = {
            "csv": ".csv",
            "geojson": ".geojson",
            "shapefile": ".shp",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "geoparquet": ".parquet",
        }
        ext = ext_map.get(output_format, "")
        if isinstance(data, str):
            base = os.path.splitext(os.path.basename(data))[0]
            output_name = f"{base}2isea4t_{resolution}{ext}"
        else:
            output_name = f"isea4t_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2isea4t_cli():
    """
    Command-line interface for vector2isea4t conversion (Windows only).
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to ISEA4T grid cells (Windows only)"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(26),
        metavar="[0-25]",
        help="ISEA4T resolution [0..25] (0=coarsest, 25=finest)",
    )
    parser.add_argument(
        "-p",
        "--predicate",
        choices=["intersect", "within", "centroid_within", "largest_overlap"],
        help="Spatial predicate: intersect, within, centroid_within, largest_overlap for polygons",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Enable ISEA4T compact mode for polygons",
    )
    parser.add_argument(
        "-t", "--topology", action="store_true", help="Enable topology preserving mode"
    )
    parser.add_argument(
        "-np",
        "-no-props",
        dest="include_properties",
        action="store_false",
        help="Do not include original feature properties.",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        default="geojson",
        choices=["geojson", "geojson_dict", "gpkg", "parquet", "csv", "shapefile", None],
        help="Output format (default: geojson). Use 'geojson_dict' for Python dict, None for list of dicts.",
    )
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()
    if not is_windows():
        print("ISEA4T DGGS conversion is only supported on Windows", file=sys.stderr)
        sys.exit(1)
    args.resolution = validate_isea4t_resolution(args.resolution)
    data = args.input
    output_name = args.output
    if not output_name and args.output_format in [
        "geojson",
        "gpkg",
        "parquet",
        "csv",
        "shapefile",
    ]:
        extensions = {
            "geojson": ".geojson",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "csv": ".csv",
            "shapefile": ".shp",
        }
        output_name = f"vector2isea4t{extensions.get(args.output_format, '')}"
    try:
        result = vector2isea4t(
            data,
            args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            include_properties=args.include_properties,
            output_format=args.output_format,
            output_name=output_name,
        )
        if args.output_format == "geojson":
            print(f"Output saved to {result}")
        elif args.output_format == "geojson_dict":
            print(f"GeoJSON dict generated with {len(result['features'])} features.")
        elif args.output_format is None:
            print(f"List of {len(result)} ISEA4T cell dicts returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2isea4t_cli()
