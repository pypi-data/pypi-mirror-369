from typing import Any, Type


class SignatureParameter:
    __signature_name: str
    __signature_type: Type[Any]

    def __init__(self, signature_name: str, signature_type: Type[Any]):
        self.__signature_name = signature_name
        self.__signature_type = signature_type

    @property
    def signature_name(self) -> str:
        return self.__signature_name

    @property
    def signature_type(self) -> Type[Any]:
        return self.__signature_type
