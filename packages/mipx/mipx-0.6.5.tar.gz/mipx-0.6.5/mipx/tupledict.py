# -*- coding: utf-8 -*-
# @Time    : 2023/4/1 10:39
# @Author  : luyi
from functools import reduce
from typing import Dict, List
from .utilx import tuple_fuzz_match_list, is_list_or_tuple, get_length
from .tuplelist import tuplelist
from .interface_ import K, ITupledict
from warnings import warn


class tupledict(ITupledict):
    """
    tupledict is a subclass of dict where
      the keys are a tuplelist.
    """

    def __new__(cls, *args, **kwargs) -> "ITupledict":
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        self.dim = None
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if self.dim is None:
            self.dim = get_length(key)
        super().__setitem__(key, value)

    def prod(self, coeff: Dict, *pattern):  # type:ignore
        """
        coeff为一个dict类型，指定待计算的元素的系数。coeff的key要与待计算的集合中的key能对应
        :param coeff:
        :param pattern:
        :return:
        """
        warn(f"call to deprecated function,use quickprod function")
        tList = tuplelist(self.keys())
        tl = tList.select(*pattern)
        if len(tl) == 0:
            return 0
        pl = []
        for key in tl:
            ok, k = tuple_fuzz_match_list(key, coeff.keys())
            if ok:
                pl.append(self[key] * coeff[k])
        return reduce(lambda a, b: a + b, pl)

    def select(self, *pattern):
        warn(f"call to deprecated function,use quickselect function")
        tlist = tuplelist(self.keys())
        keys = tlist.select(*pattern)
        return [self[key] for key in keys]

    def sum(self, *pattern):  # type:ignore
        warn(f"call to deprecated function,use quicksum function")
        v = self.select(*pattern)
        if len(v) == 0:
            return 0
        return reduce(lambda a, b: a + b, v)

    def quickprod(self, coeff: Dict, *pattern):  # type:ignore
        tList = tuplelist(self.keys())
        tl = tList.quickselect(*pattern)
        if len(tl) == 0:
            return 0
        pl = []
        for key in tl:
            ok, k = tuple_fuzz_match_list(key, coeff.keys())
            if ok:
                pl.append(self[key] * coeff[k])
        item = self[tl[0]]
        return item._solver.Sum(pl)

    def quickselect(self, *pattern) -> List:
        """
        快速挑选符合模式的items
        """
        dim = len(pattern)
        if dim == 0:
            return list(self.data.values())  # type: ignore
        else:
            assert (
                self.dim == dim
            ), f"pattern dim {dim} not match with dict dim {self.dim}"
        li = []
        if self.dim == 1:
            for key in self.data.keys():
                p = pattern[0]
                if p == "*" or p == key:
                    li.append(self[key])
            return li
        for key in self.data.keys():
            ok = True
            for i, k in enumerate(key):
                p = pattern[i]
                if p == "*":
                    continue
                if p != k:
                    ok = False
                    break
            if ok:
                li.append(self[key])
        return li

    def quicksum(self, *pattern):  # type:ignore
        v = self.quickselect(*pattern)
        if len(v) == 0:
            return 0
        item = v[0]
        return item._solver.Sum(v)


def multidict(data: Dict):
    """
    :param data:
    :return:
        keys, [dict1, dict2] = multidict( {
                 'key1': [1, 2],
                 'key2': [1, 3],
                 'key3': [1, 4] } )
    """
    t_list = tuplelist(data.keys())
    num = None
    for key, items in data.items():
        _num = get_length(items)
        if num is None:
            num = _num
        else:
            if num != _num:
                raise ValueError("length of values should be same")
    if num is None:
        raise ValueError("multidict error")
    t_dicts = [
        tupledict(
            {
                key: data[key][i] if is_list_or_tuple(data[key]) else data[key]
                for key in t_list
            }
        )
        for i in range(num)
    ]
    if num == 1:
        return t_list, t_dicts[0]
    return t_list, *t_dicts
