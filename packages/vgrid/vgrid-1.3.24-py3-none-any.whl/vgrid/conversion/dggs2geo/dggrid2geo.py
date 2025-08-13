
import json
import re
import os
import argparse
import platform

if platform.system() == "Linux":
    from vgrid.dggs.dggrid4py import DGGRIDv7, dggs_types


def dggrid2geojson(dggrid_id, dggs_type, resolution):
    if platform.system() == "Linux":
        dggrid_instance = DGGRIDv7(
            executable="/usr/local/bin/dggrid",
            working_dir=".",
            capture_logs=False,
            silent=True,
            tmp_geo_out_legacy=False,
            debug=False,
        )
        dggrid_cell = dggrid_instance.grid_cell_polygons_from_cellids(
            [dggrid_id], dggs_type, resolution, split_dateline=True
        )

        gdf = dggrid_cell.set_geometry("geometry")  # Ensure the geometry column is set
        # Check and set CRS to EPSG:4326 if needed
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
        elif not gdf.crs.equals("EPSG:4326"):
            gdf = gdf.to_crs(epsg=4326)

        feature_collection = gdf.to_json()
        return feature_collection


def dggrid2geojson_cli():
    """
    Command-line interface for dggrid2geojson.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGRID code to GeoJSON. \
                                     Usage: dggrid2geojson <SEQNUM> <dggs_type> <res>. \
                                     Ex: dggrid2geojson 783229476878 ISEA7H 13"
    )
    parser.add_argument("dggrid", help="Input DGGRID code in SEQNUM format")
    parser.add_argument(
        "type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument("res", type=int, help="resolution")
    # parser.add_argument("address", choices=input_address_types, help="Address type")

    args = parser.parse_args()
    geojson_data = dggrid2geojson(args.dggrid, args.type, args.res)
    print(geojson_data)