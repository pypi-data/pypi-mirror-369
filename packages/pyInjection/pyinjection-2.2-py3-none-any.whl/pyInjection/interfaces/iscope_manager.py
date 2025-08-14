from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from ..dtos import Registration, SignatureParameter
from ..enums import Scope


class IScopeManager(ABC):
    @abstractmethod
    def can_resolve(self, scope: Scope) -> bool:
        pass

    @abstractmethod
    def resolve(self, interface: Type[Any], container: Dict[Type[Any], Registration], signature_store: Dict[Type[Any], List[SignatureParameter]]) -> Any:
        pass
