"""Convert vector data to H3 grid cells."""

import sys
import os
import argparse        
from tqdm import tqdm
import geopandas as gpd
from shapely.geometry import box,MultiPoint, MultiLineString, MultiPolygon
from vgrid.conversion.dggs2geo.h32geo import h32geo
import h3
from vgrid.utils.geometry import (
    geodesic_buffer,
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
    geodesic_dggs_to_geoseries
    
)
from vgrid.utils.io import process_input_data_vector, convert_to_output_format
from vgrid.utils.io import validate_h3_resolution


# Function to generate grid for Point
# --- Replace geojson feature output with geoseries dict output ---
def point2h3(
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
    Convert a point to H3 grid cells.

    Args:
        resolution (int): H3 resolution [0..15]
        point: Shapely Point geometry
        feature_properties (dict): Properties to add to the H3 features
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode
        topology (bool): Enable H3 topology preserving mode - ensures disjoint points have disjoint H3 cells
        include_properties (bool): If False, do not include original feature properties
        all_points: List of all points for topology preservation (required when topology=True)

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        
        # Calculate the shortest distance between all points
        shortest_distance = shortest_point_distance(all_points)
        
        # Find resolution where H3 cell size is smaller than shortest distance
        # This ensures disjoint points have disjoint H3 cells
        if shortest_distance > 0:
            for res in range(16):
                avg_edge_length = h3.average_hexagon_edge_length(res=res, unit="m")
                # Use a factor to ensure sufficient separation (hexagon diameter is ~2x edge length)
                hexagon_diameter = avg_edge_length*2 
                if hexagon_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single point or no distance, use provided resolution
            pass

    h3_rows = []
    # Convert point to the seed cell
    h3_id = h3.latlng_to_cell(point.y, point.x, resolution)

    cell_polygon = h32geo(h3_id)
    if cell_polygon:
        num_edges = 6
        if h3.is_pentagon(h3_id):
            num_edges = 5
        row = geodesic_dggs_to_geoseries(
            "h3", h3_id, resolution, cell_polygon, num_edges
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        h3_rows.append(row)

    return h3_rows

# --- Polyline ---
def polyline2h3(
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
    Convert a polyline to H3 grid cells.

    Args:
        resolution (int): H3 resolution [0..15]
        feature: Shapely LineString or MultiLineString geometry
        feature_properties (dict): Properties to add to the H3 features
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode
        topology (bool): Enable H3 topology preserving mode - ensures disjoint polylines have disjoint H3 cells
        include_properties (bool): If False, do not include original feature properties
        all_polylines: List of all polylines for topology preservation (required when topology=True)

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        
        # Calculate the shortest distance between all polylines
        shortest_distance = shortest_polyline_distance(all_polylines)
        
        # Find resolution where H3 cell size is smaller than shortest distance
        # This ensures disjoint polylines have disjoint H3 cells
        if shortest_distance > 0:
            for res in range(16):
                avg_edge_length = h3.average_hexagon_edge_length(res=res, unit="m")
                # Use a factor to ensure sufficient separation (hexagon diameter is ~2x edge length)
                hexagon_diameter = avg_edge_length * 4 # in case there are 2 cells representing the same line segment
                if hexagon_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single polyline or no distance, use provided resolution
            pass

    h3_rows = []
    if feature.geom_type == "LineString":
        polylines = [feature]
    elif feature.geom_type == "MultiLineString":
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        bbox = box(*polyline.bounds)
        distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
        bbox_buffer = geodesic_buffer(bbox, distance)
        bbox_buffer_cells = h3.geo_to_cells(bbox_buffer, resolution)

        for bbox_buffer_cell in bbox_buffer_cells:
            cell_polygon = h32geo(bbox_buffer_cell)

            # Use the check_predicate function to determine if we should keep this cell
            if not check_predicate(cell_polygon, polyline, "intersects"):
                continue  # Skip non-matching cells

            cell_resolution = h3.get_resolution(bbox_buffer_cell)
            num_edges = 6
            if h3.is_pentagon(bbox_buffer_cell):
                num_edges = 5
            row = geodesic_dggs_to_geoseries(
                "h3", bbox_buffer_cell, cell_resolution, cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            h3_rows.append(row)

    return h3_rows

# --- Polygon ---
def polygon2h3(
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
    Convert a polygon to H3 grid cells.

    Args:
        resolution (int): H3 resolution [0..15]
        feature: Shapely Polygon or MultiPolygon geometry
        feature_properties (dict): Properties to add to the H3 features
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode
        topology (bool): Enable H3 topology preserving mode - ensures disjoint polygons have disjoint H3 cells
        include_properties (bool): If False, do not include original feature properties
        all_polygons: List of all polygons for topology preservation (required when topology=True)

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        
       
        # Calculate the shortest distance between all polygons
        shortest_distance = shortest_polygon_distance(all_polygons)
        
        # Find resolution where H3 cell size is smaller than shortest distance
        # This ensures disjoint polygons have disjoint H3 cells
        if shortest_distance > 0:
            for res in range(16):
                avg_edge_length = h3.average_hexagon_edge_length(res=res, unit="m")
                # Use a factor to ensure sufficient separation (hexagon diameter is ~2x edge length)
                hexagon_diameter = avg_edge_length * 4
                if hexagon_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single polygon or no distance, use provided resolution
            pass

    h3_rows = []
    if feature.geom_type == "Polygon":
        polygons = [feature]
    elif feature.geom_type == "MultiPolygon":
        polygons = list(feature.geoms)
    else:
        return []
    
    for polygon in polygons:
        bbox = box(*polygon.bounds)
        distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
        bbox_buffer = geodesic_buffer(bbox, distance)
        bbox_buffer_cells = h3.geo_to_cells(bbox_buffer, resolution)
        if compact:
            bbox_buffer_cells = h3.compact_cells(bbox_buffer_cells)
            
        for bbox_buffer_cell in bbox_buffer_cells:
            cell_polygon = h32geo(bbox_buffer_cell)
            # Use the check_predicate function to determine if we should keep this cell
            if not check_predicate(cell_polygon, polygon, predicate):
                continue  # Skip non-matching cells

            cell_resolution = h3.get_resolution(bbox_buffer_cell)
            num_edges = 6
            if h3.is_pentagon(bbox_buffer_cell):
                num_edges = 5
            row = geodesic_dggs_to_geoseries(
                "h3", bbox_buffer_cell, cell_resolution, cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            h3_rows.append(row)

    return h3_rows

# --- Geometry2h3 ---
def geometry2h3(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert Shapely geometry objects directly to H3 grid cells without converting to GeoJSON first.

    Args:
        geometries: Single Shapely geometry or list of Shapely geometries
        resolution (int): H3 resolution [0..15]
        properties_list: List of property dictionaries (optional)
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode - for polygon only
        topology (bool): Enable H3 topology preserving mode
        include_properties (bool): If False, do not include original feature properties

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
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

    h3_rows = []

    for i, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue

        # Get properties for this geometry
        props = properties_list[i] if i < len(properties_list) else {}

        # Process based on geometry type
        if geom.geom_type == "Point":
            h3_rows.extend(point2h3(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_points,  # Pass all points for topology preservation
            ))

        elif geom.geom_type == "MultiPoint":
            for point in geom.geoms:
                h3_rows.extend(point2h3(
                    resolution,
                    point,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_points,  # Pass all points for topology preservation
                ))

        elif geom.geom_type in ["LineString", "MultiLineString"]:
            h3_rows.extend(polyline2h3(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_polylines,  # Pass all polylines for topology preservation
            ))

        elif geom.geom_type in ["Polygon", "MultiPolygon"]:
            h3_rows.extend(polygon2h3(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_polygons=all_polygons,  # Pass all polygons for topology preservation
            ))

        else:
            raise ValueError(f"Unsupported geometry type: {geom.geom_type}")

    return h3_rows

# --- DataFrame/GeoDataFrame conversion ---
def dataframe2h3(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert pandas DataFrame with geometry column to H3 grid cells by converting to Shapely geometries first.

    Args:
        df (pd.DataFrame): Input DataFrame with geometry column
        resolution (int): H3 resolution [0..15]
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode - for polygon only
        topology (bool): Enable H3 topology preserving mode
        include_properties (bool): If False, do not include original feature properties

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
    """
    # Find geometry column
    geometry_col = None
    for col in df.columns:
        if hasattr(df[col].iloc[0], "geom_type") or hasattr(
            df[col].iloc[0], "__geo_interface__"
        ):
            geometry_col = col
            break

    if geometry_col is None:
        raise ValueError(
            "DataFrame must contain a geometry column with Shapely geometry objects"
        )

    # Extract geometries and properties from DataFrame
    geometries = []
    properties_list = []

    for _, row in df.iterrows():
        # Get the geometry
        geom = row[geometry_col]
        if geom is not None:
            geometries.append(geom)

            # Get properties (exclude geometry column)
            properties = row.to_dict()
            if geometry_col in properties:
                del properties[geometry_col]
            properties_list.append(properties)

    # Use geometry2h3 to process the geometries
    h3_rows = geometry2h3(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )
    return h3_rows


def geodataframe2h3(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert GeoDataFrame to H3 grid cells by converting to Shapely geometries first.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame
        resolution (int): H3 resolution [0..15]
        predicate (str or int): Spatial predicate to apply (see check_predicate function)
        compact (bool): Enable H3 compact mode - for polygon only
        topology (bool): Enable H3 topology preserving mode
        include_properties (bool): If False, do not include original feature properties

    Returns:
        dict: GeoJSON FeatureCollection containing H3 grid cells
    """
    # Extract geometries and properties from GeoDataFrame
    geometries = []
    properties_list = []

    for _, row in gdf.iterrows():
        # Get the geometry
        geom = row.geometry
        if geom is not None:
            geometries.append(geom)

            # Get properties (exclude geometry column)
            properties = row.to_dict()
            if "geometry" in properties:
                del properties["geometry"]
            properties_list.append(properties)

    # Use geometry2h3 to process the geometries
    h3_rows = geometry2h3(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )
    # Return as GeoDataFrame
    return gpd.GeoDataFrame(h3_rows, geometry="geometry", crs="EPSG:4326")


def vector2h3(
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
    Convert vector data to H3 grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_h3_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2h3(
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
            output_name = f"{base}2h3_{resolution}{ext}"
        else:
            output_name = f"h3_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2h3_cli():
    """Command-line interface for vector2h3 conversion."""
    parser = argparse.ArgumentParser(description="Convert vector data to H3 grid cells")
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(16),
        metavar="[0-15]",
        help="H3 resolution [0..15] (0=coarsest, 15=finest)",
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
        help="Enable H3 compact mode for polygons",
    )
    parser.add_argument(
        "-t", "--topology", action="store_true", 
        help="Enable topology preserving mode ensuring disjoint features have disjoint H3 cells by automatically calculating appropriate resolution."
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

    # Validate resolution if provided
    args.resolution = validate_h3_resolution(args.resolution)

    # Handle input (no stdin support)
    data = args.input

    # Handle output path
    output_name = args.output

    # If output path is not specified but output_format requires a file, generate default name
    if not output_name and args.output_format in [
        "geojson",
        "gpkg",
        "parquet",
        "csv",
        "shapefile",
    ]:
        # Generate default filename based on output_format
        extensions = {
            "geojson": ".geojson",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
            "csv": ".csv",
            "shapefile": ".shp",
        }
        output_name = f"vector2h3{extensions.get(args.output_format, '')}"

    try:
        result = vector2h3(
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
            print(f"List of {len(result)} H3 cell dicts returned.")
        elif output_name:
            print(f"Output saved to {output_name}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2h3_cli()
