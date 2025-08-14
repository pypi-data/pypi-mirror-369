#  Copyright 2024 Palantir Technologies, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import atexit
from typing import Any, Callable, List, Optional

from .function_registry.function import Function
from .function_registry.function_registry import add_function
from .startup import start_compute_module


def function(
    maybe_func: Any = None,
    *,
    streaming: bool = False,
    edits: Optional[List[Any]] = None,
) -> Callable[..., Any]:
    def function_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        add_function(func, streaming=streaming, edits=edits)
        return Function(func, [] if edits is None else edits)

    if callable(maybe_func):
        return function_wrapper(maybe_func)
    return function_wrapper


# Register the on_exit function to be called when the interpreter exits
atexit.register(start_compute_module)

__all__ = [
    "function",
]
