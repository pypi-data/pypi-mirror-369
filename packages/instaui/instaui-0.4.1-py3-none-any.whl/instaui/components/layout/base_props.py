from typing import Literal, Union
from typing_extensions import TypedDict
from instaui.components._responsive_type._common import (
    TMaybeResponsive,
    TLevel_0_9,
    TLevel_neg_9_9,
    TWithAutoValue,
)
from instaui.components._responsive_type._layout import TOverflowEnum


class TLayoutBaseProps(TypedDict, total=False):
    p: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    px: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    py: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    pt: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    pb: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    pl: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    pr: TMaybeResponsive[Union[str, TLevel_0_9, TWithAutoValue]]
    width: TMaybeResponsive[str]
    height: TMaybeResponsive[str]
    min_width: TMaybeResponsive[str]
    min_height: TMaybeResponsive[str]
    max_width: TMaybeResponsive[str]
    max_height: TMaybeResponsive[str]
    position: TMaybeResponsive[
        Literal["static", "relative", "absolute", "fixed", "sticky"]
    ]
    inset: TMaybeResponsive[Union[str, TLevel_neg_9_9]]
    top: TMaybeResponsive[Union[str, TLevel_neg_9_9]]
    right: TMaybeResponsive[Union[str, TLevel_neg_9_9]]
    bottom: TMaybeResponsive[Union[str, TLevel_neg_9_9]]
    left: TMaybeResponsive[Union[str, TLevel_neg_9_9]]
    overflow: TMaybeResponsive[Union[TOverflowEnum, str]]
    overflow_x: TMaybeResponsive[Union[TOverflowEnum, str]]
    overflow_y: TMaybeResponsive[Union[TOverflowEnum, str]]
    flex_basis: TMaybeResponsive[str]
    flex_shrink: TMaybeResponsive[Union[str, Literal["0", "1"]]]
    flex_grow: TMaybeResponsive[Union[str, Literal["0", "1"]]]
    grid_area: TMaybeResponsive[str]
    grid_column: TMaybeResponsive[str]
    grid_column_start: TMaybeResponsive[str]
    grid_column_end: TMaybeResponsive[str]
    grid_row: TMaybeResponsive[str]
    grid_row_start: TMaybeResponsive[str]
    grid_row_end: TMaybeResponsive[str]
    m: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    mx: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    my: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    mt: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    mr: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    mb: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
    ml: TMaybeResponsive[Union[str, TLevel_neg_9_9, TWithAutoValue]]
