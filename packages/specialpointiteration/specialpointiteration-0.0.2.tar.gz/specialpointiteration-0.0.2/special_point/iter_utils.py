"""
iterator utilities
"""

from typing import List, Tuple, Iterator, TypeVar
from itertools import product as iterprod
from itertools import chain

A = TypeVar("A")

def with_heads(my_iter : Iterator[Iterator[A]]):
    """
    first is first
    second is now first,second
    ...
    also with a boolean to say whether it is from the latest part or not
    """
    # pylint:disable = invalid-name
    it = iter(my_iter)
    head_so_far : List[A] = []
    for cur_seg in it:
        cur_seg_list = list(cur_seg)
        yield chain(
            map(lambda z: (z,False),head_so_far),
            map(lambda z: (z,True),cur_seg_list)
            )
        head_so_far += cur_seg_list

def make_n_param_version(one_param_iterator : Iterator[Iterator[A]],
                         num_params : int) -> Iterator[Tuple[A,...]]:
    """
    like iterprod repeated num_params times
        but so that we get the earlier parts as well
        so long as at least one of the factors of the tuple
        is from the latest batch
    then flatten this into just iterating over tuples
    e.g. one_param_iter is [x,y,z,...] where each of x,y,z is iterable
        first we give a tuple of num_params things all from x
        then we give a tuple of num_params things from x or y
            provided at least one was from y (so no repeats with earlier)
        continue like this
    """
    if num_params < 1:
        raise ValueError("Should be at least 1 factor")
    if num_params == 1:
        return map(lambda x: (x,),chain.from_iterable(one_param_iterator))
    one_param_iterator : Iterator[Iterator[Tuple[A,bool]]] = iter(with_heads(one_param_iterator))
    def one_true(tup : Tuple[Tuple[A,bool],...]) -> bool:
        """
        at least one factor has true
        """
        return any(map(lambda cur: cur[1],tup))
    def firsts(tup : Tuple[Tuple[A,bool],...]) -> Tuple[A,...]:
        """
        drop the booleans from each factor
        """
        return tuple(map(lambda z: z[0], tup))
    intermediate_1 = map(lambda iterable :\
                        map(firsts,
                            filter(one_true,
                                iterprod(iterable, repeat=num_params)
                            )
                        ),
                        one_param_iterator
                    )
    return chain.from_iterable(intermediate_1)
