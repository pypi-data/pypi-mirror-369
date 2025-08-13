import tricahue
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

fj_url = "charmmefj.synbiohub.org"
fj_user = ""
fj_pass = ""

sbh_url = "https://synbiohub.org"
sbh_user = "test@test.test"
sbh_pass = "test123"
sbh_collec = "XDC_package_test"

test_file_path ='tests/test_files'
excel_path = os.path.join(test_file_path, 'Medias.xlsm')

homespace = 'https://synbiohub.org/synbiotest'

fj_overwrite = False
sbh_overwrite=False

xdc = tricahue.XDC(input_excel_path = excel_path,
            fj_url = fj_url,
            fj_user = fj_user, 
            fj_pass = fj_pass, 
            sbh_url = sbh_url, 
            sbh_user = sbh_user, 
            sbh_pass = sbh_pass, 
            sbh_collection = sbh_collec, 
            sbh_collection_description = 'Tricahue XDC package test collection',
            sbh_overwrite = sbh_overwrite, 
            fj_overwrite = fj_overwrite, 
            homespace = homespace,
            fj_token = None, 
            sbh_token = None)

class Test_XDC(unittest.TestCase):
    def test_initialize(self):
        xdc.initialize()
        
