#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:40:39 2021

@author: aboumessouer

"""

import pytest
from src.timerange import TimeRange
from .custom_strategies import CustomStrategies as cs
from hypothesis import given

# pylint: disable=E1120


class TestValidity:

    def raise_value_error_if_start_greater_than_end(self):
        with pytest.raises(ValueError):
            TimeRange("01.05.2021 19:00", "01.05.2021 08:00")

    def raise_value_error_if_start_equals_end(self):
        with pytest.raises(ValueError):
            TimeRange("01.05.2021 08:00", "01.05.2021 08:00")


class TestFormat:

    def test_dtrs_equal_despite_different_format(self):
        format_1 = '%d.%m.%Y %H:%M'
        format_2 = '%d-%m-%Y %H:%M'
        dtr_1 = TimeRange("01.05.2021 08:00", "01.05.2021 19:00", format_1)
        dtr_2 = TimeRange("01-05-2021 08:00", "01-05-2021 19:00", format_2)
        assert dtr_1 == dtr_2

    def raise_value_error_if_str_and_format_mismatch(self):
        with pytest.raises(ValueError):
            TimeRange("01.05.2021 08:00", "01.05.2021 19:00", '%d-%m-%Y %H:%M')


class TestSubtraction:

    def test_subtraction_remaining_left(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        subst_dtr = TimeRange(
            "01.05.2021 14:00", "01.05.2021 19:00")
        diff_dtrs = src_dtr.subtract(subst_dtr)
        expected_remaining_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 14:00")
        assert diff_dtrs == [expected_remaining_dtr]

    def test_subtraction_remaining_right(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        subst_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 16:00")
        diff_dtrs = src_dtr.subtract(subst_dtr)
        expected_remaining_dtr = TimeRange(
            "01.05.2021 16:00", "01.05.2021 19:00")
        assert diff_dtrs == [expected_remaining_dtr]

    def test_subtraction_remaining_left_and_right(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        subst_dtr = TimeRange(
            "01.05.2021 14:00", "01.05.2021 16:00")
        diff_dtrs = src_dtr.subtract(subst_dtr)
        expected_remaining_left_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 14:00")
        expected_remaining_right_dtr = TimeRange(
            "01.05.2021 16:00", "01.05.2021 19:00")
        assert diff_dtrs == [expected_remaining_left_dtr,
                             expected_remaining_right_dtr]

    def test_subtraction_when_entire_src_encompassed_in_subt(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        subst_dtr = TimeRange(
            "01.05.2021 07:00", "01.05.2021 19:00")
        diff_dtrs = src_dtr.subtract(subst_dtr)
        assert diff_dtrs == []

    def test_subtraction_when_src_and_subst_do_not_intersect(self):
        src_dtr = TimeRange(
            "01.05.2021 08:00", "01.05.2021 19:00")
        subst_dtr = TimeRange(
            "02.05.2021 07:00", "02.05.2021 19:00")
        diff_dtrs = src_dtr.subtract(subst_dtr)
        assert diff_dtrs == [src_dtr]

    @given(src_tuple=cs.dtr_tp(), subst_tuple=cs.dtr_tp())
    # @given(src_tuple=cs.dtr_as_tuple(), subst_tuple=cs.dtr_as_tuple())
    def test_subtraction_property(self, src_tuple, subst_tuple):
        """Tests property: source DTR's must always be equal to the union
        of difference and intersection yielded from a subtraction."""
        # initialize DTRs from tuples
        src_dtr = TimeRange(*src_tuple)
        subst_dtr = TimeRange(*subst_tuple)
        # compute intersection
        inter_dtr = src_dtr.intersection(subst_dtr)
        # compute difference
        diff_dtrs = src_dtr.subtract(subst_dtr)
        # assert property
        union = TimeRange.merge([inter_dtr]+diff_dtrs)
        assert union == [src_dtr]
