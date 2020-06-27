# -*- coding: utf-8 -*-
# @File : types.py
# @Author : mocobk
# @Email : mailmzb@qq.com
# @Time : 2020-05-03 17:06

"""
自定义类型别名, 用于 TypeHint

eg.

from typing import List, Tuple, Union

# 严格限制为 最外层是元组，且只有两个元素
# 第一个元素是有两个 int 元素的元组，第二个元素只能是 str
TYPE1 = Tuple[Tuple[int, int], str]

# 参数为 字符串、列表、元组中的一个即可
TYPE2 = Union[str, list, tuple]
"""
import typing

StrSequenceOrSet = typing.Union[typing.Sequence[str], typing.Set[str]]
