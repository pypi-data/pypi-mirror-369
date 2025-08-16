from __future__ import annotations
from typing import Optional, TypeVar

from .ref_base import RefBase

_T_Value = TypeVar("_T_Value")


class Ref(RefBase):
    def __init__(
        self,
        value: Optional[_T_Value] = None,
        deep_compare: bool = False,
    ) -> None:
        super().__init__(value=value, deep_compare=deep_compare)
