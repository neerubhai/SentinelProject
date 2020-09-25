"""
This module provides an API for updating VRT files.
Currently it supports median and average composites and can be extended easily for other composite types
by adding code snippet to the methods dictionary.
"""

import os

def add_pixel_fn(filename: str, composite_type: str) -> None:
    """inserts pixel-function into vrt file named 'filename'
    Args:
        filename (:obj:`string`): name of file, into which the function will be inserted
        composite_type (:obj:`string`): type of composite function
    """

    header = """  <VRTRasterBand dataType="UInt16" band="{band}" subClass="VRTDerivedRasterBand">"""
    contents = """
    <PixelFunctionType>{0}</PixelFunctionType>
    <PixelFunctionLanguage>Python</PixelFunctionLanguage>
    <PixelFunctionCode><![CDATA[{1}]]>
    </PixelFunctionCode>\n"""

    lines = open(filename, 'r').readlines()
    band=1

    for i, line in enumerate(lines):
        if line.lstrip().startswith('<VRTRasterBand'):
            lines[i] = header.format(band=band)
            lines.insert(i+1, contents.format(composite_type, get_composite_fn(composite_type)))
            band+=1
    open(filename, 'w').write("".join(lines))

def get_composite_fn(name: str) -> str:
    """retrieves code for resampling method
    Args:
        name (:obj:`string`): name of resampling method
    Returns:
        method :obj:`string`: code of resample method
    """

    methods = {
        "median":
        """
import numpy as np
def median(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
    temp_ar = np.empty(shape=[len(in_ar), in_ar[0].shape[0], in_ar[0].shape[1]])
    i = 0
    for tup in in_ar:
        temp_ar[i] = tup
        i+=1
    # reduce temp_ar and calculate median
    temp_ar[temp_ar == 0] = np.nan
    np.nanmedian(temp_ar, axis=0, out=out_ar)
""",
        "average":
        """
import numpy as np
def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
    div = np.zeros(in_ar[0].shape)
    for i in range(len(in_ar)):
        div += (in_ar[i] != 0)
    div[div == 0] = 1
    
    y = np.sum(in_ar, axis = 0, dtype = 'uint16')
    y = y / div
    
    np.clip(y,0,255, out = out_ar)
"""}

    if name not in methods:
        raise ValueError(
            "ERROR: Unrecognized resampling method (see documentation): '{}'.".
            format(name))

    return methods[name]


def main() -> None:
    filename = os.path.join(os.getcwd(), r'sentinel_data/raster.vrt')
    add_pixel_fn(filename=filename, composite_type="median")

if __name__ == '__main__':
    main()

