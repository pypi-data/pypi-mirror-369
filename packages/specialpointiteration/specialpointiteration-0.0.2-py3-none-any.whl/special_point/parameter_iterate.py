"""
iterate through points in [-1,1]^d
with each coordinate
of the form n/d^k organized by smaller
values of k first (n is not a multiple of d)
when d>1, treat each point by it's maximum k among the coordinates
"""

from __future__ import annotations
from random import random
from typing import Callable, Optional, Tuple, TypeVar, Iterable
from .adic_rational import AdicRational
from .iter_utils import make_n_param_version

A = TypeVar("A")

class OneParameterIterator:
    """
    one parameter iterator
    """
    def __init__(self, denominator_localization : int,
                 hard_denominator_power_cut : Optional[int] = None):
        assert denominator_localization > 1
        self._denominator_localization = denominator_localization
        self._current_denominator = 1
        self._current_denominator_power = 0
        self._hard_denominator_power_cut = hard_denominator_power_cut
    def __iter__(self):
        """
        itself
        """
        return self
    def __next__(self) -> Tuple[Iterable[int],Tuple[int,int]]:
        """
        all those with the current denominator
        then multiply the denominator by denominator_localization
        to go to the next value of k
        """
        if self._hard_denominator_power_cut is not None and \
            self._current_denominator_power>self._hard_denominator_power_cut:
            raise StopIteration
        if self._current_denominator == 1:
            self._current_denominator_power += 1
            self._current_denominator *= self._denominator_localization
            numerators : Iterable[int] = [-1,0,1]
            denominator_power = 0
        else:
            numerators = (i for i in range(-self._current_denominator,self._current_denominator)\
                          if i % self._denominator_localization != 0)
            denominator_power = self._current_denominator_power
            self._current_denominator_power += 1
            self._current_denominator *= self._denominator_localization
        return (numerators,(self._denominator_localization,denominator_power))

    def deep_copy(self) -> OneParameterIterator:
        """
        a copy that is reset from the beginning
        """
        return OneParameterIterator(self._denominator_localization,self._hard_denominator_power_cut)

    def get_current_denominator(self) -> int:
        """
        read access _current_denominator
        """
        return self._current_denominator

class MultiParameterIterator:
    """
    [-1,1]^d cube parameter iterator
    """
    def __init__(self, denominator_localization : int, num_dimensions : int,
                 expected_per_denominator : Optional[Callable[[int],Optional[int]]] = None,
                 hard_denominator_power_cut : Optional[int] = None):
        assert denominator_localization > 1
        assert num_dimensions >= 1
        self._denominator_localization = denominator_localization
        self._num_dimensions = num_dimensions
        self._hard_denominator_power_cut = hard_denominator_power_cut
        self._one_param = OneParameterIterator(denominator_localization, hard_denominator_power_cut)
        self._underlying = \
            make_n_param_version(
                map(
                    lambda fracs : \
                        (AdicRational(num,fracs[1][0],fracs[1][1]) for num in fracs[0]),
                    self._one_param
                ),
                self._num_dimensions
            )
        self._expected_per_denominator = expected_per_denominator
        if expected_per_denominator is not None:
            self.__decimate_me(expected_per_denominator)

    def __decimate_me(self,expected_per_denominator : Callable[[int],Optional[int]]):
        def decimator(tup : Tuple[AdicRational,...]) -> bool:
            cur_denom_power = max(map(lambda r: r.denominator_power,tup))
            how_many_should_be = expected_per_denominator(cur_denom_power)
            if how_many_should_be is None:
                return True
            #pylint:disable=unused-variable
            cur_denom_count_leq,cur_denom_count_equal = \
                AdicRational(1,tup[0].denominator_base,cur_denom_power).count_with_denom()
            cur_denom_count_lt = cur_denom_count_leq - cur_denom_count_equal
            how_many_present = cur_denom_count_leq**len(tup)-cur_denom_count_lt**len(tup)
            if how_many_should_be >= how_many_present:
                return True
            keep = random()<(how_many_should_be/how_many_present)
            return keep
        self._underlying = filter(decimator,self._underlying)

    def __iter__(self):
        """
        itself
        """
        return self

    def __next__(self) -> Tuple[AdicRational,...]:
        """
        the next point as a tuple of num_dimensions AdicRationals
        """
        return self._underlying.__next__()

    def deep_copy(self) -> MultiParameterIterator:
        """
        a copy that is reset from the beginning
        """
        return MultiParameterIterator(denominator_localization=self._denominator_localization,
                                      num_dimensions=self._num_dimensions,
                                      expected_per_denominator=self._expected_per_denominator,
                                      hard_denominator_power_cut=self._hard_denominator_power_cut)

if __name__ == "__main__":
    np = MultiParameterIterator(2,2,lambda _: 9, 11)
    # pylint:disable = invalid-name
    index = 0
    for cur in np:
        print(cur)
        index += 1
        if index>80:
            break
