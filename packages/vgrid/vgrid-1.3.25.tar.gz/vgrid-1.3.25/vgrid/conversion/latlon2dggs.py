from vgrid.dggs import s2, olc, geohash, georef, mgrs, maidenhead, tilecode, qtm
import h3
import a5       

from vgrid.dggs.gars.garsgrid import GARSGrid

from vgrid.dggs.rhealpixdggs.dggs import RHEALPixDGGS
from vgrid.dggs.rhealpixdggs.ellipsoids import WGS84_ELLIPSOID
import platform

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.shapes.lat_long_point import LatLongPoint
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.utils.constants import ISEA3H_RES_ACCURACY_DICT, ISEA4T_RES_ACCURACY_DICT
    isea4t_dggs = Eaggr(Model.ISEA4T)
    isea3h_dggs = Eaggr(Model.ISEA3H)

if platform.system() == "Linux":
    from vgrid.dggs.healpy_helper import _latlon2cellid
    from vgrid.dggs.dggrid4py import DGGRIDv7, dggs_types
    import geopandas as gpd
    from vgrid.dggs.dggrid4py.dggrid_runner import output_address_types

from shapely import Point
from vgrid.utils.io import  (
    validate_h3_resolution, 
    validate_s2_resolution, 
    validate_a5_resolution, 
    validate_healpix_resolution,
    validate_rhealpix_resolution,
    validate_isea4t_resolution,
    validate_isea3h_resolution,
    validate_ease_resolution,
    validate_qtm_resolution,
    validate_olc_resolution, 
    validate_geohash_resolution,
    validate_georef_resolution,
    validate_mgrs_resolution, 
    validate_tilecode_resolution,
    validate_quadkey_resolution,
    validate_maidenhead_resolution,
    validate_gars_resolution,
)

from vgrid.dggs.easedggs.dggs.grid_addressing import geos_to_grid_ids

import argparse


def latlon2h3(lat, lon, res=13):
    # res: [0..15]
    res = validate_h3_resolution(res)
    h3_id = h3.latlng_to_cell(lat, lon, res)
    return h3_id

def latlon2h3_cli():
    """
    Command-line interface for latlon2h3.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to H3 code at a specific Resolution [0.15]. \
                                     Usage: latlon2h3 <lat> <lon> <res> [0..15]. \
                                     Ex: latlon2h3 10.775275567242561 106.70679737574993 13"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..15]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    h3_id = latlon2h3(lat, lon, res)
    print(h3_id)


def latlon2s2(lat, lon, res=21):
    # res: [0..30]
    res = validate_s2_resolution(res)
    lat_lng = s2.LatLng.from_degrees(lat, lon)
    s2_id = s2.CellId.from_lat_lng(lat_lng)  # return S2 cell at max level 30
    s2_id = s2_id.parent(res)  # get S2 cell at resolution
    s2_token = s2.CellId.to_token(s2_id)  # get Cell ID Token, shorter than cell_id.id()
    return s2_token


def latlon2s2_cli():
    """
    Command-line interface for latlon2s2.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to S2 code at a specific Resolution [0..30]. \
                                     Usage: latlon2s2 <lat> <lon> <res> [0..30]. \
                                     Ex: latlon2s2 10.775275567242561 106.70679737574993 21"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..30]")
    args = parser.parse_args()
    res = args.res
    lat = args.lat
    lon = args.lon
    s2_token = latlon2s2(lat, lon, res)
    print(s2_token)


def latlon2a5(lat, lon, res=18):
    res = validate_a5_resolution(res)
    a5_id = a5.lonlat_to_cell((lon, lat), res)
    a5_hex = a5.bigint_to_hex(a5_id)
    return a5_hex

def latlon2a5_cli():
    """
    Command-line interface for latlon2a5.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to A5 code at a specific Resolution [0..29]. \
                                     Usage: latlon2a5 <lat> <lon> <res> [0..29]. \
                                     Ex: latlon2a5 10.775275567242561 106.70679737574993 21"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..29]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    a5_hex = latlon2a5(lat, lon, res)
    print(a5_hex)

def latlon2healpix(lat, lon, res=9):
    """
    Convert latitude and longitude to HEALPix cell ID.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees  
        res (int): Resolution/order [0..29] (0=12 pixels, 1=48 pixels, etc.)
    
    Returns:
        int: HEALPix cell ID
    """
    if platform.system() != "Linux":
        raise RuntimeError("HEALPix is only supported on Linux systems")
    
    res = validate_healpix_resolution(res)
    
    # Calculate nside from resolution order
    nside = 2 ** res
    healpix_id = _latlon2cellid(lat, lon, nside)
    return healpix_id

def latlon2healpix_cli():
    """
    Command-line interface for latlon2healpix.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to HEALPix ID at a specific resolution [0..29]. \
                                     Usage: latlon2healpix <lat> <lon> <res> [0..29]. \
                                     Ex: latlon2healpix 10.775275567242561 106.70679737574993 9"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..29]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    healpix_id = latlon2healpix(lat, lon, res)
    print(healpix_id)
  

def latlon2rhealpix(lat, lon, res=14):
    res = validate_rhealpix_resolution(res)
    E = WGS84_ELLIPSOID
    rhealpix_dggs = RHEALPixDGGS(ellipsoid=E, north_square=1, south_square=3, N_side=3)
    point = (lon, lat)
    rhealpix_cell = rhealpix_dggs.cell_from_point(res, point, plane=False)
    rhealpix_id = str(rhealpix_cell)
    return rhealpix_id


def latlon2rhealpix_cli():
    """
    Command-line interface for latlon2rhealpix.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to Rhealpix code at a specific Resolution [0..15]. \
                                     Usage: latlon2rhealpix <lat> <lon> <res> [0..15]. \
                                     Ex: latlon2rhealpix 10.775275567242561 106.70679737574993 14"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..15]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    rhealpix_id = latlon2rhealpix(lat, lon, res)
    print(rhealpix_id)


def latlon2isea4t(lat, lon, res=21):
    if platform.system() == "Windows":
        res = validate_isea4t_resolution(res)
        max_accuracy = ISEA4T_RES_ACCURACY_DICT[39]  # maximum cell_id length with 41 characters
        lat_long_point = LatLongPoint(lat, lon, max_accuracy)
        isea4t_cell_max_accuracy = isea4t_dggs.convert_point_to_dggs_cell(lat_long_point)
        cell_id_len = res + 2
        isea4t_cell = DggsCell(isea4t_cell_max_accuracy._cell_id[:cell_id_len])
        return isea4t_cell._cell_id

def latlon2isea4t_cli():
    """
    Command-line interface for latlon2isea4t.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to OpenEaggr ISEA4T code at a specific Resolution [0..39]. \
                                     Usage: latlon2isea4t <lat> <lon> <res> [0..39]. \
                                     Ex: latlon2isea4t 10.775275567242561 106.70679737574993 21"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..39]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    isea4t_id = latlon2isea4t(lat, lon, res)
    print(isea4t_id)


def latlon2isea3h(lat, lon, res=27):
    if platform.system() == "Windows":
        # res: [0..40], res=27 is suitable for geocoding
        res = validate_isea3h_resolution(res)
        accuracy = ISEA3H_RES_ACCURACY_DICT.get(res)
        lat_long_point = LatLongPoint(lat, lon, accuracy)
        isea3h_cell = isea3h_dggs.convert_point_to_dggs_cell(lat_long_point)
        return str(isea3h_cell.get_cell_id())


def latlon2isea3h_cli():
    """
    Command-line interface for latlon2isea3h.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to OpenEaggr ISEA3H code at a specific Resolution [0..40]. \
                                     Usage: latlon2isea3h <lat> <lon> <res> [0..40]. \
                                     Ex: latlon2isea3h 10.775275567242561 106.70679737574993 14"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..40]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    isea3h_id = latlon2isea3h(lat, lon, res)
    print(isea3h_id)


def latlon2dggrid(lat, lon, dggs_type, res, address_type="SEQNUM"):
    if platform.system() == "Linux":
        dggrid_instance = DGGRIDv7(
            executable="/usr/local/bin/dggrid",
            working_dir=".",
            capture_logs=False,
            silent=True,
            tmp_geo_out_legacy=False,
            debug=False,
        )
        point = Point(lon, lat)
        geodf_points_wgs84 = gpd.GeoDataFrame([{"geometry": point}], crs="EPSG:4326")
        dggrid_cell = dggrid_instance.cells_for_geo_points(
            geodf_points_wgs84=geodf_points_wgs84,
            cell_ids_only=True,
            dggs_type=dggs_type,
            resolution=res,
        )
        seqnum = dggrid_cell.loc[0, "seqnums"]
        address_type_transform = dggrid_instance.address_transform(
            [seqnum],
            dggs_type=dggs_type,
            resolution=res,
            mixed_aperture_level=None,
            input_address_type="SEQNUM",
            output_address_type=address_type,
        )
        # cell_id_api = {f'{dggs_type}_{res}_{address_type_transform.columns[1]}': address_type_transform.loc[0,address_type]}
        dggrid_cell_id = address_type_transform.loc[0, address_type]
        return dggrid_cell_id
        # return address_type_transform


def latlon2dggrid_cli():
    """
    Command-line interface for latlon2dggrid.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to DGGRID cell at a specific Resolution. \
                                     Usage: latlon2dggrid <lat> <lon> <dggs_type> <res>. \
                                     Ex: latlon2dggrid  10.775275567242561 106.70679737574993 ISEA7H 13"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument(
        "dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument("res", type=int, help="Resolution")
    parser.add_argument(
        "address_type",
        choices=output_address_types,
        default="SEQNUM",
        nargs="?",  # This makes the argument optional
        help="Select an output address type from the available options.",
    )

    args = parser.parse_args()
    dggs_type = args.dggs_type
    res = args.res
    address_type = args.address_type
    dggrid_cell_id = latlon2dggrid(args.lat, args.lon, dggs_type, res, address_type)
    print(dggrid_cell_id)


def latlon2ease(lat, lon, res=6):
    # res = [0..6]
    res = validate_ease_resolution(res)
    ease_cell = geos_to_grid_ids([(lon, lat)], level=res)
    ease_id = ease_cell["result"]["data"][0]
    return ease_id


def latlon2ease_cli():
    """
    Command-line interface for latlon2isea3h.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to EASE-DGGS cell at a specific Resolution [0..6]. \
                                     Usage: latlon2ease <lat> <lon> <res> [0..6]. \
                                     Ex: latlon2ease 10.775275567242561 106.70679737574993 6"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..6]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    ease_id = latlon2ease(lat, lon, res)
    print(ease_id)


def latlon2qtm(lat, lon, res=10):
    res = validate_qtm_resolution(res)
    qtm_id = qtm.latlon_to_qtm_id(lat, lon, res)
    return qtm_id

def latlon2qtm_cli():
    """
    Command-line interface for latlon2qtm.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to QTM. \
                                     Usage: latlon2qtm <lat> <lon> <res> [1..24]. \
                                     Ex: latlon2qtm 10.775275567242561 106.70679737574993 10"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [1..24]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    qtm_id = latlon2qtm(lat, lon, res)
    print(qtm_id)


def latlon2olc(lat, lon, res=11):
    res = validate_olc_resolution(res)
    olc_id = olc.encode(lat, lon, res)
    return olc_id

def latlon2olc_cli():
    """
    Command-line interface for latlon2olc.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to OLC/ Google Plus Code at a specific Code length [10..15]. \
                                     Usage: latlon2olc <lat> <lon> <res> [2,4,6,8,10..15]. \
                                     Ex: latlon2olc 10.775275567242561 106.70679737574993 11"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument(
        "res",
        type=int,
        choices=[2, 4, 6, 8, 10, 11, 12, 13, 14, 15],
        help="Resolution of the OLC DGGS (choose from 2, 4, 6, 8, 10, 11, 12, 13, 14, 15)",
    )

    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon

    olc_id = latlon2olc(lat, lon, res)
    print(olc_id)


def latlon2geohash(lat, lon, res=6):
    res = validate_geohash_resolution(res)
    geohash_id = geohash.encode(lat, lon, res)
    return geohash_id


def latlon2geohash_cli():
    """
    Command-line interface for latlon2geohash.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to Geohash code at a specific resolution [1..10]. \
                                     Usage: latlon2geohash <lat> <lon> <res>[1..10]. \
                                     Ex: latlon2geohash 10.775275567242561 106.70679737574993 6"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [1..10]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    geohash_id = latlon2geohash(lat, lon, res)
    print(geohash_id)


def latlon2georef(lat, lon, res=4):
    res = validate_georef_resolution(res)
    georef_id = georef.encode(lat, lon, res)
    return georef_id

def latlon2georef_cli():
    """
    Command-line interface for latlon2georef.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to GEOREF code at a specific resolution [0..10]. \
                                     Usage: latlon2georef <lat> <lon> <res> [0..10]. \
                                     Ex: latlon2georef 10.775275567242561 106.70679737574993 5"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [0..10]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    georef_id = latlon2georef(lat, lon, res)
    print(georef_id)

def latlon2mgrs(lat, lon, res=4):
    res = validate_mgrs_resolution(res)
    mgrs_cell = mgrs.toMgrs(lat, lon, res)
    return mgrs_cell


def latlon2mgrs_cli():
    """
    Command-line interface for latlon2mgrs.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to GEOREF code at a specific resolution [0..5]. \
                                     Usage: latlon2mgrs <lat> <lon> <res> [0..5]. \
                                     Ex: latlon2mgrs 10.775275567242561 106.70679737574993 4"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution  [0..5]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    mgrs_id = latlon2mgrs(lat, lon, res)
    print(mgrs_id)


def latlon2tilecode(lat, lon, res=23):
    res = validate_tilecode_resolution(res)
    tilecode_id = tilecode.latlon2tilecode(lat, lon, res)
    return tilecode_id

def latlon2tilecode_cli():
    """
    Command-line interface for latlon2tilecode.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to Tile code at a specific resolution/ zoom level [0..29]. \
                                     Usage: latlon2tilecode <lat> <lon> <res> [0..29]. \
                                     Ex: latlon2tilecode 10.775275567242561 106.70679737574993 23"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution/ Zoom level [0..29]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    tilecode_id = latlon2tilecode(lat, lon, res)
    print(tilecode_id)

def latlon2quadkey(lat, lon, res=23):
    res = validate_quadkey_resolution(res)
    quadkey_id = tilecode.latlon2quadkey(lat, lon, res)
    return quadkey_id

def latlon2quadkey_cli():
    """
    Command-line interface for latlon2tilecode.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to Quadkey at a specific resolution/ zoom level [0..29]. \
                                     Usage: latlon2quadkey <lat> <lon> <res> [0..29]. \
                                     Ex: latlon2quadkey 10.775275567242561 106.70679737574993 23"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution/ Zoom level [0..29]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    quadkey_id = latlon2quadkey(lat, lon, res)
    print(quadkey_id)


def latlon2maidenhead(lat, lon, res=4):
    res = validate_maidenhead_resolution(res)
    maidenhead_id = maidenhead.toMaiden(lat, lon, res)
    # maidenhead_id = maidenhead.to_maiden(lat, lon, res)
    return maidenhead_id

def latlon2maidenhead_cli():
    """
    Command-line interface for latlon2maidenhead.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to Tile code at a specific resolution [1..4]. \
                                     Usage: latlon2maidenhead <lat> <lon> <res> [1..4]. \
                                     Ex: latlon2maidenhead 10.775275567242561 106.70679737574993 4"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument("res", type=int, help="Input Resolution [1..4]")
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    maidenhead_id = latlon2maidenhead(lat, lon, res)
    print(maidenhead_id)



def latlon2gars(lat, lon, res=1):
    # res: [1..4] where 1 is min res (30 minutes), 4 is max res (1 minute)
    res = validate_gars_resolution(res)
    # Convert res to minutes: 1->30, 2->15, 3->5, 4->1
    minutes_map = {1: 30, 2: 15, 3: 5, 4: 1}
    minutes = minutes_map[res]
    gars_cell = GARSGrid.from_latlon(lat, lon, minutes)
    return str(gars_cell)


def latlon2gars_cli():
    """
    Command-line interface for latlon2gars.
    """
    parser = argparse.ArgumentParser(
        description="Convert Lat, Long to GARS code at a specific resolution [1..4]. \
                                     Usage: latlon2gars <lat> <lon> <res> [1..4]. \
                                     Ex: latlon2gars 10.775275567242561 106.70679737574993 1"
    )
    parser.add_argument("lat", type=float, help="Input Latitude")
    parser.add_argument("lon", type=float, help="Input Longitude")
    parser.add_argument(
        "res",
        type=int,
        help="Input Resolution [1..4] (1=30min, 2=15min, 3=5min, 4=1min)",
    )
    args = parser.parse_args()

    res = args.res
    lat = args.lat
    lon = args.lon
    gars_id = latlon2gars(lat, lon, res)
    print(gars_id)