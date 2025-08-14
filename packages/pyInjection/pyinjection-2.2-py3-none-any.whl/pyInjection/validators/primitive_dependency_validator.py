from inspect import Signature, signature
from typing import Any, Callable, List, Type

from ..interfaces.ivalidator import IValidator


class PrimitiveDependencyValidator(IValidator):
    def is_valid(self, interface: Type[Any], implementation: Any) -> bool:
        implementation_type: Type[Any] = type(implementation)
        if implementation_type is type(type):
            # Not a Concrete implementation - therefore cannot have primitive
            return not self.has_primitive_dependency(value=implementation)
        elif implementation_type is type(lambda: ""):
            return True
        else:
            return True

    def has_primitive_dependency(self, value: Callable[..., Any]) -> bool:
        sig: Signature = signature(value)
        for parameter_key in sig.parameters:
            if self.is_primitive(sig.parameters[parameter_key].annotation):
                return True
        return False

    def is_primitive(self, value: Type[Any]) -> bool:
        primitive_types: List[Type[Any]] = [int, str, bool, float, complex]
        return primitive_types.__contains__(value)
