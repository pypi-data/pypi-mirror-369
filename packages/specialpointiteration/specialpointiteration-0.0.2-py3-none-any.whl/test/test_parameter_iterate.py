"""
test the classes in parameter_iterate
"""
from __future__ import absolute_import
from itertools import product
from random import choice
import pytest

from ..special_point.iter_utils import make_n_param_version
from ..special_point.parameter_iterate import OneParameterIterator

def test_1d():
    """
    test of OneParameterIterator
    """
    localization_factor = choice([2,3,5,6])
    p = OneParameterIterator(localization_factor)
    cur_denominator = 1
    cur_denominator_power = 0
    for cur in p:
        if cur_denominator_power == 0:
            expected_nums = [-1,0,1]
        else:
            expected_nums = [i for i in\
                             range(-cur_denominator,cur_denominator+1)\
                                if i % localization_factor != 0]
        assert list(cur[0]) == expected_nums
        assert cur[1] == (localization_factor,cur_denominator_power)
        cur_denominator_power += 1
        cur_denominator *= localization_factor
        if p.get_current_denominator()>16:
            break
    q = p.deep_copy()
    for cur in p:
        if cur_denominator_power == 0:
            expected_nums = [-1,0,1]
        else:
            expected_nums = [i for i in\
                             range(-cur_denominator,cur_denominator+1)\
                                if i % localization_factor != 0]
        assert list(cur[0]) == expected_nums
        assert cur[1] == (localization_factor,cur_denominator_power)
        cur_denominator_power += 1
        cur_denominator *= localization_factor
        if p.get_current_denominator()>20:
            break
    cur_denominator = 1
    cur_denominator_power = 0
    for cur in q:
        if cur_denominator_power == 0:
            expected_nums = [-1,0,1]
        else:
            expected_nums = [i for i in\
                             range(-cur_denominator,cur_denominator+1)\
                                if i % localization_factor != 0]
        assert list(cur[0]) == expected_nums
        assert cur[1] == (localization_factor,cur_denominator_power)
        cur_denominator_power += 1
        cur_denominator *= localization_factor
        if q.get_current_denominator()>10:
            break

def test_hard_cutoff():
    """
    a hard cutoff where the denominators are only 1
    """
    localization_factor = choice([2,3,5,6])
    num_dimensions = choice([2,3,4,5])
    p = OneParameterIterator(localization_factor,0)
    np = make_n_param_version(
        map(lambda fracs : (num/(fracs[1][0]**fracs[1][1]) for num in fracs[0]),p),num_dimensions)
    expected = product([-1.0,0.0,1.0],repeat=num_dimensions)
    for cur_obs in np:
        cur_exp = next(expected)
        assert cur_obs==cur_exp
    with pytest.raises(StopIteration):
        _z = next(expected)
