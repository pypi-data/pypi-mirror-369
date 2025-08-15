"""
Intent Kit - A Python library for building hierarchical intent classification and execution systems.

This library provides a tree-based intent architecture with classifier and action nodes,
supports multiple AI service backends, and enables context-aware execution.
"""

from intent_kit.core import (
    IntentDAG,
    DAGBuilder,
    GraphNode,
    ExecutionResult,
    ExecutionError,
    NodeProtocol,
    run_dag,
    ContextProtocol,
    DefaultContext,
)

# run_dag moved to DAGBuilder.run()

__version__ = "0.6.0"

__all__ = [
    "IntentDAG",
    "DAGBuilder",
    "GraphNode",
    "ExecutionResult",
    "ExecutionError",
    "NodeProtocol",
    "run_dag",
    "ContextProtocol",
    "DefaultContext",
]
