"""Test Suite for ClearFlow - The Purely Functional LLM Framework.

This test suite validates the core principles of ClearFlow:
- Pure functions (no side effects)
- Explicit routing
- Composability of flows
- Type safety with any state structure

Testing approach:
- Property-based testing: verify invariants
- Example-based testing: verify specific behaviors
- Edge case testing: handle errors gracefully
- Composition testing: verify that functions compose correctly

Each test documents the functional programming principle it validates.

Copyright (c) 2025 ClearFlow Contributors
"""

from dataclasses import dataclass as dc
from typing import Any, TypedDict, override

import pytest

from clearflow import (
    Flow,
    Node,
    NodeResult,
)

# Type aliases for domain-specific test scenarios

ChatState = dict[str, Any]  # For chat agent tests
DocumentState = dict[str, Any]  # For document processing tests
ToolState = dict[str, Any]  # For tool execution tests

# More specific types for certain test cases
DocumentListState = dict[str, list[str] | str]
MessageListState = dict[str, list[str] | int]


# Simple test node for cases where we need a concrete Node
class SimpleNode(Node[dict[str, Any]]):
    """A simple node that just passes through state with a configurable outcome."""

    outcome: str = "done"

    @override
    async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
        return NodeResult(state, outcome=self.outcome)


# ===== FLEXIBLE STATE TESTS =====


class TestFlexibleState:
    """Test that ClearFlow works with any state structure."""

    @staticmethod
    async def test_dict_state() -> None:
        """Test with plain dictionaries."""

        class DictNode(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                # Create new dict (immutable pattern)
                new_state = {**state, "processed": True}
                return NodeResult(new_state, outcome="done")

        node = DictNode()
        initial: dict[str, Any] = {"data": "test"}
        result = await node(initial)

        assert result.state["processed"] is True
        assert result.state["data"] == "test"
        # Original unchanged (if following immutable pattern)
        assert "processed" not in initial

    @staticmethod
    async def test_typed_dict_state() -> None:
        """Test with TypedDict for type safety."""

        class AgentState(TypedDict):
            messages: list[str]
            context: str

        class TypedNode(Node[AgentState]):
            @override
            async def exec(self, state: AgentState) -> NodeResult[AgentState]:
                new_state: AgentState = {
                    "messages": [*state["messages"], "response"],
                    "context": state["context"],
                }
                return NodeResult(new_state, outcome="responded")

        node = TypedNode()
        initial: AgentState = {"messages": ["hello"], "context": "chat"}
        result = await node(initial)

        assert len(result.state["messages"]) == 2
        assert result.state["messages"][1] == "response"

    @staticmethod
    async def test_dataclass_state() -> None:
        """Test with frozen dataclasses for immutability."""

        @dc(frozen=True)
        class WorkflowState:
            documents: tuple[str, ...]
            processed: bool = False

        class DataclassNode(Node[WorkflowState]):
            @override
            async def exec(self, state: WorkflowState) -> NodeResult[WorkflowState]:
                # Create new instance (immutable)
                new_state = WorkflowState(documents=state.documents, processed=True)
                return NodeResult(new_state, outcome="processed")

        node = DataclassNode()
        initial = WorkflowState(documents=("doc1", "doc2"))
        result = await node(initial)

        assert result.state.processed is True
        assert initial.processed is False  # Original unchanged

    @staticmethod
    async def test_primitive_state() -> None:
        """Test with primitive types as state."""

        class CounterNode(Node[int]):
            @override
            async def exec(self, state: int) -> NodeResult[int]:
                return NodeResult(state + 1, outcome="incremented")

        node = CounterNode()
        result = await node(42)

        assert result.state == 43
        assert result.outcome == "incremented"


# ===== NODE TESTS =====


class TestNode:
    """Test the Node abstraction."""

    @staticmethod
    async def test_pure_exec_function() -> None:
        """Core principle: exec functions are pure - same input, same output."""

        @dc(frozen=True)
        class DeterministicNode(Node[dict[str, int]]):
            """A node with deterministic behavior."""

            @override
            async def exec(self, state: dict[str, int]) -> NodeResult[dict[str, int]]:
                # Pure transformation
                new_state = {**state, "value": state.get("value", 0) * 2}
                return NodeResult(new_state, outcome="doubled")

        node = DeterministicNode()
        initial = {"value": 5}

        # Multiple calls with same input produce same output
        result1 = await node(initial)
        result2 = await node(initial)

        assert result1.state == result2.state
        assert result1.outcome == result2.outcome
        assert result1.state["value"] == 10

    @staticmethod
    async def test_lifecycle_hooks() -> None:
        """Test that prep and post hooks work correctly."""

        @dc(frozen=True)
        class LifecycleNode(Node[dict[str, Any]]):
            """Node that uses lifecycle hooks."""

            @override
            async def prep(self, state: dict[str, Any]) -> dict[str, Any]:
                # Add preprocessing flag
                return {**state, "preprocessed": True}

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                # Main processing
                new_state = {**state, "executed": True}
                return NodeResult(new_state, outcome="processed")

            @override
            async def post(
                self, result: NodeResult[dict[str, Any]]
            ) -> NodeResult[dict[str, Any]]:
                # Add postprocessing flag
                new_state = {**result.state, "postprocessed": True}
                return NodeResult(new_state, outcome=result.outcome)

        node = LifecycleNode()
        result = await node({})

        assert result.state["preprocessed"] is True
        assert result.state["executed"] is True
        assert result.state["postprocessed"] is True

    @staticmethod
    async def test_llm_simulation() -> None:
        """Test a node that simulates LLM interaction."""

        @dc(frozen=True)
        class LLMNode(Node[ChatState]):
            """Simulates an LLM chat completion."""

            @override
            async def exec(self, state: ChatState) -> NodeResult[ChatState]:
                messages = state.get("messages", [])

                # Simulate LLM response
                if any("weather" in str(msg).lower() for msg in messages):
                    response = "I cannot provide real-time weather information."
                    outcome = "weather_query"
                elif any("code" in str(msg).lower() for msg in messages):
                    response = "I can help you write code. What language?"
                    outcome = "code_request"
                else:
                    response = "How can I assist you today?"
                    outcome = "general"

                new_messages = [*messages, {"role": "assistant", "content": response}]
                new_state = {
                    **state,
                    "messages": new_messages,
                    "last_response": response,
                }

                return NodeResult(new_state, outcome=outcome)

        node = LLMNode()

        # Test weather query
        weather_state: ChatState = {
            "messages": [{"role": "user", "content": "What's the weather?"}]
        }
        result = await node(weather_state)
        assert result.outcome == "weather_query"
        assert "weather information" in result.state["last_response"]

        # Test code request
        code_state: ChatState = {
            "messages": [{"role": "user", "content": "Help me write code"}]
        }
        result = await node(code_state)
        assert result.outcome == "code_request"
        assert "language" in result.state["last_response"]


# ===== FLOW TESTS =====


class TestFlow:
    """Test the Flow orchestration."""

    @staticmethod
    async def test_linear_flow() -> None:
        """Test a simple linear flow: A -> B -> C -> None."""

        @dc(frozen=True)
        class TokenizerNode(Node[DocumentState]):
            @override
            async def exec(self, state: DocumentState) -> NodeResult[DocumentState]:
                text = state.get("text", "")
                tokens = text.split() if isinstance(text, str) else []
                new_state = {**state, "tokens": tokens}
                return NodeResult(new_state, outcome="tokenized")

        @dc(frozen=True)
        class EmbedderNode(Node[DocumentState]):
            @override
            async def exec(self, state: DocumentState) -> NodeResult[DocumentState]:
                tokens = state.get("tokens", [])
                # Simulate embeddings
                embeddings = [len(str(t)) * 0.1 for t in tokens]
                new_state = {**state, "embeddings": embeddings}
                return NodeResult(new_state, outcome="embedded")

        @dc(frozen=True)
        class IndexerNode(Node[DocumentState]):
            @override
            async def exec(self, state: DocumentState) -> NodeResult[DocumentState]:
                new_state = {**state, "indexed": True}
                return NodeResult(new_state, outcome="indexed")

        # Build the flow
        tokenizer = TokenizerNode()
        embedder = EmbedderNode()
        indexer = IndexerNode()

        flow = (
            Flow[DocumentState]("DocumentPipeline")
            .start_with(tokenizer)
            .route(tokenizer, "tokenized", embedder)
            .route(embedder, "embedded", indexer)
            .route(indexer, "indexed", None)  # Terminal
            .build()
        )

        # Execute
        initial: DocumentState = {"text": "Natural language processing"}
        result = await flow(initial)

        assert result.outcome == "indexed"
        assert "tokens" in result.state
        assert "embeddings" in result.state
        assert result.state["indexed"] is True

    @staticmethod
    async def test_branching_flow() -> None:
        """Test flow with conditional branching based on outcomes."""

        @dc(frozen=True)
        class ClassifierNode(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                content = state.get("content", "")

                if "urgent" in str(content).lower():
                    outcome = "urgent"
                elif "question" in str(content).lower():
                    outcome = "question"
                else:
                    outcome = "normal"

                new_state = {**state, "classification": outcome}
                return NodeResult(new_state, outcome=outcome)

        @dc(frozen=True)
        class UrgentHandler(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                new_state = {**state, "priority": "high", "handled_by": "urgent_team"}
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class QuestionHandler(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                new_state = {
                    **state,
                    "priority": "medium",
                    "handled_by": "support_team",
                }
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class NormalHandler(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                new_state = {**state, "priority": "low", "handled_by": "bot"}
                return NodeResult(new_state, outcome="handled")

        @dc(frozen=True)
        class CompleteHandler(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                new_state = {**state, "status": "completed"}
                return NodeResult(new_state, outcome="done")

        # Build branching flow with single termination
        classifier = ClassifierNode()
        urgent = UrgentHandler()
        question = QuestionHandler()
        normal = NormalHandler()
        complete = CompleteHandler()

        flow = (
            Flow[dict[str, Any]]("TicketRouter")
            .start_with(classifier)
            .route(classifier, "urgent", urgent)
            .route(classifier, "question", question)
            .route(classifier, "normal", normal)
            .route(urgent, "handled", complete)  # Converge to complete
            .route(question, "handled", complete)  # Converge to complete
            .route(normal, "handled", complete)  # Converge to complete
            .route(complete, "done", None)  # Single termination
            .build()
        )

        # Test urgent path
        urgent_result = await flow({"content": "URGENT: Server is down!"})
        assert urgent_result.state["priority"] == "high"
        assert urgent_result.state["handled_by"] == "urgent_team"
        assert urgent_result.state["status"] == "completed"
        assert urgent_result.outcome == "done"

        # Test question path
        question_result = await flow({"content": "Question about billing"})
        assert question_result.state["priority"] == "medium"
        assert question_result.state["handled_by"] == "support_team"
        assert question_result.state["status"] == "completed"
        assert question_result.outcome == "done"

        # Test normal path
        normal_result = await flow({"content": "Monthly newsletter"})
        assert normal_result.state["priority"] == "low"
        assert normal_result.state["handled_by"] == "bot"
        assert normal_result.state["status"] == "completed"
        assert normal_result.outcome == "done"

    @staticmethod
    async def test_single_termination_enforcement() -> None:
        """Test that flows must have exactly one termination point."""
        node_a = SimpleNode()

        # This should fail - multiple termination points
        with pytest.raises(ValueError, match="multiple termination points"):
            (
                Flow[dict[str, Any]]("InvalidFlow")
                .start_with(node_a)
                .route(node_a, "done", None)  # First termination
                .route(node_a, "error", None)  # Second termination - should fail
                .build()
            )

    @staticmethod
    async def test_nested_flows() -> None:
        """Test that flows can be composed as nodes."""

        @dc(frozen=True)
        class StartNode(Node[dict[str, str]]):
            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                new_state = {**state, "started": "true"}
                return NodeResult(new_state, outcome="ready")

        @dc(frozen=True)
        class EndNode(Node[dict[str, str]]):
            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                new_state = {**state, "completed": "true"}
                return NodeResult(new_state, outcome="done")

        # Create inner flow
        start = StartNode()
        end = EndNode()

        inner_flow = (
            Flow[dict[str, str]]("InnerFlow")
            .start_with(start)
            .route(start, "ready", end)
            .route(end, "done", None)
            .build()
        )

        # Use inner flow as a node in outer flow
        outer_flow = (
            Flow[dict[str, str]]("OuterFlow")
            .start_with(inner_flow)
            .route(inner_flow, "done", None)
            .build()
        )

        result = await outer_flow({"initial": "value"})

        assert result.state["started"] == "true"
        assert result.state["completed"] == "true"
        assert result.outcome == "done"


# ===== REAL-WORLD SCENARIO TESTS =====


class TestRealWorldScenarios:
    """Test realistic LLM agent scenarios."""

    @staticmethod
    async def test_rag_pipeline() -> None:
        """Test a Retrieval-Augmented Generation pipeline."""

        @dc(frozen=True)
        class RetrieverNode(Node[dict[str, Any]]):
            """Simulates document retrieval."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                query = state.get("query", "")

                # Simulate retrieval
                if "machine learning" in str(query).lower():
                    docs = [
                        (
                            "ML is a subset of AI focused on algorithms that "
                            "improve through experience."
                        ),
                        (
                            "Common ML techniques include neural networks and "
                            "decision trees."
                        ),
                    ]
                else:
                    docs = ["No relevant documents found."]

                new_state = {**state, "retrieved_docs": docs}
                outcome = "docs_found" if len(docs) > 1 else "no_docs"
                return NodeResult(new_state, outcome=outcome)

        @dc(frozen=True)
        class GeneratorNode(Node[dict[str, Any]]):
            """Simulates LLM generation with context."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                docs = state.get("retrieved_docs", [])

                if docs and docs[0] != "No relevant documents found.":
                    response = f"Based on the documents: {docs[0]}"
                else:
                    response = (
                        "I don't have enough information to answer that question."
                    )

                new_state = {**state, "response": response}
                return NodeResult(new_state, outcome="generated")

        # Build RAG pipeline
        retriever = RetrieverNode()
        generator = GeneratorNode()

        rag_pipeline = (
            Flow[dict[str, Any]]("RAGPipeline")
            .start_with(retriever)
            .route(retriever, "docs_found", generator)
            .route(retriever, "no_docs", generator)
            .route(generator, "generated", None)
            .build()
        )

        # Test with relevant query
        result = await rag_pipeline({"query": "What is machine learning?"})
        assert "ML is a subset of AI" in result.state["response"]

        # Test with irrelevant query
        result = await rag_pipeline({"query": "What's for dinner?"})
        assert "don't have enough information" in result.state["response"]

    @staticmethod
    async def test_agent_with_tools() -> None:
        """Test an agent that can use tools."""

        @dc(frozen=True)
        class PlannerNode(Node[dict[str, Any]]):
            """Plans which tool to use."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                task = state.get("task", "")

                if "calculate" in str(task).lower():
                    tool = "calculator"
                elif "search" in str(task).lower():
                    tool = "web_search"
                elif "code" in str(task).lower():
                    tool = "code_interpreter"
                else:
                    tool = "none"

                new_state = {**state, "selected_tool": tool}
                return NodeResult(new_state, outcome=tool)

        @dc(frozen=True)
        class CalculatorNode(Node[dict[str, Any]]):
            """Simulates calculator tool."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                # Simulate calculation
                new_state = {**state, "result": "42", "tool_used": "calculator"}
                return NodeResult(new_state, outcome="calculated")

        @dc(frozen=True)
        class SearchNode(Node[dict[str, Any]]):
            """Simulates web search tool."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                # Simulate search
                new_state = {
                    **state,
                    "result": "Found 10 relevant results",
                    "tool_used": "web_search",
                }
                return NodeResult(new_state, outcome="searched")

        @dc(frozen=True)
        class ResponseNode(Node[dict[str, Any]]):
            """Generates final response."""

            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                tool_used = state.get("tool_used", "none")
                result = state.get("result", "No result")

                if tool_used != "none":
                    response = f"Used {tool_used}: {result}"
                else:
                    response = "I can help with calculations, searches, and code."

                new_state = {**state, "final_response": response}
                return NodeResult(new_state, outcome="responded")

        # Build agent flow
        planner = PlannerNode()
        calculator = CalculatorNode()
        search = SearchNode()
        responder = ResponseNode()

        agent = (
            Flow[dict[str, Any]]("ToolAgent")
            .start_with(planner)
            .route(planner, "calculator", calculator)
            .route(planner, "web_search", search)
            .route(planner, "code_interpreter", responder)  # Not implemented
            .route(planner, "none", responder)
            .route(calculator, "calculated", responder)
            .route(search, "searched", responder)
            .route(responder, "responded", None)
            .build()
        )

        # Test calculator path
        calc_result = await agent({"task": "Calculate 6 * 7"})
        assert calc_result.state["tool_used"] == "calculator"
        assert "calculator" in calc_result.state["final_response"]

        # Test search path
        search_result = await agent({"task": "Search for Python tutorials"})
        assert search_result.state["tool_used"] == "web_search"
        assert "web_search" in search_result.state["final_response"]

        # Test no tool path
        no_tool_result = await agent({"task": "Hello there"})
        assert no_tool_result.state.get("tool_used") is None
        assert "can help" in no_tool_result.state["final_response"]


# ===== ERROR HANDLING TESTS =====


class TestErrorHandling:
    """Test error handling and edge cases."""

    @staticmethod
    async def test_missing_route() -> None:
        """Test behavior when a route is not defined."""

        @dc(frozen=True)
        class UnpredictableNode(Node[dict[str, str]]):
            """Node with variable outcomes."""

            @override
            async def exec(self, state: dict[str, str]) -> NodeResult[dict[str, str]]:
                # Return an outcome that might not be routed
                outcome = state.get("force_outcome", "unexpected")
                return NodeResult(state, outcome=outcome)

        node = UnpredictableNode()

        # Flow with incomplete routing
        flow = (
            Flow[dict[str, str]]("IncompleteFlow")
            .start_with(node)
            .route(node, "expected", None)
            # "unexpected" outcome not routed
            .build()
        )

        # Should bubble up the unhandled outcome
        result = await flow({"force_outcome": "unexpected"})
        assert result.outcome == "unexpected"

    @staticmethod
    async def test_empty_flow_name() -> None:
        """Test that flow names must be non-empty."""
        with pytest.raises(ValueError, match="non-empty string"):
            Flow[dict[str, Any]]("")

        with pytest.raises(ValueError, match="non-empty string"):
            Flow[dict[str, Any]]("   ")

    @staticmethod
    async def test_node_name_inference() -> None:
        """Test that nodes get names from their class if not provided."""

        @dc(frozen=True)
        class MyCustomNode(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                return NodeResult(state, outcome="done")

        # No name provided
        node = MyCustomNode()
        assert node.name == "MyCustomNode"

        # Explicit name provided
        named_node = MyCustomNode(name="custom_name")
        assert named_node.name == "custom_name"

    @staticmethod
    async def test_single_node_flow_no_routes() -> None:
        """Test a flow with a single node and no routes (line 94 coverage)."""

        @dc(frozen=True)
        class StandaloneNode(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                return NodeResult(state, outcome="standalone")

        node = StandaloneNode()

        # Create flow with single node but no routes
        flow = Flow[dict[str, Any]]("SingleNodeFlow").start_with(node).build()

        # Execute - should return result as-is since no routes exist
        result = await flow({"test": "value"})
        assert result.outcome == "standalone"
        assert result.state["test"] == "value"

    @staticmethod
    async def test_node_without_name_validation() -> None:
        """Test routing fails when from_node lacks name (lines 122-123 coverage)."""

        @dc(frozen=True)
        class UnnamedNode(Node[dict[str, Any]]):
            @override
            async def exec(self, state: dict[str, Any]) -> NodeResult[dict[str, Any]]:
                return NodeResult(state, outcome="done")

        # Manually create node with empty name to trigger validation
        unnamed_node = UnnamedNode()
        object.__setattr__(unnamed_node, "name", "")  # noqa: PLC2801

        target_node = SimpleNode()

        # Should raise ValueError when trying to route from unnamed node
        with pytest.raises(ValueError, match="from_node must have a name"):
            (
                Flow[dict[str, Any]]("TestFlow")
                .start_with(target_node)
                .route(unnamed_node, "done", None)
            )
