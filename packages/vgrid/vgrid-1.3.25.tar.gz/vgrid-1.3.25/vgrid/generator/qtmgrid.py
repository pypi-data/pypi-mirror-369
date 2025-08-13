from shapely.geometry import shape, Polygon
import argparse
import geopandas as gpd
import json
from vgrid.dggs import qtm
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from shapely.ops import unary_union
from tqdm import tqdm
from vgrid.utils.constants import MAX_CELLS
from vgrid.utils.io import convert_to_output_format, validate_qtm_resolution

p90_n180, p90_n90, p90_p0, p90_p90, p90_p180 = (
    (90.0, -180.0),
    (90.0, -90.0),
    (90.0, 0.0),
    (90.0, 90.0),
    (90.0, 180.0),
)
p0_n180, p0_n90, p0_p0, p0_p90, p0_p180 = (
    (0.0, -180.0),
    (0.0, -90.0),
    (0.0, 0.0),
    (0.0, 90.0),
    (0.0, 180.0),
)
n90_n180, n90_n90, n90_p0, n90_p90, n90_p180 = (
    (-90.0, -180.0),
    (-90.0, -90.0),
    (-90.0, 0.0),
    (-90.0, 90.0),
    (-90.0, 180.0),
)


def qtm_grid(resolution):
    resolution = validate_qtm_resolution(resolution)
    levelFacets = {}
    QTMID = {}
    qtm_rows = []
    for lvl in tqdm(range(resolution), desc="Generating QTM DGGS"):
        levelFacets[lvl] = []
        QTMID[lvl] = []
        if lvl == 0:
            initial_facets = [
                [p0_n180, p0_n90, p90_n90, p90_n180, p0_n180, True],
                [p0_n90, p0_p0, p90_p0, p90_n90, p0_n90, True],
                [p0_p0, p0_p90, p90_p90, p90_p0, p0_p0, True],
                [p0_p90, p0_p180, p90_p180, p90_p90, p0_p90, True],
                [n90_n180, n90_n90, p0_n90, p0_n180, n90_n180, False],
                [n90_n90, n90_p0, p0_p0, p0_n90, n90_n90, False],
                [n90_p0, n90_p90, p0_p90, p0_p0, n90_p0, False],
                [n90_p90, n90_p180, p0_p180, p0_p90, n90_p90, False],
            ]
            for i, facet in enumerate(initial_facets):
                facet_geom = qtm.constructGeometry(facet)
                QTMID[0].append(str(i + 1))
                levelFacets[0].append(facet)
                qtm_id = QTMID[0][i]
                num_edges = 3
                row = geodesic_dggs_to_geoseries(
                    "qtm", qtm_id, resolution, facet_geom, num_edges
                )
                qtm_rows.append(row)
        else:
            for i, pf in enumerate(levelFacets[lvl - 1]):
                subdivided_facets = qtm.divideFacet(pf)
                for j, subfacet in enumerate(subdivided_facets):
                    new_id = QTMID[lvl - 1][i] + str(j)
                    QTMID[lvl].append(new_id)
                    levelFacets[lvl].append(subfacet)
                    if lvl == resolution - 1:
                        subfacet_geom = qtm.constructGeometry(subfacet)
                        qtm_id = new_id
                        num_edges = 3
                        row = geodesic_dggs_to_geoseries(
                            "qtm", qtm_id, resolution, subfacet_geom, num_edges
                        )
                        qtm_rows.append(row)
    return gpd.GeoDataFrame(qtm_rows, geometry="geometry", crs="EPSG:4326")


def qtm_grid_within_bbox(resolution, bbox):
    resolution = validate_qtm_resolution(resolution)
    levelFacets = {}
    QTMID = {}
    qtm_rows = []
    bbox_poly = Polygon(
        [
            (bbox[0], bbox[1]),
            (bbox[2], bbox[1]),
            (bbox[2], bbox[3]),
            (bbox[0], bbox[3]),
            (bbox[0], bbox[1]),
        ]
    )
    for lvl in tqdm(range(resolution), desc="Generating QTM DGGS"):
        levelFacets[lvl] = []
        QTMID[lvl] = []
        if lvl == 0:
            initial_facets = [
                [p0_n180, p0_n90, p90_n90, p90_n180, p0_n180, True],
                [p0_n90, p0_p0, p90_p0, p90_n90, p0_n90, True],
                [p0_p0, p0_p90, p90_p90, p90_p0, p0_p0, True],
                [p0_p90, p0_p180, p90_p180, p90_p90, p0_p90, True],
                [n90_n180, n90_n90, p0_n90, p0_n180, n90_n180, False],
                [n90_n90, n90_p0, p0_p0, p0_n90, n90_n90, False],
                [n90_p0, n90_p90, p0_p90, p0_p0, n90_p0, False],
                [n90_p90, n90_p180, p0_p180, p0_p90, n90_p90, False],
            ]
            for i, facet in enumerate(initial_facets):
                QTMID[0].append(str(i + 1))
                facet_geom = qtm.constructGeometry(facet)
                levelFacets[0].append(facet)
                if shape(facet_geom).intersects(bbox_poly) and resolution == 1:
                    qtm_id = QTMID[0][i]
                    num_edges = 3
                    row = geodesic_dggs_to_geoseries(
                        "qtm", qtm_id, resolution, facet_geom, num_edges
                    )
                    qtm_rows.append(row)
        else:
            for i, pf in enumerate(levelFacets[lvl - 1]):
                subdivided_facets = qtm.divideFacet(pf)
                for j, subfacet in enumerate(subdivided_facets):
                    subfacet_geom = qtm.constructGeometry(subfacet)
                    if shape(subfacet_geom).intersects(bbox_poly):
                        new_id = QTMID[lvl - 1][i] + str(j)
                        QTMID[lvl].append(new_id)
                        levelFacets[lvl].append(subfacet)
                        if lvl == resolution - 1:
                            qtm_id = new_id
                            num_edges = 3
                            row = geodesic_dggs_to_geoseries(
                                "qtm", qtm_id, resolution, subfacet_geom, num_edges
                            )
                            qtm_rows.append(row)
    return gpd.GeoDataFrame(qtm_rows, geometry="geometry", crs="EPSG:4326")


def qtm_grid_resample(resolution, geojson_features):
    resolution = validate_qtm_resolution(resolution)
    levelFacets = {}
    QTMID = {}
    qtm_rows = []
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    for lvl in tqdm(range(resolution), desc="Generating QTM DGGS"):
        levelFacets[lvl] = []
        QTMID[lvl] = []
        if lvl == 0:
            initial_facets = [
                [p0_n180, p0_n90, p90_n90, p90_n180, p0_n180, True],
                [p0_n90, p0_p0, p90_p0, p90_n90, p0_n90, True],
                [p0_p0, p0_p90, p90_p90, p90_p0, p0_p0, True],
                [p0_p90, p0_p180, p90_p180, p90_p90, p0_p90, True],
                [n90_n180, n90_n90, p0_n90, p0_n180, n90_n180, False],
                [n90_n90, n90_p0, p0_p0, p0_n90, n90_n90, False],
                [n90_p0, n90_p90, p0_p90, p0_p0, n90_p0, False],
                [n90_p90, n90_p180, p0_p180, p0_p90, n90_p90, False],
            ]
            for i, facet in enumerate(initial_facets):
                QTMID[0].append(str(i + 1))
                facet_geom = qtm.constructGeometry(facet)
                levelFacets[0].append(facet)
                if shape(facet_geom).intersects(unified_geom) and resolution == 1:
                    qtm_id = QTMID[0][i]
                    num_edges = 3
                    row = geodesic_dggs_to_geoseries(
                        "qtm", qtm_id, resolution, facet_geom, num_edges
                    )
                    qtm_rows.append(row)
        else:
            for i, pf in enumerate(levelFacets[lvl - 1]):
                subdivided_facets = qtm.divideFacet(pf)
                for j, subfacet in enumerate(subdivided_facets):
                    subfacet_geom = qtm.constructGeometry(subfacet)
                    if shape(subfacet_geom).intersects(unified_geom):
                        new_id = QTMID[lvl - 1][i] + str(j)
                        QTMID[lvl].append(new_id)
                        levelFacets[lvl].append(subfacet)
                        if lvl == resolution - 1:
                            qtm_id = new_id
                            num_edges = 3
                            row = geodesic_dggs_to_geoseries(
                                "qtm", qtm_id, resolution, subfacet_geom, num_edges
                            )
                            qtm_rows.append(row)
    return gpd.GeoDataFrame(qtm_rows, geometry="geometry", crs="EPSG:4326")


def qtmgrid(resolution, bbox=None, output_format=None):
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        gdf = qtm_grid(resolution)
        num_cells = len(gdf)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
    else:
        gdf = qtm_grid_within_bbox(resolution, bbox)
        num_cells = len(gdf)
        if num_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} within bbox {bbox} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
    base_name = f"qtm_grid_{resolution}"
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


def qtmgrid_cli():
    parser = argparse.ArgumentParser(description="Generate QTM DGGS.")
    parser.add_argument(
        "-r", "--resolution", required=True, type=int, help="Resolution [1..24]."
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
        help="Output output_format (geojson, csv, geo, gpd, shapefile, gpkg, parquet, or None for list of QTM IDs)",
    )
    args = parser.parse_args()

    if args.output_format == "None":
        args.output_format = None
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180, -90, 180, 90]
    
    try:
        result = qtmgrid(resolution, bbox, args.output_format)
        if result is None:
            return
        if args.output_format is None:
            print(result)
        elif args.output_format in ["geo", "gpd"]:
            print(result)
        elif args.output_format in ["csv", "parquet", "gpkg", "shapefile", "geojson"] and isinstance(result, str):
            print(f"Output saved as {result}")
        elif args.output_format == "geojson" and isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(f"Output saved in current directory.")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return



if __name__ == "__main__":
    qtmgrid_cli()
