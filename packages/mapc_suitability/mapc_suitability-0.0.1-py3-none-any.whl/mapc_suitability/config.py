import os

## THESE NEED TO BE UPDATED ANNUALLY ## 
boston_geojson_url = r'https://data.boston.gov/dataset/9ef4ed7e-f35c-4821-a27c-fd38a54a78ce/resource/15078d15-9dc5-4779-a15a-bc0f6bfbde0c/download/parcels__2024__geojson.zip'
boston_assessors_csv = r'http://data.boston.gov/dataset/e02c44d2-3c64-459c-8fe2-e1ce5f38a035/resource/6b7e460e-33f6-4e61-80bc-1bef2e73ac54/download/fy2025-property-assessment-data_12_30_2024.csv'

datasets_dir = r'K:\DataServices\Datasets'
mapc_lpd_folder = os.path.join(datasets_dir, 'Parcel_DB\Data\LPDB_Municipal_Data/current')
mass_mainland_crs = "EPSG:26986"