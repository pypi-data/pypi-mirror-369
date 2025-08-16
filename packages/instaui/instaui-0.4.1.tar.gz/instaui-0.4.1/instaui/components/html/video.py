from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Optional
from instaui.components.element import Element
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from . import _src_utils


if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Video(Element):
    def __init__(
        self,
        src: Optional[TMaybeRef[str]] = None,
        *,
        controls: Optional[TMaybeRef[bool]] = None,
        autoplay: Optional[TMaybeRef[bool]] = None,
        loop: Optional[TMaybeRef[bool]] = None,
        muted: Optional[TMaybeRef[bool]] = None,
        playsinline: Optional[TMaybeRef[bool]] = None,
        poster: Optional[TMaybeRef[str]] = None,
        preload: Optional[TMaybeRef[Literal["auto", "metadata", "none"]]] = None,
    ):
        """
        Creates an HTML video element with configurable playback options.

        Args:
            src (Optional[TMaybeRef[str]]): The URL or path to the video file.
                - If a relative path is provided (e.g., "/xxx.mp4"), it will resolve
                to the `assets` directory in the application root.
                - Absolute URLs (e.g., "https://example.com/video.mp4") are also supported.
            controls (Optional[TMaybeRef[bool]]): Whether to display browser-native video controls.
            autoplay (Optional[TMaybeRef[bool]]): Whether the video should start playing automatically.
            loop (Optional[TMaybeRef[bool]]): Whether the video should loop after reaching the end.
            muted (Optional[TMaybeRef[bool]]): Whether the video should be muted by default.
            playsinline (Optional[TMaybeRef[bool]]): Whether the video should play inline on mobile devices.
            poster (Optional[TMaybeRef[str]]): URL to an image shown as a placeholder before playback starts.
            preload (Optional[TMaybeRef[Literal["auto", "metadata", "none"]]]): Hints how much video data should be preloaded.

        Example:
        .. code-block:: python
            from instaui import ui

            # Play a video from the assets directory
            ui.video("/xxx.mp4", controls=True, autoplay=False)

            # Play a remote video with a custom poster image
            ui.video("https://example.com/video.mp4", poster="/thumbnail.jpg", muted=True)
        """
        super().__init__("video")
        if src is not None:
            if isinstance(src, ElementBindingMixin):
                src = _src_utils.complete_src_computed(src)
            else:
                src = _src_utils.complete_src(src)
        self.props(
            {
                "src": src,
                "controls": controls,
                "autoplay": autoplay,
                "loop": loop,
                "muted": muted,
                "playsinline": playsinline,
                "poster": poster,
                "preload": preload,
            }
        )
