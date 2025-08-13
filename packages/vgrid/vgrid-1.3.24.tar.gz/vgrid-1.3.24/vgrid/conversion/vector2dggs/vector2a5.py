"""
A5 Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to A5 grid cells.
A5 is a hierarchical geospatial indexing system that divides the Earth's surface into cells of
varying resolutions, from 0 (coarsest) to 28 (finest).

Key Features:
- Convert points, lines, and polygons to A5 grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion
- Topology preservation mode to ensure disjoint features have disjoint A5 cells
- A5 compact mode to reduce cell count
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
import a5
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance
)
from vgrid.utils.io import validate_a5_resolution, process_input_data_vector, convert_to_output_format
from vgrid.conversion.latlon2dggs import latlon2a5
from vgrid.conversion.dggs2geo.a52geo import a52geo
from vgrid.conversion.dggscompact.a5compact import a5compact
from vgrid.stats.a5stats import a5_metrics
geod = Geod(ellps="WGS84")


def point2a5(
    resolution=None,
    point=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,  # New parameter for topology preservation
):
    """
    Convert a single point geometry to A5 grid cells.

    Args:
        resolution (int, optional): A5 resolution level [0..29]. Required when topology=False, auto-calculated when topology=True
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable A5 compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode - ensures disjoint points have disjoint A5 cells
        include_properties (bool, optional): Whether to include properties in output
        all_points: List of all points for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing A5 cells containing the point

    Example:
        >>> from shapely.geometry import Point
        >>> point = Point(-122.4194, 37.7749)  # San Francisco
        >>> cells = point2a5(10, point, {"name": "SF"})
        >>> len(cells)
        1
    """
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        
        # Calculate the shortest distance between all points
        shortest_distance = shortest_point_distance(all_points)
        
        # Find resolution where A5 cell size is smaller than shortest distance
        # This ensures disjoint points have disjoint A5 cells
        if shortest_distance > 0:
            for res in range(30):
                # Use a5_metrics to get accurate edge length
                _, avg_edge_length, _ = a5_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length*1.4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 29
        else:
            # Single point or no distance, use provided resolution
            pass

    a5_rows = []
    a5_hex = latlon2a5(point.y, point.x, resolution)
    cell_polygon = a52geo(a5_hex)     
    resolution = a5.get_resolution(a5.hex_to_bigint(a5_hex))
    num_edges = 4
    row = geodesic_dggs_to_geoseries(
        "a5", a5_hex, resolution, cell_polygon, num_edges
    )
    if include_properties and feature_properties:
        row.update(feature_properties)
    a5_rows.append(row)
    return a5_rows


def polyline2a5(
    resolution=None,
    feature=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,  # New parameter for topology preservation
):
    """
    Convert line geometries (LineString, MultiLineString) to A5 grid cells.

    Args:
        resolution (int, optional): A5 resolution level [0..29]. Required when topology=False, auto-calculated when topology=True
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable A5 compact mode (not used for lines)
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polylines have disjoint A5 cells
        include_properties (bool, optional): Whether to include properties in output
        all_polylines: List of all polylines for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing A5 cells intersecting the line

    Example:
        >>> from shapely.geometry import LineString
        >>> line = LineString([(-122.4194, 37.7749), (-122.4000, 37.7800)])
        >>> cells = polyline2a5(10, line, {"name": "route"})
        >>> len(cells) > 0
        True
    """
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        
        # Calculate the shortest distance between all polylines
        shortest_distance = shortest_polyline_distance(all_polylines)
        
        # Find resolution where A5 cell size is smaller than shortest distance
        # This ensures disjoint polylines have disjoint A5 cells
        if shortest_distance > 0:
            for res in range(30):
                # Use a5_metrics to get accurate edge length
                _, avg_edge_length, _ = a5_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * 1.4  # in case there are 2 cells representing the same line segment
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 29
        else:
            # Single polyline or no distance, use provided resolution
            pass

    a5_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        min_lng, min_lat, max_lng, max_lat = polyline.bounds
        
        # Calculate longitude and latitude width based on resolution
        if resolution == 0:
            # For resolution 0, use larger width
            lon_width = 35
            lat_width = 35
        elif resolution == 1:
            lon_width = 18
            lat_width = 18
        elif resolution == 2:
            lon_width = 10
            lat_width = 10
        elif resolution == 3:
            lon_width = 5
            lat_width = 5
        elif resolution > 3:
            base_width = 5  # at resolution 3
            factor = 0.5 ** (resolution - 3)
            lon_width = base_width * factor
            lat_width = base_width * factor
               
        # Generate longitude and latitude arrays
        longitudes = []
        latitudes = []
        
        lon = min_lng
        while lon < max_lng:
            longitudes.append(lon)
            lon += lon_width
        
        lat = min_lat
        while lat < max_lat:
            latitudes.append(lat)
            lat += lat_width
        
        seen_a5_hex = set()  # Track unique A5 hex codes
        
        # Generate and check each grid cell
        for lon in longitudes:
            for lat in latitudes:
                min_lon = lon
                min_lat = lat
                max_lon = lon + lon_width
                max_lat = lat + lat_width
                
                # Calculate centroid
                centroid_lat = (min_lat + max_lat) / 2
                centroid_lon = (min_lon + max_lon) / 2
                
                try:
                    # Convert centroid to A5 cell ID using direct A5 functions
                    a5_hex = latlon2a5(centroid_lat, centroid_lon, resolution)
                    cell_polygon = a52geo(a5_hex)
                    
                    if cell_polygon is not None:                        
                        # Only process if this A5 hex code hasn't been seen before
                        if a5_hex not in seen_a5_hex:
                            seen_a5_hex.add(a5_hex)                            
                            # Check if cell intersects with polyline
                            if cell_polygon.intersects(polyline):
                                cell_resolution = a5.get_resolution(a5.hex_to_bigint(a5_hex))
                                num_edges = 4
                                row = geodesic_dggs_to_geoseries(
                                    "a5", a5_hex, cell_resolution, cell_polygon, num_edges
                                )
                                if include_properties and feature_properties:
                                    row.update(feature_properties)
                                a5_rows.append(row)
                        
                except Exception as e:
                    # Skip cells that can't be processed
                    continue
    
    return a5_rows


def polygon2a5(
    resolution=None,
    feature=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,  # New parameter for topology preservation
):
    """
    Convert polygon geometries (Polygon, MultiPolygon) to A5 grid cells.

    Args:
        resolution (int, optional): A5 resolution level [0..29]. Required when topology=False, auto-calculated when topology=True
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable A5 compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polygons have disjoint A5 cells
        include_properties (bool, optional): Whether to include properties in output
        all_polygons: List of all polygons for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing A5 cells based on predicate

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])
        >>> cells = polygon2a5(10, poly, {"name": "area"}, predicate="intersect")
        >>> len(cells) > 0
        True
    """
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        
        # Calculate the shortest distance between all polygons
        shortest_distance = shortest_polygon_distance(all_polygons)
        
        # Find resolution where A5 cell size is smaller than shortest distance
        # This ensures disjoint polygons have disjoint A5 cells
        if shortest_distance > 0:
            for res in range(29):
                # Use a5_metrics to get accurate edge length
                _, avg_edge_length, _ = a5_metrics(res)
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

    a5_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    
    for polygon in polygons:
        min_lng, min_lat, max_lng, max_lat = polygon.bounds
        
        # Calculate longitude and latitude width based on resolution
        if resolution == 0:
            lon_width = 35
            lat_width = 35
        elif resolution == 1:
            lon_width = 18
            lat_width = 18
        elif resolution == 2:
            lon_width = 10
            lat_width = 10
        elif resolution == 3:
            lon_width = 5
            lat_width = 5
        elif resolution > 3:
            base_width = 5  # at resolution 3
            factor = 0.5 ** (resolution - 3)
            lon_width = base_width * factor
            lat_width = base_width * factor
                
        # Generate longitude and latitude arrays
        longitudes = []
        latitudes = []
        
        lon = min_lng
        while lon < max_lng:
            longitudes.append(lon)
            lon += lon_width
        
        lat = min_lat
        while lat < max_lat:
            latitudes.append(lat)
            lat += lat_width
        
        seen_a5_hex = set()  # Track unique A5 hex codes
        
        # Generate and check each grid cell
        for lon in longitudes:
            for lat in latitudes:
                min_lon = lon
                min_lat = lat
                max_lon = lon + lon_width
                max_lat = lat + lat_width
                
                # Calculate centroid
                centroid_lat = (min_lat + max_lat) / 2
                centroid_lon = (min_lon + max_lon) / 2
                
                try:
                    # Convert centroid to A5 cell ID using direct A5 functions
                    a5_hex = latlon2a5(centroid_lat, centroid_lon, resolution)
                    cell_polygon = a52geo(a5_hex)
                    
                    # Only process if this A5 hex code hasn't been seen before
                    if a5_hex not in seen_a5_hex:
                        seen_a5_hex.add(a5_hex)
                        
                        # Check if cell satisfies the predicate with polygon
                        if check_predicate(cell_polygon, polygon, predicate):
                            cell_resolution = a5.get_resolution(a5.hex_to_bigint(a5_hex))
                            num_edges = 4
                            row = geodesic_dggs_to_geoseries(
                                "a5", a5_hex, cell_resolution, cell_polygon, num_edges
                            )
                            if include_properties and feature_properties:
                                row.update(feature_properties)
                            a5_rows.append(row)
                        
                except Exception as e:
                    # Skip cells that can't be processed
                    continue
    
    # Apply compact mode if enabled
    if compact and a5_rows:
        # Create a GeoDataFrame from the current results
        temp_gdf = gpd.GeoDataFrame(a5_rows, geometry="geometry", crs="EPSG:4326")
        
        # Use a5compact function directly
        compacted_gdf = a5compact(temp_gdf, a5_hex="a5", output_format="gpd")
        
        if compacted_gdf is not None:
            # Convert back to list of dictionaries
            a5_rows = compacted_gdf.to_dict('records')
        # If compaction failed, keep original results
    
    return a5_rows


# --- Main geometry conversion ---
def geometry2a5(
    geometries,
    resolution=None,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to A5 grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int, optional): A5 resolution level [0..29]. Required when topology=False, auto-calculated when topology=True
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable A5 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with A5 grid cells

    Example:
        >>> from shapely.geometry import Point, Polygon
        >>> geoms = [Point(-122.4194, 37.7749), Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])]
        >>> props = [{"name": "point"}, {"name": "polygon"}]
        >>> result = geometry2a5(geoms, 10, props, predicate="intersect")
        >>> result["type"]
        'FeatureCollection'
    """ 
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    if resolution is not None:
        resolution = validate_a5_resolution(resolution)

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

    a5_rows = []
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
            a5_rows.extend(
                point2a5(
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
                a5_rows.extend(
                    point2a5(
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
            a5_rows.extend(
                polyline2a5(
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
            a5_rows.extend(
                polygon2a5(
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
    return gpd.GeoDataFrame(a5_rows, geometry="geometry", crs="EPSG:4326")


# --- DataFrame/GeoDataFrame conversion ---
def dataframe2a5(
    df,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to A5 grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int, optional): A5 resolution level [0..28]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable A5 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with A5 grid cells

    Example:
        >>> import pandas as pd
        >>> from shapely.geometry import Point
        >>> df = pd.DataFrame({
        ...     'geometry': [Point(-122.4194, 37.7749)],
        ...     'name': ['San Francisco']
        ... })
        >>> result = dataframe2a5(df, 10)
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
    return geometry2a5(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2a5(
    gdf,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to A5 grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int, optional): A5 resolution level [0..28]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable A5 compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with A5 grid cells

    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Point
        >>> gdf = gpd.GeoDataFrame({
        ...     'name': ['San Francisco'],
        ...         'geometry': [Point(-122.4194, 37.7749)]
        ... })
        >>> result = geodataframe2a5(gdf, 10)
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
    return geometry2a5(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


# --- Main vector2a5 function ---
def vector2a5(
    data,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    output_format=None,
    include_properties=True,
    **kwargs,
):
    """
    Convert vector data to A5 grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_a5_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2a5(
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
            if resolution is not None:
                output_name = f"{base}2a5_{resolution}{ext}"
            else:
                output_name = f"{base}2a5_topology{ext}"
        else:
            if resolution is not None:
                output_name = f"a5_{resolution}{ext}"
            else:
                output_name = f"a5_topology{ext}"
    return convert_to_output_format(result, output_format, output_name)


# --- CLI ---
def vector2a5_cli():
    """
    Command-line interface for vector2a5 conversion.
    """
    parser = argparse.ArgumentParser(description="Convert vector data to A5 grid cells")
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(30    ),
        metavar="[0-29]",
        help="A5 resolution [0..29] (0=coarsest, 29=finest). Required when topology=False, auto-calculated when topology=True",
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
        help="Enable A5 compact mode for polygons",
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
    args.resolution = validate_a5_resolution(args.resolution)
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
        output_name = f"vector2a5{extensions.get(args.output_format, '')}"
    try:
        result = vector2a5(
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
            print(f"GeoDataFrame with {len(result)} A5 cell rows returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2a5_cli()
