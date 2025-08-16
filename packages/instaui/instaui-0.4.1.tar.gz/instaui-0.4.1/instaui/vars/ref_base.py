from __future__ import annotations
from typing import Any, Dict, Optional
from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.path_var import PathVar
from instaui.missing import MISSING

from .mixin_types.var_type import VarMixin
from .mixin_types.py_binding import CanInputMixin, CanOutputMixin
from .mixin_types.observable import ObservableMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.pathable import CanPathPropMixin
from .mixin_types.str_format_binding import StrFormatBindingMixin


class RefBase(
    Jsonable,
    PathVar,
    VarMixin,
    ObservableMixin,
    CanInputMixin,
    CanOutputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
):
    def __init__(
        self,
        *,
        ref_type: Optional[str] = None,
        value: Optional[Any] = MISSING,
        deep_compare: bool = False,
        args: Optional[Dict] = None,
    ) -> None:
        scope = get_current_scope()
        self.__register_info = scope.register_ref_task(self)
        self._deep_compare = deep_compare
        self._value = value
        self._args = args
        self._ref_type = ref_type

    def __to_binding_config(self):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_output_config(self):
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__register_info.var_id

        if self._deep_compare is True:
            data["deepCompare"] = True

        if self._args:
            data["args"] = {k: v for k, v in self._args.items() if v is not None}

        if self._ref_type:
            data["type"] = self._ref_type

        if self._value is not MISSING:
            data["value"] = self._value

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref
