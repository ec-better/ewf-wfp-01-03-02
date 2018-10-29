#!/opt/anaconda/bin/python

import sys
import os
import string
import numpy as np
from osgeo import gdal, ogr, osr

def matrix_sum(mat1, mat2, no_data_value=None):
    if no_data_value is not None:
        if not isinstance(mat1, int):
            mat1[(mat1 == no_data_value)] = 0
        if not isinstance(mat2, int):
            mat2[(mat2 == no_data_value)] = 0
    return mat1 + mat2

def mask_matrix(input_mat, threshold_value, greater_than, no_data_value=None):
    if no_data_value is not None:
        input_mat[(input_mat == no_data_value)] = 0
    if greater_than:
        result = np.where(input_mat > threshold_value, 1, 0)
    else: 
        result = np.where((input_mat < threshold_value) & (input_mat > 0), 1, 0)

    
    return result    

def crop_image(input_image, polygon_wkt, output_path):
    if '.gz' in input_image:
        dataset = gdal.Open('/vsigzip//vsicurl/%s' % input_image)
    else:
        dataset = gdal.Open(input_image)
    polygon_ogr = ogr.CreateGeometryFromWkt(polygon_wkt)
    envelope = polygon_ogr.GetEnvelope()
    bounds = [envelope[0], envelope[2], envelope[1], envelope[3]]
    gdal.Warp(output_path, dataset, format="GTiff", outputBoundsSRS='EPSG:4326', outputBounds=bounds)
    
def write_output_image(filepath, output_matrix, image_format, mask=None):
    driver = gdal.GetDriverByName(image_format)
    out_rows = np.size(output_matrix, 0)
    out_columns = np.size(output_matrix, 1)
    if mask is not None:
        output = driver.Create(filepath, out_rows, out_columns, 2, gdal.GDT_Float32)
        mask_band = output.GetRasterBand(2)
        mask_band.WriteArray(mask)
    else:
        output = driver.Create(filepath, out_rows, out_columns, 1, gdal.GDT_Float32)
    
    raster_band = output.GetRasterBand(1)
    raster_band.WriteArray(output_matrix)
    