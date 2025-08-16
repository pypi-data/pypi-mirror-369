from __future__ import annotations
from typing import TypeVar

from .ref_base import RefBase
from .state import _ready_state

_T = TypeVar("_T")


class LocalStorageRef(RefBase):
    def __init__(
        self,
        key: str,
        value,
        deep_compare: bool = False,
    ) -> None:
        super().__init__(
            ref_type="storage",
            deep_compare=deep_compare,
            args={"type": "local", "key": key, "value": value},
        )


def local_storage(key: str, value: _T, deep_compare: bool = False) -> _T:
    """
    Creates a reactive state object synchronized with the browser's local storage.

    This function initializes a reactive value tied to a given key in local storage.
    The state persists across page reloads and retains its value between sessions
    on the same browser and device.

    Args:
        key (str): The local storage key to associate with the value.
        value (_T): The default value to use if no value exists in local storage.

    Returns:
        _T: A reactive value linked to the specified local storage key.

    Example:
    .. code-block:: python

        from instaui import ui, html

        @ui.page('/')
        def index():
            name = ui.local_storage("username", "")
            html.input(name)
    """

    create_proxy, is_proxy = _ready_state(value)
    if is_proxy:
        return value

    return create_proxy(
        lambda value: LocalStorageRef(key, value=value, deep_compare=deep_compare)
    )
