import os  # module
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import zipfile36 as zipfile
from io import BytesIO
from urllib.request import urlopen
import shutil  # module
import rasterio
import math
from shapely.geometry.polygon import Polygon
from shapely.geometry import Polygon, box
import osmnx as ox
import tempfile  # module
import requests
import io
import networkx as nx
from shapely.geometry import LineString, Point, Polygon


import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

import sys

sys.path.append("..")


from mapc_suitability.config import (
    mapc_lpd_folder,
    mass_mainland_crs,
    boston_assessors_csv,
    boston_geojson_url,
)


##### UNDERLYING FUNCTIONS #######
def normalize_field(df, col: str):
    """
    removes outliers then rescales column to a value from 0-1

    input = data frame, column name that you are normalizing
    output = normalized value btwn 0 and 1

    we can play around with methods layer. for now, it's min max scaling
    https://towardsdatascience.com/data-normalization-with-pandas-and-scikit-learn-7c1cc6ed6475

    """

    # cap outliers at Q1 - 1.5*IQR and Q3 + 1.5*IQR
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    low_limit = Q1 - 1.5 * IQR
    high_limit = Q3 + 1.5 * IQR

    # trim outliers
    def trim_outliers(row):
        if (row[col] <= low_limit).any():
            return low_limit
        elif (row[col] >= high_limit).any():
            return high_limit
        else:
            return row[col]

    df_norm = df.copy()

    df_norm[col] = df_norm.apply(lambda row: trim_outliers(row), axis=1)

    # df_norm=df[col][~((df[col]<(Q1-1.5*IQR)) | (df[col]>(Q3+1.5*IQR)))]

    # apply min-max scaling to capped values
    df_norm = (df_norm[col] - df_norm[col].min()) / (
        df_norm[col].max() - df_norm[col].min()
    )

    return df_norm


## DATA EXTRACTION FUNCTIONS ##


def download_and_extract_zip_to_temp(url):
    """
    Downloads a zipped file from a URL, extracts it to a temporary directory,
    and returns the path to the temporary directory.

    Args:
        url (str): The URL of the zipped file.

    Returns:
        str: The path to the temporary directory where the files are extracted.
             Returns None if an error occurs during download or extraction.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Define the path for the downloaded zip file within the temporary directory
    zip_file_path = os.path.join(temp_dir, "downloaded_archive.zip")

    # Download the zip file
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(zip_file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    return temp_dir


def get_file(dir_name: str, muni: str = None, fileType: str = None):
    """
    some town names are substrings of other town names (ex: Reading is a substring of North Reading,
        or Dover in Andover)
    this causes errors when trying to pull the right muni's file from a directory.
    this function pulls the correct matching file.
    can  also pull just the correct file type out (ie, a .shp from a whole shapefile)

    inputs:
    - dir_name: directory name to search through
    - muni(str): muni name, as seen in file paths (ie, with any included underscores). Not case sensitive.
    - filetype(str): optional, could be .shp, .csv, etc.

    output:
    correct file name to read from
    """

    # search through all file names in the directory for those that include the muni name
    # outputs a list of file names

    if muni:
        list_of_files = []
        if fileType:  # if there is a specified file type to draw from
            for dirpath, dirnames, filenames in os.walk(dir_name):
                for filename in filenames:
                    if muni.casefold() in filename.casefold():  # ignores case
                        if filename.endswith(fileType):  # search for file type
                            list_of_files.append(filename)
        else:
            for dirpath, dirnames, filenames in os.walk(dir_name):
                for filename in filenames:
                    if muni.casefold() in filename.casefold():  # ignores case
                        list_of_files.append(filename)

        if (
            len(list_of_files) == 1
        ):  # for towns that don't trigger multiple file names, can stop here
            file = os.path.join(dirpath, list_of_files[0])

        else:  # otherwise, match muni prefix or name depending on type of substring conflict
            # start with names (cases where muni names are substrings of others, not related to prefix)
            non_prefix_munis = ["Lynn", "Dover", "Milton", "Stow"]
            if muni in non_prefix_munis:
                if muni.casefold() == "Lynn".casefold():
                    list_of_files = list(
                        filter(
                            lambda x: "Lynnfield".casefold() not in x.casefold(),
                            list_of_files,
                        )
                    )
                    file = os.path.join(dirpath, list_of_files[0])
                elif muni.casefold() == "Dover".casefold():
                    list_of_files = list(
                        filter(
                            lambda x: "Andover".casefold() not in x.casefold(),
                            list_of_files,
                        )
                    )
                    file = os.path.join(dirpath, list_of_files[0])
                elif muni.casefold() == "Milton".casefold():
                    list_of_files = list(
                        filter(
                            lambda x: "Hamilton".casefold() not in x.casefold(),
                            list_of_files,
                        )
                    )
                    file = os.path.join(dirpath, list_of_files[0])
                elif muni.casefold() == "Stow".casefold():
                    list_of_files = list(
                        filter(
                            lambda x: "Williamstown".casefold() not in x.casefold(),
                            list_of_files,
                        )
                    )
                    file = os.path.join(dirpath, list_of_files[0])
            else:  # move on to prefixes
                prefixes = ["East", "North", "West", "South", "New"]
                for prefix in prefixes:  # loop through prefixes
                    # if a town has a prefix, find the matching prefix in the fle name
                    if prefix.casefold() in muni.casefold():
                        # search through list of files for that prefix
                        list_of_files = list(
                            filter(
                                lambda x: prefix.casefold() in x.casefold(),
                                list_of_files,
                            )
                        )
                        file = os.path.join(dirpath, list_of_files[0])
                    # if no prefix in town name, find the file name without the prefix
                    else:
                        list_of_files = list(
                            filter(
                                lambda x: prefix.casefold() not in x.casefold(),
                                list_of_files,
                            )
                        )
                        file = os.path.join(dirpath, list_of_files[0])
    else:
        for dirpath, dirnames, filenames in os.walk(dir_name):
            for filename in filenames:
                if filename.endswith(fileType):
                    file = os.path.join(dirpath, filename)

    return file


def get_most_updated_state_assessors_data(muni, path=None, include_row=False):
    """
    pulls parcel data from the state's assessors website (with an exception for Boston who hosts separately)
    """

    if not path:
        path = tempfile.mkdtemp()

    if muni == "Boston":
        print("reading Boston data from ", boston_geojson_url, ". Update if necessary.")
        # get geojson from boston's open data portal and download

        # unzip to temp folder
        temp_folder = download_and_extract_zip_to_temp(boston_geojson_url)
        layer = get_file(temp_folder, fileType="geojson")
        boston_parcels_gdf = gpd.read_file(layer)
        shutil.rmtree(temp_folder)

        # download csv
        s = requests.get(boston_assessors_csv).content
        boston_assessors = pd.read_csv(io.StringIO(s.decode("utf-8")))
        boston_assessors["GIS_ID"] = boston_assessors["GIS_ID"].astype(str)

        # merge gdf to assessor's data
        parcel_layer = boston_parcels_gdf.merge(
            boston_assessors, how="inner", left_on="MAP_PAR_ID", right_on="GIS_ID"
        )

        if include_row:
            pass
        else:
            parcel_layer = parcel_layer.loc[parcel_layer["POLY_TYPE"] == "FEE"]
        return parcel_layer

    else:
        # get shapefile from a massgis link
        shapefile_excel = (
            "https://www.mass.gov/doc/massgis-parcel-data-download-links-table/download"
        )
        shapefile_lookup = pd.read_excel(shapefile_excel)

        town_shp_lookup_link = shapefile_lookup.loc[
            shapefile_lookup["Town Name"] == muni.upper()
        ]

        # extract into a temporary folder for use

        # path = os.path.join(project_dir, 'Data', muni) #make a subdirectory in ortho folder w town name
        # os.makedirs(path, exist_ok=True)

        for url in town_shp_lookup_link["Shapefile Download URL"].tolist():
            with urlopen(url) as zipresp:
                with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                    zfile.extractall(path)

        layer = get_file(path, "TaxPar", ".shp")
        parcel_layer = gpd.read_file(layer)
        if include_row:
            pass
        else:
            parcel_layer = parcel_layer.loc[parcel_layer["POLY_TYPE"] == "FEE"]

        # delete temporary directory
        shutil.rmtree(path)

        return parcel_layer


def get_landuse_data(muni):
    """
    input = muni name
    process = picks out the right shapefile from the state's municipal land use database;
             makes a subdirectory in intermediate folder w town name and exports land use shapefile to it
             reads that shapefile in as a geodataframe
             merges with mapc land parcel database
    output = state detailed parcel layer, merged with mapc land parcel database
    """

    # get the most updated parcel data from massgis
    muni_state_parcels = get_most_updated_state_assessors_data(muni)

    # read in land parcel database
    file_name = get_file(dir_name=mapc_lpd_folder, muni=muni)

    # file_name = lpd_prefix + muni + lpd_suffix
    muni_lpd_path = os.path.join(mapc_lpd_folder, file_name)
    mapc_lpd = pd.read_csv(muni_lpd_path)

    # merge land parcel database with state muni parcels
    # only keep the loc_id from state parcel database because we only want the MAPC lpd fields
    muni_lpd_preprocess = muni_state_parcels[["LOC_ID", "geometry"]].merge(
        mapc_lpd, on="LOC_ID", how="left"
    )

    muni_lpd_preprocess = muni_lpd_preprocess.to_crs(mass_mainland_crs)

    return muni_lpd_preprocess


def buffer_gdf(gdf, buffer_size, point=False):
    """
    function that buffers an input gdf. returns input gdf, but with buffered geometry.
    If the input gdf is a point layer, point=True
    """
    if point:
        gdf_buffer = gdf.to_crs(mass_mainland_crs)
        gdf_buffer["geometry"] = gdf_buffer["geometry"].buffer(buffer_size)

    else:
        # perform buffer, returns geoseries
        gdf_buffer = gpd.GeoDataFrame(
            geometry=(gdf.buffer(distance=buffer_size))
        )  # transform to gdf to merge back to og gdf
        gdf_buffer = gdf.drop(columns="geometry").merge(
            gdf_buffer, left_index=True, right_index=True
        )  # merge back to gdf, returns df

        # finally, create a gdf out of df
        gdf_buffer = gpd.GeoDataFrame(
            data=gdf_buffer, geometry=gdf_buffer["geometry"], crs=mass_mainland_crs
        )

    return gdf_buffer


# function to download from a link
def get_gdf_from_zipped_link(url, topic: str):
    """

    input: a URL that downloads a zipped shapefile
    output: a gdf of the download, with the shapefile download deleted (no storage need)

    """

    # path = os.path.join(sp_data_dir, topic)
    path = os.path.join(
        "S:\\Network Shares\\K Drive\\DataServices\\Projects\\Current_Projects\\LandUse_VMT_GHG\\Analysis\\Spatial",
        topic,
    )
    # path = os.path.join('K:\DataServices\Projects\Current_Projects\PDAs_PPAs\I90_PPA_PDA\Data', topic)
    os.makedirs(path, exist_ok=True)

    # extract zipped folder to path
    with urlopen(url) as zipresp:
        with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(path)

    # pull out just the .shp file
    shapefile = get_file(dir_name=path, fileType=".shp")

    # read gdf from shapefile
    gdf = gpd.read_file(shapefile)
    gdf = gdf.to_crs(mass_mainland_crs)

    # delete file after extracted
    shutil.rmtree(path)

    return gdf


def create_grid(feature, shape, side_length):
    """Create a grid consisting of either rectangles or hexagons with a specified side length that covers the extent of input feature."""

    # Slightly displace the minimum and maximum values of the feature extent by creating a buffer
    # This decreases likelihood that a feature will fall directly on a cell boundary (in between two cells)
    # Buffer is projection dependent (due to units)
    feature = feature.buffer(20)

    # Get extent of buffered input feature
    min_x, min_y, max_x, max_y = feature.total_bounds

    # Create empty list to hold individual cells that will make up the grid
    cells_list = []

    # Create grid of squares if specified
    if shape in ["square", "rectangle", "box"]:
        # Adapted from https://james-brennan.github.io/posts/fast_gridding_geopandas/
        # Create and iterate through list of x values that will define column positions with specified side length
        for x in np.arange(min_x - side_length, max_x + side_length, side_length):
            # Create and iterate through list of y values that will define row positions with specified side length
            for y in np.arange(min_y - side_length, max_y + side_length, side_length):
                # Create a box with specified side length and append to list
                cells_list.append(box(x, y, x + side_length, y + side_length))

    # Otherwise, create grid of hexagons
    elif shape == "hexagon":
        # Set horizontal displacement that will define column positions with specified side length (based on normal hexagon)
        x_step = 1.5 * side_length

        # Set vertical displacement that will define row positions with specified side length (based on normal hexagon)
        # This is the distance between the centers of two hexagons stacked on top of each other (vertically)
        y_step = math.sqrt(3) * side_length

        # Get apothem (distance between center and midpoint of a side, based on normal hexagon)
        apothem = math.sqrt(3) * side_length / 2

        # Set column number
        column_number = 0

        # Create and iterate through list of x values that will define column positions with vertical displacement
        for x in np.arange(min_x, max_x + x_step, x_step):
            # Create and iterate through list of y values that will define column positions with horizontal displacement
            for y in np.arange(min_y, max_y + y_step, y_step):
                # Create hexagon with specified side length
                hexagon = [
                    [
                        x + math.cos(math.radians(angle)) * side_length,
                        y + math.sin(math.radians(angle)) * side_length,
                    ]
                    for angle in range(0, 360, 60)
                ]

                # Append hexagon to list
                cells_list.append(Polygon(hexagon))

            # Check if column number is even
            if column_number % 2 == 0:
                # If even, expand minimum and maximum y values by apothem value to vertically displace next row
                # Expand values so as to not miss any features near the feature extent
                min_y -= apothem
                max_y += apothem

            # Else, odd
            else:
                # Revert minimum and maximum y values back to original
                min_y += apothem
                max_y -= apothem

            # Increase column number by 1
            column_number += 1

    # Else, raise error
    else:
        raise Exception("Specify a rectangle or hexagon as the grid shape.")

    # Create grid from list of cells
    grid = gpd.GeoDataFrame(cells_list, columns=["geometry"], crs=mass_mainland_crs)

    # Create a column that assigns each grid a number. Call it LOC_ID for other functions
    grid["LOC_ID"] = np.arange(len(grid))
    grid = grid.clip(feature)

    # Return grid
    return grid


def get_heat_score(heat_index_fp, muni_gdf):
    """
    For each census block  in the municipality, determines the relative heat index score compared to all other
    block groups. Parcels within those block groups can then be prioritized higher.

    Inputs: Muni boundary (gdf), heat index raster (geotiff), comparitive geography

    """
    from rasterstats import zonal_stats
    from src.data.make_dataset import census_bl

    with rasterio.open(heat_index_fp) as raster:
        transform = raster.transform
        lst = raster.read(1).astype("float64")

    # retain census blocks within MUNI
    census_bl["og_area"] = census_bl[
        "geometry"
    ].area  # get original area to do sliver analysis

    muni_blocks = census_bl.clip(muni_gdf)
    muni_blocks["pct_bg"] = (
        (muni_blocks["geometry"].area) / (muni_blocks["og_area"])
    ) * 100
    muni_blocks["pct_bg"] = (
        (muni_blocks["geometry"].area) / (muni_blocks["og_area"])
    ) * 100
    muni_blocks = muni_blocks.loc[
        muni_blocks["pct_bg"] > 5
    ].reset_index()  # only keep block groups where 5% or more of the bg remains. Reset index for zonal stats

    ## ZONAL STATS ##
    # run zonal stats on heat index for mmc - what is the mean lst index score across census block?
    lst_stats = pd.DataFrame(
        zonal_stats(muni_blocks, lst, affine=transform, stats="mean")
    )

    # join back to blocks, rename field
    muni_blocks_heat = muni_blocks[["geoid20", "geometry"]].join(lst_stats)
    muni_blocks_heat = muni_blocks_heat.rename(columns={"mean": "lst_mean"})

    return muni_blocks_heat


def get_open_space_density(muni_gdf):
    from src.data.make_dataset import open_space_protected
    from src.features.indicator_functions import overlap_stats

    """
    get a weighted (by open space area) density of protected open space over a grid

    steps:
    1. buffer grid cells
    2. get average area of open space within [grid cells + buffer]
    3. then join back to grid cells

    """

    ## STEP 1: BUFFER GRID CELLS ##

    # create grid
    muni_grid = create_grid(feature=muni_gdf, shape="hexagon", side_length=200)

    # buffer grid cells
    muni_grid_w_buffer = buffer_gdf(gdf=muni_grid, buffer_size=300)

    ## STEP 2: GET AVERAGE AREA OF OPEN SPACE THAT OVERLAP BUFFERED GRID CELLS ##

    # clip open space to buffered muni boundary
    open_space_protected_muni = open_space_protected.clip(muni_grid_w_buffer)

    # create field for area of open space
    open_space_protected_muni["area"] = open_space_protected_muni.geometry.area

    # run overlap statistics to get a mean size of overlapping open space for each grid cell
    grid_openspace_overlap_mean = overlap_stats(
        layer_1=muni_grid_w_buffer,
        layer_2=open_space_protected_muni.drop(columns="LOC_ID"),
        stats="mean",
        stats_field="area",
        new_field_name="os",
        normalize=True,
    ).fillna(0)

    ## STEP 3: JOIN BACK TO ORIGINAL CELLS ##
    muni_grid_w_open_space = (
        muni_grid.merge(
            grid_openspace_overlap_mean[["LOC_ID", "os_mean_n"]],
            on="LOC_ID",
            how="left",
        )
        .fillna(0)
        .drop_duplicates()
    )

    return muni_grid_w_open_space


def get_isochrones_from_input_poly(
    layer_1, layer_1_id, travel_times: list, travel_type: str
):
    """
    uses osmnx to generate isochrones for an input layer of a determined size (based on travel type and desired time)

    inputs:
    - layer_1 = layer of interest
    - layer_1_id = ID field for layer_1
    - travel_times = list of times for generating isochrones (ie, 5 for 5-minute walk/drive time)
    - traevl_type = 'walk' or 'drive' (current options)
    """

    # function to get isochrones
    def get_isochrones(lon, lat, travel_times: list, network_type_input, name=None):
        """
        generates isochrones based on lat/lon
        """

        # set standard speeds
        if network_type_input == "walk":
            speed = 4.5
            dist = 804.672  # 10 minute walk in m (1 mile)
        elif network_type_input == "drive":  # 30 mph
            speed = 48.2803
            dist = 12874.8  # 10 minute drive in m (8 miles)
        else:
            print("input for now must be walk or drive")

        loc = (lat, lon)
        G = ox.graph.graph_from_point(
            center_point=loc,
            dist=dist,
            dist_type="network",
            network_type=network_type_input,
            simplify=False,
            retain_all=True,
            truncate_by_edge=True,
        )
        # gdf_nodes = ox.graph_to_gdfs(G, edges=False)
        center_node = ox.distance.nearest_nodes(G, lon, lat)

        meters_per_minute = speed * 1000 / 60  # km per hour to m per minute
        for u, v, k, data in G.edges(data=True, keys=True):
            data["time"] = data["length"] / meters_per_minute
        polys = []
        for time in travel_times:
            subgraph = nx.ego_graph(G, center_node, radius=time, distance="time")
            node_points = [
                Point(data["x"], data["y"]) for node, data in subgraph.nodes(data=True)
            ]
            polys.append(gpd.GeoSeries(node_points).union_all().convex_hull)
        info = {}
        info[layer_1_id] = [name for t in travel_times]
        return {**{"geometry": polys, "time": travel_times}, **info}

    ## RUN FOR INPUTS ##
    # convert to centroids, reproject
    layer_1_points = layer_1.copy()
    layer_1_points["geometry"] = layer_1["geometry"].centroid.to_crs("epsg:4326")

    # build geopandas data frame of isochrone polygons for each location
    isochrones = pd.concat(
        [
            gpd.GeoDataFrame(
                get_isochrones(
                    r["geometry"].x,
                    r["geometry"].y,
                    name=r[layer_1_id],
                    network_type_input=travel_type,
                    travel_times=travel_times,
                ),
                crs=layer_1_points.crs,
            )
            for i, r in layer_1_points.iterrows()
        ]
    )

    # reproject to mass mainland and return layer
    isochrones = isochrones.to_crs(mass_mainland_crs)

    return isochrones


##### INDICATOR FUNCTIONS #######


def if_overlap(
    layer_1, layer_2, new_field_name: str, inverse: bool = False, point: bool = False
):
    """
    For a given base layer (layer_1), identifies whether there is overlap (intersection) with a layer of interest (layer_2). If the layer of interest is a point layer,
    identifies whether the point is within the base layer feature.

    INPUTS:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - layer_2: (GeoDataFrame) The overlap layer of interest
    - new_field_name: (string)  Input a string to represent this layer in the output dataset

    OPTIONAL PARAMETER(S):
    - inverse: (bool, default False) When true, reverses the 0 and 1. This should be applied for layers in which overlap is unfavorable.
    - point: (bool, default False) Select 'True' when layer_2 is a point layer. In these cases, the function looks for whether the base layer contains a point layer.

    OUTPUT:
    '[new_field_name]_ovlp' field added to layer_1
        - Value of 1 if:
            - There is overlap, and overlap is favorable (Inverse = 'False')
            - There is no overlap, and overlap is unfavorable (Inverse = 'True')
        - Value of 0 if:
            - There is no overlap and overlap is favorable (Inverse = 'False')
            - There is overlap is and overlap is unfavorable (Inverse = 'True')
    """

    # reproject all to mass mainland
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    # determine predicate based on 'point' input
    if point:
        predicate = "contains"
    else:
        predicate = "intersects"

    overlap_only = gpd.sjoin(
        layer_1, layer_2, predicate=predicate, how="inner"
    )  # only keep geometry from layer_1

    ## MERGE BACK TO FULL DATASET ##
    new_field_name = new_field_name + "_ovlp"

    # add a field for whether it overlaps or not. If inverse is not selected, a value of 1 indicates overlap. Reverse is true if inverse not selected.
    if inverse:
        overlap_only[new_field_name] = 0

        # join back to base layer
        layer_1_with_overlap = (
            layer_1.merge(
                overlap_only[new_field_name],
                how="left",
                left_index=True,
                right_index=True,
            )
            .fillna(1)
            .drop_duplicates()
        )

    else:
        overlap_only[new_field_name] = 1

        # join back to base layer
        layer_1_with_overlap = (
            layer_1.merge(
                overlap_only[new_field_name],
                how="left",
                left_index=True,
                right_index=True,
            )
            .fillna(0)
            .drop_duplicates()
        )

    return layer_1_with_overlap


def calculate_overlap(
    layer_1,
    layer_2,
    how: str,
    new_field_name: str,
    normalize: bool = True,
    inverse: bool = False,
    buffer=None,
):
    """
    For a given polygon base layer, calculates either
    1) the total area of overlap (in meters squared) with a polygon layer of interest;
    2) the percentage of the base layer that is overlapped by a polygon layer of interest; OR
    3) the total length of a line layer of interest that is contained by the base layer [need to do this]


    INPUTS:
    - layer_1: (GeoDataFrame, polygon) The base layer being enriched
    - layer_2: (GeoDataFrame, polygon or line) The overlap layer of interest
    - how: (string, default 'area') the type of calculation:
        - 'area' = calculates the area of overlap in meters squared
        - 'percent' = calculate the percentage of the base layer
        - 'length' = calculate the length (in m) of an overlapping line layer within a chosen distance from layer_1
    - new_field_name: (string)  Input a string to represent this layer in the output dataset

    OPTIONAL PARAMETER(S):
    - normalize: (bool, default True) When True, adds an additional field containing a normalized value (0-1 scale) of the area/percentage of overlap.
    - inverse: (bool, default False) When True, normalized values are scored in the inverse. This implies that greater overlap = less suitability.
    - buffer: (int, default None) For calculating length, specify a buffer distance around layer_1 to search

    OUTPUT:
    Fields added to layer_1:
    - Overlap values:
        - '[new_field_name]_sqm' or '[new_field_name]_pct' or '[new_field_name]_m'
    - Normalized overlap values (with inverse applied if selected):
        - '[new_field_name]_sqm_n' or '[new_field_name]_pct_n' or '[new_field_name]_m_n'

    """
    from src.data.make_dataset import id_field

    if not how:
        how = "area"

    valid = {"area", "percent", "length"}
    if how not in valid:
        raise ValueError("how must be one of %r." % valid)

    # reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    # make a list of original columns for later
    layer_1_fields = layer_1.columns.tolist()

    if how in ["area", "percent"]:
        # only keep parts of layer 1 that intersects with layer 2
        intersection_layer = layer_1.overlay(
            layer_2, how="intersection", keep_geom_type=False
        )

        # get area of overlap for the area of intersection
        intersection_layer[new_field_name + "_sqm"] = intersection_layer[
            "geometry"
        ].area
        intersection_layer = (
            intersection_layer.groupby(by=id_field)
            .agg({(new_field_name + "_sqm"): "sum"})
            .reset_index()
        )

        # join back to parcels data, remove additional rows with groupby
        layer_1_enriched = layer_1.merge(
            intersection_layer[[id_field, (new_field_name + "_sqm")]],
            on=id_field,
            how="left",
        )

        # try a fillna() to account for np.nan in overlap values
        layer_1_enriched[new_field_name + "_sqm"] = layer_1_enriched[
            new_field_name + "_sqm"
        ].fillna(0)

        # get percent of overlap for each feature in the base layer
        layer_1_enriched[new_field_name + "_pct"] = layer_1_enriched[
            new_field_name + "_sqm"
        ] / (layer_1_enriched["geometry"].area)

        # final output defined by input and optional parameters
        if how == "area":
            if normalize:
                layer_1_enriched[(new_field_name + "_sqm_n")] = normalize_field(
                    layer_1_enriched, (new_field_name + "_sqm")
                )
                if inverse:
                    layer_1_enriched[(new_field_name + "_sqm_n")] = (
                        1 - layer_1_enriched[(new_field_name + "_sqm_n")]
                    )
                layer_1_enriched = layer_1_enriched[
                    layer_1_fields
                    + [(new_field_name + "_sqm"), (new_field_name + "_sqm_n")]
                ]
            else:
                layer_1_enriched = layer_1_enriched[
                    layer_1_fields + [(new_field_name + "_sqm")]
                ]

        elif how == "percent":
            if normalize:
                layer_1_enriched[(new_field_name + "_pct_n")] = normalize_field(
                    layer_1_enriched, [(new_field_name + "_pct")]
                )
                if inverse:
                    layer_1_enriched[(new_field_name + "_pct_n")] = (
                        1 - layer_1_enriched[(new_field_name + "_pct_n")]
                    )
                layer_1_enriched = layer_1_enriched[
                    layer_1_fields
                    + [(new_field_name + "_pct"), (new_field_name + "_pct_n")]
                ]
            else:
                layer_1_enriched = layer_1_enriched[
                    layer_1_fields + [(new_field_name + "_pct")]
                ]

    else:  # for line length overlaps
        layer_1_buffer = buffer_gdf(layer_1, buffer)

        # Intersect buffered parcels with lines - returns line segments that intersect with each parcel
        intersection_layer = gpd.overlay(
            df1=layer_1_buffer, df2=layer_2, how="intersection", keep_geom_type=False
        )

        # sum line length per unique ID
        intersection_layer[new_field_name + "_m"] = intersection_layer[
            "geometry"
        ].length
        intersection_layer[new_field_name + "_m"] = intersection_layer.groupby(
            id_field
        )[new_field_name + "_m"].transform("sum")

        # merge length field back to layer_1
        layer_1_enriched = (
            layer_1.merge(
                intersection_layer[[id_field, (new_field_name + "_m")]],
                on=id_field,
                how="left",
            )
            .fillna(0)
            .drop_duplicates()
        )

        if normalize:
            layer_1_enriched[(new_field_name + "_m_n")] = normalize_field(
                layer_1_enriched, (new_field_name + "_m")
            )
            if inverse:
                layer_1_enriched[(new_field_name + "_m_n")] = (
                    1 - layer_1_enriched[(new_field_name + "_m_n")]
                )
            layer_1_enriched = layer_1_enriched[
                layer_1_fields + [(new_field_name + "_m"), (new_field_name + "_m_n")]
            ]
        else:
            layer_1_enriched = layer_1_enriched[
                layer_1_fields + [(new_field_name + "_m")]
            ]

    return layer_1_enriched


def overlap_stats(
    layer_1,
    layer_2,
    new_field_name: str,
    stats: str = "maj",
    normalize: bool = True,
    inverse: bool = False,
    stats_field: str = None,
    nan_value=None,
):
    """
    Assigns the base layer with the (max, min, mean, median, maj (majority), count, sum) value from an overlapping geography that may have multiple
    values overlapping the parcel. Best suited for an overlapping geography that may have multiple values within the parcel.

    INPUT PARAMETERS:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - layer_2: (GeoDataFrame) The overlap layer of interest
    - new_field_name: (string) Input a string to represent this layer in the output dataset

    OPTIONAL PARAMETERS:
    - stats_field: (string) The field of interest for getting statistics
    - stats: (string, default 'mean') 'max', 'min', 'mean', 'median', 'majority', 'count', 'sum'
    - nan_value: Input a nan value for performing stats or normalizing. Will replace with np.nan so it isn't calculated in stats
    - normalize: (bool, default True) When True, adds an additional field containing a normalized value (0-1 scale) of the associated value. Can only be used with continuous variables.
    - inverse: (bool, default False) When True, the normalized or ranked value is returned as an inverse so that values closer to 1

    OUTPUT:
    Fields added to layer_1:
    - [new_field_name]_['stat']
    - If normalize: '[new_field_name']_['stat']_n
    """
    from src.data.make_dataset import id_field

    valid = {"max", "min", "mean", "median", "maj", "count", "sum"}
    if stats not in valid:
        raise ValueError("stats must be one of %r." % valid)

    # if there is a nan_value in the stats field, replace here with np.nan
    if nan_value:
        layer_2[stats_field] = layer_2.replace(nan_value, np.NaN).copy()

    # make a list of original columns for later
    layer_1_fields = layer_1.columns.tolist()

    # reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    if (
        stats == "maj"
    ):  # first, if majority, sort by area than drop everything except the largest
        # this can only be done with two polygon features currently because limited to 'overlay'
        layers_joined = layer_1.overlay(layer_2, how="intersection")

        # Sort by area so largest area is last
        layers_joined["area"] = layers_joined.geometry.area
        layers_joined = layers_joined.sort_values(by="area")
        layers_joined = layers_joined.drop_duplicates(
            subset=id_field, keep="last"
        )  # Drop duplicates, keep last/largest

        layers_joined[(new_field_name + "_" + stats)] = layers_joined[
            stats_field
        ]  # rename

    if stats == "count":  # if count, get the number of overlapping features
        # first, perform a spatial join
        layers_joined = gpd.sjoin(
            layer_1, layer_2, how="inner"
        )  # spatial join so can be for features beyond polygons. inner to just get intersecting layers.

        layers_joined[stats] = 1
        layers_joined = (
            layers_joined.groupby(by=[id_field]).agg({stats: "sum"}).reset_index()
        )
        layers_joined[(new_field_name + "_" + stats)] = layers_joined[stats].fillna(
            0
        )  # rename

    if stats in {"max", "min", "mean", "median", "sum"}:
        # first, perform a spatial join
        layers_joined = gpd.sjoin(layer_1, layer_2, how="inner")

        # then do a groupby with the stats field and stats
        layers_joined = (
            layers_joined.groupby(by=id_field).agg({stats_field: stats}).reset_index()
        )

        layers_joined[new_field_name + "_" + stats] = layers_joined[stats_field]

    layer_1_enriched = layer_1.merge(
        layers_joined[[id_field, (new_field_name + "_" + stats)]],
        on=id_field,
        how="left",
    ).fillna(np.nan)

    if normalize:
        layer_1_enriched[(new_field_name + "_" + stats + "_n")] = normalize_field(
            layer_1_enriched, (new_field_name + "_" + stats)
        )
        if inverse:
            layer_1_enriched[(new_field_name + "_" + stats + "_n")] = (
                1 - layer_1_enriched[(new_field_name + "_" + stats + "_n")]
            )
        layer_1_enriched = layer_1_enriched[
            layer_1_fields
            + [(new_field_name + "_" + stats), (new_field_name + "_" + stats + "_n")]
        ]

    else:
        layer_1_enriched = layer_1_enriched[
            layer_1_fields + [(new_field_name + "_" + stats)]
        ]

    return layer_1_enriched


def proximity(
    layer_1,
    layer_2,
    new_field_name: str,
    normalize: bool = True,
    inverse: bool = False,
    unit: str = "m",
    fields: list = None,
):
    """
    For a given base layer, calculates the distance to the nearest part of a layer of interest. Can also provide information
    about the nearest part.

    INPUT PARAMETERS:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - layer_2: (GeoDataFrame) The layer of interest for proximity
    - new_field_name:(string) Input a string to represent this layer in the output dataset


    - normalize: (bool, default True) When True, adds an additional field containing a normalized value (0-1 scale) of distance to layer_2.
    - inverse: (bool, default True) When true, normalized values are scored in the inverse, implying that greater distances to layer_2 are less favorable, or in other words that proximity is favorable. This is the default. Set to false if greater distances are favorable.
    - unit: (string, default 'meters') 'meters' ('m'), 'miles' ('mi'), 'kilometers' ('km')
    - fields: (list, default None) When a list of field names from layer_2 are provided, those fields will also be added to layer_1

    OUTPUT:
    Fields added to layer_1:
    - '[new_field_name]_['unit']
    - If normalize:
        - '[new_field_name]_['unit']_n, where values closer to 1 indicate greater proximity/shorter distances (unless inverse is False)
    - If fields list provided, those fields will also
    """

    from src.data.make_dataset import id_field

    # first make sure units are correct. default to meters.
    if not unit:
        unit = "m"

    valid = {"m", "mi", "km", "ft"}
    if unit not in valid:
        raise ValueError("unit must be one of %r." % valid)

    new_field_name = new_field_name + ("_") + unit

    # convert all to mass mainlan
    mass_mainland_crs = "EPSG:26986"
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    # make a list of original columns for later
    layer_1_fields = layer_1.columns.tolist()

    # run sjoin_nearest, will join layer_1 with closest feature of layer_2 and add all fields
    layers_joined = gpd.sjoin_nearest(
        layer_1, layer_2, how="left", distance_col=new_field_name
    )

    if unit == "m":
        layers_joined[new_field_name] = layers_joined[new_field_name]
    elif unit == "mi":
        layers_joined[new_field_name] = layers_joined[new_field_name] / 1609
    elif unit == "km":
        layers_joined[new_field_name] = layers_joined[new_field_name] / 1000
    elif unit == "ft":
        layers_joined[new_field_name] = layers_joined[new_field_name] * 3.281

    layers_joined = layers_joined.groupby(layers_joined.index).agg(
        "first"
    )  # do this just in case

    # what fields do bring in from layers_joined? Start with the join field and distance field
    fields_list = [new_field_name]

    # then add any other fields listed in input
    if fields:
        for field in fields:
            fields_list.append(field)

    # then add normalized values
    if (
        normalize
    ):  # for proximity, we assume we want to be CLOSER to layer_2, so we inverse automatically.
        layers_joined[(new_field_name + "_n")] = 1 - normalize_field(
            layers_joined, new_field_name
        )
        if inverse:
            layers_joined[(new_field_name + "_n")] = (
                1 + layers_joined[(new_field_name + "_n")]
            )
        fields_list.append((new_field_name + "_n"))
        # define final table

    # join only desired fields to layer_1
    layer_1_enriched = layer_1.merge(
        layers_joined[fields_list + [id_field]], on=id_field, how="left"
    ).fillna(np.nan)

    # ensure only original fields + additional field list
    layer_1_enriched = layer_1_enriched[layer_1_fields + fields_list]

    return layer_1_enriched


def field_stats(
    layer_1,
    stats_field: str,
    new_field_name: str,
    inverse: bool = False,
    nan_value=None,
):
    """
    Assigns the base layer with the normalized value for an existing field in an input dataset.

    INPUT PARAMETERS:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - new_field_name: (string)  Input a string to represent this layer in the output dataset
    - stats_field: (string) The field you are interested in normalizing

    OPTIONAL PARAMETERS
    - nan_value: Input a nan value for normalizing. Will replace with np.nan.
    - inverse: (bool, default False) When True, the normalized or ranked value is returned as an inverse so that values closer to 1

    OUTPUT
    Fields added to layer_1:
    - '[new_field_name']_n (inversed if inverse)

    """
    # first, replace nan value
    layer_1_enriched = layer_1.copy()

    # get field names for later
    layer_1_fields = layer_1_enriched.columns.tolist()

    if nan_value:
        layer_1_enriched[stats_field] = (
            layer_1_enriched[stats_field].replace(nan_value, np.NaN).copy()
        )

    # get normalized value for field
    layer_1_enriched[(new_field_name + "_n")] = normalize_field(
        layer_1_enriched, stats_field
    )

    # inverse if desired
    if inverse:
        layer_1_enriched[(new_field_name + "_n")] = (
            1 - layer_1_enriched[(new_field_name + "_n")]
        )

    layer_1_enriched = layer_1_enriched[layer_1_fields + [(new_field_name + "_n")]]

    return layer_1_enriched


def points_within_isochrone(
    layer_1,  # layer that isochrone was built from
    isochrone,
    layer_2,  # points layer
    id_layer_1: str,
    id_layer_2,
    new_field_name: str,
    fields: list = None,  # do not include id or geometry. fields you want to retain from layer_2
):
    """
    For the isochrones of a layer of interest, counts the number of points from an input points. The output is for the layer of
    interest, not the isochrones.

    inputs:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - isochrone: (GeoDataFrame)isochrone layer for layer_1
    - layer_2:(GeoDataFrame) The points layer of interest
    - id_layer_1: (string) field name for layer 1 id field
    - id_layer_2: (string) field name for layer 2 id field
    - fields:(list) do not include id or geometry. fields you want to retain from layer_2
    - new_field_name: (string) field name for output layer

    output:
    - layer_1, with additional field [new_field_name] for number of points (from layer_2) within the provided isochrone. plus any additional
    fields provided in [fields]


    """

    # ten_mile_walk = 804.672  #half mile in meters

    # reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    isochrone = isochrone.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    # make a list of original columns for later
    layer_1_fields = layer_1.columns.tolist()

    # clip  layer of interest to those within the walking buffers
    layer_2_in_isochrone = layer_2.clip(isochrone)

    # join the lot ID to the isocrhone - one row per point/isochrone combination
    layers_sjoin = gpd.sjoin(layer_2_in_isochrone, isochrone, predicate="within")

    # add a field to get count
    layers_sjoin[new_field_name + "_count"] = 1

    ##CREATE DICTIONARY
    dict = {}
    dict[id_layer_2] = list
    dict[new_field_name + "_count"] = sum

    fields_to_enrich = [id_layer_2, (new_field_name + "_count")]

    if fields:
        for field in fields:
            dict[field] = list
        fields_to_enrich = fields_to_enrich + fields

    # group by lot ID but aggregate with lists of
    isochrone_grouped = layers_sjoin.groupby(by=id_layer_1).agg(dict).reset_index()

    # join back to layer_1
    layer_1_enriched = layer_1.merge(
        isochrone_grouped, on=id_layer_1, how="left"
    ).fillna(0)

    layer_1_enriched = layer_1_enriched[layer_1_fields + fields_to_enrich]

    return layer_1_enriched


def points_within_buffer(
    layer_1,  # layer to buffer
    layer_2,  # points layer
    buffer_distance,  # defaults to half mile walking buffer
    id_layer_1: str,
    id_layer_2: str,
    new_field_name: str,
    fields: list = None,  # do not include id or geometry. fields you want to retain from
):
    """
    Creates a buffer of given size around an input layer, and counts the number of points from an input points layer
    within the buffer.

    Inputs:
    - layer_1: (GeoDataFrame) The base layer being enriched
    - layer_2:(GeoDataFrame) The points layer of interest
    - buffer_distance: (number) in miles
    - id_layer_1: (string) field name for layer 1 id field
    - id_layer_2: (string) field name for layer 2 id field
    - fields:(list) do not include id or geometry. fields you want to retain from layer_2
    - new_field_name: (string) field name for output layer

    output:
    - layer_1, with additional field [new_field_name] for number of points (from layer_2) within the buffer.
    also adds any additional fields provided in [fields]

    """

    # ten_mile_walk = 804.672  #half mile in meters

    # reproject all to mass mainland
    mass_mainland_crs = "EPSG:26986"
    layer_1 = layer_1.to_crs(mass_mainland_crs)
    layer_2 = layer_2.to_crs(mass_mainland_crs)

    # make a list of original columns for later
    layer_1_fields = layer_1.columns.tolist()

    # buffer layer_1
    layer_1_buffer = buffer_gdf(gdf=layer_1, buffer_size=buffer_distance)

    # clip EV chargers (or layer of interest) to those within the walking buffers
    layer_2_in_layer_1_buffer = layer_2.clip(layer_1_buffer)

    # join the lot ID to the lot - one row per charger/ID combination
    # new_fields = [id_layer_2, 'geometry']
    # fields = fields_layer_2  + new_fields

    layers_sjoin = gpd.sjoin(
        layer_2_in_layer_1_buffer, layer_1_buffer, predicate="within"
    )

    # add a field to get count
    layers_sjoin[new_field_name + "_count"] = 1

    # add a field for distance
    def get_distance(row):
        origin = layer_1.loc[layer_1[id_layer_1] == row[id_layer_1]]
        destination = layer_2.loc[layer_2[id_layer_2] == row[id_layer_2]]
        distance = origin.distance(destination, align=False)
        distance_miles = (distance.iloc[0] / 1609).round(
            2
        )  # defaults to miles, can change later
        return distance_miles

    layers_sjoin["distance"] = layers_sjoin.apply(lambda row: get_distance(row), axis=1)

    ##CREATE DICTIONARY
    dict = {}
    dict[id_layer_2] = list
    dict["distance"] = list
    dict[new_field_name + "_count"] = sum

    fields_to_enrich = [id_layer_2, "distance", (new_field_name + "_count")]

    if fields:
        for field in fields:
            dict[field] = list
        fields_to_enrich = fields_to_enrich + fields

    # group by lot ID but aggregate with lists of
    layer_1_grouped = layers_sjoin.groupby(id_layer_1, as_index=False).agg(dict)

    # join back to layer_1
    layer_1_enriched = layer_1.merge(layer_1_grouped, on=id_layer_1, how="left").fillna(
        0
    )

    layer_1_enriched = layer_1_enriched[layer_1_fields + fields_to_enrich]

    return layer_1_enriched


def calculate_indicator_score(
    function: str,
    layer_1,
    layer_2=None,
    new_field_name=None,
    normalize=None,  # set normalize to True automatically?
    how=None,
    inverse=None,
    nan_value=None,
    stats=None,
    stats_field=None,
    point=None,
    unit=None,
    fields=None,
    buffer=None,
    layer_2_buffer=None,
    id_layer_1=None,
    id_layer_2=None,
    isochrone=None,
    buffer_distance=None,
):
    """
    Functions: 'if_overlap', 'calculate_overlap', 'overlap_stats', 'proximity', 'field_stats',   'points_within_isochrone', 'points_within_buffer'

    Rachel to fill in
    A function that fits in all other functions to calculate indicator scores

    Added 'layer_2_buffer' parameter to buffer layer_2 for running all functions

    """

    valid = {
        "if_overlap",
        "calculate_overlap",
        "overlap_stats",
        "proximity",
        "field_stats",
        "points_within_buffer",
        "points_within_isochrone",
    }

    if layer_2_buffer:
        layer_2 = buffer_gdf(gdf=layer_2, buffer_size=layer_2_buffer)

    if function not in valid:
        raise ValueError("function must be one of %r." % valid)

    if function == "if_overlap":
        return if_overlap(
            layer_1=layer_1,
            layer_2=layer_2,
            new_field_name=new_field_name,
            inverse=inverse,
            point=point,
        )

    elif function == "calculate_overlap":
        if not normalize:
            normalize = True

        return calculate_overlap(
            layer_1=layer_1,
            layer_2=layer_2,
            how=how,
            new_field_name=new_field_name,
            normalize=normalize,
            inverse=inverse,
            buffer=buffer,
        )

    elif function == "overlap_stats":
        if not stats:
            stats = "maj"
            normalize = False

        else:
            if not normalize:
                normalize = True

        return overlap_stats(
            layer_1=layer_1,
            layer_2=layer_2,
            stats_field=stats_field,
            new_field_name=new_field_name,
            stats=stats,
            normalize=normalize,
            inverse=inverse,
            nan_value=nan_value,
        )

    elif function == "proximity":
        if not normalize:
            normalize = True

        return proximity(
            layer_1=layer_1,
            layer_2=layer_2,
            new_field_name=new_field_name,
            normalize=normalize,
            inverse=inverse,
            unit=unit,
            fields=fields,
        )

    elif function == "field_stats":
        return field_stats(
            layer_1=layer_1,
            stats_field=stats_field,
            new_field_name=new_field_name,
            inverse=inverse,
            nan_value=nan_value,
        )

    elif function == "points_within_isochrone":
        return points_within_isochrone(
            layer_1=layer_1,
            layer_2=layer_2,
            new_field_name=new_field_name,
            id_layer_1=id_layer_1,
            id_layer_2=id_layer_2,
            isochrone=isochrone,
            fields=fields,
        )
    elif function == "points_within_buffer":
        return points_within_buffer(
            layer_1=layer_1,
            layer_2=layer_2,
            new_field_name=new_field_name,
            buffer_distance=buffer_distance,
            id_layer_1=id_layer_1,
            id_layer_2=id_layer_2,
        )
