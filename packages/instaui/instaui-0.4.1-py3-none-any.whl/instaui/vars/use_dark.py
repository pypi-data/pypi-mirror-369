from __future__ import annotations
from typing import Optional

from .ref_base import RefBase
from .state import _ready_state


class UseDarkRef(RefBase):
    def __init__(
        self,
        deep_compare: bool = False,
        options: Optional[dict] = None,
    ) -> None:
        super().__init__(ref_type="useDark", deep_compare=deep_compare, args=options)


def use_dark(*, storage_key: Optional[str] = None, deep_compare: bool = False) -> bool:
    """
    On start up, it reads the value from localStorage/sessionStorage (the key is configurable) to see if there is a user configured color scheme, if not, it will use users' system preferences.

    Args:
        storage_key (Optional[str], optional): The local storage key to read the value from. Defaults to None(eg. "insta-color-scheme").

    Example:
    .. code-block:: python
        from instaui import ui,html

        @ui.page('/')
        def index():
            dark = ui.use_dark()
            html.checkbox(dark)
    """

    create_proxy, _ = _ready_state(None)

    return create_proxy(
        lambda _: UseDarkRef(
            deep_compare=deep_compare, options={"storageKey": storage_key}
        )
    )
