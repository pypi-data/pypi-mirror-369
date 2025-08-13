import sys
import os
import argparse
import platform
from tqdm import tqdm
from shapely.geometry import box
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from vgrid.utils.io import (
    validate_isea3h_resolution,
    process_input_data_vector,
    convert_to_output_format,
)

def is_windows():
    return platform.system() == "Windows"


if is_windows():
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.dggs.eaggr.shapes.lat_long_point import LatLongPoint
    from vgrid.stats.isea3hstats import isea3h_metrics
    from vgrid.utils.constants import (
        ISEA3H_RES_ACCURACY_DICT,
        ISEA3H_ACCURACY_RES_DICT,
    )
    from vgrid.generator.isea3hgrid import (
        get_isea3h_children_cells_within_bbox,
    )
    from vgrid.conversion.dggscompact.isea3hcompact import isea3h_compact
    from vgrid.utils.geometry import geodesic_dggs_to_geoseries, isea3h_cell_to_polygon
    isea3h_dggs = Eaggr(Model.ISEA3H)


def point2isea3h(
    resolution,
    point,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,
):
    """
    Convert a point geometry to an ISEA3H grid cell.

    Args:
        resolution (int): ISEA3H resolution [0..32]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable ISEA3H compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode (not used for points)
        include_properties (bool, optional): Whether to include properties in output
        all_points (shapely.geometry.MultiPoint, optional): MultiPoint geometry for topology preservation

    Returns:
        list: List of GeoJSON feature dictionaries representing ISEA3H cells containing the point
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        if shortest_distance > 0:
            for res in range(33):
                _, avg_edge_length, _ = isea3h_metrics(isea3h_dggs, res)
                cell_diameter = avg_edge_length * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break

            else:
                resolution = 32
    isea3h_rows = []
    accuracy = ISEA3H_RES_ACCURACY_DICT.get(resolution)
    lat_long_point = LatLongPoint(point.y, point.x, accuracy)
    isea3h_cell = isea3h_dggs.convert_point_to_dggs_cell(lat_long_point)
    cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
    if cell_polygon:
        isea3h_id = isea3h_cell.get_cell_id()
        cell_resolution = resolution
        num_edges = 3 if cell_resolution == 0 else 6
        row = geodesic_dggs_to_geoseries(
            "isea3h", isea3h_id, cell_resolution, cell_polygon, num_edges
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        isea3h_rows.append(row)
    return isea3h_rows


def polyline2isea3h(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,
):
    """
    Convert line geometries (LineString, MultiLineString) to ISEA3H grid cells.

    Args:
        resolution (int): ISEA3H resolution [0..32]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable ISEA3H compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for lines)
        include_properties (bool, optional): Whether to include properties in output
        all_polylines (shapely.geometry.MultiLineString, optional): MultiLineString geometry for topology preservation

    Returns:
        list: List of GeoJSON feature dictionaries representing ISEA3H cells intersecting the line
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        if shortest_distance > 0:
            for res in range(33):
                _, avg_edge_length, _ = isea3h_metrics(isea3h_dggs, res)
                cell_diameter = avg_edge_length * 4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 32

    isea3h_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        accuracy = ISEA3H_RES_ACCURACY_DICT.get(resolution)
        bounding_box = box(*polyline.bounds)
        bounding_box_wkt = bounding_box.wkt
        shapes = isea3h_dggs.convert_shape_string_to_dggs_shapes(
            bounding_box_wkt, ShapeStringFormat.WKT, accuracy
        )
        shape = shapes[0]
        bbox_cells = shape.get_shape().get_outer_ring().get_cells()
        bounding_cell = isea3h_dggs.get_bounding_dggs_cell(bbox_cells)
        bounding_child_cells = get_isea3h_children_cells_within_bbox(bounding_cell.get_cell_id(), bounding_box, resolution)
        for child in bounding_child_cells:
            isea3h_cell = DggsCell(child)
            cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
            if cell_polygon.intersects(polyline):
                isea3h_id = isea3h_cell.get_cell_id()
                isea3h2point = isea3h_dggs.convert_dggs_cell_to_point(isea3h_cell)
                cell_accuracy = isea3h2point._accuracy
                cell_resolution = ISEA3H_ACCURACY_RES_DICT.get(cell_accuracy)
                num_edges = 3 if cell_resolution == 0 else 6
                row = geodesic_dggs_to_geoseries(
                    "isea3h", isea3h_id, cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                isea3h_rows.append(row)
    return isea3h_rows


def polygon2isea3h(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,
):
    """
    Convert polygon geometries (Polygon, MultiPolygon) to ISEA3H grid cells.

    Args:
        isea3h_dggs: Eaggr instance for ISEA3H DGGS operations.
        resolution (int): ISEA3H resolution [0..32]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable ISEA3H compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for polygons)
        include_properties (bool, optional): Whether to include properties in output
        all_polygons (shapely.geometry.MultiPolygon, optional): MultiPolygon geometry for topology preservation

    Returns:
        list: List of GeoJSON feature dictionaries representing ISEA3H cells based on predicate
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        if shortest_distance > 0:
            for res in range(33):
                _, avg_edge_length, _ = isea3h_metrics(isea3h_dggs, res)
                cell_diameter = avg_edge_length * 4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 32

    isea3h_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        accuracy = ISEA3H_RES_ACCURACY_DICT.get(resolution)
        bounding_box = box(*polygon.bounds)
        bounding_box_wkt = bounding_box.wkt
        shapes = isea3h_dggs.convert_shape_string_to_dggs_shapes(
            bounding_box_wkt, ShapeStringFormat.WKT, accuracy
        )
        shape = shapes[0]
        bbox_cells = shape.get_shape().get_outer_ring().get_cells()
        bounding_cell = isea3h_dggs.get_bounding_dggs_cell(bbox_cells)
        bounding_child_cells = get_isea3h_children_cells_within_bbox(bounding_cell.get_cell_id(), bounding_box, resolution)
        if compact:
            bounding_child_cells = isea3h_compact(bounding_child_cells)
        for child in bounding_child_cells:
            isea3h_cell = DggsCell(child)
            cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
            if check_predicate(cell_polygon, polygon, predicate):
                isea3h_id = isea3h_cell.get_cell_id()
                isea3h2point = isea3h_dggs.convert_dggs_cell_to_point(isea3h_cell)
                cell_accuracy = isea3h2point._accuracy
                cell_resolution = ISEA3H_ACCURACY_RES_DICT.get(cell_accuracy)
                num_edges = 3 if cell_resolution == 0 else 6
                row = geodesic_dggs_to_geoseries(
                    "isea3h", isea3h_id, cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                isea3h_rows.append(row)
    return isea3h_rows


def geometry2isea3h(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to ISEA3H grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): ISEA3H resolution [0..32]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable ISEA3H compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with ISEA3H grid cells
    """

    resolution = validate_isea3h_resolution(resolution)
    # Handle single geometry or list of geometries
    if not isinstance(geometries, list):
        geometries = [geometries]

    # Handle properties
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    isea3h_rows = []
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
            isea3h_rows.extend(
                point2isea3h(                   
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
                isea3h_rows.extend(
                    point2isea3h(
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
            isea3h_rows.extend(
                polyline2isea3h(
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
            isea3h_rows.extend(
                polygon2isea3h(                    
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
    import geopandas as gpd
    if isea3h_rows:
        gdf = gpd.GeoDataFrame(isea3h_rows, geometry="geometry", crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    return gdf


def dataframe2isea3h(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to ISEA3H grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): ISEA3H resolution [0..32]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable ISEA3H compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with ISEA3H grid cells
    """
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
    return geometry2isea3h(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2isea3h(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to ISEA3H grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): ISEA3H resolution [0..32]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable ISEA3H compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with ISEA3H grid cells
    """
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
    return geometry2isea3h(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2isea3h(
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
    Convert vector data to ISEA3H grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    if not is_windows():
        raise NotImplementedError("ISEA3H DGGS conversion is only supported on Windows")
    resolution = validate_isea3h_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2isea3h(
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
            output_name = f"{base}2isea3h_{resolution}{ext}"
        else:
            output_name = f"isea3h_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2isea3h_cli():
    """
    Command-line interface for vector2isea3h conversion (Windows only).
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to ISEA3H grid cells (Windows only)"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(33),
        metavar="[0-32]",
        help="ISEA3H resolution [0..32] (0=coarsest, 32=finest)",
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
        help="Enable ISEA3H compact mode for polygons",
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
        choices=[
            "geojson",
            "geojson_dict",
            "gpkg",
            "parquet",
            "csv",
            "shapefile",
            None,
        ],
        help="Output format (default: geojson). Use 'geojson_dict' for Python dict, None for list of dicts.",
    )
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()  
    
    if not is_windows():
        print("ISEA3H DGGS conversion is only supported on Windows", file=sys.stderr)
        sys.exit(1)
    
    args.resolution = validate_isea3h_resolution(args.resolution)
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
        output_name = f"vector2isea3h{extensions.get(args.output_format, '')}"
    try:
        result = vector2isea3h(
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
            print(f"List of {len(result)} ISEA3H cell dicts returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2isea3h_cli()
