#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 11:46:25 2021

@author: aboumessouer

"""

from __future__ import annotations
from typing import List
import pandas as pd
from datetimerange import DateTimeRange


class TimeRange(DateTimeRange):
    def __init__(self, start: str, end: str, format: str = '%d.%m.%Y %H:%M'):
        self.start = start
        self.end = end
        self.format = format
        start_datetime = pd.to_datetime(start, format=format)
        end_datetime = pd.to_datetime(end, format=format)
        super().__init__(start_datetime, end_datetime, format, format)
        if self.is_set():
            if self.start_datetime > self.end_datetime:
                raise ValueError(
                    "time inversion found: {:s} > {:s}".format(
                        str(self.start_datetime), str(self.end_datetime)
                    )
                )

    def convert(self, x: DateTimeRange | List[DateTimeRange]) -> TimeRange | List[TimeRange]:
        """Converts a (list of) DateTimeRange object(s) to (a list of) DTR object(s)"""
        if isinstance(x, list):
            converted = []
            for elem in x:
                converted.append(TimeRange(start=elem.start_datetime,
                                           end=elem.end_datetime, format=self.format))
            return converted
        return TimeRange(start=x.start_datetime, end=x.end_datetime, format=self.format)

    @DateTimeRange.timedelta.getter
    def timedelta(self):
        if not self.is_valid_timerange():
            return pd.Timedelta(value=0)
        return self.end_datetime - self.start_datetime

    def intersection(self, x: TimeRange) -> TimeRange:
        """Wrapper for intersection method from parent class DateTimeRange."""
        return self.convert(super(TimeRange, self).intersection(x))

    def encompass(self, x: TimeRange) -> TimeRange:
        """Wrapper for encompass method from parent class DateTimeRange."""
        return self.convert(super(TimeRange, self).encompass(x))

    def subtract(self, x: TimeRange) -> TimeRange | List[TimeRange]:
        """Wrapper for substract method from parent class DateTimeRange."""
        return self.convert(super(TimeRange, self).subtract(x))

    def split(self, separator: TimeRange) -> TimeRange | List[TimeRange]:
        """Wrapper for split method from parent class DateTimeRange."""
        return self.convert(super(TimeRange, self).split(separator))

    def copy(self) -> TimeRange:
        """Return a copy of the instance object."""
        return TimeRange(start=self.start, end=self.end, format=self.format)

    def differences(self, subt_dtrs: List[TimeRange]) -> List[TimeRange]:
        """
        Returns list of TimeRanges resulting from the substraction
        of multiple TimeRanges from a source TimeRange.

        Parameters
        ----------
        subt_dtrs : list
            List of DTRs to be subtracted from source DTR.

        Returns
        -------
        list
            Remaining DTRs after subtraction.

        """
        if not subt_dtrs:
            return [self]
        subt_dtrs = TimeRange.merge(subt_dtrs)
        dtrs = [self.copy()]
        diff_dtrs = []
        for i, subt_dtr in enumerate(subt_dtrs):
            if i != 0:
                dtrs = diff_dtrs
                diff_dtrs = []
            for dtr in dtrs:
                diff_dtrs.extend(dtr.subtract(subt_dtr))
        return diff_dtrs

    @staticmethod
    def from_strftime_day(date_strftime: str, strftime_format: str = '%d.%m.%Y') -> TimeRange:
        date_ts = pd.to_datetime(
            date_strftime, format=strftime_format)
        date_ts_next = (date_ts +
                        pd.Timedelta(value=1, unit='d') - pd.Timedelta.resolution)
        # TODO string format
        return TimeRange(date_ts, date_ts_next, strftime_format+' %H:%M')

    @staticmethod
    def validate(dtrs: List[TimeRange]) -> None:
        assert isinstance(dtrs, list)
        if dtrs:
            assert all([isinstance(x, TimeRange) for x in dtrs])

    @staticmethod
    def merge(dtrs: List[TimeRange]) -> List[TimeRange]:
        """
        Simplifies given TimeRanges by merging those which either overlap
        or are adjacent.

        Parameters
        ----------
        dtrs : list
            TimeRanges to merge.

        Returns
        -------
        joined_dtrs : list
            Unified TimeRanges.

        """
        TimeRange.validate(dtrs)
        if len(dtrs) == 0 or len(dtrs) == 1:
            return dtrs

        dtrs = list(filter(lambda x: x.is_set(), dtrs))
        dtrs.sort(key=lambda x: x.start_datetime, reverse=False)
        joined = [dtrs[0].copy()]

        for i in range(1, len(dtrs)):
            x = joined[-1]
            y = dtrs[i].copy()
            if x.is_intersection(y):
                joined[-1] = x.encompass(y)
            else:
                joined.append(y)
        return joined
