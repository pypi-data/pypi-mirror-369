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
# Copyright (c) 2023 United States Government as represented by
# the National Aeronautics and Space Administration. No copyright is
# claimed in the United States under Title 17, U.S.Code. All Other
# Rights Reserved.
#

"""
Module for unittest of the AccessURL class.<br>

Copyright &copy; 2023 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""

import unittest
import xml.etree.ElementTree as ET
import copy

from context import hdpws  # pylint: disable=unused-import

from hdpws import NAMESPACES as NS
from hdpws.spase import AccessURL, HapiAccessURL, HAPI_DISPLAY_URL  # pylint: disable=import-error


BAD_ACCESS_URL = ET.fromstring('<BadAccessUrl/>')

TEST_NAME = 'CDAWeb HAPI Server'
TEST_URL = 'https://cdaweb.gsfc.nasa.gov/hapi'
TEST_STYLE = 'HAPI'
TEST_PRODUCT_KEYS = ['WI_H0_MFI@0', 'WI_H0_MFI@1', 'WI_H0_MFI@2']
TEST_DESCRIPTION = 'Web Service to this product using the HAPI interface.'
TEST_LANGUAGE = 'en'

TEST_ACCESS_URL = ET.fromstring(
'<AccessURL xmlns="http://www.spase-group.org/data/schema">\
<Name>' + TEST_NAME + '</Name>\
<URL>' + TEST_URL + '</URL>\
<Style>' + TEST_STYLE + '</Style>\
<ProductKey>' + TEST_PRODUCT_KEYS[0] + '</ProductKey>\
<ProductKey>' + TEST_PRODUCT_KEYS[1] + '</ProductKey>\
<ProductKey>' + TEST_PRODUCT_KEYS[2] + '</ProductKey>\
<Description>' + TEST_DESCRIPTION + '</Description>\
<Language>' + TEST_LANGUAGE + '</Language>\
</AccessURL>')


class TestAccessURL(unittest.TestCase):
    """
    Class for unittest of AccessURL class.
    """

    def __init__(self, *args, **kwargs):
        super(TestAccessURL, self).__init__(*args, **kwargs)


    def test_access_url_exception(self):
        """
        Test for constructor exception.
        """

        with self.assertRaises(ValueError):
            AccessURL(BAD_ACCESS_URL)



    def test_access_url_properties(self):
        """
        Test for AccessURL properties.
        """

        access_url = AccessURL(TEST_ACCESS_URL)

        self.assertEqual(access_url.name, TEST_NAME)
        self.assertEqual(access_url.url, TEST_URL)
        self.assertEqual(access_url.style, TEST_STYLE)
        for idx, product_key in enumerate(access_url.product_key):
            self.assertEqual(product_key, TEST_PRODUCT_KEYS[idx])
        self.assertEqual(access_url.description, TEST_DESCRIPTION)
        self.assertEqual(access_url.language, TEST_LANGUAGE)


class TestHapiAccessURL(unittest.TestCase):
    """
    Class for unittest of HapiAccessURL class.
    """

    def __init__(self, *args, **kwargs):
        super(TestHapiAccessURL, self).__init__(*args, **kwargs)


    def test_hapi_access_url_exception(self):
        """
        Test for constructor exception.
        """

        hapi_access_url = copy.deepcopy(TEST_ACCESS_URL)
        style = hapi_access_url.find('Style', namespaces=NS)
        self.assertIsNotNone(style)
        style.text = 'WebService'

        with self.assertRaises(ValueError):
            HapiAccessURL(hapi_access_url)

    def test_get_html_url(self):
        """
        Test for get_html_url method.
        """

        hapi_access_url = HapiAccessURL(TEST_ACCESS_URL)

        self.assertEqual(hapi_access_url.get_html_url(),
                         HAPI_DISPLAY_URL + '#url=' + hapi_access_url.url + \
                         '&id=' + TEST_PRODUCT_KEYS[0] + ',' + \
                         TEST_PRODUCT_KEYS[1] + ',' + \
                         TEST_PRODUCT_KEYS[2])


if __name__ == '__main__':
    unittest.main()
