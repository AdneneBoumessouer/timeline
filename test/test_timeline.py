#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 10:41:39 2021

@author: aboumessouer

"""

import pytest
import pandas as pd
from hypothesis import given, settings, strategies as st
from src.timerange import TimeRange
from src.timeline import TimeLine, UnsuficientTimedeltaError
from .custom_strategies import CustomStrategies as cs
from .utils import flatten


# pylint: disable=E1120


class TestMerge:

    """Testing merge method (method automatically executes in initializer)."""

    dtr1 = TimeRange("01.05.2021 08:00", "01.05.2021 10:00")
    dtr2 = TimeRange("01.05.2021 09:00", "01.05.2021 11:00")
    dtr3 = TimeRange("01.05.2021 10:00", "01.05.2021 12:00")
    dtr4 = TimeRange("01.05.2021 11:00", "01.05.2021 13:00")
    dtr5 = TimeRange("01.05.2021 12:00", "01.05.2021 14:00")
    dtr6 = TimeRange("01.05.2021 13:00", "01.05.2021 15:00")
    dtr7 = TimeRange("01.05.2021 14:00", "01.05.2021 16:00")
    dtr8 = TimeRange("01.05.2021 15:00", "01.05.2021 17:00")
    dtr9 = TimeRange("01.05.2021 16:00", "01.05.2021 18:00")

    def test_merge_with_empty_list(self):
        timeline = TimeLine()
        assert timeline == []

    def test_merge_with_one_dtr(self):
        timeline = TimeLine([self.dtr1])
        assert timeline == [self.dtr1]

    def test_merge_two_overlapping_dtrs(self):
        timeline = TimeLine([self.dtr1, self.dtr2])
        assert timeline == TimeLine([
            ("01.05.2021 08:00", "01.05.2021 11:00")])

    def test_merge_two_adjacent_dtrs(self):
        timeline = TimeLine([self.dtr1, self.dtr3])
        assert timeline == TimeLine([("01.05.2021 08:00", "01.05.2021 12:00")])

    def test_merge_two_disjoint_dtrs(self):
        timeline = TimeLine([self.dtr1, self.dtr4])
        assert timeline == [self.dtr1, self.dtr4]

    def test_merge_overlapping_and_disjoint_dtrs(self):
        dtrs = [self.dtr1, self.dtr2,
                self.dtr5, self.dtr6,  self.dtr9]
        timeline = TimeLine(dtrs)
        assert timeline == TimeLine([
            ("01.05.2021 08:00", "01.05.2021 11:00"),
            ("01.05.2021 12:00", "01.05.2021 15:00"),
            ("01.05.2021 16:00", "01.05.2021 18:00")])

    def test_merge_adjacent_and_overlapping_and_disjoint_dtrs(self):
        dtrs = [self.dtr1, self.dtr4, self.dtr5,
                self.dtr6, self.dtr8, self.dtr9]
        timeline = TimeLine(dtrs)
        assert timeline == TimeLine([
            ("01.05.2021 08:00", "01.05.2021 10:00"),
            ("01.05.2021 11:00", "01.05.2021 18:00")])


class TestSplit:

    def test_split_TimeRange(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        separator = pd.to_datetime(
            "01.05.2021 10:00", format=src_dtr.format)
        left_split, right_split = src_dtr.split(separator)
        assert left_split == TimeRange("01.05.2021 08:00", "01.05.2021 10:00")
        assert right_split == TimeRange("01.05.2021 10:00", "01.05.2021 19:00")

    def test_split_timeline_case_1(self):
        """Test Case 1: seperator before timeline"""
        timeline = TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                             ("01.05.2021 11:00", "01.05.2021 12:00"),
                             ("01.05.2021 13:00", "01.05.2021 14:00")])
        separator = pd.to_datetime(
            "01.05.2021 07:00", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == TimeLine()
        assert right == TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                                  ("01.05.2021 11:00", "01.05.2021 12:00"),
                                  ("01.05.2021 13:00", "01.05.2021 14:00")])

    def test_split_timeline_case_2(self):
        """Test Case 2: seperator after timeline"""
        timeline = TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                             ("01.05.2021 11:00", "01.05.2021 12:00"),
                             ("01.05.2021 13:00", "01.05.2021 14:00")])
        separator = pd.to_datetime(
            "01.05.2021 15:00", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                                 ("01.05.2021 11:00",
                                  "01.05.2021 12:00"),
                                 ("01.05.2021 13:00", "01.05.2021 14:00")])
        assert right == TimeLine()

    def test_split_timeline_case_3(self):
        timeline = TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                             ("01.05.2021 11:00", "01.05.2021 12:00"),
                             ("01.05.2021 13:00", "01.05.2021 14:00")])
        separator = pd.to_datetime(
            "01.05.2021 10:30", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == TimeLine(
            [("01.05.2021 08:00", "01.05.2021 10:00")])
        assert right == TimeLine([("01.05.2021 11:00", "01.05.2021 12:00"),
                                  ("01.05.2021 13:00", "01.05.2021 14:00")])

    def test_split_timeline_case_4(self):
        timeline = TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                             ("01.05.2021 11:00", "01.05.2021 12:00"),
                             ("01.05.2021 13:00", "01.05.2021 14:00")])
        separator = pd.to_datetime(
            "01.05.2021 11:30", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == TimeLine([("01.05.2021 08:00", "01.05.2021 10:00"),
                                 ("01.05.2021 11:00", "01.05.2021 11:30")])
        assert right == TimeLine([("01.05.2021 11:30", "01.05.2021 12:00"),
                                  ("01.05.2021 13:00", "01.05.2021 14:00")])

    def test_split_timeline_separator_left_edge(self):
        timeline = TimeLine(
            [("01.05.2021 08:00", "01.05.2021 10:00")])
        separator = pd.to_datetime(
            "01.05.2021 08:00", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == TimeLine() and right == timeline

    def test_split_timeline_separator_right_edge(self):
        timeline = TimeLine(
            [("01.05.2021 08:00", "01.05.2021 10:00")])
        separator = pd.to_datetime(
            "01.05.2021 10:00", format='%d.%m.%Y %H:%M')
        left, right = timeline.split(separator)
        assert left == timeline and right == TimeLine()


class TestIntersection:

    @given(tuples_1=st.lists(cs.dtr_tp(), max_size=10), tuples_2=st.lists(cs.dtr_tp(), max_size=10))
    @settings(deadline=None)
    def test_intersection_timelines_property(self, tuples_1, tuples_2):
        """Test intersection property."""
        t1 = TimeLine([TimeRange(*tpl) for tpl in tuples_1])
        t2 = TimeLine([TimeRange(*tpl) for tpl in tuples_2])
        assert t1.intersection(t2) == t2.intersection(t1)


class TestDifferences:

    def test_differences(self):
        t1 = TimeLine([("01.05.2021 08:00", "01.05.2021 16:00")])
        t2 = TimeLine([
            ("01.05.2021 07:00", "01.05.2021 10:00"),
            ("01.05.2021 12:00", "01.05.2021 14:00"),
            ("01.05.2021 15:00", "01.05.2021 19:00")])
        diff = t1.difference(t2)
        assert diff == TimeLine([
            ("01.05.2021 10:00", "01.05.2021 12:00"),
            ("01.05.2021 14:00", "01.05.2021 15:00")])

    @given(src_tuple=cs.dtr_tp(), subst_tuples=st.lists(cs.dtr_tp()))
    # @given(src_tuple=cs.dtr_as_tuple(), subst_tuples=st.lists(cs.dtr_as_tuple()))
    def test_difference_property(self, src_tuple, subst_tuples):
        t1 = TimeLine([TimeRange(*src_tuple)])
        t2 = TimeLine([TimeRange(*tpl) for tpl in subst_tuples])
        inter, diff = t1.inter_diff(t2)
        assert t1 == inter + diff


class TestDifferenceIntersectionUnion:

    @given(src_tuples=st.lists(cs.dtr_as_tuple()), subst_tuples=st.lists(cs.dtr_as_tuple()))
    @settings(deadline=None)
    def test_orig_equals_difference_plus_intersection_property(self, src_tuples, subst_tuples):
        """
        Test the most general case:
        if we take multiple DTRs (src_dtrs) and substract from them multiple DTRs (subt_dtrs)
        to get the difference DTRs (diff_dtrs), then src_dtr must be equal to the union
        of inter_dtrs and diff_dtrs should always be true.

        """
        # initialize DTRs from tuples
        src_timeline = TimeLine([TimeRange(*src_tuple)
                                 for src_tuple in src_tuples])
        subst_timeline = TimeLine([TimeRange(*subst_tuple)
                                   for subst_tuple in subst_tuples])
        # compute intersections
        inter_timeline = TimeLine([src_dtr.intersection(
            subt_dtr) for src_dtr in src_timeline for subt_dtr in subst_timeline
            if src_dtr.is_intersection(subt_dtr)])
        # compute differences
        diff_timeline = TimeLine(flatten([src_dtr.differences(subst_timeline.timeranges)
                                          for src_dtr in src_timeline]))
        # test property
        assert src_timeline == inter_timeline + diff_timeline

    @given(tuples_1=st.lists(cs.dtr_tp(), max_size=10), tuples_2=st.lists(cs.dtr_tp(), max_size=10))
    @settings(deadline=None)
    def test_union_equals_differences_plus_intersection_property(self, tuples_1, tuples_2):
        """property: diff(t1, t2) + diff(t2, t1) + inter(t1, t2) == (dtrs1 + dtrs2) """
        t1 = TimeLine([TimeRange(*tpl) for tpl in tuples_1])
        t2 = TimeLine([TimeRange(*tpl) for tpl in tuples_2])
        inter, diff_12 = t1.inter_diff(t2)
        diff_21 = t2.difference(t1)
        # compute union through differences and intersection
        union = diff_12 + diff_21 + inter
        # compute union through original timelines
        union_expected = t1 + t2
        # assert property
        assert union == union_expected


class TestConsume:
    def test_consumed_and_remaining_example_1(self):
        # TODO add description
        timeline = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        timedelta = pd.Timedelta(value=1, unit="hours")
        consumed = timeline.consume(timedelta)

        expected_consumed = TimeLine(
            [("01.03.2021 08:00", "01.03.2021 09:00")])
        expected_remaining = TimeLine([
            ("01.03.2021 09:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00")])

        assert consumed == expected_consumed
        assert timeline == expected_remaining

    def test_consumed_and_remaining_example_2(self):
        # TODO add description
        timeline = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00")])
        timedelta = pd.Timedelta(value=2, unit="hours")
        consumed = timeline.consume(timedelta)

        expected_consumed = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00")])
        expected_remaining = TimeLine([
            ("01.03.2021 12:00", "01.03.2021 15:00")])

        assert consumed == expected_consumed
        assert timeline == expected_remaining

    def test_consumed_and_remaining_example_3(self):
        # TODO add description
        timeline = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        timedelta = pd.Timedelta(value=5, unit="hours")
        consumed, remaining = timeline.consume(timedelta, update=False)

        expected_consumed = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        expected_remaining = TimeLine()

        assert consumed == expected_consumed
        assert remaining == expected_remaining

    def test_consumed_and_remaining_example_4(self):
        # TODO add description
        available = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        consumed = TimeLine()
        for string in ["30 minutes", "2 hours", "2 hours 30 minutes"]:
            timedelta = pd.Timedelta(string)
            consumed += available.consume(timedelta, update=True)
        consumed.merge()

        expected_consumed = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        expected_remaining = TimeLine([])

        assert consumed == expected_consumed
        assert available == expected_remaining

    def test_raises_error_if_available_time_shorter_than_timedelta_to_consume(self):
        # TODO add description
        timeline = TimeLine([
            ("01.03.2021 08:00", "01.03.2021 10:00"),
            ("01.03.2021 12:00", "01.03.2021 15:00"),
        ])
        timedelta = pd.Timedelta(value=10, unit="hours")
        with pytest.raises(UnsuficientTimedeltaError):
            _ = timeline.consume(timedelta)

    # @given(list_src_tuples=st.lists(cs.dtr_as_tuple(), min_size=1), list_timedeltas=cs.list_timedeltas())
    @given(list_tuples=st.lists(cs.dtr_tp(), min_size=1, max_size=20), list_timedeltas=cs.list_timedeltas())
    def test_consumed_union_remaining_equals_original(self, list_tuples, list_timedeltas):
        """
        Tests invariate ptoperty of consume function:
        The union of consumed DTRs and remaining DTRs must always be equal to original DTR.
        """
        timeline = TimeLine([TimeRange(*tpl) for tpl in list_tuples])
        for timedelta in list_timedeltas:
            if timedelta <= timeline.timedelta:
                consumed, remaining = timeline.consume(timedelta, update=False)
                assert consumed + remaining == timeline
            else:
                with pytest.raises(UnsuficientTimedeltaError):
                    _ = timeline.consume(timedelta)
