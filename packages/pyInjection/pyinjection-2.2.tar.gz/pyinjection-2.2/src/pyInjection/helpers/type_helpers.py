import re
from typing import Any, List, Type


class TypeHelpers:
    @staticmethod
    def to_string(input_type: Type[Any]) -> str:
        return_string: str = ""
        type_string: str = str(input_type)
        ## Generic Split
        generic_split: List[str] = type_string.split("[")
        max_generic_index: int = len(generic_split)
        for index, token in enumerate(generic_split):
            token_split: List[str] = token.split(".")
            class_string: str = re.sub("'|>|]", "", token_split[-1])

            if max_generic_index > 1:
                ## Nested
                if index == max_generic_index - 1:
                    closing_brackets: str = "]" * (max_generic_index - 1)
                    return_string = f"{return_string}{class_string}{closing_brackets}"
                else:
                    return_string = f"{return_string}{class_string}["
            else:
                return_string = class_string
        return f"{return_string}"
