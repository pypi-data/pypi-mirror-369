"""
Vector to EASE DGGS Grid Conversion Module
"""

import sys
import os
import argparse
from tqdm import tqdm
from shapely.geometry import  box, MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.dggs.easedggs.constants import levels_specs, geo_crs, ease_crs
from vgrid.dggs.easedggs.dggs.grid_addressing import (    
    geos_to_grid_ids,
    geo_polygon_to_grid_ids,
)
from vgrid.conversion.dggscompact.easecompact import ease_compact
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from vgrid.utils.io import validate_ease_resolution, process_input_data_vector, convert_to_output_format
from vgrid.conversion.dggs2geo.ease2geo import ease2geo
from vgrid.conversion.latlon2dggs import latlon2ease


def point2ease(
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
    Convert a single point geometry to EASE grid cell.

    Args:
        resolution (int): EASE resolution level [0..6]
        point (shapely.geometry.Point): Point geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable EASE compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode - ensures disjoint points have disjoint EASE cells
        include_properties (bool, optional): Whether to include properties in output
        all_points: List of all points for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing EASE cells containing the point
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        
        # Calculate the shortest distance between all points
        shortest_distance = shortest_point_distance(all_points)
        
        # Find resolution where EASE cell size is smaller than shortest distance
        # This ensures disjoint points have disjoint EASE cells
        if shortest_distance > 0:
            for res in range(7):  # EASE resolution range is [0..6]
                if res in levels_specs:
                    cell_width = levels_specs[res]["x_length"]
                    # Use a factor to ensure sufficient separation (cell diagonal is ~1.4x cell width)
                    cell_diagonal = cell_width * 1.4
                    if cell_diagonal < shortest_distance:
                        resolution = res
                        break
            else:
                # If no resolution found, use the highest resolution
                resolution = 6
        else:
            # Single point or no distance, use provided resolution
            pass
    ease_rows = []
    ease_id = latlon2ease(point.y, point.x, resolution)
    cell_polygon = ease2geo(ease_id)
    if cell_polygon:
        num_edges = 4
        row = geodesic_dggs_to_geoseries(
            "ease", ease_id, int(ease_id[1]), cell_polygon, num_edges
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        ease_rows.append(row)
    return ease_rows


def polyline2ease(
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
    Convert line geometries (LineString, MultiLineString) to EASE grid cells.

    Args:
        resolution (int): EASE resolution level [0..6]
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Line geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for lines)
        compact (bool, optional): Enable EASE compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polylines have disjoint EASE cells
        include_properties (bool, optional): Whether to include properties in output
        all_polylines: List of all polylines for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing EASE cells intersecting the line
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        
        # Calculate the shortest distance between all polylines
        shortest_distance = shortest_polyline_distance(all_polylines)
        
        # Find resolution where EASE cell size is smaller than shortest distance
        # This ensures disjoint polylines have disjoint EASE cells
        if shortest_distance > 0:
            for res in range(7):  # EASE resolution range is [0..6]
                if res in levels_specs:
                    cell_width = levels_specs[res]["x_length"]
                    # Use a factor to ensure sufficient separation (cell diagonal is ~1.4x cell width)
                    cell_diagonal = cell_width * 2.8  # in case there are 2 cells representing the same line segment
                    if cell_diagonal < shortest_distance:
                        resolution = res
                        break
            else:
                # If no resolution found, use the highest resolution
                resolution = 6
        else:
            # Single polyline or no distance, use provided resolution
            pass
    ease_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []

    for polyline in polylines:
        poly_bbox = box(*polyline.bounds)
        polygon_bbox_wkt = poly_bbox.wkt
        cells_bbox = geo_polygon_to_grid_ids(
            polygon_bbox_wkt,
            resolution,
            geo_crs,
            ease_crs,
            levels_specs,
            return_centroids=True,
            wkt_geom=True,
        )
        ease_ids = cells_bbox["result"]["data"]
        if compact:
            ease_ids = ease_compact(ease_ids)
        for ease_id in ease_ids:
            cell_resolution = int(ease_id[1])
            # Use ease2geo to get the cell geometry
            cell_polygon = ease2geo(ease_id)
            if cell_polygon and cell_polygon.intersects(polyline):
                num_edges = 4
                row = geodesic_dggs_to_geoseries(
                    "ease", str(ease_id), cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                ease_rows.append(row)
    return ease_rows


def polygon2ease(
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
    Convert polygon geometries (Polygon, MultiPolygon) to EASE grid cells.

    Args:
        resolution (int): EASE resolution level [0..6]
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable EASE compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode - ensures disjoint polygons have disjoint EASE cells
        include_properties (bool, optional): Whether to include properties in output
        all_polygons: List of all polygons for topology preservation (required when topology=True)

    Returns:
        list: List of GeoJSON feature dictionaries representing EASE cells based on predicate
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        
        # Calculate the shortest distance between all polygons
        shortest_distance = shortest_polygon_distance(all_polygons)
        
        # Find resolution where EASE cell size is smaller than shortest distance
        # This ensures disjoint polygons have disjoint EASE cells
        if shortest_distance > 0:
            for res in range(7):  # EASE resolution range is [0..6]
                if res in levels_specs:
                    cell_width = levels_specs[res]["x_length"]
                    # Use a factor to ensure sufficient separation (cell diagonal is ~1.4x cell width)
                    cell_diagonal = cell_width * 2.8
                    if cell_diagonal < shortest_distance:
                        resolution = res
                        break
            else:
                # If no resolution found, use the highest resolution
                resolution = 6
        else:
            # Single polygon or no distance, use provided resolution
            pass
    ease_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        poly_bbox = box(*polygon.bounds)
        polygon_bbox_wkt = poly_bbox.wkt
        cells_bbox = geo_polygon_to_grid_ids(
            polygon_bbox_wkt,
            resolution,
            geo_crs,
            ease_crs,
            levels_specs,
            return_centroids=True,
            wkt_geom=True,
        )
        ease_ids = cells_bbox["result"]["data"]
        if not ease_ids:
            continue
        if compact:
            ease_ids = ease_compact(ease_ids)
        for ease_id in ease_ids:
            cell_resolution = int(ease_id[1])
            # Use ease2geo to get the cell geometry
            cell_polygon = ease2geo(ease_id)
            if cell_polygon and check_predicate(cell_polygon, polygon, predicate):
                num_edges = 4
                row = geodesic_dggs_to_geoseries(
                    "ease", str(ease_id), cell_resolution, cell_polygon, num_edges
                )
                if feature_properties:
                    row.update(feature_properties)
                ease_rows.append(row)
    return ease_rows


# --- Main geometry conversion ---
def geometry2ease(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to EASE grid cells.

    Args:
        geometries (shapely.geometry.BaseGeometry or list): Single geometry or list of geometries
        resolution (int): EASE resolution level [0..6]
        properties_list (list, optional): List of property dictionaries for each geometry
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable EASE compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with EASE grid cells
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

    ease_rows = []
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
            ease_rows.extend(
                point2ease(
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
                ease_rows.extend(
                    point2ease(
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
            ease_rows.extend(
                polyline2ease(
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
            ease_rows.extend(
                polygon2ease(
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
    if ease_rows:
        gdf = gpd.GeoDataFrame(ease_rows, geometry="geometry", crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    return gdf


# --- DataFrame/GeoDataFrame conversion ---
def dataframe2ease(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to EASE grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): EASE resolution level [0..6]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable EASE compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with EASE grid cells
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
    return geometry2ease(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2ease(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to EASE grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): EASE resolution level [0..6]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable EASE compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with EASE grid cells
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
    return geometry2ease(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


# --- Main vector2ease function ---
def vector2ease(
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
    Convert vector data to EASE grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_ease_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2ease(
        gdf, resolution, predicate, compact, topology, include_properties
    )
    file_formats = ["csv", "geojson", "shapefile", "gpkg", "parquet", "geoparquet"]
    output_name = kwargs.get("output_name", None)
    if output_format in file_formats and output_name is None:
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
            output_name = f"{base}2ease_{resolution}{ext}"
        else:
            output_name = f"ease_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


# --- CLI ---
def vector2ease_cli():
    """
    Command-line interface for vector2ease conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to EASE grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(7),
        metavar="[0-6]",
        help="EASE resolution [0..6] (0=coarsest, 6=finest)",
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
        help="Enable EASE compact mode for polygons",
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
    args.resolution = validate_ease_resolution(args.resolution)
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
        output_name = f"vector2ease{extensions.get(args.output_format, '')}"
    try:
        result = vector2ease(
            data,
            args.resolution,
            predicate=args.predicate,
            topology=args.topology,
            compact=args.compact,
            output_format=args.output_format,
            output_name=output_name,
            include_properties=args.include_properties,
        )
        if args.output_format == "geojson":
            print(f"Output saved to {result}")
        elif args.output_format == "geojson_dict":
            print(f"GeoJSON dict generated with {len(result['features'])} features.")
        elif args.output_format is None:
            print(f"List of {len(result)} EASE cell dicts returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2ease_cli()
