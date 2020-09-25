#!/bin/bash
# Download data from Sentinel-2
python data_download.py

# Takes sentinel-2 L2A data from downloads and convert it to tif images

for file in sentinel_data/*; do
    y=${file%.*}
    echo $y
    gdal_translate -of GTiff SENTINEL2_L2A:"$file"/MTD_MSIL2A.xml:10m:EPSG_32737 sentinel_data/10m_"${y##*/}".tif -co COMPRESS=LZW -co TILED=YES -a_nodata 0 --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS 2
done

