from instaui.vars._types import OutputSetType
from instaui.vars.mixin_types.py_binding import CanOutputMixin


class JsOutput(CanOutputMixin):
    def _to_output_config(self):
        return {"type": "js"}

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.JsCode
