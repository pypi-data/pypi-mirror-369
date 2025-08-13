"""
S2 Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to S2 grid cells.
S2 is a hierarchical geospatial indexing system that divides the Earth's surface into cells of
varying resolutions, from 0 (coarsest) to 28 (finest).

Key Features:
- Convert points, lines, and polygons to S2 grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion
- Topology preservation mode to ensure disjoint features have disjoint S2 cells
- S2 compact mode to reduce cell count
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
"""

import sys
import os
import argparse
import math
from tqdm import tqdm
from pyproj import Geod
import geopandas as gpd
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
from vgrid.dggs import s2
from vgrid.utils.geometry import s2_cell_to_polygon
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance
)
from vgrid.stats.s2stats import s2_metrics
from vgrid.utils.io import validate_s2_resolution, process_input_data_vector, convert_to_output_format
geod = Geod(ellps="WGS84")


def point2s2(
    resolution,
    point,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,  # New parameter for topology preservation
):
    """
    Convert a single point geometry to S2 grid cells.

    Args:
        resolution (int): S2 resolution level [0..28]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable S2 compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode - ensures disjoint points have disjoint S2 cells
        include_properties (bool, optional): Whether to include properties in output
        all_points: List of all points for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing S2 cells containing the point

    Example:
        >>> from shapely.geometry import Point
        >>> point = Point(-122.4194, 37.7749)  # San Francisco
        >>> cells = point2s2(10, point, {"name": "SF"})
        >>> len(cells)
        1
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        
        # Calculate the shortest distance between all points
        shortest_distance = shortest_point_distance(all_points)
        
        # Find resolution where S2 cell size is smaller than shortest distance
        # This ensures disjoint points have disjoint S2 cells
        if shortest_distance > 0:
            for res in range(29):
                # Use s2_metrics to get accurate edge length
                _, avg_edge_length, _ = s2_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * math.sqrt(2) * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 28
        else:
            # Single point or no distance, use provided resolution
            pass

    s2_rows = []
    lat_lng = s2.LatLng.from_degrees(point.y, point.x)
    cell_id_max_res = s2.CellId.from_lat_lng(lat_lng)
    cell_id = cell_id_max_res.parent(resolution)
    s2_cell = s2.Cell(cell_id)
    cell_token = s2.CellId.to_token(s2_cell.id())
    if s2_cell:
        cell_polygon = s2_cell_to_polygon(cell_id)
        resolution = cell_id.level()
        num_edges = 4
        row = geodesic_dggs_to_geoseries(
            "s2", cell_token, resolution, cell_polygon, num_edges
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        s2_rows.append(row)
    return s2_rows


def polyline2hs2(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,  # New parameter for topology preservation
):
    """
    Convert line geometries (LineString, MultiLineString) to S2 grid cells.

    Args:
        resolution (int): S2 resolution level [0..28]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable S2 compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polylines have disjoint S2 cells
        include_properties (bool, optional): Whether to include properties in output
        all_polylines: List of all polylines for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing S2 cells intersecting the line

    Example:
        >>> from shapely.geometry import LineString
        >>> line = LineString([(-122.4194, 37.7749), (-122.4000, 37.7800)])
        >>> cells = polyline2hs2(10, line, {"name": "route"})
        >>> len(cells) > 0
        True
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        
        # Calculate the shortest distance between all polylines
        shortest_distance = shortest_polyline_distance(all_polylines)
        
        # Find resolution where S2 cell size is smaller than shortest distance
        # This ensures disjoint polylines have disjoint S2 cells
        if shortest_distance > 0:
            for res in range(29):
                # Use s2_metrics to get accurate edge length
                _, avg_edge_length, _ = s2_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * math.sqrt(2) * 2  # in case there are 2 cells representing the same line segment
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 28
        else:
            # Single polyline or no distance, use provided resolution
            pass

    s2_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        min_lng, min_lat, max_lng, max_lat = polyline.bounds
        level = resolution
        coverer = s2.RegionCoverer()
        coverer.min_level = level
        coverer.max_level = level
        region = s2.LatLngRect(
            s2.LatLng.from_degrees(min_lat, min_lng),
            s2.LatLng.from_degrees(max_lat, max_lng),
        )
        covering = coverer.get_covering(region)
        cell_ids = covering        
        for cell_id in cell_ids:
            cell_polygon = s2_cell_to_polygon(cell_id)
            if not cell_polygon.intersects(polyline):
                continue
            cell_token = s2.CellId.to_token(cell_id)
            cell_resolution = cell_id.level()
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "s2", cell_token, cell_resolution, cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            s2_rows.append(row)
    return s2_rows


def polygon2hs2(
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,  # New parameter for topology preservation
):
    """
    Convert polygon geometries (Polygon, MultiPolygon) to S2 grid cells.

    Args:
        resolution (int): S2 resolution level [0..28]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable S2 compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polygons have disjoint S2 cells
        include_properties (bool, optional): Whether to include properties in output
        all_polygons: List of all polygons for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing S2 cells based on predicate

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])
        >>> cells = polygon2hs2(10, poly, {"name": "area"}, predicate="intersect")
        >>> len(cells) > 0
        True
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        
        # Calculate the shortest distance between all polygons
        shortest_distance = shortest_polygon_distance(all_polygons)
        
        # Find resolution where S2 cell size is smaller than shortest distance
        # This ensures disjoint polygons have disjoint S2 cells
        if shortest_distance > 0:
            for res in range(29):
                # Use s2_metrics to get accurate edge length
                _, avg_edge_length, _ = s2_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * math.sqrt(2) * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 28
        else:
            # Single polygon or no distance, use provided resolution
            pass

    s2_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    
    for polygon in polygons:
        min_lng, min_lat, max_lng, max_lat = polygon.bounds
        level = resolution
        coverer = s2.RegionCoverer()
        coverer.min_level = level
        coverer.max_level = level
        region = s2.LatLngRect(
            s2.LatLng.from_degrees(min_lat, min_lng),
            s2.LatLng.from_degrees(max_lat, max_lng),
        )
        covering = coverer.get_covering(region)
        cell_ids = covering
        if compact:
            covering = s2.CellUnion(covering)
            covering.normalize()
            cell_ids = covering.cell_ids()
        
        for cell_id in cell_ids:
            cell_polygon = s2_cell_to_polygon(cell_id)
            if not check_predicate(cell_polygon, polygon, predicate):
                continue
            cell_token = s2.CellId.to_token(cell_id)
            cell_resolution = cell_id.level()
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "s2", cell_token, cell_resolution, cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            s2_rows.append(row)
    
    return s2_rows


# --- Main geometry conversion ---
def geometry2s2(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to S2 grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): S2 resolution level [0..28]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable S2 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with S2 grid cells

    Example:
        >>> from shapely.geometry import Point, Polygon
        >>> geoms = [Point(-122.4194, 37.7749), Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])]
        >>> props = [{"name": "point"}, {"name": "polygon"}]
        >>> result = geometry2s2(geoms, 10, props, predicate="intersect")
        >>> result["type"]
        'FeatureCollection'
    """
    resolution = validate_s2_resolution(resolution)

    # Handle single geometry or list of geometries
    if not isinstance(geometries, list):
        geometries = [geometries]

    # Handle properties
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    # Collect all points, polylines, and polygons for topology preservation if needed
    all_points = None
    all_polylines = None
    all_polygons = None
    if topology:
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

    s2_rows = []
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
            s2_rows.extend(
                point2s2(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_points,  # Pass all points for topology preservation
                )
            )
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                s2_rows.extend(
                    point2s2(
                        resolution,
                        pt,
                        props,
                        predicate,
                        compact,
                        topology,
                        include_properties,
                        all_points,  # Pass all points for topology preservation
                    )
                )
        elif geom.geom_type in ("LineString", "MultiLineString"):
            s2_rows.extend(
                polyline2hs2(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polylines,  # Pass all polylines for topology preservation
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            s2_rows.extend(
                polygon2hs2(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polygons,  # Pass all polygons for topology preservation
                )
            )    
    return gpd.GeoDataFrame(s2_rows, geometry="geometry", crs="EPSG:4326")


# --- DataFrame/GeoDataFrame conversion ---
def dataframe2s2(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to S2 grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): S2 resolution level [0..28]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable S2 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with S2 grid cells

    Example:
        >>> import pandas as pd
        >>> from shapely.geometry import Point
        >>> df = pd.DataFrame({
        ...     'geometry': [Point(-122.4194, 37.7749)],
        ...     'name': ['San Francisco']
        ... })
        >>> result = dataframe2s2(df, 10)
        >>> result["type"]
        'FeatureCollection'
    """
    geometries = []
    properties_list = []
    for _, row in df.iterrows():
        geom = row.geometry if "geometry" in row else row["geometry"]
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)
    return geometry2s2(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2s2(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to S2 grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): S2 resolution level [0..28]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable S2 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with S2 grid cells

    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Point
        >>> gdf = gpd.GeoDataFrame({
        ...     'name': ['San Francisco'],
        ...     'geometry': [Point(-122.4194, 37.7749)]
        ... })
        >>> result = geodataframe2s2(gdf, 10)
        >>> result["type"]
        'FeatureCollection'
    """
    geometries = []
    properties_list = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            properties_list.append(props)
    return geometry2s2(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


# --- Main vector2s2 function ---
def vector2s2(
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
    Convert vector data to S2 grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_s2_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2s2(
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
            output_name = f"{base}2s2_{resolution}{ext}"
        else:
            output_name = f"s2_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


# --- CLI ---
def vector2s2_cli():
    """
    Command-line interface for vector2s2 conversion.
    """
    parser = argparse.ArgumentParser(description="Convert vector data to S2 grid cells")
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(29),
        metavar="[0-28]",
        help="S2 resolution [0..28] (0=coarsest, 28=finest)",
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
        help="Enable S2 compact mode for polygons",
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
    args.resolution = validate_s2_resolution(args.resolution)
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
        output_name = f"vector2s2{extensions.get(args.output_format, '')}"
    try:
        result = vector2s2(
            data,
            args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            output_format=args.output_format,
            output_name=output_name,
            include_properties=args.include_properties,
        )
        if args.output_format == "geojson":
            print(f"Output saved to {result}")
        elif args.output_format == "geojson_dict":
            print(f"GeoJSON dict generated with {len(result)} features.")
        elif args.output_format is None:
            print(f"GeoDataFrame with {len(result)} S2 cell rows returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2s2_cli()
