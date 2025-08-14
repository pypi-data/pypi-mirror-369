import copy
from inspect import (
    Signature,
    signature,
)
from typing import (  # type: ignore
    Any,
    Callable,
    Dict,
    List,
    Type,
    TypeVar,
    _GenericAlias,
    get_args,
    get_origin,
)

from ..dtos import Registration, SignatureParameter
from .type_helpers import TypeHelpers


class ContainerHelpers:
    ignore_parameters: List[str] = ["self", "args", "kwargs"]

    @staticmethod
    def resolve(
        interface: Type[Any],
        container: Dict[Type[Any], Registration],
        signature_store: Dict[Type[Any], List[SignatureParameter]],
        is_same_registration_scope: Callable[..., Any],
        resolve_scope_decorator: Callable[[Type[Any], Any], Any],
        base_types: List[Type[Any]],
    ) -> Any:
        error_message: str = ""
        if interface in container.keys():
            implementation: Any = container[interface].implementation
            if type(implementation) in base_types:
                if type(implementation) is _GenericAlias:
                    return resolve_scope_decorator(
                        interface,
                        ContainerHelpers.resolve_generic(
                            interface=interface,
                            container=container,
                            signature_store=signature_store,
                            is_same_registration_scope=is_same_registration_scope,
                            resolve_scope_decorator=resolve_scope_decorator,
                            base_types=base_types,
                        ),
                    )
                else:
                    kwargs: Any = {}
                    signature_parameters: List[SignatureParameter] = ContainerHelpers.get_genetic_signature_parameters(
                        implementation=implementation,
                        signature_collection=signature_store,
                    )
                    for signature_parameter in signature_parameters:
                        signature_type: Type[Any] = copy.deepcopy(signature_parameter.signature_type)
                        is_same_registration_scope(
                            interface=interface,
                            child_interface=signature_type,
                            container=container,
                        )
                        instance: Any = resolve_scope_decorator(
                            signature_type,
                            ContainerHelpers.resolve(
                                interface=signature_type,
                                container=container,
                                signature_store=signature_store,
                                is_same_registration_scope=is_same_registration_scope,
                                resolve_scope_decorator=resolve_scope_decorator,
                                base_types=base_types,
                            ),
                        )
                        kwargs[signature_parameter.signature_name] = instance
                    return implementation(**kwargs)
            elif type(implementation) is type(lambda: ""):
                return implementation()
            else:
                return implementation
        else:
            error_message = f"Cannot resolve type: {TypeHelpers.to_string(interface)}"
            raise Exception(error_message)

    @staticmethod
    def resolve_generic(
        interface: Type[Any],
        container: Dict[Type[Any], Registration],
        signature_store: Dict[Type[Any], List[SignatureParameter]],
        is_same_registration_scope: Callable[..., Any],
        resolve_scope_decorator: Callable[[Type[Any], Any], Any],
        base_types: List[Type[Any]],
    ) -> Any:
        implementation: Any = container[interface].implementation
        implementation_type: Type[Any] = get_origin(implementation) or implementation
        generic_class: Type[Any] = get_args(implementation)[0]
        kwargs: Any = {}

        signature_parameters: List[SignatureParameter] = ContainerHelpers.get_genetic_signature_parameters(
            implementation=implementation_type,
            signature_collection=signature_store,
        )
        for signature_parameter in signature_parameters:
                signature_type: Type[Any] = copy.deepcopy(signature_parameter.signature_type)
                if type(signature_type) is _GenericAlias:
                    child_interface_generic_type = signature_type.__args__[0]
                    if type(child_interface_generic_type) is TypeVar:
                        ## Need to rebuild type using the Generic Class and force a new object without reference
                        signature_type = signature_type.copy_with((generic_class,))
                is_same_registration_scope(
                    interface=interface,
                    child_interface=signature_type,
                    container=container,
                )
                instance: Any = resolve_scope_decorator(
                    signature_type,
                    ContainerHelpers.resolve(
                        interface=signature_type,
                        container=container,
                        signature_store=signature_store,
                        is_same_registration_scope=is_same_registration_scope,
                        resolve_scope_decorator=resolve_scope_decorator,
                        base_types=base_types,
                    ),
                )
                kwargs[signature_parameter.signature_name] = instance
        return implementation(**kwargs)

    @staticmethod
    def get_genetic_signature_parameters(
        implementation: Type[Any],
        signature_collection: Dict[Type[Any], List[SignatureParameter]],
    ) -> List[SignatureParameter]:
        if implementation not in signature_collection.keys():
            sig: Signature = signature(implementation)
            signature_collection[implementation] = [SignatureParameter(signature_name=p, signature_type=sig.parameters[p].annotation) for p in sig.parameters if p not in ContainerHelpers.ignore_parameters]
        return signature_collection[implementation]
