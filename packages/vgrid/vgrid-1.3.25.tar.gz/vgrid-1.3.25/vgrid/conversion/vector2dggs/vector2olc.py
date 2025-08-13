import sys
import os
import argparse
from tqdm import tqdm
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
import geopandas as gpd
from vgrid.dggs import olc
from vgrid.generator.olcgrid import olc_grid, olc_refine_cell
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
    shortest_polyline_distance,
    shortest_polygon_distance,
)
from vgrid.stats.olcstats import olc_metrics
from math import sqrt
from vgrid.utils.io import validate_olc_resolution, convert_to_output_format, process_input_data_vector
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.conversion.dggs2geo.olc2geo import olc2geo
from vgrid.conversion.dggscompact.olccompact import olccompact


def point2olc(
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
    Convert a point geometry to an OLC grid cell.
    Returns a list of dicts suitable for GeoDataFrame construction.
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_points is None:
            raise ValueError("all_points parameter is required when topology=True")
        
        # Calculate the shortest distance between all points
        shortest_distance = shortest_point_distance(all_points)
        
        # Find resolution where OLC cell size is smaller than shortest distance
        # This ensures disjoint points have disjoint OLC cells
        if shortest_distance > 0:
            for res in [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]:  # OLC valid resolutions
                _, avg_edge_length, _ = olc_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * sqrt(2)* 2
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single point or no distance, use provided resolution
            pass

    olc_rows = []
    olc_id = olc.encode(point.y, point.x, resolution)
    cell_polygon = olc2geo(olc_id)
    if cell_polygon:
        olc_row = graticule_dggs_to_geoseries("olc", olc_id, resolution, cell_polygon)
        if include_properties and feature_properties:
            olc_row.update(feature_properties)
        olc_rows.append(olc_row)
    return olc_rows


def polyline2olc(
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
    Convert line geometries (LineString, MultiLineString) to OLC grid cells.
    Returns a list of dicts suitable for GeoDataFrame construction.
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polylines is None:
            raise ValueError("all_polylines parameter is required when topology=True")
        
        # Calculate the shortest distance between all polylines
        shortest_distance = shortest_polyline_distance(all_polylines)
        
        # Find resolution where OLC cell size is smaller than shortest distance
        # This ensures disjoint polylines have disjoint OLC cells
        if shortest_distance > 0:
            for res in [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]:  # OLC valid resolutions
                _, avg_edge_length, _ = olc_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * sqrt(2) * 4  # in case there are 2 cells representing the same line segment
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single polyline or no distance, use provided resolution
            pass
    olc_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        base_resolution = 2
        base_cells = olc_grid(base_resolution, verbose=False)
        seed_cells = []
        for idx, base_cell in base_cells.iterrows():
            base_cell_poly = base_cell["geometry"]
            if polyline.intersects(base_cell_poly):
                seed_cells.append(base_cell)
        refined_features = []
        for seed_cell in seed_cells:
            seed_cell_poly = seed_cell["geometry"]
            if seed_cell_poly.contains(polyline) and resolution == base_resolution:
                refined_features.append(seed_cell)
            else:
                refined_features.extend(
                    olc_refine_cell(
                        seed_cell_poly.bounds, base_resolution, resolution, polyline
                    )
                )
        # refined_features may be a mix of GeoDataFrame rows and dicts from refine_cell
        # Normalize all to dicts for downstream processing
        normalized_features = []
        for feat in refined_features:
            if isinstance(feat, dict):
                normalized_features.append(feat)
            else:
                # Convert GeoDataFrame row to dict
                d = dict(feat)
                d["geometry"] = feat["geometry"]
                normalized_features.append(d)
        resolution_features = [
            refined_feature
            for refined_feature in normalized_features
            if refined_feature["resolution"] == resolution
        ]
        seen_olc_codes = set()
        for resolution_feature in resolution_features:
            olc_id = resolution_feature["olc"]
            if olc_id not in seen_olc_codes:
                cell_polygon = olc2geo(olc_id)
                olc_row = graticule_dggs_to_geoseries("olc", olc_id, resolution, cell_polygon)
                if include_properties and feature_properties:
                    olc_row.update(feature_properties)
                olc_rows.append(olc_row)
                seen_olc_codes.add(olc_id)
    # Compact mode not supported for geoseries output
    return olc_rows


def polygon2olc(
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
    Convert polygon geometries (Polygon, MultiPolygon) to OLC grid cells.
    Returns a list of dicts suitable for GeoDataFrame construction.
    """
    # If topology preservation is enabled, calculate appropriate resolution
    if topology:
        if all_polygons is None:
            raise ValueError("all_polygons parameter is required when topology=True")
        
        # Calculate the shortest distance between all polygons
        shortest_distance = shortest_polygon_distance(all_polygons)
        
        # Find resolution where OLC cell size is smaller than shortest distance
        # This ensures disjoint polygons have disjoint OLC cells
        if shortest_distance > 0:
            for res in [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]:  # OLC valid resolutions
                _, avg_edge_length, _ = olc_metrics(res)
                # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                cell_diameter = avg_edge_length * sqrt(2) * 4
                if cell_diameter < shortest_distance:
                    resolution = res
                    break
            else:
                # If no resolution found, use the highest resolution
                resolution = 15
        else:
            # Single polygon or no distance, use provided resolution
            pass
    olc_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    for polygon in polygons:
        base_resolution = 2
        base_cells = olc_grid(base_resolution, verbose=False)
        seed_cells = []
        for idx, base_cell in base_cells.iterrows():
            base_cell_poly = base_cell["geometry"]
            if polygon.intersects(base_cell_poly):
                seed_cells.append(base_cell)
        refined_features = []
        for seed_cell in seed_cells:
            seed_cell_poly = seed_cell["geometry"]
            if seed_cell_poly.contains(polygon) and resolution == base_resolution:
                refined_features.append(seed_cell)
            else:
                refined_features.extend(
                    olc_refine_cell(
                        seed_cell_poly.bounds, base_resolution, resolution, polygon
                    )
                )
        # refined_features may be a mix of GeoDataFrame rows and dicts from refine_cell
        # Normalize all to dicts for downstream processing
        normalized_features = []
        for feat in refined_features:
            if isinstance(feat, dict):
                normalized_features.append(feat)
            else:
                # Convert GeoDataFrame row to dict
                d = dict(feat)
                d["geometry"] = feat["geometry"]
                normalized_features.append(d)
        resolution_features = [
            refined_feature
            for refined_feature in normalized_features
            if refined_feature["resolution"] == resolution
        ]
        seen_olc_codes = set()
        for resolution_feature in resolution_features:
            olc_id = resolution_feature["olc"]
            if olc_id not in seen_olc_codes:
                cell_geom = olc2geo(olc_id)
                if not check_predicate(cell_geom, polygon, predicate):
                    continue
                olc_row = graticule_dggs_to_geoseries("olc", olc_id, resolution, cell_geom)
                if include_properties and feature_properties:
                    olc_row.update(feature_properties)
                olc_rows.append(olc_row)
                seen_olc_codes.add(olc_id)
    # Compact mode not supported for geoseries output
    return olc_rows


def geometry2olc(
    geometries,
    resolution,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a list of geometries to OLC grid cells.
    Returns a GeoDataFrame with OLC grid cells.
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

    olc_rows = []

    for i, geom in enumerate(tqdm(geometries, desc="Processing features")):
        if geom is None:
            continue

        # Get properties for this geometry
        props = properties_list[i] if i < len(properties_list) else {}

        # Process based on geometry type
        if geom.geom_type == "Point":
            point_features = point2olc(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_points,  # Pass all points for topology preservation
            )
            olc_rows.extend(point_features)

        elif geom.geom_type == "MultiPoint":
            for point in geom.geoms:
                point_features = point2olc(
                    resolution,
                    point,
                    props,
                    predicate,
                    compact,
                    topology,
                    include_properties,
                    all_points,  # Pass all points for topology preservation
                )
                olc_rows.extend(point_features)

        elif geom.geom_type in ["LineString", "MultiLineString"]:
            polyline_features = polyline2olc(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_polylines,  # Pass all polylines for topology preservation
            )
            olc_rows.extend(polyline_features)

        elif geom.geom_type in ["Polygon", "MultiPolygon"]:
            poly_features = polygon2olc(
                resolution,
                geom,
                props,
                predicate,
                compact,
                topology,
                include_properties,
                all_polygons=all_polygons,  # Pass all polygons for topology preservation
            )
            olc_rows.extend(poly_features)

        else:
            raise ValueError(f"Unsupported geometry type: {geom.geom_type}")

    result_gdf = gpd.GeoDataFrame(olc_rows, geometry="geometry", crs="EPSG:4326")
    
    return result_gdf


def dataframe2olc(
    df,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a pandas DataFrame with geometry column to OLC grid cells.

    Args:
        df (pandas.DataFrame): DataFrame with geometry column
        resolution (int): OLC resolution [2,4,6,8,10,11,12,13,14,15]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable OLC compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with OLC grid cells
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
    return geometry2olc(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def geodataframe2olc(
    gdf,
    resolution,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to OLC grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int): OLC resolution [2,4,6,8,10,11,12,13,14,15]
        predicate (str, optional): Spatial predicate to apply for polygons
        compact (bool, optional): Enable OLC compact mode for polygons and lines
        topology (bool, optional): Enable topology preserving mode
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        dict: GeoJSON FeatureCollection with OLC grid cells
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
    return geometry2olc(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )


def vector2olc(
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
    Convert vector data to OLC grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    """
    resolution = validate_olc_resolution(resolution)
    gdf = process_input_data_vector(data)
    geometries = list(gdf.geometry)
    properties_list = [row.drop(labels=["geometry"]).to_dict() for idx, row in gdf.iterrows()]
    result = geometry2olc(
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
    )
    # Apply compact if requested and result is a GeoDataFrame
    if compact:
        result = olccompact(result, olc_id="olc", output_format="gpd")
    
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
            output_name = f"{base}2olc_{resolution}{ext}"
        else:
            output_name = f"olc_{resolution}{ext}"
    return convert_to_output_format(result, output_format, output_name)


def vector2olc_cli():
    """
    Command-line interface for vector2olc conversion.

    Usage:
        python vector2olc.py -i input.shp -r 10 -c -f geojson -o output.geojson

    Arguments:
        -i, --input: Input file path or URL
        -r, --resolution: OLC resolution (see OLC spec)
        -c, --compact: Enable OLC compact mode
        -p, --predicate: Spatial predicate (intersect, within, centroid_within, largest_overlap)
        -t, --topology: Enable topology preserving mode
        -np, --no-props: Do not include original feature properties
        -f, --output_format: Output output_format (geojson, gpkg, parquet, csv, shapefile)
        -o, --output: Output file path
    """
    parser = argparse.ArgumentParser(
        description="Convert vector data to OLC grid cells"
    )
    parser.add_argument("-i", "--input", help="Input file path, URL")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=[2, 4, 6, 8, 10, 11, 12, 13, 14, 15],
        metavar="[2,4,6,8,10,11,12,13,14,15]",
        help="OLC resolution (see OLC spec)",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Enable OLC compact mode for polygons",
    )
    parser.add_argument(
        "-p",
        "--predicate",
        choices=["intersect", "within", "centroid_within", "largest_overlap"],
        help="Spatial predicate: intersect, within, centroid_within, largest_overlap for polygons",
    )
    parser.add_argument(
        "-t", "--topology", action="store_true", 
        help="Enable topology preserving mode ensuring disjoint features have disjoint OLC cells by automatically calculating appropriate resolution."
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
        choices=["geojson", "gpkg", "parquet", "csv", "shapefile"],
        help="Output output_format (default: geojson)",
    )
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()
    args.resolution = validate_olc_resolution(args.resolution)
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
        output_name = f"vector2olc{extensions.get(args.output_format, '')}"
    try:
        vector2olc(
            data,
            args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            output_format=args.output_format,
            output_name=output_name,
            include_properties=args.include_properties,
        )
        if output_name:
            print(f"Output saved to {output_name}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2olc_cli()
