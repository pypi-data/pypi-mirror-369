"""
rHEALPix DGGS Grid Generator Module
"""
import argparse
import json
from vgrid.dggs.rhealpixdggs.dggs import RHEALPixDGGS
from shapely.geometry import box, shape
from tqdm import tqdm
from shapely.ops import unary_union
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.geometry import rhealpix_cell_to_polygon, geodesic_dggs_to_geoseries
from vgrid.utils.io import validate_rhealpix_resolution, convert_to_output_format

from pyproj import Geod
import geopandas as gpd

geod = Geod(ellps="WGS84")
rhealpix_dggs = RHEALPixDGGS()


def rhealpix_grid(resolution):
    resolution = validate_rhealpix_resolution(resolution)
    rhealpix_rows = []
    total_cells = rhealpix_dggs.num_cells(resolution)
    rhealpix_grid = rhealpix_dggs.grid(resolution)
    with tqdm(
        total=total_cells, desc="Generating rHEALPix DGGS", unit=" cells"
    ) as pbar:
        for rhealpix_cell in rhealpix_grid:
            cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
            rhealpix_id = str(rhealpix_cell)
            num_edges = 4
            if rhealpix_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            row = geodesic_dggs_to_geoseries(
                "rhealpix", rhealpix_id, resolution, cell_polygon, num_edges
            )
            rhealpix_rows.append(row)
            pbar.update(1)
    return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")


def rhealpix_grid_within_bbox(resolution, bbox):
    resolution = validate_rhealpix_resolution(resolution)
    bbox_polygon = box(*bbox)
    bbox_center_lon = bbox_polygon.centroid.x
    bbox_center_lat = bbox_polygon.centroid.y
    seed_point = (bbox_center_lon, bbox_center_lat)
    rhealpix_rows = []
    seed_cell = rhealpix_dggs.cell_from_point(resolution, seed_point, plane=False)
    seed_cell_id = str(seed_cell)
    seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)
    if seed_cell_polygon.contains(bbox_polygon):
        num_edges = 4
        if seed_cell.ellipsoidal_shape() == "dart":
            num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "rhealpix", seed_cell_id, resolution, seed_cell_polygon, num_edges
        )
        rhealpix_rows.append(row)
        return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")
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
        for cell_id in tqdm(
            covered_cells, desc="Generating rHEALPix DGGS", unit=" cells"
        ):
            rhealpix_uids = (cell_id[0],) + tuple(map(int, cell_id[1:]))
            cell = rhealpix_dggs.cell(rhealpix_uids)
            cell_polygon = rhealpix_cell_to_polygon(cell)
            if cell_polygon.intersects(bbox_polygon):
                num_edges = 4
                if seed_cell.ellipsoidal_shape() == "dart":
                    num_edges = 3
                row = geodesic_dggs_to_geoseries(
                    "rhealpix", cell_id, resolution, cell_polygon, num_edges
                )
                rhealpix_rows.append(row)
        return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")


def rhealpix_grid_resample(resolution, geojson_features):
    resolution = validate_rhealpix_resolution(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    seed_point = (unified_geom.centroid.x, unified_geom.centroid.y)
    rhealpix_rows = []
    seed_cell = rhealpix_dggs.cell_from_point(resolution, seed_point, plane=False)
    seed_cell_id = str(seed_cell)
    seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)
    if seed_cell_polygon.contains(unified_geom):
        num_edges = 4
        if seed_cell.ellipsoidal_shape() == "dart":
            num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "rhealpix", seed_cell_id, resolution, seed_cell_polygon, num_edges
        )
        rhealpix_rows.append(row)
        return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")
    covered_cells = set()
    queue = [seed_cell]
    while queue:
        current_cell = queue.pop()
        current_cell_id = str(current_cell)
        if current_cell_id in covered_cells:
            continue
        covered_cells.add(current_cell_id)
        cell_polygon = rhealpix_cell_to_polygon(current_cell)
        if not cell_polygon.intersects(unified_geom):
            continue
        neighbors = current_cell.neighbors(plane=False)
        for _, neighbor in neighbors.items():
            neighbor_id = str(neighbor)
            if neighbor_id not in covered_cells:
                queue.append(neighbor)
    for cell_id in tqdm(covered_cells, desc="Generating rHEALPix DGGS", unit=" cells"):
        rhealpix_uids = (cell_id[0],) + tuple(map(int, cell_id[1:]))
        cell = rhealpix_dggs.cell(rhealpix_uids)
        cell_polygon = rhealpix_cell_to_polygon(cell)
        if cell_polygon.intersects(unified_geom):
            num_edges = 4
            if seed_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            row = geodesic_dggs_to_geoseries(
                "rhealpix", cell_id, resolution, cell_polygon, num_edges
            )
            rhealpix_rows.append(row)
    return gpd.GeoDataFrame(rhealpix_rows, geometry="geometry", crs="EPSG:4326")


# Remove convert_rhealpixgrid_output_format and handle output logic in rhealpixgrid

def rhealpixgrid(resolution, bbox=None, output_format=None):
    """
    Generate rHEALPix grid for pure Python usage.

    Args:
        resolution (int): rHEALPix resolution [0..15]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output output_format ('geojson', 'csv', 'geo', 'gpd', 'shapefile', 'gpkg', 'parquet', or None for list of rHEALPix IDs). Defaults to None.

    Returns:
        dict, list, or str: Output in the requested output_format (GeoJSON FeatureCollection, list of IDs, file path, etc.)
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        num_cells = rhealpix_dggs.num_cells(resolution)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = rhealpix_grid(resolution)
    else:
        gdf = rhealpix_grid_within_bbox(resolution, bbox)
    base_name = f"rhealpix_grid_{resolution}"
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


def rhealpixgrid_cli():
    """CLI interface for generating rHEALPix grid."""
    parser = argparse.ArgumentParser(description="Generate rHEALPix DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..15]"
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of rHEALPix IDs)",
    )
    args = parser.parse_args()
    # Ensure Python None, not string 'None'
    if args.output_format == "None":
        args.output_format = None
    try:
        result = rhealpixgrid(args.resolution, args.bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            # Print the entire Python list of rHEALPix IDs at once
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
    rhealpixgrid_cli()

