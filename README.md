## Sentinel Project

### Introduction
This project includes a collection of python and shell scripts that provides capabilities for:
1) Automating data ingestion of Sentinel-2 Imagery for an Region of interest (ROI) over a given time period. 
2) An API to create composite images based on different methods such as median or average composite for overlapping images.
This is useful in combining time series of imagery and this is a type of **_temporal reduction_**. 
3) A CLI tool to resample images and aggregate them using various resampling techniques.

This project is written with the help of GDAL, OGR, 'sentinelsat' python package and other geo data science libaries. 

### How to run:

#### Prerequisites:
- Python v3.8
- Conda package manager (this makes installation of GDAL and dependencies easy)
Setup a conda environment and run ‘conda install gdal’
- QGIS to visualize the output results.
- Other python libraries listed in requirements.txt

#### Install required packages
`$ pip install -r requirements.txt
`
#### Step 1: Data download
- The first step is to download the sentinel imagery and extract it. 

- In preparation for this step **update username and password in 'data_download.py'** with your Copernicus Oepn Data Hub credentials. See line 21.
You can create a free account if you don't have one from [this link](https://scihub.copernicus.eu/dhus/#/self-registration).

- By default the script will download upto 5 images for the 'S2MSI2A' imagery product from the last 10 days for the ROI specified. 
These settings can easily be updated in data_download.py (line 26-30). 

- The second preparatory step is to update your ROI with a geojson file, 
a default/example ROI file is included in vector_data/ directory named 'ROI.geojson'.

- Once the preparatory steps are complete, run sentinel2_to_tif.sh. 

`$ /bin/bash sentinel2_to_tif.sh`

- This will download the images from sentinel-2, 
extract only the 10m data from it and convert it to TIFF raster files. 
      
#### Step 2: Create median composites
- The second step is to create a median composite image.

`$ /bin/bash create_median_composite.sh`

What does the script do?
- Add a list of source TIFF files to a txt file.
- Use GDAL gdalbuildvrt program to create a VRT (GDAL Virtual Dataset) file. This will generate a .vrt file for the input raster TIFFs. 
This file is created in /sentinel_data/ directory along with the raster files.
- Update VRT file with a pixel function that will apply a median composite on the rasters. 
This function is a Python code snippet, embedded in the VRT file and this aspect is automated involving no manual intervention.
- Generate a median composite raster from a vrt file to create a median composite raster. 

#### Step 3 Resample images with reducer selector: 
Use CLI tool to resample and reduce an image. 
The CLI tool provides an API to specify input image, input and output cell sizes, 
ROI and reducer selector among other options.

Example run for resampling from 10m to 500m with the ‘average’ option. This is an example, it’ll vary based on your input source image name, please update that before running.

`$ python resample_reducer.py -f sentinel_data/10m_S2A_MSIL2A_20200831T073621_N0214_R092_T37MBU_20200831T101156.ti f -o raster_data/aggregate_raster_avg.tif -ci 10 -co 500 -ri vector_data/ROI_clip.geojson -r average`

API help can be accessed by running:

`$ python resample_reducer.py -h`

The API has the following options:

`usage: resample_reducer.py [-h] -f FILE -o OUTPUT -ci IN_CELLSIZE -co OUT_CELLSIZE -ri REGION [-r RESAMPLE]
`

It supports all built-in GDAL resampling techniques such as:
_near, bilinear, cubic, cubicspline, lanczos, average, mode, max, min, 
med, q1, q3, sum_

**NOTE:** ‘sum’ method requires GDAL v3.1 or higher.