"""
test the iterator utilities
"""
from ..special_point.iter_utils import with_heads

def test_head():
    """
    test of with_heads
    """
    my_iter = [[],[0],[],[1],[2,3],[4,5,6]]
    expected = [[],
                [(0,True)],
                [(0,False)],
                [(0,False),(1,True)],
                [(0,False),(1,False),(2,True),(3,True)],
                [(0,False),(1,False),(2,False),(3,False),(4,True),(5,True),(6,True)]]
    after_iter = iter(with_heads(my_iter))
    for idx,observed_idx in enumerate(after_iter):
        assert list(observed_idx) == expected[idx]
