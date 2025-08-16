import asyncio
import logging
import sys
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, ToolMessage

from liman_core.base.schemas import S
from liman_core.conf import settings
from liman_core.edge.dsl.grammar import when_parser
from liman_core.edge.dsl.transformer import WhenTransformer
from liman_core.edge.schemas import EdgeSpec
from liman_core.node_actor.conditional_evaluator import ConditionalEvaluator
from liman_core.node_actor.errors import NodeActorError
from liman_core.node_actor.schemas import (
    NextNode,
    NodeActorStatus,
    Result,
)
from liman_core.nodes.base.node import BaseNode
from liman_core.nodes.base.schemas import (
    NS,
    LangChainMessage,
)
from liman_core.nodes.function_node.node import FunctionNode
from liman_core.nodes.llm_node.node import LLMNode
from liman_core.nodes.llm_node.schemas import LLMNodeState
from liman_core.nodes.node.node import Node
from liman_core.nodes.supported_types import get_node_cls
from liman_core.nodes.tool_node.node import ToolNode
from liman_core.nodes.tool_node.schemas import ToolCall, ToolNodeState
from liman_core.plugins.core.base import ExecutionStateProvider
from liman_core.utils import to_snake_case

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

logger = logging.getLogger(__name__)

if settings.DEBUG:
    try:
        from rich.logging import RichHandler
    except ImportError:
        logger.warning(
            "Rich logging is not available. Install 'rich' package to enable rich logging."
        )
    else:
        handler = RichHandler(show_time=True, show_path=True, rich_tracebacks=True)
        handler.setFormatter(logging.Formatter("%(actor_id)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)


T = TypeVar("T", bound=BaseNode[Any, Any])


class NodeActor(Generic[T]):
    """
    Unified NodeActor supporting both sync and async execution
    """

    def __init__(
        self,
        node: T,
        actor_id: UUID | None = None,
        llm: BaseChatModel | None = None,
    ):
        self.id = actor_id or uuid4()
        self.llm = llm
        self.node = node
        self.node_state = node.get_new_state()

        self.status = NodeActorStatus.IDLE
        self.error: NodeActorError | None = None

        self._execution_lock = asyncio.Lock()

        self.logger = logging.LoggerAdapter(logger, {"actor_id": str(self.id)})

        self._initialize()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, node={self.node.name}, status={self.status.value})"

    @property
    def composite_id(self) -> str:
        """
        Standardized composite identifier in format: actor_type/node_type/node_name/uuid
        """
        actor_type = to_snake_case(self.__class__.__name__)
        node_type = to_snake_case(self.node.__class__.__name__)
        node_name = self.node.name
        return f"{actor_type}/{node_type}/{node_name}/{self.id}"

    @classmethod
    def can_restore(cls, node: BaseNode[S, NS], saved_state: dict[str, Any]) -> bool:
        """
        Check if NodeActor can be restored based on node type and status
        """
        status = saved_state.get("status")

        if node.is_tool_node:
            return status == NodeActorStatus.READY
        elif isinstance(node, LLMNode):
            return status in [
                NodeActorStatus.READY,
                NodeActorStatus.EXECUTING,
                NodeActorStatus.COMPLETED,
            ]
        return False

    @classmethod
    def create(
        cls,
        node: T,
        actor_id: UUID | None = None,
        llm: BaseChatModel | None = None,
    ) -> Self:
        """
        Create a NodeActor instance from a node.

        Args:
            node: The node to wrap in this actor
            actor_id: Optional custom actor ID
            llm: Optional LLM instance for LLMNodes

        Returns:
            Configured NodeActor instance
        """
        actor = cls(node=node, actor_id=actor_id, llm=llm)
        return actor

    @classmethod
    async def create_or_restore(
        cls,
        node: T,
        state: dict[str, Any] | None,
        llm: BaseChatModel | None = None,
    ) -> Self:
        """
        Create a new NodeActor or restore from saved state

        Args:
            node: The node to wrap in this actor
            state: Saved state to restore
            llm: Optional LLM instance for LLMNodes

        Returns:
            NodeActor instance (new or restored)
        """
        if state and cls.can_restore(node, state):
            actor_id = UUID(state["actor_id"])
            actor = cls(node=node, actor_id=actor_id, llm=llm)
            actor._restore_state(state)
            return actor
        else:
            return cls.create(node=node, llm=llm)

    async def execute(
        self,
        input_: Any,
        execution_id: UUID,
        context: dict[str, Any] | None = None,
    ) -> Result:
        """
        Execute the wrapped node with the provided inputs (async version).

        Args:
            input_: Input for the node
            context: Additional execution context
            execution_id: Execution tracking ID

        Returns:
            Result from node execution

        Raises:
            NodeActorError: If execution fails or actor is in invalid state
        """
        if self.status in (NodeActorStatus.IDLE, NodeActorStatus.SHUTDOWN):
            raise create_error(
                f"Cannot execute actor in status {self.status.value}", self
            )

        context = context or {}
        async with self._execution_lock:
            return await self._execute_internal(input_, context, execution_id)

    def serialize_state(self) -> dict[str, Any]:
        """
        Serialize NodeActor state for persistence
        """
        return {
            "actor_id": str(self.id),
            "node_id": str(self.node.id),
            "status": self.status.value,
            "node_state": self.node_state.model_dump(),
        }

    def _initialize(self) -> None:
        """
        Initialize the actor and prepare for execution (async version)
        """
        if self.status != NodeActorStatus.IDLE:
            raise create_error(f"Cannot initialize actor in status {self.status}", self)

        self.status = NodeActorStatus.INITIALIZING
        self.has_error = False

        try:
            if not self.node._compiled:
                self.node.compile()

            self.status = NodeActorStatus.READY

        except Exception as e:
            self.error = create_error(f"Failed to initialize actor: {e}", self)
            self.has_error = True
            raise self.error from e

    async def _execute_internal(
        self, input_: Any, context: dict[str, Any], execution_id: UUID
    ) -> Result:
        self.status = NodeActorStatus.EXECUTING

        registry = self.node.registry
        plugins = [
            plugin
            for plugin in registry.get_plugins(self.node.spec.kind)
            if isinstance(plugin, ExecutionStateProvider)
        ]
        state = {
            k: v
            for d in [
                plugin.get_execution_state(self.node, context, registry)
                for plugin in plugins
            ]
            for k, v in d.items()
        }

        self.logger.debug(
            f"NodeActor executes {self.node.full_name} with input: {input_}, state: {state}"
        )

        try:
            execution_context = self._prepare_execution_context(context, execution_id)

            if isinstance(self.node, LLMNode):
                node_output = await self._execute_llm_node(input_, execution_context)
            elif isinstance(self.node, ToolNode):
                node_output = await self._execute_tool_node(input_, execution_context)
            elif isinstance(self.node, FunctionNode):
                node_output = await self._execute_function_node(
                    input_, execution_context
                )
            else:
                raise create_error(
                    f"Unsupported node type {self.node.spec.kind} for execution", self
                )

            self.logger.debug(
                f"NodeActor completed {self.node.full_name} with output: {node_output}"
            )

            next_nodes = self._get_next_nodes(node_output)
            self.logger.debug(f"Next nodes to execute: {next_nodes}")

            self.status = NodeActorStatus.COMPLETED
            return Result(
                output=node_output,
                next_nodes=next_nodes,
            )

        except Exception as e:
            self.error = create_error(
                f"Node execution failed: {e}", self, execution_id=execution_id
            )
            raise self.error from e

    async def _execute_llm_node(
        self, input_: Any, context: dict[str, Any]
    ) -> LangChainMessage:
        if not self.llm:
            raise create_error(
                "LLM required for LLMNode execution but not provided", self
            )

        node_state = self.node_state

        # it's needed for proper typing
        if not isinstance(self.node, LLMNode):
            raise create_error(f"Expected LLMNode, got {type(self.node)}", self)
        if not isinstance(node_state, LLMNodeState):
            raise create_error(
                "NodeActor state has improper node_state for LLMNode", self
            )

        inputs: list[LangChainMessage] = []
        if isinstance(input_, str):
            inputs.append(HumanMessage(content=input_))
        elif isinstance(input_, HumanMessage | ToolMessage):
            inputs.append(input_)
        elif isinstance(input_, list):
            inputs.extend(input_)
        else:
            raise create_error(
                f"Unsupported input type {type(input_)} for LLMNode", self
            )

        node_output = await self.node.invoke(
            self.llm, [*node_state.messages, *inputs], **context
        )

        node_state.messages.extend(inputs)
        node_state.messages.append(node_output)
        return node_output

    async def _execute_tool_node(
        self, input_: Any, context: dict[str, Any] | None = None
    ) -> ToolMessage:
        # it's needed for proper typing
        if not isinstance(self.node, ToolNode):
            raise create_error(f"Expected ToolNode, got {type(self.node)}", self)
        if not isinstance(self.node_state, ToolNodeState):
            raise create_error(
                f"Expected ToolNodeState, got {type(self.node_state)}", self
            )

        tool_call = ToolCall.model_validate(input_)
        node_output = await self.node.invoke(tool_call, state=context)
        self.node_state.input_ = tool_call
        self.node_state.output = node_output
        return node_output

    async def _execute_function_node(
        self, input_: Any, context: dict[str, Any] | None = None
    ) -> Any:
        if not isinstance(self.node, FunctionNode):
            raise create_error(f"Expected FunctionNode, got {type(self.node)}", self)

        return await self.node.invoke(input_, state=context or {})

    # State synchronization privatemethods

    def _get_next_nodes(
        self, output: LangChainMessage | ToolMessage | dict[str, Any] | None
    ) -> list[NextNode]:
        """
        Get the next nodes to execute based on the output
        """
        registry = self.node.registry

        # LLMNode supports only ToolNode edges
        if isinstance(self.node, LLMNode):
            next_nodes = []
            if tool_calls := getattr(output, "tool_calls", []):
                for tool_call in tool_calls:
                    if isinstance(tool_call, dict) and "name" in tool_call:
                        tool_name: str = tool_call["name"]
                        tool = registry.lookup(ToolNode, tool_name)
                        next_nodes.append(NextNode(tool, tool_call))

            return next_nodes

        edges = self._get_node_edges()
        if not edges:
            return []

        context, state_context = self._build_evaluation_context(output)
        transformer = WhenTransformer()

        # ToolNode supports FunctionNode and LLMNode edges
        if isinstance(self.node, ToolNode) and edges:
            next_nodes = []
            for node_type, edge in edges:
                if self._should_follow_edge(edge, context, state_context, transformer):
                    target_node = registry.lookup(node_type, edge.target)
                    next_nodes.append(NextNode(target_node, output))
            return next_nodes

        return []

    def _get_node_edges(self) -> list[tuple[type[Node | LLMNode], EdgeSpec]]:
        edges: list[tuple[type[Node | LLMNode], EdgeSpec]] = []

        if nodes := getattr(self.node.spec, "nodes", []):
            for node_ref in nodes:
                if isinstance(node_ref, EdgeSpec):
                    edges.append((Node, node_ref))

        if llm_nodes := getattr(self.node.spec, "llm_nodes", []):
            for node_ref in llm_nodes:
                if isinstance(node_ref, EdgeSpec):
                    edges.append((LLMNode, node_ref))

        return edges

    def _build_evaluation_context(
        self, output: Any
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Build context for edge condition evaluation
        Variables with $ prefix: $output, $status, $state
        Variables without $ prefix: taken from $state.context
        """
        state_data = self.node_state.model_dump()

        context = {
            "$output": output if isinstance(output, dict) else {},
            "$status": self.status.value,
            "$state": state_data,
        }

        return context, state_data.get("context", {})

    def _should_follow_edge(
        self,
        edge: EdgeSpec,
        context: dict[str, Any],
        state_context: dict[str, Any],
        transformer: WhenTransformer,
    ) -> bool:
        """
        Determine if an edge should be followed based on its conditions
        """
        if not edge.when:
            return True

        try:
            tree = when_parser.parse(edge.when)
            ast = transformer.transform(tree)
            evaluator = ConditionalEvaluator(context, state_context)
            return evaluator.evaluate(ast)
        except Exception:
            return False

    def _prepare_execution_context(
        self, context: dict[str, Any], execution_id: UUID
    ) -> dict[str, Any]:
        """
        Prepare execution context with actor metadata
        """
        execution_context = {
            **context,
            "actor_id": self.id,
            "execution_id": execution_id,
            "node_name": self.node.name,
            "node_type": self.node.spec.kind,
        }

        return execution_context

    def _restore_state(self, state: dict[str, Any]) -> None:
        """
        Restore NodeActor state from serialized data
        """
        try:
            node_cls = get_node_cls(state["node_state"]["kind"])
            state_cls = node_cls.state_type

            node_state = state_cls.model_validate(state["node_state"])

            self.status = NodeActorStatus(state["status"])
            self.node_state = node_state
            self.error = None

        except Exception as e:
            raise create_error(f"Failed to restore actor state: {e}", self) from e


def create_error(
    message: str, actor: NodeActor[T], *, execution_id: UUID | None = None
) -> NodeActorError:
    return NodeActorError(
        message,
        actor_id=actor.id,
        actor_composite_id=actor.composite_id,
        node_kind=actor.node.spec.kind,
        node_name=actor.node.name,
        execution_id=execution_id,
    )
