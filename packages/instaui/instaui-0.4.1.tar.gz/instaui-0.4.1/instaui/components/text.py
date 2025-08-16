from __future__ import annotations
from typing import Optional, Literal, Union
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.components._responsive_type._common import (
    TMaybeResponsive,
    TLevel_1_9,
)
from instaui.components._responsive_type._color import TColor
from instaui.components._responsive_type._typography import (
    TWeightEnum,
    TTextWrapEnum,
    TTrimEnum,
    TAlignEnum,
)
from instaui.components._responsive_utils import gen_responsive_props


class Text(Element):
    def __init__(
        self,
        text: Optional[TMaybeRef[str]] = None,
        *,
        as_: Optional[TMaybeRef[Literal["span", "div", "label", "p"]]] = None,
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[TLevel_1_9]] = None,
        color: Optional[TMaybeRef[Union[TColor, str]]] = None,
        weight: Optional[TMaybeResponsive[Union[TWeightEnum, str]]] = None,
        align: Optional[TMaybeResponsive[Union[TAlignEnum, str]]] = None,
        trim: Optional[TMaybeRef[Union[TTrimEnum, str]]] = None,
        truncate: Optional[TMaybeRef[bool]] = None,
        text_wrap: Optional[TMaybeRef[Union[TTextWrapEnum, str]]] = None,
        high_contrast: Optional[TMaybeRef[bool]] = None,
    ):
        super().__init__("text")

        self.props({"innerText": text})
        self.props(
            gen_responsive_props(
                {
                    "as": as_,
                    "as_child": as_child,
                    "size": size,
                    "color": color,
                    "weight": weight,
                    "text_align": align,
                    "trim": trim,
                    "truncate": truncate,
                    "text_wrap": text_wrap,
                    "high_contrast": high_contrast,
                }
            )
        )
