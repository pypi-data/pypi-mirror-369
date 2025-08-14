from abc import ABC, abstractmethod
from typing import Any, Type


class IValidator(ABC):
    @abstractmethod
    def is_valid(self, interface: Type[Any], implementation: Any) -> bool:
        pass
