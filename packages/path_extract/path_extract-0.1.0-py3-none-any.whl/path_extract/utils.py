from typing import Iterable, TypeVar
from itertools import chain

T = TypeVar("T")


def chain_flatten(lst: Iterable[Iterable[T]]) -> list[T]:
    return list(chain.from_iterable(lst))


def set_difference(s_large: Iterable, s2: Iterable):
    return list(set(s_large).difference(set(s2)))


# def set_intersection(s_large: Iterable, s2: Iterable):
#     return list(set(s_large).difference(set(s2)))


def set_symmetric_difference(s1: Iterable, s2: Iterable):
    return list(set(s1).symmetric_difference(set(s2)))


def set_union(s1: Iterable, s2: Iterable):
    return list(set(s1).union(set(s2)))


def are_sets_equal(_s1: Iterable, _s2: Iterable):
    s1 = set(_s1)
    s2 = set(_s2)
    assert len(s1) == len(s2), "Sets are not equal - do not have metching len"
    assert s1.intersection(s2) == s1, (
        "Sets are not equal - their intersection does not match s1"
    )
    return True
