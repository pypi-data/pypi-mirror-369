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
# Copyright (c) 2025 United States Government as represented by
# the National Aeronautics and Space Administration. No copyright is
# claimed in the United States under Title 17, U.S.Code. All Other
# Rights Reserved.
#


"""
Module defining a class to represent a SPASE HTML parser.  At present,
its main function is to extract the JSON-LD embedded in an HTML
representation of a SPASE XML document.  Any other information should
be obtained from the original SPASE XML document.<br>

Copyright &copy; 2025 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""


from html.parser import HTMLParser



class SpaseHtmlParser(HTMLParser):
    """
    A class representing a SPASE HTML parser.

    Parameters
    ----------
    json_ld_element
        Flag indicating that we have encountered the json-ld element.
        The value is set back to false when we encounter the end tag.
    json_ld
        The json-ld "data" extracted from the json-ld element.
    """
    def __init__(self):

        super().__init__()

        self._json_ld_element = False
        self._json_ld = None


    def handle_starttag(self, tag, attrs):
        """
        This method is called to handle the start tag of an element.

        Parameters
        ----------
        tag
            The name of the tag encountered.
        attrs
            List of (name, value) pairs containing the attributes found
            inside the tag’s &lt;&gt; brackets. 
        """

        if tag == 'script':
            for attr in attrs:
                if attr[0] == 'type' and attr[1] == 'application/ld+json':
                    self._json_ld_element = True


    def handle_endtag(self, tag):
        """
        This method is called to handle the end tag of an element.

        Parameters
        ----------
        tag
            The name of the tag encountered.
        """

        self._json_ld_element = False


    def handle_data(self, data):
        """
        This method is called to process arbitrary data (e.g. text nodes
        and the content of &lt;script&gt;...&lt;/script&gt; and 
        &lt;style&gt;...&lt;/style&gt;).

        Parameters
        ----------
        data
            The content of the element.
        """

        if self._json_ld_element:

            self._json_ld = data


    def get_json_ld(self) -> str:
        """
        Gets the JSON-LD from the SPASE HTML fed to this parser.

        Returns:
        --------
        str
            JSON-LD from the SPASE HTML or None.
        """

        return self._json_ld
