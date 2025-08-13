"""
A5 Grid Generator Module.
This module provides functionality to generate A5 DGGS grids.
"""

import json
import argparse
import geopandas as gpd
from tqdm import tqdm
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import convert_to_output_format
from a5.core.cell_info import get_num_cells
from vgrid.conversion.latlon2dggs import latlon2a5
from vgrid.conversion.dggs2geo.a52geo import a52geo
from vgrid.utils.io import validate_a5_resolution

def a5_grid(resolution, bbox):
    resolution = validate_a5_resolution(resolution)
    """
    Generate an A5 DGGS grid for a given resolution and bounding box.
    Based on JavaScript logic that creates a regular grid and converts centroids to A5 cells.
    
    Args:
        resolution (int): A5 resolution [0..29]
        bbox (list): Bounding box [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        GeoDataFrame: A5 grid cells within the bounding box
    """
    min_lng, min_lat, max_lng, max_lat = bbox
    
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
    
    a5_rows = []
    num_edges = 5
    seen_a5_hex = set()  # Track unique A5 hex codes
        
    # Generate features for each grid cell
    total_cells = len(longitudes) * len(latitudes)
    with tqdm(total=total_cells, desc="Generating A5 DGGS", unit=" cells") as pbar:
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
                        # Only add if this A5 hex code hasn't been seen before
                        if a5_hex not in seen_a5_hex:
                            seen_a5_hex.add(a5_hex)
                            
                            # Create row data
                            row = geodesic_dggs_to_geoseries(
                                "a5", a5_hex, resolution, cell_polygon, num_edges
                            )
                            a5_rows.append(row)
                
                except Exception as e:
                    # Skip cells that can't be processed
                    print(f"Error processing cell at ({centroid_lon}, {centroid_lat}): {e}")
                finally:
                    pbar.update(1)

    
    if not a5_rows:
        raise ValueError("No A5 cells were generated. Check the input parameters and A5 library functions.")
    
    return gpd.GeoDataFrame(a5_rows, geometry="geometry", crs="EPSG:4326")


def a5grid(resolution, bbox=None, output_format=None):
    """
    Generate A5 grid for pure Python usage.

    Args:
        resolution (int): A5 resolution [0..30]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output output_format ('geojson', 'csv', etc.). Defaults to None (list of A5 tokens).

    Returns:
        dict or list: GeoJSON FeatureCollection, list of A5 tokens, or file path depending on output_format
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        num_cells = get_num_cells(resolution)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
    gdf = a5_grid(resolution, bbox)
    
    base_name = f"a5_grid_{resolution}"
    if output_format is None:
        return gdf
    elif output_format in ["gpd", "geo"]:
        return gdf
    elif output_format == "geojson_dict":
        return gdf.__geo_interface__
    elif output_format == "geojson":
        output_name = base_name + ".geojson"
        geojson = gdf.__geo_interface__
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)
        return output_name
    elif output_format == "csv":
        output_name = base_name + ".csv"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "shapefile":
        output_name = base_name + ".shp"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format == "gpkg":
        output_name = base_name + ".gpkg"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    elif output_format in ["geoparquet", "parquet"]:
        output_name = base_name + ".parquet"
        return convert_to_output_format(gdf, output_format, output_name=output_name)
    else:
        return convert_to_output_format(gdf, output_format)


def a5grid_cli():
    """CLI interface for generating A5 DGGS."""
    parser = argparse.ArgumentParser(description="Generate A5 DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..29]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the output_format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=["geojson", "csv", "geo", "gpd", "shapefile", "gpkg", "parquet", None],
        default=None,
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of A5 IDs)",
    )
    args = parser.parse_args()
    # Ensure Python None, not string 'None'
    if args.output_format == "None":
        args.output_format = None
    try:
        result = a5grid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            # Print the entire Python list of A5 IDs at once
            print(result)
        elif args.output_format in ["geo", "gpd"]:
            print(result)
        elif args.output_format in [
            "csv",
            "parquet",
            "gpkg",
            "shapefile",
            "geojson",
        ] and isinstance(result, str):
            print(f"Output saved as {result}")
        elif args.output_format == "geojson" and isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"Output saved in current directory.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    a5grid_cli()
    