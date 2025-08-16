import inspect
import typing
from typing_extensions import ParamSpec
from instaui.common.jsonable import Jsonable
from instaui.event.event_modifier import TEventModifier
from instaui.runtime._app import get_current_scope, get_app_slot
from instaui.vars.mixin_types.py_binding import (
    CanInputMixin,
    CanOutputMixin,
    _assert_outputs_be_can_output_mixin,
    inputs_to_config,
    outputs_to_config,
)
from instaui.handlers import event_handler
from instaui import pre_setup as _pre_setup
from .event_mixin import EventMixin


_SYNC_TYPE = "sync"
_ASYNC_TYPE = "async"

P = ParamSpec("P")
R = typing.TypeVar("R")


class WebEvent(Jsonable, EventMixin, typing.Generic[P, R]):
    def __init__(
        self,
        fn: typing.Callable[P, R],
        inputs: typing.Sequence[CanInputMixin],
        outputs: typing.Sequence[CanOutputMixin],
        pre_setup: typing.Optional[typing.List] = None,
        modifier: typing.Optional[typing.Sequence[TEventModifier]] = None,
    ):
        # if pre_setup:
        #     _pre_setup._check_args(pre_setup)

        _assert_outputs_be_can_output_mixin(outputs)

        self._inputs = inputs
        self._outputs = outputs
        self._fn = fn
        self._pre_setup = _pre_setup.convert_list2list(pre_setup)
        self._modifier = modifier

        scope = get_current_scope()
        self._sid = scope.id

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._fn(*args, **kwargs)

    def copy_with_extends(
        self,
        extends: typing.Optional[typing.Sequence[CanInputMixin]],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ):
        if extends is None and modifier is None:
            return self

        inputs = list(self._inputs)
        if extends is not None:
            inputs = inputs + list(extends)

        return WebEvent(
            fn=self._fn,
            inputs=inputs,
            outputs=self._outputs,
            modifier=modifier,
        )

    def event_type(self):
        return "web"

    def _to_json_dict(self):
        app = get_app_slot()

        hkey = event_handler.create_handler_key(
            page_path=app.page_path, handler=self._fn
        )

        event_handler.register_event_handler(
            hkey, self._fn, self._outputs, self._inputs
        )

        data = {}
        data["type"] = self.event_type()
        data["fType"] = (
            _ASYNC_TYPE if inspect.iscoroutinefunction(self._fn) else _SYNC_TYPE
        )
        data["hKey"] = hkey
        data["sid"] = self._sid

        if self._inputs:
            data["inputs"] = inputs_to_config(self._inputs)

        if self._outputs:
            data["sets"] = outputs_to_config(self._outputs)

        if self._pre_setup:
            data["preSetup"] = _pre_setup.convert_config(self._pre_setup)

        if self._modifier:
            data["modifier"] = self._modifier

        return data


def event(
    *,
    inputs: typing.Optional[typing.Sequence] = None,
    outputs: typing.Optional[typing.Sequence] = None,
    pre_setup: typing.Optional[typing.List] = None,
):
    """
    Creates an event handler decorator for binding reactive logic to component events.

    Args:
        inputs (typing.Optional[typing.Sequence], optional): Reactive sources (state objects, computed properties)
                                   that should be accessible during event handling.
                                   These values will be passed to the decorated function
                                   when the event fires.
        outputs (typing.Optional[typing.Sequence], optional): Targets (state variables, UI elements) that should
                                    update when this handler executes. Used for coordinating
                                    interface updates after the event is processed.
        pre_setup (typing.Optional[typing.List], optional): A list of pre-setup actions to be executed before the event executes.


    # Example:
    .. code-block:: python
        from instaui import ui, html

        a = ui.state(0)

        @ui.event(inputs=[a], outputs=[a])
        def plus_one(a):
            return a + 1

        html.button("click me").on_click(plus_one)
        html.paragraph(a)

    use pre_setup:
    .. code-block:: python
        a = ui.state(0)
        task_running = ui.state(False)

        @ui.event(inputs=[a], outputs=[a], pre_setup=[task_running,True,False])
        async def long_running_task(a):
            await asyncio.sleep(3)
            return a + 1

        html.button("click me").on_click(long_running_task).disabled(task_running)
    """

    def wrapper(func: typing.Callable[P, R]):
        return WebEvent(
            func,
            inputs or [],
            outputs=outputs or [],
            pre_setup=pre_setup,
        )

    return wrapper
