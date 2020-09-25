#!/bin/bash
# Create VRT files for the input source rasters in preparation for composite calculations.

#Create a text file with a list of the .tif files that will be composited
ls sentinel_data/*.tif > sentinel_data/composite_list.txt

# Step 1. Build vrt file and merge all rasters
gdalbuildvrt sentinel_data/raster.vrt -srcnodata 0 -input_file_list sentinel_data/composite_list.txt

# Step 2. Update VRT file with a pixel function for calculating median composite
python UpdateVRT.py

#Step 3. generate a Median Composite raster from a vrt file
gdal_translate --config GDAL_VRT_ENABLE_PYTHON YES sentinel_data/raster.vrt raster_data/composite_median.tif