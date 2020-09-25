"""
This script will download 5 recent images from a region in Africa based on a region of interest.
The script will unzip the contents and remove the zipped files after completion of unzip.
"""
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import logging
import os, zipfile

#Set logging
logger = logging.getLogger('sentinelsat')
logger.setLevel('INFO')
h = logging.StreamHandler()
h.setLevel('INFO')
fmt = logging.Formatter('%(message)s')
h.setFormatter(fmt)
logger.addHandler(h)

#specify output data path
out_data_dir = os.path.join(os.getcwd(), r'sentinel_data')

api = SentinelAPI('username', 'password', 'https://scihub.copernicus.eu/dhus')

footprint = geojson_to_wkt(read_geojson(os.path.join(os.getcwd(), r'vector_data/ROI.geojson')))

# Get 5 products for a time range
products = api.query(footprint,
                     date=('NOW-10DAYS','NOW'),
                     platformname='Sentinel-2',limit = 5,
                     producttype = 'S2MSI2A'
                     )

api.download_all(products, directory_path=out_data_dir)

# convert to Pandas DataFrame
# products_df = api.to_dataframe(products)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
# api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
out_gdf = api.to_geodataframe(products)
out_gdf.to_file(r"vector_data\out_footprint.geojson", driver='GeoJSON')

#unzip the downloaded products
os.chdir(out_data_dir)
extension = ".zip"
for item in os.listdir(out_data_dir):
    if item.endswith(extension):
        file_name = os.path.abspath(item)  # get full path of files
        zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
        zip_ref.extractall(out_data_dir)  # extract file to dir
        zip_ref.close()  # close file
        os.remove(file_name)  # delete zipped file