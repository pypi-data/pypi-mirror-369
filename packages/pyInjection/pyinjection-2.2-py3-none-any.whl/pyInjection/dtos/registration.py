from typing import Any

from ..enums import Scope


class Registration:
    __implementation: Any
    __scope: Scope

    def __init__(self, implementation: Any, scope: Scope):
        self.__implementation = implementation
        self.__scope = scope

    @property
    def implementation(self) -> Any:
        return self.__implementation

    @property
    def scope(self) -> Scope:
        return self.__scope
