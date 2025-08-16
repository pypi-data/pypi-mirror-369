import asyncio
import inspect
from collections.abc import Callable
from functools import reduce
from importlib import import_module
from typing import Any, cast

from langchain_core.messages import ToolMessage

from liman_core.errors import InvalidSpecError
from liman_core.languages import LanguageCode, flatten_dict
from liman_core.nodes.base.node import BaseNode
from liman_core.nodes.tool_node.schemas import ToolCall, ToolNodeSpec, ToolNodeState
from liman_core.nodes.tool_node.utils import (
    ToolArgumentJSONSchema,
    noop,
    tool_arg_to_jsonschema,
)
from liman_core.registry import Registry

DEFAULT_TOOL_PROMPT_TEMPLATE = """
{name} - {description}
{triggers}
""".strip()


class ToolNode(BaseNode[ToolNodeSpec, ToolNodeState]):
    """
    Represents a tool node in a directed graph.
    This node can be used to execute specific tools or functions within a workflow.

    YAML example:
    ```
    kind: ToolNode
    name: get_weather
    description:
      en: |
        This tool retrieves the current weather for a specified location.
      ru: |
        Эта функция получает текущую погоду для указанного местоположения.
    func: lib.tools.get_weather
    arguments:
      - name: lat
        type: float
        description:
          en: latitude of the location
          ru: широта местоположения (latitude)
      - name: lon
        type: float
        description:
          en: longitude of the location
          ru: долгота местоположения (longitude)
    # Optionally, you can specify example triggers for the tool.
    triggers:
      en:
        - What's the weather in New York?
      ru:
        - Какая погода в Нью-Йорке?
    # Optionally, you can specify a template for the tool prompt.
    # It will allow to improve tool execution accuracy.
    # supported only {name}, {description} and {triggers} variables.
    tool_prompt_template:
      en: |
        {name} - {description}
        Examples:
          {triggers}
      ru: |
        {name} - {description}
        Примеры:
          {triggers}
    ```

    Usage:
    ```yaml
    kind: LLMNode
    ...
    tools:
      - get_weather
      - another_tool
    ```
    """

    spec_type = ToolNodeSpec
    state_type = ToolNodeState

    def __init__(
        self,
        spec: ToolNodeSpec,
        registry: Registry,
        *,
        initial_data: dict[str, Any] | None = None,
        yaml_path: str | None = None,
        strict: bool = False,
        default_lang: str = "en",
        fallback_lang: str = "en",
    ) -> None:
        super().__init__(
            spec,
            registry,
            initial_data=initial_data,
            yaml_path=yaml_path,
            strict=strict,
            default_lang=default_lang,
            fallback_lang=fallback_lang,
        )

        self.registry = registry
        self.registry.add(self)
        self.func: Callable[..., Any] | None = None
        self._compiled = False

    def compile(self) -> None:
        self.func = self._load_func()
        self._compiled = True

    def set_func(self, func: Callable[..., Any]) -> None:
        """
        Set the function to be executed by the tool node.
        This function should match the signature defined in the tool node specification.
        """
        self.func = func
        self.spec.func = str(func)

    async def invoke(
        self, tool_call: ToolCall, state: dict[str, Any] | None = None
    ) -> ToolMessage:
        """
        Asynchronously invoke the tool function with the provided arguments.

        Args:
            tool_call: Tool call dict with structure like {'name': 'tool_name', 'args': {...}, 'id': '...', 'type': 'tool_call'}

        Returns:
            ToolMessage with function result and proper tool call metadata
        """
        if not self.func:
            raise ValueError(
                f"ToolNode {self.name} has no function set. Please compile the node first."
            )
        func = self.func
        tool_call_id = tool_call.id_
        tool_call_name = tool_call.name
        call_args = self._extract_function_args(tool_call.args)

        try:
            if asyncio.iscoroutinefunction(func) or (
                callable(func)
                and not inspect.isfunction(func)
                and asyncio.iscoroutinefunction(getattr(func, "__call__", None))
            ):
                result = await func(**call_args)
            else:
                result = func(**call_args)
        except Exception as e:
            response = ToolMessage(
                content=str(e),
                tool_call_id=tool_call_id,
                name=tool_call.name,
            )
        else:
            response = ToolMessage(
                content=str(result),
                tool_call_id=tool_call_id,
                name=tool_call_name,
            )
        return response

    def _extract_function_args(self, args_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Extract function arguments based on function signature from provided args dict.

        Args:
            args_dict: Dictionary containing all available arguments

        Returns:
            Dictionary with only the arguments that match function signature
        """
        if not hasattr(self, "func") or self.func is None:
            return args_dict

        sig = inspect.signature(self.func)
        filtered_args = {}

        for param_name, param in sig.parameters.items():
            if param_name in args_dict:
                filtered_args[param_name] = args_dict[param_name]
            elif param.default is not inspect.Parameter.empty:
                continue
            else:
                raise ValueError(f"Required parameter is missing: '{param_name}'")

        return filtered_args

    def _load_func(self) -> Callable[..., Any]:
        if self.func is not None and str(self.func) == self.spec.func:
            return self.func

        if not self.spec.func:
            raise InvalidSpecError(
                f"ToolNode '{self.name}' must have a 'func' attribute defined."
            )

        try:
            func_path = self.spec.func.split(".")
            module = import_module(".".join(func_path[:-1]))
            func = getattr(module, func_path[-1])
            if not callable(func):
                raise ValueError(
                    f"Function '{self.spec.func}' is not callable or does not exist."
                )
            return cast(Callable[..., Any], func)
        except (ImportError, ValueError) as e:
            if self.strict:
                raise InvalidSpecError(
                    f"Failed to import module for function '{self.spec.func}': {e}"
                ) from e
            return noop

    def get_tool_description(self, lang: LanguageCode) -> str:
        if not self.spec.description:
            return ""
        template = self._get_tool_prompt_template(lang)

        description = self.spec.description.get(lang) or self.spec.description.get(
            self.fallback_lang, ""
        )
        if isinstance(description, dict):
            # Flatten the description dictionary if it contains nested structures
            description = flatten_dict(description)

        triggers = [
            trigger.get(lang) or trigger.get(self.fallback_lang, "")
            for trigger in (self.spec.triggers or [])
        ]
        triggers_str = "\n".join(
            f"- {trigger}" for trigger in triggers if trigger.strip()
        )

        return template.format(
            name=self.name,
            description=description,
            triggers=triggers_str,
        ).strip()

    def get_json_schema(self, lang: LanguageCode | None = None) -> dict[str, Any]:
        if lang is None:
            lang = self.default_lang

        if self.spec.description:
            desc = self.spec.description.get(lang)
            if not desc:
                # Fallback to the default language if the specified language is not available
                desc = self.spec.description.get(self.fallback_lang)
                if not desc:
                    raise InvalidSpecError("Spec doesn't have a description.")
            if isinstance(desc, dict):
                # Flatten the description dictionary if it contains nested structures
                desc = flatten_dict(desc)
        else:
            desc = ""

        args = [
            tool_arg_to_jsonschema(arg, self.default_lang, self.fallback_lang)
            for arg in self.spec.arguments or []
        ]
        properties: dict[str, ToolArgumentJSONSchema] = reduce(
            lambda acc, arg: acc | arg, args, {}
        )

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": desc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": [
                        arg.name
                        for arg in self.spec.arguments or []
                        if not arg.optional
                    ],
                },
            },
        }

    def get_new_state(self) -> ToolNodeState:
        """
        Get a new state for the ToolNode.

        Returns:
            ToolNodeState: A new instance of ToolNodeState.
        """
        return ToolNodeState(kind=self.spec.kind, name=self.spec.name)

    def _get_tool_prompt_template(self, lang: LanguageCode) -> str:
        """
        Get the tool prompt template from the declaration or use the default template.
        """
        tool_prompt_template = self.spec.tool_prompt_template
        if not tool_prompt_template:
            return DEFAULT_TOOL_PROMPT_TEMPLATE

        if hasattr(tool_prompt_template, lang):
            template = tool_prompt_template[lang]
            if not isinstance(template, str):
                raise InvalidSpecError(
                    f"Tool prompt template for language '{lang}' must be a string, got {type(template).__name__}."
                )
            return template

        if hasattr(tool_prompt_template, self.fallback_lang):
            template = tool_prompt_template[self.fallback_lang]
            if not isinstance(template, str):
                raise InvalidSpecError(
                    f"Tool prompt template for fallback language '{self.fallback_lang}' must be a string, got {type(template).__name__}."
                )

        return DEFAULT_TOOL_PROMPT_TEMPLATE
