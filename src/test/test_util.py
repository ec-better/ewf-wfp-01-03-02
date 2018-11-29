#!/opt/anaconda/bin/python

import sys
import os
import unittest
import string
import numpy as np
from StringIO import StringIO
import py_compile
from osgeo import gdal, ogr

sys.path.append('/workspace/wfp-01-03-02/src/main/app-resources/notebook/libexec')

from aux_functions import matrix_sum, mask_matrix, crop_image, write_output_image
# Simulating the Runtime environment
os.environ['TMPDIR'] = '/tmp'
os.environ['_CIOP_APPLICATION_PATH'] = '/application'
os.environ['ciop_job_nodeid'] = 'dummy'
os.environ['ciop_wf_run_root'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'artifacts')

#sys.path.append('../main/app-resources/util/')

#from util import log_input

class NodeATestCase(unittest.TestCase):

    def setUp(self):
        self.mat1 = np.matrix('1, 1; 1, 1')
        self.mat2 = np.matrix('2, 2; 2, 2')
        self.mat3 = np.matrix('-9999, -9999; -9999, -9999')
        self.mat4 = np.matrix('-9999, 2; 3, -9999')
        self.mat5 = 0
        self.test_img = "/workspace/data/test_image_chirps.tif"
    
    def test_matrix_sum(self):
        sum1 = matrix_sum(self.mat1, self.mat2)
        self.assertTrue((sum1 == np.matrix('3, 3; 3, 3')).all())
    
    def test_matrix_sum_with_no_data_value(self):
        sum1 = matrix_sum(self.mat1, self.mat4, -9999)
        self.assertTrue((sum1 == np.matrix('1, 3; 4, 1')).all())
    
    def test_matrix_sum_with_different_sizes(self):
        sum1 = matrix_sum(self.mat1, self.mat5, -9999)
        self.assertTrue((sum1 == self.mat1).all())
        
    def test_matrix_mask(self):
        masked_mat = mask_matrix(self.mat4, 1, True, -9999)
        self.assertTrue((masked_mat == np.matrix('0, 1; 1, 0')).all())
    
    def test_matrix_with_lower_operation(self):
        masked_mat = mask_matrix(self.mat4, 3, False, -9999)
        self.assertTrue((masked_mat == np.matrix('0, 1; 0, 0')).all())
        
    def test_crop_image(self):
        polygon = 'POLYGON((-30 -10, 20 -10, 20 40, -30 40, -30 -10))'
        cropped_image_path = "output.tif"
        crop_image(self.test_img, polygon, cropped_image_path)
        self.assertGreaterEqual(os.path.getsize(cropped_image_path), 0)
        os.remove('output.tif')
    
    def test_crop_image_remote_gzip(self):
        polygon = 'POLYGON((-30 -10, 20 -10, 20 40, -30 40, -30 -10))'
        image_url = 'ftp://ftp.chg.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/2017/chirps-v2.0.2017.08.10.tif.gz'
        cropped_image_path = "/workspace/wfp-01-03-02/src/test/output_from_gzip.tif"
        crop_image(image_url, polygon, cropped_image_path)
        self.assertGreaterEqual(os.path.getsize(cropped_image_path), 0)
        os.remove('output_from_gzip.tif')
        
    def test_write_image(self):
        matrix_rand = np.random.rand(30,30)
        mask_rand = np.random.randint(2, size=(30,30))
        filepath = "/workspace/wfp-01-03-02/src/test/output_test.tif"
        write_output_image(filepath, matrix_rand, "GTiff", mask=mask_rand)
        self.assertGreaterEqual(os.path.getsize(filepath), 0)
        os.remove('output_test.tif')
        
    def test_compile(self):
        try:
          py_compile.compile('../main/app-resources/notebook/run', doraise=True)
        except:
          self.fail('failed to compile src/main/app-resources/notebook/run')
 
if __name__ == '__main__':
    unittest.main()


