#!/usr/bin/env python3

#
# NOSA HEADER START
#
# The contents of this file are subject to the terms of the NASA Open
# Source Agreement (NOSA), Version 1.3 only (the "Agreement").  You may
# not use this file except in compliance with the Agreement.
#
# You can obtain a copy of the agreement at
#   docs/NASA_Open_Source_Agreement_1.3.txt
# or
#   https://cdaweb.gsfc.nasa.gov/WebServices/NASA_Open_Source_Agreement_1.3.txt.
#
# See the Agreement for the specific language governing permissions
# and limitations under the Agreement.
#
# When distributing Covered Code, include this NOSA HEADER in each
# file and include the Agreement file at
# docs/NASA_Open_Source_Agreement_1.3.txt.  If applicable, add the
# following below this NOSA HEADER, with the fields enclosed by
# brackets "[]" replaced with your own identifying information:
# Portions Copyright [yyyy] [name of copyright owner]
#
# NOSA HEADER END
#
# Copyright (c) 2023-2025 United States Government as represented by
# the National Aeronautics and Space Administration. No copyright is
# claimed in the United States under Title 17, U.S.Code. All Other
# Rights Reserved.
#

"""
Module for unittest of the HdpWs class.<br>

Copyright &copy; 2023-2025 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""

import unittest
import datetime
import xml.etree.ElementTree as ET
import json

from context import hdpws  # pylint: disable=unused-import

from hdpws.hdpws import HdpWs   # pylint: disable=import-error
from hdpws import XHTML_NS, NAMESPACES as NS
from hdpws.resourcetype import ResourceType as rt


# More checks of the following result should probably be added
# but more checks risk failing when the contents of the database
# changes.

class TestHdpWs(unittest.TestCase):
    """
    Class for unittest of HdpWs class.
    """

    def __init__(self, *args, **kwargs):
        super(TestHdpWs, self).__init__(*args, **kwargs)
#        self._hdp = HdpWs(endpoint='http://localhost:8080/exist/restxq/')
        self._hdp = HdpWs(endpoint='http://localhost:8100/exist/restxq/')


    def test_get_application_interfaces(self):
        """
        Test for get_application_interfaces function.
        """

        result = self._hdp.get_application_interfaces()

        self.assertEqual(result['HttpStatus'], 200)
        application_interfaces = result['ApplicationInterface']
        self.assertTrue(len(application_interfaces) > 0)
        #print(f'ai = {application_interfaces}')
        self.assertTrue(application_interfaces[0] == 'API')


    def test_get_keywords(self):
        """
        Test for get_keywords function.
        """

        result = self._hdp.get_keywords()

        self.assertEqual(result['HttpStatus'], 200)
        keywords = result['Keyword']
        self.assertTrue(len(keywords) > 0)


    def test_get_instrument_ids(self):
        """
        Test for get_instrument_ids function.
        """

        result = self._hdp.get_instrument_ids()

        self.assertEqual(result['HttpStatus'], 200)
        instr_ids = result['InstrumentID']
        self.assertTrue(len(instr_ids) > 0)


    def test_get_repository_ids(self):
        """
        Test for get_repository_ids function.
        """

        result = self._hdp.get_repository_ids()

        self.assertEqual(result['HttpStatus'], 200)
        repo_ids = result['RepositoryID']
        self.assertTrue(len(repo_ids) > 0)


    def test_get_styles(self):
        """
        Test for get_style function.
        """

        result = self._hdp.get_styles()

        self.assertEqual(result['HttpStatus'], 200)
        styles = result['Style']
        self.assertTrue(len(styles) > 0)
        self.assertTrue(styles[0] == 'EPNTAP')


    def test_get_measurement_types(self):
        """
        Test for get_measurement_types function.
        """

        result = self._hdp.get_measurement_types()

        self.assertEqual(result['HttpStatus'], 200)
        measurement_types = result['MeasurementType']
        self.assertTrue(len(measurement_types) > 0)
        self.assertTrue(measurement_types[0] == 'ActivityIndex')


    def test_get_spectral_ranges(self):
        """
        Test for get_spectral_ranges function.
        """

        result = self._hdp.get_spectral_ranges()

        self.assertEqual(result['HttpStatus'], 200)
        s_range = result['SpectralRange']
        self.assertTrue(len(s_range) > 0)
        self.assertTrue(s_range[0] == 'CaK')


    def test_get_observatory_group_ids(self):
        """
        Test for get_observatory_group_ids function.
        """

        result = self._hdp.get_observatory_group_ids()

        self.assertEqual(result['HttpStatus'], 200)
        obs_grp_ids = result['ObservatoryGroupID']
        self.assertTrue(len(obs_grp_ids) > 0)


    def test_get_observatory_ids(self):
        """
        Test for get_observatory_ids function.
        """

        result = self._hdp.get_observatory_ids()

        self.assertEqual(result['HttpStatus'], 200)
        obs_ids = result['ObservatoryID']
        self.assertTrue(len(obs_ids) > 0)


    def test_get_observed_regions(self):
        """
        Test for get_observed_regions function.
        """

        result = self._hdp.get_observed_regions()

        self.assertEqual(result['HttpStatus'], 200)
        obs_regions = result['ObservedRegion']
        self.assertTrue(len(obs_regions) > 0)
        self.assertTrue(obs_regions[0] == 'Asteroid')


    def test_get_spase(self):
        """
        Test for get_spase function.
        """

        resource_ids = [ 
            #'spase://NASA/Collection/IRIS_AIA',
            'spase://NASA/Collection/IRIS/IRIS_Hinode',
            'spase://SMWG/Service/CCMC/Models',
            'spase://NASA/NumericalData/LANL/1991/SOPA+ESP/PT10M'
        ]   
        result = self._hdp.get_spase(resource_ids)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID', namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        #print(f'resources = {resource_ids}')
        #print(f'result_ids = {result_ids}')
        # self.assertTrue(len(result_ids) == 3) 
        # above should be == 2 when duplicate is removed from hdp and
        # then the following will work
        self.assertTrue(sorted(result_ids) == sorted(resource_ids))


    def test_get_spase_w_prior_ids(self):
        """
        Test for get_spase function using PriorID values.
        """

        resource_ids = [ 
            'spase://NASA/Collection/IRIS/IRIS_Hinode',
            'spase://NASA/Catalog/CarringtonEvent/AuroralSightings',
            'spase://NASA/NumericalData/LANL/1991/SOPA+ESP/PT10M'
        ]   
        prior_ids = [ 
            'spase://NASA/Collection/IRIS_HINODE',
            'spase://NASA/Catalog/Carrington_Event/Great_Magnetic_Storm_of_1859_List_of_Auroral_Sightings',
            'spase://VSPO/NumericalData/LANL/1991/SOPA+ESP/PT10M'
        ]   
        result = self._hdp.get_spase(prior_ids)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID', namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        #print(f'resources = {resource_ids}')
        #print(f'prior_ids = {prior_ids}')
        #print(f'result_ids = {result_ids}')
        # self.assertTrue(len(result_ids) == 3) 
        # above should be == 2 when duplicate is removed from hdp and
        # then the following will work
        self.assertTrue(sorted(result_ids) == sorted(resource_ids))


    def test_get_spase_if_modified_since(self):
        """
        Test for get_spase function's if_modified_since option.
        """

        resource_ids = [ 
            'spase://NASA/NumericalData/Wind/MFI/PT03S'
        ]   
        result = self._hdp.get_spase(resource_ids)

        self.assertEqual(result['HttpStatus'], 200)

        last_modified = result['Last-Modified']
        self.assertIsNotNone(last_modified)

        result = self._hdp.get_spase(resource_ids, 
                                     if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 304)

        last_modified -= datetime.timedelta(seconds=5)
        result = self._hdp.get_spase(resource_ids, 
                                     if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 200)


    def test_get_spase_url(self):
        """
        Test for get_spase_url function.
        """

        resource_id = 'spase://NASA/NumericalData/Wind/MFI/PT03S'

        result = self._hdp.get_spase_url(resource_id)

        self.assertIsNotNone(result)
        self.assertEqual(result, 
                         self._hdp.endpoint + 'Spase?ResourceID=' + \
                         resource_id)


    def test_get_spase_html(self):
        """
        Test for get_spase_html function.
        """

        resource_id = 'spase://NASA/NumericalData/Wind/MFI/PT03S'

        result = self._hdp.get_spase_html(resource_id)

        self.assertEqual(result['HttpStatus'], 200)

        last_modified = result['Last-Modified']
        self.assertIsNotNone(last_modified)

        result = self._hdp.get_spase_html(resource_id, 
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 304)

        last_modified -= datetime.timedelta(seconds=5)
        result = self._hdp.get_spase_html(resource_id, 
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 200)
        result_element = ET.fromstring(result['Result'])
        self.assertEqual(result_element.tag, 
                         '{' + XHTML_NS + '}html')


    def test_get_spase_json_ld(self):
        """
        Test for get_spase_json_ld function.
        """

        resource_id = 'spase://NASA/NumericalData/Wind/MFI/PT03S'

        result = self._hdp.get_spase_json_ld(resource_id)

        self.assertEqual(result['HttpStatus'], 200)

        last_modified = result['Last-Modified']
        self.assertIsNotNone(last_modified)

        result = self._hdp.get_spase_json_ld(resource_id, 
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 304)

        last_modified -= datetime.timedelta(seconds=5)
        result = self._hdp.get_spase_json_ld(resource_id, 
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 200)
        json_ld = json.loads(result['Result'])
        self.assertEqual(json_ld['@context'], 'https://schema.org/')
        self.assertEqual(json_ld['@type'], 'Dataset')
#        print(result['Result'])
#        result_element = ET.fromstring(result['Result'])
#        self.assertEqual(result_element.tag, 
#                         '{' + XHTML_NS + '}html')


    def test_get_spase_data(self):
        """
        Test for get_spase_data function.
        """

        query = { 
            'ResourceID': ['spase://NASA/NumericalData/ACE/CRIS/L2/P1D',
                'spase://NASA/NumericalData/ACE/CRIS/L2/PT1H'
            ],  
#            'DOI': ['10.48322/e0dc-0h53'],
#            'InstrumentID': 'spase://SMWG/Instrument/ACE/CRIS',
#            'ObservatoryID': 'spase://SMWG/Observatory/ACE',
#            'Cadence': '=PT1H',
#            'ObservedRegion': 'Heliosphere.NearEarth',
#            'MeasurementType': 'EnergeticParticles',
#            'AccessRights': 'Open',
#            'Format': 'CDF'
        }

        types = [rt.NUMERICAL_DATA, rt.DISPLAY_DATA]
        time_range = ['2022-01-01', '2022-01-02']

        result = self._hdp.get_spase_data(types, query, time_range)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 2)
        self.assertTrue(sorted(result_ids) == sorted(query['ResourceID']))


    def test_get_spase_data_if_modified_since(self):
        """
        Test for get_spase_data function's if_modified_since option.
        """

        query = { 
            'ResourceID': ['spase://NASA/NumericalData/ACE/CRIS/L2/P1D'],  
        }

        types = [rt.NUMERICAL_DATA, rt.DISPLAY_DATA]
        time_range = ['2022-01-01', '2022-01-02']

        result = self._hdp.get_spase_data(types, query, time_range)

        self.assertEqual(result['HttpStatus'], 200)

        last_modified = result['Last-Modified']
        last_modified += datetime.timedelta(seconds=1)
        self.assertIsNotNone(last_modified)

        result = self._hdp.get_spase_data(types, query, time_range,
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 304)

        last_modified -= datetime.timedelta(seconds=5)
        result = self._hdp.get_spase_data(types, query, time_range,
                                          if_modified_since=last_modified)

        self.assertEqual(result['HttpStatus'], 200)


    def test_get_spase_catalog(self):
        """
        Test for get_spase_catalog function.
        """

        #query = { 
        #    'InstrumentID': 'spase://SMWG/Instrument/ACE/MAG',
        #    'PhenomenonType': 'MagneticCloud',
        #    'Description': 'ICME'
        #} 
        #time_range = ['1999-01-01', '1999-01-02']
        query = { 
            'InstrumentID': 'spase://SMWG/Instrument/Wind/MFI',
            'PhenomenonType': 'SolarWindExtreme'
        } 
        time_range = ['1999-01-01', '1999-01-02']

        result = self._hdp.get_spase_catalog(query, time_range)

        #print(f'get_spase_catalog HttpStatus = {result["HttpStatus"]}')
        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        #self.assertTrue(result_ids[0] == 'spase://NASA/Catalog/CME-ICME_Cho2003')
        self.assertTrue(result_ids[0] == 'spase://NASA/Catalog/ISTP/SWCAT')


    def test_get_spase_catalog_prior_id(self):
        """
        Test for get_spase_catalog function with a PriorID value for 
        ResourceID query.
        """

        #time_range = ['1999-01-01', '1999-01-02']
        query = { 
            'ResourceID': 'spase://VSPO/Catalog/ISTP/SWCAT'
        } 
        time_range = ['1999-01-01', '1999-01-02']

        result = self._hdp.get_spase_catalog(query, time_range)

        #print(f'get_spase_catalog HttpStatus = {result["HttpStatus"]}')
        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        self.assertTrue(result_ids[0] == 'spase://NASA/Catalog/ISTP/SWCAT')


    def test_get_spase_collection(self):
        """
        Test for get_spase_collection function.
        """

        #query = { 
        #    'ResourceID': 'spase://NASA/Collection/IRIS_AIA',
        #    'MemberID': 'spase://NASA/NumericalData/SDO/AIA/PT10S',
        #    'Description': 'IRIS AND SDO and AIA'
        #} 
        query = { 
            'ResourceID': 'spase://NASA/Collection/IRIS/IRIS_Hinode',
            'MemberID': 'spase://NASA/NumericalData/IRIS/IRIS/PT1S',
            'Description': 'IRIS AND EIS and Hinode'
        } 

        result = self._hdp.get_spase_collection(query)

        #print(f'get_spase_collection HttpStatus = {result["HttpStatus"]}')
        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        #self.assertTrue(result_ids[0] == 'spase://NASA/Collection/IRIS_AIA')
        self.assertTrue(result_ids[0] == 'spase://NASA/Collection/IRIS/IRIS_Hinode')


    def test_get_spase_collection_prior_id(self):
        """
        Test for get_spase_collection function with a prior_id.
        """

        query = { 
            # PriorID
            'ResourceID': 'spase://NASA/Collection/IRIS_HINODE',
        } 

        result = self._hdp.get_spase_collection(query)

        #print(f'get_spase_collection HttpStatus = {result["HttpStatus"]}')
        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        #print(f'get_spase_collection: result_ids = {result_ids}')
        self.assertTrue(len(result_ids) == 1)
        self.assertTrue(result_ids[0] == 'spase://NASA/Collection/IRIS/IRIS_Hinode')


    def test_get_spase_document(self):
        """
        Test for get_spase_document function.
        """

        query = { 
            'ResourceID': 'spase://SMWG/Document/HPDE/Policy/HP_DataPolicy_v1.2',
            'DOI': '10.21978/P83P78',
            'Description': '"Program Data Management Plan"'
        } 

        result = self._hdp.get_spase_document(query)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        self.assertTrue(result_ids[0] == 'spase://SMWG/Document/HPDE/Policy/HP_DataPolicy_v1.2')


    def test_get_spase_service(self):
        """
        Test for get_spase_service function.
        """

        query = {
            'ResourceID': 'spase://CCMC/Service/InstantRun',
            'Description': '"Instant-Run"'
        }  

        result = self._hdp.get_spase_service(query)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        self.assertTrue(result_ids[0] == 'spase://CCMC/Service/InstantRun')


    def test_get_spase_software(self):
        """
        Test for get_spase_software function.
        """

        query = {
            'ResourceID': 'spase://CCMC/Software/Kamodo',
            'CodeLanguage': 'Python',
            'Description': '"space weather models and data"'
        }  

        result = self._hdp.get_spase_software(query)

        self.assertEqual(result['HttpStatus'], 200)
        result = result['Result']
        result_id_elements = result.findall('.//ResourceID',
                                            namespaces=NS)
        result_ids = list(map(lambda e: e.text, result_id_elements))
        self.assertTrue(len(result_ids) == 1)
        self.assertTrue(result_ids[0] == 'spase://CCMC/Software/Kamodo')


if __name__ == '__main__':
    unittest.main()
