from __future__ import annotations
from typing import Optional, Literal
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive
from instaui.components._responsive_utils import gen_responsive_props


class Box(Element):
    def __init__(
        self,
        *,
        as_: Optional[TMaybeRef[Literal["div", "span"]]] = None,
        as_child: Optional[TMaybeRef[bool]] = None,
        display: Optional[
            TMaybeResponsive[Literal["none", "inline-block", "block", "contents"]]
        ] = None,
        **kwargs: Unpack[TLayoutBaseProps],
    ):
        super().__init__("box")

        self.props(
            gen_responsive_props(
                {
                    "as": as_,
                    "as_child": as_child,
                    "display": display,
                    **kwargs,
                }
            )
        )
