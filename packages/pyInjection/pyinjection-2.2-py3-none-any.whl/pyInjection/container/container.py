from abc import ABCMeta
from functools import wraps
from inspect import Signature, signature
from typing import (  # type: ignore
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    Type,
    _GenericAlias,
)

from ..container.container_instance import ContainerInstance
from ..scope_managers import SingletonScopeManager, TransientScopeManager
from ..validators.decorator_validator import DecoratorValidator
from ..validators.primitive_dependency_validator import PrimitiveDependencyValidator


class Container:
    base_types: List[Type[Any]] = [type(type), ABCMeta, _GenericAlias]
    _containers: Dict[str, "ContainerInstance"] = {}

    @staticmethod
    def get_instance(container_identifier: str = "default") -> ContainerInstance:
        if container_identifier not in Container._containers:
            Container._containers[container_identifier] = ContainerInstance(
                validators=[PrimitiveDependencyValidator(), DecoratorValidator()],
                scope_managers=[
                    TransientScopeManager(base_types=Container.base_types),
                    SingletonScopeManager(base_types=Container.base_types),
                ],
                base_types=Container.base_types,
            )
        return Container._containers[container_identifier]

    @staticmethod
    def inject(implementation: Callable[..., Any], container_identifier: str = "default") -> Callable[..., Any]:
        @wraps(implementation)
        def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
            if len(kwargs) == 0:
                sig: Signature = signature(implementation)
                if len(sig.parameters) != len(args):
                    for p in sig.parameters:
                        if p != "self":
                            instance = Container.resolve(sig.parameters[p].annotation, container_identifier=container_identifier)
                            kwargs[p] = instance
            return implementation(*args, **kwargs)
        return wrapper

    @staticmethod
    def add_transient(interface: Type[Any], implementation: Any, container_identifier: str = "default") -> None:
        Container.get_instance(container_identifier).add_transient(interface=interface, implementation=implementation)

    @staticmethod
    def add_singleton(interface: Type[Any], implementation: Any, container_identifier: str = "default") -> None:
        Container.get_instance(container_identifier).add_singleton(interface=interface, implementation=implementation)

    @staticmethod
    def resolve(interface: Type[Any], container_identifier: str = "default") -> Any:
        return Container.get_instance(container_identifier).resolve(interface=interface)

    @staticmethod
    def validate(container_identifier: str = "default") -> None:
        Container.get_instance(container_identifier).validate()
