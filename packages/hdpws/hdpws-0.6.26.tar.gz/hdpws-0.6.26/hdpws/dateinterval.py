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
Module defining a class to represent date interval.<br>

Copyright &copy; 2023 United States Government as represented by the
National Aeronautics and Space Administration. No copyright is claimed in
the United States under Title 17, U.S.Code. All Other Rights Reserved.
"""


from datetime import date
from typing import Tuple, Union



class DateInterval:
    """
    A class representing a date interval.

    Parameters
    ----------
    start
        Start date of interval.
    end
        End date of interval.

    Raises
    ------
    ValueError
        If the given start/end datedate values are invalid.
    """
    def __init__(self,
                 start: Union[date, str],
                 end: Union[date, str]):

        self._start = DateInterval.get_date(start)
        self._end = DateInterval.get_date(end)


    @property
    def start(self) -> date:
        """
        Gets the start value.

        Returns
        -------
        date
            start value.
        """
        return self._start


    @start.setter
    def start(self, value: Union[date, str]):
        """
        Sets the start value.

        Parameters
        ----------
        value
            start date value.
        """
        self._start = DateInterval.get_date(value)


    @property
    def end(self) -> date:
        """
        Gets the end value.

        Returns
        -------
        date
            end value.
        """
        return self._end


    @end.setter
    def end(self, value: Union[date, str]):
        """
        Sets the _end value.

        Parameters
        ----------
        value
            end date value.
        """
        self._end = DateInterval.get_date(value)


    def __str__(self):
        return self._start.isoformat() + ',' + self._end.isoformat()


    def __eq__(self, other):
        return self._start == other.start and self._end == other.end



    @staticmethod
    def get_date(value: Union[date, str]) -> date:
        """
        Produces a date representation of the given value. 

        Parameters
        ----------
        value
            value to convert to a date.
        Returns
        -------
        date
            date representation of the given value.
        Raises
        ------
        ValueError
            If the given value is not a valid datetime.date value.
        """
        if isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            date_value = date.fromisoformat(value)
        else:
            raise ValueError('unrecognized datetime.date value')

        return date_value


    @staticmethod
    def get_dates(
            start: Union[date, str],
            end: Union[date, str]
        ) -> Tuple[date, date]:
        """
        Produces a date representation of the given values.

        Parameters
        ----------
        start
            start value to convert to a date.
        end
            end value to convert to a date.
        Returns
        -------
        Tuple
            [0] date representation of the given start value.
            [1] date representation of the given end value.
        Raises
        ------
        ValueError
            If either of the given values is not a valid date value.
        """
        try:
            start_date = DateInterval.get_date(start)
        except ValueError as invalid_start_date:
            raise ValueError('unrecognized start date value')\
            from invalid_start_date

        try:
            end_date = DateInterval.get_date(end)
        except ValueError as invalid_end_date:
            raise ValueError('unrecognized end date value')\
            from invalid_end_date

        return start_date, end_date
