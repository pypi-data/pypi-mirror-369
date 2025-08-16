from typing import Any, Dict, List, Optional, Sequence, Union, cast
from instaui.common.jsonable import Jsonable
from instaui.missing import TMissing
from instaui.vars.mixin_types.py_binding import CanOutputMixin, CanInputMixin


def _check_args(config: Dict):
    for key in config.keys():
        if not isinstance(key, CanOutputMixin):
            raise TypeError(f"key {key} is not a CanOutputMixin")


def convert_list2list(pre_setup: Optional[List]) -> List:
    if not pre_setup:
        return []

    first = pre_setup[0]
    # e.g [ref, True, False]
    if not isinstance(first, list):
        return [pre_setup]

    # e.g [[ref, True, False], [ref2, False, True]]
    return pre_setup


def convert_config(configs: List[List]):
    return [
        [
            cast(CanInputMixin, target)._to_input_config(),
            _to_config_value(running_value),
            _to_config_value(reset_value),
        ]
        for target, running_value, reset_value in configs
    ]


def _to_config_value(maybe_action: Union[Any, TMissing]) -> Any:
    if isinstance(maybe_action, TMissing):
        return {
            "type": "missing",
        }

    if isinstance(maybe_action, PreSetupAction):
        return {
            "type": "action",
            "value": maybe_action._to_json_dict(),
        }

    return {"type": "const", "value": maybe_action}


class PreSetupAction(Jsonable):
    def __init__(
        self,
        *,
        code: str,
        inputs: Optional[Sequence] = None,
    ):
        self.type = "action"
        self._inputs = inputs
        self.code = code

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self._inputs:
            data["inputs"] = [
                binding._to_input_config()
                if isinstance(binding, CanInputMixin)
                else binding
                for binding in self._inputs
            ]

        return data
