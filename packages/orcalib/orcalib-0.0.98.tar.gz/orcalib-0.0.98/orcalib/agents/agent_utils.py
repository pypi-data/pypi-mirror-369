import asyncio
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from .agent_workflow import AgentWorkflow

TInput = TypeVar("TInput", bound=BaseModel)
TDeps = TypeVar("TDeps", bound=BaseModel)
TResult = TypeVar("TResult", bound=BaseModel)


def run_agent_safely(
    agent: AgentWorkflow[TResult, TInput, TDeps], agent_input: TInput, context: TDeps
) -> TResult | None:
    """
    Safely run an agent with proper async context handling.

    Args:
        agent: The agent workflow to run
        agent_input: Input data for the agent
        context: Context/dependencies for the agent

    Returns:
        The agent's description or None if it cannot be run safely.
    """
    try:
        # Check if we're in an async context using the modern approach
        try:
            # This will raise RuntimeError if no event loop is running
            _ = asyncio.get_running_loop()
            # If we reach here, there's an active event loop
            # We cannot use asyncio.run() or loop.run_until_complete() on a running loop
            # Since this function is synchronous, we skip agent execution in async contexts
            logging.debug("Skipping agent execution: running in async context where synchronous await is not possible")
            return None
        except RuntimeError:
            # No running event loop - we can safely create one
            pass

        # No running event loop, safe to use asyncio.run()
        result = asyncio.run(agent.run(agent_input, deps=context))
        return result.output

    except Exception as e:
        # Handle any other errors (network, API, validation, etc.)
        logging.warning(f"Agent execution failed: {e}")
        return None
