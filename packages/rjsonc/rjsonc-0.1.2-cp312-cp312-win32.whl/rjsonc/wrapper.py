from typing import Any, Union
from .rjsonc import loads_bytes, loads_str


def loads(s: Union[bytes, str]) -> Any:
    if isinstance(s, str):
        return loads_str(s)
    else:
        return loads_bytes(s)
