"""
rational of the form a/b^d
"""

from __future__ import annotations
from typing import Tuple

class AdicRational:
    """
    unreduced rational number
    where denominator is power of given base
    """
    def __init__(self,numerator : int,denominator_base : int,denominator_power : int):
        self.numerator = numerator
        self.denominator_base = denominator_base
        self.denominator_power = denominator_power

    def __repr__(self):
        if self.denominator_power == 1:
            return f"{self.numerator}/{self.denominator_base}"
        if self.denominator_power == 0:
            return f"{self.numerator}"
        return f"{self.numerator}/{self.denominator_base}^{self.denominator_power}"

    def count_with_denom(self) -> Tuple[int,int]:
        """
        how many have this same denominator power
        how many have denominator powers less than or equal to this one's
        """
        if self.denominator_power == 0:
            return 3,3
        def count_leq(denom_power) -> int:
            top_power = self.denominator_base**denom_power
            return top_power*2 + 1
        def count_equal(denom_power) -> int:
            return self.denominator_base**(denom_power-1)*(self.denominator_base-1)*2
        my_count_leq = count_leq(self.denominator_power)
        my_count_equal = count_equal(self.denominator_power)
        return my_count_leq, my_count_equal

    def to_float(self) -> float:
        """
        convert to float
        """
        return self.numerator/(self.denominator_base**self.denominator_power)

    def rescale(self, zoom_in_factor: int) -> AdicRational:
        """
        zoom in by self.denominator_base^zoom_in_factor
        """
        return AdicRational(self.numerator,
                            self.denominator_base,
                            self.denominator_power+zoom_in_factor)

    def __add__(self, other : AdicRational) -> AdicRational:
        """
        add two adic rationals with same denominator base
        """
        if self.denominator_base != other.denominator_base:
            raise ValueError("Mismatched bases")
        if self.denominator_power>other.denominator_power:
            other_numerator_rescaling = \
                self.denominator_base**(self.denominator_power - other.denominator_power)
            return AdicRational(self.numerator + other.numerator*other_numerator_rescaling,
                                self.denominator_base,self.denominator_power)
        if other.denominator_power<self.denominator_power:
            self_numerator_rescaling = \
                self.denominator_base**(other.denominator_power - self.denominator_power)
            return AdicRational(self.numerator*self_numerator_rescaling + other.numerator,
                                self.denominator_base,self.denominator_power)
        return AdicRational(self.numerator + other.numerator,
                            self.denominator_base,self.denominator_power)

    def clone(self) -> AdicRational:
        """
        Clone a AdicRational
        """
        return AdicRational(self.numerator,self.denominator_base,self.denominator_power)
