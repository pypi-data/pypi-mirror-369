"""
Vector to Geohash DGGS Grid Conversion Module
"""

import sys
import os
import argparse
from tqdm import tqdm
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from vgrid.conversion.dggs2geo.geohash2geo import geohash2geo
from vgrid.dggs import geohash
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.generator.geohashgrid import  expand_geohash_bbox
from vgrid.utils.constants import INITIAL_GEOHASHES

from vgrid.conversion.dggscompact.geohashcompact import geohashcompact
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from math import sqrt
from vgrid.utils.io import (
    validate_geohash_resolution,
    process_input_data_vector,
    convert_to_output_format,
)


def point2geohash(
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
    Convert a point geometry to a Geohash grid cell.

    Args:
        resolution (int): Geohash resolution [1..10]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable Geohash compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode - ensures disjoint points have disjoint Geohash cells
        include_properties (bool, optional): Whether to include properties in output
        all_points: List of all points for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing Geohash cells containing the point
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        # Geohash cell size (approx): each character increases resolution, cell size shrinks by ~1/8 to 1/32
        # We'll use a rough estimate: cell size halves every character, so use a lookup or formula
        # For simplicity, use a fixed table for WGS84 (meters) for geohash length 1-10
        geohash_cell_sizes = [
            5000000,
            1250000,
            156000,
            39100,
            4890,
            1220,
            153,
            38.2,
            4.77,
            1.19,
        ]  # meters
        for res in range(1, 11):
            cell_diameter = geohash_cell_sizes[res - 1] * sqrt(2) * 2
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 10
    
    geohash_rows = []
    longitude = point.x
    latitude = point.y
    geohash_id = geohash.encode(latitude, longitude, resolution)
    cell_polygon = geohash2geo(geohash_id)
    row = graticule_dggs_to_geoseries(
        "geohash", geohash_id, resolution, cell_polygon
    )
    if include_properties and feature_properties:
        row.update(feature_properties)
    geohash_rows.append(row)
    return geohash_rows


def polyline2geohash(
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
    Convert line geometries (LineString, MultiLineString) to Geohash grid cells.

    Args:
        resolution (int): Geohash resolution [1..10]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable Geohash compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polylines have disjoint Geohash cells
        include_properties (bool, optional): Whether to include properties in output
        all_polylines: List of all polylines for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing Geohash cells intersecting the line
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        geohash_cell_sizes = [
            5000000,
            1250000,
            156000,
            39100,
            4890,
            1220,
            153,
            38.2,
            4.77,
            1.19,
        ]  # meters
        for res in range(1, 11):
            cell_diameter = (
                geohash_cell_sizes[res - 1] * sqrt(2) * 4
            )  # in case there are 2 cells representing the same line segment
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 10
    geohash_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        intersected_geohashes = {
            gh
            for gh in INITIAL_GEOHASHES
            if geohash2geo(gh).intersects(polyline)
        }
        geohashes_bbox = set()
        for gh in intersected_geohashes:
            expand_geohash_bbox(gh, resolution, geohashes_bbox, polyline)
        
        for gh in geohashes_bbox:
            cell_polygon = geohash2geo(gh)
            row = graticule_dggs_to_geoseries(
                "geohash", gh, resolution, cell_polygon
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            geohash_rows.append(row)
    return geohash_rows


def polygon2geohash(
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
    Convert polygon geometries (Polygon, MultiPolygon) to Geohash grid cells.

    Args:
        resolution (int): Geohash resolution [1..10]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Geohash compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polygons have disjoint Geohash cells
        include_properties (bool, optional): Whether to include properties in output
        all_polygons: List of all polygons for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing Geohash cells based on predicate
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        geohash_cell_sizes = [
            5000000,
            1250000,
            156000,
            39100,
            4890,
            1220,
            153,
            38.2,
            4.77,
            1.19,
        ]  # meters
        for res in range(1, 11):
            cell_diameter = geohash_cell_sizes[res - 1] * sqrt(2) * 4
            if cell_diameter < shortest_distance:
                resolution = res
                break
        else:
            resolution = 10
    geohash_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        intersected_geohashes = {
            gh for gh in INITIAL_GEOHASHES if geohash2geo(gh).intersects(polygon)
        }
        geohashes_bbox = set()
        for gh in intersected_geohashes:
            expand_geohash_bbox(gh, resolution, geohashes_bbox, polygon)
        
        for gh in geohashes_bbox:
            cell_polygon = geohash2geo(gh)
            row = graticule_dggs_to_geoseries(
                "geohash", gh, resolution, cell_polygon
            )
            cell_geom = row["geometry"]
            if not check_predicate(cell_geom, polygon, predicate):
                continue
            if include_properties and feature_properties:
                row.update(feature_properties)
            geohash_rows.append(row)
    return geohash_rows


# --- Main geometry conversion ---
def geometry2geohash(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to Geohash grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): Geohash resolution [1..10]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Geohash compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with Geohash grid cells
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

    geohash_rows = []
    for i, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue
        props = properties_list[i] if i < len(properties_list) else {}
        if not include_properties:
            props = {}
        if geom.geom_type == "Point":
            geohash_rows.extend(
                point2geohash(
                    resolution,
                    geom,
                    props,
                    predicate,
                    False,  # compact handled at GeoDataFrame level
                    topology,
                    include_properties,
                    all_points,  # Pass all points for topology preservation
                )
            )
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                geohash_rows.extend(
                    point2geohash(
                        resolution,
                        pt,
                        props,
                        predicate,
                        False,  # compact handled at GeoDataFrame level
                        topology,
                        include_properties,
                        all_points,  # Pass all points for topology preservation
                    )
                )
        elif geom.geom_type in ("LineString", "MultiLineString"):
            geohash_rows.extend(
                polyline2geohash(
                    resolution,
                    geom,
                    props,
                    predicate,
                    False,  # compact handled at GeoDataFrame level
                    topology,
                    include_properties,
                    all_polylines,  # Pass all polylines for topology preservation
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            geohash_rows.extend(
                polygon2geohash(
                    resolution,
                    geom,
                    props,
                    predicate,
                    False,  # compact handled at GeoDataFrame level
                    topology,
                    include_properties,
                    all_polygons=all_polygons,  # Pass all polygons for topology preservation
                )
            )
    result_gdf = gpd.GeoDataFrame(geohash_rows, geometry="geometry", crs="EPSG:4326")
    
    return result_gdf


# --- DataFrame/GeoDataFrame conversion ---
def dataframe2geohash(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to Geohash grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): Geohash resolution [1..10]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Geohash compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with Geohash grid cells
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
    return geometry2geohash(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2geohash(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to Geohash grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): Geohash resolution [1..10]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable Geohash compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with Geohash grid cells
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
    return geometry2geohash(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


# --- Main vector2geohash function ---
def vector2geohash(
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
    Convert vector data to Geohash grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_geohash_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2geohash(
        gdf, resolution, predicate, compact, topology, include_properties
    )
    
    # Apply compaction if requested
    if compact:
        result = geohashcompact(result, geohash_id="geohash", output_format="gpd")

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
            output_name = f"{base}2geohash_{resolution}{ext}"
        else:
            output_name = f"geohash_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)



# --- CLI ---
def vector2geohash_cli():
    """
    Command-line interface for vector2geohash conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to Geohash grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(1, 11),
        metavar="[1-10]",
        help="Geohash resolution [1..10] (1=coarsest, 10=finest)",
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
        help="Enable Geohash compact mode for polygons",
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
    args.resolution = validate_geohash_resolution(args.resolution)

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
        output_name = f"vector2geohash{extensions.get(args.output_format, '')}"
    try:
        result = vector2geohash(
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
            print(f"List of {len(result)} Geohash cell dicts returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2geohash_cli()
