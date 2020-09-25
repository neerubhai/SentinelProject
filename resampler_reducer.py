"""
An API to select reducer methods and resample image files based on a ROI
"""

import os
from osgeo import ogr, gdal
import argparse

def resample_reducer(image_file, output_file, in_cell_size, out_cell_size, roi, reducer_method):
    """
    Args:
        image_file: Input image file
        output_file: Output file after reducing
        in_cell_size: Input cell size
        out_cell_size: Output cell size to resample to.
        roi: GeoJSON file to clip extent of reducer operation
        reducer_method: reducer method to apply during resampling.
    Returns: None
    """
    """Get GeoJSON extents"""
    # Open datasets
    VectorFormat = 'GeoJSON'
    VectorDriver = ogr.GetDriverByName(VectorFormat)
    VectorDataset = VectorDriver.Open(roi, 0)  # 0=Read-only, 1=Read-Write
    layer = VectorDataset.GetLayer()
    FeatureCount = layer.GetFeatureCount()
    # Iterate through the geojson features (use the last)
    Count = 0
    for feature in layer:
        Count += 1
        print("Processing feature " + str(Count) + " of " + str(FeatureCount) + "...")

        geom = feature.GetGeometryRef()
        minX, maxX, minY, maxY = geom.GetEnvelope()  # Get bounding box of the geojson feature
    VectorDataset.Destroy()

    """Run aggregator function"""
    if reducer_method != "variance":
        os.system("gdalwarp -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:4326 -tr {cellsize} {cellsize} -r {reducer_method} {image_file} {output_file}"
                  .format(xmin=minX, ymin=minY, xmax=maxX, ymax=maxY,
                          cellsize=out_cell_size, reducer_method=reducer_method,
                          image_file=image_file, output_file=output_file))

    elif reducer_method == "variance":
        # First calculate average and resample to out_cell_size
        os.system("gdalwarp -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:4326 -tr {out_cs} {out_cs} -r average {image_file} raster_data/mean_course.tif"
                  .format(xmin=minX, ymin=minY, xmax=maxX, ymax=maxY,
                          out_cs=out_cell_size, image_file=image_file))
        # Next go back to source resolution aka in_cell_size
        os.system("gdalwarp -tr {in_cs} {in_cs} -r near raster_data/mean_course.tif raster_data/mean_fine.tif"
                  .format(in_cs=in_cell_size, output_file=output_file))
        #get the difference squared (X - MeanX)^2
        os.system("gdal_calc.py -A raster_data/mean_ras2.tif -B {image_file} --outfile=raster_data/diff_sqr.tif --type=Float32 --overwrite --calc='(B-A)^2'"
                  .format(image_file=image_file))
        #calculate variance by resampling to out_cell_size again and taking average
        os.system("gdalwarp -tr {out_cs} {out_cs} -r average raster_data/diff_sqr.tif {output_file}"
                  .format(out_cs=out_cell_size, output_file=output_file))


def main():
    """CLI interface for image reducer"""

    parser = argparse.ArgumentParser(description="Reducer option parser")
    parser.add_argument("-f",
                        "--file",
                        required=True,
                        help="Image file to reduce",
                        )
    parser.add_argument("-o",
                        "--output",
                        required=True,
                        help="Name of output file")
    parser.add_argument("-ci",
                        "--in_cellsize",
                        required=True,
                        help="Input Cell size")
    parser.add_argument("-co",
                        "--out_cellsize",
                        required=True,
                        help="Output Cell size")
    parser.add_argument("-ri",
                        "--region",
                        required=True,
                        help="Region of Interest (ROI) GeoJSON file")
    parser.add_argument("-r",
                        "--resample",
                        required=False,
                        help="Reduction technique: average, sum (> v3.1 GDAL), variance, med, mode, near, bilenear, cubic",
                        default="average")

    args = parser.parse_args()

    if args.file is None:
        raise ValueError("ERROR: No input files passed.")

    resample_reducer(args.file,
                     output_file=args.output,
                     in_cell_size=args.in_cellsize,
                     out_cell_size=args.out_cellsize,
                     roi=args.region,
                     reducer_method=args.resample)

if __name__ == '__main__':
    main()