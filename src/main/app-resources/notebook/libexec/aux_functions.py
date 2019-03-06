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
        input_mat[(input_mat == no_data_value)] = -9999.0
    if greater_than:
        result = np.where(input_mat > threshold_value, 1, 0)
    else: 
        result = np.where((input_mat < threshold_value) & (input_mat >= 0), 1, 0)

    
    return result    

def crop_image(input_image, polygon_wkt, output_path):
    dataset = None
    crop_directory = os.path.dirname(output_path)
    if crop_directory is not '' and not os.path.exists(crop_directory):
        os.makedirs(crop_directory)
    if input_image.startswith('ftp://') or input_image.startswith('http'): 
        dataset = gdal.Open('/vsigzip//vsicurl/%s' % input_image)
    else:
        dataset = gdal.Open(input_image)
    no_data_value = dataset.GetRasterBand(1).GetNoDataValue()
    if no_data_value is None:
        no_data_value = dataset.GetRasterBand(1).ComputeRasterMinMax()[0]
    polygon_ogr = ogr.CreateGeometryFromWkt(polygon_wkt)
    envelope = polygon_ogr.GetEnvelope()
    bounds = [envelope[0], envelope[2], envelope[1], envelope[3]]
    gdal.Warp(output_path, dataset, format="GTiff", dstNodata=no_data_value, outputBoundsSRS='EPSG:4326', outputBounds=bounds)
    
def write_output_image(filepath, output_matrix, image_format, number_of_images, output_projection=None, output_geotransform=None, mask=None, no_data_value=None):
    driver = gdal.GetDriverByName(image_format)
    out_rows = np.size(output_matrix, 0)
    out_columns = np.size(output_matrix, 1)
    if mask is not None:
        output = driver.Create(filepath, out_columns, out_rows, 2, gdal.GDT_Float32)
        mask_band = output.GetRasterBand(2)
        mask_band.WriteArray(mask)
        if no_data_value is not None:
            output_matrix[mask >= number_of_images] = no_data_value
    else:
        output = driver.Create(filepath, out_columns, out_rows, 1, gdal.GDT_Float32)
        
    if output_projection is not None:
        output.SetProjection(output_projection)
    if output_geotransform is not None:
        output.SetGeoTransform(output_geotransform)
    
    raster_band = output.GetRasterBand(1)
    if no_data_value is not None:
        raster_band.SetNoDataValue(no_data_value)
    raster_band.WriteArray(output_matrix)
    
    output.FlushCache()
    
def get_matrix_list(image_list):
    mat_list = []
    for img in image_list:
        dataset = gdal.Open(img)
        product_array = dataset.GetRasterBand(1).ReadAsArray()
        mat_list.append(product_array)
        dataset = None
    return mat_list
    