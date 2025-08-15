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
Module for unittest of the DateInterval class.<br>

Copyright &copy; 2023 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""

import unittest
from datetime import date

from context import hdpws  # pylint: disable=unused-import

from hdpws.dateinterval import DateInterval  # pylint: disable=import-error



class TestDateInterval(unittest.TestCase):
    """
    Class for unittest of DateInterval class.
    """

    def __init__(self, *args, **kwargs):
        super(TestDateInterval, self).__init__(*args, **kwargs)


    def test_get_date_exceptions(self):
        """
        Test for get_date function exceptions.
        """

        with self.assertRaises(ValueError):
            DateInterval.get_date(123)

        with self.assertRaises(ValueError):
            DateInterval.get_date('bad_date')


    def test_get_dates_exceptions(self):
        """
        Test for get_date function.
        """

        with self.assertRaises(ValueError):
            DateInterval.get_dates('2020-01-01', 123)

        with self.assertRaises(ValueError):
            DateInterval.get_dates('2020-01-01', 'bad_date')


    def test_date_interval_init(self):
        """
        Test for DateInterval constructor.
        """

        self.assertEqual(DateInterval.get_date('2023-01-01'),
                         date(2023, 1, 1))


    def test_date_interval_eq(self):
        """
        Test for DateInterval equality operator.
        """

        t_1 = DateInterval('2023-01-01', '2023-01-02')
        t_2 = DateInterval(date(2023, 1, 1),
                           date(2023, 1, 2))

        self.assertEqual(t_1, t_2)


    def test_date_interval_str(self):
        """
        Test DateInterval.str().
        """

        t_1 = DateInterval(date(2023, 1, 1),
                           date(2023, 1, 2))

        self.assertEqual(str(t_1),
                         '2023-01-01,2023-01-02')


    def test_date_interval_properties(self):
        """
        Test DateInterval properties.
        """

        t_1 = DateInterval(date(2023, 1, 1),
                           date(2023, 1, 2))

        t_1.start = date(2020, 1, 1)
        t_1.end = date(2020, 1, 2)

        self.assertEqual(t_1.start, date(2020, 1, 1))
        self.assertEqual(t_1.end, date(2020, 1, 2))


if __name__ == '__main__':
    unittest.main()
