# -- __all__
__all__ = [
    "__version__",
    "TMaybeRef",
    "MISSING",
    "TMissing",
    "TBindable",
    "is_bindable",
    "slient",
    "data",
    "TConstData",
    "vue_computed",
    "TVueComputed",
    "js_computed",
    "TJsComputed",
    "computed",
    "TComputed",
    "state",
    "StateModel",
    "local_storage",
    "session_storage",
    "use_dark",
    "inject_state",
    "provide_state",
    "injection_key",
    "TVForItem",
    "TVForIndex",
    "element_ref",
    "run_element_method",
    "to_json",
    "to_config_data",
    "element",
    "vfor",
    "iter_info",
    "content",
    "add_style",
    "add_css_link",
    "remove_css_link",
    "add_js_code",
    "add_js_link",
    "add_vue_app_use",
    "use_tailwind",
    "use_page_title",
    "directive",
    "vif",
    "page",
    "event",
    "js_event",
    "vue_event",
    "event_context",
    "TEventFn",
    "server",
    "context",
    "row",
    "grid",
    "container",
    "text",
    "theme",
    "heading",
    "watch",
    "vue_watch",
    "js_watch",
    "js_fn",
    "TWatchState",
    "match",
    "column",
    "experimental",
    "skip_output",
    "str_format",
    "pre_setup_action",
    "patch_set",
    "on_page_request_lifespan",
    "webview",
    "code",
    "markdown",
    "echarts",
    "use_shadcn_classless",
    "mermaid",
    "timer",
    "teleport",
    "icon",
    "box",
    "flex",
    "image",
    "video",
]

# -- static imports
from instaui.version import __version__
from instaui.vars.types import TMaybeRef
from instaui.missing import MISSING, TMissing

from instaui.vars.data import ConstData as data, TConstData
from instaui.vars.js_computed import JsComputed as js_computed, TJsComputed
from instaui.vars.vue_computed import VueComputed as vue_computed, TVueComputed
from instaui.vars.web_computed import web_computed as computed, TComputed
from instaui.vars.state import state, StateModel
from instaui.vars.local_storage import local_storage
from instaui.vars.session_storage import session_storage
from instaui.vars.use_dark import use_dark
from instaui.inject import inject_state, provide_state, injection_key
from instaui.vars.vfor_item import TVForItem, TVForIndex
from instaui.vars.element_ref import ElementRef as element_ref, run_element_method
from instaui.html_tools import (
    to_json,
    add_css_link,
    remove_css_link,
    add_js_link,
    add_style,
    add_js_code,
    add_vue_app_use,
    to_config_data,
    use_tailwind,
    use_page_title,
)

from instaui.components.element import Element as element
from instaui.components.heading import Heading as heading
from instaui.components.directive import Directive as directive
from instaui.components.vfor import VFor as vfor, iter_info
from instaui.components.vif import VIf as vif
from instaui.components.match import Match as match
from instaui.components.content import Content as content
from instaui.components.timer.timer import Timer as timer
from instaui.components.teleport import teleport
from instaui.components.icon import Icon as icon
from instaui.components.layout.box import Box as box
from instaui.components.layout.flex import (
    Flex as flex,
    FlexRow as row,
    FlexColumn as column,
)
from instaui.components.layout.grid import Grid as grid
from instaui.components.layout.container import Container as container
from instaui.components.text import Text as text
from instaui.components.theme import Theme as theme

from instaui.event.web_event import event, WebEvent as TEventFn
from instaui.event.js_event import js_event
from instaui.event.vue_event import vue_event
from instaui.vars.event_context import EventContext as event_context
from instaui.runtime.context import get_context as context

from instaui.watch.web_watch import watch
from instaui.watch.vue_watch import vue_watch
from instaui.watch.js_watch import js_watch
from instaui.handlers.watch_handler import WatchState as TWatchState
from instaui.skip import skip_output
from instaui.ui_functions.input_slient_data import InputSilentData as slient
import instaui.experimental as experimental

from instaui.ui_functions.server import create_server as server
from instaui.ui_functions.ui_page import page
from instaui.ui_functions.str_format import str_format
from instaui.ui_functions.ui_types import TBindable, is_bindable

from ._events import on_page_request_lifespan
from instaui.extra_libs._import_error import show_error  # noqa: E402, F401
from instaui.js.fn import JsFn as js_fn
from instaui.pre_setup import PreSetupAction as pre_setup_action
from instaui.patch_update import patch_set
from instaui.components.html.image import Image as image
from instaui.components.html.video import Video as video

# -- dynamic imports
from instaui.components.markdown.markdown import Markdown as markdown
from instaui.webview import WebviewWrapper as webview
from instaui.shadcn_classless._index import use_shadcn_classless

# -- extra libs
# mermaid = _LazyModule('instaui.extra_libs._mermaid', 'mermaid', import_error_callback=show_error('Mermaid is not installed. Please run "pip install instaui-mermaid" to install it.'),)
from instaui_mermaid import Mermaid as mermaid  # type: ignore

# code = _LazyModule('instaui.extra_libs._shiki_code', 'code', import_error_callback=show_error('Shiki is not installed. Please run "pip install instaui-shiki" to install it.'),)
from instaui_shiki import shiki as code  # type: ignore

# echarts = _LazyModule('instaui.extra_libs._echarts', 'echarts', import_error_callback=show_error('Echarts is not installed. Please run "pip install instaui-echarts" to install it.'),)
from instaui_echarts import echarts  # type: ignore
