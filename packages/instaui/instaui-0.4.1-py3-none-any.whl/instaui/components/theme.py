from __future__ import annotations
from typing import Optional, Union
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.components._responsive_type._color import TColor


class Theme(Element):
    def __init__(
        self,
        *,
        accent_color: Optional[TMaybeRef[Union[TColor, str]]] = None,
    ):
        super().__init__("theme")
        self.props({"accent-color": accent_color})
