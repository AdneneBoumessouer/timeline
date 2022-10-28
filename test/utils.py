#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:40:39 2021

@author: aboumessouer
"""

from datetime import datetime, timedelta


def truncate(dt):
    """Truncates milliseconds from datetime"""
    dt_trunc = datetime(dt.year, dt.month, dt.day,
                        dt.hour, dt.minute, dt.second)
    return dt_trunc


def truncate_timedelta(td):
    """Truncates milliseconds from datetime"""
    td_trunc = timedelta(days=td.days, seconds=td.seconds)
    return td_trunc


def flatten(t): return [item for sublist in t for item in sublist]
