from __future__ import annotations
from typing import Literal, Union
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive, TLevel_0_9
from instaui.components._responsive_utils import gen_responsive_props


class TFlexBaseProps(TLayoutBaseProps, total=False):
    as_: TMaybeRef[Literal["div", "span"]]
    as_child: TMaybeRef[bool]
    display: TMaybeResponsive[Literal["none", "inline-flex", "flex"]]
    align: TMaybeResponsive[Literal["start", "center", "end", "stretch", "baseline"]]
    justify: TMaybeResponsive[Literal["start", "center", "end", "between"]]
    wrap: TMaybeResponsive[Literal["nowrap", "wrap", "wrap-reverse"]]
    gap: TMaybeResponsive[Union[str, TLevel_0_9]]
    gap_x: TMaybeResponsive[Union[str, TLevel_0_9]]
    gap_y: TMaybeResponsive[Union[str, TLevel_0_9]]


class TFlexProps(TFlexBaseProps, total=False):
    direction: TMaybeResponsive[
        Literal["row", "column", "row-reverse", "column-reverse"]
    ]


class Flex(Element):
    def __init__(
        self,
        **kwargs: Unpack[TFlexProps],
    ):
        super().__init__("flex")

        self.props(gen_responsive_props(kwargs))


class FlexRow(Flex):
    def __init__(
        self,
        **kwargs: Unpack[TFlexBaseProps],
    ):
        super().__init__(direction="row", **kwargs)


class FlexColumn(Flex):
    def __init__(
        self,
        **kwargs: Unpack[TFlexBaseProps],
    ):
        super().__init__(direction="column", **kwargs)
