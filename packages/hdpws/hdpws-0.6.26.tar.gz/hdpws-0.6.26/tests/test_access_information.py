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
from hdpws.spase import AccessInformation  # pylint: disable=import-error


BAD_ACCESS_INFO = ET.fromstring('<BadAccessInformation/>')

TEST_REPOSITORY_ID = 'spase://SMWG/Repository/NASA/GSFC/SPDF'
TEST_AVAILABILITY = 'Online'
TEST_ACCESS_RIGHTS = 'Open'
TEST_NAME = 'CDAWeb HAPI Server'
TEST_URL = 'https://cdaweb.gsfc.nasa.gov/hapi'
TEST_STYLE = 'HAPI'
TEST_PRODUCT_KEYS = ['WI_H0_MFI@0', 'WI_H0_MFI@1', 'WI_H0_MFI@2']
TEST_DESCRIPTION = 'Web Service to this product using the HAPI interface.'
TEST_LANGUAGE = 'en'
TEST_FORMAT = 'CSV'

TEST_ACCESS_INFO = ET.fromstring(
'<AccessInformation xmlns="http://www.spase-group.org/data/schema">\
<RepositoryID>' + TEST_REPOSITORY_ID + '</RepositoryID>\
<Availability>' + TEST_AVAILABILITY + '</Availability>\
<AccessRights>' + TEST_ACCESS_RIGHTS + '</AccessRights>\
<AccessURL>\
<Name>' + TEST_NAME + '</Name>\
<URL>' + TEST_URL + '</URL>\
<Style>' + TEST_STYLE + '</Style>\
<ProductKey>' + TEST_PRODUCT_KEYS[0] + '</ProductKey>\
<ProductKey>' + TEST_PRODUCT_KEYS[1] + '</ProductKey>\
<ProductKey>' + TEST_PRODUCT_KEYS[2] + '</ProductKey>\
<Description>' + TEST_DESCRIPTION + '</Description>\
<Language>' + TEST_LANGUAGE + '</Language>\
</AccessURL>\
<Format>' + TEST_FORMAT + '</Format>\
</AccessInformation>')


class TestAccessInformation(unittest.TestCase):
    """
    Class for unittest of AccessInformation class.
    """

    def __init__(self, *args, **kwargs):
        super(TestAccessInformation, self).__init__(*args, **kwargs)


    def test_access_information_exception(self):
        """
        Test for constructor exception.
        """

        with self.assertRaises(ValueError):
            AccessInformation(BAD_ACCESS_INFO)



    def test_access_information_properties(self):
        """
        Test for AccessInformation properties.
        """

        access_info = AccessInformation(TEST_ACCESS_INFO)

        self.assertEqual(access_info.repository_id, TEST_REPOSITORY_ID)
        self.assertEqual(access_info.availability, TEST_AVAILABILITY)
        self.assertEqual(access_info.access_rights, TEST_ACCESS_RIGHTS)
        self.assertListEqual(access_info.format, [TEST_FORMAT])



if __name__ == '__main__':
    unittest.main()
