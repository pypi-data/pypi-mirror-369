import geopandas as gpd
import pandas as pd
import json
import os
import zipfile
import tarfile
import requests
from urllib.parse import urlparse


def process_input_data_compact(input_data, id_field=None, crs="EPSG:4326"):
    """
    Convert various inputs into a GeoDataFrame with 'id_field' and None geometry.
    Supports:
    - List of Cell IDs
    - GeoJSON dictionary (FeatureCollection with id_field in properties)
    - Local or remote files (GeoJSON, Shapefile, GPKG, etc.) using gpd.read_file
    - CSV and Parquet files (local or remote) with id_field column
    """
    if id_field is None:
        id_field = "cellid"

    # 1. GeoDataFrame or DataFrame
    if isinstance(input_data, gpd.GeoDataFrame) or isinstance(input_data, pd.DataFrame):
        if id_field not in input_data.columns:
            raise ValueError(f"Missing '{id_field}' in GeoDataFrame")
        df = input_data[[id_field]].copy()
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 2. GeoJSON dictionary
    if isinstance(input_data, dict) and "features" in input_data:
        ids = []
        for feature in input_data["features"]:
            props = feature.get("properties", {})
            if id_field not in props:
                raise ValueError(f"Feature missing '{id_field}' in properties")
            ids.append(props[id_field])
        df = pd.DataFrame({id_field: ids})
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 3. List of IDs
    if isinstance(input_data, list):
        df = pd.DataFrame({id_field: [str(i) for i in input_data]})
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 4. File path or URL
    if isinstance(input_data, str):
        try:
            if input_data.endswith(".csv"):
                df = pd.read_csv(input_data)
            elif input_data.endswith(".parquet"):
                df = pd.read_parquet(input_data)
            else:
                df = gpd.read_file(input_data)
            if id_field not in df.columns:
                raise ValueError(f"Missing '{id_field}' in file/URL: {input_data}")
            df = df[[id_field]].copy()
            df["geometry"] = None
            return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)
        except Exception as e:
            raise ValueError(f"Failed to read from '{input_data}': {e}")
    raise ValueError("Unsupported input type")


def process_input_data_bin(data, lat_col="lat", lon_col="lon", delimiter=None, **kwargs):
    if isinstance(data, gpd.GeoDataFrame):
        return data
    elif isinstance(data, pd.DataFrame):
        if "geometry" in data.columns:
            return gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
        elif lat_col in data.columns and lon_col in data.columns:
            gdf = gpd.GeoDataFrame(
                data.copy(),
                geometry=gpd.points_from_xy(data[lon_col], data[lat_col]),
                crs="EPSG:4326",
            )
            return gdf
        else:
            raise ValueError(f"DataFrame must have either a 'geometry' column or '{lat_col}' and '{lon_col}' columns.")
    elif isinstance(data, list):
        gdf = gpd.GeoDataFrame.from_features(data)
        gdf.set_crs(epsg=4326, inplace=True)
        return gdf
    elif isinstance(data, dict) and "type" in data:
        if data["type"] == "FeatureCollection":
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            gdf.set_crs(epsg=4326, inplace=True)
            return gdf
        elif data["type"] == "Feature":
            gdf = gpd.GeoDataFrame.from_features([data])
            gdf.set_crs(epsg=4326, inplace=True)
            return gdf
        else:
            raise ValueError(f"Unsupported GeoJSON type: {data['type']}")
    elif isinstance(data, str):
        ext = os.path.splitext(data)[1].lower()
        if ext in [".csv", ".txt", ".tsv"]:
            if delimiter is None:
                if ext == ".tsv":
                    delimiter = "\t"
                else:
                    delimiter = ","
            df = pd.read_csv(data, delimiter=delimiter, **kwargs)
            if lat_col in df.columns and lon_col in df.columns:
                gdf = gpd.GeoDataFrame(
                    df.copy(),
                    geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
                    crs="EPSG:4326",
                )
                return gdf
            else:
                raise ValueError(f"Tabular file must have columns '{lat_col}' and '{lon_col}'")
        else:
            gdf = gpd.read_file(data, **kwargs)
            return process_input_data_bin(gdf, lat_col=lat_col, lon_col=lon_col)
    else:
        raise ValueError(f"Unsupported input type: {type(data)}")


def process_input_data_vector(input_data, crs="EPSG:4326", **kwargs):
    """
    Convert various vector inputs into a GeoDataFrame with geometry column preserved.
    Supports:
    - GeoDataFrame (returns as is)
    - DataFrame with geometry column
    - GeoJSON dictionary (FeatureCollection)
    - File path or URL (GeoJSON, Shapefile, GPKG, etc.) using gpd.read_file
    - List of GeoJSON features
    """
    # 1. GeoDataFrame
    if isinstance(input_data, gpd.GeoDataFrame):
        if input_data.crs is None:
            input_data = input_data.set_crs(crs)
        return input_data
    # 2. DataFrame with geometry column
    if isinstance(input_data, pd.DataFrame):
        if "geometry" in input_data.columns:
            gdf = gpd.GeoDataFrame(input_data, geometry="geometry", crs=crs)
            if gdf.crs is None:
                gdf = gdf.set_crs(crs)
            return gdf
        else:
            raise ValueError("DataFrame must have a 'geometry' column.")
    # 3. GeoJSON dictionary
    if isinstance(input_data, dict) and "features" in input_data:
        gdf = gpd.GeoDataFrame.from_features(input_data["features"])
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        return gdf
    # 4. List of GeoJSON features
    if isinstance(input_data, list) and len(input_data) > 0 and isinstance(input_data[0], dict):
        gdf = gpd.GeoDataFrame.from_features(input_data)
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        return gdf
    # 5. File path or URL
    if isinstance(input_data, str):
        gdf = gpd.read_file(input_data, **kwargs)
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        return gdf
    raise ValueError(f"Unsupported input type for vector data: {type(input_data)}")


def convert_to_output_format(gdf, output_format=None, output_name=None):
    """
    Utility to output a GeoDataFrame in various formats.
    output_format: None, 'csv','geojson', 'shapefile', 'gpd', 'geojson_dict', 'gpkg', 'geoparquet'
    output_name: if provided, write to file in the current directory
    """
    if output_format is None:
        return gdf.to_dict(orient="records")
    elif output_format in ["gpd", "geopandas"]:
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        return gdf
    elif output_format == "csv":
        if output_name:
            output_name = os.path.join(os.getcwd(), output_name)
            gdf.to_csv(output_name, index=False)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return gdf.to_csv(index=False)
    elif output_format == "geojson_dict":
        return gdf.__geo_interface__
    elif output_format == "geojson":
        geojson = gdf.__geo_interface__
        if output_name:
            output_name = os.path.join(os.getcwd(), output_name)
            with open(output_name, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return geojson
    elif output_format == "shapefile":
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.shp")
        else:
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_file(output_name, driver="ESRI Shapefile")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format == "gpkg":
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.gpkg")
        else:
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_file(output_name, driver="GPKG")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format in ["geoparquet", "parquet"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.parquet")
        else:
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_parquet(output_name)
        print(f"Output file saved as: {output_name}")
        return output_name
    else:
        raise ValueError(f"Unsupported output_format: {output_format}")

# =============================
# Resolution Validators
# =============================

def validate_h3_resolution(resolution):
    """
    Validate that H3 resolution is in the valid range [0..15].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..15]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 15:
        raise ValueError(f"Resolution must be in range [0..15], got {resolution}")
    return resolution

def validate_a5_resolution(resolution):
    """
    Validate that A5 resolution is in the valid range [0..29].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..29]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 29:
        raise ValueError(f"Resolution must be in range [0..29], got {resolution}")
    return resolution



def validate_geohash_resolution(resolution):
    """
    Validate that Geohash resolution is in the valid range [1..12] (1=coarsest, 12=finest).
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [1..12]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 1 or resolution > 12:
        raise ValueError(f"Resolution must be in range [1..12], got {resolution}")
    return resolution

def validate_ease_resolution(resolution):
    """
    Validate that EASE resolution is in the valid range [0..6].
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..6]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 6:
        raise ValueError(f"Resolution must be in range [0..6], got {resolution}")
    return resolution

def validate_isea3h_resolution(resolution):
    """
    Validate that ISEA3H resolution is in the valid range [0..32].
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..32]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 40:
        raise ValueError(f"Resolution must be in range [0..40], got {resolution}")
    return resolution

def validate_isea4t_resolution(resolution):
    """
    Validate that ISEA4T resolution is in the valid range [0..39].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..39]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 39:
        raise ValueError(f"Resolution must be in range [0..39], got {resolution}")
    return resolution

def validate_qtm_resolution(resolution):
    """
    Validate that QTM resolution is in the valid range [1..24].
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [1..24]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 1 or resolution > 24:
        raise ValueError(f"Resolution must be in range [1..24], got {resolution}")
    return resolution

def validate_olc_resolution(resolution):
    """
    Validate that OLC resolution is in the valid range [2,4,6,8,10,11,12,13,14,15].
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [2,4,6,8,10,11,12,13,14,15]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution not in [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]:
        raise ValueError(
            f"Resolution must be in [2,4,6,8,10,11,12,13,14,15], got {resolution}"
        )
    return resolution

def validate_geohash_resolution(resolution):
    """
    Validate that Geohash resolution is in the valid range [0..12] (0=coarsest, 12=finest).
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..12]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 12:
        raise ValueError(f"Resolution must be in range [0..12], got {resolution}")
    return resolution

def validate_georef_resolution(resolution):
    """
    Validate that Georef resolution is in the valid range [0..10] (0=coarsest, 10=finest).
    Args:       
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..10]
        TypeError: If resolution is not an integer  
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 10:
        raise ValueError(f"Resolution must be in range [0..10], got {resolution}")
    return resolution

def validate_mgrs_resolution(resolution):
    """
    Validate that MGRS resolution is in the valid range [0..5] (0=coarsest, 5=finest).
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..5]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 5:
        raise ValueError(f"Resolution must be in range [0..5], got {resolution}")
    return resolution

def validate_tilecode_resolution(resolution):
    """
    Validate that Tilecode resolution is in the valid range [0..29] (0=coarsest, 29=finest).
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..29]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 29:
        raise ValueError(f"Resolution must be in range [0..29], got {resolution}")
    return resolution

def validate_quadkey_resolution(resolution):
    """
    Validate that Quadkey resolution is in the valid range [0..29] (0=coarsest, 29=finest).
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..29] (0=coarsest, 29=finest)
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 29:
        raise ValueError(
            f"Resolution must be in range [0..29] (0=coarsest, 29=finest), got {resolution}"
        )
    return resolution

def validate_maidenhead_resolution(resolution):
    """
    Validate that Maidenhead resolution is in the valid range [1..4].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [1..4]    
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(    
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 1 or resolution > 4:
        raise ValueError("Resolution must be in range [1..4]")
    return resolution

def validate_gars_resolution(resolution):
    """
    Validate that Maidenhead resolution is in the valid range [1..4].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [1..4]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 1 or resolution > 4:
        raise ValueError("Resolution must be in range [1..4]")
    return resolution

def validate_healpix_resolution(resolution):
    """
    Validate that HEALPix resolution is in the valid range [0..29].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..29]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 29:
        raise ValueError(f"Resolution must be in range [0..29], got {resolution}")
    return resolution

def validate_rhealpix_resolution(resolution):
    """
    Validate that rHEALPix resolution is in the valid range [0..15].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..15]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 15:
        raise ValueError(f"Resolution must be in range [0..15], got {resolution}")
    return resolution

def validate_s2_resolution(resolution):
    """
    Validate that S2 resolution is in the valid range [0..28].
    Args:
        resolution: Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [0..28]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < 0 or resolution > 28:
        raise ValueError(f"Resolution must be in range [0..28], got {resolution}")
    return resolution

def gars_num_cells(resolution: int) -> int:
    """
    Return the total number of GARS cells at a given resolution.

    Resolution levels:
    1 = 30' × 30' cell
    2 = 15' × 15' quadrant
    3 = 5' × 5' area (keypad)
    4 = 1' × 1' sub-cell (optional extension)
    """
    resolution = validate_gars_resolution(resolution)
    # Base 30' × 30' cells
    lon_bands = 720
    lat_bands = 360
    base_cells = lon_bands * lat_bands

    # Multipliers for each resolution
    multipliers = {
        1: 1,
        2: 4,
        3: 4 * 9,
        4: 4 * 9 * 25
    }

    return base_cells * multipliers[resolution]

def is_url(path):
    """Check if the given path is a URL."""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def read_geojson_file(geojson_path):
    """Read GeoJSON from either a local file or URL."""
    if is_url(geojson_path):
        try:
            response = requests.get(geojson_path)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.RequestException as e:
            print(
                f"Error: Failed to download GeoJSON from URL {geojson_path}: {str(e)}"
            )
            return None
    else:
        if not os.path.exists(geojson_path):
            print(f"Error: The file {geojson_path} does not exist.")
            return None
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading GeoJSON file: {e}")
            return None

def github_raw_url(url):
    """Get the raw URL for a GitHub file.

    Args:
        url (str): The GitHub URL.
    Returns:
        str: The raw URL.
    """
    if isinstance(url, str) and url.startswith("https://github.com/") and "blob" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace(
            "blob/", ""
        )
    return url

def install_package(package):
    """Install a Python package.

    Args:
        package (str | list): The package name or a GitHub URL or a list of package names or GitHub URLs.
    """
    import subprocess

    if isinstance(package, str):
        packages = [package]
    elif isinstance(package, list):
        packages = package

    for package in packages:
        if package.startswith("https"):
            package = f"git+{package}"

        # Execute pip install command and show output in real-time
        command = f"pip install {package}"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == b"" and process.poll() is not None:
                break
            if output:
                print(output.decode("utf-8").strip())

        # Wait for process to complete
        process.wait()

def extract_archive(archive, outdir=None, **kwargs) -> None:
    """
    Extracts a multipart archive.

    This function uses the patoolib library to extract a multipart archive.
    If the patoolib library is not installed, it attempts to install it.
    If the archive does not end with ".zip", it appends ".zip" to the archive name.
    If the extraction fails (for example, if the files already exist), it skips the extraction.

    Args:
        archive (str): The path to the archive file.
        outdir (str): The directory where the archive should be extracted.
        **kwargs: Arbitrary keyword arguments for the patoolib.extract_archive function.

    Returns:
        None

    Raises:
        Exception: An exception is raised if the extraction fails for reasons other than the files already existing.

    Example:

        files = ["sam_hq_vit_tiny.zip", "sam_hq_vit_tiny.z01", "sam_hq_vit_tiny.z02", "sam_hq_vit_tiny.z03"]
        base_url = "https://github.com/opengeos/datasets/releases/download/models/"
        urls = [base_url + f for f in files]
        vgrid.utils.io.download_files(urls, out_dir="models", multi_part=True)

    """
    try:
        import patoolib
    except ImportError:
        install_package("patool")
        import patoolib

    if not archive.endswith(".zip"):
        archive = archive + ".zip"

    if outdir is None:
        outdir = os.path.dirname(archive)

    try:
        patoolib.extract_archive(archive, outdir=outdir, **kwargs)
    except Exception:
        print("The unzipped files might already exist. Skipping extraction.")
        return

def download_file(
    url=None,
    output=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    verify=True,
    id=None,
    fuzzy=False,
    resume=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
):
    """Download a file from URL, including Google Drive shared URL.

    Args:
        url (str, optional): Google Drive URL is also supported. Defaults to None.
        output (str, optional): Output filename. Default is basename of URL.
        quiet (bool, optional): Suppress terminal output. Default is False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        verify (bool | str, optional): Either a bool, in which case it controls whether the server's TLS certificate is verified, or a string,
            in which case it must be a path to a CA bundle to use. Default is True.. Defaults to True.
        id (str, optional): Google Drive's file ID. Defaults to None.
        fuzzy (bool, optional): Fuzzy extraction of Google Drive's file Id. Defaults to False.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.
        unzip (bool, optional): Unzip the file. Defaults to True.
        overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
        subfolder (bool, optional): Create a subfolder with the same name as the file. Defaults to False.

    Returns:
        str: The output file path.
    """
    try:
        import gdown
    except ImportError:
        print(
            "The gdown package is required for this function. Use `pip install gdown` to install it."
        )
        return

    if output is None:
        if isinstance(url, str) and url.startswith("http"):
            output = os.path.basename(url)

    out_dir = os.path.abspath(os.path.dirname(output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(url, str):
        if os.path.exists(os.path.abspath(output)) and (not overwrite):
            print(
                f"{output} already exists. Skip downloading. Set overwrite=True to overwrite."
            )
            return os.path.abspath(output)
        else:
            url = github_raw_url(url)

    if "https://drive.google.com/file/d/" in url:
        fuzzy = True

    output = gdown.download(
        url, output, quiet, proxy, speed, use_cookies, verify, id, fuzzy, resume
    )

    if unzip:
        if output.endswith(".zip"):
            with zipfile.ZipFile(output, "r") as zip_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]

                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    zip_ref.extractall(output)
                else:
                    zip_ref.extractall(os.path.dirname(output))
        elif output.endswith(".tar.gz") or output.endswith(".tar"):
            if output.endswith(".tar.gz"):
                mode = "r:gz"
            else:
                mode = "r"

            with tarfile.open(output, mode) as tar_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]
                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    tar_ref.extractall(output)
                else:
                    tar_ref.extractall(os.path.dirname(output))

    return os.path.abspath(output)

def download_files(
    urls,
    out_dir=None,
    filenames=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    verify=True,
    id=None,
    fuzzy=False,
    resume=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
    multi_part=False,
):
    """Download files from URLs, including Google Drive shared URL.

    Args:
        urls (list): The list of urls to download. Google Drive URL is also supported.
        out_dir (str, optional): The output directory. Defaults to None.
        filenames (list, optional): Output filename. Default is basename of URL.
        quiet (bool, optional): Suppress terminal output. Default is False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        verify (bool | str, optional): Either a bool, in which case it controls whether the server's TLS certificate is verified, or a string, in which case it must be a path to a CA bundle to use. Default is True.. Defaults to True.
        id (str, optional): Google Drive's file ID. Defaults to None.
        fuzzy (bool, optional): Fuzzy extraction of Google Drive's file Id. Defaults to False.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.
        unzip (bool, optional): Unzip the file. Defaults to True.
        overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
        subfolder (bool, optional): Create a subfolder with the same name as the file. Defaults to False.
        multi_part (bool, optional): If the file is a multi-part file. Defaults to False.

    Examples:

        files = ["sam_hq_vit_tiny.zip", "sam_hq_vit_tiny.z01", "sam_hq_vit_tiny.z02", "sam_hq_vit_tiny.z03"]
        base_url = "https://github.com/opengeos/datasets/releases/download/models/"
        urls = [base_url + f for f in files]
        vgrid.utils.io.download_files(urls, out_dir="models", multi_part=True)
    """

    if out_dir is None:
        out_dir = os.getcwd()

    if filenames is None:
        filenames = [None] * len(urls)

    filepaths = []
    for url, output in zip(urls, filenames):
        if output is None:
            filename = os.path.join(out_dir, os.path.basename(url))
        else:
            filename = os.path.join(out_dir, output)

        filepaths.append(filename)
        if multi_part:
            unzip = False

        download_file(
            url,
            filename,
            quiet,
            proxy,
            speed,
            use_cookies,
            verify,
            id,
            fuzzy,
            resume,
            unzip,
            overwrite,
            subfolder,
        )

    if multi_part:
        archive = os.path.splitext(filename)[0] + ".zip"
        out_dir = os.path.dirname(filename)
        extract_archive(archive, out_dir)

        for file in filepaths:
            os.remove(file)

def download_folder(
    url=None,
    id=None,
    output=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    remaining_ok=False,
):
    """Downloads the entire folder from URL.

    Args:
        url (str, optional): URL of the Google Drive folder. Must be of the format 'https://drive.google.com/drive/folders/{url}'. Defaults to None.
        id (str, optional): Google Drive's folder ID. Defaults to None.
        output (str, optional):  String containing the path of the output folder. Defaults to current working directory.
        quiet (bool, optional): Suppress terminal output. Defaults to False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.

    Returns:
        list: List of files downloaded, or None if failed.
    """

    try:
        import gdown
    except ImportError:
        print(
            "The gdown package is required for this function. Use `pip install gdown` to install it."
        )
        return

    files = gdown.download_folder(
        url, id, output, quiet, proxy, speed, use_cookies, remaining_ok
    )
    return files