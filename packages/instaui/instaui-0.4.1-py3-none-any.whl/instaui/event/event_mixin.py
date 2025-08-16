from abc import ABC, abstractmethod
import typing

from instaui.event.event_modifier import TEventModifier


class EventMixin(ABC):
    @abstractmethod
    def copy_with_extends(
        self,
        extends: typing.Optional[typing.Sequence],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ) -> "EventMixin":
        pass

    @abstractmethod
    def event_type(self) -> typing.Literal["web", "js"]:
        pass
