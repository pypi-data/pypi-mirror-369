"""
Maidenhead DGGS Grid Generator Module
Reference:
    https://github.com/ha8tks/Leaflet.Maidenhead
    https://ha8tks.github.io/Leaflet.Maidenhead/examples/
    https://www.sotamaps.org/
"""

import json
import math
import argparse
from vgrid.dggs import maidenhead
import geopandas as gpd
from tqdm import tqdm
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import validate_maidenhead_resolution, convert_to_output_format
from vgrid.conversion.dggs2geo.maidenhead2geo import maidenhead2geo

def maidenhead_grid(resolution):
    resolution = validate_maidenhead_resolution(resolution)
    if resolution == 1:
        lon_width, lat_width = 20, 10
    elif resolution == 2:
        lon_width, lat_width = 2, 1
    elif resolution == 3:
        lon_width, lat_width = 0.083333, 0.041666  # 5 minutes x 2.5 minutes
    elif resolution == 4:
        lon_width, lat_width = 0.008333, 0.004167  # 30 seconds x 15 seconds
    else:
        raise ValueError("Unsupported resolution")

    # Determine the bounding box
    min_lon, min_lat, max_lon, max_lat = [-180, -90, 180, 90]
    x_cells = int((max_lon - min_lon) / lon_width)
    y_cells = int((max_lat - min_lat) / lat_width)
    total_cells = x_cells * y_cells

    maidenhead_records = []
    with tqdm(total=total_cells, desc="Generating Maidenhead DGGS", unit=" cells") as pbar:
        for i in range(x_cells):
            for j in range(y_cells):
                cell_min_lon = min_lon + i * lon_width
                cell_max_lon = cell_min_lon + lon_width
                cell_min_lat = min_lat + j * lat_width
                cell_max_lat = cell_min_lat + lat_width

                cell_center_lat = (cell_min_lat + cell_max_lat) / 2
                cell_center_lon = (cell_min_lon + cell_max_lon) / 2
                maidenhead_id = maidenhead.toMaiden(cell_center_lat, cell_center_lon, resolution)
                cell_polygon = maidenhead2geo(maidenhead_id)
                             
                maidenhead_record = graticule_dggs_to_geoseries('maidenhead',maidenhead_id,resolution,cell_polygon)
                maidenhead_records.append(maidenhead_record)
                pbar.update(1)

    return gpd.GeoDataFrame(maidenhead_records, geometry="geometry", crs="EPSG:4326")

def maidenhead_grid_within_bbox(resolution, bbox):
    resolution = validate_maidenhead_resolution(resolution)
    # Define the grid parameters based on the resolution
    if resolution == 1:
        lon_width, lat_width = 20, 10 # 20 degrees x 10 degrees
    elif resolution == 2:
        lon_width, lat_width = 2, 1 # 2 degrees x 1 degree
    elif resolution == 3:
        lon_width, lat_width = 0.083333, 0.041666  # 5 minutes x 2.5 minutes
    elif resolution == 4:
        lon_width, lat_width = 0.008333, 0.004167  # 30 seconds x 15 seconds
    else:
        raise ValueError("Unsupported resolution")

    min_lon, min_lat, max_lon, max_lat = bbox

    # Calculate grid cell indices for the bounding box
    base_lat, base_lon = -90, -180
    start_x = math.floor((min_lon - base_lon) / lon_width)
    end_x = math.floor((max_lon - base_lon) / lon_width)
    start_y = math.floor((min_lat - base_lat) / lat_width)
    end_y = math.floor((max_lat - base_lat) / lat_width)

    maidenhead_records = []

    total_cells = (end_x - start_x + 1) * (end_y - start_y + 1)

    # Loop through all intersecting grid cells with tqdm progress bar
    with tqdm(total=total_cells, desc="Generating Maidenhead DGGS") as pbar:
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                # Calculate the cell bounds
                cell_min_lon = base_lon + x * lon_width
                cell_max_lon = cell_min_lon + lon_width
                cell_min_lat = base_lat + y * lat_width
                cell_max_lat = cell_min_lat + lat_width

                # Ensure the cell intersects with the bounding box
                if not (cell_max_lon < min_lon or cell_min_lon > max_lon or
                        cell_max_lat < min_lat or cell_min_lat > max_lat):
                    # Center point for the Maidenhead code
                    cell_center_lat = (cell_min_lat + cell_max_lat) / 2
                    cell_center_lon = (cell_min_lon + cell_max_lon) / 2
                    
                    maidenhead_id = maidenhead.toMaiden(cell_center_lat, cell_center_lon, resolution)
                    cell_polygon = maidenhead2geo(maidenhead_id)            
                    
                    maidenhead_record = graticule_dggs_to_geoseries('maidenhead',maidenhead_id,resolution,cell_polygon)
                 
                    maidenhead_records.append(maidenhead_record)

                pbar.update(1)

    return gpd.GeoDataFrame(maidenhead_records, geometry="geometry", crs="EPSG:4326")
   

def maidenheadgrid(resolution, bbox=None, output_format=None, output_path=None):
    """
    Generate Maidenhead grid for pure Python usage.

    Args:
        resolution (int): Maidenhead resolution [1..4]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', etc.). Defaults to None (list of Maidenhead IDs).
        output_path (str, optional): Output file path. Defaults to None.

    Returns:
        dict, list, or str: Output depending on output_format
    """
    resolution = validate_maidenhead_resolution(resolution)
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        num_cells = maidenhead.num_cells(resolution)     
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = maidenhead_grid(resolution)
    else:
        gdf = maidenhead_grid_within_bbox(resolution, bbox)

    base_name = f"maidenhead_grid_{resolution}"
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


def maidenheadgrid_cli():
    parser = argparse.ArgumentParser(description="Generate Maidenhead DGGS")
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help="resolution [1..4]",
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of Maidenhead IDs)",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file path (optional)", default=None
    )
    args = parser.parse_args()
    
    if args.output_format == "None":
        args.output_format = None   

    try:
        result = maidenheadgrid(args.resolution, args.bbox, args.output_format)
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
    maidenheadgrid_cli()
