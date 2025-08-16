from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Label(Element):
    def __init__(
        self,
        *,
        for_: Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("label")

        self.props(
            {
                "for": for_,
            }
        )
