from inspect import Signature, signature
from typing import Any, Callable, Type

from ..interfaces.ivalidator import IValidator


# Check that the registration does not require resolving the same base type
# if it does - it should be a decorator and therefore registered as a Lambda or a Concrete implementation
class DecoratorValidator(IValidator):
    def is_valid(self, interface: Type[Any], implementation: Callable[..., Any]) -> bool:
        implementation_type: Type[Any] = type(implementation)
        if implementation_type is type(type):
            return not self.has_parameter_of_return_type(
                interface=interface, implementation=implementation
            )
        elif implementation_type is type(lambda: ""):
            return True
        else:
            return True

    def has_parameter_of_return_type(
        self, interface: Type[Any], implementation: Callable[..., Any]
    ) -> bool:
        sig: Signature = signature(implementation)
        for parameter_key in sig.parameters:
            if interface == sig.parameters[parameter_key].annotation:
                return True
        return False
