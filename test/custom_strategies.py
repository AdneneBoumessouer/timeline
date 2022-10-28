#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:40:39 2021

@author: aboumessouer
"""

import datetime
import pandas as pd
from hypothesis import strategies as st
from .utils import truncate, truncate_timedelta


class CustomStrategies:
    """
    This class implements custom property based testing strategies
    using the Hypothesis framework that generate data matching some
    specification for unittests.

    For an example, run: dtr_as_tuple().example()

    Literature:
        https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.builds

    """

    @staticmethod
    def dtr_as_tuple():
        """
        Returns Hypothesis strategy for generating valid time intervals
        as tuples composed of start and end datetimes.
        """
        start_datetime_min = datetime.datetime(
            year=2021, month=3, day=1, hour=8, minute=0)
        end_datetime_min = datetime.datetime(
            year=2021, month=3, day=1, hour=8, minute=0)  # minute=1
        datetime_max = datetime.datetime(
            year=2021, month=3, day=2, hour=12, minute=0)
        assert datetime_max > start_datetime_min
        assert datetime_max > end_datetime_min
        # instantiate and return strategy
        st_start_datetime = st.datetimes(
            min_value=start_datetime_min, max_value=datetime_max, allow_imaginary=False).map(truncate)
        st_end_datetime = st.datetimes(
            min_value=end_datetime_min, max_value=datetime_max, allow_imaginary=False).map(truncate)
        return st.tuples(st_start_datetime, st_end_datetime).filter(lambda x: x[0] < x[1])

    @staticmethod
    @st.composite
    def dtr_tp(draw):
        """
        Returns Hypothesis strategy for generating valid time intervals
        as tuples composed of start and end datetimes.
        """
        # generate start_datetime
        vmin_datetime = datetime.datetime(
            year=2021, month=3, day=1, hour=8, minute=0, second=0)
        vmax_datetime = datetime.datetime(
            year=2021, month=8, day=1, hour=8, minute=0, second=0)
        st_start_datetime = st.datetimes(
            min_value=vmin_datetime, max_value=vmax_datetime, allow_imaginary=False).map(truncate)
        start_datetime = draw(st_start_datetime)
        # generate a timedelta
        vmin_timedelta = pd.Timedelta(value=1, unit="seconds")
        vmax_timedelta = pd.Timedelta(value=24, unit="hours")
        st_timedelta = st.timedeltas(
            min_value=vmin_timedelta, max_value=vmax_timedelta).map(truncate_timedelta)
        timedelta = draw(st_timedelta)
        # generate end_datetime
        end_datetime = start_datetime + timedelta
        return (start_datetime, end_datetime)

    @ staticmethod
    def list_timedeltas():
        vmin = pd.Timedelta(value=0, unit="seconds")
        vmax = pd.Timedelta(value=28, unit="hours")
        return st.lists(st.timedeltas(min_value=vmin, max_value=vmax).map(truncate_timedelta),
                        min_size=1, max_size=10)


# CustomStrategies.dtr_as_tuple().example()
# CustomStrategies.dtr_tp().example()

# datetime.timedelta(days=1, seconds=1, microseconds=5, milliseconds=500, minutes=1, hours=1, weeks=1)
# st.integers().example()

# st_start_datetime = st.datetimes(allow_imaginary=False)
# st_start_datetime.example()

# st_timedelta = st.builds(datetime.timedelta, minutes=st.integers(min_value=0))
# st_timedelta.example()

# st_start_datetime.example() + st_timedelta.example()

# st_end_datetime = st.builds(add, st_start_datetime, st_timedelta)
# st_end_datetime.example()
