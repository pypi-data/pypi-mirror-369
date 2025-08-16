# Copyright (c) 2025 ClearFlow Contributors

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TypeVar, override

__all__ = [
    "Flow",
    "Node",
    "NodeResult",
]

# Type definitions
T = TypeVar("T")
FromNodeName = str
Outcome = str
RouteKey = tuple[FromNodeName, Outcome]


@dataclass(frozen=True)
class NodeResult[T]:
    """Result of node execution with state and outcome."""

    state: T
    outcome: Outcome


@dataclass(frozen=True, kw_only=True)
class Node[T](ABC):
    """Async node that transforms state of type T."""

    name: str = field(default="")

    def __post_init__(self) -> None:
        """Set name from class if not provided."""
        if not self.name:
            # Use object.__setattr__ to bypass frozen dataclass restriction
            object.__setattr__(self, "name", self.__class__.__name__)

    async def __call__(self, state: T) -> NodeResult[T]:
        """Execute node lifecycle."""
        state = await self.prep(state)
        result = await self.exec(state)
        return await self.post(result)

    async def prep(self, state: T) -> T:
        """Pre-execution hook."""
        return state

    @abstractmethod
    async def exec(self, state: T) -> NodeResult[T]:
        """Main execution - must be implemented by subclasses."""
        ...

    async def post(self, result: NodeResult[T]) -> NodeResult[T]:
        """Post-execution hook."""
        return result


@dataclass(frozen=True, kw_only=True)
class _Flow(Node[T]):
    """Internal flow implementation."""

    start_node: Node[T]
    routes: Mapping[RouteKey, Node[T] | None]

    @override
    async def exec(self, state: T) -> NodeResult[T]:
        current_node = self.start_node
        current_state = state

        # Execution loop
        while True:
            # Execute current node
            result = await current_node(current_state)

            # Find next node in routes based on outcome
            key: RouteKey = (current_node.name, result.outcome)

            # Check if route exists
            if key not in self.routes:
                # No route defined - for nested flows, bubble up the outcome
                # For top-level flows, this is an error
                if not self.routes:
                    # Flow has no routes at all - it's a single-node flow
                    # Return the result as-is
                    return result
                # Flow has some routes but not for this outcome
                # This means the flow should terminate with this outcome
                return result

            next_node = self.routes[key]

            if next_node is None:
                # Explicit termination
                return result
            # Continue to next node
            current_node = next_node
            current_state = result.state


@dataclass(frozen=True)
class _StartedWithFlow[T]:
    """Private: Flow with a starting node - can add routes or build."""

    _name: str
    _start: Node[T]
    _routes: MappingProxyType[RouteKey, Node[T] | None]

    def route(
        self, from_node: Node[T], outcome: Outcome, to_node: Node[T] | None
    ) -> "_StartedWithFlow[T]":
        """Connect nodes: from_node --outcome--> to_node."""
        if not from_node.name:
            msg = f"from_node must have a name: {from_node}"
            raise ValueError(msg)

        # Create new dict with existing routes plus new route
        route_key: RouteKey = (from_node.name, outcome)
        new_routes = {**self._routes, route_key: to_node}

        return _StartedWithFlow(
            _name=self._name, _start=self._start, _routes=MappingProxyType(new_routes)
        )

    def build(self) -> Node[T]:
        """Build and return the flow as a Node."""
        # Validate single termination
        none_routes = [
            (from_node, outcome)
            for (from_node, outcome), to_node in self._routes.items()
            if to_node is None
        ]

        if len(none_routes) > 1:
            msg = (
                f"Flow '{self._name}' has multiple termination points "
                f"(routes to None): {none_routes}. "
                f"Flows must have exactly one termination point."
            )
            raise ValueError(msg)

        return _Flow(name=self._name, start_node=self._start, routes=self._routes)


@dataclass(frozen=True)
class Flow[T]:
    """Type-safe flow with immutable construction."""

    _name: str

    def __post_init__(self) -> None:
        """Validate flow name."""
        if not self._name or not self._name.strip():
            msg = "Flow name must be a non-empty string"
            raise ValueError(msg)

    def start_with(self, node: Node[T]) -> _StartedWithFlow[T]:
        """Set starting node."""
        return _StartedWithFlow(
            _name=self._name,
            _start=node,
            _routes=MappingProxyType({}),  # Explicit empty immutable mapping
        )
