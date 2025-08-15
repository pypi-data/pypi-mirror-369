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
Package for accessing the NASA's Heliophysics Data Portal (HDP) web
services https://heliophysicsdata.gsfc.nasa.gov/WebServices/.

Copyright &copy; 2023-2025 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.

"""


__version__ = "0.6.26"


#
# Limit on the number of times an HTTP request which returns a
# 429 or 503 status with a Retry-After header will be retried.
#
#RETRY_LIMIT = 100


#
# XML schema namespace
#
HDP_NS = 'http://heliophysicsdata.gsfc.nasa.gov/hdp'
#
# SPASE schema namespace
#
SPASE_NS = 'http://www.spase-group.org/data/schema'
#
# XHTML schema namespace
#
XHTML_NS = 'http://www.w3.org/1999/xhtml'
#
# All namespaces found in responses with spase being the default.
#
NAMESPACES = {
    'hdp': HDP_NS,
    '': SPASE_NS,
    'xhtml': XHTML_NS
}
