from typing import Any, Dict, List, Type

from ..dtos import Registration, SignatureParameter
from ..enums import Scope
from ..helpers import ContainerHelpers, TypeHelpers
from ..interfaces import IScopeManager


class TransientScopeManager(IScopeManager):
    __base_types: List[Type[Any]]

    def __init__(self, base_types: List[Type[Any]]) -> None:
        self.__base_types = base_types

    def can_resolve(self, scope: Scope) -> bool:
        return scope == Scope.TRANSIENT

    def is_same_registration_scope_v2(
        self,
        interface: Type[Any],
        child_interface: Type[Any],
        container: Dict[Type[Any], Registration],
    ) -> None:
        registration: Registration = container[child_interface]
        if registration.scope != Scope.TRANSIENT:
            error_message: str = f"Error Transient type: {TypeHelpers.to_string(interface)} registered with Singleton dependency: {TypeHelpers.to_string(child_interface)}"
            raise Exception(error_message)

    def resolve_scope_decorator(self, interface: Type[Any], instance: Any) -> Any:
        return instance

    def resolve(self, interface: Type[Any], container: Dict[Type[Any], Registration], signature_store: Dict[Type[Any], List[SignatureParameter]]) -> Any:
        return ContainerHelpers.resolve(
            interface=interface,
            container=container,
            signature_store=signature_store,
            is_same_registration_scope=self.is_same_registration_scope_v2,
            resolve_scope_decorator=self.resolve_scope_decorator,
            base_types=self.__base_types,
        )
