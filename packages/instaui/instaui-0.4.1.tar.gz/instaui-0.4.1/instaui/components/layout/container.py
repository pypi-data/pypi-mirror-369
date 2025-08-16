from __future__ import annotations
from typing import Optional, Literal
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive
from instaui.components._responsive_utils import gen_responsive_props


class Container(Element):
    def __init__(
        self,
        *,
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[Literal["1", "2", "3", "4"]]] = "4",
        display: Optional[TMaybeResponsive[Literal["none", "initial"]]] = None,
        align: Optional[TMaybeResponsive[Literal["left", "center", "right"]]] = None,
        **kwargs: Unpack[TLayoutBaseProps],
    ):
        super().__init__("container")

        self.props(
            gen_responsive_props(
                {
                    "as_child": as_child,
                    "ctn_size": size,
                    "display": display,
                    "align": align,
                    **kwargs,
                }
            )
        )
