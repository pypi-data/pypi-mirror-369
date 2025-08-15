"""
iterate within a prod_i [a_i,b_i]
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple
from math import sin, pi as PI, asin
from .adic_rational import AdicRational
from .parameter_iterate import MultiParameterIterator

class BoxTransformation(Enum):
    """
    how to specify the transfomations from
    the standard [-1,1]^d to the provided box
    """
    NOTRANSFORMATION = auto()
    COORDINATEWISELINEAR = auto()
    COORDINATEWISESIN = auto()
    COORDINATEWISEASIN = auto()
    COORDINATEWISEGIVEN = auto()
    CUSTOM = auto()

class BoxIterator:
    """
    iterate through special points in prod_i [a_i,b_i]
    transformed from the standard one which goes through
    special points in [-1,1]^d
    as described in parameter_iterate.py
    """
    #pylint:disable=too-many-locals,too-many-branches,too-many-arguments
    def __init__(self, *, denominator_localization : int = 2,
                 num_dimensions : Optional[int] = None,
                 bounding_box : Optional[List[Tuple[float,float]]]=None,
                 bounding_is_tight: bool = True,
                 expected_per_denominator : Optional[Callable[[int],Optional[int]]] = None,
                 hard_denominator_power_cut : Optional[int] = None,
                 transformation : BoxTransformation = BoxTransformation.COORDINATEWISELINEAR,
                 coordinatewise_given_func : Optional[Callable[[int,float],float]]=None,
                 custom_func : Optional[Callable[[List[float]],List[float]]]=None,
                 bdry_checking_eps : float = 1e-3
                 ):
        bounding_box = self.__check_bounding_box(bounding_box,num_dimensions)
        self._bounding_is_tight = bounding_is_tight
        self._pre_transformation_iter = MultiParameterIterator(
                denominator_localization,
                self._num_dimensions,
                expected_per_denominator,
                hard_denominator_power_cut)
        self.__how_many_coarsest(expected_per_denominator,hard_denominator_power_cut)
        self._bdry_checking_eps = bdry_checking_eps
        if transformation == BoxTransformation.NOTRANSFORMATION:
            for (left_pt,right_pt) in bounding_box:
                if bounding_is_tight:
                    if abs(left_pt+1.0)>bdry_checking_eps or abs(right_pt-1.0)>bdry_checking_eps:
                        raise ValueError("When no transform, bounding box should be [-1,1]^d")
                else:
                    if left_pt+1.0<-bdry_checking_eps or right_pt-1.0>bdry_checking_eps:
                        raise ValueError(
                            "When no transform, bounding box should be contained inside [-1,1]^d")
            self._post_transformation : Callable[[Tuple[AdicRational,...]],Tuple[float,...]] = \
                lambda x: tuple(map(lambda z: z.to_float(),x))
        elif transformation == BoxTransformation.COORDINATEWISELINEAR:
            def linear_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
                new_point = [0.0]*len(standard_pt)
                for (idx,coord) in enumerate(standard_pt):
                    left_bdry, right_bdry = bounding_box[idx]
                    new_point[idx] = (coord.to_float() + 1.0)/2.0*(right_bdry-left_bdry) + left_bdry
                return tuple(new_point)
            self._post_transformation = linear_transform
        elif transformation == BoxTransformation.COORDINATEWISESIN:
            def sin_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
                new_point = [0.0]*len(standard_pt)
                for (idx,coord) in enumerate(standard_pt):
                    left_bdry, right_bdry = bounding_box[idx]
                    new_point[idx] = (sin(PI/2.0*coord.to_float()) + 1.0)/2.0*\
                        (right_bdry-left_bdry) + left_bdry
                return tuple(new_point)
            self._post_transformation = sin_transform
        elif transformation == BoxTransformation.COORDINATEWISEASIN:
            def asin_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
                new_point = [0.0]*len(standard_pt)
                for (idx,coord) in enumerate(standard_pt):
                    left_bdry, right_bdry = bounding_box[idx]
                    new_point[idx] = (asin(coord.to_float())*2.0/PI + 1.0)/2.0*\
                        (right_bdry-left_bdry) + left_bdry
                return tuple(new_point)
            self._post_transformation = asin_transform
        elif transformation == BoxTransformation.COORDINATEWISEGIVEN:
            if coordinatewise_given_func is None:
                raise ValueError("A coordinatewise transformation must be given")
            # only check the endpoints
            # otherwise
            # assuming the caller actually gave a [-1,1] simeq [a_i,b_i]
            BoxIterator.__check_boundaries(bounding_box,coordinatewise_given_func,
                                           bdry_checking_eps,bounding_is_tight)
            def given_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
                new_point = [0.0]*len(standard_pt)
                for (axis_num,coord) in enumerate(standard_pt):
                    new_point[axis_num] = coordinatewise_given_func(axis_num,coord.to_float())
                return tuple(new_point)
            self._post_transformation = given_transform
        elif transformation == BoxTransformation.CUSTOM:
            if custom_func is None:
                raise ValueError("A custom transformation must be given")
            # does not check anything about custom_func
            # assuming the caller actually gave a [-1,1]^d simeq prod_i [a_i,b_i]
            def given_custom_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
                standard_pt_floated = list(map(lambda x : x.to_float(),standard_pt))
                new_point = custom_func(standard_pt_floated)
                return tuple(new_point)
            self._post_transformation = given_custom_transform
        else:
            assert False, "A transformation must be one of the enum"

    def my_bounding_box(self) -> List[Tuple[float,float]]:
        """
        give a copy of the bounding box
        """
        return list(self._bounding_box)

    def __iter__(self):
        """
        itself
        """
        return self

    def __next__(self) -> Tuple[Tuple[AdicRational,...],Tuple[float,...]]:
        """
        the next point as a tuple of num_dimensions floats
        """
        standard_pt = self._pre_transformation_iter.__next__()
        return standard_pt,self._post_transformation(standard_pt)

    def __check_bounding_box(self,bounding_box : Optional[List[Tuple[float,float]]],
                             num_dimensions : Optional[int]) -> List[Tuple[float,float]]:
        if bounding_box is None and num_dimensions is None:
            raise ValueError(
                "At least the number of dimensions or the bounding box must be explicit")
        if bounding_box is None:
            bounding_box = [(0.0,1.0) for _ in range(num_dimensions)]
        if len(bounding_box) < 1:
            raise ValueError("There must be at least one coordinate axis")
        for (left_pt,right_pt) in bounding_box:
            if right_pt<=left_pt:
                raise ValueError("Each axis of the box must be an interval")
        self._num_dimensions = len(bounding_box)
        self._bounding_box = bounding_box
        return bounding_box

    @staticmethod
    def __check_boundaries(bounding_box : List[Tuple[float,float]],
                           coordinatewise_given_func : Callable[[int,float],float],
                           bdry_checking_eps : float, bounding_is_tight: bool) -> None:
        """
        helper for coordinatewise given function
        making sure it maps the -1,1 for each axis
        to the respective a_i and b_i
        """
        for axis_num,(left_bdry,right_bdry) in enumerate(bounding_box):
            neg_one_goes = coordinatewise_given_func(axis_num,-1.0)
            one_goes = coordinatewise_given_func(axis_num,1.0)
            seen_left_endpoint, seen_right_endpoint = \
                min(neg_one_goes,one_goes), max(neg_one_goes,one_goes)
            if bounding_is_tight:
                if abs(seen_left_endpoint - left_bdry)>bdry_checking_eps or \
                    abs(seen_right_endpoint - right_bdry)>bdry_checking_eps:
                    #pylint:disable=line-too-long
                    raise ValueError(
                        f"On axis {axis_num} the transformation should take -1,1 to {left_bdry},{right_bdry} or vice-versa")
            else:
                if seen_left_endpoint - left_bdry<-bdry_checking_eps or \
                    seen_right_endpoint - right_bdry>bdry_checking_eps:
                    #pylint:disable=line-too-long
                    raise ValueError(
                        f"On axis {axis_num} the transformation should take -1,1 to within {left_bdry},{right_bdry} or vice-versa")

    def __how_many_coarsest(self,expected_per_denominator,hard_denominator_power_cut):
        """
        helper for number of points where
        the coordinates pre-transformation
        are all -1,0,1
        """
        if expected_per_denominator is not None:
            self._num_with_denom_power_0 = expected_per_denominator(0)
        else:
            self._num_with_denom_power_0 = None
        if self._num_with_denom_power_0 is None:
            self._num_with_denom_power_0 = 3**self._num_dimensions
        if hard_denominator_power_cut is not None and hard_denominator_power_cut<0:
            self._num_with_denom_power_0 = 0

    def zoom_in(self, this_point: Tuple[AdicRational,...]) -> BoxIterator:
        """
        another BoxIterator which is zoomed in around the given point
        assumes that self was done with a coordinatewise BoxTransformation
        """
        to_return = BoxIterator(num_dimensions = 1)
        #pylint:disable=protected-access,attribute-defined-outside-init
        to_return._num_dimensions = self._num_dimensions
        def make_zoomed_in(box: List[Tuple[float,float]],
                           this_point: Tuple[AdicRational,...]) -> \
                            Tuple[Tuple[AdicRational,...],int,List[Tuple[float,float]]]:
            cur_denom_power = max(map(lambda r: r.denominator_power,this_point))
            denominator_base = this_point[0].denominator_base
            num_dimensions = len(this_point)
            zoomed_in_factor = cur_denom_power+1
            #pylint:disable=unnecessary-comprehension
            new_box = [(z0,z1) for (z0,z1) in box]
            hits_boundary = False
            for idx in range(num_dimensions):
                for_one_end = list(map(lambda r: r.clone(),this_point))
                for_one_end[idx] = for_one_end[idx] + \
                    AdicRational(-1,denominator_base,zoomed_in_factor)
                one_end = self._post_transformation(tuple(for_one_end))[idx]
                for_other_end = list(map(lambda r: r.clone(),this_point))
                for_other_end[idx] = for_other_end[idx] + \
                    AdicRational(1,denominator_base,zoomed_in_factor)
                other_end = self._post_transformation(tuple(for_other_end))[idx]
                if other_end<one_end:
                    one_end, other_end = other_end, one_end
                if one_end<=box[idx][0] or other_end>=box[idx][1]:
                    hits_boundary = True
            if not hits_boundary:
                return this_point,zoomed_in_factor,new_box
            # if we don't need to worry about the points yielded by to_return
            #   to be within the original box, e.g. periodicity
            #   or just an arbitrary restriction on domain
            #   then we can use this the same return
            #   it all depends on what self._post_transformation does with stuff outside
            #   [-1,1]^d
            return this_point,zoomed_in_factor,new_box
        zoomed_in_center,zoomed_in_factor,zoomed_in_box = \
            make_zoomed_in(self._bounding_box,this_point)
        to_return._bounding_box = zoomed_in_box
        to_return._pre_transformation_iter = self._pre_transformation_iter.deep_copy()
        to_return._num_with_denom_power_0 = self._num_with_denom_power_0
        def given_custom_transform(standard_pt : Tuple[AdicRational,...]) -> Tuple[float,...]:
            standard_pt_fixed : Tuple[AdicRational,...] = tuple(
                (x.rescale(zoomed_in_factor) + zoomed_in_center[idx]
                    for idx,x in enumerate(standard_pt))
                )
            return self._post_transformation(standard_pt_fixed)
        to_return._post_transformation = given_custom_transform
        to_return._bdry_checking_eps = self._bdry_checking_eps
        to_return._bounding_is_tight = self._bounding_is_tight and zoomed_in_factor == 0
        return to_return

if __name__ == "__main__":
    np = BoxIterator(denominator_localization=2,bounding_box=[(0,1),(-1,1)])
    # pylint:disable = invalid-name
    index = 0
    for _,cur in np:
        print(cur)
        index += 1
        if index>20:
            break
    print("Now with sin")
    np = BoxIterator(denominator_localization=2,bounding_box=[(0,1),(-1,1)],
                     transformation=BoxTransformation.COORDINATEWISESIN)
    # pylint:disable = invalid-name
    index = 0
    for _,cur in np:
        print(cur)
        index += 1
        if index>20:
            break
    print("Now with asin")
    np2 = BoxIterator(denominator_localization=2,
                      num_dimensions=1,
                     transformation=BoxTransformation.COORDINATEWISEASIN)
    # pylint:disable = invalid-name
    index = 0
    for _,cur in np2:
        print(cur)
        index += 1
        if index>20:
            break
