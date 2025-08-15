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
Example Heliophysics Data Portal (HDP) web services client.
https://heliophysicsdata.gsfc.nasa.gov/WebServices/.

Copyright &copy; 2023-2025 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""

import sys
import getopt
import json
import logging
import logging.config
from typing import Dict, List
import xml.etree.ElementTree as ET  # pylint: disable=unused-import
import datetime
import urllib3


from hdpws.hdpws import HdpWs
from hdpws import NAMESPACES as NS
from hdpws.resourcetype import ResourceType as rt


logging.basicConfig()
LOGGING_CONFIG_FILE = 'logging_config.json'
try:
    with open(LOGGING_CONFIG_FILE, 'r', encoding='utf-8') as fd:
        logging.config.dictConfig(json.load(fd))
except BaseException as exc:    # pylint: disable=broad-except
    if not isinstance(exc, FileNotFoundError):
        print('Logging configuration failed')
        print('Exception: ', exc)
        print('Ignoring failure')
        print()


ENDPOINT = "https://heliophysicsdata.gsfc.nasa.gov/WS/hdp/1/"
#ENDPOINT = "http://heliophysicsdata-dev.sci.gsfc.nasa.gov/WS/hdp/1/"
#ENDPOINT = "http://localhost:8100/exist/restxq/"
#ENDPOINT = "http://localhost:8080/exist/restxq/"
#CA_CERTS = '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'


def print_usage(
        name: str
    ) -> None:
    """
    Prints program usage information to stdout.

    Parameters
    ----------
    name
        name of this program

    Returns
    -------
    None
    """
    print(f'USAGE: {name} [-e url][-d][-c cacerts][-h]')
    print('WHERE: url = HDP web service endpoint URL')
    print('       -d disables TLS server certificate validation')
    print('       cacerts = CA certificate filename')


# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def example(
        argv: List[str]
    ) -> None:
    """
    Example Heliophysics Data Portal (HDP) web service client.
    Includes example calls to most of the web services.

    Parameters
    ----------
    argv
        Command-line arguments.<br>
        -e url or --endpoint=url where url is the cdas web service endpoint
            URL to use.<br>
        -c url or --cacerts=filename where filename is the name of the file
            containing the CA certificates to use.<br>
        -d or --disable-cert-check to disable verification of the server's
            certificate
        -h or --help prints help information.
    """

    try:
        opts = getopt.getopt(argv[1:], 'he:c:d',
                             ['help', 'endpoint=', 'cacerts=',
                              'disable-cert-check'])[0]
    except getopt.GetoptError:
        print('ERROR: invalid option')
        print_usage(argv[0])
        sys.exit(2)

    endpoint = ENDPOINT
    ca_certs = None
    disable_ssl_certificate_validation = False

    for opt, arg in opts:
        if opt in ('-e', '--endpoint'):
            endpoint = arg
        elif opt in ('-c', '--cacerts'):
            ca_certs = arg
        elif opt in ('-d', '--disable-cert-check'):
            disable_ssl_certificate_validation = True
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        elif opt in ('-h', '--help'):
            print_usage(argv[0])
            sys.exit()

    hdp = HdpWs(endpoint=endpoint, ca_certs=ca_certs,
                disable_ssl_certificate_validation=
                disable_ssl_certificate_validation, user_agent='Example')


    result = hdp.get_application_interfaces()
    if result['HttpStatus'] == 200:
        print('HDP ApplicationInterfaces:')
        for value in result['ApplicationInterface']:
            print(f'    {value}')
    else:
        print_error('hdp.get_application_interfaces', result)

    result = hdp.get_keywords()
    if result['HttpStatus'] == 200:
        print('HDP Keywords:')
        for value in result['Keyword'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_keywords', result)

    result = hdp.get_instrument_ids()
    if result['HttpStatus'] == 200:
        print('HDP InstrumentIDs:')
        for value in result['InstrumentID'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_instrument_ids', result)

    result = hdp.get_repository_ids()
    if result['HttpStatus'] == 200:
        print('HDP RepositoryIDs:')
        for value in result['RepositoryID'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_repository_ids', result)

    result = hdp.get_measurement_types()
    if result['HttpStatus'] == 200:
        print('HDP MeasurementTypes:')
        for value in result['MeasurementType']:
            print(f'    {value}')
    else:
        print_error('hdp.get_measurement_types', result)

    result = hdp.get_spectral_ranges()
    if result['HttpStatus'] == 200:
        print('HDP SpectralRanges:')
        for value in result['SpectralRange']:
            print(f'    {value}')
    else:
        print_error('hdp.get_spectral_ranges', result)

    result = hdp.get_phenomenon_types()
    if result['HttpStatus'] == 200:
        print('HDP PhenomenonType:')
        for value in result['PhenomenonType']:
            print(f'    {value}')
    else:
        print_error('hdp.get_phenomenon_types', result)

    result = hdp.get_observatory_group_ids()
    if result['HttpStatus'] == 200:
        print('HDP ObservatoryGroupIDs:')
        for value in result['ObservatoryGroupID'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_observatory_group_ids', result)

    result = hdp.get_observatory_ids()
    if result['HttpStatus'] == 200:
        print('HDP ObservatoryIDs:')
        for value in result['ObservatoryID'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_observatory_group_ids', result)

    result = hdp.get_observed_regions()
    if result['HttpStatus'] == 200:
        print('HDP Observed Regions:')
        for value in result['ObservedRegion'][0:5]:
            print(f'    {value}')
        print('    ...')
    else:
        print_error('hdp.get_observed_regions', result)

    result = hdp.get_styles()
    if result['HttpStatus'] == 200:
        print('HDP Styles:')
        for value in result['Style']:
            print(f'    {value}')
    else:
        print_error('hdp.get_styles', result)


    resource_ids = [
        'spase://NASA/Collection/IRIS_AIA',
        'spase://SMWG/Service/CCMC/Models'
    ]
    result = hdp.get_spase(resource_ids)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('get_spase Result ResourceIDs:')
        for spase in result['Result'].findall('.//Spase', namespaces=NS):
            print(spase.findall('.//ResourceID', namespaces=NS)[0].text)
            print('    ', spase.findall('.//ResourceName', namespaces=NS)[0].text)
        if 'Last-Modified' in result:
            last_modified = result['Last-Modified']
            print('last_modified = ', last_modified.isoformat())
    else:
        print_error('hdp.get_spase', result)

    if last_modified is not None:
        #last_modified -= datetime.timedelta(seconds=1)
        result = hdp.get_spase(resource_ids, if_modified_since=last_modified)

        if result['HttpStatus'] == 304:
            print('get_spase if_modified_since ', last_modified.isoformat(),
                  'return Not Modified')
        else:
            print_error('hdp.get_spase if_modified_since', result)

    result = hdp.get_spase_url('spase://NASA/NumericalData/Wind/MFI/PT03S')

    if result is not None:
        print('get_spase_url returned:', result)
    else:
        print('get_spase_url failed')

    result = hdp.get_spase_html('spase://NASA/NumericalData/Wind/MFI/PT03S')

    if result is not None:
        print('get_spase_html was successful')
        #print('HTML result', result)
    else:
        print('get_spase_html failed')


    query = {
        'ResourceID': ['spase://NASA/NumericalData/ACE/CRIS/L2/P1D',
            'spase://NASA/NumericalData/ACE/CRIS/L2/PT1H'
        ],
#        'InstrumentID': 'spase://SMWG/Instrument/ACE/CRIS',
#        'ObservatoryID': 'spase://SMWG/Observatory/ACE',
#        'Cadence': '=PT1H',
#        'ObservedRegion': 'Heliosphere.NearEarth',
#        'MeasurementType': 'EnergeticParticles',
#        'AccessRights': 'Open',
#        'Format': 'CDF'
    }
    types = [rt.NUMERICAL_DATA, rt.DISPLAY_DATA]
    time_range = ['2022-01-01', '2022-01-02']

    result = hdp.get_spase_data(types, query, time_range)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('get_spase_data Result ResourceIDs:')
        for r_id in result['Result'].findall('.//ResourceID', namespaces=NS):
            print(r_id.text)
        if 'Last-Modified' in result:
            last_modified = result['Last-Modified']
            print('last_modified = ', last_modified.isoformat())
        else:
            last_modified = None
    else:
        print_error('hdp.get_spase_data', result)

    if last_modified is not None:
        last_modified += datetime.timedelta(seconds=5)
        result = hdp.get_spase_data(types, query, time_range,
                                    if_modified_since=last_modified)
        if result['HttpStatus'] == 304:
            print('get_spase_data if_modified_since ',
                  last_modified.isoformat(), 'return Not Modified')
        else:
            print_error('hdp.get_spase_data if_modified_since', result)

    query = {
        'ResourceID': ['spase://NASA/NumericalData/ACE/MAG/L2/PT16S', 'bad']
    }

    result = hdp.get_spase_data(types, query)
    if result['HttpStatus'] == 200:
        print('get_spase_data Result:')
        print(result['Result'])
    else:
        print_error('hdp.get_spase_data', result)


    query = {
        'InstrumentID': 'spase://SMWG/Instrument/ACE/MAG',
        'PhenomenonType': 'MagneticCloud',
        'Description': 'ICME'
#        'Keyword': 'current sheet'
    }
    time_range = ['1999-01-01', '1999-01-02']

    result = hdp.get_spase_catalog(query, time_range)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('Result Catalogs:')
        for catalog in result['Result'].findall('.//Catalog', namespaces=NS):
            print(catalog.findall('.//ResourceID', namespaces=NS)[0].text)
            print('    ', catalog.findall('.//ResourceName', namespaces=NS)[0].text)
            #ET.indent(catalog)
            #print(ET.tostring(catalog, encoding='unicode',
            #                  default_namespace=SPASE_NS))
    else:
        print_error('hdp.get_spase_catalog', result)


    query = {
        'ResourceID': 'spase://NASA/Collection/IRIS_AIA',
        'MemberID': 'spase://NASA/NumericalData/SDO/AIA/PT10S',
        'Description': 'IRIS AND SDO and AIA'
    }

    result = hdp.get_spase_collection(query)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('Result Collections:')
        for collection in result['Result'].findall('.//Collection', namespaces=NS):
            print(collection.findall('.//ResourceID', namespaces=NS)[0].text)
            print('    ', collection.findall('.//ResourceName', namespaces=NS)[0].text)
            #ET.indent(collection)
            #print(ET.tostring(collection, encoding='unicode',
            #                  default_namespace=SPASE_NS))
    else:
        print_error('hdp.get_spase_collection', result)


    query = {
        'ResourceID': 'spase://SMWG/Document/HPDE/Policy/HP_DataPolicy_v1.2',
        'DOI': '10.21978/P83P78',
        'Description': '"Program Data Management Plan"'
    }

    result = hdp.get_spase_document(query)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('Result Documents:')
        for document in result['Result'].findall('.//Document', namespaces=NS):
            print(document.findall('.//ResourceID', namespaces=NS)[0].text)
            print('    ', document.findall('.//ResourceName', namespaces=NS)[0].text)
            #ET.indent(document)
            #print(ET.tostring(document, encoding='unicode',
            #                  default_namespace=SPASE_NS))
    else:
        print_error('hdp.get_spase_document', result)


    query = {
        'ResourceID': 'spase://CCMC/Software/Kamodo',
        'CodeLanguage': 'Python',
        'Description': '"space weather models and data"'
    }


    result = hdp.get_spase_software(query)
    if result['HttpStatus'] == 200:
        #print('HDP Spase:')
        #print(ET.tostring(result['Result']))
        print('Result Software:')
        for software in result['Result'].findall('.//Software', namespaces=NS):
            print(software.findall('.//ResourceID', namespaces=NS)[0].text)
            print('    ', software.findall('.//ResourceName', namespaces=NS)[0].text)
            #ET.indent(software)
            #print(ET.tostring(software, encoding='unicode',
            #                  default_namespace=SPASE_NS))
    else:
        print_error('hdp.get_spase_software', result)


def print_error(
        label: str,
        result: Dict
    ) -> None:
    """
    Prints an error result.

    Parameters
    ----------
    result
        Dictionary result returned by the hdpws.
    """
    print(f'{label} failed with status = {result["HttpStatus"]}')
    if 'ErrorMessage' in result:
        print(f'ErrorMessage = {result["ErrorMessage"]}')
        print(f'ErrorDescription = {result["ErrorDescription"]}')
    elif 'ErrorText' in result:
        print(f'HttpText = {result["ErrorText"]}')
    else:
        print('No ErrorText')


if __name__ == '__main__':
    example(sys.argv)
