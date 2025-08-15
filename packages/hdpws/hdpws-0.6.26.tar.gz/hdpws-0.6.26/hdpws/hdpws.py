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
# Copyright (c) 2023-2024 United States Government as represented by
# the National Aeronautics and Space Administration. No copyright is
# claimed in the United States under Title 17, U.S.Code. All Other
# Rights Reserved.
#

""" 
Module for accessing the Heliophysics Data Portal (HDP) web services
https://heliophysicsdata.gsfc.nasa.gov/WebServices/.
"""

import platform
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import logging
from typing import Dict, List, Union
from datetime import datetime
import requests
from dateutil import parser

from hdpws import __version__, NAMESPACES as NS
from hdpws.dateinterval import DateInterval
from hdpws.resourcetype import ResourceType
from hdpws.spasehtmlparser import SpaseHtmlParser


#
# HTTP If-Modified-Since header datetime.strftime format value.
#
IF_MODIFIED_SINCE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'


class HdpWs:
    """
    Class representing the web service interface to NASA's
    Heliophysics Data Portal (HDP) <https://heliophysicsdata.gsfc.nasa.gov/>.

    Parameters
    ----------
    endpoint
        URL of the HDP web service.  If None, the default is
        'https://heliophysicsdata.gsfc.nasa.gov/WS/hdp/1/'.
    timeout
        Number of seconds to wait for a response from the server.
    proxy
        HTTP proxy information.  For example,<pre>
        proxies = {
          'http': 'http://10.10.1.10:3128',
          'https': 'http://10.10.1.10:1080',
        }</pre>
        Proxy information can also be set with environment variables.
        For example,<pre>
        $ export HTTP_PROXY="http://10.10.1.10:3128"
        $ export HTTPS_PROXY="http://10.10.1.10:1080"</pre>
    ca_certs
        Path to certificate authority (CA) certificates that will
        override the default bundle.
    disable_ssl_certificate_validation
        Flag indicating whether to validate the SSL certificate.
    user_agent
        A value that is appended to the HTTP User-Agent values.

    Notes
    -----
    The logger used by this class has the class' name (HdpWs).  By default,
    it is configured with a NullHandler.  Users of this class may configure
    the logger to aid in diagnosing problems.

    This class is dependent upon xml.etree.ElementTree module which is
    vulnerable to an "exponential entity expansion" and "quadratic blowup
    entity expansion" XML attack.  However, this class only receives XML
    from the (trusted) HDP server so these attacks are not a threat.  See
    the xml.etree.ElementTree "XML vulnerabilities" documentation for
    more details
    <https://docs.python.org/3/library/xml.html#xml-vulnerabilities>.
    """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(
            self,
            endpoint=None,
            timeout=None,
            proxy=None,
            ca_certs=None,
            disable_ssl_certificate_validation=False,
            user_agent=None):

        self.logger = logging.getLogger(type(self).__name__)
        self.logger.addHandler(logging.NullHandler())

        self.retry_after_time = None

        self.logger.debug('endpoint = %s', endpoint)
        self.logger.debug('ca_certs = %s', ca_certs)
        self.logger.debug('disable_ssl_certificate_validation = %s',
                          disable_ssl_certificate_validation)

        if endpoint is None:
            self._endpoint = 'https://heliophysicsdata.gsfc.nasa.gov/WS/hdp/1/'
        else:
            self._endpoint = endpoint

        self._user_agent = 'hdpws/' + __version__ + ' (' + \
            platform.python_implementation() + ' ' \
            + platform.python_version() + '; '+ platform.platform() + ')'

        if user_agent is not None:
            self._user_agent += ' (' + user_agent + ')'

        self._request_headers = {
            'Content-Type' : 'application/xml',
            'Accept' : 'application/xml',
            'User-Agent' : self._user_agent
        }
        self._session = requests.Session()
        #self._session.max_redirects = 0
        self._session.headers.update(self._request_headers)

        if ca_certs is not None:
            self._session.verify = ca_certs

        if disable_ssl_certificate_validation is True:
            self._session.verify = False

        if proxy is not None:
            self._proxy = proxy

        self._timeout = timeout

    # pylint: enable=too-many-arguments


    def __str__(self) -> str:
        """
        Produces a string representation of this object.

        Returns
        -------
        str
            A string representation of this object.
        """
        return 'HdpWs(endpoint=' + self._endpoint + ', timeout=' + \
               str(self._timeout) + ')'


    def __del__(self):
        """
        Destructor.  Closes all network connections.
        """

        self.close()


    def close(self) -> None:
        """
        Closes any persistent network connections.  Generally, deleting
        this object is sufficient and calling this method is unnecessary.
        """
        self._session.close()


    @property
    def endpoint(self) -> str:
        """
        Gets the endpoint value.

        Returns
        -------
        str
            endpoint value.
        """
        return self._endpoint


    def get_application_interfaces(
            self
        ) -> Dict:
        """
        Gets all /Spase/Software/ApplicationInterface values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'ApplicationInterface' key with a value
            of a List containing all /Spase/Software/ApplicationInterface values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/ApplicationInterface',
                                          'ApplicationInterface', 
                                          'ApplicationInterface')

    def get_keywords(
            self
        ) -> Dict:
        """
        Gets all //Keyword values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'Keyword' key with a value
            of a List containing all /Keyword values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Keyword',
                                          'Keyword', 
                                          'Keyword')


    def get_instrument_ids(
            self
        ) -> Dict:
        """
        Gets all /Spase/Instrument/ResourceID values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'InstrumentID' key with a value
            of a List containing all /Spase/Instrument/ResourceID values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Instrument/ResourceID',
                                          'ResourceID', 
                                          'InstrumentID')


    def get_repository_ids(
            self
        ) -> Dict:
        """
        Gets all /Spase/Repository/ResourceID values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'RespositoryID' key with a value
            of a List containing all /Spase/Respository/ResourceID values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Repository/ResourceID',
                                          'ResourceID', 
                                          'RepositoryID')


    def get_styles(
            self
        ) -> Dict:
        """
        Gets all /Spase/Style values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'Style' key with a value
            of a List containing all /Spase/Style values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Style',
                                          'Style', 
                                          'Style')


    def get_measurement_types(
            self
        ) -> Dict:
        """
        Gets all /Spase/MeasurementType values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'MeasurementType' key with a value
            of a List containing all /Spase/MeasurementType values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/MeasurementType',
                                          'MeasurementType', 
                                          'MeasurementType')


    def get_spectral_ranges(
            self
        ) -> Dict:
        """
        Gets all /Spase/SpectralRange values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'SpectralRange' key with a value
            of a List containing all /Spase/SpectralRange values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/SpectralRange',
                                          'SpectralRange', 'SpectralRange')


    def get_phenomenon_types(
            self
        ) -> Dict:
        """
        Gets all /Spase/PhenomenonType values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'PhenomenonType' key with a value
            of a List containing all /Spase/PhenomenonType values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/PhenomenonType',
                                          'PhenomenonType', 
                                          'PhenomenonType')


    def get_observatory_group_ids(
            self
        ) -> Dict:
        """
        Gets all /Spase/Observatory/ObservatoryGroupID values available
        at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'ObservatoryGroupID' key with a value
            of a List containing all /Spase/Observed/ObservatoryGroupID
            values with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Observatory/ObservatoryGroupID',
                                          'ObservatoryGroupID', 'ObservatoryGroupID')


    def get_observatory_ids(
            self
        ) -> Dict:
        """
        Gets all /Spase/Observatory/ResourceID values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'ObservatoryID' key with a value
            of a List containing all /Spase/Observatory/ResourceID values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/Observatory/ResourceID',
                                          'ResourceID', 'ObservatoryID')


    def get_observed_regions(
            self
        ) -> Dict:
        """
        Gets all /Spase/ObservedRegion values available at HDP.

        Returns
        -------
        Dict
            Dictionary containing a 'ObservedRegion' key with a value
            of a List containing all /Spase/ObservedRegion values
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_simple_resource('Spase/ObservedRegion',
                                          'Region', 'ObservedRegion')


    def get_spase(
            self,
            resource_ids: List[str],
            **keywords: Union[
                datetime]
        ) -> Dict:
        """
        Gets the specified SPASE documents from HDP.

        Parameters
        ----------
        resource_ids
            List of SPASE ResourceID values of the documents to get.
        keywords
            Optional keyword paramaters as follows:<br>
            <b>if_modified_since</b> - conditional GET If-Modified-Since
            datetime value.<br>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            - Last-Modified: the value of the HTTP Last-Modified header
              when available.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        url = self._endpoint + 'Spase'

        headers = {}

        if_modified_since = keywords.get('if_modified_since', None)
        if if_modified_since is not None:
            headers = {
                'If-Modified-Since': \
                    if_modified_since.strftime(IF_MODIFIED_SINCE_FORMAT)
            }
        query = {
            'ResourceID': resource_ids
        }
        response = self._session.get(url, params=query, headers=headers,
                                     timeout=self._timeout)

        self.logger.debug('response.url = %s', response.url)

        status = self.__get_status(response)
        if response.status_code != 200:
            return status

        result = {
            'Result': ET.fromstring(response.text)
        }

        result.update(status)
        return result


    def get_spase_url(
            self,
            resource_id: str
        ) -> str:
        """
        Gets the URL of the specified SPASE document from HDP.

        Parameters
        ----------
        resource_id
            SPASE ResourceID value of the document to get.

        Returns
        -------
        str
            URL of the specified SPASE document.
        """
        return self.endpoint + 'Spase?ResourceID=' + resource_id


    def get_spase_html(
            self,
            resource_id: str,
            **keywords: Union[
                datetime]
        ) -> Dict:
        """
        Gets the an HTML representation of the specified SPASE document 
        from HDP.

        Parameters
        ----------
        resource_id
            SPASE ResourceID value of the document to get.
        keywords
            Optional keyword paramaters as follows:<br>
            <b>if_modified_since</b> - conditional GET If-Modified-Since
            datetime value.<br>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key whose value is an HTML
            representation of the specified SPASE document with the
            addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            - Last-Modified: the value of the HTTP Last-Modified header
              when available.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        url = self.endpoint + 'Spase'

        headers = {
            'Accept': 'text/html'
        }

        if_modified_since = keywords.get('if_modified_since', None)
        if if_modified_since is not None:
            headers['If-Modified-Since'] = \
                if_modified_since.strftime(IF_MODIFIED_SINCE_FORMAT)

        query = {
            'ResourceID': resource_id
        }
        response = self._session.get(url, params=query, headers=headers,
                                     timeout=self._timeout)

        self.logger.debug('response.url = %s', response.url)

        status = self.__get_status(response)
        if response.status_code != 200:
            return status

        result = {
            'Result': response.text
        }

        result.update(status)
        return result


    def get_spase_json_ld(
            self,
            resource_id: str,
            **keywords: Union[
                datetime]
        ) -> Dict:
        """
        Gets the an JSON-LD representation of the specified SPASE document 
        from HDP.

        Parameters
        ----------
        resource_id
            SPASE ResourceID value of the document to get.
        keywords
            Optional keyword paramaters as follows:<br>
            <b>if_modified_since</b> - conditional GET If-Modified-Since
            datetime value.<br>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key whose value is the JSON-LD
            representation of the specified SPASE document with the
            addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            - Last-Modified: the value of the HTTP Last-Modified header
              when available.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """

        response = self.get_spase_html(resource_id, **keywords)

        if response['HttpStatus'] != 200:
            return response

        spase_html_parser = SpaseHtmlParser()
        spase_html_parser.feed(response['Result'])

        response['Result'] = spase_html_parser.get_json_ld()

        return response


    def get_spase_data(
            self,
            resource_types: List[ResourceType],
            query: Dict,
            date_range: Union[List[str], DateInterval] = None,
            **keywords: Union[
                datetime]
        ) -> Dict:
        """
        Gets the specified SPASE "data" documents from HDP.

        Parameters
        ----------
        resource_types
            List of SPASE ResourceTypes to get.  ResourceType.NUMERICAL_DATA
            , ResourceType.DISPLAY_DATA, or both.
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'InstrumentID': 'spase://SMWG/Instrument/ACE/CRIS',
                'Cadence': '=PT1H',
                'ObservedRegion': 'Heliosphere.NearEarth',
                'MeasurementType': 'EnergeticParticles',
                'AccessRights': 'Open',
                'Format': 'CDF'
            }</pre>
        date_range
            A DateInterval or two element array of ISO 8601 string
            values of the start and stop date of the requested resources.
            for example,<pre>
            date_range = ['2022-01-01', '2022-01-02']
            </pre>
        keywords
            Optional keyword paramaters as follows:<br>
            <b>if_modified_since</b> - conditional GET If-Modified-Since
            datetime value.<br>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            - Last-Modified: the value of the HTTP Last-Modified header
              when available.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource(resource_types, query,
                                           date_range, **keywords)


    def get_spase_catalog(
            self,
            query: Dict,
            date_range: Union[List[str], DateInterval] = None
        ) -> Dict:
        """
        Gets the specified SPASE Catalog documents from HDP.

        Parameters
        ----------
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'InstrumentID': 'spase://SMWG/Instrument/ACE/MAG',
                'PhenomenonType': 'MagneticCloud',
                'Description': 'ICME'
            }</pre>
        date_range
            A DateInterval or two element array of ISO 8601 string
            values of the start and stop date of the requested resources.
            for example,<pre>
            date_range = ['1999-01-01', '1999-01-02']
            </pre>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource([ResourceType.CATALOG], query,
                                           date_range)


    def get_spase_collection(
            self,
            query: Dict
        ) -> Dict:
        """
        Gets the specified SPASE Collection documents from HDP.

        Parameters
        ----------
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'ResourceID': 'spase://NASA/Collection/IRIS_AIA',
                'MemberID': 'spase://NASA/NumericalData/SDO/AIA/PT10S',
                'Description': 'IRIS AND SDO and AIA'
            }</pre>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource([ResourceType.COLLECTION], query)


    def get_spase_document(
            self,
            query: Dict
        ) -> Dict:
        """
        Gets the specified SPASE Document documents from HDP.

        Parameters
        ----------
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'ResourceID': 'spase://SMWG/Document/HPDE/Policy/HP_DataPolicy_v1.2',
                'DOI': '10.21978/P83P78',
                'Description': '"Program Data Management Plan"'
            }</pre>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource([ResourceType.DOCUMENT], query)


    def get_spase_service(
            self,
            query: Dict
        ) -> Dict:
        """
        Gets the specified SPASE Service documents from HDP.

        Parameters
        ----------
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'ResourceID': 'spase://CCMC/Service/InstantRun',
                'Description': '"Instan-Run"'
            }</pre>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource([ResourceType.SERVICE], query)


    def get_spase_software(
            self,
            query: Dict
        ) -> Dict:
        """
        Gets the specified SPASE Software documents from HDP.

        Parameters
        ----------
        query
            Dictionary containing query parameters and values.  For
            example,<pre>
            query = { 
                'ResourceID': 'spase://CCMC/Software/Kamodo',
                'CodeLanguage': 'Python',
                'Description': '"space weather models and data"'
            }</pre>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        return self.__get_complex_resource([ResourceType.SOFTWARE], query)


    def __get_simple_resource(
            self,
            resource: str,
            name: str,
            result_name: str
        ) -> Dict:
        """
        Gets all simple resource values available at HDP.

        Parameters
        ----------
        resource
            Resource path.  For example, Spase/ObservedRegion.
        name
            Element name to get from response.  For example, Region.
        result_name
            Name of key to return result in.  For example, 
            ObservedRegion.

        Returns
        -------
        Dict
            Dictionary containing a key with the given result_name and
            a value equal to a List of the given name element values from
            the response
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        url = self._endpoint + resource

        self.logger.debug('request url = %s', url)

        response = self._session.get(url, timeout=self._timeout)

        status = self.__get_status(response)
        if response.status_code != 200:
            return status

        mt_response = ET.fromstring(response.text)

        result = {
            result_name: []
        }

        for value in mt_response.findall('.//hdp:' + name,
                                         namespaces=NS):

            result[result_name].append(value.text)

        result.update(status)
        return result


    def __get_complex_resource(
            self,
            resource_types: List[ResourceType],
            query: Dict,
            date_range: Union[List[str], DateInterval] = None,
            **keywords: Union[
                datetime]
        ) -> Dict:
        """
        Gets the specified SPASE documents from HDP.

        Parameters
        ----------
        resource_types
            List of SPASE ResourceTypes to get.
        query
            Dictionary containing query parameters and values.
        date_range
            A DateInterval or two element array of ISO 8601 string
            values of the start and stop date of the requested resources.
            for example,<pre>
            date_range = ['2022-01-01', '2022-01-02']
            </pre>
        keywords
            Optional keyword paramaters as follows:<br>
            <b>if_modified_since</b> - conditional GET If-Modified-Since
            datetime value.<br>

        Returns
        -------
        Dict
            Dictionary containing a 'Result' key with a value of an
            ElementTree representation of the results as described by
            <https://heliophysicsdata.gsfc.nasa.gov/WebServices/hdpspase.xsd>
            with the addition of the following key/values:<br>
            - HttpStatus: with the value of the HTTP status code.
              Successful == 200.<br>
            - Last-Modified: the value of the HTTP Last-Modified header
              when available.<br>
            When HttpStatus != 200:<br>
            - HttpText: containing a string representation of the HTTP
              entity body.<br>
            When HttpText is a standard HDP WS error entity body the
            following key/values (convenience to avoid parsing
            HttpStatus):<br>
            - ErrorMessage: value from HttpText.<br>
            - ErrorDescription: value from HttpText.<br>
        """
        resource_path = ';'.join(type.value for type in resource_types)
        url = self._endpoint + 'Spase/' + resource_path

        if date_range is not None:

            if isinstance(date_range, list):
                date_interval = DateInterval(date_range[0], date_range[1])
            else:
                date_interval = date_range

            url += '/' + str(date_interval)

        headers = {}

        if_modified_since = keywords.get('if_modified_since', None)
        if if_modified_since is not None:
            headers = {
                'If-Modified-Since': \
                    if_modified_since.strftime(IF_MODIFIED_SINCE_FORMAT)
            }

        response = self._session.get(url, params=query, headers=headers,
                                     timeout=self._timeout)

        self.logger.debug('response.url = %s', response.url)

        status = self.__get_status(response)
        if response.status_code != 200:
            return status

        result = {
            'Result': ET.fromstring(response.text)
        }

        result.update(status)
        return result


    @staticmethod
    def __get_status(
            response: requests.Response
        ) -> Dict:
        """
        Gets status and header information from the given response.  In 
        particular, when status_code != 200, an attempt is made to 
        extract the HDP WS ErrorMessage and ErrorDescription from the 
        response.

        Parameters
        ----------
        response
            requests Response object.

        Returns
        -------
        Dict
            Dict containing the following:<br>
            - HttpStatus: the HTTP status code<br>
            - Last-Modified: the HTTP Last-Modified header value when 
              available<br>
            additionally, when HttpStatus != 200<br>
            - ErrorText: a string representation of the entire entity
              body<br>
            - ErrorMessage: HDP WS ErrorMessage (when available)<br>
            - ErrorDescription: HDP WS ErrorDescription (when available)
        """
        http_result = {
            'HttpStatus': response.status_code
        }

        if 'Last-Modified' in response.headers:
            http_result['Last-Modified'] = \
                parser.parse(response.headers['Last-Modified'])

        if response.status_code != 200:

            http_result['ErrorText'] = response.text
            try:
                error_element = ET.fromstring(response.text)
                http_result['ErrorMessage'] = error_element.findall(\
                    './/xhtml:p[@class="ErrorMessage"]/xhtml:b',
                    namespaces=NS)[0].tail
                http_result['ErrorDescription'] = error_element.findall(\
                    './/xhtml:p[@class="ErrorDescription"]/xhtml:b',
                    namespaces=NS)[0].tail
            except ParseError:
                pass  # ErrorText is the best we can do

        return http_result
