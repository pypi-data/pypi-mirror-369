"""
Vector2Tilecode Module

This module provides functionality to convert vector geometries to Tilecode grid cells.
Tilecode is a hierarchical geospatial indexing system based on Web Mercator tiles.

Key Features:
- Convert points, lines, and polygons to Tilecode cells
- Support for various spatial predicates (intersect, within, centroid_within, largest_overlap)
- Compact mode to reduce cells representing polygons
- Topology preserving mode for maintaining spatial relationships
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
"""

import sys
import os
import re
import argparse
from math import sqrt
from tqdm import tqdm
from shapely.geometry import Polygon, MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from vgrid.dggs import tilecode
from vgrid.dggs import mercantile
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.conversion.dggscompact.tilecodecompact import tilecodecompact
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from vgrid.utils.io import (
    validate_tilecode_resolution,
    process_input_data_vector,
    convert_to_output_format,
)


def point2tilecode(
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
    Convert a point geometry to a Tilecode grid cell.

    Args:
        resolution (int): Tilecode resolution [0..29]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable Tilecode compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode (not used for points)
        include_properties (bool, optional): Whether to include properties in output
        all_points (list, optional): List of points for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Tilecode cells containing the point
    """
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        tilecode_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = tilecode_cell_sizes[res] * sqrt(2) * 2
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    tilecode_rows = []
    tilecode_id = tilecode.latlon2tilecode(point.y, point.x, resolution)
    tilecode_cell = mercantile.tile(point.x, point.y, resolution)
    bounds = mercantile.bounds(tilecode_cell)
    if bounds:
        min_lat, min_lon = bounds.south, bounds.west
        max_lat, max_lon = bounds.north, bounds.east
        cell_polygon = Polygon(
            [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]
        )
        tilecode_row = graticule_dggs_to_geoseries("tilecode", tilecode_id, resolution, cell_polygon)
        if include_properties and feature_properties:
            tilecode_row.update(feature_properties)
        tilecode_rows.append(tilecode_row)
    return tilecode_rows


def polyline2tilecode(
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
    Convert line geometries (LineString, MultiLineString) to Tilecode grid cells.

    Args:
        resolution (int): Tilecode resolution [0..29]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable Tilecode compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for lines)
        include_properties (bool, optional): Whether to include properties in output
        all_polylines (list, optional): List of polylines for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Tilecode cells intersecting the line
    """
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        tilecode_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = tilecode_cell_sizes[res] * sqrt(2) * 4
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    tilecode_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        min_lon, min_lat, max_lon, max_lat = polyline.bounds
        tilecodes = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
        tilecode_ids = []
        for tile in tilecodes:
            tilecode_id = f"z{tile.z}x{tile.x}y{tile.y}"
            tilecode_ids.append(tilecode_id)
        for tilecode_id in tilecode_ids:
            match = re.match(r"z(\d+)x(\d+)y(\d+)", tilecode_id)
            if not match:
                raise ValueError(
                    "Invalid tilecode output_format. Expected output_format: 'zXxYyZ'"
                )
            cell_resolution = int(match.group(1))
            z = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            bounds = mercantile.bounds(x, y, z)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                cell_polygon = Polygon(
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]
                )
                if cell_polygon.intersects(polyline):
                    tilecode_row = graticule_dggs_to_geoseries("tilecode", tilecode_id, cell_resolution, cell_polygon)
                    if feature_properties:
                        tilecode_row.update(feature_properties)
                    tilecode_rows.append(tilecode_row)
    return tilecode_rows


def polygon2tilecode(
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
    Convert polygon geometries (Polygon, MultiPolygon) to Tilecode grid cells.

    Args:
        resolution (int): Tilecode resolution [0..29]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Tilecode compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (not used for polygons)
        include_properties (bool, optional): Whether to include properties in output
        all_polygons (list, optional): List of polygons for topology preservation

    Returns:
        list: List of GeoDataFrame format dictionaries representing Tilecode cells based on predicate
    """
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        tilecode_cell_sizes = [40075016.68557849 / (2**z) for z in range(30)]
        for res in range(0, 30):
            cell_diameter = tilecode_cell_sizes[res] * sqrt(2) * 4
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 29
    tilecode_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        min_lon, min_lat, max_lon, max_lat = polygon.bounds
        tilecodes = mercantile.tiles(min_lon, min_lat, max_lon, max_lat, resolution)
        tilecode_ids = []
        for tile in tilecodes:
            tilecode_id = f"z{tile.z}x{tile.x}y{tile.y}"
            tilecode_ids.append(tilecode_id)
        for tilecode_id in tilecode_ids:
            match = re.match(r"z(\d+)x(\d+)y(\d+)", tilecode_id)
            if not match:
                raise ValueError(
                    "Invalid tilecode output_format. Expected output_format: 'zXxYyZ'"
                )
            cell_resolution = int(match.group(1))
            z = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            bounds = mercantile.bounds(x, y, z)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                cell_polygon = Polygon(
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]
                )
                if check_predicate(cell_polygon, polygon, predicate):
                    tilecode_row = graticule_dggs_to_geoseries("tilecode", tilecode_id, cell_resolution, cell_polygon)
                    if include_properties and feature_properties:
                        tilecode_row.update(feature_properties)
                    tilecode_rows.append(tilecode_row)   
    return tilecode_rows


def geometry2tilecode(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to Tilecode grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): Tilecode resolution [0..29]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Tilecode compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Tilecode grid cells
    """
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

    tilecode_rows = []
    for i, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue
        props = properties_list[i] if i < len(properties_list) else {}
        if not include_properties:
            props = {}
        if geom.geom_type == "Point":
            tilecode_rows.extend(
                point2tilecode(
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
                tilecode_rows.extend(
                    point2tilecode(
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
            tilecode_rows.extend(
                polyline2tilecode(
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
            tilecode_rows.extend(
                polygon2tilecode(
                    resolution,
                    geom,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_polygons=all_polygons,  # Pass all polygons for topology preservation
                )
            )
    # Convert to GeoDataFrame
    return gpd.GeoDataFrame(tilecode_rows, geometry="geometry", crs="EPSG:4326")


def dataframe2tilecode(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to Tilecode grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): Tilecode resolution [0..29]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Tilecode compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Tilecode grid cells
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
    return geometry2tilecode(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2tilecode(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to Tilecode grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): Tilecode resolution [0..29]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Tilecode compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Tilecode grid cells
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
    return geometry2tilecode(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2tilecode(
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
    Convert vector data to Tilecode grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    The internal processing always uses GeoDataFrame format for consistency.
    """
    resolution = validate_tilecode_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    geometries = list(gdf.geometry)
    properties_list = [row.drop(labels=["geometry"]).to_dict() for idx, row in gdf.iterrows()]
    result = geometry2tilecode(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )
    if compact:
        result = tilecodecompact(result, tilecode_id="tilecode", output_format="gpd")
        
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
            output_name = f"{base}2tilecode_{resolution}{ext}"
        else:
            output_name = f"tilecode_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2tilecode_cli():
    """
    Command-line interface for vector2tilecode conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to Tilecode grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(0, 30),
        metavar="[0-29]",
        help="Tilecode resolution [0..29] (0=coarsest, 29=finest)",
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
        help="Enable Tilecode compact mode for polygons",
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
            "gpd",
            "geopandas",
            None,
        ],
        help="Output format (default: geojson). Use 'geojson_dict' for Python dict, None for GeoDataFrame, 'gpd' or 'geopandas' for GeoDataFrame.",
    )
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()
    args.resolution = validate_tilecode_resolution(args.resolution)
    data = args.input
    output_name = args.output
    if not output_name and args.output_format in [
        "geojson",
        "gpkg",
        "parquet",
        "csv",
        "shapefile",
        "gpd",
        "geopandas",
    ]:
        extensions = {
            "geojson": ".geojson",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "csv": ".csv",
            "shapefile": ".shp",
        }
        output_name = f"vector2tilecode{extensions.get(args.output_format, '')}"
    try:
        result = vector2tilecode(
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
            print(f"GeoJSON dict generated with {len(result['features'])} features.")
        elif args.output_format is None:
            print(f"GeoDataFrame with {len(result)} Tilecode cells returned.")
        elif args.output_format in ["gpd", "geopandas"]:
            print(f"GeoDataFrame with {len(result)} Tilecode cells returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2tilecode_cli()
