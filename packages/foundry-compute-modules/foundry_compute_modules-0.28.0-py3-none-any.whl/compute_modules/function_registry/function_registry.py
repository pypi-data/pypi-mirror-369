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


from typing import Any, Callable, Dict, List, Optional

from .function_schema_parser import parse_function_schema
from .types import ComputeModuleFunctionSchema, PythonClassNode

REGISTERED_FUNCTIONS: Dict[str, Callable[..., Any]] = {}
FUNCTION_SCHEMAS: List[ComputeModuleFunctionSchema] = []
FUNCTION_SCHEMA_CONVERSIONS: Dict[str, PythonClassNode] = {}
IS_FUNCTION_CONTEXT_TYPED: Dict[str, bool] = {}
STREAMING: Dict[str, bool] = {}


def add_functions(*args: Callable[..., Any]) -> None:
    for function_ref in args:
        add_function(function_ref=function_ref)


def add_function(
    function_ref: Callable[..., Any],
    *,
    streaming: bool = False,
    edits: Optional[List[Any]] = None,
) -> None:
    """Parse & register a Compute Module function"""
    function_name = function_ref.__name__
    parse_result = parse_function_schema(
        function_ref,
        function_name,
        edits=edits if edits is not None else [],
        # TODO: currently do not support runtime function inference for OntologyEdits.
        # Not sure if we will but would need to update here if we decide to do so
        api_name_type_id_mapping={},
    )
    _register_parsed_function(
        function_name=function_name,
        function_ref=function_ref,
        function_schema=parse_result.function_schema,
        function_schema_conversion=parse_result.class_node,
        is_context_typed=parse_result.is_context_typed,
        streaming=streaming,
    )


def _register_parsed_function(
    function_name: str,
    function_ref: Callable[..., Any],
    function_schema: ComputeModuleFunctionSchema,
    function_schema_conversion: Optional[PythonClassNode],
    is_context_typed: bool,
    streaming: bool,
) -> None:
    """Registers a Compute Module function"""
    REGISTERED_FUNCTIONS[function_name] = function_ref
    FUNCTION_SCHEMAS.append(function_schema)
    IS_FUNCTION_CONTEXT_TYPED[function_name] = is_context_typed
    STREAMING[function_name] = streaming
    if function_schema_conversion is not None:
        FUNCTION_SCHEMA_CONVERSIONS[function_name] = function_schema_conversion
