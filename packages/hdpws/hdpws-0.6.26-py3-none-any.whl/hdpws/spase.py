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
Module defines classes representing the Space Physics Archive Search and
Extract (SPASE) <https://spase-group.org/> 
data model <https://spase-group.org/data/index.html>.<br>

Copyright &copy; 2023 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.

Notes
-----
<ul>
  <li>At this time, this module is limited and does not attempt
      to represent the entire SPASE data model.</li>
  <li>If this module is extented to more completely represent the
      SPASE data model, it should probably be a separate project.</li>
</ul>
"""

import xml.etree.ElementTree as ET
from typing import List

from hdpws import SPASE_NS
from hdpws import NAMESPACES as NS



class AccessURL:
    """
    A class representing a /Spase//AccessURL element.

    Parameters
    ----------
    element_tree
        A /Spase//AccessURL element tree.

    Raises
    ------
    ValueError
        If the given element_tree is not a /Spase//AccessURL element tree.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 element_tree: ET):

        access_url = element_tree.find('.', namespaces=NS)
        if access_url is None or \
           access_url.tag != '{' + SPASE_NS + '}AccessURL':
            raise ValueError('the given element is not an AccessURL')

        name = access_url.find('Name', namespaces=NS)
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        url = access_url.find('URL', namespaces=NS)
        if url is not None:
            self.url = url.text
        else:
            self.url = None
        style = access_url.find('Style', namespaces=NS)
        if style is not None:
            self.style = style.text

        self.product_key = []
        for product_key in access_url.findall('ProductKey', namespaces=NS):
            self.product_key.append(product_key.text)

        description = access_url.find('Description', namespaces=NS)
        if description is not None:
            self.description = description.text
        else:
            self.description = None

        language = access_url.find('Language', namespaces=NS)
        if language is not None:
            self.language = language.text
        else:
            self.language = None


    @property
    def name(self) -> str:
        """
        Gets the name value.

        Returns
        -------
        str
            name value.
        """
        return self._name


    @name.setter
    def name(self, value: str):
        """
        Sets the name value.

        Parameters
        ----------
        value
            name value.
        """
        self._name = value


    @property
    def url(self) -> str:
        """
        Gets the url value.

        Returns
        -------
        str
            url value.
        """
        return self._url


    @url.setter
    def url(self, value: str):
        """
        Sets the url value.

        Parameters
        ----------
        value
            url value.
        """
        self._url = value


    @property
    def style(self) -> str:
        """
        Gets the style value.

        Returns
        -------
        str
            style value.
        """
        return self._style


    @style.setter
    def style(self, value: str):
        """
        Sets the style value.

        Parameters
        ----------
        value
            style value.
        """
        self._style = value


    @property
    def product_key(self) -> str:
        """
        Gets the product_key value.

        Returns
        -------
        str
            product_key value.
        """
        return self._product_key


    @product_key.setter
    def product_key(self, value: str):
        """
        Sets the product_key value.

        Parameters
        ----------
        value
            product_key value.
        """
        self._product_key = value


    @property
    def description(self) -> str:
        """
        Gets the description value.

        Returns
        -------
        str
            description value.
        """
        return self._description


    @description.setter
    def description(self, value: str):
        """
        Sets the description value.

        Parameters
        ----------
        value
            description value.
        """
        self._description = value


    @property
    def language(self) -> str:
        """
        Gets the language value.

        Returns
        -------
        str
            language value.
        """
        return self._language


    @language.setter
    def language(self, value: str):
        """
        Sets the language value.

        Parameters
        ----------
        value
            language value.
        """
        self._language = value


#
# URL of a page to display HAPI information
#
HAPI_DISPLAY_URL = 'https://cdaweb.gsfc.nasa.gov/registry/hdp/hapi/hapiHtml.html'

class HapiAccessURL(AccessURL):
    """
    A HAPI specialization of a AccessURL class.

    Parameters
    ----------
    element_tree
        A /Spase//AccessURL[Style = 'HAPI'] element tree.

    Raises
    ------
    ValueError
        If the given element_tree is not a /Spase//AccessURL[Style = 'HAPI']
        element tree.
    """
    def __init__(self,
                 element_tree: ET):

        super().__init__(element_tree)

        if self.style != 'HAPI':
            raise ValueError('the given element is not a HAPI AccessURL')


    def get_html_url(self) -> str:
        """
        Gets a URL that produces an HTML representation of the HAPI this
        AccessURL.

        Returns
        -------
        str
            a URL that produces an HTML representation of the HAPI this
            AccessURL.
        """
        url = HAPI_DISPLAY_URL + '#url=' + self.url + '&id='

        for product_key in self.product_key:
            url += product_key + ','

        return url[:-1]



class AccessInformation:
    """
    A class representing a /Spase//AccessInformation element.

    Parameters
    ----------
    element_tree
        A /Spase//AccessInformation element tree.

    Raises
    ------
    ValueError
        If the given element_tree is not a /Spase//AccessInformation 
            element tree.
    """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-branches
    def __init__(self,
                 element_tree: ET):

        access_info = element_tree.find('.',
                                        namespaces=NS)
        if access_info is None or \
           access_info.tag != '{' + SPASE_NS + '}AccessInformation':
            raise ValueError('the given element is not an AccessInformation')

        repository_id = access_info.find('RepositoryID', namespaces=NS)
        if repository_id is not None:
            self.repository_id = repository_id.text
        else:
            self.repository_id = None

        availability = access_info.find('Availability', namespaces=NS)
        if availability is not None:
            self.availability = availability.text
        else:
            self.availability = None

        access_rights = access_info.find('AccessRights', namespaces=NS)
        if access_rights is not None:
            self.access_rights = access_rights.text
        else:
            self.access_rights = None

        self.access_url = []
        for access_url in access_info.findall('AccessURL', namespaces=NS):
            self.access_url.append(AccessURL(access_url))

        self.format = []
        for format_element in access_info.findall('Format', namespaces=NS):
            self.format.append(format_element.text)

        encoding = access_info.find('Encoding', namespaces=NS)
        if encoding is not None:
            self.encoding = encoding.text
        else:
            self.encoding = None

        data_extent = access_info.find('DataExtent', namespaces=NS)
        if data_extent is not None:
            self.data_extent = data_extent.text
        else:
            self.data_extent = None

        acknowledgement = access_info.find('Acknowledgement', namespaces=NS)
        if acknowledgement is not None:
            self.acknowledgement = acknowledgement.text
        else:
            self.acknowledgement = None


    @property
    def repository_id(self) -> str:
        """
        Gets the RepositoryID value.

        Returns
        -------
        str
            repository_id value.
        """
        return self._repository_id


    @repository_id.setter
    def repository_id(self, value: str):
        """
        Sets the repository_id value.

        Parameters
        ----------
        value
            repository_id value.
        """
        self._repository_id = value


    @property
    def availability(self) -> str:
        """
        Gets the availability value.

        Returns
        -------
        str
            availability value.
        """
        return self._availability


    @availability.setter
    def availability(self, value: str):
        """
        Sets the availability value.

        Parameters
        ----------
        value
            availability value.
        """
        self._availability = value


    @property
    def access_rights(self) -> str:
        """
        Gets the access_rights value.

        Returns
        -------
        date
            access_rights value.
        """
        return self._access_rights


    @access_rights.setter
    def access_rights(self, value: str):
        """
        Sets the access_rights value.

        Parameters
        ----------
        value
            access_rights value.
        """
        self._access_rights = value


    @property
    def access_url(self) -> List[AccessURL]:
        """
        Gets the access_url values.

        Returns
        -------
        List
            access_url values.
        """
        return self._access_url


    @access_url.setter
    def access_url(self, values: List[AccessURL]):
        """
        Sets the access_url values.

        Parameters
        ----------
        values
            access_url values.
        """
        self._access_url = values


    @property
    def format(self) -> List[str]:
        """
        Gets the format value.

        Returns
        -------
        List
            format values.
        """
        return self._format


    @format.setter
    def format(self, values: List[str]):
        """
        Sets the format values.

        Parameters
        ----------
        values
            format value.
        """
        self._format = values


    @property
    def encoding(self) -> str:
        """
        Gets the encoding value.

        Returns
        -------
        date
            encoding value.
        """
        return self._encoding


    @encoding.setter
    def encoding(self, value: str):
        """
        Sets the encoding value.

        Parameters
        ----------
        value
            encoding value.
        """
        self._encoding = value


    @property
    def data_extent(self) -> str:
        """
        Gets the data_extent value.

        Returns
        -------
        str
            data_extent value.
        """
        return self._data_extent


    @data_extent.setter
    def data_extent(self, value: str):
        """
        Sets the data_extent value.

        Parameters
        ----------
        value
            data_extent value.
        """
        self._data_extent = value


    @property
    def acknowledgement(self) -> str:
        """
        Gets the acknowledgement value.

        Returns
        -------
        str
            acknowledgement value.
        """
        return self._acknowledgement


    @acknowledgement.setter
    def acknowledgement(self, value: str):
        """
        Sets the acknowledgement value.

        Parameters
        ----------
        value
            acknowledgement value.
        """
        self._acknowledgement = value
