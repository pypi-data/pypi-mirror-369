from typing import List, Literal, Optional, Sequence, Union, cast, Tuple

TSystemModifiers = Literal["ctrl", "shift", "alt", "meta"]
TModifierGuards = Literal[
    "shift",
    "ctrl",
    "alt",
    "meta",
    "left",
    "right",
    "stop",
    "prevent",
    "self",
    "middle",
    "exact",
]
TCompatModifiers = Literal["esc", "space", "up", "left", "right", "down", "delete"]

TOtherModifier = Literal["passive", "capture", "once"]


TEventModifier = Union[
    TSystemModifiers, TModifierGuards, TCompatModifiers, TOtherModifier
]


def parse_event_modifiers(
    event_name: str,
    org_modifier: Optional[List[TEventModifier]] = None,
) -> Tuple[str, Optional[Sequence[TEventModifier]]]:
    """Parse event name and modifiers from both event_name string and org_modifier list.

    Args:
        event_name: Event name string, may contain modifiers separated by dots (e.g. 'click.stop')
        org_modifier: Optional list of additional modifiers

    Returns:
        Tuple of (cleaned_event_name, combined_modifiers) where:
            - cleaned_event_name: event name without modifiers
            - combined_modifiers: tuple of unique modifiers from both sources
    """
    parts = event_name.split(".")
    base_name = parts[0]
    modifiers = [m.strip() for m in parts[1:]] if len(parts) > 1 else []

    if not org_modifier and not modifiers:
        return base_name, None

    combined = set(modifiers)
    if org_modifier:
        combined.update(org_modifier)

    return base_name, cast(
        Sequence[TEventModifier], tuple(combined)
    ) if combined else None
