import typing
from instaui.event.event_modifier import TEventModifier
from instaui.vars.mixin_types.py_binding import (
    CanInputMixin,
    CanOutputMixin,
    inputs_to_config,
    outputs_to_config,
)
from instaui.common.jsonable import Jsonable
from .event_mixin import EventMixin


class JsEvent(Jsonable, EventMixin):
    def __init__(
        self,
        code: str,
        inputs: typing.Optional[typing.Sequence[CanInputMixin]] = None,
        outputs: typing.Optional[typing.Sequence[CanOutputMixin]] = None,
        modifier: typing.Optional[typing.Sequence[TEventModifier]] = None,
    ):
        self._is_const_data = [
            int(not isinstance(input, CanInputMixin)) for input in inputs or []
        ]
        self._org_inputs = list(inputs or [])
        self._org_outputs = list(outputs or [])
        self._inputs = inputs or []
        self._outputs = outputs or []
        self.code = code
        self._modifier = modifier

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["type"] = self.event_type()

        if self._inputs:
            data["inputs"] = inputs_to_config(self._inputs)

        if self._outputs:
            data["sets"] = outputs_to_config(self._outputs)

        if sum(self._is_const_data) > 0:
            data["data"] = self._is_const_data

        if self._modifier:
            data["modifier"] = self._modifier

        return data

    def copy_with_extends(
        self,
        extends: typing.Optional[typing.Sequence],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ):
        if extends is None and modifier is None:
            return self

        inputs = self._org_inputs
        if extends is not None:
            inputs = inputs + list(extends)

        return JsEvent(
            code=self.code,
            inputs=inputs,
            outputs=self._org_outputs,
            modifier=modifier,
        )

    def event_type(self):
        return "js"


def js_event(
    *,
    inputs: typing.Optional[typing.Sequence] = None,
    outputs: typing.Optional[typing.Sequence] = None,
    code: str,
):
    """
    Creates a client-side event handler decorator for binding JavaScript logic to UI component events.

    Args:
        inputs (typing.Optional[typing.Sequence], optional):Reactive sources (state variables, computed values)
                                   that should be passed to the event handler. These values
                                   will be available in the JavaScript context through the `args` array.
        outputs (typing.Optional[typing.Sequence], optional): Targets (state variables, UI elements) that should
                                    update when this handler executes. Used for coordinating
                                    interface updates after the event is processed.
        code (str): JavaScript code to execute when the event is triggered.

    # Example:
    .. code-block:: python
        from instaui import ui, html

        a = ui.state(0)

        plus_one = ui.js_event(inputs=[a], outputs=[a], code="a =>a + 1")

        html.button("click me").on_click(plus_one)
        html.paragraph(a)

    """
    return JsEvent(inputs=inputs, outputs=outputs, code=code)
