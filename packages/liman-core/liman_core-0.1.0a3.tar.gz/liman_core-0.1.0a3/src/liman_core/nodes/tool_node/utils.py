from __future__ import annotations

from typing import Annotated, Any, TypedDict, cast

from pydantic import Field

from liman_core.errors import InvalidSpecError
from liman_core.languages import (
    LanguageCode,
    LocalizationError,
    flatten_dict,
    get_localized_value,
)
from liman_core.nodes.tool_node.schemas import ToolArgument, ToolObjectArgument


class ToolArgumentJSONSchema(TypedDict, total=False):
    """
    TypedDict for JSON Schema representation of a tool argument.
    """

    type: str | None
    any_of: Annotated[list[dict[str, Any]], Field(alias="anyOf")] | None
    description: str | None
    properties: dict[str, ToolArgumentJSONSchema] | None


def tool_arg_to_jsonschema(
    spec: ToolArgument | ToolObjectArgument,
    default_lang: LanguageCode,
    fallback_lang: LanguageCode,
) -> dict[str, ToolArgumentJSONSchema]:
    """
    Convert a tool specification to JSON Schema format.

    Args:
        spec (ToolArgument | ToolObjectArgument): The tool specification model.

    Returns:
        dict[str, Any]: The JSON Schema representation of the tool specification.
    """
    name = spec.name
    try:
        desc_bundle = spec.description
        if desc_bundle:
            desc = get_localized_value(desc_bundle, default_lang, fallback_lang)
        else:
            desc = ""
    except LocalizationError as e:
        raise InvalidSpecError(f"Invalid description in tool specification: {e}") from e

    if isinstance(desc, dict):
        desc_str = flatten_dict(desc)
    elif isinstance(desc, str):
        desc_str = desc
    else:
        raise InvalidSpecError(
            f"Invalid description type in tool specification: {type(desc).__name__}"
        )

    type_ = get_tool_arg_type(spec.type)
    params: ToolArgumentJSONSchema = {"description": desc_str}

    if isinstance(type_, list):
        params["any_of"] = [{"type": t} for t in type_]
    else:
        params["type"] = type_

    if isinstance(spec, ToolObjectArgument):
        properties = {}
        for property_ in spec.properties or []:
            properties.update(
                tool_arg_to_jsonschema(property_, default_lang, fallback_lang)
            )
        params["properties"] = properties

    return {name: params}


def get_tool_arg_type(type_: str | list[str]) -> str | list[str]:
    if isinstance(type_, list):
        return cast(list[str], [get_tool_arg_type(t) for t in type_])

    match type_:
        case "string" | "number" | "boolean":
            # For primitive types, we can directly use the type as a string
            ...
        case "str":
            type_ = "string"
        case "integer":
            type_ = "number"
        case "int":
            type_ = "number"
        case "float":
            type_ = "number"
        case "bool":
            type_ = "boolean"
        case "object":
            type_ = "object"
        case "array":
            raise NotImplementedError("Array type is not supported yet.")
        case _:
            raise InvalidSpecError(f"Unsupported type in tool specification: {type_}")
    return type_


def noop(*args: Any, **kwargs: Any) -> None:
    """A no-operation function that does nothing."""
    pass
