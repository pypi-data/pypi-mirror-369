from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional, Union
from instaui.components.element import Element
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from . import _src_utils

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Image(Element):
    def __init__(
        self,
        src: Optional[TMaybeRef[str]] = None,
        *,
        alt: Optional[TMaybeRef[str]] = None,
        width: Optional[TMaybeRef[Union[int, str]]] = None,
        height: Optional[TMaybeRef[Union[int, str]]] = None,
        title: Optional[TMaybeRef[str]] = None,
        srcset: Optional[TMaybeRef[str]] = None,
        sizes: Optional[TMaybeRef[str]] = None,
        loading: Optional[TMaybeRef[Literal["lazy", "eager"]]] = None,
    ):
        """
        Creates an HTML `<img>` element with configurable attributes.

        The `src` parameter specifies the image source. If a relative path is provided
        (starting with `/`), it resolves to files in the application's `assets/` directory.
        Absolute URLs are used directly.

        Args:
            src: Path to the image file or URL. Relative paths must start with `/` and
                 resolve to files in the `assets/` directory. Example: `/xxx.png` refers to
                 `assets/xxx.png`.
            alt: Alternative text for accessibility and SEO when the image cannot be displayed.
            width: Width of the image in pixels or percentage (e.g., `300` or `"100%"`).
            height: Height of the image in pixels or percentage (e.g., `200` or `"50%"`).
            title: Tooltip text displayed when hovering over the image.
            srcset: Comma-separated list of image URLs with descriptors for responsive design.
            sizes: Media query conditions to define image size based on viewport width.
            loading: Specifies whether the image should load lazily (`"lazy"`) or eagerly (`"eager"`).

        Example:
        .. code-block:: python
            # Renders <img src="/xxx.png" alt="Example Image" width="300" height="200">
            html.image("/xxx.png", alt="Example Image", width=300, height=200)
        """
        super().__init__("img")

        if src is not None:
            if isinstance(src, ElementBindingMixin):
                src = _src_utils.complete_src_computed(src)
            else:
                src = _src_utils.complete_src(src)

        self.props(
            {
                "src": src,
                "alt": alt,
                "width": width,
                "height": height,
                "title": title,
                "srcset": srcset,
                "sizes": sizes,
                "loading": loading,
            }
        )
