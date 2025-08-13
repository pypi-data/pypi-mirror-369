"""
Vector to rHEALPix DGGS Grid Conversion Module
"""

import sys
import os
import argparse
from shapely.geometry import box, MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from tqdm import tqdm
from vgrid.dggs.rhealpixdggs.dggs import RHEALPixDGGS
from vgrid.utils.geometry import geodesic_dggs_to_geoseries, rhealpix_cell_to_polygon
from vgrid.conversion.dggscompact.rhealpixcompact import rhealpix_compact
from vgrid.utils.geometry import check_predicate
from vgrid.stats.rhealpixstats import rhealpix_metrics
from vgrid.utils.geometry import (
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from vgrid.utils.io import validate_rhealpix_resolution
from vgrid.utils.io import process_input_data_vector, convert_to_output_format
rhealpix_dggs = RHEALPixDGGS()

def point2rhealpix(
    rhealpix_dggs,
    resolution,
    point,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,
):
    """Convert point geometry to rHEALPix grid cells.
    
    Args:
        rhealpix_dggs: RHEALPixDGGS instance
        resolution: rHEALPix resolution level
        point: Point geometry
        feature_properties: Optional properties to include
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        all_points: All points for topology preservation
        
    Returns:
        list: List of rHEALPix feature dictionaries
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        shortest_distance = shortest_point_distance(all_points)
        # print(shortest_distance)
        if shortest_distance > 0:
            for res in range(16):
                _, avg_edge_length, _ = rhealpix_metrics(res)
                cell_diameter = avg_edge_length * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 15
    
    rhealpix_rows = []
    seed_cell = rhealpix_dggs.cell_from_point(
        resolution, (point.x, point.y), plane=False
    )

    seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)
    if seed_cell_polygon:
        seed_cell_id = str(seed_cell)
        num_edges = 4
        if seed_cell.ellipsoidal_shape() == "dart":
            num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "rhealpix", seed_cell_id, resolution, seed_cell_polygon, num_edges
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        rhealpix_rows.append(row)
    return rhealpix_rows


def polyline2rhealpix(
    rhealpix_dggs,
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,
):
    """Convert polyline geometry to rHEALPix grid cells.
    
    Args:
        rhealpix_dggs: RHEALPixDGGS instance
        resolution: rHEALPix resolution level
        feature: LineString or MultiLineString geometry
        feature_properties: Optional properties to include
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        all_polylines: All polylines for topology preservation
        
    Returns:
        list: List of rHEALPix feature dictionaries
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        shortest_distance = shortest_polyline_distance(all_polylines)
        if shortest_distance > 0:
            for res in range(16):
                _, avg_edge_length, _ = rhealpix_metrics(res)
                cell_diameter = avg_edge_length * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 15
    rhealpix_rows = []
    polylines = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)

    for polyline in polylines:
        minx, miny, maxx, maxy = polyline.bounds
        bbox_polygon = box(minx, miny, maxx, maxy)
        bbox_center_lon = bbox_polygon.centroid.x
        bbox_center_lat = bbox_polygon.centroid.y
        seed_point = (bbox_center_lon, bbox_center_lat)
        seed_cell = rhealpix_dggs.cell_from_point(resolution, seed_point, plane=False)
        seed_cell_id = str(seed_cell)
        seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)
        if seed_cell_polygon.contains(bbox_polygon):
            num_edges = 4
            if seed_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            cell_resolution = resolution
            row = geodesic_dggs_to_geoseries(
                "rhealpix", seed_cell_id, cell_resolution, seed_cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            rhealpix_rows.append(row)
            return rhealpix_rows
        else:
            covered_cells = set()
            queue = [seed_cell]
            while queue:
                current_cell = queue.pop()
                current_cell_id = str(current_cell)
                if current_cell_id in covered_cells:
                    continue
                covered_cells.add(current_cell_id)
                cell_polygon = rhealpix_cell_to_polygon(current_cell)
                if not cell_polygon.intersects(bbox_polygon):
                    continue
                neighbors = current_cell.neighbors(plane=False)
                for _, neighbor in neighbors.items():
                    neighbor_id = str(neighbor)
                    if neighbor_id not in covered_cells:
                        queue.append(neighbor)

            for cell_id in covered_cells:
                rhealpix_uids = (cell_id[0],) + tuple(map(int, cell_id[1:]))
                rhelpix_cell = rhealpix_dggs.cell(rhealpix_uids)
                cell_resolution = rhelpix_cell.resolution
                cell_polygon = rhealpix_cell_to_polygon(rhelpix_cell)
                if not cell_polygon.intersects(polyline):
                    continue
                num_edges = 4
                if seed_cell.ellipsoidal_shape() == "dart":
                    num_edges = 3
                row = geodesic_dggs_to_geoseries(
                    "rhealpix", str(cell_id), cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                rhealpix_rows.append(row)

 

    return rhealpix_rows


def polygon2rhealpix(
    rhealpix_dggs,
    resolution,
    feature,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,
):
    """Convert polygon geometry to rHEALPix grid cells.
    
    Args:
        rhealpix_dggs: RHEALPixDGGS instance
        resolution: rHEALPix resolution level
        feature: Polygon or MultiPolygon geometry
        feature_properties: Optional properties to include
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        all_polygons: All polygons for topology preservation
        
    Returns:
        list: List of rHEALPix feature dictionaries
    """
     # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        shortest_distance = shortest_polygon_distance(all_polygons)
        if shortest_distance > 0:
            for res in range(16):
                _, avg_edge_length, _ = rhealpix_metrics(res)
                cell_diameter = avg_edge_length * 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                resolution = 15
    rhealpix_rows = []
    polygons = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)

    for polygon in polygons:
        minx, miny, maxx, maxy = polygon.bounds
        bbox_polygon = box(minx, miny, maxx, maxy)
        bbox_center_lon = bbox_polygon.centroid.x
        bbox_center_lat = bbox_polygon.centroid.y
        seed_point = (bbox_center_lon, bbox_center_lat)
        seed_cell = rhealpix_dggs.cell_from_point(resolution, seed_point, plane=False)
        seed_cell_id = str(seed_cell)
        seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)
        if seed_cell_polygon.contains(bbox_polygon):
            num_edges = 4
            if seed_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            cell_resolution = resolution
            row = geodesic_dggs_to_geoseries(
                "rhealpix", seed_cell_id, cell_resolution, seed_cell_polygon, num_edges
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            rhealpix_rows.append(row)
            return rhealpix_rows
        else:
            covered_cells = set()
            queue = [seed_cell]
            while queue:
                current_cell = queue.pop()
                current_cell_id = str(current_cell)
                if current_cell_id in covered_cells:
                    continue
                covered_cells.add(current_cell_id)
                cell_polygon = rhealpix_cell_to_polygon(current_cell)
                if not cell_polygon.intersects(bbox_polygon):
                    continue
                neighbors = current_cell.neighbors(plane=False)
                for _, neighbor in neighbors.items():
                    neighbor_id = str(neighbor)
                    if neighbor_id not in covered_cells:
                        queue.append(neighbor)
            # Compact mode: just pass covered_cells (not rhealpix_dggs)
            if compact:                
                covered_cells = rhealpix_compact(covered_cells)
            for cell_id in covered_cells:
                rhealpix_uids = (cell_id[0],) + tuple(map(int, cell_id[1:]))
                rhelpix_cell = rhealpix_dggs.cell(rhealpix_uids)
                cell_resolution = rhelpix_cell.resolution
                cell_polygon = rhealpix_cell_to_polygon(rhelpix_cell)
                if not check_predicate(cell_polygon, polygon, predicate):
                    continue
                num_edges = 4
                if seed_cell.ellipsoidal_shape() == "dart":
                    num_edges = 3
                row = geodesic_dggs_to_geoseries(
                    "rhealpix", str(cell_id), cell_resolution, cell_polygon, num_edges
                )
                if include_properties and feature_properties:
                    row.update(feature_properties)
                rhealpix_rows.append(row)

    return rhealpix_rows


def geometry2rhealpix(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """Convert list of geometries to rHEALPix grid cells.
    
    Args:
        geometries: Single geometry or list of geometries
        resolution: rHEALPix resolution level
        properties_list: Optional list of properties for each geometry
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        
    Returns:
        dict: GeoJSON FeatureCollection with rHEALPix features
    """
    # Handle single geometry or list of geometries
    if not isinstance(geometries, list):
        geometries = [geometries]

    # Handle properties
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    
    rhealpix_rows = []

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
            rhealpix_rows.extend(
                point2rhealpix(
                    rhealpix_dggs,
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
                rhealpix_rows.extend(
                    point2rhealpix(
                        rhealpix_dggs,
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
            rhealpix_rows.extend(
                polyline2rhealpix(
                    rhealpix_dggs,
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
            rhealpix_rows.extend(
                polygon2rhealpix(
                    rhealpix_dggs,
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
    return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")


def dataframe2rhealpix(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """Convert pandas DataFrame with geometry column to rHEALPix grid cells.
    
    Args:
        df: pandas DataFrame with geometry column
        resolution: rHEALPix resolution level
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        
    Returns:
        dict: GeoJSON FeatureCollection with rHEALPix features
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
    return geometry2rhealpix(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2rhealpix(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """Convert GeoDataFrame to rHEALPix grid cells.
    
    Args:
        gdf: GeoDataFrame with geometry column
        resolution: rHEALPix resolution level
        predicate: Spatial predicate for filtering
        compact: Enable compact mode
        topology: Enable topology preserving mode
        include_properties: Whether to include properties
        
    Returns:
        dict: GeoJSON FeatureCollection with rHEALPix features
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
    return geometry2rhealpix(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2rhealpix(
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
    Convert vector data to rHEALPix grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_rhealpix_resolution(resolution)
    gdf = process_input_data_vector(data, **kwargs)
    result = geodataframe2rhealpix(
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
            output_name = f"{base}2rhealpix_{resolution}{ext}"
        else:
            output_name = f"rhealpix_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2rhealpix_cli():
    """
    Command-line interface for vector2rhealpix conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to rHEALPix grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(16),
        metavar="[0-15]",
        help="rHEALPix resolution [0..15] (0=coarsest, 15=finest)",
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
        help="Enable rHEALPix compact mode for polygons",
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
    args.resolution = validate_rhealpix_resolution(args.resolution)
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
        output_name = f"vector2rhealpix{extensions.get(args.output_format, '')}"
    try:
        result = vector2rhealpix(
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
            print(f"GeoDataFrame with {len(result)} rHEALPix cell rows returned.")
        elif output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2rhealpix_cli()
