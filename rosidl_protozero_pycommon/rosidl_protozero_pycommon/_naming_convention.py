from typing import Iterable

from abc import ABC, abstractmethod

from .utils import not_none

class NamingConvention(ABC):
    @abstractmethod
    def struct(self, message_name: str) -> str:
        pass

    @abstractmethod
    def field(self, message_name: str, field_name: str) -> str:
        pass

    @staticmethod
    def constant(
            *components: Iterable[str or None],
            glue: str = '__',
    ) -> str:
        return glue.join(filter(not_none, components))
