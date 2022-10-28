#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 16:40:31 2021

@author: aboumessouer
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from pprint import pformat
import numpy as np
import pandas as pd
from src.timerange import TimeRange
# import plotly.express as px


class TimeLine:
    """Class representing a timeline, i.e a set of ordered timeranges.

    Returns
    -------
    None

    Raises
    ------
    UnsuficientTimedeltaError
        raised when time to consume is greater than available time.
    """

    NOT_A_TIMELINE = "NaTL"

    def __init__(self,
                 timeranges: Optional[List[TimeRange | Tuple[str]]] = None,
                 ts_format="%d.%m.%Y %H:%M",
                 merged: bool = False,) -> None:
        """

        Parameters
        ----------
        timeranges : List[TimeRange | Tuple[str]], optional
            list of TimeRange objects or list of tuples, where each element represents a valid timerange, by default []
        ts_format : str, optional
            timestamp string format, by default "%d.%m.%Y %H:%M"
        merged : bool, optional
            whether the passed timeranges are merged, i.e do not overlap and are ordered chronologically, by default False
        """
        timeranges = timeranges or []
        self.timeranges = [TimeRange(*elem, format=ts_format) if isinstance(
            elem, (list, tuple)) else elem for elem in timeranges]
        assert len(self.timeranges) == len(timeranges)
        self.ts_format = ts_format
        self._merged = merged
        self.merge()

    def __eq__(self, other: TimeRange) -> bool:
        if isinstance(other, list):
            return self.timeranges == other
        return self.timeranges == other.timeranges

    def __repr__(self) -> str:
        if self.is_valid:
            return pformat(self.timeranges, width=10)
        return self.NOT_A_TIMELINE

    def __getitem__(self, i: int) -> TimeRange:
        return self.timeranges[i]

    def __add__(self, other: TimeLine) -> TimeLine:
        """Merge two timelines."""
        return TimeLine(self.timeranges + other.timeranges, self.ts_format)

    def __len__(self) -> int:
        return len(self.timeranges)

    @property
    def is_valid(self) -> bool:
        # TODO __bool__()
        return len(self) > 0

    @property
    def start_time(self):
        if not self.is_valid:
            return None
        self.merge()
        return self[0].start_datetime

    @property
    def end_time(self):
        if not self.is_valid:
            return None
        self.merge()
        return self[-1].end_datetime

    @property
    def timedelta(self) -> pd.Timedelta:
        if not self.is_valid:
            return pd.Timedelta(value=0)
        return np.sum([timerange.timedelta for timerange in self])

    def merge(self) -> None:
        """simplifies timeline by merging timeranges which either overlap
        or are adjacent."""
        if self._merged or len(self) <= 1:
            return
        timeranges = list(filter(lambda x: x.is_set(), self.timeranges))
        timeranges.sort(key=lambda x: x.start_datetime, reverse=False)
        merged = [timeranges[0].copy()]
        for i in range(1, len(timeranges)):
            x = merged[-1]
            y = timeranges[i].copy()
            if x.is_intersection(y):
                merged[-1] = x.encompass(y)
            else:
                merged.append(y)
        self.timeranges = merged
        self._merged = True

    def inter_diff(self, other: TimeLine) -> Tuple[TimeLine]:
        """Calculates intersection and difference of a timeline with another."""
        assert isinstance(other, TimeLine)
        self.merge()
        other.merge()
        inter = []
        diff = []
        if len(other) == 0:
            return TimeLine(), TimeLine(self.timeranges, merged=True)
        for src_tr in self:
            for subt_tr in other:
                if src_tr.is_intersection(subt_tr):
                    inter.append(src_tr.intersection(subt_tr))
            diff.extend(src_tr.differences(other.timeranges))
        return TimeLine(inter, merged=True), TimeLine(diff, merged=True)

    def intersection(self, other: TimeLine) -> TimeLine:
        """Calculate intersection of a timeline with another."""
        return self.inter_diff(other)[0]

    def difference(self, other: TimeLine) -> TimeLine:
        """Calculate difference of a timeline with another."""
        return self.inter_diff(other)[1]

    @property
    def has_overlaps(self) -> bool:
        """Tests whether timeline has overlapping TimeRanges"""
        timeranges = list(filter(lambda x: x.is_set(), self.timeranges))
        if len(timeranges) == 0:
            return False
        timeranges.sort(key=lambda x: x.start_datetime, reverse=False)
        for i in range(len(timeranges)-1):
            current, successor = timeranges[i], timeranges[i+1]
            if current.intersection(successor).timedelta > pd.Timedelta(value=0):
                return True
        return False

    def split(self, separator: pd.Timestamp) -> Tuple[TimeLine]:
        """Split timeline into two timelines according to separator."""
        # Case 1: seperator before timeline
        if separator < self[0].start_datetime:
            return TimeLine(), TimeLine(self[:], merged=True)
        # Case 2: separator after timeline
        if separator > self[-1].end_datetime:
            return TimeLine(self[:], merged=True), TimeLine()
        # Case 3: separator within timeline but not in any DTR
        bool_arr = [separator in x for x in self]
        if not any(bool_arr):
            end_datetimes = np.array(
                [dtr.end_datetime for dtr in self])
            i = np.nonzero(separator < end_datetimes)[0][0]
            return TimeLine(self[:i], merged=True), TimeLine(self[i:], merged=True)
        # Case 4: separator within timeline and in a DTR
        i = bool_arr.index(True)
        x_left = TimeRange(self[i].start_datetime, separator, self[i].format)
        x_right = TimeRange(separator, self[i].end_datetime, self[i].format)
        if x_left.timedelta > pd.Timedelta(value=0):
            dtrs_left = self[:i] + [x_left]
        else:
            dtrs_left = self[:i]
        if x_right.timedelta > pd.Timedelta(value=0):
            dtrs_right = [x_right] + self[i+1:]
        else:
            dtrs_right = self[i+1:]
        return TimeLine(dtrs_left, merged=True), TimeLine(dtrs_right, merged=True)

    def left_split(self, separator: pd.Timestamp) -> TimeLine:
        """Returns timeline left of the seperator."""
        return self.split(separator)[0]

    def right_split(self, separator: pd.Timestamp) -> TimeLine:
        """Returns timeline right of the seperator."""
        return self.split(separator)[1]

    def copy(self) -> TimeLine:
        """Copy timeline"""
        return TimeLine([timerange.copy() for timerange in self.timeranges], merged=self._merged)

    def consume(self, timedelta: pd.Timedelta, update: bool = True) -> TimeLine | Tuple[TimeLine]:
        """Consumes a certain amount of time from timeline."""
        for timerange in self:
            assert isinstance(timerange, TimeRange)
        # find self[i], i.e TimeRange at which the workstep finishes
        cumsum = np.cumsum([timerange.timedelta for timerange in self])
        if timedelta > self.timedelta:
            raise UnsuficientTimedeltaError(self.timedelta, timedelta)
        diffs = cumsum - timedelta
        i = np.nonzero(diffs >= pd.Timedelta(value=0))[0][0]
        remaining_timedelta = diffs[i]
        # calcualte split datetime
        split_datetime = self[i].end_datetime - remaining_timedelta
        # split opr_dtrs into two sub dtrs: consumed and remaining
        consumed, remaining = self.split(split_datetime)
        if not update:
            return consumed, remaining
        self.timeranges = remaining
        return consumed

    # def plot_timeline(self, y="None", title=None):
    #     "Plots timeline that can be visualized in jupyter notebook."
    #     dicts = []
    #     for timerange in self:
    #         dicts.append(dict(
    #             start=timerange.start_datetime.strftime("%Y-%m-%dT%H:%M"),
    #             end=timerange.end_datetime.strftime("%Y-%m-%dT%H:%M"),
    #             y=y))
    #     df = pd.DataFrame(dicts)
    #     fig = px.timeline(data_frame=df, x_start="start",
    #                       x_end="end", y="y", title=title)
    #     fig.update_layout(height=300)
    #     return fig


class UnsuficientTimedeltaError(ValueError):
    def __init__(self, av_timedelta, cons_timedelta: pd.Timedelta) -> None:
        self.message = f"available time {av_timedelta} is shorter than time to consume {cons_timedelta}."
        super().__init__(self.message)
