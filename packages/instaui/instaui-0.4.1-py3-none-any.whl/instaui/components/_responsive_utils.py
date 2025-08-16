from typing import Mapping
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


def gen_responsive_props(props: Mapping):
    """
    def __init__(
        self,
        **kwargs: Unpack[TFlexProps],
    ):
        super().__init__("flex")

        self.props(gen_responsive_props(kwargs))
    """
    binding_props = {}
    static_props = {}

    for key, value in props.items():
        if value is None:
            continue
        if isinstance(value, ElementBindingMixin):
            binding_props[key] = value._to_element_binding_config()
        else:
            static_props[key] = value

    layout_props = {}

    if static_props:
        layout_props["props"] = static_props

    if binding_props:
        layout_props["bind"] = binding_props

    if not layout_props:
        return {}

    return {"_resp": layout_props}
